# Handoff

## State at 0.7.0 (2026-10-19): native-only server, compiler-backed prototype

- XAX pin: `4c3e60bef96c56162003838b36d6756295b1de41`, the first commit that carries the authoring tooling
  (`compiler/integration/mcp`). Its `compiler/src` is byte-identical to `f79b532fd4651ba808676d02f4b038e2cc271e6a`
  (XAX `main`, 2026-10-19), host contract `xax-host-contract-v1` r10, toolchain fingerprint
  `0ab800baf79464895bceeb0ccdaa13f4b8d1969fc627644f01e447575731f5d9`.
- The deployed server is `native/xax-mcp-native.exe`: a canonical XAX store (`native/xax-mcp-native-gen0.xax`)
  built from `native/construction_request.json`. It implements STDIO framing, strict JSON validation, JSON-RPC 2.0,
  MCP initialize/ping/tools/list/tools/call, tool dispatch, and host rights. It imports kernel32 and msvcrt and
  starts no Python.
- This repository holds no source code: carriers, canonical stores, executables, evidence and docs only. The build
  tooling (`server.py`, `sandbox.py`, `dsl.py`, `schemas.py`, `seed.py`, `chain.py`, `bench.py`,
  `fingerprint.py`) is in XAX under `compiler/integration/mcp`. It is not on the request path.
- `native/xax-mcp-seed.xax` is a committed form-2 build-request seed; `compiler/integration/mcp/chain.py` in XAX
  authors `XAXEDIT1` carriers and drives the native compiler for tests.
- Five tools are a **PROTOTYPE** over a host-granted native compiler: `xax_workspace` and `xax_query` describe the
  current store's root and byte size, `xax_build` runs `resolve` + `build`, `xax_transaction` applies one
  `XAXEDIT1` record with `edit`, and `xax_execute` runs the built artifact under Windows OS confinement. Without
  `XAX_MCP_COMPILER`/`XAX_MCP_WORK`/`XAX_MCP_STORE` they fail closed with `denied_capability`; `xax_execute` also
  needs `--allow-execute` and `xax-mcp-sandbox.exe` beside the server.
- `compiler/integration/mcp/sandbox.py` in XAX builds `xax-mcp-sandbox.exe`, a **separate** native XAX program: a capability-less AppContainer
  inside a job object (5 s CPU, 256 MiB, one process, 10 s wall, 1 MiB per stream). The server spawns it with a fixed
  three-word argv and reads back stdout, stderr and a 16-byte result record.
- `xax_construct` and `xax_result` are **UNIMPLEMENTED natively** and return structured `unsupported` errors.
  Upstream, `compiler/integration/construct` (branch `feat/native-construct`) decodes both committed carriers
  through step 5a: kinds 3, 5 and 7 are byte-identical. Packages, build requests, the store and the command are
  still missing.
- Tests: `compiler/integration/mcp/tests/test_native_stdio.py` in XAX, 44 passed and 1 skipped (the Linux build)
  in 68 s on Windows 11, Python
  3.12.10 (test client only), mcp 2.3.0, with `XAX_MCP_TEST_COMPILER` set. The suite rebuilds both committed stores,
  checks them byte for byte, builds both PEs, drives the server over STDIO, and (when granted) runs the seed -> build
  -> transaction -> confined execute chain.
- Evidence: new files `docs/evidence/native-windows-x86_64-build-f79b532-r3.json` (build identity),
  `docs/evidence/native-windows-x86_64-sandbox-f79b532.json` (confinement results and measurements),
  `docs/evidence/native-windows-x86_64-construct-dabf730.json` (native construct step 5a: both carriers'
  listings byte-identical) and `docs/evidence/native-windows-ci-sandbox-0137179.json` (the same confinement
  reproduced on a clean GitHub windows-2022 runner), alongside the earlier
  `native-windows-x86_64-chain-f79b532.json`. The earlier `f79b532` and 6885f89 evidence files are unchanged.
- The retired 0.5.1 Python adapter (`src/xax_mcp`) is removed. Its docs are marked historical; git history retains
  the implementation for the porting work.

### Exact blockers

- **B1**: no reproducible native compiler is committed for the pinned Windows tree. The committed
  `xaxc-linux-x86_64` is a Linux ELF and this host has no Linux. The prototype therefore consumes a host-granted
  `xaxc-windows.exe` at `D:\GitHub\XAX\build\windows_helpers` (verify/inspect/build/resolve/lower/edit, no
  `construct`, no committed build script). It is not committed, not shipped, and not a dependency.
- **B2**: the native compiler's command set is files and exit status, not a versioned service. There is no native
  carrier decoder (`construct`), no bounded query, and no generation/root-checked transaction interface.
- **B3**: no Linux build/run of the native server was tested here.
- **B4**: the Windows sandbox is a prototype (LPAC AppContainer + job object in `compiler/integration/mcp/sandbox.py` in XAX), measured but not
  reviewed as a security boundary; Linux confinement and the typed I/O contract are missing.

### Next steps, in order of leverage

1. Upstream: commit a reproducible native Windows compiler build for `f79b532`, then a versioned `xaxc serve`
   interface (construct/open/verify/query/edit/build, length-prefixed typed requests, structured diagnostics).
2. Here: grow the prototype behind the same tool names - bounded queries, expected-generation/root transactions,
   artifact handles and `xax_result` - without reimplementing graph construction or the compiler in the server.
3. Sandbox: harden the Windows executor (typed I/O, argv, per-call limits, independent review), and port the Linux
   sandbox after a Linux build.
4. Record a model-driven Codex/Claude session only after a novel construct -> build -> execute loop actually works.

## Historical: 0.5.1 and earlier (Python adapter)

These releases used a Python server (`src/xax_mcp`). They are recorded for provenance, not as descriptions of the
current server.

- 0.5.1 (2026-10-10): XAX `f0aa191`, host contract r3. 49/49 tests on Python 3.11/3.13. Warm-server first result
  0.17 s; in-process populated cache 1.1 s; empty-cache `--prepare` 20.1 s.
- 0.5.0 (2026-10-09): XAX `13a6843`, host contract r3. `xax_native.prepare`; warm server; 49/49 tests.
- 0.4.0 (2026-10-09): XAX `6c2df90`, host contract r2. Per-user warm server; 49 tests.
- 0.3.1 / 0.3.0 / 0.2.0 / 0.1.0: see the compatibility matrix and `docs/evidence/`.
- Unreleased Windows WIP (2026-10-10): XAX `44b5f3c`, host contract r7; Windows construct/build/run in an LPAC
  AppContainer; 39 pass, 12 platform skips. This was the last Python implementation.

## Rules

- The deployed server and every runtime component are XAX, and this repository contains no Python and no source
  code. Build tooling lives in `MrxSiN/XAX` (`compiler/integration/mcp`).
- No workload logic in the server or build tooling: no per-operation tools, no adapter-side computation.
- Keep XAX changes in `MrxSiN/XAX`; dependency direction is one-way (`XAX-MCP -> XAX`).
- When the pin changes, update `NATIVE_XAX_COMMIT` in `compiler/integration/mcp/{server,sandbox}.py` upstream, and
  the CI checkout ref, `README.md`, `docs/NATIVE.md`, `docs/COMPATIBILITY.md`, and this file together. Add new
  evidence; never overwrite old evidence files.
