# Instructions for agents working on this repository

## Git
- Commit and push directly to `main`.
- Do not add Claude (or any AI tool) as a contributor: no `Co-Authored-By:` trailers, no session links, and no
  "Generated with" lines in commit messages, PR descriptions, or code.

## Project rules
- No workload logic in the adapter: no per-operation tools and no Python fallbacks. Results come from
  XAX-generated code.
- XAX changes belong in `MrxSiN/XAX`; the dependency direction is one-way (`XAX-MCP -> XAX`).
- When the XAX pin changes, update `compat.TESTED_XAX`, `PINNED_XAX_COMMIT`, `pyproject.toml`, the CI checkout ref,
  and `docs/COMPATIBILITY.md` together.
- Record new evidence in new files under `docs/evidence/`; never overwrite old evidence.

`agent-guidance/` holds optional guidance for agents that *use* the server; this file is for agents that develop it.
