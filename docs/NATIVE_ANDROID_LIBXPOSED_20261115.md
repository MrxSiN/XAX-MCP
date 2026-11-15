# android-libxposed build and construct (2026-11-15)

`native/candidates/20261115-android-libxposed/` holds a separate candidate
server that builds and edits libxposed module APKs, and that reports this in
`xax_capabilities`. It uses the XAX compiler named in
[`native/android-libxposed-dependency.json`](../native/android-libxposed-dependency.json).
The default gen3 deployment, its `af376e8` pin and its release identities do not
change. Promoting the candidate to the default is a separate decision.

## What changed in the server

The capability transaction is four native batches in
[`native/transactions/20261115-android-libxposed/`](../native/transactions/20261115-android-libxposed/manifest.json).
Each batch redefines one capability literal function (`define` + `replace`): the
two halves of the structured JSON and the two halves of its escaped text copy.
Native edit applies each batch to gen3, and native verify accepts each result.
No other function changes. The new strings add:

- a second `targets` entry: `android-libxposed`, artifact "unsigned libxposed
  module APK", tools `xax_construct`, `xax_transaction` and `xax_build`,
  `execute: false`;
- `xax.pinned_commit`: `acd4046ecddd6d113f86fb23ff1558ae1355b4d6`;
- one sentence each in the `xax_build` and `xax_execute` descriptions.

The compiler builds the server and the unchanged gen1 launcher twice each, and
both builds give identical bytes. Against the read-only protocol fixture, the
only response that changes is `xax_capabilities`. The `io-echo` and
`confinement-read-network` probes give the same results as gen3.

## Use

Run `native/candidates/20261115-android-libxposed/xax-mcp-native.exe`, with its
`xax-mcp-sandbox.exe` in the same directory. Set `XAX_MCP_COMPILER` to the seed
named by the dependency file, `XAX_MCP_STORE` to an android-libxposed build
request (for example `tests/android-libxposed/module-v7.xax`) and `XAX_MCP_WORK`
to a private directory. Then:

- `xax_build` runs native `resolve` and `build`. The unsigned APK goes to
  `artifact.exe` in the work directory. The server keeps that file name for
  every target.
- `xax_construct` and `xax_transaction` take the usual exact-root `XAXEDIT1`
  record, run native edit, verify the result and publish it. The fixture record
  replaces the module's target object, which changes versionCode 7 to 8.

The rights flags and the sandbox work as in gen3. `xax_execute` cannot run an
APK. It builds the APK, then fails with `launcher_setup_failed`. Signing and
installing an APK are up to the host.

`tests/android-libxposed/check.ps1` runs all of this. The CI job
`windows-android-libxposed` runs the same script.

## Known gaps

- JSON `xax-construct-v1` requests are still not accepted, on any platform. The
  native seed has no `construct` command.
- Large modules can still decline until MrxSiN/XAX#53 is merged. This pin is
  older than that change.
- The server version string is still `0.10.0+native`.

Evidence: [native-android-libxposed-20261115.json](evidence/native-android-libxposed-20261115.json).
