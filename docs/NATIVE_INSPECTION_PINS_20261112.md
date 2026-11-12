# Native inspection output-name pins

This explicit preview prevents the tested `edit.rec` name substitutions from
redirecting a native inspection write into an unrelated outside file. It extends
the Android server through one exact-root native transaction. The default Gen3,
Android acceptance checkpoint and active desktop Windows preview remain unchanged.
It is a bounded name-protection increment, not complete workspace security or
candidate promotion.

## Mechanism and use

The new native helper recognizes the server's internal `inspect` invocation.
Before launching the compiler, it creates the output with `CREATE_NEW`, obtains
its volume-GUID path from the held handle and supplies that path as the compiler's
output argument. Existing output objects are refused before truncation. The
non-inheritable read handle shares read/write access, denies delete sharing, and
stays open for the server lifetime. Subsequent inspections reuse that owned object;
substituting or renaming its name fails while the pin is held. Configured ancestor
pins, native compiler cancellation/job control and host authority checks remain in
force. Other compiler modes retain their previous contract.

Select `native/candidates/20261112-read-pins/xax-mcp-native.exe` explicitly and use
a **fresh trusted work directory for each server process**. Read-only acceptance
uses `--read-only`; a separate `--allow-execute --deny mutate` query/build/Android
execution sequence was also tested. The companion broker and supervisor are exact
copies from the accepted Android checkpoint. Device and compiler configuration
follow [the Android contract](NATIVE_ANDROID_20261112.md).

The output pin closes at server exit, but `edit.rec` remains. A new process refuses
that existing object instead of assuming ownership lost at shutdown or crash.
Use a new work directory. This preview does not replace the default deployment or
provide general mutation/publication acceptance.

## Executed checks

The [evidence](evidence/native-inspection-pins-20261112.json) binds the final source,
compiler, replay, deterministic builds and client records. The old server overwrote
disposable outside sentinels through pre-existing and concurrent record hard links.
The new preview preserved all outside sentinels across the corresponding cases,
including twenty concurrent substitution trials, and denied a pre-existing regular
output. Repeated queries succeeded and an owned output could not be renamed.

The tested unused DOS drive-alias remapping was rejected by both old and new
servers without outside writes; this is a bounded denial observation, not closure
of every DOS namespace race. Workspace/ancestor renames were denied. After 101
queries, handle counts were stable; exit released the pin. Native compiler fault
fixtures confirmed cancellation, normal-return descendant cleanup and server-death
cleanup, with output handles released after exit. These fault fixtures are distinct
from the tested real compiler seed.

Authority checks retained host grants despite forged client rights. Unknown path,
executable, environment, device and budget arguments were rejected before build.
Public reference paging, installed read-only backend calls and a fresh-package
native replay/build check passed. A query/build/Android-execute/query sequence on
the connected device passed with paths containing spaces. The immutable Android
static-profile toolchain remains tested; JVM is not implemented by these previews.
The CI workflow now replays the Android and inspection-pin carriers and double
builds thirteen native programs. Local execution of that exact step is separate
from any hosted CI result; no hosted device execution is claimed.

## Gates that remain open

The compiler still writes by pathname. Its output must be writable while it runs,
so the held read handle permits other writers. An independent probe successfully
modified the pinned output contents while the server was idle; the next inspection
regenerated valid facts. The pin does not authenticate concurrent output contents,
seal a completed candidate, or bind verification and atomic publication to a held
object. Input-record, candidate/build/provenance outputs, publication, every DOS
alias race and crash window still need the reusable upstream
[handle/identity contract](NATIVE_HANDLE_CONTRACT.md).

Full typed semantic inspection, full CUM prepare, portable result handles,
registered tools, exhaustive pressure/escape acceptance, Android staging-crash
cleanup and promotion remain open. Release readiness and full mission completion
stay false. Preserve these distinctions when reporting the fixed name-substitution
cases; do not relabel the historical servers or broader gates as safe.
