# Development report — configured paths and preview packaging

| Status | Issue | Result |
|---|---|---|
| Completed | Configured paths traverse reparse points | Native gen3 checks compiler/store/work components before every compiler-backed operation; unsafe paths return `unsafe_host_path` |
| Completed | Lease cache skips later path checks | Ancestor replacement between requests after lease acquisition is rejected |
| Completed | ZIP omits replay inputs / reuses staging | Existing CI configuration includes transactions and refuses an existing staging root or archive |
| Partially completed | Filesystem security | Check/use races, hard links and workspace child-file substitution remain open |
| Blocked / incomplete | Full mission / release | General semantic queries, typed candidates/results, modern MCP, compiler cancellation and independent review remain incomplete |

All new implementation is canonical XAX. Native transaction carriers, JSON test
vectors, documentation and evidence accompany it. No new other-language program
or test script is retained in XAX-MCP. Existing CI changes select native inputs
and package options; external orchestration/transport packing is disclosed below.

## Changes and evidence

The old server accepted all 11 setup cases, including eight unsafe path forms.
Gen3 rejects those eight and preserves the three ordinary valid forms. Sixteen
additional enforcement checks cover all six compiler-backed tools, revalidation
after lease acquisition, invalid object kinds and configuration bounds. Initial
rejection creates no scratch files. Busy workspaces and host authority behavior
remain compatible with the existing tests.

The authoritative root changes from
`16a25c0805b900e3bb45082b0ac88e1217cbf184c1bf739d29d1df1bc298eb83`
to `44f8e6b34a4bd3d50bfb670c1be6a73c9e5bfae7f701383f70eb51e37befd94d`.
3837 objects retain identity. The native authoring carrier constructs the new
helpers and changes the affected graph entry/calls. External record packing copies
45 already native-authored immutable objects; it does not author graph objects.
The pinned native Windows editor replays the result to identical canonical bytes,
and mandatory verification succeeds. The compiler pin and launcher are unchanged.

The final checkout passes 65 verified source records, 15 native probe rebuilds,
two byte-identical executor/provenance builds each, golden STDIO responses, all
92 native client exchanges, wall timeout and live-worker launcher-termination
checks. The new path cases are locally executed; a new hosted CI run is not claimed.

[Machine evidence](native-host-path-guard-20261110.json) records identities, raw
before/after responses, external harnesses, failed candidates and limitations.
[The contract](../NATIVE_HOST_PATH_GUARD.md) describes the compatibility boundary.
Fresh extracted-package results are recorded separately in
`native-host-path-package-20261110.json`; package assembly includes canonical
sources, native carriers, compiler/seed metadata and provenance.

## Reproduction

From `D:\GitHub\XAX-MCP`, use fresh output paths and the exact compiler hash in
`native/xax-dependency.json`. These are native compiler argument vectors:

```text
D:\GitHub\XAX\compiler\bootstrap\windows\xaxc-windows-x86_64.exe edit native/xax-mcp-native-gen2.xax native/transactions/20261110-host-paths/server-host-paths.edit C:\Users\User\.codex\scratch\xax-mcp-20261110\reproduce-host-path.xax
D:\GitHub\XAX\compiler\bootstrap\windows\xaxc-windows-x86_64.exe verify C:\Users\User\.codex\scratch\xax-mcp-20261110\reproduce-host-path.xax C:\Users\User\.codex\scratch\xax-mcp-20261110\reproduce-host-path.diag
D:\GitHub\XAX\compiler\bootstrap\windows\xaxc-windows-x86_64.exe resolve C:\Users\User\.codex\scratch\xax-mcp-20261110\reproduce-host-path.xax C:\Users\User\.codex\scratch\xax-mcp-20261110\reproduce-host-path-snapshot.xax
D:\GitHub\XAX\compiler\bootstrap\windows\xaxc-windows-x86_64.exe build C:\Users\User\.codex\scratch\xax-mcp-20261110\reproduce-host-path-snapshot.xax C:\Users\User\.codex\scratch\xax-mcp-20261110\reproduce-host-path.exe C:\Users\User\.codex\scratch\xax-mcp-20261110\reproduce-host-path.prov
```

Require exit 0 and empty verification diagnostics. Compare canonical source,
snapshot, executable and provenance bytes with the current release/transaction
manifests. The full replay starts from the 20261027 base and then consumes
`native/transactions/20261110-host-paths/manifest.json`, verifying every candidate.
The historical 20261101 manifest remains unchanged.

For an independent client, start `native/xax-mcp-native.exe` with the documented
trusted compiler/store/work environment. Use absolute ordinary paths for the
positive control, then the setups in
[the regression vectors](../../tests/security/host-paths/cases.json). Initialize
legacy MCP, send `notifications/initialized`, call the specified tools and compare
`isError`, `ok` and the error code. Do not interpret the path-replacement-between-
requests case as a check/use race test.

The existing workflow's run blocks reproduce source/build, protocol, resource and
package gates; they were executed from external scripts in
`C:\Users\User\.codex\scratch\xax-mcp-20261110`. The path-specific external
assertion harnesses are identified in machine evidence and are outside the
repository/package. Native batch authoring uses the separately recorded Linux
native executable; the Windows deployment does not require it or an interpreter.

## Remaining risks

The checks do not hold filesystem identities across subsequent use. Hostile
same-user TOCTOU, hard links, scratch child-file substitution, mapped-drive/volume
policy and compiler hashing at point of use still need native solutions and
independent review. The preview still reports raw child exits and lacks complete
compiler cancellation, crash-window and resource-pressure coverage.

The working tree already contained the large uncommitted 0.10 increment and its
HEAD predates that implementation. No unrelated changes were reverted or combined
into a commit/push. The current working source/artifacts and exact reproduction
records are the reviewable result. `release_ready` and `full_mission_complete`
remain false.
