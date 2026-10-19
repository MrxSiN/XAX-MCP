# Instructions for agents working on this repository

## Git
- Commit and push directly to `main`.
- Do not add Claude (or any AI tool) as a contributor: no `Co-Authored-By:` trailers, no session links, and no
  "Generated with" lines in commit messages, PR descriptions, or code.

## Project rules
- The deployed server and every runtime component are XAX. No Python server, sidecar, wrapper, or fallback,
  including during development. Python is allowed only as build tooling and as external test clients.
- No workload logic in the server or build tooling: no per-operation tools, no adapter-side computation, and no
  hard-coded results. Results must come from XAX-generated code.
- XAX changes belong in `MrxSiN/XAX`; the dependency direction is one-way (`XAX-MCP -> XAX`).
- When the XAX pin changes, update `native/server.py` (`NATIVE_XAX_COMMIT`), `pyproject.toml`, the CI checkout ref,
  `README.md`, `docs/NATIVE.md`, and `docs/COMPATIBILITY.md` together.
- Record new evidence in new files under `docs/evidence/`; never overwrite old evidence.
- Do not claim a capability that is not executable natively. Use the labels in `docs/EVIDENCE.md`.

`agent-guidance/` holds optional guidance for agents that *use* the server; this file is for agents that develop it.
