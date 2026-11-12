# Android ARM64 execution preview

This explicit Windows-hosted preview builds static Android ARM64 ELF artifacts
with the retained deployment compiler, then deploys and executes them through
host-controlled ADB. Application components remain native canonical XAX. The
server, Windows ADB broker and Android supervisor are in
`native/candidates/20261112-android/`; Gen3 and the existing read-only desktop
preview remain unchanged. Release readiness and promotion remain false.

The [target/toolchain verification](evidence/native-android-target-verification-20261112.json)
confirms the live preview advertises `android-arm64`, builds ELF machine 183 and
executes the exact artifact on the authorized device. The immutable deployment
seed is **TESTED for this static Android profile**, not an untested toolchain.
This does not certify a moving upstream seed, JVM, all Android devices or general
release readiness. JVM is not exposed by this MCP preview. The currently active
`xax_native_preview_20261111` desktop connection remains Windows-only; selecting
the separate Android server is required for Android calls.

## Use

Select `native/candidates/20261112-android/xax-mcp-native.exe` as the stdio server.
Keep its `xax-mcp-sandbox.exe` broker and `android-runner` beside it. Grant execution
with `--allow-execute` and configure these host environment variables:

- `XAX_MCP_COMPILER`: the retained compiler identified by `native/xax-dependency.json`.
- `XAX_MCP_STORE`: an authorized Android ARM64 canonical request, for example
  `tests/android/hello-arm64.xax`.
- `XAX_MCP_WORK`: a dedicated, trusted Windows workspace.
- `XAX_MCP_ADB`: `C:\platform-tools\adb.exe` on the tested host.
- `XAX_MCP_ANDROID_SERIAL`: the authorized device serial from `adb devices`.

The device must already authorize host ADB access. The client cannot choose a
host/device executable, remote path, serial, environment or larger resource budget.
`xax_build` builds the current authorized request; `xax_execute` builds and runs it.
The eight-tool interface is `schemas/tools-v4.json`; existing read-only and deny
flags still control authority. Binary stdin is hex and arguments are explicit
strings. Streams are returned separately as exact hex, with actual exit and
resource measurements. The hello fixture emits `XAX Android ARM64` plus LF and
exits 66. Windows PE artifacts fail Android admission.

## Native execution boundary

The broker launches fixed ADB operations with quoted Windows argv, no command
interpreter on Windows, and exclusive temporary capture files held open until
closed. Remote command strings contain only generated private paths and fixed
operations. Client arguments travel as bounded binary UTF-8, never shell text.
The supervisor admits only the pinned compiler's bounded static ELF64 ARM64
layout. It holds the artifact/input/output descriptors, unlinks its six staging
names and removes its private UUID directory before starting the worker. The
worker executes the held artifact descriptor after unlinking.

The worker receives an empty environment and only fd 0, 1 and 2. Native setup
clears the signal mask, resets budget signal handlers, disables core dumps,
sets no-new-privileges and applies an ARM64-checked seccomp allowlist. Read is
restricted to stdin and write to stdout/stderr. After the one held-fd launch,
process creation, file opening, networking, further execution, signal-handler
changes and signal return are denied. The initial executable descriptor closes
on exec. Parent death kills the worker. The supervisor reports monotonic elapsed
time and wait4 CPU/peak RSS observations; peak RSS is distinct from virtual
address space and from Windows job commit accounting.

Fixed limits are 256 KiB stdin, 64 arguments with the existing UTF-16 transport
budget, 256 MiB virtual address space, five seconds CPU and ten seconds wall time.
CPU uses a default SIGXCPU at five seconds with a six-second hard-stop backup.
Each device output file is capped at 1 MiB + 1 byte; combined returned output is
at most 1 MiB. Device spooling can therefore reach 2 MiB + 2 bytes. On output,
CPU or wall exhaustion, partial streams are withheld. Other signals are reported
as raw `128 + signal` exits, without claiming general trap classification.

## Evidence and remaining gates

See `docs/evidence/native-android-20261112.json` for exact source/artifact identities,
native replay, device acceptance, protocol/backend acceptance and a separate fresh
package record. Native construction intermediates are identified in the replay
manifest; they are never accepted as runnable deployments. Foreign inspection,
packing and test utilities remain outside the repository and request path.

This profile covers static native programs on the tested authorized device.
APK packaging, Android framework/JNI APIs, shared libraries, general typed layouts,
Android-hosted MCP and a device/OS compatibility matrix remain unsupported.
Cancellation and forced server death during the running worker were tested;
interruption during staging can leave inert files in the owned UUID directory.
Pre-existing workspace aliases, atomic publication, DOS alias remapping, exhaustive
pressure/crash windows and independent escape acceptance remain open. ADB access
and Windows workspace administration are trusted host grants. Do not infer those
broader guarantees from the worker syscall tests or promote this preview by default.
