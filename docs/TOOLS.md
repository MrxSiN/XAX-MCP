# Tool reference (`xax-mcp-tools-v1`)

Every tool returns one JSON object as `structuredContent`, mirrored as a compact text block. Success is
`{"ok": true, ...}`. Failure is `{"ok": false, "error": {"code", "message", "xax_diagnostic"?, "repair"?, "details"?}}`
with `isError: true`.

Error codes: `unsupported`, `invalid_request`, `verification_failed`, `stale_root`, `conflict`, `build_error`,
`denied_capability`, `resource_limit`, `runtime_failure`, `not_found`, `stale_artifact`, `sandbox_unavailable`,
`incompatible_xax`, `internal_error`.

Required rights (granted by launch flags, never by arguments): `read` for capabilities, workspace, query and
result; `mutate` for construct and transaction; `build` for build; `execute` for execute (`--allow-execute`).

## `xax_capabilities` `{}`
Reports the server and SDK versions, the XAX pin, fingerprint and compatibility status, and the compiler
identity. It lists the target (`linux-x86_64`, profile `x86_64-linux-elf-exec-v1`) with its verifier-supported
operations, carrier types and entities, and the process-entry contract. It also reports I/O modes, effects,
granted rights, limits, the sandbox probe, and a maturity label per feature.

## `xax_construct` `{request}`
`request` is an `xax-construct-v1` carrier (upstream `xax_construct.py` docstring):

```json
{"format": "xax-construct-v1", "platform": "linux-x86_64",
 "types": {"mem": "linux.memory_effect", "in": {"view": 4096}, ...},
 "functions": [{"name": "term", "params": ["b64"], "returns": ["b64"],
                "blocks": [{"params": ["b64"],
                            "nodes": [["mul.wrap", ["p0", "p0"], ["b64"]], ...],
                            "end": ["ret", ["n4"]]}]}, ...],
 "package": {"name": "polyreduce", "entries": {"app": "main"}, "release": "app"}}
```

Multi-byte integers in byte views (heap views of `linux.bytes_rw`): one checked access moves 1, 2, 4 or 8
bytes at a dynamic `b32` byte offset (`checked_byte_view_widths`, XAX ADR-231). The bounds check is
`offset + size <= extent`, and alignment stays 1:

```json
["checked.load.bits.le",  ["p0", "p3", "p2"],       ["b64", "mem"], {"attrs": [8, 1]}]
["checked.store.bits.le", ["p0", "p3", "p4", "p2"], ["mem"],        {"attrs": [8, 1]}]
```

The operands are view pointer, byte offset, (value,) memory effect. Other sizes fail verification with
`MEMORY-ACCESS-SIZE`.

List callees before their callers. The process entry takes only effect/proof parameters, ends with
`linux.exit_group`, and returns at most one integer (upstream `linux-x86_64-process-v1`). Available runtime
channels: `linux.read` on fd 0, `linux.write` on fds 1/2, `linux.startup.*` reads of argv/env/auxv (entry function
only), and the exit status. Bounds: 256 functions, 4096 blocks per function, 100 000 nodes,
nesting depth 12, integers within ±2^64, view extents up to 1 GiB, 1 MiB of arguments.

Returns `workspace`, `root` (canonical CID), `generation` 0, `entries`, `store` (bytes, sha256), and
`function_handles` (carrier name → workspace handle, e.g. `"term": "F1"`; informational only, because names are
transport).

## `xax_query` `{workspace, kind, handle?, limit?, continuation?, from_generation?}`
Kinds: `root`, `functions`, `function_nodes` (function handle), `function_view` (function handle; a
non-authoritative tooling view plus alias map), `operands`, `neighborhood`, `uses` (node or value handle),
`callers`, `callees` (function handle), `type`, `effects`, `effect_summary`, `entity`, `proof`, `diff`
(`from_generation`), and `repair` (a `diag_…` handle from a rejected transaction). Pages carry `truncated` and
`continuation`. The upstream response budget is 16 KiB.

## `xax_transaction` `{workspace, mode, expected_generation, expected_root, mutations[], read_set?}` / `{workspace, mode: "rollback", candidate}`
`mode`: `verify` (private candidate; root unchanged; returns `candidate`), `commit`, or `rollback`. Mutations
(handles must have been exposed by a query at this generation):

| op | fields |
|---|---|
| `set_constant` | `node`, `value` |
| `set_operation` | `node`, `value` (`add.wrap`, `sub.wrap`, `mul.wrap`) |
| `replace_operand` | `node`, `index`, `value` (value handle, or `@ID` for an inserted node) |
| `delete` / `prune_dead` | `node` |
| `move` | `node`, `before` |
| `insert_constant` | `anchor`, `id`, `value` |
| `set_edge` | `anchor`, `edge`, `argument`, `value` |
| `set_type` | `target`, `type`, optional `result` |
| `set_signature` | `function`, `params[]`, `returns[]` (type handles) |

A mismatched generation or root returns `stale_root` with the current values. Re-query and rebuild the edit;
the server never refreshes on its own. A verifier rejection returns the XAX diagnostic projected onto exposed
handles plus a `diag_…` handle for the repair query.

## `xax_build` `{workspace, entry?, expected_generation?}`
Returns `artifact` (`art_…`), `bytes`, `artifact_digest_blake3`, `artifact_sha256`, `executable_here`,
`cache` (`hit`/`miss`), `build_ms`, and `provenance`: `build_key`, `provenance_cid`, the decoded provenance
object (snapshot root, request root, target, profile, artifact digest, compiler and lowering identity),
`target_profile`, `xax_toolchain_fingerprint`, `xax_commit`, `xax_native_components`, `snapshot_root`,
`workspace_root`, and `generation`.

## `xax_execute` `{artifact, input?, argv?, output?, effects?, limits?, require_current?}`
- `input`: one of `{"ints": [{"type": "b8|b16|b32|b64", "value": N}]}` (little-endian, concatenated),
  `{"bytes_base64": "..."}`, or `{"text": "..."}`. At most 1 MiB.
- `argv`: up to 64 strings (no NUL, at most 64 KiB in total) that become `argv[1:]`. Programs read them with
  `linux.startup.argc`/`arg_length`/`arg_copy` in the entry function. They are passed as separate execve
  arguments, never through a shell.
- `output`: `"bytes"` (default), `"text"`, or `{"ints": ["b64", ...]}`. A length mismatch is reported
  (`layout_matched: false`) and never padded.
- `effects`: only `stdio`. Anything else is `denied_capability`.
- `limits`: `wall_ms`, `cpu_seconds`, `memory_mb`, `max_output_bytes`. These can only lower the host's limits.
- Returns `exit_status`, `signal`, `status` (`exited`/`trap`/`crashed`), `stdout` (inline up to 4 KiB, plus
  `stdout_result` for the rest), bounded `stderr`, and `evidence` (label `EXECUTED`, sandbox mechanism, limits,
  verified artifact digest, build key, root, and wall time).

## `xax_result` `{handle, offset?, length?}`
Bounded chunks of at most 64 KiB, base64-encoded, from a `res_…` stdout, a `ws_…` canonical store (for export
and reopening), or a `diag_…` diagnostic.

## Worked example (generic client)
`examples/generic_client.py` runs the whole loop with `examples/carriers/poly_reduce.json`:

```text
xax_capabilities → xax_construct(carrier) → xax_build(ws) → xax_execute(art, ints [1,2,3], layout [b64,b64])
→ values [93, 3]   # 3·(1+4+9) + 5·(1+2+3) + 3·7, max = 3, computed by the XAX-generated executable
```
