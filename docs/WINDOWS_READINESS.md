# Windows readiness — 0.9.0, 2026-10-27

The supported native construction/build/confined-exit loop is **EXECUTED**. The full mission and general release
security gate remain **incomplete**. Earlier 0.8 findings are preserved in
[the historical audit](history/WINDOWS_READINESS_0_8.md); new evidence supersedes only the cases actually retested.

## Repaired and tested

| Previous finding | Current result |
|---|---|
| Invalid candidate published | Native verify precedes atomic publication; invalid-add fixture rejects, current source verifies unchanged and candidate is removed |
| Query/build ignored forbidden properties | Native argument guards return `invalid_request` before compiler work |
| No native construction route | `xax_construct` accepts native `XAXEDIT1` records; seven calls construct the new result-136 graph |
| No shipped usable Windows seed | Immutable XAX dependency `af376e8a8a1ac5635bcad459cb7063ef0b326430` publishes the exact tested native seed; application source rebuilds twice identically |
| Same-directory concurrency unsafe | Exclusive Windows lease denies a second process and releases automatically on owner crash |
| Function discovery required external compiler reads | MCP query returns root/bytes/first function from bounded native inspection |
| Zero expected root admitted | Public construction/transaction reject zero roots before edit |

The generic external client recorded **28 EXECUTED checks**, with no blocker status in that run. The workflow's
transport fixture contains 46 sequential exchanges plus five concurrency exchanges. CI replays all 46 canonical
application-source edits, verifies every candidate and performs native deterministic rebuilds. The timeout program
calls Windows `Sleep(60000)` from XAX and is terminated after approximately 10 seconds with timeout flag 1.

## Remaining gates

| Area | Current boundary |
|---|---|
| Modern MCP | Handshake protocol through 2025-11-25; 2026-07-28 stateless/per-request protocol unsupported |
| Semantic service | One private host workspace, root and first-function query; general graph queries, pagination and portable scoped handles absent |
| Runtime data | Construction constants and exit-u32 results; no general typed entry ABI, argv/effects input or result paging |
| Execution supervision | AppContainer/job prototype; no compiler-call cancellation, comprehensive output/disk/handle quota or escape certification |
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

[Windows CI run 40451172993](https://github.com/MrxSiN/XAX-MCP/actions/runs/40451172993) passed on clean windows-2022 at implementation commit a9d285d, including preview packaging. The implementation bytes and tested source remain unchanged by this evidence update.
