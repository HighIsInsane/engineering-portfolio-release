"""Heuristic disclosure scan of the entire reachable Git history and release files.

Matches are reported by rule and path, never by matched secret text.
This is a review aid, not a proof that secrets or personal information are absent.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
from pathlib import Path

RULES = {
    "credential": re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{24,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)"),
    "personal_path": re.compile(r"/(?:Users|home)/[A-Za-z0-9_.-]+/|[A-Za-z]:\\Users\\"),
    "private_network": re.compile(r"\b(?:192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|169\.254\.\d{1,3}\.\d{1,3})\b|\b(?:f[cd][0-9a-f]{2}|fe[89ab][0-9a-f]):[0-9a-f:]+", re.I),
    "phone_number": re.compile(r"(?<![\w+])\+[1-9](?:[ ()-]*\d){9,14}(?!\d)"),
    "url_credential": re.compile(r"https?://[^\s/@:]+:[^\s/@]+@", re.I),
    "private_source_locator": re.compile("|".join(re.escape(s) for s in (
        "Spilus-" + "Engineering-Evidence", "Spilus-" + "APU-Probe",
        "programs/" + "spilus-learning", "workflows/" + "qwen25-reviewed-github",
        "stages/" + "stage2", "model-" + "qualification/"))),
}
EMAILS = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
FORBIDDEN = ("*.zip", "*.gguf", "*.apk", "*.aab", "*.jks", "*.keystore", "*.pem", "*.key", "*.sqlite*", "*.db", ".env", ".env.*", "*.p12", "*.pfx", "*.mobileprovision")


def git(root: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, timeout=30).stdout


def inspect_text(raw: bytes, location: str) -> list[dict]:
    if len(raw) > 1_000_000:
        return [{"rule": "oversized_payload", "location": location}]
    try:
        content = raw.decode("utf-8")
    except UnicodeError:
        return [{"rule": "binary_payload", "location": location}]
    if "\0" in content:
        return [{"rule": "binary_payload", "location": location}]
    findings = [{"rule": name, "location": location} for name, pattern in RULES.items() if pattern.search(content)]
    if any(match.group(1).lower() != "users.noreply.github.com" for match in EMAILS.finditer(content)):
        findings.append({"rule": "personal_email", "location": location})
    return findings


def audit(root: Path) -> dict:
    root = root.resolve(strict=True)
    findings = []
    manifest = root / "release-files.txt"
    if manifest.is_symlink():
        raise ValueError("release manifest must not be a symlink")
    allowed = set(manifest.read_text("utf-8").splitlines())
    if not allowed or any(not p or p.startswith("/") or ".." in Path(p).parts for p in allowed):
        raise ValueError("invalid release manifest")
    tracked = {p.decode("utf-8") for p in git(root, "ls-files", "-z").split(b"\0") if p}
    untracked = [p.decode("utf-8") for p in git(root, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0") if p]
    for name in sorted((tracked | set(untracked)) - allowed):
        findings.append({"rule": "unreviewed_file", "location": name})
    # Ignoring a local key or environment file must not make the audit look clean.
    ignored = git(root, "ls-files", "--others", "--ignored", "--exclude-standard", "-z").split(b"\0")
    for raw_name in ignored:
        if raw_name:
            name = raw_name.decode("utf-8")
            if any(fnmatch.fnmatch(Path(name).name.lower(), pattern) for pattern in FORBIDDEN):
                findings.append({"rule": "ignored_sensitive_file", "location": name})
    for name in sorted(allowed):
        path = root / name
        components = [path, *path.parents]
        linked = any(p.is_symlink() for p in components if p != root and root in p.parents)
        if linked:
            findings.append({"rule": "symlink", "location": name})
        elif not path.is_file():
            findings.append({"rule": "missing_file", "location": name})
        else:
            findings.extend(inspect_text(path.read_bytes(), name))
        if any(fnmatch.fnmatch(Path(name).name.lower(), pattern) for pattern in FORBIDDEN):
            findings.append({"rule": "forbidden_file", "location": name})
    # Inspect every commit tree, including paths deleted before HEAD.
    commits = git(root, "rev-list", "--all").decode().splitlines()
    blobs = set()
    for commit in commits:
        for row in git(root, "ls-tree", "-rz", "--full-tree", commit).split(b"\0"):
            if not row:
                continue
            info, raw_name = row.split(b"\t", 1)
            mode, kind, object_id = info.decode().split()
            name = raw_name.decode("utf-8")
            if mode != "100644" or kind != "blob":
                findings.append({"rule": "unexpected_git_mode", "location": name})
            if name not in allowed:
                findings.append({"rule": "unreviewed_history_path", "location": name})
            if any(fnmatch.fnmatch(Path(name).name.lower(), pattern) for pattern in FORBIDDEN):
                findings.append({"rule": "forbidden_history_file", "location": name})
            if kind == "blob" and object_id not in blobs:
                blobs.add(object_id)
                findings.extend(inspect_text(git(root, "cat-file", "blob", object_id), "history:" + name))
    if commits:
        findings.extend(inspect_text(git(root, "log", "--all", "--format=fuller"), "commit_metadata"))
    for row in git(root, "for-each-ref", "--format=%(refname) %(objecttype) %(objectname)").decode().splitlines():
        name, kind, object_id = row.split()
        findings.extend(inspect_text(name.encode(), "ref_metadata"))
        if kind == "tag":
            findings.extend(inspect_text(git(root, "cat-file", "tag", object_id), "tag_metadata"))
    return {"status": "PASS" if not findings else "FAIL", "commits_scanned": len(commits),
            "unique_blobs_scanned": len(blobs), "release_files": len(allowed),
            "findings": findings, "scope": "reachable_refs_and_release_manifest",
            "human_disclosure_review_still_required": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        report = audit(args.root)
    except (ValueError, OSError, subprocess.SubprocessError):
        print(json.dumps({"status": "FAIL", "reason": "audit could not complete"}))
        return 1
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
