# Handoff

## State at 0.7.0 (2026-10-19): native-only server, compiler-backed prototype

- XAX pin: `f79b532fd4651ba808676d02f4b038e2cc271e6a` (XAX `main`, 2026-10-19), host contract
  `xax-host-contract-v1` r10, toolchain fingerprint
  `0ab800baf79464895bceeb0ccdaa13f4b8d1969fc627644f01e447575731f5d9`.
- The deployed server is `native/xax-mcp-native.exe`: a canonical XAX store (`native/xax-mcp-native-gen0.xax`)
  built from `native/construction_request.json`. It implements STDIO framing, strict JSON validation, JSON-RPC 2.0,
  MCP initialize/ping/tools/list/tools/call, tool dispatch, and host rights. It imports kernel32 and msvcrt and
  starts no Python.
- `native/server.py`, `native/dsl.py`, and `native/schemas.py` are build tooling. They are not on the request path.
- `native/xax-mcp-seed.xax` is a committed form-2 build-request seed; `native/chain.py` authors `XAXEDIT1` carriers
  and drives the native compiler for tests.
- Four tools are a **PROTOTYPE** over a host-granted native compiler: `xax_workspace` and `xax_query` describe the
  current store's root and byte size, `xax_build` runs `resolve` + `build`, and `xax_transaction` applies one
  `XAXEDIT1` record with `edit`. Without `XAX_MCP_COMPILER`/`XAX_MCP_WORK`/`XAX_MCP_STORE` they fail closed with
  `denied_capability`.
- `xax_construct`, `xax_execute` and `xax_result` are **UNIMPLEMENTED natively** and return structured `unsupported`
  errors. `xax_execute` also fails closed because no native sandbox exists.
- Tests: `tests/test_native_stdio.py`, 43 passed and 1 skipped (the Linux build) in 56 s on Windows 11, Python
  3.12.10 (test client only), mcp 2.3.0, with `XAX_MCP_TEST_COMPILER` set. Without the compiler grant, 42 passed and
  2 skipped. The suite rebuilds the committed store, checks it byte for byte, builds the PE, drives it over STDIO,
  and (when granted) runs the seed -> build -> transaction chain.
- Evidence: new files `docs/evidence/native-windows-x86_64-build-f79b532-r2.json` (build identity) and
  `docs/evidence/native-windows-x86_64-chain-f79b532.json` (chain results and measurements). The earlier `f79b532`
  and 6885f89 evidence files are unchanged.
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
- **B4**: no native Windows sandbox (LPAC AppContainer + job object) yet; execution fails closed.

### Next steps, in order of leverage

1. Upstream: commit a reproducible native Windows compiler build for `f79b532`, then a versioned `xaxc serve`
   interface (construct/open/verify/query/edit/build, length-prefixed typed requests, structured diagnostics).
2. Here: grow the prototype behind the same tool names - bounded queries, expected-generation/root transactions,
   artifact handles and `xax_result` - without reimplementing graph construction or the compiler in the server.
3. Port the Windows LPAC/job-object sandbox to XAX for `xax_execute`; port the Linux sandbox after a Linux build.
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

- The deployed server and every runtime component are XAX. No Python server, sidecar, wrapper, or fallback,
  including during development.
- Build tooling may be Python only outside the deployed runtime path; disclose it.
- No workload logic in the server or build tooling: no per-operation tools, no adapter-side computation.
- Keep XAX changes in `MrxSiN/XAX`; dependency direction is one-way (`XAX-MCP -> XAX`).
- When the pin changes, update `native/server.py` (`NATIVE_XAX_COMMIT`), `pyproject.toml`, the CI checkout ref,
  `README.md`, `docs/NATIVE.md`, `docs/COMPATIBILITY.md`, and this file together. Add new evidence; never overwrite
  old evidence files.
