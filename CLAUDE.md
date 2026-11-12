# Instructions for agents working on this repository

## Git
- Commit and push directly to `main`.
- Do not add Claude (or any AI tool) as a contributor: no `Co-Authored-By:` trailers, no session links, and no
  "Generated with" lines in commit messages, PR descriptions, or code. The only exception is a commit that does
  nothing but record a benchmark the AI ran; that commit may carry one `Co-Authored-By:` trailer.
- Do not push branches named after an AI tool (for example `claude/...`).
- Write commit subjects and PR titles in plain English that says what changed for a reader, for example
  "Let the native executor accept binary stdin and arguments". Skip internal codes (W3, S15, ADR numbers),
  hashes and jargon in the title; put them in the body if they matter.
- PR descriptions: start with one or two sentences on what changed and why. Then list how it was checked and
  anything still missing. Use short paragraphs or bullets, not a wall of identifiers.

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
- The XAX pin lives in `native/xax-dependency.json` and the CI checkout ref (`native/release-status.json` records
  the embedded pin). When it changes, update those together; docs link to the JSON instead of repeating the hash. Check that the new pin's `compiler/src` is
  compatible with the canonical program's recorded compiler identity. Change embedded identity through a verified
  XAX transaction and record the exact toolchain/artifact identities. Do not edit retired upstream Python authors.
- Record new evidence in new files under `docs/evidence/`; never overwrite old evidence.
- Do not claim a capability that is not executable natively. Use the labels in `docs/EVIDENCE.md`.
- Design choices follow the section "Engineering principles for compiler and semantic-graph changes" in XAX's `AGENT.md`
  (SOLID, DRY, KISS, YAGNI, Law of Demeter, Boy Scout Rule, Separation of Concerns as context-sensitive rules). They
  never override the rules above, verified state integrity or evidence quality, and they never justify code in another
  language here.

`agent-guidance/` holds optional guidance for agents that *use* the server; this file is for agents that develop it.

Implementation was paused on 2026-11-10. Read [the continuation prompt](CONTINUE_NATIVE_EVOLUTION.md)
before resuming file races, compiler cancellation, semantic APIs or modern MCP.
Experimental canonical checkpoints are archived under `native/candidates/20261110/`;
they are not the default deployment. The last capabilities candidate has a known JSON framing failure.

Work resumed on 2026-11-11. Read `docs/NATIVE_CANDIDATE_20261111.md` and
`native/candidates/20261111/checkpoints.json` for the repaired experimental successor
and its complete pinned replay. It is not deployed: controlled workspace `edit.rec`
hard-link aliases still overwrite files outside work. Request cancellation and
typed/paginated semantic APIs remain absent. The 20261110 failure record is historical.

The later control preview is recorded in `docs/NATIVE_CONTROL_20261111.md` and
`native/candidates/20261111-control/checkpoints.json`. It adds tested native
compiler cancellation, descendant cleanup and bounded public reference-query
pages, plus legacy progress-metadata compatibility. Its selected query schema is
`schemas/tools-v3.json`. It is an explicit preview; Gen3 remains the default and
the compiler dependency is unchanged. Preserve the trusted-host workspace-alias
boundary, inspection-prefix limit, separate desktop UI evidence and false release
readiness flags. Do not relabel older evidence as acceptance of this source.
Final-source acceptance completed on 2026-11-12; see
`docs/evidence/native-control-20261112.json` for separate runtime, fresh-package,
installed backend and active desktop read-only evidence. The prior paused handoff
is superseded by `REMAINING_MCP_TASKS.md`; default Gen3 and release flags stay unchanged.

Current native pin: see `native/xax-dependency.json` (`xax-native-file-v1`); sources are `native/xax-mcp-native-gen3.xax` and `native/xax-mcp-sandbox-gen1.xax`. The 20261110-host-paths manifest extends native replay through the configured-path guard. Binary stdin/argv are implemented within host bounds; JSON xax-construct-v1 and full CUM prepare remain unsupported. Full mission readiness is false.

The 20261112 JVM preview is separate: read `docs/NATIVE_JVM_20261112.md`,
`native/jvm-dependency.json` and `native/candidates/20261112-jvm/checkpoints.json`.
Its newer immutable native compiler is tested only for that snapshot build/execute
preview; do not silently replace the default pin or the user's existing MCP setup.
Native snapshot mutation declines, Windows-1252 argument limits are enforced,
and content integrity, atomic publication, crash ACL/cache cleanup and broader
security remain open. Java is the required host platform runtime; no handwritten
Java helper is part of the server. New evidence is `docs/evidence/native-jvm-20261112.json`.

Current gen3 evidence: `docs/evidence/native-host-path-guard-20261110.json` and the separate clean-package record. The current hosted result below remains the historical gen2 baseline.

Historical evidence: local acceptance and clean-package records plus hosted run
41314738774 at implementation commit `1e584cdfb00fe3230855b82b92eda3c63a50e807`.
See `docs/EVIDENCE.md` and ADR-0011. Passing CI and uploaded preview artifacts do
not change `release_ready` or full CUM prepare to true.
