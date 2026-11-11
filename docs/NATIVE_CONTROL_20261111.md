# Native control and reference-query preview

This is a tested experimental successor to Gen3, not the default deployment.
The canonical source and all artifact identities are in
[`native/candidates/20261111-control/checkpoints.json`](../native/candidates/20261111-control/checkpoints.json).
The compiler dependency stays pinned to [`native/xax-dependency.json`](../native/xax-dependency.json).
Windows compiler self-hosting and production readiness remain unestablished.

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

Work is paused. Final evidence export and clean-package acceptance are unfinished;
see [REMAINING_MCP_TASKS.md](../REMAINING_MCP_TASKS.md) for the exact test bindings
and remaining gates. Historical evidence remains unchanged. `release_ready` and
`full_mission_complete` remain false.
