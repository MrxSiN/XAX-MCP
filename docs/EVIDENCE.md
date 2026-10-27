# Evidence and claim labels

## 2026-10-27 current audit

[Native transaction construction evidence](evidence/native-windows-x86_64-transaction-construction-20261027.json)
records a new canonical arithmetic graph built and executed through the unchanged XAX MCP server, returning
136 under native confinement, plus stale-root, launch-right and separate-work-directory checks. It also
preserves failing schema checks and successful publication of an invalid candidate before independent native
verification rejected it. These negative results block release; the invalid candidate was never executed.

The native carrier decoder is unavailable on this host. The recovered compiler is identified separately from
the embedded pin and has not been certified as that pin. Current CI is a native smoke workflow; the SDK and
external Python-suite counts below are historical. Canonical `.xax` application state is source owned here.
See [Windows readiness](WINDOWS_READINESS.md) for exact scope and unresolved work.

Labels: **PROVEN** (formal or exhaustive argument), **EXECUTED** (ran end to end and checked against an
independent oracle), **MEASURED** (raw samples recorded), **STRUCTURAL** (present and wired, but not exercised end
to end), **PROTOTYPE** (works for a narrow case), **UNIMPLEMENTED**.

Evidence files are append-only. A new pin, build or capability writes a new file; older files are never edited.
Raw samples for the current build are in `docs/evidence/native-windows-x86_64-build-3e9b0c2.json` (this pin: new
identities, the native decoder's byte-identity check, test counts),
`docs/evidence/native-windows-x86_64-chain-3e9b0c2.json` (the chain re-run with a native compiler rebuilt at the pin),
`docs/evidence/native-windows-x86_64-native-build-parity-3e9b0c2.json` (the native compiler running the PE stage on
both committed stores, and the measured byte-parity result),
`docs/evidence/native-windows-x86_64-author-retirement-7ed308f.json` (the five carrier authors retired; the stores are
the programs; the suite and bench run against the committed executables),
`docs/evidence/native-windows-ci-author-retirement-39945240009.json` (the clean windows-2022 run: 44 passed, 3 skipped,
executable hashes and server identity),
`docs/evidence/native-windows-x86_64-build-f79b532-r3.json`,
`docs/evidence/native-windows-x86_64-chain-f79b532.json` and
`docs/evidence/native-windows-x86_64-sandbox-f79b532.json` and
`docs/evidence/native-windows-ci-sandbox-0137179.json` (the clean Windows CI host). The earlier
`native-windows-x86_64-build-f79b532.json`, `native-windows-x86_64-build-f79b532-r2.json`,
`native-windows-x86_64-protocol-f79b532.json`, the 6885f89 native files, and every Python-era file remain unchanged.

## Current native server (0.8.0)

| Claim | Label | Evidence |
|---|---|---|
| The server is an XAX-built PE32+ and the committed canonical store is reproducible | EXECUTED | pin `3e9b0c2`; store root `18ceecd9...4b07`; store SHA-256 `0a698799...dcab`; artifact 359 424 B, SHA-256 `9f6e272b...076a`; 181 functions; `native-windows-x86_64-build-3e9b0c2.json` |
| The native compiler runs the PE stage on the committed snapshot stores | EXECUTED | `xaxc build native/xax-mcp-sandbox-gen0.xax` → 25 600 B / `6d563e0f...`, byte-identical to the committed executor PE; `xaxc build native/xax-mcp-native-gen0.xax` → 359 424 B / `a87fdd10...`, which reports the 0.8.0 identity and passes the external suite; `native-windows-x86_64-native-build-parity-3e9b0c2.json` |
| Native `build` byte parity with the reference author build | MEASURED | executor: identical; server: same 359 424 B size, identical `.idata`, 231 313 of 359 424 bytes differ while 99.5% of the tail matches under a 16-byte shift; the native image omits the reference image's single Windows guard-page probe (`sub rsp, 0x1000; test [rsp], 0; sub rsp, 0xd38` vs one `sub rsp, 0x1d38`), so it is not claimed safe for frames over 4 KiB; entry point `0x52970` author vs `0x52960` native; `xax_build.build` reproduces the committed `9f6e272b...` exactly; the only failing test on the native-built server is the byte-identity assertion; `native-windows-x86_64-native-build-parity-3e9b0c2.json` |
| Both committed stores are reproducible from the committed carriers by a **native** XAX decoder, with no Python | EXECUTED | `construct.exe native/construction_request.json` → 1 103 602 B / `0a698799...` and `construct.exe native/sandbox_request.json` → 74 434 B / `588f57c0...`, both byte-identical to the committed stores, 0.38 s and 0.04 s; `native-windows-x86_64-build-3e9b0c2.json` |
| The server reports its own identity and pin, and starts no Python | EXECUTED | over STDIO the 0.8.0 PE answered `server.version = 0.8.0+native`, `xax.pinned_commit = 3e9b0c2b...1995b`, `host_contract = xax-host-contract-v1 r10`, `python_on_request_path = false`; artifact imports kernel32 and msvcrt only |
| An MCP client initializes the native STDIO server, negotiates the handshake versions, discovers the eight tool schemas, and calls tools | EXECUTED | `compiler/integration/mcp/tests/test_native_stdio.py` at `6b6c359`; 44 passed, 1 skipped on Windows 11 x86-64 without the compiler gate, and 45 passed, 0 skipped with a native `xaxc` rebuilt at the pin (`native-windows-x86_64-chain-3e9b0c2.json`) |
| The full prototype chain runs against a **native** compiler rebuilt from the pinned tree | EXECUTED | query → resolve+build (1536-byte artifact, 268-byte provenance) → one `XAXEDIT1` edit 40→41 (root `8c01664c...`) → rebuild → `xax_execute` exit 41 with empty output; the chain test passed in 26.63 s, the suite 45 passed / 0 skipped in 58.47 s; `native-windows-x86_64-chain-3e9b0c2.json` |
| The official MCP Python SDK client interoperates (STDIO) | EXECUTED | `test_standard_sdk_client` ran and passed at 0.8.0 (`mcp.Client`, mcp 2.3.0) |
| Toolchain pin and fingerprint | EXECUTED | compiler revision `3e9b0c2` (byte-identical `compiler/src` in the tooling commit `6b6c359`), fingerprint `ba009daa...b740` over 125 files; `fingerprint.py` recomputed it from the checkout |
| The carrier authors are retired; the verified stores are the programs | EXECUTED | tooling commit `7ed308f`; `programs/{xax-mcp-native,xax-mcp-sandbox,xax-mcp-seed,xax-mcp-seed-snapshot}.xax` and the two carriers are byte-identical to `native/*`; the five Python emitters are gone; `native-windows-x86_64-author-retirement-7ed308f.json` |
| The external suite drives the committed executables with no author on any path | EXECUTED | 46 passed, 1 skipped with the native compiler/decoder gates and 43 passed, 4 skipped without them; the executor test runs the committed `xax-mcp-sandbox.exe` and `xax-mcp-seed.exe`; `native-windows-x86_64-author-retirement-7ed308f.json` |
| The three executables are committed canonical artifacts and CI checks them | EXECUTED | `native/xax-mcp-native.exe` `9f6e272b...`, `native/xax-mcp-sandbox.exe` `6d563e0f...`, `native/xax-mcp-seed.exe` `8faaeb7e...`; CI run 39945240009 on windows-2022 verified all three and ran 44 passed, 3 skipped with no author; `native-windows-ci-author-retirement-39945240009.json` |

The capability claims below were recorded at 0.7.0. They are unchanged and still current for 0.8.0: the protocol
code, the tool bodies, the grants and the executor store are byte-identical, and only the embedded pin and version
string moved.

## Native capability evidence (0.7.0, still current for these rows)

| Claim | Label | Evidence |
|---|---|---|
| An MCP client initializes the native STDIO server, negotiates four handshake versions, discovers the eight tool schemas, and calls tools | EXECUTED | `compiler/integration/mcp/tests/test_native_stdio.py` in XAX; 43 passed, 2 skipped on Windows 11 x86-64 (no `mcp` 2.x SDK client, no native Windows `xaxc` on the recording host) |
| The server is an XAX-built PE32+ and the committed canonical store is reproducible | EXECUTED | store root `9493014f...1eb9`; store SHA-256 `afa5b600...9013`; artifact SHA-256 `2c72ea0f...cfc1`; `test_build_is_deterministic` |
| No Python, MCP SDK, shell wrapper, or other non-XAX service is on the request path | EXECUTED | the executable imports kernel32 and msvcrt only (no Python DLL); the test client is external; `xax_capabilities.server.python_on_request_path` is false |
| The native JSON validator matches Python's strict RFC 8259/UTF-8 parser | EXECUTED | 1500 randomized cases in `test_json_validation_matches_python_strict_parser` |
| Host rights come only from launch configuration, never from tool arguments | EXECUTED | 7 flag sets and 8 rejected forms in `test_host_rights_come_from_launch_flags` / `test_unknown_flags_fail_closed` |
| The official MCP Python SDK client interoperates (STDIO) | EXECUTED | `test_standard_sdk_client` (`mcp.Client`, mcp 2.3.0) |
| The server describes the current store, resolves and builds it, and applies one XAXEDIT1 transaction through a host-granted native compiler | PROTOTYPE | `test_native_compiler_chain_over_stdio`; seed root `572f683e...1587`, 1536-byte artifact, 268-byte provenance, record 40 -> 41, new root `8c01664c...1e97`; `native-windows-x86_64-chain-f79b532.json` |
| Compiler-backed latency (native, one seed program) | MEASURED | `native-windows-x86_64-chain-f79b532.json`: initialize 18.0 ms, query 0.140 ms, build 44.1 ms, transaction 22.0 ms, peak working set 9.18 MB |
| Protocol latency and memory (native, protocol layer only) | MEASURED | `native-windows-x86_64-protocol-f79b532.json` (0.6.0 artifact; protocol code unchanged): initialize 11.5 ms, ping 17.5 us, tools/list 97.1 us, capabilities 43.0 us, peak working set 8.16 MB |
| The repository holds no source code, and the pinned XAX tooling reproduces every committed carrier and store byte for byte | EXECUTED | `compiler/integration/mcp` in XAX at `0a0b1c4`; six committed files and three executables regenerated identically locally (`native-windows-x86_64-construct-0a0b1c4.json`) and on a clean windows-2022 runner with 43 passed / 2 skipped (`native-windows-ci-tooling-9746e8d.json`); the historical run at the earlier pin is `native-windows-ci-tooling-476b865.json` |
| `xax_capabilities` reports the exact pin, rights, grants, and blockers | EXECUTED | every test calls it; the payload names each tool's status and the compiler and decoder grants |
| `xax_workspace`, `xax_query`, `xax_build`, `xax_transaction` | PROTOTYPE | implement root description, resolve+build, and one XAXEDIT1 edit over a host-granted native compiler; fail closed with `denied_capability` without the grant; docs/NATIVE.md B1/B2 |
| `xax_construct` | PROTOTYPE | copies the inline `xax-construct-v1` carrier to `<work>\construct-request.json` and spawns the host-granted native decoder (`construct <carrier> <store>`); the committed sandbox carrier reproduces the committed 74 434 B store byte for byte and becomes the current store; refusals and missing grants leave the current store untouched; Windows only, 1 MiB arguments limit; `native-windows-x86_64-construct-0a0b1c4.json` |
| `xax_execute` | PROTOTYPE | rebuilds the current store and runs the artifact under Windows OS confinement (`compiler/integration/mcp/sandbox.py` in XAX -> `xax-mcp-sandbox.exe`); `denied_capability` without `--allow-execute`, `sandbox_unavailable` without the executor, `invalid_request` if given arguments; `native-windows-x86_64-sandbox-f79b532.json` |
| An artifact really runs confined (Windows) | MEASURED | `GetTokenInformation(TokenIsAppContainer)` = 1 inside / 0 outside; a host-writable path is refused inside / created outside; `Sleep(60000)` killed at 10 s with `FLAG_TIMEOUT`; a talker artifact's 14 stdout bytes, 5 stderr bytes and exit code 7 all captured; `native-windows-x86_64-sandbox-f79b532.json` |
| The committed stores reproduce and the executor confines on a foreign clean host | EXECUTED | GitHub-hosted windows-2022, run 39291600926 at `0137179`: both stores matched byte for byte, the seed artifact exited 40 with flags 0; `native-windows-ci-sandbox-0137179.json` |
| `xax_result` | UNIMPLEMENTED | needs session state; structured `unsupported` |
| A novel computation is constructed, built, and executed through MCP | UNIMPLEMENTED | the pieces exist separately (construct: committed sandbox carrier; build/execute: seed edit), but no recorded session constructs a novel program, builds it and executes it; the typed I/O contract is missing |
| Sandbox isolation and resource limits (Linux) | UNIMPLEMENTED | Windows AppContainer + job object only; no namespaces, seccomp or rlimits; docs/NATIVE.md B3 |
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
narrow prototype, only its Windows execution path runs anything, and that path has not been reviewed as a security
boundary.
