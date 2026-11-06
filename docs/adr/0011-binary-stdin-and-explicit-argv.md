# 0011 — Binary stdin and explicit argv for the current artifact

Date: 2026-11-01. Status: implemented and tested for the 0.10 Windows preview;
production release acceptance remains false.

The previous executor could run the authorized build but could not deliver the
binary input or arguments required by downstream process clients. Extend only
`xax_execute` with optional `stdin_hex` and `args`, excluding executor-controlled
argv[0]. Omitted fields preserve empty input and no extra arguments. Do not expose
executable paths, shell commands, environment overrides, filesystem grants or
per-call resource increases.

Implement validation, Windows quoting and process supervision as canonical XAX
semantic graphs, using exact-root native transactions and mandatory candidate
verification. Preserve unchanged objects by identity and use the existing pinned
native compiler. No compiler/BBC change or foreign runtime helper is required.

Use a private binary regular-file stdin handle with physical EOF, duplicate only
read access, and inherit only stdin and the two output write handles. Supply an
explicit process path and bounded environment; attach the capability-less
AppContainer and job at process creation and verify membership before resume.
Drain stdout/stderr concurrently within a combined host budget. Independently
observe argv and byte streams with native synthetic probes.

Measure actual user/kernel CPU, wall time and peak process commit. Sample and
enforce total CPU rather than assuming job configuration proves timely enforcement.
Report sampling overshoot. Unknown measurements stay absent. Child exit, setup,
budget exhaustion, incomplete transport, measurement and cleanup failures remain
distinct; partial output or failed cleanup cannot be successful execution.

The [execution contract](../NATIVE_EXECUTION_INCREMENT.md) defines installed host
bounds and result semantics; these are transport/execution capabilities, not
permanent XAX limits. [Local acceptance](../evidence/native-executor-input-argv-20261101.json)
and [hosted CI](../evidence/native-executor-ci-41314738774.json) establish the tested
scope. CUM transformations/full prepare, registered external tools, typed layouts,
complete cancellation/crash handling and independent escape review remain separate
work. This decision extends [ADR-0010](0010-native-verified-windows-contract.md)
and replaces neither semantic verification nor host authorization.
