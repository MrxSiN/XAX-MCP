# Native release-gate regressions

These are transport fixtures and observed native diagnostics. They are not application source or passing
release claims. The full observations are in
[`native-windows-x86_64-transaction-construction-20261027.json`](../../docs/evidence/native-windows-x86_64-transaction-construction-20261027.json).

`invalid-add-operand.edit` expects the canonical seed root and inserts an add of node 0's bits32 result and
parameter 0's effect token. Correct behavior is rejection before publication, with the seed root and generation
unchanged. Current behavior is a successful MCP transaction publishing an invalid candidate. Independent native
verification returns exit 1, `XAX.STRUCT.OP_TYPE / GRAPH-OP-TYPE`; `invalid-add-operand.diag` is its exact binary
record. Never execute this candidate. Reproduce only with a fresh, isolated scratch workspace.

Query `{ "path": "../../private" }` and build `{ "command": "cmd.exe" }` must return `invalid_request` because
their schemas disallow properties. The current server ignores those properties and reports success. The test
observed the unchanged seed root/build; it did not observe arbitrary file access or shell execution.

Current CI is a native smoke gate, not a passing security gate. These failing cases remain explicitly tracked
until canonical server transactions fix them and native end-to-end checks demonstrate rejection and cleanup.
