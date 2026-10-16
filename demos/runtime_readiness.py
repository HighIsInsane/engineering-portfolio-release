"""Validate saved local-server metadata without contacting or invoking a model."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

MAX_BYTES = 64 * 1024


def read_object(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("regular file required")
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("metadata too large")

    def unique_pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate key")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError("nonfinite JSON constant")

    result = json.loads(raw, object_pairs_hook=unique_pairs, parse_constant=reject_constant)
    if not isinstance(result, dict):
        raise ValueError("object required")
    return result


def check_metadata(health: dict, models: dict, expected_alias: str) -> dict:
    if not isinstance(expected_alias, str) or not expected_alias.strip():
        raise ValueError("expected alias required")
    if not isinstance(health, dict) or health.get("status") != "ok":
        raise ValueError("health not ready")
    if not isinstance(models, dict):
        raise ValueError("model list required")
    rows = models.get("data")
    if not isinstance(rows, list) or not rows:
        raise ValueError("model list required")
    ids = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
            raise ValueError("invalid model entry")
        ids.append(row["id"])
    if len(ids) != len(set(ids)) or ids.count(expected_alias) != 1:
        raise ValueError("model alias absent or ambiguous")
    return {
        "status": "METADATA_CONTRACT_PASS",
        "scope": "saved_metadata_only",
        "runtime_identity_attested": False,
        "live_health_verified": False,
        "inference_performed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--health", type=Path, required=True)
    parser.add_argument("--models", type=Path, required=True)
    parser.add_argument("--expected-alias", required=True)
    args = parser.parse_args()
    try:
        result = check_metadata(read_object(args.health), read_object(args.models), args.expected_alias)
    except (OSError, ValueError, UnicodeError):
        print(json.dumps({"status": "FAIL", "scope": "saved_metadata_only"}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
