# 0010 — Native Windows file contract and verified publication

Date: 2026-10-27. Status: implemented for the narrow 0.9 Windows preview.

Use the immutable upstream native Windows seed and xax-native-file-v1, keeping the compiler's generic seed/hash
contract upstream and all MCP application semantics here. Canonical application source is edited through native
XAXEDIT1 transactions; transport carries typed edits, never authoritative source. Historical JSON construction
requests are not required for a rebuild and remain unsupported inputs to xax_construct.

Stage native edit output, require native verify success, then publish atomically. Reject zero/stale roots. Hold a
non-inheritable exclusive Windows delete-on-close directory lease before compiler-backed work, for the process
lifetime. This excludes concurrent servers sharing fixed compiler scratch and releases on crash without a stale PID
file or another-language lock helper. A private host-owned directory remains required.

Queries expose bounded native inspection (root/bytes/first CID-ordered function) to prepare new typed edits through
MCP itself. Preserve root freshness rather than the old constant generation field. Do not claim general queries,
portable session handles, typed I/O or result paging. Current evidence and unsupported gates are explicit in the
readiness document. A complete release security claim remains deferred.

External preparation tooling, stored outside both repositories, encoded typed mutation envelopes and obtained semantic CID hashes from the native XAX hash program. It never wrote authoritative canonical stores, implemented verification or performed the workload. Native edit/verify alone produced and accepted canonical state. External PowerShell also provides test/CI transport and packaging. These dependencies are disclosed separately from the deployed XAX-only path.
