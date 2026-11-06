# Windows readiness — 0.10.0, 2026-11-01

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

The historical 0.9 generic client recorded **28 EXECUTED checks**, with no blocker status in that run. The workflow's
transport fixture contains 46 sequential exchanges plus five concurrency exchanges. CI replays all 46 canonical
application-source base edits; the 0.10 increment adds 15 server and three launcher records, with verification
of every candidate and native deterministic rebuilds. The timeout program
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

[Windows CI run 40451172993](https://github.com/MrxSiN/XAX-MCP/actions/runs/40451172993) is historical 0.9 evidence.
The 0.10 workflow and local acceptance checks are updated; this task does not push,
publish a package, or claim a new GitHub-hosted CI run.
