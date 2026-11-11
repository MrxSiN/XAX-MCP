# Continuation prompt: native reliability, semantic APIs and modern MCP

## Resume update — 2026-11-11

The prompt below records the 2026-11-10 pause. Continue from
[the resumed candidate](docs/NATIVE_CANDIDATE_20261111.md) and
`native/candidates/20261111/checkpoints.json`. Its capabilities JSON is repaired,
discovery reports all five tested versions and required cache hints, and nine
pinned Windows transactions reproduce it. It remains experimental: controlled
workspace record aliases overwrite disposable files outside work. Cancellation,
typed semantic queries, paging and desktop-client acceptance remain unfinished.
The default gen3 deployment and XAX pin are unchanged.

Resume work in `D:\GitHub\XAX-MCP`. The user paused implementation on 2026-11-10
and requested this prompt, a commit and a push. Do not describe the unfinished
candidate work below as delivered functionality.

## Instructions to preserve

- Only XAX implementation may be written in this repository. Canonical `.xax`
  stores are authoritative application source. Native view/batch and XAXEDIT1
  records are construction carriers. Documentation, schemas and evidence are data.
- Keep foreign-language test orchestration, transport packing and inspection
  utilities outside this repository. No foreign runtime, compiler implementation,
  canonical graph generator or replacement textual source language is permitted.
- Read `CLAUDE.md`, `native/release-status.json`, the manifests and current Git
  state before editing. Preserve identities of unchanged objects, exact roots,
  mandatory verification and existing native tests. Commit and push to `main`
  when the resumed work is ready; do not add attribution trailers.
- Keep deployment pinned to `native/xax-dependency.json`. The tested Windows seed
  SHA-256 is `aa72234d6dd8a111efde62b47ced8449a482c4c5506d876714ff7fbe0968ab79`.
  No Windows compiler self-hosting or production readiness is established.
- Do not disturb unrelated upstream changes in `D:\GitHub\XAX`. Its working tree
  was heavily modified at entry. General compiler features belong upstream through
  separate, verified work; the dependency remains XAX-MCP to XAX.

## Current default and archived candidates

The default server is **gen3**, root
`44f8e6b34a4bd3d50bfb670c1be6a73c9e5bfae7f701383f70eb51e37befd94d`.
It has configured-path validation and the tested existing execution path. Its
Windows replay chain is `native/transactions/20261110-host-paths/manifest.json`.
The default executable, snapshot, workflow and deployment pin select this source.
The memory probes and path guard have separate evidence under `docs/evidence/`.

Experimental checkpoints are retained in `native/candidates/20261110/`; their
identities, exact native authoring carriers and validation labels are in
`native/candidates/20261110/checkpoints.json`. They are **not installed** as the
default server and have no completed pinned Windows XAXEDIT1 replay chain yet.
The source chain is:

1. gen3 -> `server-file-pins.xax`;
2. file pins -> `server-compiler-process.xax`;
3. compiler process control -> `server-modern-mcp.xax`;
4. modern MCP -> `server-semantic-inspect.xax`;
5. semantic inspection -> `server-modern-capabilities.xax` (**known runtime failure**).

`json-test.xax` is a separate native JSON helper test program. Full native batch
carriers are under `native/transactions/20261110-{file-pins,compiler-process,modern-mcp,semantic-inspect}/`.
Rootless `.batch` files there are fragments; use the full `server-*.batch` carrier
against its exact recorded base. Do not concatenate fragments without checking
the native view's entity selectors, labels, ownership and definition order.

Authorship used the native Linux seed through WSL, SHA-256
`a35fd59fc9effe08f58f6d1db0d2e951abbd56a065dc0dca729c9bc6f5ec793b`;
deployment validation/builds used the unchanged pinned Windows seed. This is an
authoring tool identity, not permission to silently upgrade the deployment pin.

## Remaining job, in order

### 1. Repair the last capabilities candidate before any promotion

`server-semantic-inspect.xax` is the last checkpoint that passed the 25-exchange
modern/legacy protocol exercise and the seed object-inventory comparison.
Its embedded capabilities still report modern MCP as unimplemented and list only
legacy versions. This must be corrected before shipping the modern implementation.

The subsequent `server-modern-capabilities.batch` replaces gen3 literal writers
whose original native-view CIDs are
`e134ffbe543ed47474f98e3147ebde628e09ed1e3040350865e21700ffa14e30` and
`ea4351788249ea89a7ac137a3f9fad9f3c2c6d6131da8393a077a73e38b9b104`.
The candidate verifies and builds, but `xax_capabilities` produces malformed
JSON. The last independent decoder failure was at character 5304 of a 9023-byte
response. Exact bytes are retained in
`docs/evidence/native-modern-capabilities-failure-20261110.bin`.
Inspect literal widths, appended stores, offsets, returned lengths and escaping;
do not assume verification/build proves correct framing. One earlier defect was
replacing 21 bytes of the 22-byte `UNIMPLEMENTED natively` string; that was fixed,
but the remaining JSON failure is unresolved. Test full text/structured equality.

Discovery currently advertises only `2026-07-28` and `2025-11-25`; reconcile it
with all actually supported legacy versions. Finish accurate schema, capabilities,
compatibility and release metadata. Do not advertise unimplemented features.

### 2. Finish file replacement protection

The file-pins checkpoint holds non-inheritable handles to compiler/store files
and their ancestors, plus the workspace directory. It rejects reparse objects,
wrong types and configured files with multiple hard links. Identity-cache bounds
and post-lease sealing are native XAX. Seven OS-enforced write/rename denials,
exit-time handle release, path negatives and the 92-exchange baseline passed.

This does **not** close writable workspace child-file substitution/publication
races or DOS drive-alias remapping. The pinned compiler accesses writable outputs
by filename. Develop handle/identity-based publication and input/output contracts,
or record the exact required upstream contract and residual trusted-host boundary.
Do not call another pathname recheck complete TOCTOU protection. Add hard-link
alias, directory replacement, pre-existing output, crash and concurrent attacker
tests, including source/root preservation after rejection.

### 3. Finish compiler cancellation

The compiler-process checkpoint replaces eight synchronous `_spawnv(P_WAIT)`
sites with a 64-bit process-handle wait. A server-owned kill-on-close job contains
the server before compiler creation. Each call has a 30-second deadline, child
termination and a bounded termination wait; failure to confirm termination exits
the server instead of releasing live compiler scratch. Existing 92 exchanges,
a hanging native compiler deadline, responsiveness after timeout and compiler
termination after server death passed.

Incoming `notifications/cancelled` is **not processed while a compiler call is
running**. Implement bounded input polling/queuing or an appropriate native event
loop, match the active JSON-RPC ID, preserve ordinary queued requests and do not
interpret stdin EOF as automatic cancellation. Confirm child/descendant cleanup,
late/unknown cancellation behavior, no publication on cancellation and lease
recovery. Deadline/server-death handling alone is not request-level cancellation.

### 4. Finish useful semantic APIs

The semantic checkpoint appends an `inspection` object to successful native
workspace/query results. It consumes the compiler's **public inspection record**,
not canonical-store internals: kind tags, stable CIDs and reference arrays in CID
order. Complete records within the existing 65,536-byte inspection read are emitted;
`complete:false` distinguishes an incomplete inventory. The seed's 12 objects,
kinds and reference edges match an independent store reader, including matching
MCP text/structured bodies.

Typed selectors, entity lookup/not-found, dependencies/users/neighborhoods,
root-bound continuation/pagination, result budgets and candidate comparisons are
not implemented. The public pinned record lacks function signatures, blocks,
operations and typed/effect facts. Do not fabricate those or implement a second
canonical parser. Track the smallest reusable upstream inspection extension if
required, and independently test it before integrating/repinning.

P1 acceptance still needs an unfamiliar multi-function program located through
documented tools, a real use/call dependency and a paginated bounded neighborhood.
The existing argument schema still accepts `{}` for queries; do not claim typed
semantic query arguments or general semantic evolution acceptance.

### 5. Complete modern MCP verification and integration

The native modern checkpoint implements per-request metadata validation,
`server/discover`, request normalization, modern result envelopes and existing
tool dispatch without a legacy handshake. Reserved keys/method/tool names support
JSON escaping. The JSON helpers passed 160 cases; the modern/semantic exercise
passed 25 exchanges, including escaped names, Unicode IDs, metadata errors,
unsupported versions, clientInfo validation and mixed legacy/modern calls.

Use the current official normative spec, not assumptions from the original mission:
protocolVersion and clientCapabilities are required in params._meta; clientInfo
is optional. Invalid metadata returns -32602; unsupported modern version returns
-32022 with supported/requested data. Successful modern results include
`resultType:"complete"`. Client identity never grants authority.

Add explicit denied read/mutate/build/execute tests and cross-request authority
tests. A normalization bug once replaced the packed host-rights byte with a
constant; it is fixed by preserving the original high byte in XAX-owned scratch.
Never regress that boundary. Exercise all eight tools, malformed/oversize input,
notifications, unknown methods/tools, output budgets, mutation/build/execution
and current real clients. No modern desktop-client interoperability is established.

### 6. Replay, package, document and ship only after the above checks

Pack immutable native-authored objects into pinned Windows XAXEDIT1 carriers
outside the repository without graph generation. Replay exact roots with mandatory
verification and compare canonical bytes. Preserve unchanged CIDs. Add manifests,
provenance, deterministic double builds, appropriate regression data and new
append-only evidence. Promote the tested final canonical source and update all
default source/snapshot/executable/workflow identities together.

Re-run the existing 65 source-edit chain, 15 probes, 92 client exchanges,
timeout/termination and extracted clean-package gates with the final candidate.
The default gen3 package evidence predates the archived experimental candidates.
Do not relabel it as candidate acceptance. Keep release_ready and
full_mission_complete false while their separate gates remain open.

## Local scratch (optional aid, not a reproducibility dependency)

External scripts, temporary native builds and observations were kept under
`C:\Users\User\.codex\scratch\xax-mcp-20261110\evolution` and its parent.
They include `Compose-Modern.py`, `Compose-Semantics.py`,
`Compose-Capabilities.py`, `Check-Modern.py`, `Test-CompilerProcess.ps1`,
`Test-Pins.ps1` and baseline harnesses. They are deliberately not repository code.
Use retained canonical checkpoints/carriers/evidence if scratch is unavailable.
Set XAXC for each new shell invocation; environment changes do not persist across
tool calls. WSL shell carriers require LF. Python on this host defaults to cp1252;
read/write documentation explicitly as UTF-8 if external tooling is used.

Before this pause, the local Git baseline was aligned to published
`a2677d7cfa08c4d0ad9608d4cd397fa1b523e485` after a fetch and content-hash check;
no working file changed during that alignment. Older audit evidence intentionally
records the original entry state. Re-read current Git status rather than treating
those historical entry observations as the current checkout.
