# Evidence and claim labels

Labels: **PROVEN** (formal or exhaustive argument), **EXECUTED** (ran end to end and checked against an
independent oracle), **MEASURED** (raw samples recorded), **STRUCTURAL** (present and wired, but not exercised end
to end), **PROTOTYPE** (works for a narrow case), **UNIMPLEMENTED**.

Evidence files are append-only. A new pin, build or capability writes a new file; older files are never edited.
Raw samples for the current build are in `docs/evidence/native-windows-x86_64-build-f79b532-r2.json` and
`docs/evidence/native-windows-x86_64-chain-f79b532.json`. The earlier `native-windows-x86_64-build-f79b532.json`
and `native-windows-x86_64-protocol-f79b532.json`, the 6885f89 native files, and every Python-era file remain
unchanged.

## Current native server (0.7.0)

| Claim | Label | Evidence |
|---|---|---|
| An MCP client initializes the native STDIO server, negotiates four handshake versions, discovers the eight tool schemas, and calls tools | EXECUTED | `tests/test_native_stdio.py`; 43 passed, 1 skipped on Windows 11 x86-64 (the skip is the untestable Linux build) |
| The server is an XAX-built PE32+ and the committed canonical store is reproducible | EXECUTED | store root `9a511d00...1f1a`; store SHA-256 `0bd08c0e...154b`; artifact SHA-256 `2c244f56...1dd8`; `test_build_is_deterministic` |
| No Python, MCP SDK, shell wrapper, or other non-XAX service is on the request path | EXECUTED | the executable imports kernel32 and msvcrt only (no Python DLL); the test client is external; `xax_capabilities.server.python_on_request_path` is false |
| The native JSON validator matches Python's strict RFC 8259/UTF-8 parser | EXECUTED | 1500 randomized cases in `test_json_validation_matches_python_strict_parser` |
| Host rights come only from launch configuration, never from tool arguments | EXECUTED | 7 flag sets and 8 rejected forms in `test_host_rights_come_from_launch_flags` / `test_unknown_flags_fail_closed` |
| The official MCP Python SDK client interoperates (STDIO) | EXECUTED | `test_standard_sdk_client` (`mcp.Client`, mcp 2.3.0) |
| The server describes the current store, resolves and builds it, and applies one XAXEDIT1 transaction through a host-granted native compiler | PROTOTYPE | `test_native_compiler_chain_over_stdio`; seed root `572f683e...1587`, 1536-byte artifact, 268-byte provenance, record 40 -> 41, new root `8c01664c...1e97`; `native-windows-x86_64-chain-f79b532.json` |
| Compiler-backed latency (native, one seed program) | MEASURED | `native-windows-x86_64-chain-f79b532.json`: initialize 18.0 ms, query 0.140 ms, build 44.1 ms, transaction 22.0 ms, peak working set 9.18 MB |
| Protocol latency and memory (native, protocol layer only) | MEASURED | `native-windows-x86_64-protocol-f79b532.json` (0.6.0 artifact; protocol code unchanged): initialize 11.5 ms, ping 17.5 us, tools/list 97.1 us, capabilities 43.0 us, peak working set 8.16 MB |
| `xax_capabilities` reports the exact pin, rights, grants, and blockers | EXECUTED | every test calls it; the payload names each tool's status and the compiler grant |
| `xax_workspace`, `xax_query`, `xax_build`, `xax_transaction` | PROTOTYPE | implement root description, resolve+build, and one XAXEDIT1 edit over a host-granted native compiler; fail closed with `denied_capability` without the grant; docs/NATIVE.md B1/B2 |
| `xax_construct` | UNIMPLEMENTED | no native carrier decoder; structured `unsupported` |
| `xax_execute` | UNIMPLEMENTED | `denied_capability` without the host grant; `unsupported` with it; no native sandbox (B4) |
| `xax_result` | UNIMPLEMENTED | needs session state; structured `unsupported` |
| A novel computation is constructed, built, and executed through MCP | UNIMPLEMENTED | the prototype edits and builds a fixed seed; no construct and no execution |
| Sandbox isolation and resource limits | UNIMPLEMENTED | execution is refused, not sandboxed |
| Streamable HTTP transport | UNIMPLEMENTED | STDIO only |

The MCP latencies are tool round trips on one shared host. They are not XAX R4 generated-code benchmarks, and they
are not the deferred AI-token efficiency milestone. The chain measurements include the native compiler child
process; the server's own handling is sub-millisecond.

## Historical Python adapter (0.1.0 - 0.5.1)

These claims were executed by the retired Python server and are kept for provenance and for the porting work. They
are not claims about the 0.7.0 native server.

| Claim | Label | Evidence |
|---|---|---|
| Python adapter constructed, built, and executed novel computations on Linux and Windows | EXECUTED | `docs/evidence/e2e-*-0.5.1.json`, `e2e-windows-x86_64-warm-in-process-unreleased-44b5f3c.json`, and the historical tests in git history |
| Python sandbox denied filesystem/network access and enforced limits | EXECUTED | `tests/test_security.py` in git history |
| Warm-server start-up: first construct+build+execute about 0.2 s | MEASURED | `docs/evidence/*-0.5.1.json`; `docs/PERFORMANCE.md` (historical) |
| Codex/Claude registration and MCP Inspector | STRUCTURAL | `docs/HOSTS.md` (historical); no model-driven session |

Do not reinterpret those runs as evidence for the native server. The native server's compiler-backed tools are a
narrow prototype, and it executes nothing.
