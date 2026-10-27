# Native semantic transaction construction

This is an **EXECUTED, narrow prototype**. Starting from `native/xax-mcp-seed.xax`, seven native XAX transactions
produce a new canonical graph computing `((40 + 7) * 3) - 5`. MCP `xax_build` compiles that graph;
`xax_execute` runs its executable under Windows confinement and returns exit result **136**.
No arithmetic is implemented in the adapter or the external test client.

| File | Meaning |
|---|---|
| `program.xax` | Authoritative new canonical semantic source, 2,330 bytes |
| `transactions/01.edit` through `07.edit` | Exact-root `XAXEDIT1` transport records, applied in order |
| `program.exe` | Actual XAX-built Windows artifact, 1,536 bytes |
| `program.prov` | Native build provenance, 268 bytes |
| `requests.ndjson` | Single-session MCP replay, including expected failure cases |

Final root: `236b15c2acc1ac10246b06ac5e23707cd3ffbb144507ca9bc52dd86286d6d8fb`.
Source SHA-256: `3454b07d7d958d8b15323d9d5a6e633db69b3449357b5f9fc78d9a22262d7658`.
Artifact SHA-256: `832a06e874a109c4cdaf4385e0b50e88b7b8070ee532da6544e3568eaedd2a07`.

The records insert constant 7, add, constant 3, multiply, constant 5, subtract, then replace the original
`ExitProcess` input with the new subtraction result. Every record names the current function CID and root.
Each intermediate candidate passed a separate native verifier invocation. Multiple inserts at the same anchor
in one transaction were rejected by the native editor's unique-mutation-target rule; the successful example
uses separate exact-root transactions. This is native semantic construction by edits, not a JSON decoder test.

To reproduce the MCP experiment, the host must grant the exact tested native compiler or independently certify
a compatible one. Its SHA-256 is `ff0355c5bf148bc79cf463748a285c3f982b6c8e47faf8d2d25bd3571b2ad638`;
it is a recovered local prototype and is not distributed here. Set `XAX_MCP_COMPILER` to that executable,
`XAX_MCP_STORE` to this checkout's seed store, and `XAX_MCP_WORK` to a fresh, empty, dedicated directory. Then
feed `requests.ndjson` to `native/xax-mcp-native.exe --allow-execute` over stdin. The host must have the committed
sandbox executable beside the server. Do not share a work directory with another session.

Responses 6, 18 and 19 report exit results 40, 136 and 136. Request 15 deliberately replays a stale transaction;
20 checks the absent decoder and 21 checks an unsupported result handle. Those failures are expected. The
complete observed transcript is in
[`docs/evidence/native-windows-x86_64-transaction-construction-20261027.json`](../../docs/evidence/native-windows-x86_64-transaction-construction-20261027.json).

CI can run the committed executable in the native sandbox without a compiler or interpreter. That validates the
recorded artifact's behavior, not a rebuild or the full construction path. This program has no typed runtime
arguments or outputs; its result is the process exit status. See [release blockers](../../docs/WINDOWS_READINESS.md)
before enabling mutation/execution in an agent host.
