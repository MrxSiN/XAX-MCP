# MCP continuation — updated 2026-11-12

The resumed control-preview acceptance increment is complete. This is an
experimental acceptance result, not promotion or production release readiness.
The paused 2026-11-11 handoff remains in Git history at `1850dd7`.

## JVM increment completed before broader security work

- [x] Added an explicit native JVM snapshot build/execute preview. Canonical XAX
  snapshots produce executable JARs with the separately pinned native compiler;
  a native Windows supervisor runs the host-controlled Java runtime in an
  AppContainer and one-process job. No foreign implementation entered the request path.
- [x] Verified final capabilities report target `jvm`, implementation `EXECUTED`
  and toolchain `TESTED`, with no untested label. The exact compiler and Microsoft
  Java 17 runtime identities are recorded in `native/jvm-dependency.json` and
  the runtime inventory; the default deployment pin is unchanged.
- [x] Passed 53 final MCP feature exchanges, 18 forged-authority denials,
  independent JVM argument/isolation/budget/lifecycle oracles, protocol/paging
  checks and direct installed read-only backend calls to all eight tools.
- [x] Replayed all 49 new native records with mandatory verification and rebuilt
  four programs twice in a fresh empty-PATH package with paths containing spaces.
  Repeated feature and client gates; all packaged bytes stayed unchanged.

See [the JVM acceptance index](docs/evidence/native-jvm-20261112.json), explicit
[target verification](docs/evidence/native-jvm-target-verification-20261112.json)
and [contract](docs/NATIVE_JVM_20261112.md). Build/execute requires already resolved
memory-profile snapshots. Snapshot mutation and unresolved build requests decline;
the native mutation rejection preserves the source. Arguments must fit
Windows-1252; lossy arguments decline before Java creation, while binary stdin
supports all bytes. Forced termination can retain the owned cached JAR's read ACL.
The preview branches from Android and does not combine the separate inspection pin.

The user's existing MCP connection setup remains unchanged. JVM is implemented and
its exact scoped toolchain is tested in the separate preview. Content integrity,
atomic publication, broader workspace aliases and security gates below remain open
and are the next priority. No default promotion or release readiness is claimed.

## Android increment completed

- [x] Built Android ARM64 static artifacts with the retained compiler and executed
  them through host-controlled ADB on the connected authorized Pixel 8 Pro.
- [x] Added native Windows ADB broker and native Android supervisor, exact bounded
  stdin/argv/streams, syscall and resource enforcement, and worker lifecycle tests.
- [x] Replayed 56 new native transactions and rebuilt twelve programs twice in a
  fresh extracted package with empty PATH and Windows paths containing spaces.
- [x] Passed protocol, authority, metadata, whitespace, public paging and installed
  read-only backend gates against the Android server.

See [the Android evidence](docs/evidence/native-android-20261112.json) and
[contract](docs/NATIVE_ANDROID_20261112.md). This is a separate explicit preview;
static ELF only, staging-interruption cleanup and workspace aliases remain open.
The control preview and default Gen3 remain unchanged. A fresh
[target/toolchain verification](docs/evidence/native-android-target-verification-20261112.json)
passed before further alias work: Android ARM64 is implemented and its exact seed
is tested for this profile. At that milestone JVM was not exposed; the active
desktop connection remains the separate Windows-only preview. The later JVM
increment above is separate from both this Android source and that connection.

## Bounded alias/security increment completed

- [x] Added an explicit native inspection-output pin preview. Pre-existing record
  aliases decline before truncation; twenty concurrent substitution trials caused
  no outside sentinel writes. All source bytes remained unchanged.
- [x] Tested directory replacement, an owned DOS mapping, stable handles across
  101 queries, native compiler descendant cleanup, host authority and client
  execution-override denials. Confirmed that output content remains writable.
- [x] Passed one exact-root pinned replay, deterministic rebuilds, public pages,
  installed read-only backend calls and a fresh empty-PATH package.
- [x] Added and locally executed a CI step replaying 57 new records and double
  building thirteen native programs. Hosted acceptance is a separate gate.
- [x] Reconfirmed Android query/build/device execution after the change. Android
  static-profile toolchain status is tested; that source does not expose JVM. At the user's
  request, existing active MCP connection setup remains unchanged.

See [the inspection-pin evidence](docs/evidence/native-inspection-pins-20261112.json)
and [contract](docs/NATIVE_INSPECTION_PINS_20261112.md). The preview requires a fresh
work directory for every server process and does not authenticate output contents
or cover other compiler outputs and publication. It is not promoted.

## Prior completed increment

- [x] Completed the append-only historical evidence export with actual source
  milestone bindings; preserved all existing evidence.
- [x] Passed the required final-source local protocol, metadata, whitespace,
  cancellation/queue, post-edit verification, timeout, server-death, descendant,
  file-pin and public-query suites.
- [x] Repeated the unfamiliar-program exercise with retained independent data:
  three functions, two real calls, four neighborhood pages and actual exit 66.
  The final-server inventory matched 5,443 objects over 86 pages.
- [x] Tested a fresh extracted package with an empty parent PATH and bundled
  pinned compiler. Replayed all 65 + 9 + 19 source transactions with native
  verification; rebuilt fifteen probes, final binaries and three new fixtures
  twice; matched snapshot/executable/provenance identities; passed all client gates.
- [x] Reconfirmed direct installed Codex backend calls to all eight tools, with
  no capture proxy on the accepted path.
- [x] Exercised all eight tools through this active desktop chat, including
  successful reads, read-only write/build/execute denials, unsupported result
  handles and full text/structured equality. Repeated after compiler relocation.
- [x] Updated current release/status links while preserving false readiness
  flags and default Gen3 identities. Reviewed native carriers, fixtures, schema
  and artifacts; no foreign implementation entered the repository.

The [evidence index](docs/evidence/native-control-20261112.json) links separate
historical, final-source local, clean-package, backend, desktop and review records.
The package records assembly-time contents; subsequent evidence and reporting-only
metadata are outside that tested archive. Its README uses committed bytes, while
the user's working README edit remains intact and excluded from the increment.

## Current source and toolchain

The JVM preview uses `native/candidates/20261112-jvm/checkpoints.json` and its own
immutable `native/jvm-dependency.json`. It does not repin the default deployment.
The separate Android and inspection-pin canonical sources and artifacts are bound
by `native/candidates/20261112-android/checkpoints.json` and
`native/candidates/20261112-read-pins/checkpoints.json`. Neither is selected as
the default or active desktop connection.

The control preview remains `native/candidates/20261111-control/server.xax`, root
`2e8497012a44db978ff71c768243b6c5b66c1f5f75a0ae7bd85c856118745612`.
Its artifacts and nineteen source records are unchanged. See
`native/candidates/20261111-control/checkpoints.json` and
`native/transactions/20261111-control/manifest.json`.

The default server remains Gen3, root
`44f8e6b34a4bd3d50bfb670c1be6a73c9e5bfae7f701383f70eb51e37befd94d`.
`release_ready`, `full_mission_complete` and candidate promotion remain false.
The deployment dependency is unchanged in `native/xax-dependency.json`.

`D:\GitHub\XAX` was pulled to `745e80150605f3812aa012e6884f6e417d9423b4`
and is clean. The updated upstream Windows compiler is a different seed and is
not certified for this deployment. Before updating it, the original pinned
compiler was retained at:

```text
C:\Users\User\.codex\scratch\xax-mcp-20261112\toolchain\xaxc-windows-x86_64.exe
SHA-256: aa72234d6dd8a111efde62b47ced8449a482c4c5506d876714ff7fbe0968ab79
```

The configured `xax_native_preview_20261111` remains read-only with its prior
store/work paths. Only its compiler environment path changed to that separate
pinned copy. Active tools reconnected and passed after the change; no user reload
was needed. Preserve that pin rather than silently using upstream main's seed.

Foreign inspection/acceptance/packing utilities stay outside the repository.
The resumed harness, logs and extracted archive are under
`C:\Users\User\.codex\scratch\xax-mcp-20261112`. Earlier utilities/evidence
remain under the 20261111 and 20261111-next scratch directories. Set `XAXC` per
PowerShell invocation; use the separate pinned copy for this deployment.

## Remaining release and capability boundaries

- [ ] Close writable workspace child-file substitution/publication and DOS
  drive-alias remapping through the reusable upstream handle/identity contract.
  Historical/default/control previews retain the recorded outside writes. The
  new inspection-pin preview prevents the tested `edit.rec` name substitutions;
  output content remains writable and other compiler file modes are unchanged. Preserve `docs/NATIVE_HANDLE_CONTRACT.md`; pathname rechecks
  alone do not close TOCTOU races. Broaden hard-link, directory replacement,
  output and crash coverage before claiming safety for untrusted workspace files.
- [ ] Add independently verified public typed inspection upstream before
  repinning: signatures, blocks/operations, effects, typed traversals, candidate
  comparisons and complete inventory continuation remain absent. Current pages
  expose generic references, stop at a 4 MiB prefix and contain at most 64 rows.
- [ ] Address cancellation backpressure beyond the 1 MiB queue where required;
  retain the 30-second compiler deadline and the documented nonzero numeric-ID
  exponent normalization bound of 8,388,608.
- [ ] Implement full CUM prepare, portable result handles, registered external
  tools and general typed execution layouts as separate native increments.
- [ ] Complete exhaustive pressure/exhaustion, crash/cleanup and independent
  escape/security acceptance. The pinned deployment compiler's self-hosting
  and production readiness are not established by this increment.
- [ ] Run/verify hosted CI for the Android/inspection-pin workflow step and separate
  JVM build/replay job, then satisfy promotion gates before selecting a preview
  as the default. Desktop acceptance here covers the configured read-only path;
  writable desktop execution requires separate acceptance.

Continue canonical changes only through exact-root native XAX transactions with
mandatory verification. Keep application implementation native XAX, preserve
historical evidence, and commit/push completed increments to `main` without
attribution trailers or the user's unrelated README edit.
