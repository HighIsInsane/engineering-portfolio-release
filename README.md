# Uzay Sağlam — Engineering Portfolio

Local LLM operations, evaluation infrastructure, and Android accelerator research. I work on making experimental systems observable and repeatable, and on keeping engineering conclusions within the available evidence.

This repository contains three engineering case studies and independently runnable synthetic examples. The underlying research repositories, implementation, original device records, task material, and histories remain private.

## Engineering case studies

| Study | Problem addressed | What you can verify here |
| --- | --- | --- |
| [Local LLM operations](case-studies/01-local-llm.md) | Identify the intended runtime and model before using a phone-hosted service | Defensive parsing of disclosed synthetic health and model records |
| [Evaluation integrity](case-studies/02-evaluation.md) | Distinguish structural validity, guided repair, and behavioral evidence | Classification of synthetic red/green records with stable test identities |
| [Android accelerator research](case-studies/03-android-accelerators.md) | Separate API selection, correct output, and hardware attribution | A hardware-free signed INT8 numerical oracle |

## Run the examples

Python 3.10+ and Git are required. No external Python packages, model downloads, credentials, server, phone, or paid API are needed.

```bash
python3 -m tools.validate --out validation-local
python3 -m demos.runtime_readiness --health fixtures/health.json --models fixtures/models.json --expected-alias portfolio-synthetic-model
python3 -m demos.result_contract fixtures/guided.json
python3 -m demos.numeric_probe fixtures/probe.json
python3 -m tools.audit_release
```

Use a fresh output directory for each validation run. The release scanner requires a Git checkout. The examples consume synthetic records: they do not invoke a model, execute generated code, access an accelerator, or authenticate historical evidence. The guided fixture uses an explicit placeholder digest.

## Evidence and scope

[Validation](reports/VALIDATION.md) · [Claim scope](reports/TRACEABILITY.md) · [Disclosure boundary](reports/WITHHELD.md) · [Release review](reports/PUBLICATION_READINESS.md) · [Provenance](PROVENANCE.md)

Historical device observations and private implementation review are described separately from the synthetic examples. They cannot be independently reproduced from this repository alone. Passing CI does not establish model quality, physical accelerator activity, training, customer acceptance, or revenue.

Development and portfolio preparation used AI assistance. This work does not assert sole manual authorship or independent third-party certification.

**Status: private release candidate. Publication requires explicit owner approval of the exact reviewed commit.**
