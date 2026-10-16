"""Classify synthetic red/green test records without running candidate code."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from demos.runtime_readiness import read_object

COUNTS = ("failures", "errors", "skips")


def validate_run(run: dict) -> None:
    if not isinstance(run, dict) or set(run) != {"test_ids", *COUNTS}:
        raise ValueError("invalid run schema")
    ids = run["test_ids"]
    if (not isinstance(ids, list) or not ids or
            any(not isinstance(item, str) or not item for item in ids) or
            len(ids) != len(set(ids))):
        raise ValueError("unique nonempty test identities required")
    if any(type(run[key]) is not int or run[key] < 0 for key in COUNTS):
        raise ValueError("nonnegative integer counts required")
    if sum(run[key] for key in COUNTS) > len(ids):
        raise ValueError("counts exceed test population")


def classify(record: dict) -> dict:
    keys = {"origin", "attempt", "tests_sha256", "fixtures_unchanged", "baseline", "candidate"}
    if not isinstance(record, dict) or set(record) != keys:
        raise ValueError("invalid record schema")
    if record["origin"] != "synthetic_portfolio":
        raise ValueError("only disclosed synthetic records admitted")
    if record["attempt"] not in ("first", "guided"):
        raise ValueError("attempt category required")
    if not isinstance(record["tests_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", record["tests_sha256"]):
        raise ValueError("test digest required")
    if record["fixtures_unchanged"] is not True:
        raise ValueError("fixture mutation or missing verification")
    baseline, candidate = record["baseline"], record["candidate"]
    validate_run(baseline)
    validate_run(candidate)
    if sorted(baseline["test_ids"]) != sorted(candidate["test_ids"]):
        raise ValueError("test identities differ")
    if any(run["errors"] or run["skips"] for run in (baseline, candidate)):
        label = "INCOMPLETE"
    elif baseline["failures"] == 0:
        label = "NO_RED_BASELINE"
    elif candidate["failures"]:
        label = "REPAIR_FAIL"
    else:
        label = "GUIDED_REPAIR_PASS" if record["attempt"] == "guided" else "FIRST_ATTEMPT_REPAIR_PASS"
    return {"classification": label, "origin": "synthetic_portfolio",
            "evidence_authenticity_verified": False, "candidate_code_executed": False,
            "historical_scores_modified": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    try:
        result = classify(read_object(args.record))
    except (OSError, ValueError, UnicodeError):
        print(json.dumps({"classification": "INVALID_RECORD"}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0 if result["classification"].endswith("_PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
