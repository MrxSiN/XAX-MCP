# Current tool surface — 0.9.0

The exact emitted schema is [tools-v2.json](../schemas/tools-v2.json). Input JSON is transport; canonical semantic
stores are source. Every tool rejects unsupported properties. Rights come from host launch configuration.

| Tool | Input | Native behavior |
|---|---|---|
| `xax_capabilities` | `{}` | Identity, pinned compiler contract, target/input/result modes, rights, limits and maturity |
| `xax_workspace` | `{}` | Describe the single host workspace, root, bytes, first function CID |
| `xax_query` | `{}` | Same bounded native inspection; first function is CID-ordered, not necessarily entry |
| `xax_construct` | `{"record":"<hex XAXEDIT1>"}` | Native exact-root edit, candidate verification, atomic publication |
| `xax_transaction` | `{"record":"<hex XAXEDIT1>"}` | Same verified transaction path |
| `xax_build` | `{}` | Native resolve/build current source; exact root, artifact byte count and provenance hex |
| `xax_execute` | `{}` | Rebuild current source and run in native AppContainer/job; return actual exit, flags, bounded capture |
| `xax_result` | Schema-described handle request | Unsupported; fails closed |

`record` is hexadecimal transport capped by the schema and native request bounds. Every public mutation must carry
a nonzero exact expected root; native edit checks freshness. Upstream defines `XAXEDIT1`; the adapter does not
implement graph semantics. No JSON `xax-construct-v1` decoder is needed or supported in this preview.

Queries inspect at most 65,536 native bytes. No generic graph queries, paging, scoped workspace lifecycle or monotonic
generation are claimed. `ws_0` is a descriptive label, not an accepted object capability. One process owns an exclusive
OS lease on compiler scratch until exit; another gets `workspace_busy` and may retry.

Results use MCP text plus matching `structuredContent` and `isError`. Native compiler failures are compact existing
adapter codes such as `transaction_rejected`; detailed structured verifier neighborhoods are not yet transported.
Zero expected roots and malformed/unknown arguments return `invalid_request`; missing grants return
`denied_capability`. General runtime input, effects, per-call quotas and artifact selection are rejected.

The schema upgrade changes `xax_construct` from the obsolete `{request: ...}` prototype to `{record: ...}`. Clients
must rediscover schemas. Its `idempotentHint` is false. The constant `generation:1` response was removed; compare roots.
