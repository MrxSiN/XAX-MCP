# Instructions for agents working on this repository

## Git
- Commit and push directly to `main`.
- Do not add Claude (or any AI tool) as a contributor: no `Co-Authored-By:` trailers, no session links, and no
  "Generated with" lines in commit messages, PR descriptions, or code.

## Project rules
- The deployed server and every runtime component are XAX. This repository contains **no Python and no source code
  at all**: carriers, canonical stores, executables, evidence and documents. Rebuilding the committed artifacts needs
  only native XAX programs (a host-granted carrier decoder and compiler); the offline carrier authors and the external
  MCP test client live in `MrxSiN/XAX` (`compiler/integration/mcp`) and are disclosed as B5 in `docs/NATIVE.md`.
- No workload logic in the server or build tooling: no per-operation tools, no adapter-side computation, and no
  hard-coded results. Results must come from XAX-generated code.
- XAX changes belong in `MrxSiN/XAX`; the dependency direction is one-way (`XAX-MCP -> XAX`).
- When the XAX pin changes, update the CI checkout ref, `README.md`, `docs/NATIVE.md`, `docs/COMPATIBILITY.md`,
  `docs/HANDOFF.md`, `docs/EVIDENCE.md` and this file together. Check that the new pin's `compiler/src` is
  byte-identical to the recorded `NATIVE_XAX_COMMIT`; if it is not, update it in
  `compiler/integration/mcp/{server,sandbox}.py` upstream, regenerate both stores, and record the new toolchain
  fingerprint too.
- Record new evidence in new files under `docs/evidence/`; never overwrite old evidence.
- Do not claim a capability that is not executable natively. Use the labels in `docs/EVIDENCE.md`.

`agent-guidance/` holds optional guidance for agents that *use* the server; this file is for agents that develop it.
