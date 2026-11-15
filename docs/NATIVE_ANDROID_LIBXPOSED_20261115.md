# android-libxposed build and construct (2026-11-15)

Since 2026-11-15 the default server, `native/xax-mcp-native.exe`, is gen4. Gen4
builds and edits libxposed module APKs, and it reports that in
`xax_capabilities`. The deployment uses the XAX pin in
[`native/xax-dependency.json`](../native/xax-dependency.json) (`acd4046`). The
previous pin, `af376e8`, declines the module build. That pin is kept in
[`native/preview-20261112-dependency.json`](../native/preview-20261112-dependency.json)
for the 20261112 Android ARM64 and inspection-pin previews, because it built
their recorded artifacts.

## What changed in the server

Gen4 is gen3 plus four native batches, recorded in
[`native/transactions/20261115-android-libxposed/`](../native/transactions/20261115-android-libxposed/manifest.json).
Each batch redefines one capability literal function (`define` + `replace`): the
two halves of the structured JSON and the two halves of its escaped text copy.
Native edit applies each batch, and native verify accepts each result. No other
function changes. The new strings add:

- a second `targets` entry: `android-libxposed`, artifact "unsigned libxposed
  module APK", tools `xax_construct`, `xax_transaction` and `xax_build`,
  `execute: false`;
- `xax.pinned_commit`: `acd4046ecddd6d113f86fb23ff1558ae1355b4d6`;
- one sentence each in the `xax_build` and `xax_execute` descriptions.

## What moved with the pin

The new compiler builds every program to new bytes. The following were rebuilt
with it, each built twice with identical results, and recorded again:

- the server and the unchanged gen1 launcher;
- the server snapshot;
- the 15 executor probes and the timeout fixture.

The read-only golden capabilities response was also recorded again, because the
capabilities text changed.

The source replays are unchanged: the 46 base records, the 19 host-path records
and the 15 probe sources reproduce exactly with the new compiler. The CI job
`windows-native` uses the new pin. A second checkout of `af376e8` serves only
the 20261112 preview replay and rebuild step.

## Use

Install as before ([INSTALL_WINDOWS.md](INSTALL_WINDOWS.md)). For a libxposed
module, set `XAX_MCP_STORE` to an android-libxposed build request, for example
`tests/android-libxposed/module-v7.xax`. Then:

- `xax_build` runs native `resolve` and `build`. The unsigned APK goes to
  `artifact.exe` in the work directory. The server keeps that file name for
  every target.
- `xax_construct` and `xax_transaction` take the usual exact-root `XAXEDIT1`
  record, run native edit, verify the result and publish it. The fixture record
  replaces the module's target object, which changes versionCode 7 to 8.

`xax_execute` cannot run an APK. It builds the APK, then fails with
`launcher_setup_failed`. Signing and installing an APK are up to the host.

The `windows-native` CI step "Build, construct and rebuild a libxposed module through the native server" replays
the four records and runs the module session through the deployed server.

## Known gaps

- JSON `xax-construct-v1` requests are still not accepted, on any platform. The
  native seed has no `construct` command.
- Large modules can still decline until MrxSiN/XAX#53 is merged. This pin is
  older than that change.
- The server version string is still `0.10.0+native`. Release readiness remains
  false.

Evidence: [native-android-libxposed-20261115.json](evidence/native-android-libxposed-20261115.json).
