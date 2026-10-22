# Handoff

## State at 0.7.0 (2026-10-22): native-only server, compiler- and decoder-backed prototype

- XAX pin: `0a0b1c4f1b217ce3a46917e93c1a1b7a66ee9bd8` (`feat/mcp-tooling`: its parent
  `4c3e60bef96c56162003838b36d6756295b1de41` moved the authoring tooling (`compiler/integration/mcp`) into XAX;
  the pin adds the `xax_construct` wiring). Its `compiler/src` is byte-identical to
  `f79b532fd4651ba808676d02f4b038e2cc271e6a` (XAX `main`, 2026-10-19), host contract `xax-host-contract-v1` r10,
  toolchain fingerprint `0ab800baf79464895bceeb0ccdaa13f4b8d1969fc627644f01e447575731f5d9`.
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
- `xax_construct` is a **PROTOTYPE** over a host-granted native carrier decoder: it copies the inline
  `xax-construct-v1` request verbatim to `<work>\construct-request.json`, spawns the decoder
  (`XAX_MCP_CONSTRUCT`) with a fixed three-word argv, and makes the verified store current only after exit 0 and a
  readable store. It executed over STDIO on 2026-10-22: the committed sandbox carrier produced the committed
  74 434 B store byte for byte (root `7ef7099d...`). Without `XAX_MCP_CONSTRUCT`/`XAX_MCP_WORK` it fails closed.
- `xax_result` is **UNIMPLEMENTED natively** and returns a structured `unsupported` error. Upstream, the native
  decoder `compiler/integration/construct` (branch `feat/native-construct`, step 6) also reproduces the new
  server store from `native/construction_request.json` byte for byte (1 103 601 B / `afa5b600...`, root
  `9493014f...`). The general driver does not dispatch the command: the decoder is a separate native program.
- Tests: `compiler/integration/mcp/tests/test_native_stdio.py` in XAX, 43 passed and 2 skipped on this host
  (the `mcp` 2.x SDK client and a native Windows `xaxc` were absent), 28 s on Windows 11, Python 3.12.10 (test
  client only), with `XAX_MCP_TEST_CONSTRUCT` set. The suite rebuilds both committed stores, checks them byte for
  byte, builds both PEs, drives the server over STDIO, and (when granted) runs the carrier -> decoder path and the
  seed -> build -> transaction -> confined execute chain.
- Evidence: new file `docs/evidence/native-windows-x86_64-construct-0a0b1c4.json` (new server identity, native
  decoder oracle match, `xax_construct` results, test counts), alongside
  `docs/evidence/native-windows-x86_64-build-f79b532-r3.json` (build identity),
  `docs/evidence/native-windows-x86_64-sandbox-f79b532.json` (confinement results and measurements),
  `docs/evidence/native-windows-x86_64-construct-dabf730.json` (native construct step 5a: both carriers'
  listings byte-identical), `docs/evidence/native-windows-x86_64-construct-ae85b8d.json` (native construct
  step 5b: target, module, package, profile, policy and build request included),
  `docs/evidence/native-windows-x86_64-construct-f0fc9c9.json` (native construct step 5c root: the snapshot
  CID is the reference store root), `docs/evidence/native-windows-x86_64-construct-1e78168.json` (native
  construct step 5c container: both stores byte-identical to the committed files),
  `docs/evidence/native-windows-x86_64-construct-486fa9d.json` (native construct step 6: the
  `construct <carrier> <store>` command reproduces both stores) and
  `docs/evidence/native-windows-ci-sandbox-0137179.json` (the same confinement
  reproduced on a clean GitHub windows-2022 runner), alongside the earlier
  `native-windows-x86_64-chain-f79b532.json`. The earlier `f79b532` and 6885f89 evidence files are unchanged.
- The retired 0.5.1 Python adapter (`src/xax_mcp`) is removed. Its docs are marked historical; git history retains
  the implementation for the porting work.

### Exact blockers

- **B1**: no reproducible native compiler or carrier decoder is committed for the pinned Windows tree. The committed
  `xaxc-linux-x86_64` is a Linux ELF and this host has no Linux. The prototype therefore consumes a host-granted
  `xaxc-windows.exe` at `D:\GitHub\XAX\build\windows_helpers` (verify/inspect/build/resolve/lower/edit, no
  `construct`, no committed build script) and a host-granted `construct.exe`
  (`D:\GitHub\XAX\build\construct_cmd\construct.exe`, 2 852 352 B, SHA-256 `a6bd67fd...`, built from
  `feat/native-construct` `486fa9d`). Neither is committed, shipped, or a dependency.
- **B2**: the native programs' command set is files and exit status, not a versioned service. The carrier decoder is
  a separate `construct <carrier> <store>` program, not a driver command; there is no bounded query and no
  generation/root-checked transaction interface.
- **B3**: no Linux build/run of the native server was tested here.
- **B4**: the Windows sandbox is a prototype (LPAC AppContainer + job object in `compiler/integration/mcp/sandbox.py` in XAX), measured but not
  reviewed as a security boundary; Linux confinement and the typed I/O contract are missing.

### Next steps, in order of leverage

1. Upstream: commit reproducible native Windows builds of the compiler (for `f79b532`) and the carrier decoder
   (for `486fa9d`), then a versioned `xaxc serve` interface (construct/open/verify/query/edit/build,
   length-prefixed typed requests, structured diagnostics).
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
- When the pin changes, update the CI checkout ref, `README.md`, `docs/NATIVE.md`, `docs/COMPATIBILITY.md`,
  `CLAUDE.md` and this file together. Check that the new pin's `compiler/src` is still `f79b532`; if it is not,
  update `NATIVE_XAX_COMMIT` in `compiler/integration/mcp/{server,sandbox}.py` and the fingerprint upstream too.
  Add new evidence; never overwrite old evidence files.
