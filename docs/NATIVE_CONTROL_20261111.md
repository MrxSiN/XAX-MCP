# Native control and reference-query preview

This is a tested experimental successor to Gen3, not the default deployment.
The canonical source and all artifact identities are in
[`native/candidates/20261111-control/checkpoints.json`](../native/candidates/20261111-control/checkpoints.json).
The compiler dependency stays pinned to [`native/xax-dependency.json`](../native/xax-dependency.json).
These tests establish neither self-hosting of the pinned deployment compiler nor
production readiness.

The source extends the previous nine-record experimental replay with nineteen
exact-root Windows XAXEDIT1 transactions. Every edit requires native verification;
the replay compares canonical bytes, file bytes and unchanged object identities.
The authoring carriers are native view/batch records, not a replacement source
language. Canonical `.xax` stores remain authoritative. Foreign orchestration and
transport-packing utilities are outside this repository.

Compiler calls poll stdin while waiting. A matching `notifications/cancelled`
notification stops the active child, confirms cleanup of its descendants and
suppresses the cancelled request's response. Ordinary queued requests are retained.
String IDs compare logical Unicode values; numeric IDs compare decimal values
without floating-point rounding. The number normalizer bounds nonzero exponents
at 8,388,608. This covers finite integer IDs within the message-size bound; larger
nonzero exponents are not a cancellation compatibility claim.

The input queue holds 1,048,576 bytes. Backpressure behind a larger ordinary frame
can delay a subsequent cancellation until the running compiler's deadline.
Compiler calls retain the 30-second deadline. stdin EOF does not cancel a request.
The server-owned kill-on-close job contains compiler descendants. Cleanup rechecks
job membership on opened process handles before termination; failure to confirm
cleanup exits the server instead of releasing live scratch. These are bounded
Windows prototype contracts, not real-time guarantees under host suspension.

[`xax_query` selectors](NATIVE_REFERENCE_QUERIES.md) expose the pinned compiler's
public kind/CID/reference record. The preview supports object and entity lookup,
dependencies, users, one-hop neighborhoods, root-bound cursors, source-kind filters
and pages of at most 64 rows. Empty arguments retain the legacy inventory result.
The inspection prefix is bounded at 4 MiB. `inventoryComplete` and `complete`
report truncation; there is no continuation beyond that prefix. Signatures,
operations, typed/effect facts, candidate comparisons and general semantic
evolution acceptance are not implemented.

Legacy progress metadata no longer opts a request into the modern protocol.
Protocol-specific metadata still receives modern validation; `server/discover`
still requires its modern metadata. Client identity and capability descriptions
do not grant authority. The installed Codex backend has exercised all eight tools
directly against the native executable, including read-only denials and full
text/structured equality. Desktop UI registration/loading is recorded separately
from executing tools through that UI.

The write/rename protections for configured compiler/store files and their
ancestors remain present. Writable workspace child-file aliases still permit
outside writes in controlled tests. This increment does not close that boundary.
Use the preview only with a trusted host and trusted workspace child files; the
required reusable upstream contract is in [NATIVE_HANDLE_CONTRACT.md](NATIVE_HANDLE_CONTRACT.md).
Another pathname recheck would not close the race.

The native multi-function fixture is
[`tests/protocol/semantic-paging/program.xax`](../tests/protocol/semantic-paging/program.xax).
Its three functions and two real calls were located through public queries and
compared with an independent reader. A real caller-body neighborhood required
four one-row pages. The program builds with the pinned Windows seed and exits 66.
This establishes the stated structural-reference exercise, not typed semantic
query acceptance.

Final-source acceptance completed on 2026-11-12. The [evidence index](evidence/native-control-20261112.json)
separates [historical milestone runs](evidence/native-control-historical-runtime-20261112.json),
[final-source runtime checks](evidence/native-control-runtime-20261112.json), and
[fresh extracted-package acceptance](evidence/native-control-package-20261112.json).
The package replayed 65 base, nine earlier-preview and nineteen control records,
verified every edit, rebuilt the fifteen native probes and final binaries twice,
and ran all final client gates with an empty parent PATH and bundled pinned seed.
Snapshot, executable and provenance identities match the canonical artifacts.

The final unfamiliar-program exercise checked three functions, two independently
confirmed calls, a four-page neighborhood and actual exit 66. Its final-server
inventory matched all 5,443 objects across 86 pages. These are generic-reference
observations; typed facts still come only from the independent fixture oracle.

[Active desktop tool calls](evidence/native-control-desktop-reconnect-20261112.json)
passed for all eight tools after the upstream checkout update and compiler-pin
relocation. Reads succeeded; mutation, build and execute respected read-only
denials; result handles remained unsupported. Text and structured results agree.
This is separate from the direct installed-client backend run and does not claim
writable desktop execution. The configured read-only preview remains available.

The source and default Gen3 deployment are unchanged. The remaining release
boundaries are in [REMAINING_MCP_TASKS.md](../REMAINING_MCP_TASKS.md).
Historical evidence is unchanged. `release_ready` and `full_mission_complete`
remain false. No new hosted CI result is claimed.
