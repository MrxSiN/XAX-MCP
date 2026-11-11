# Resumed native candidate — 2026-11-11

This is an **experimental checkpoint, not the deployed server**. The default source,
snapshot, executable, workflow and dependency pin still select gen3. Both
`release_ready` and `full_mission_complete` remain false. The retained 20261110
capabilities candidate still records its original failure; it was not overwritten.

The final experimental source and artifact identities are in
[`checkpoints.json`](../native/candidates/20261111/checkpoints.json). Its source is
`native/candidates/20261111/server-modern-mcp.xax`; its root is
`38724fe570dcddb9bb82c5bf2bd49aca468445a38ab2d0e5d19ed4599559c10f`.
Use these identities to distinguish it from the default `0.10.0+native` preview.

## Changes and authorship

The old capabilities edit changed constants shared by several native stores. A
new desired literal chunk could therefore corrupt another chunk using that same
constant. The repair supplies a separate native constant for each changed use,
preserves the original offsets and store widths, appends the added tail, and
returns the exact new length. Independent carrier inspection checked every byte
offset, width and returned length. Full runtime text/structured equality and a
comparison against the prior capabilities body found only the two intended changes:
the modern-protocol maturity label and the versions array.

A later full mixed-client run exposed a separate CRLF/state failure: a malformed
transaction followed by a tool-argument rejection could return a legacy-shaped
result despite valid modern metadata. Native trailing-JSON-whitespace normalization
before metadata validation repairs that sequence. The regression covers 768 modern
requests across 16 padding lengths, eight whitespace forms and both fresh and
legacy-initialized processes. The [first package record](evidence/native-resumed-package-first-20261111.json)
predates this repair and remains scoped to its eight-record source. The final
checkpoint includes a ninth exact-root transaction.

Discovery now reports `2026-07-28`, `2024-11-05`, `2025-03-26`, `2025-06-18` and
`2025-11-25`. Each legacy version was independently negotiated through `initialize`;
modern requests still require per-request `_meta`. The unsupported-modern-version
error lists the modern metadata version it accepts; legacy versions require the
handshake. Discovery identity now agrees with the existing server name and
`0.10.0+native` version. Discovery and modern `tools/list` include `ttlMs: 0` and
`cacheScope: "private"`. The request-local framing/cache flag resets on every call;
the original packed host-rights byte is preserved.

These fields follow the current normative [versioning](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/basic/versioning.mdx),
[discovery](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/server/discover.mdx)
and [caching](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/server/utilities/caching.mdx)
requirements. The exact official schema digest and independent validation results
are retained in [schema evidence](evidence/native-modern-schema-20261111.json).
No modern desktop-client interoperability follows from schema validation.

Canonical stores were authored with the identified Linux native seed under WSL.
All new construction uses native view/batch transactions with exact roots and
mandatory verification. External transport packing copies immutable native objects;
it does not construct a canonical graph. The unchanged pinned Windows seed replays
the nine-record chain from gen3, verifies every result and reproduces every source
byte, preserving unchanged CIDs. The [manifest](../native/transactions/20261111-capabilities/manifest.json)
records every base/result root, source, carrier and hash. The capabilities literals
use two smaller transactions because their combined Windows transport was rejected
with `EDIT-RECORD-COUNT`. No toolchain upgrade was used to bypass that rejection.

## Executed checks

[New candidate evidence](evidence/native-resumed-candidate-20261111.json) records:

- The unchanged 65-record source chain, 15 native probe rebuilds and two identical
  builds of each default executor; nine additional pinned candidate records and
  two identical candidate executable/provenance builds.
- The existing 92-exchange native baseline, including construction, invalid/stale
  rejection, binary execution, confinement, lease contention and crash recovery.
- The retained 25-exchange metadata/escape/legacy-mixing exercise, plus 96 further
  exchanges covering all eight tools, native mutation/build/execution, 18 denied
  authority attempts, four legacy versions, malformed/oversized input recovery,
  silent notifications and cross-request client-identity/capability escalation.
- A second full 92-exchange run using mixed legacy initialization and modern tool
  requests, with 68 complete modern responses, including native output/CPU/wall
  budgets and large binary streams; all 67 tool text/structured bodies agree.
- [769 whitespace/state exchanges](evidence/native-trailing-whitespace-20261111.json):
  768 complete modern results and one legacy initialization.
- Full text/structured equality, 162 official-schema request/response validations,
  160 native JSON helper cases and an independent comparison of all 12 seed
  objects, kind tags and reference edges.
- A 30-second compiler deadline, continued responsiveness afterward, compiler
  termination on server death, seven OS-enforced configured-object replacement
  denials and exit-time handle release.

The [fresh-package evidence](evidence/native-resumed-package-20261111.json) separately
identifies the tested archive and extraction. Historical gen3 package evidence
does not count as acceptance of this candidate.

## Confirmed open boundary

[Four controlled alias trials](evidence/native-candidate-aliases-20261111.json)
reject pre-existing hard links on configured compiler/store files and preserve both
configured and current source bytes. However, a pre-existing hard link at
`<work>/edit.rec`, and a concurrently installed link at that name, allow a query
to overwrite a disposable file outside work. A successful query did not imply
that the outside-write boundary held. These are retained failures, not passed
security tests. Root/source preservation does not make the outside write safe.

The host must currently trust every process able to modify workspace child names
and the drive namespace. File/ancestor handle pins and another pathname check do
not establish complete TOCTOU protection. The required reusable upstream
[handle/identity contract](NATIVE_HANDLE_CONTRACT.md) is specified without changing
the upstream checkout or silently repinning deployment.

## Remaining acceptance

Request-level cancellation is absent: the compiler wait does not read matching
`notifications/cancelled`. Deadline/server-death handling is separate. Typed
selectors, entity lookup, bounded neighborhoods, root-bound continuation/paging,
result budgets and candidate comparisons remain absent; query arguments still
accept `{}`. The inspection record supplies kinds/CIDs/reference arrays, not
function signatures, blocks, operations or typed/effect facts. The smallest
upstream extension is documented in the handle contract; no second canonical
parser was added. P1 unfamiliar multi-function/call/neighborhood acceptance,
desktop clients, exhaustive crash/pressure/escape review and full CUM prepare
remain open. This checkpoint is not promoted.
