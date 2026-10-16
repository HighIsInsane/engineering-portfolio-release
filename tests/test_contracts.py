import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from demos.runtime_readiness import check_metadata, read_object, MAX_BYTES
from demos.result_contract import classify
from demos.numeric_probe import check_probe

ROOT = Path(__file__).resolve().parents[1]


class RuntimeMetadataTests(unittest.TestCase):
    def test_metadata_pass_does_not_attest_live_runtime(self):
        result = check_metadata({"status": "ok"}, {"data": [{"id": "demo"}]}, "demo")
        self.assertFalse(result["inference_performed"])
        self.assertFalse(result["live_health_verified"])
        self.assertFalse(result["runtime_identity_attested"])

    def test_loading_state_rejected(self):
        with self.assertRaises(ValueError):
            check_metadata({"status": "loading"}, {"data": [{"id": "demo"}]}, "demo")

    def test_alias_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            check_metadata({"status": "ok"}, {"data": [{"id": "other"}]}, "demo")

    def test_duplicate_alias_rejected(self):
        with self.assertRaises(ValueError):
            check_metadata({"status": "ok"}, {"data": [{"id": "demo"}] * 2}, "demo")

    def test_malformed_model_entries_rejected(self):
        for rows in (None, [], [None], [{"id": True}], [{"id": ""}]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                check_metadata({"status": "ok"}, {"data": rows}, "demo")

    def test_empty_expected_alias_rejected(self):
        with self.assertRaises(ValueError):
            check_metadata({"status": "ok"}, {"data": [{"id": "demo"}]}, " ")

    def test_invalid_json_inputs_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "input.json"
            for raw in ('{"a":1,"a":2}', '{"a":NaN}', '[]', '{'):
                p.write_text(raw)
                with self.subTest(raw=raw), self.assertRaises(ValueError):
                    read_object(p)

    def test_size_limit_enforced_before_json_parse(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "large.json"
            p.write_bytes(b" " * (MAX_BYTES + 1))
            with self.assertRaisesRegex(ValueError, "too large"):
                read_object(p)

    def test_symlink_input_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "target.json"
            target.write_text("{}")
            link = Path(folder) / "link.json"
            link.symlink_to(target)
            with self.assertRaises(ValueError):
                read_object(link)


class RepairClassificationTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / "fixtures/guided.json").read_text())

    def test_guided_pass_keeps_attempt_category(self):
        result = classify(self.record)
        self.assertEqual(result["classification"], "GUIDED_REPAIR_PASS")
        self.assertFalse(result["evidence_authenticity_verified"])
        self.assertFalse(result["candidate_code_executed"])
        self.assertFalse(result["historical_scores_modified"])

    def test_input_is_unchanged(self):
        before = copy.deepcopy(self.record)
        classify(self.record)
        self.assertEqual(self.record, before)

    def test_first_attempt_label_requires_first_record(self):
        self.record["attempt"] = "first"
        self.assertEqual(classify(self.record)["classification"], "FIRST_ATTEMPT_REPAIR_PASS")

    def test_no_red_baseline_is_not_repair(self):
        self.record["baseline"]["failures"] = 0
        self.assertEqual(classify(self.record)["classification"], "NO_RED_BASELINE")

    def test_candidate_failures_remain_failures(self):
        self.record["candidate"]["failures"] = 1
        self.assertEqual(classify(self.record)["classification"], "REPAIR_FAIL")

    def test_skip_or_error_is_incomplete(self):
        for side in ("baseline", "candidate"):
            for field in ("errors", "skips"):
                record = copy.deepcopy(self.record)
                record[side][field] = 1
                with self.subTest(side=side, field=field):
                    self.assertEqual(classify(record)["classification"], "INCOMPLETE")

    def test_equal_counts_different_test_identities_rejected(self):
        self.record["candidate"]["test_ids"] = ["case_a", "changed"]
        with self.assertRaises(ValueError):
            classify(self.record)

    def test_duplicate_or_empty_test_population_rejected(self):
        for ids in ([], ["x", "x"], [""]):
            self.record["candidate"]["test_ids"] = ids
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                classify(self.record)

    def test_boolean_negative_and_impossible_counts_rejected(self):
        for value in (True, -1, "0", 3):
            self.record["candidate"]["failures"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                classify(self.record)

    def test_fixture_mutation_rejected(self):
        self.record["fixtures_unchanged"] = False
        with self.assertRaises(ValueError):
            classify(self.record)

    def test_unreviewed_origin_rejected(self):
        self.record["origin"] = "external_unreviewed"
        with self.assertRaises(ValueError):
            classify(self.record)

    def test_missing_or_extra_fields_rejected(self):
        for record in ({k: v for k, v in self.record.items() if k != "attempt"}, dict(self.record, claimed_revenue=1)):
            with self.assertRaises(ValueError):
                classify(record)

    def test_invalid_digest_rejected(self):
        self.record["tests_sha256"] = "unknown"
        with self.assertRaises(ValueError):
            classify(self.record)


class NumericContractTests(unittest.TestCase):
    def test_exhaustive_signed_int8_domain(self):
        values = list(range(-128, 128))
        observed = [0] * 128 + list(range(128))
        result = check_probe({"origin": "synthetic_portfolio", "input": values, "observed": observed})
        self.assertEqual(result["numeric_contract"], "PASS")
        for field in ("device_execution_verified", "silicon_activity_verified", "speedup_measured"):
            self.assertFalse(result[field])

    def test_wrong_output_remains_fail(self):
        self.assertEqual(check_probe({"origin": "synthetic_portfolio", "input": [-1, 2], "observed": [0, 3]})["numeric_contract"], "FAIL")

    def test_shape_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            check_probe({"origin": "synthetic_portfolio", "input": [1, 2], "observed": [1]})

    def test_non_int8_vectors_rejected(self):
        for values in ([], [True], [1.0], [-129], [128], ["1"]):
            with self.subTest(values=values), self.assertRaises(ValueError):
                check_probe({"origin": "synthetic_portfolio", "input": values, "observed": [0]})

    def test_unreviewed_origin_rejected(self):
        with self.assertRaises(ValueError):
            check_probe({"origin": "external_unreviewed", "input": [1], "observed": [1]})


class CLITests(unittest.TestCase):
    def test_three_offline_demos(self):
        commands = [
            ["demos.runtime_readiness", "--health", "fixtures/health.json", "--models", "fixtures/models.json", "--expected-alias", "portfolio-synthetic-model"],
            ["demos.result_contract", "fixtures/guided.json"],
            ["demos.numeric_probe", "fixtures/probe.json"],
        ]
        for args in commands:
            with self.subTest(module=args[0]):
                result = subprocess.run([sys.executable, "-m", *args], cwd=ROOT, capture_output=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr.decode())
                self.assertIsInstance(json.loads(result.stdout), dict)

    def test_bad_input_cli_returns_failure(self):
        result = subprocess.run([sys.executable, "-m", "demos.numeric_probe", "fixtures/health.json"], cwd=ROOT, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
