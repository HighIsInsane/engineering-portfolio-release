"""Offline INT8 ReLU oracle; this file does not access an accelerator."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from demos.runtime_readiness import read_object


def int8_vector(values) -> list[int]:
    if (not isinstance(values, list) or not values or len(values) > 4096 or
            any(type(value) is not int or not -128 <= value <= 127 for value in values)):
        raise ValueError("nonempty signed INT8 vector required")
    return values


def check_probe(record: dict) -> dict:
    if not isinstance(record, dict) or set(record) != {"origin", "input", "observed"}:
        raise ValueError("invalid probe schema")
    if record["origin"] != "synthetic_portfolio":
        raise ValueError("only synthetic fixtures admitted")
    values = int8_vector(record["input"])
    observed = int8_vector(record["observed"])
    if len(values) != len(observed):
        raise ValueError("tensor shape mismatch")
    expected = [max(0, value) for value in values]
    return {"numeric_contract": "PASS" if observed == expected else "FAIL",
            "quantization": "shared_input_output_scale_and_zero_point_zero",
            "evidence_level": "SYNTHETIC_REPLAY_ONLY",
            "device_execution_verified": False, "silicon_activity_verified": False,
            "speedup_measured": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    try:
        result = check_probe(read_object(args.record))
    except (OSError, ValueError, UnicodeError):
        print(json.dumps({"numeric_contract": "INVALID_RECORD"}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0 if result["numeric_contract"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
