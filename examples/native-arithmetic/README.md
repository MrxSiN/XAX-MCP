# Native construction example — 0.9.0

Starting from `native/xax-mcp-seed.xax`, seven `xax_construct` calls apply typed `XAXEDIT1` records to construct
canonical semantics for `((40 + 7) * 3) - 5`. The client obtains each exact root and function CID through MCP query;
no external compiler read is needed to prepare the next request. Native edit applies each candidate, native verify
gates publication, and native build/execute returns the actual process-exit result **136** under OS confinement.
No arithmetic is implemented by the adapter or external client.

| File | Role |
|---|---|
| `program.xax` | Authoritative new canonical source (2,330 bytes) |
| `transactions/01.edit` through `07.edit` | Exact-root typed transport, in order |
| `program.exe`, `program.prov` | Native XAX-built executable and provenance |
| `requests.ndjson` | Current 0.9 discovery/query/construction/build/execute replay |

Final root: `236b15c2acc1ac10246b06ac5e23707cd3ffbb144507ca9bc52dd86286d6d8fb`.
Source SHA-256: `3454b07d7d958d8b15323d9d5a6e633db69b3449357b5f9fc78d9a22262d7658`.
Artifact SHA-256: `832a06e874a109c4cdaf4385e0b50e88b7b8070ee532da6544e3568eaedd2a07`.

The edits insert constant 7, add, constant 3, multiply, constant 5, subtract, then replace the original ExitProcess
operand. Every intermediate candidate also passed independent native verifier checks in the recorded audit.
Use the pinned native compiler from XAX `af376e8a8a1ac5635bcad459cb7063ef0b326430`, not an unrecorded local build.
[Installation and replay commands](../../docs/INSTALL_WINDOWS.md) set host compiler/store/private-work grants.
The native sandbox must be beside the server, and the replay needs `--allow-execute`.

The replay runs the seed (40), constructs the graph, rejects a stale transaction, builds/runs 136 twice, rejects the
unsupported JSON construction carrier and rejects a forged result handle. These expected errors do not indicate a
fallback. [Current transcript](../../docs/evidence/native-windows-x86_64-verified-construction-20261027.json)
records 28 checks. The [older transcript](../../docs/evidence/native-windows-x86_64-transaction-construction-20261027.json)
retains its previously failing security observations; those defects were repaired and retested in 0.9.

There are no typed runtime arguments/results here; the result is an observed unsigned process-exit value.
General runtime I/O and other [remaining gates](../../docs/WINDOWS_READINESS.md) are not implied by this example.
