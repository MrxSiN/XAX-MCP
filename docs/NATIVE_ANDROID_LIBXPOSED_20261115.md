# android-libxposed build and construct (2026-11-15)

The gen3 server (`native/xax-mcp-native.exe`, bytes unchanged) builds and edits
libxposed module APKs when the host gives it the XAX compiler named in
[`native/android-libxposed-dependency.json`](../native/android-libxposed-dependency.json).
No server code changed for this. The default pin is still the older compiler, and
that compiler declines the module build with exit 2.

## Use

Set `XAX_MCP_COMPILER` to the seed that dependency file names, `XAX_MCP_STORE` to
an android-libxposed build request (for example `tests/android-libxposed/module-v7.xax`)
and `XAX_MCP_WORK` to a private directory. Then:

- `xax_build` runs native `resolve` and `build`. The unsigned APK goes to
  `artifact.exe` in the work directory. The server keeps that file name for
  every target.
- `xax_construct` and `xax_transaction` take the usual exact-root `XAXEDIT1`
  record, run native edit, verify the result and publish it. The fixture record
  replaces the module's target object, which changes versionCode 7 to 8.

The rights flags (`--read-only`, `--deny`) and the sandbox work as before.
`xax_execute` cannot run an APK. It builds the APK, then fails with
`launcher_setup_failed`, because the Windows launcher cannot start a file that
is not a PE executable. Signing and installing an APK are up to the host.

## Known gaps

- `xax_capabilities` still reports only `windows-x86_64` and the `af376e8` pin.
  Both strings are compiled into the server. Changing them means a verified
  server transaction and a new server release built with this compiler, which
  produces a different binary (402,944 bytes instead of 399,360).
- JSON `xax-construct-v1` requests are still not accepted, on any platform. The
  native seed has no `construct` command, so new modules have to be written as
  `XAXEDIT1` records or prepared by the host.
- Large modules can still decline until MrxSiN/XAX#53 is merged. This pin is
  older than that change.

Evidence: [native-android-libxposed-20261115.json](evidence/native-android-libxposed-20261115.json).
