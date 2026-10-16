# Evidence and claim scope

REVIEWED means implementation or recorded results were inspected. HISTORICAL means a prior device observation was recorded, without a fresh device rerun for this release. SYNTHETIC means a newly authored example can be run from this checkout. These are internal review categories, not third-party certification.

| ID | Claim | Evidence available here | Limitation |
| --- | --- | --- | --- |
| LLM-01 | Private operations tooling checks runtime/model identity before use | REVIEWED summary in case study 1 | Private implementation and historical device records withheld |
| LLM-02 | Saved model/health records can be checked defensively | SYNTHETIC runtime-readiness example and tests | No live service, model weights, or liveness attestation |
| EVAL-01 | Test identity, skips, and guided interventions affect repair classification | SYNTHETIC result-contract example and tests | Input records are assertions, not authenticated executions |
| EVAL-02 | Structural compliance can coexist with an algorithmic defect | HISTORICAL summary in case study 2 | No new model score or candidate execution asserted |
| EVAL-03 | Private tooling retains failed attempts and blocks unsupported conclusions | REVIEWED summary in case study 2 | Private test totals, scores, and task material withheld |
| APU-01 | API selection, numeric correctness, and physical attribution need separate evidence | REVIEWED and HISTORICAL summary in case study 3 | No fresh hardware run or performance result |
| APU-02 | A signed INT8 ReLU contract can be checked without hardware | SYNTHETIC numeric-probe example and tests | Shared scale and zero point zero assumed; no vendor API invoked |
| SAFE-01 | The disclosed payload has an explicit file boundary and privacy checks | Release allowlist and disclosure scanner | Heuristic scanner; owner review still required |

Per-test results and hashes for the disclosed code are in the validation evidence. No locator in this document grants access to private work. Reproducing the historical device work would require a separately reviewed and authorized release.
