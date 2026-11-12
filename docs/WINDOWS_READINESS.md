# Windows readiness — 0.10.0, 2026-11-01

2026-11-12: the separate [JVM snapshot preview](NATIVE_JVM_20261112.md) passed
native replay, deterministic host/JAR rebuilds, confined Java execution, direct
read-only backend calls and a fresh empty-PATH package. Its implementation is
`EXECUTED` and its exact [separate toolchain](../native/jvm-dependency.json) is
`TESTED`. Snapshot mutation, non-Windows-1252 arguments, crash ACL cleanup and
broader integrity/publication/security gates remain open. The default pin,
Gen3, active MCP connection and readiness flags are unchanged.

2026-11-12: the later [control preview](NATIVE_CONTROL_20261111.md) completed
[final-source, clean-package and read-only desktop acceptance](evidence/native-control-20261112.json).
Compiler cancellation, descendant cleanup, modern metadata and bounded public
reference pages passed within their documented limits. It remains experimental:
workspace child-file aliases still permit outside writes, semantic facts are
generic references, and pressure/crash/escape review remains incomplete. The
tables below describe the default Gen3 deployment; preview acceptance does not
promote it or change either readiness flag.

2026-11-11: a [resumed experimental candidate](NATIVE_CANDIDATE_20261111.md)
repairs capabilities framing and discovery and has complete pinned replay.
It remains unpromoted. Controlled workspace `edit.rec` hard-link aliases overwrite
outside disposable files; request cancellation and typed/paginated semantic APIs
remain absent. Default gen3 and both readiness flags remain unchanged.

2026-11-10: the [native configured-path guard](NATIVE_HOST_PATH_GUARD.md) rejects
configured junction/reparse components before compiler-backed operations, including
after lease acquisition. Native replay now covers 65 source records; the 92-client
baseline remains passing locally. Packaging includes source carriers and refuses
stale staging/output. TOCTOU, hard links, workspace child-file substitution,
cancellation and independent security review remain release blockers.

2026-11-10: [native memory tests](../tests/security/memory-commit/README.md)
observe allocation denial above the existing cap with positive controls. This
narrows one local coverage gap; broad pressure, independent escape review and
release acceptance remain open. The server/runtime is unchanged.

Binary stdin, explicit argv, separate byte streams, sampled total CPU and resource
observations are implemented and exercised with independent native synthetic probes.
See the [execution contract](NATIVE_EXECUTION_INCREMENT.md) and
[retained acceptance results](evidence/native-executor-input-argv-20261101.json).
Source-written, verified, compiled, executed and measured do not mean release-accepted.
Release readiness and full CUM prepare remain false.

The supported native construction/build/confined-exit loop is **EXECUTED**. The full mission and general release
security gate remain **incomplete**. Earlier 0.8 findings are in git history and `docs/evidence/`; new evidence
supersedes only the cases actually retested.

## Repaired and tested

| Previous finding | Current result |
|---|---|
| Invalid candidate published | Native verify precedes atomic publication; invalid-add fixture rejects, current source verifies unchanged and candidate is removed |
| Query/build ignored forbidden properties | Native argument guards return `invalid_request` before compiler work |
| No native construction route | `xax_construct` accepts native `XAXEDIT1` records; seven calls construct the new result-136 graph |
| No shipped usable Windows seed | The immutable XAX dependency in [`native/xax-dependency.json`](../native/xax-dependency.json) publishes the exact tested native seed; application source rebuilds twice identically |
| Same-directory concurrency unsafe | Exclusive Windows lease denies a second process and releases automatically on owner crash |
| Function discovery required external compiler reads | MCP query returns root/bytes/first function from bounded native inspection |
| Zero expected root admitted | Public construction/transaction reject zero roots before edit |
| No binary stdin or explicit argv | Optional stdin_hex/args, physical EOF and independent native argv checks pass |
| Wait-before-drain pipe deadlock | Simultaneous large stdin/stdout/stderr and exact stream checks pass |
| CPU configuration assumed sufficient | Total user+kernel CPU sampled and actually enforced; observed overshoot documented |
| Output truncation treated as success | Exact combined budget passes; one-byte-over and both floods return explicit errors |
| Unknown cleanup/measurement presented as success | Locked-file cleanup fails explicitly; simulated native launcher statuses omit unknown observations |

The 0.10 local and hosted workflows passed **92 client exchanges**, including the
46 sequential and five concurrency baseline exchanges. CI replays 46 canonical
application-source base edits, 15 server and three launcher increment records,
verifies every candidate, replays/rebuilds 15 native probes, and builds both
executors twice identically. The timeout program
calls Windows `Sleep(60000)` from XAX and is terminated after approximately 10 seconds with timeout flag 1.

## Remaining gates

| Area | Current boundary |
|---|---|
| Modern MCP | Handshake protocol through 2025-11-25; 2026-07-28 stateless/per-request protocol unsupported |
| Semantic service | One private host workspace, root and first-function query; general graph queries, pagination and portable scoped handles absent |
| Runtime data | Binary stdin/argv and separate streams work within host bounds; general typed entry ABI, result paging and registered external tools remain absent |
| Execution supervision | AppContainer/job prototype, CPU/wall/output enforcement measured; no compiler-call cancellation, exhaustive crash/resource-pressure coverage or escape certification |
| Host adoption | Generic STDIO client executed; Codex registration syntax checked locally; no current Claude installation available |
| Toolchain | Trusted historical native seed; application builds reproduce, compiler own-source build declines |
| Repository migration | No new non-XAX implementation; upstream legacy bootstrap/test code still exists and was not deleted |

These gaps must not be described as implemented. JSON `xax-construct-v1`, Linux, HTTP and `xax_result` have no native
fallback. Host-granted toolchain/work directories are trusted configuration, not client-selected paths.

Evidence: [client and semantic construction](evidence/native-windows-x86_64-verified-construction-20261027.json),
[wall timeout](evidence/native-windows-x86_64-timeout-20261027.json),
[artifact/dependency identities](../native/release-status.json), [source/build](NATIVE.md).

The protocol baseline is the official
[2025-11-25 STDIO specification](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports).
The separate [2026-07-28 version](https://modelcontextprotocol.io/specification/2026-07-28) remains open work.

[Windows CI run 41314738774](https://github.com/MrxSiN/XAX-MCP/actions/runs/41314738774)
passed for the pushed 0.10 implementation, including timeout, launcher termination
and preview artifact upload. [Run and downloaded evidence observations](evidence/native-executor-ci-41314738774.json)
record that scope. It does not close the remaining release gates above.
