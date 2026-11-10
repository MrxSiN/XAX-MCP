# Native reliability audit — 2026-11-10

Recorded before implementation. This is a working-tree audit, not evidence that
the published 0.10 commit is checked out. Historical records are unchanged.

## Checkout and identity

- XAX-MCP branch `main`, HEAD `27ffb9491bfe69000b3ce9744b2b689a4d594a3e`;
  55 dirty/untracked status entries at entry. Working files describe 0.10 and
  cite `1e584cdfb00fe3230855b82b92eda3c63a50e807`; that is not this HEAD.
- XAX HEAD `8c9ce91351b664b927df066d4c2ef549167ae0ef`; 1236 status entries.
  No upstream modification or pin upgrade is part of this increment.
- Dependency manifest, workflow checkout ref and release embedded pin agree on
  `af376e8a8a1ac5635bcad459cb7063ef0b326430`. The local Windows seed actually
  hashes to `aa72234d6dd8a111efde62b47ced8449a482c4c5506d876714ff7fbe0968ab79`.
  Current upstream HEAD is not substituted for the pinned contract.
- Canonical server root: `16a25c0805b900e3bb45082b0ac88e1217cbf184c1bf739d29d1df1bc298eb83`;
  launcher: `d378055b3c4c490c667db8d7f61b2d871f4bb3b8701ae54e5dc5308037904dff`.
  Sources: `native/xax-mcp-native-gen2.xax`, `native/xax-mcp-sandbox-gen1.xax`.

## Gap matrix at entry

EXECUTED below means recorded prior evidence, pending local reproduction in this
session. A tool name does not establish the missing operations.

| Surface / operation | Label | Existing implementation and remaining boundary |
|---|---|---|
| xax_capabilities | EXECUTED | Native identity/rights/host bounds; no general typed ABI |
| xax_workspace | PARTIAL | One host workspace, exclusive scratch lease; no scoped handles |
| xax_query | PARTIAL | Native inspect: root, byte size, first CID; no general graph/dependency query or paging |
| xax_construct | PARTIAL | Nonzero exact-root XAXEDIT1; typed JSON structural authoring absent |
| xax_transaction | PARTIAL | Native edit → verify → publish; no retained candidate/test-before-commit lifecycle |
| xax_build | EXECUTED | Native resolve/build with provenance; compiler cancellation incomplete |
| xax_execute | PARTIAL | Host-granted current artifact, binary input/argv, AppContainer/job; no typed result layouts |
| xax_result | UNIMPLEMENTED | Explicit unsupported result; no bounded scoped paging |
| Semantic validation | EXECUTED | Pinned native verify after edit; not a behavioral correctness proof |
| Application authorship/build | EXECUTED | 64 recorded source transactions, canonical sources and deterministic application rebuilds |
| Transport | PARTIAL | Legacy 2025-11-25; modern 2026-07-28 unimplemented |
| Authority/isolation/cleanup | PARTIAL | Host grants, native launcher, bounded streams/CPU/wall; hostile same-user races, crash windows and independent escape review open |
| Cross-client state | PARTIAL | Scratch lease/crash release; no general multi-client transactions |
| Packaging | PARTIAL | Workflow excludes native/transactions yet installation guide promises replay; no extracted-package gate in CI |
| Host adoption | UNVERIFIED | Prior Codex registration only; no current model-driven Codex/Claude use |
| Windows compiler self-build | UNIMPLEMENTED | Trusted historical seed; own-source build declines per seed contract |
| Other platforms / HTTP | UNSUPPORTED ON HOST | Windows x86-64 STDIO is the tested contract |
| AI reliability comparison | UNIMPLEMENTED | P1–P4 prerequisites and comparable trials absent |

## Call chains and selected slice

`schemas/tools-v2.json`, `tests/protocol/native-sessions.json`, native transaction
manifests and `.github/workflows/ci.yml` define the current executable contract.
Public construct/transaction invoke pinned `edit`, then `verify`; build invokes
`resolve` then `build`; execution rebuilds current state and invokes the adjacent
native sandbox. No foreign-language server or compiler implementation is added.

The reproducible packaging defect is in the workflow's `Copy-Item native/* ...
-Exclude transactions`. `docs/INSTALL_WINDOWS.md` promises source replay, but a
fresh ZIP cannot replay its missing carriers. The initial external-script
packaging implementation was withdrawn after the user clarified that only XAX
code may be written in this repository. Its scripts and generated artifacts were
moved outside the repository; its workflow/doc changes were restored. That defect
remains open. No packaging fix or new hosted gate is claimed.

Selected final P0 slice: natively authored canonical XAX memory-commit probes,
pinned Windows verification/rebuild, and actual confined allocation-denial tests
with unconfined positive controls. Server and launcher roots remain unchanged.
The probes use the current native Linux compiler only as an explicitly identified
authoring tool; the old pinned Windows seed verifies and builds them. There is no
runtime or release dependency upgrade. No non-XAX implementation is added.

The full mission, sandbox review, semantic query/authoring and protocol work remain
open. Native allocations are a bounded denial observation, not exhaustive memory
pressure/escape testing. The new probes have local evidence, not a new hosted CI
run or an MCP-only typed-authorship acceptance demonstration.

## External references checked

Official specifications were read at both versioned URLs on 2026-11-10:
[legacy](https://modelcontextprotocol.io/specification/2025-11-25) and
[modern](https://modelcontextprotocol.io/specification/2026-07-28). They describe
different stateful and stateless request eras; this slice does not implement modern MCP.

`CUM prepare` is not `xax_native.prepare(parallel=True)` compiler warmup. The
downstream CUM README identifies Certified Useless Module; the MCP execution
increment explicitly excludes its transformations, BBC registry and full prepare.
No full-prepare claim or implementation is made here; the complete downstream
prepare contract still needs a separate ownership audit before implementation.
