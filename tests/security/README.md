# Native security regression data

2026-11-10: [memory-commit](memory-commit/README.md) adds canonical XAX allocation
probes, positive controls, native transactions and MCP evolution/stale-root evidence.
Only XAX implementation was added. The broader pressure/escape/cancellation
release gates remain open.

`invalid-add-operand.edit` carries a native edit with an effect-token operand where bits32 is required. The historical
`.diag` proves the resulting candidate fails native verification. Current 0.10 MCP tests must reject the transaction,
retain the original valid source and delete `next.xax`; the candidate is never executed.

`timeout/timeout.xax` is an authoritative canonical XAX program that calls Windows Sleep(60000). Its exact-root native
construction carrier and native executable/provenance accompany it. The AppContainer/job launcher must terminate it
at approximately 10 seconds with timeout flag 1. CI rebuilds this fixture with the pinned native seed before running.

`tests/protocol/native-sessions.json` covers the new graph, stale roots, forbidden properties, malformed carriers,
read-only grants, execution denial, unsupported construction/results and zero expected roots. External CI orchestration
also tests shared-workdir refusal and lease release after a process crash. All program logic is native XAX.
These regressions do not constitute complete sandbox/escape/quota certification; release readiness remains false.

The [executor-input fixtures](executor-input/README.md) extend coverage to binary
stdin/EOF, independently observed argv, simultaneous streams, exact/over-limit
budgets, actual CPU enforcement, environment and continued confinement. CI also
terminates the launcher while its exact worker is alive and checks that the child
exits, stdin is removed and no successful metadata is published. The
[passing hosted-run record](../../docs/evidence/native-executor-ci-41314738774.json)
supplements the [local observations and retained failures](../../docs/evidence/native-executor-input-argv-20261101.json).
Actual WinAPI measurement-failure injection, in-flight compiler cancellation and
exhaustive creation/publication crash windows remain unverified.
