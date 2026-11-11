# Remaining MCP work — paused 2026-11-11

Implementation stopped at the user's request. This is a handoff, not a release
or completion claim. Do not describe unfinished acceptance work as delivered.

## Current checkout and protected work

- Work in `D:\GitHub\XAX-MCP`; branch `main`, last published baseline
  `289e377` (`Repair experimental protocol replies and preserve native replay`).
  The user subsequently requested a checkpoint commit and push of the paused
  increment. Inspect Git history/status for that checkpoint before resuming.
- `README.md` had a pre-existing user edit removing sixteen progress-note lines.
  Preserve it and exclude it from this increment's commit. Its last observed
  SHA-256 was `9c662558dc41a6730149c1b1f49f5b062adc4770f575c0e4e0fc743b5b236bcf`;
  a later user change must also be preserved.
- XAX was clean at `6bcaf771bbb22e1b72a5a9af4c806da763b70b8f` on the last check.
  No upstream implementation was changed. Do not disturb unrelated upstream work.
- The default server, snapshot, executable and workflow still select Gen3, root
  `44f8e6b34a4bd3d50bfb670c1be6a73c9e5bfae7f701383f70eb51e37befd94d`.
  The new source is an explicit experimental preview, not the default deployment.
- Keep `release_ready` and `full_mission_complete` false. No Windows compiler
  self-hosting or production readiness is established.

Read `CLAUDE.md`, `native/release-status.json`, the current manifests and Git
state before editing. Only native XAX implementation belongs in this repository.
Canonical `.xax` stores are authoritative; native batch/XAXEDIT1 files are
construction carriers. Foreign test, inspection and packing utilities remain
outside the repository. Commit and push to `main` when the resumed increment is
ready; do not add attribution trailers.

## Frozen experimental source

The latest canonical source is
`native/candidates/20261111-control/server.xax`, root:

```text
2e8497012a44db978ff71c768243b6c5b66c1f5f75a0ae7bd85c856118745612
```

`native/candidates/20261111-control/checkpoints.json` records the canonical
milestones, snapshot, executable, provenance and sandbox identities.
`native/transactions/20261111-control/manifest.json` records **19 new exact-root
Windows replays**, after the previous nine experimental records. All nineteen
passed mandatory native verification and canonical/file byte comparisons.
Unchanged object CIDs were checked. These extend the original 65-record Gen3
chain; do not confuse source-record counts with client-exchange counts.

The final executable and provenance were built twice and compared byte for byte.
The deployment compiler pin is unchanged:

- Dependency: `native/xax-dependency.json`, commit
  `af376e8a8a1ac5635bcad459cb7063ef0b326430`.
- Windows seed: `D:\GitHub\XAX\compiler\bootstrap\windows\xaxc-windows-x86_64.exe`.
- Windows seed SHA-256:
  `aa72234d6dd8a111efde62b47ced8449a482c4c5506d876714ff7fbe0968ab79`.
- Native authoring used the Linux seed through WSL, SHA-256
  `a35fd59fc9effe08f58f6d1db0d2e951abbd56a065dc0dca729c9bc6f5ec793b`.
  This is an authoring identity, not permission to repin deployment.

Do not concatenate rootless `.batch` fragments. Full carriers retain their
exact bases, native selectors, definition order, labels and ownership. Schema
prefix and capability chunks are construction intermediates, not working
runtime checkpoints. The pinned Windows transport limit required splitting the
schema literal; do not silently recombine it or upgrade the seed.

## Implemented in the preview, within stated bounds

- Compiler waits poll stdin and preserve queued ordinary requests. Matching
  cancellation stops the child, confirms descendant cleanup and suppresses the
  cancelled request's response. EOF is not automatic cancellation.
- The server-owned kill-on-close job contains descendants. Cleanup opens each
  process and checks membership in the exact job before termination, guarding
  against PID reuse. Failure to confirm cleanup exits the server.
- Compiler deadline: 30 seconds. Input polling interval: 20 ms. Queue: 1 MiB.
  A larger queued ordinary frame can delay a later cancellation through
  backpressure; this is an explicit remaining boundary.
- String IDs compare logical Unicode; numeric IDs compare exact decimal values
  without floating-point rounding. Nonzero exponent normalization is bounded at
  8,388,608. Do not claim compatibility for larger nonzero exponents. Zero
  exponent spellings and negative zero are handled separately.
- Closed query arguments support objects, entity lookup, dependencies, users,
  one-hop reference neighborhoods, source-kind filters and root-bound cursors.
  Pages contain at most 64 rows. Empty arguments retain the legacy query body.
- Queries consume only the compiler's public kind/CID/reference record, bounded
  at a 4 MiB prefix. Incomplete inventories are explicit; there is no continuation
  beyond that prefix. Typed signatures, blocks/operations, effects, deeper typed
  traversals and candidate comparisons remain unimplemented.
- Legacy progress metadata is distinguished from modern protocol-specific
  metadata. Modern mandatory metadata validation and host authority are retained.
- The preview advertises `schemas/tools-v3.json`. Default Gen3 still uses v2.

The corresponding drafts are `docs/NATIVE_CONTROL_20261111.md` and
`docs/NATIVE_REFERENCE_QUERIES.md`. `CLAUDE.md` has a new preview handoff paragraph.
The final evidence index has **not yet been created**; the preview guide points
to this paused-work checklist instead.

## Test provenance — do not merge old and final acceptance

The final source above passed:

- 19 new pinned Windows edit/verify replays, exact canonical/file comparisons,
  and two identical final executable/provenance builds.
- 96 protocol exchanges, including 18 authority denials, all eight tools,
  legacy versions, malformed/oversize recovery and full text/structured equality.
- 169 semantic-page exchanges against an independent seed inventory, including
  all selectors, page sizes, escaped CIDs, unknown entities and stale cursors
  after a real mutation.
- 28 numeric query-argument cases using a Decimal oracle, including whole-valued
  decimal/exponent forms and out-of-range/fractional rejection.
- Seven configured-file/ancestor OS-enforced replacement denials and exit release.
- A real native mutation cancelled during its mandatory verification child:
  source bytes, root and file identity were preserved; staged source was removed;
  cancellation was silent, queued ping worked and the lease released on exit.
- The alias probe again observed the **known outside-write failures** for
  pre-existing and concurrent workspace `edit.rec` aliases. This gate is open.

Other completed development runs have earlier source bindings:

- Root `d5653a7c630eb6ee5e5c9ea7595bc14dbb714c646d1d07cd99ce0d926098d0b4`
  (stage 11, before the final query-integer normalization): 92 legacy exchanges;
  cancellation string/Unicode/prefetch cases; numeric cancellation equivalence
  and distinct-large-integer cases; five cancelled compiler-backed tool paths;
  ordinary/partial queues, EOF and late/unknown notifications; descendant cleanup
  on cancellation, normal compiler exit and server death; installed Codex backend
  calls to all eight tools with read-only denials and text/structured equality.
- Root `4166f654254dbbb60ed14d68e8255654721089978093d7988c86ad0e0f074b6c`
  (completed capability literals): 25 modern/legacy metadata exchanges.
- Root `d0a87bd290ca5115aa4b3535071ea5d721b61024aa71385fa3e741bb07e7a0b7`
  (stage 06): 107 program/inventory exchanges. Three functions and two real calls
  were located through public queries and checked independently. A caller-body
  neighborhood needed four one-row pages. Its 4,807-object server input was
  compared over 76 pages. This is not final-source acceptance.
- The earlier deadline/server-death probe was run on the cancellation milestone
  `fc2d6cedfb98f952ee76379620871d22bd0f09782b1805ab29a4d615397ab337`.

The native fixture manifest is
`native/transactions/20261111-control/fixtures.json`. It records Windows replay,
verification and double builds for the three-function program and hanging /
returning descendant fixtures. The semantic program exits 66. Descendant fixtures
use `tests/security/timeout/timeout.exe` relative to the test working directory,
so clean-package tests must run with the extracted package as cwd.

## Remaining tasks

- [ ] Finish the append-only evidence export and final evidence index. Bind each
  suite to its actual source milestone; do not present earlier runs as final-source
  acceptance. Preserve historical evidence.
- [ ] Re-run the required final-source gates: original 65-edit chain, 15 native
  probes, 92 legacy exchanges, mixed modern/legacy baseline, 25 metadata cases,
  96 protocol cases, whitespace/state cases, cancellation and queue cases,
  post-edit verification cancellation, timeout/server-death and descendants.
- [ ] Re-run the unfamiliar-program/public-inventory exercise with the final
  executable. Use the independent retained fixture data and actual native program
  execution. Keep the generic-reference/typed-fact distinction.
- [ ] Build and test a genuinely fresh extracted package with an empty parent
  PATH and the bundled pinned compiler. Replay all 65 + 9 + 19 source transactions
  with mandatory verification; rebuild the 15 probes and final binaries twice;
  compare snapshot, executable and provenance identities. Run the final client
  gates against the extracted candidate. New-candidate clean-package acceptance
  has **not been run**.
- [ ] Confirm final-source installed Codex backend interoperability again, directly
  with the native executable (no capture proxy on the accepted path). Keep this
  separate from desktop UI tool-call acceptance.
- [ ] Complete desktop UI tool-call acceptance when the active chat can expose
  the configured server. The UI configuration/loading observation alone is not
  execution acceptance. Do not repeatedly ask the user to reload it.
- [ ] Finish accurate release/status metadata and evidence links. Preserve false
  readiness flags and the default Gen3 identities until promotion gates are met.
- [ ] Review native carriers, fixture manifests, schema and docs for consistency;
  check no foreign implementation/orchestration files entered the repository.
- [ ] After completing the remaining gates, commit the ready resumed increment
  and push `main`, excluding the user's README edit and without attribution
  trailers. The user-requested paused checkpoint is separate from release acceptance.

## Desktop preview state

The global Codex MCP entry `xax_native_preview_20261111` was added with:

```text
command: D:/GitHub/XAX-MCP/native/candidates/20261111-control/xax-mcp-native.exe
args: --read-only
XAX_MCP_COMPILER: D:/GitHub/XAX/compiler/bootstrap/windows/xaxc-windows-x86_64.exe
XAX_MCP_STORE: D:/GitHub/XAX-MCP/tests/protocol/semantic-paging/program.xax
XAX_MCP_WORK: C:/Users/User/.codex/scratch/xax-mcp-desktop-20261111-7e41b3f5d2ef494c819f412db60d4263
```

The user explicitly asked to reload it, then reported **“MCP loaded.”** Its
configuration was observed in the desktop UI. The active chat's tool inventory
still exposed no XAX tools, and no running native preview process was observed
on the subsequent check. Do not claim desktop UI tool calls passed. The standalone
installed client backend did execute all eight tools in an isolated ephemeral
test session, without a model turn or user-visible test chat.

Keep the configured read-only preview; the user requested it loaded. Do not
change unrelated MCP entries or app permissions. The active app-server proxy
failed with Windows socket error 10050; it is not a working reload/call route.

## External tools and incomplete export

All new foreign utilities are under:

```text
C:\Users\User\.codex\scratch\xax-mcp-20261111-next
```

Important scripts: `native_carriers.py`, `author-*.py`, `native_literal.py`,
`pack-control.py`, `pack-control-fixtures.py`, `Check-Protocol.py`,
`Check-SemanticPages.py`, `Check-PagingProgram.py`, `Check-QueryNumbers.py`,
`Check-Cancellation.py`, `Check-NumericCancellation.py`, `Check-CancelMutation.py`,
`Check-CancelQueue.py`, `Test-CancelVerify.ps1`, `Test-Descendants.ps1`,
`Test-CompilerProcess.ps1`, `Test-Pins.ps1`, `Check-Aliases.py` and
`Check-CodexClient.py`. `final-source.txt` names stage 12 in its `build/` folder.

`record-control-runtime.py` **failed partway through**, because Python does not
recognize encoding `utf8-sig`; use `utf-8-sig`. It already created:

- `tests/protocol/semantic-paging/inventories.json`: independent read-only oracle
  data for the seed, fixture program and final server source, with real call facts
  for the program. The server never consumes this data.
- `docs/evidence/native-control-protocol-20261111.ndjson.gz` (final-source run).
- `docs/evidence/native-control-reference-pages-20261111.ndjson.gz` (final-source run).
- `docs/evidence/native-control-reference-program-20261111.ndjson.gz` (earlier
  stage-06 program run; preserve that binding).

Do not blindly rerun the export: its existing-file assertions will fire. Make
resumption compare existing contents without overwriting them, or write separate
new evidence files. The intended runtime index also needs milestone bindings
corrected as described above. `native-control-runtime-20261111.json`,
`native-control-20261111.json` and the new clean-package result do not exist yet.
`native/release-status.json` has not been updated for this control preview.

The older clean-package harness is
`C:\Users\User\.codex\scratch\xax-mcp-20261111\Check-Package.py`.
Adapt it outside the repository: combine the previous nine-record manifest and
the new nineteen-record manifest, use the new candidate artifacts/schema, and
retain fresh extraction and empty-PATH checks. Copy/adapt its mixed-modern harness
from `modern-full/Test-ModernBaseline.ps1`. Never overwrite its historical evidence.
For the user's modified README, package the committed README bytes without
changing the working file, so acceptance can match the eventual commit.

Set `XAXC` for each new PowerShell invocation; environment changes do not persist
between tool calls. Use LF for WSL carriers and explicit UTF-8 for documentation.
The installed CLI observed during acceptance was `codex-cli 0.167.0-alpha.4.1`;
resolve its current executable instead of retaining an obsolete app-update path.

## Boundaries still open beyond this increment

- Writable workspace child-file substitution/publication and DOS drive-alias
  remapping remain open. The pinned compiler accesses outputs by filename.
  Preserve `docs/NATIVE_HANDLE_CONTRACT.md`; another pathname recheck is not
  complete TOCTOU protection. More hard-link/directory-replacement/output/crash/
  attacker coverage and the upstream handle/identity contract remain necessary.
- Typed semantic facts and complete inventory continuation need a reusable,
  independently verified upstream public inspection extension before repinning.
- Full CUM prepare, portable result handles, registered external tools, general
  typed execution layouts, exhaustive pressure/crash/escape acceptance and Windows
  compiler self-hosting remain separate incomplete gates.

No additional implementation test jobs matching this scratch/candidate were
observed running at the pause check. Recheck processes before resuming; do not
terminate unrelated user processes.
