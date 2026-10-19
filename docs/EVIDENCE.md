# Evidence and claim labels

Labels: **PROVEN** (formal or exhaustive argument), **EXECUTED** (ran end to end and checked against an
independent oracle), **MEASURED** (raw samples recorded), **STRUCTURAL** (present and wired, but not exercised end
to end), **PROTOTYPE** (works for a narrow case), **UNIMPLEMENTED**.

Evidence files are append-only. A new pin or build writes a new file; older files are never edited. Raw samples for
the current build are in `docs/evidence/native-windows-x86_64-protocol-f79b532.json` and
`docs/evidence/native-windows-x86_64-build-f79b532.json`. The 6885f89 native evidence file and every Python-era
file remain unchanged.

## Current native server (0.6.0)

| Claim | Label | Evidence |
|---|---|---|
| An MCP client initializes the native STDIO server, negotiates four handshake versions, discovers the eight tool schemas, and calls tools | EXECUTED | `tests/test_native_stdio.py`; 42 passed on Windows 11 x86-64 |
| The server is an XAX-built PE32+ and the committed canonical store is reproducible | EXECUTED | store root `2a87c9e5…a238`; store SHA-256 `c367233a…917e`; artifact SHA-256 `b98ea071…23d6`; `test_build_is_deterministic` |
| No Python, MCP SDK, shell wrapper, or other non-XAX service is on the request path | EXECUTED | the executable's imports are kernel32 only; the test client is external; `xax_capabilities.server.python_on_request_path` is false |
| The native JSON validator matches Python's strict RFC 8259/UTF-8 parser | EXECUTED | 1500 randomized cases in `test_json_validation_matches_python_strict_parser` |
| Host rights come only from launch configuration, never from tool arguments | EXECUTED | 7 flag sets and 8 rejected forms in `test_host_rights_come_from_launch_flags` / `test_unknown_flags_fail_closed` |
| The official MCP Python SDK client interoperates (STDIO) | EXECUTED | `test_standard_sdk_client` (`mcp.Client`, mcp 2.3.0) |
| Protocol latency and memory (native, protocol layer only) | MEASURED | `native-windows-x86_64-protocol-f79b532.json`: initialize 11.5 ms, ping 17.5 µs, tools/list 97.1 µs, capabilities 43.0 µs, peak working set 8.16 MB |
| `xax_capabilities` reports the exact pin, rights, and blockers | EXECUTED | every test calls it; the payload names B1/B2/B4 |
| `xax_workspace`, `xax_query`, `xax_construct`, `xax_transaction`, `xax_build`, `xax_result` | UNIMPLEMENTED | structured `unsupported`; docs/NATIVE.md B1/B2 |
| `xax_execute` | UNIMPLEMENTED | `denied_capability` without the host grant; `unsupported` with it; no native sandbox (B4) |
| A novel computation is constructed, built, and executed through MCP | UNIMPLEMENTED | not claimable until the native compiler service and sandbox exist |
| Sandbox isolation and resource limits | UNIMPLEMENTED | execution is refused, not sandboxed |
| Streamable HTTP transport | UNIMPLEMENTED | STDIO only |

The MCP latencies are tool round trips on one shared host. They are not XAX R4 generated-code benchmarks, and they
are not the deferred AI-token efficiency milestone.

## Historical Python adapter (0.1.0 - 0.5.1)

These claims were executed by the retired Python server and are kept for provenance and for the porting work. They
are not claims about the 0.6.0 native server.

| Claim | Label | Evidence |
|---|---|---|
| Python adapter constructed, built, and executed novel computations on Linux and Windows | EXECUTED | `docs/evidence/e2e-*-0.5.1.json`, `e2e-windows-x86_64-warm-in-process-unreleased-44b5f3c.json`, and the historical tests in git history |
| Python sandbox denied filesystem/network access and enforced limits | EXECUTED | `tests/test_security.py` in git history |
| Warm-server start-up: first construct+build+execute about 0.2 s | MEASURED | `docs/evidence/*-0.5.1.json`; `docs/PERFORMANCE.md` (historical) |
| Codex/Claude registration and MCP Inspector | STRUCTURAL | `docs/HOSTS.md` (historical); no model-driven session |

Do not reinterpret those runs as evidence for the native server. The native server has no compiler-backed tools yet.
