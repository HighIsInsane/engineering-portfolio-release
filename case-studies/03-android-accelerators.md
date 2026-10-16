# Case study 3 — Android accelerator evidence levels

Loading a vendor library, discovering a device, compiling a graph, obtaining correct output, and independently observing hardware activity answer different questions.

## Engineering work

The reviewed private Android/native probes progress through library visibility, device discovery, explicit target selection, and numerical output checks. A small signed INT8 graph provides a tractable correctness contract. A separate runtime path requires generated dependencies; an ordinary build can select a stub, so successful compilation alone does not establish real device execution.

Historical retail-device reports record successful API/runtime execution with expected output. The private investigation also retains unsuccessful attempts to obtain independent hardware attribution through available telemetry interfaces. Those observations were not rerun for this release.

No physical silicon utilization, full LLM acceleration, speedup, sustained performance, or energy benefit is claimed. A successful build or diagnostic audit only establishes its own documented scope.

## Runnable example

`demos/numeric_probe.py` is a hardware-free signed INT8 ReLU oracle with synthetic input. It checks shape, integer type, range, and output correctness under a shared positive input/output scale and zero point zero. Tests cover the complete signed INT8 domain.

The example never loads a vendor library or accesses a device. Its output explicitly denies device-execution, silicon-activity, and speedup verification. Vendor definitions, binaries, device traces, and original native source remain private.
