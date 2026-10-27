# Instructions for agents working on this repository

## Git
- Commit and push directly to `main`.
- Do not add Claude (or any AI tool) as a contributor: no `Co-Authored-By:` trailers, no session links, and no
  "Generated with" lines in commit messages, PR descriptions, or code.

## Project rules
- The deployed server and every runtime component are XAX. Canonical `.xax` semantic stores ARE application source
  and belong here. MCP schemas, carriers, regression data, packaging and guides also belong here. Do not add an
  implementation in another programming language or move MCP application implementation into XAX.
- Change canonical programs through native XAX construction/workspace transactions with exact roots and mandatory
  verification. Do not invent textual XAX syntax, regenerate unchanged graphs, or restore retired Python emitters.
- The exact native compiler seed must be available before claiming a native rebuild. See `docs/WINDOWS_READINESS.md` for remaining gates.
- No workload logic in the server or build tooling: no per-operation tools, no adapter-side computation, and no
  hard-coded results. Results must come from XAX-generated code.
- XAX changes belong in `MrxSiN/XAX`; the dependency direction is one-way (`XAX-MCP -> XAX`).
- When the XAX pin changes, update the CI checkout ref, `README.md`, `docs/NATIVE.md`, `docs/COMPATIBILITY.md`,
  `docs/HANDOFF.md`, `docs/EVIDENCE.md` and this file together. Check that the new pin's `compiler/src` is
  compatible with the canonical program's recorded compiler identity. Change embedded identity through a verified
  XAX transaction and record the exact toolchain/artifact identities. Do not edit retired upstream Python authors.
- Record new evidence in new files under `docs/evidence/`; never overwrite old evidence.
- Do not claim a capability that is not executable natively. Use the labels in `docs/EVIDENCE.md`.

`agent-guidance/` holds optional guidance for agents that *use* the server; this file is for agents that develop it.

Current native pin: `af376e8a8a1ac5635bcad459cb7063ef0b326430` (`xax-native-file-v1`); source is `native/xax-mcp-native-gen1.xax`. JSON xax-construct-v1 remains unsupported. Full mission readiness is false.
