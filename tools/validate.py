"""Run offline synthetic tests and preserve per-test outcomes and source hashes."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outcomes = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.outcomes.append({"test": test.id(), "status": "PASS"})

    def addFailure(self, test, error):
        super().addFailure(test, error)
        self.outcomes.append({"test": test.id(), "status": "FAIL"})

    def addError(self, test, error):
        super().addError(test, error)
        self.outcomes.append({"test": test.id(), "status": "ERROR"})

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.outcomes.append({"test": test.id(), "status": "SKIP", "reason": reason})


def source_hashes() -> dict:
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ("demos", "tests", "tools", "fixtures")
            for p in sorted((ROOT / folder).rglob("*"))
            if p.is_file() and not p.is_symlink() and p.suffix in (".py", ".json")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "validation-local")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    before = source_hashes()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=RecordedResult).run(suite)
    unchanged = before == source_hashes()
    complete = (result.testsRun > 0 and result.wasSuccessful() and not result.skipped and
                not result.expectedFailures and not result.unexpectedSuccesses and unchanged)
    raw = stream.getvalue().encode()
    (args.out / "unittest.log").write_bytes(raw)
    report = {
        "status": "PASS" if complete else "FAIL_OR_INCOMPLETE", "python": platform.python_version(),
        "platform": sys.platform, "tests": result.testsRun,
        "passed": result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped) - len(result.expectedFailures) - len(result.unexpectedSuccesses),
        "failures": len(result.failures), "errors": len(result.errors), "skips": len(result.skipped),
        "expected_failures": len(result.expectedFailures), "unexpected_successes": len(result.unexpectedSuccesses),
        "outcomes": result.outcomes, "source_sha256": before, "sources_unchanged": unchanged,
        "log_sha256": hashlib.sha256(raw).hexdigest(), "scope": "synthetic_portfolio_only",
        "new_model_inference": 0, "device_tests": "NOT_RUN", "candidate_code_execution": False,
    }
    (args.out / "validation.json").write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in ("status", "tests", "passed", "failures", "errors", "skips")}))
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
