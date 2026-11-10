# Security — native 0.10 preview

Current gen3 [path validation](NATIVE_HOST_PATH_GUARD.md) checks configured compiler,
seed and work-directory components before each compiler-backed operation. Initial
rejection creates no lease/scratch files and returns `unsafe_host_path`. This
rejects configured junctions, not replacement races across check/use, hard links
or every workspace child-file substitution. Host directories still require trusted
ownership. A drive-qualified name is not proof of local storage. New negative
tests and remaining boundaries are recorded separately from historical evidence.

2026-11-10: [native memory probes](../tests/security/memory-commit/README.md)
observed 64 MiB allowed and 320 MiB denied in three confined trials each; both
allocations succeeded outside confinement. The unchanged 256 MiB job cap is thus
observed for this pattern. No pages are dereferenced. Gradual/physical pressure,
concurrent exhaustion and exhaustive crash/cleanup coverage remain open. The
server still returns raw u32 exits; it does not classify every trap as a tool
error. See [new evidence](evidence/native-memory-commit-20261110.json).

Binary stdin and argv are implemented with measured Windows acceptance, not full
release certification. [Execution contract](NATIVE_EXECUTION_INCREMENT.md) and
[current evidence](evidence/native-executor-input-argv-20261101.json) supersede only
the historical cases actually retested. XAX semantic verification is not permission
to run arbitrary native code.

Host configuration owns compiler/seed paths, private workspace, rights and installed
execution bounds. `xax_execute` accepts only optional `stdin_hex` and `args`.
Arguments exclude argv[0] and cannot grant access, choose an executable or compiler,
invoke a shell, override the environment, add filesystem/network grants or raise
quotas. Unknown/duplicate fields, invalid Unicode/NUL, malformed hex, wrong types
and exceeded bounds are rejected before compiler or artifact execution. Invalid
JSON/UTF-8 is rejected at framing. Authority denial precedes the execution path.

Public edits require a nonzero exact root. Native edit checks freshness, native
verify checks the staged candidate, and atomic publication follows only success.
Rejected/declined candidates cannot replace the current source. A native diagnostic
file must never be mistaken for a successful output.

A non-inheritable, share-mode-zero, delete-on-close lease owns compiler scratch for
the server lifetime. It excludes cooperating concurrent servers and releases on
process exit. Host directories and pinned tools must remain protected from hostile
same-user peers, links and replacement. The lease is not a defence against such peers.

The launcher uses an explicit `CreateProcessW` application path, checked attribute
list, capability-less AppContainer and job membership at creation. Membership is
checked before resume. The explicit inherited-handle list contains only a read-only
stdin duplicate and stdout/stderr write ends. Parent pipe ends, job, workspace
lease and configuration handles are excluded. Only the host-selected current build
is copied and launched; there is no unrestricted fallback.

The parent supplies OS-derived `LOCALAPPDATA` and `SystemRoot`. Windows rewrites
`LOCALAPPDATA` and adds container-local `TEMP`/`TMP`; an independent native observer
found exactly those four keys and no parent MCP configuration/PATH. AppContainer's
existing OS-owned storage remains part of its policy. No tool argument grants a path.
Synthetic tests observed token isolation, outside-file denial and blocked access to
a live loopback peer, with a successful native operator control. They are not an
exhaustive escape audit.

Current host caps are 4 MiB request, 256 KiB stdin, 64 arguments/8192 UTF-16 units,
1 MiB combined stdout/stderr, 5 seconds total user+kernel CPU, 10 seconds worker
wall time, 256 MiB job process commit and one active process. They are transport/
execution capabilities, not compiler limits. CPU is sampled with requested 5 ms
waits; observed accounting/scheduling overshoot reached 15.625 ms in the retained
final CPU test. No hard sampling-latency guarantee is claimed. Both output streams
are drained concurrently. Exhaustion, short transport, failed measurement or cleanup
cannot produce successful execution or successful truncated output.

The launcher waits for job cleanup and closes handles before publishing a versioned
resource record. The server checks exact capture lengths and removes transport
files before returning success. Timeout and launcher-termination cleanup were
executed; a locked-file cleanup failure is an explicit error. Setup/measurement
failures omit unknown observations instead of fabricating zeroes. Stdin consumption
and file offsets are not reported as semantic consumption.

Remaining security gates include memory-pressure/disk/handle exhaustion coverage,
actual WinAPI measurement-failure injection, independent escape review, current
desktop-host interoperability and complete asynchronous cancellation/crash handling.
The launcher-termination test covers a live contained child, not every creation or
publication crash window. Killing a server during synchronous compiler work can
leave its trusted compiler child running; during launcher work, immediate server-
death cancellation is not certified. Host/kernel crashes and interrupted publication
are not fully tested. No HTTP service, Linux fallback, typed entry ABI, registered
external-tool launcher or full CUM prepare is exposed.

External PowerShell/Node verification and semantic transport packing are operator
orchestration only. Every installed request-path component and synthetic worker is
canonical/native XAX. Historical evidence remains append-only.

[Hosted Windows CI](evidence/native-executor-ci-41314738774.json) also passed the
synthetic confinement, budget and live-worker launcher-termination gates. It does
not certify the untested security and crash scenarios listed above.
