# Native JVM snapshot mutation preview

This separate preview extends the JVM build/execute preview with native edits of
unsigned, resolved `jvm-classfile-memory-v1` snapshots. Its dependency is
`native/jvm-mutation-dependency.json`; the source, artifacts and native replay are
bound by `native/candidates/20261113-jvm-mutation/checkpoints.json` and
`native/transactions/20261113-jvm-mutation/manifest.json`. The existing desktop
connection, default Gen3 dependency and false release-readiness flags stay in place.

Call `xax_capabilities` first. `xax_transaction` and `xax_construct` accept the
existing typed `XAXEDIT1` carrier with an exact, nonzero expected root. The pinned
native editor rebuilds reachable functions, modules, packages, requests and the
resolved snapshot. The server verifies the staged candidate natively before
publishing it. Subsequent query, build and execution use that current workspace.
The compiler may stage a type-invalid edit successfully; the separate verification
gate rejects it and preserves the published source.

The upstream increment follows its edge-copy staging fix and adds canonical
package/snapshot reference-list rebuilding. It supports multi-byte reference
indices and preserves resolver identity, external digests and the trust-policy
role. Replacements that collide within a canonical collection reject with
`WORKSPACE-REBUILD-DISTINCT`. Changing a signed package rejects; editing supplies
neither signing nor provenance authority. Recursion-group users,
signature/provenance rewriting and unresolved build requests remain outside this
profile. Generic query pages still expose references rather than typed operation
or effect facts.

The carrier retains its existing nine operation kinds. JVM acceptance exercises
all nine: constants, wrapping operations, reference and operand replacement,
insertion, deletion of an unused node, a valid result-type change, and edge
disconnection/reconnection. Independent checks compare canonical bytes and JVM
behavior. It also checks stale roots, invalid result types, live-node deletion,
incomplete edges, preconditions, range, unknown nodes, truncated records, zero
roots, read-only authority and forged client grants. The delimiter fixture changes
LF counting to semicolon counting in the canonical word-count program; the server
contains no word-count implementation or Java helper.

Use a fresh, trusted workspace and the exact compiler from the mutation manifest.
Set host-owned `XAX_MCP_COMPILER`, `XAX_MCP_STORE`, `XAX_MCP_WORK` and
`XAX_MCP_JAVA`, then launch
`native/candidates/20261113-jvm-mutation/xax-mcp-native.exe --allow-execute`.
Mutation and build rights are host controlled; `--read-only` and `--deny mutate`
continue to deny mutations. This document does not install or change a connection.

Java remains the separately installed, inventoried Microsoft Java 17 platform
runtime. The inherited AppContainer/job budgets, Windows-1252 argument bound,
raw child-exit behavior, temporary JAR read grant and normal cleanup apply.
Content integrity, atomic publication, full workspace-alias resistance, crash
ACL/cache cleanup, pressure/escape acceptance and wider security gates remain
open. This preview is not promoted to a default or a production-ready release.

Acceptance and exact identities are recorded in
`docs/evidence/native-jvm-mutation-20261113.json`.
