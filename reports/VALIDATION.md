# Validation scope

Run `python3 -m tools.validate --out validation-local` to create per-test outcomes, source digests, and an execution log in a new directory. The committed evidence records the release preparation run; later runs belong in their own output directories.

The test suites exercise synthetic metadata validation, repair-record classification, numeric contracts, CLI behavior, and privacy checks. They do not evaluate an LLM, execute model-generated source, reproduce Android device behavior, or qualify an operating-system sandbox.

Private source-tool totals, historical benchmark scores, internal suite names, and CI identifiers are intentionally excluded. Existing private results were preserved, including failures and skipped scope.

The disclosure scanner checks allowlisted files, reachable commit trees, commit/ref/tag metadata, and selected ignored sensitive files. It rejects known credential patterns, private contact/network/path formats, private source locators, unexpected files, and unsuitable Git modes. A clean scan is a bounded check, not a guarantee against all possible disclosures.
