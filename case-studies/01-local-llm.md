# Case study 1 — Local LLM operations on Android

A phone-hosted model needs reliable identification of its model file, runtime, transport, and operating state. Seeing a process in a terminal is insufficient evidence that the intended model is ready.

## Engineering work

The reviewed private operational tooling verifies pinned files before starting a CPU-based local inference server in Termux. Host-side checks establish an authorized device connection and inspect service health and advertised model identity. Startup and generation are separate operations. Response capture is bounded and distinguishes complete, truncated, oversized, and failed responses.

The private records describe local model operation across phone and host. Those are historical observations, not a fresh device qualification for this release. Metadata and aliases alone cannot authenticate weights or prove current liveness. No latency, throughput, thermal, energy, or commercial-readiness claim is made.

## Runnable example

`demos/runtime_readiness.py` validates saved synthetic health/model records. It rejects duplicate JSON keys, ambiguous identities, malformed records, and oversized input. It explicitly denies live-service and runtime-identity attestation.

The example does not start a server, call a model, contain private device addresses, or reproduce the private operations tooling. Its purpose is to demonstrate defensive validation and precise evidence boundaries.
