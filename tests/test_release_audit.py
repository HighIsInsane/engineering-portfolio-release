from pathlib import Path
import subprocess
import tempfile
import unittest

from tools.audit_release import audit, inspect_text


class ReleaseAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "--quiet")
        self.git("config", "user.name", "Portfolio Fixture")
        self.git("config", "user.email", "fixture@users.noreply.github.com")
        (self.root / "README.md").write_text("Synthetic fixture.\n")
        self.manifest("README.md", "release-files.txt")
        self.commit()

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True, timeout=10)

    def manifest(self, *names):
        (self.root / "release-files.txt").write_text("\n".join(names) + "\n")

    def commit(self):
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "synthetic test commit")

    def test_clean_history_and_manifest_pass(self):
        report = audit(self.root)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["commits_scanned"], 1)

    def test_deleted_secret_still_blocks_release(self):
        name = "old.txt"
        (self.root / name).write_text("gh" + "p_" + "A" * 36)
        self.commit()
        (self.root / name).unlink()
        self.commit()
        findings = audit(self.root)["findings"]
        self.assertTrue(any(x["rule"] == "credential" and x["location"].startswith("history:") for x in findings))

    def test_untracked_payload_rejected(self):
        (self.root / "unreviewed.txt").write_text("unreviewed payload")
        self.assertTrue(any(x["rule"] == "unreviewed_file" for x in audit(self.root)["findings"]))

    def test_binary_payload_rejected(self):
        (self.root / "README.md").write_bytes(b"\x00\xff")
        self.assertTrue(any(x["rule"] == "binary_payload" for x in audit(self.root)["findings"]))

    def test_symlink_payload_rejected(self):
        (self.root / "README.md").unlink()
        (self.root / "README.md").symlink_to(self.root / "release-files.txt")
        self.assertTrue(any(x["rule"] == "symlink" for x in audit(self.root)["findings"]))

    def test_personal_email_in_commit_metadata_rejected(self):
        self.git("config", "user.email", "fixture" + "@" + "invalid.example")
        (self.root / "README.md").write_text("second fixture\n")
        self.commit()
        self.assertTrue(any(x["rule"] == "personal_email" and x["location"] == "commit_metadata" for x in audit(self.root)["findings"]))

    def test_symlink_parent_directory_rejected(self):
        real = self.root / "actual"
        real.mkdir()
        (real / "data.txt").write_text("fixture")
        (self.root / "linked").symlink_to(real, target_is_directory=True)
        self.manifest("README.md", "release-files.txt", "linked/data.txt")
        self.assertTrue(any(x["rule"] == "symlink" for x in audit(self.root)["findings"]))

    def test_forbidden_archive_rejected_even_when_allowlisted(self):
        (self.root / "archive.zip").write_text("placeholder")
        self.manifest("README.md", "release-files.txt", "archive.zip")
        self.assertTrue(any(x["rule"] == "forbidden_file" for x in audit(self.root)["findings"]))

    def test_exact_noreply_domain_required(self):
        safe = "fixture" + "@" + "users.noreply.github.com"
        self.assertEqual(inspect_text(safe.encode(), "fixture"), [])
        for address in (safe + ".invalid.example", "fixture" + "@" + "sub.users.noreply.github.com"):
            with self.subTest(address=address):
                self.assertTrue(any(x["rule"] == "personal_email" for x in inspect_text(address.encode(), "fixture")))

    def test_additional_private_network_ranges_rejected(self):
        for value in ("172." + "16.2.3", "172." + "31.2.3", "169." + "254.2.3", "fd00" + "::1234", "fe80" + "::1"):
            with self.subTest(value=value):
                self.assertTrue(any(x["rule"] == "private_network" for x in inspect_text(value.encode(), "fixture")))

    def test_exact_github_platform_noreply_address(self):
        address = "noreply" + "@" + "github.com"
        self.git("config", "user.email", address)
        (self.root / "README.md").write_text("GitHub platform identity fixture\n")
        self.commit()
        self.assertEqual(audit(self.root)["findings"], [])
        for value in ("person" + "@" + "github.com", address + ".invalid.example", "noreply" + "@" + "sub.github.com"):
            with self.subTest(value=value):
                self.assertTrue(any(x["rule"] == "personal_email" for x in inspect_text(value.encode(), "fixture")))

    def test_phone_and_url_credentials_rejected_without_echoing_values(self):
        samples = [("phone_number", "+" + "90 555 123 45 67"), ("url_credential", "https" + "://user:password" + "@" + "example.invalid/path")]
        for rule, value in samples:
            with self.subTest(rule=rule):
                findings = inspect_text(value.encode(), "fixture")
                self.assertTrue(any(x["rule"] == rule for x in findings))
                self.assertNotIn(value, str(findings))

    def test_private_source_locators_rejected(self):
        value = "Spilus-" + "Engineering-Evidence"
        self.assertTrue(any(x["rule"] == "private_source_locator" for x in inspect_text(value.encode(), "fixture")))

    def test_ignored_environment_file_rejected(self):
        (self.root / ".gitignore").write_text(".env\n")
        (self.root / ".env").write_text("synthetic fixture\n")
        self.manifest("README.md", "release-files.txt", ".gitignore")
        self.commit()
        self.assertTrue(any(x["rule"] == "ignored_sensitive_file" for x in audit(self.root)["findings"]))

    def test_annotated_tag_identity_rejected(self):
        self.git("config", "user.email", "fixture" + "@" + "invalid.example")
        self.git("tag", "--annotate", "fixture-tag", "--message", "synthetic tag")
        self.assertTrue(any(x["rule"] == "personal_email" and x["location"] == "tag_metadata" for x in audit(self.root)["findings"]))

    def test_private_ref_name_rejected(self):
        self.git("branch", "review/fixture" + "@" + "invalid.example")
        self.assertTrue(any(x["rule"] == "personal_email" and x["location"] == "ref_metadata" for x in audit(self.root)["findings"]))


if __name__ == "__main__":
    unittest.main()
