# Case study 2 — Evaluation integrity and guided repair

Valid JSON, parseable source, structural admissibility, correct behavior, and independent first-attempt success are different outcomes. A narrow static check can accept code that still contains the original algorithmic defect.

## Engineering work

The reviewed private evaluation tooling keeps static inspection separate from execution, checks stable test identities and fixture integrity, and records interventions without replacing the first attempt. Transport failures, skipped tests, and infrastructure errors are treated separately from behavioral failure.

A historical guided attempt satisfied a structural restriction while retaining a functional sorting defect. The defensible result is a documented example of structural compliance failing to establish behavioral repair. This release does not rescore that attempt or distribute its source, prompt, tests, or raw response.

The underlying records preserve failures and unsupported scope. Offline tooling checks do not establish model capability. A training reference script is not evidence of a trained adapter or learned improvement.

## Runnable example

`demos/result_contract.py` classifies a synthetic baseline/candidate record. It rejects mismatched test populations, impossible counts, and declared fixture changes; treats errors/skips as incomplete; and retains the guided category.

It does not run candidate code or authenticate the supplied record. The placeholder digest is not an acceptance-test attestation. The contribution demonstrated here is a precise result contract rather than a model-quality score.
