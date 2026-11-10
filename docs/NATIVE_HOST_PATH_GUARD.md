# Native configured-path guard — 2026-11-10

The native server now rejects unsafe **host-configured compiler, seed-store and
workspace paths** before compiler-backed operations. The implementation is XAX;
the existing Windows compiler pin and sandbox launcher are unchanged. The server's
authoritative source is `native/xax-mcp-native-gen3.xax`, root
`44f8e6b34a4bd3d50bfb670c1be6a73c9e5bfae7f701383f70eb51e37befd94d`.
The previous gen2 source is retained. The preview version string remains
`0.10.0+native`; use source roots and artifact hashes to distinguish this increment.

## Behavior

`xax_workspace`, `xax_query`, `xax_construct`, `xax_transaction`, `xax_build` and
`xax_execute` validate their configured paths on every operation, including after
the exclusive workspace lease has already been acquired. The compiler and seed
must be existing files; the workspace must be an existing directory.

The guard requires a drive-qualified absolute name, checks each directory prefix
and final component with the existing XAX `GetFileAttributesA` foreign interface,
and rejects an invalid attribute result or `FILE_ATTRIBUTE_REPARSE_POINT`.
Relative, UNC/device, alternate-stream and empty/interior repeated components,
dot/dotdot components and components ending in a dot or space fail closed.
Forward slashes and a final directory separator remain accepted. The guard bounds
its copied path at 4096 bytes; existing configuration/ANSI Windows API bounds may
reject a path earlier. This does not establish general long-path or Unicode-host-
path support. Unicode workload arguments retain their existing separate contract.

An accepted legacy request with an unsafe configured path returns matching text
and structured content, `isError: true`, and:

```json
{"error":{"code":"unsafe_host_path","message":"host paths must be absolute drive paths without reparse points"},"ok":false}
```

No workspace lease or scratch file is created on initial path rejection. A busy
ordinary workspace still returns `workspace_busy`; tool arguments cannot promote
authority or replace host configuration. Extremely long configuration that the
existing startup reader cannot accept still returns `denied_capability`.

## Native authorship and reproducibility

`native/transactions/20261110-host-paths/server-host-paths.batch` is the complete
native workspace carrier. Supporting `.batch` fragments are review data, not
independent sources. The Linux native compiler translates that carrier into the
canonical store. It is an explicitly hash-identified authoring tool, not a Windows
deployment pin upgrade. All graph construction, canonicalization and CID creation
occur natively.

For compatibility with the older pinned Windows editor, external tooling packs
45 already native-authored immutable objects into `server-host-paths.edit` without
changing their bodies/references or constructing graph objects. The pinned native
Windows editor replays that exact-root record and mandatory verification succeeds;
its canonical output is byte-identical to the Linux-native-authored store. 3837
objects retain their canonical identities. The manifest extends the historical
server chain to gen3 and leaves the launcher chain unchanged: 65 source records
in total, including the 46-record base. Historical manifests/evidence are unchanged.

The existing CI selects the new manifest and source through configuration path
changes. No other-language server, native graph emitter or new test script is
added to this repository. External test orchestration remains outside the tree.

## Packaging repair

The existing archive configuration now includes `native/transactions`. Its
staging-directory creation and archive command no longer force reuse/replacement.
A second assembly fails instead of including stale staging content. No new
packaging program or runtime dependency was introduced. Fresh extracted-package
replay/rebuild/execution is recorded locally; a new hosted CI run is not claimed.

## Evidence and boundaries

[Machine evidence](evidence/native-host-path-guard-20261110.json) and
[regression vectors](../tests/security/host-paths/cases.json) distinguish:

- 11 before/after cases: the old server accepted all eight now-rejected path forms;
  three valid forms remain accepted.
- 16 enforcement checks: all six compiler-backed tools, ancestor replacement
  between requests after lease acquisition, object-kind failures and bounded
  configuration failure, with no scratch writes on initial rejection.
- The existing 92-exchange native client suite, golden responses, source replay,
  deterministic builds, native probes and separate timeout/termination checks.

This guard observes paths **before use**; it does not hold their identities across
the check/use interval. Hostile same-user TOCTOU races, hard links, substitutions
of workspace child files, mapped-drive/volume-alias policy, compiler identity at
point of use, cancellation and independent escape review remain open. A drive
letter is not proof that storage is local. Rejecting configured junctions does not
certify arbitrary untrusted native execution or close every path-security gate.

Microsoft documents the attribute semantics used here in
[GetFileAttributesA](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfileattributesa)
and [file attribute constants](https://learn.microsoft.com/en-us/windows/win32/fileio/file-attribute-constants).
The executed junction tests are separate evidence of this server's behavior.
`release_ready` and `full_mission_complete` remain false.
