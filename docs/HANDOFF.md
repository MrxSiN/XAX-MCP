# Handoff

## State at 0.6.0 (2026-10-19): native-only server

- XAX pin: `f79b532fd4651ba808676d02f4b038e2cc271e6a` (XAX `main`, 2026-10-19), host contract
  `xax-host-contract-v1` r10, toolchain fingerprint
  `0ab800baf79464895bceeb0ccdaa13f4b8d1969fc627644f01e447575731f5d9`.
- The deployed server is `native/xax-mcp-native.exe`: a canonical XAX store (`native/xax-mcp-native-gen0.xax`)
  built from `native/construction_request.json`. It implements STDIO framing, strict JSON validation, JSON-RPC 2.0,
  MCP initialize/ping/tools/list/tools/call, tool dispatch, and host rights. It uses kernel32 only and starts no
  Python.
- `native/server.py`, `native/dsl.py`, and `native/schemas.py` are build tooling. They are not on the request path.
- The seven compiler-backed tools are **UNIMPLEMENTED natively** and return structured `unsupported` errors (or
  `denied_capability` before the grant). `xax_execute` also fails closed because no native sandbox exists.
- Tests: `tests/test_native_stdio.py`, 42 passed in 29.9 s on Windows 11, Python 3.12.10 (test client only), mcp
  2.3.0. The suite rebuilds the committed store, checks it byte for byte, builds the PE, and drives it over STDIO.
- Evidence: new files `docs/evidence/native-windows-x86_64-protocol-f79b532.json` (measurements) and
  `docs/evidence/native-windows-x86_64-build-f79b532.json` (build identity). The 6885f89 evidence file is unchanged.
- The retired 0.5.1 Python adapter (`src/xax_mcp`) is removed. Its docs are marked historical; git history retains
  the implementation for the porting work.

### Exact blockers

- **B1/B2**: XAX publishes no native compiler for the pinned Windows tree. The committed `xaxc-linux-x86_64` is a
  Linux ELF and this host has no Linux. A local, uncommitted `xaxc-windows.exe` prototype exists under
  `D:\GitHub\XAX\build\windows_helpers` and supports verify/inspect/build/resolve/lower/edit, but not `construct`,
  and has no committed build script. It is not a dependency of this release.
- **B3**: no Linux build/run of the native server was tested here.
- **B4**: no native Windows sandbox (LPAC AppContainer + job object) yet; execution fails closed.

### Next steps, in order of leverage

1. Upstream: commit a reproducible native Windows compiler build for `f79b532`, then a versioned `xaxc serve`
   interface (construct/open/verify/query/edit/build, length-prefixed typed requests, structured diagnostics).
2. Here: proxy `xax_workspace`/`xax_query`/`xax_transaction`/`xax_build` to that service. Do not reimplement graph
   construction or the compiler in the server.
3. Port the Windows LPAC/job-object sandbox to XAX for `xax_execute`; port the Linux sandbox after a Linux build.
4. Add session handles and bounded `xax_result`, backed by OS randomness.
5. Record a model-driven Codex/Claude session only after a novel construct → build → execute loop actually works.

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
