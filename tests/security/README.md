# Native security regression data

`invalid-add-operand.edit` carries a native edit with an effect-token operand where bits32 is required. The historical
`.diag` proves the resulting candidate fails native verification. Current 0.9 MCP tests must reject the transaction,
retain the original valid source and delete `next.xax`; the candidate is never executed.

`timeout/timeout.xax` is an authoritative canonical XAX program that calls Windows Sleep(60000). Its exact-root native
construction carrier and native executable/provenance accompany it. The AppContainer/job launcher must terminate it
at approximately 10 seconds with timeout flag 1. CI rebuilds this fixture with the pinned native seed before running.

`tests/protocol/native-sessions.json` covers the new graph, stale roots, forbidden properties, malformed carriers,
read-only grants, execution denial, unsupported construction/results and zero expected roots. External CI orchestration
also tests shared-workdir refusal and lease release after a process crash. All program logic is native XAX.
These regressions do not constitute complete sandbox/escape/quota certification; release readiness remains false.
