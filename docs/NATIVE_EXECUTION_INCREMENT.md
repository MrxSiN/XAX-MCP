# Native binary stdin and argument vectors — 0.10.0

Implemented and executed locally on Windows x86-64, 2026-11-01. Canonical XAX
graphs implement the server and launcher. The pinned compiler is unchanged.
[Acceptance evidence](evidence/native-executor-input-argv-20261101.json) separates
source-written, verified, compiled, executed, measured and release-accepted states.
Release acceptance and full CUM prepare remain false.
The earlier incomplete [baseline audit](evidence/native-executor-input-audit-20261101.json)
is retained as historical evidence, not the state of this completed increment.

## CUM-facing contract

Grant execution at host startup with `--allow-execute`, then initialize MCP and call:

```json
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"xax_execute","arguments":{"stdin_hex":"00ff0a","args":["","one two","Unicode Ω"]}}}
```

`args` excludes argv[0]. The executor selects the current authorized build and
controls argv[0] (`prog.exe`). Omitted fields, `{}`, and explicit empty fields
mean empty stdin and no extra arguments. Arguments preserve empty strings,
Unicode, spaces, tabs, quotes and backslashes. They confer no path, executable,
environment, network or filesystem authority. There is no shell or executable
lookup through PATH.

`stdin_hex` decodes to exact bytes, including NUL and all 256 byte values. Each
execution gets physical EOF after those bytes. The inherited stdin is a seekable
regular-file handle, not a terminal or a pipe. No application-consumption or file
offset measurement is returned: kernel offsets/read-ahead would not establish
semantic bytes consumed. `stdin_bytes_supplied` describes the input supplied.

Malformed hex, wrong types, unknown or duplicate fields, embedded argument NUL,
invalid Unicode and exceeded argument/input bounds fail before compiler work or
artifact execution. Invalid JSON/UTF-8 fails at JSON-RPC framing instead.

## Host-owned capabilities

| Bound | Current value |
|---|---:|
| Request bytes before the LF delimiter | 4,194,304 bytes |
| Decoded stdin | 262,144 bytes |
| Extra arguments | 64 |
| Total decoded argument text | 8,192 UTF-16 code units |
| Internal UTF-16 command file | 65,534 bytes; the argument bound is tighter |
| Combined stdout + stderr | 1,048,576 bytes |
| Total user + kernel CPU | 50,000,000 units of 100 ns (5 seconds) |
| Worker wall budget | 10,000 ms |
| Job process memory / active processes | 256 MiB / 1 |

These are host transport/execution capabilities, not permanent XAX compiler limits.
Tool arguments cannot raise them. The host currently chooses fixed bounds by its
installed canonical executor; there are no per-call budget overrides. Output is
fully captured within the combined budget. Exceeded output is an explicit error;
partial captured data is withheld, never returned as successful truncated output.
All budget errors withhold partial captures; their stream fields count returned
bytes, not the total bytes the child attempted to produce.

## Results and failures

Successful transport preserves `ok`, `exit_code`, `duration_ms`, `flags`,
`stdout_bytes`, `stdout_hex`, `stderr_bytes` and `stderr_hex`. It adds
`user_cpu_100ns`, `kernel_cpu_100ns`, `peak_memory_bytes` and
`stdin_bytes_supplied`. A nonzero child exit remains an observed child result,
including the existing seed exit 40. It is distinct from launcher failure.

Failures set MCP `isError: true` and `ok: false`. Execution error strings distinguish
`launcher_setup_failed`, `wall_timeout`, `cpu_limit`, `output_limit`,
`incomplete_transport`, `measurement_failed` and `cleanup_failed`. Invalid tool
arguments retain the existing `error.code: invalid_request` shape. Unknown resource
observations are omitted on setup/measurement failures. A measured zero is allowed
only after the corresponding native measurement API succeeded.

Flags retain bit 0 for wall timeout and bit 2 for output exhaustion; bit 3 means
total CPU exhaustion. Exhaustion now fails the tool call. `duration_ms` measures
supervision from immediately before resume through completion/termination and
measurement; it excludes compilation, setup and capture-file publication.
`peak_memory_bytes` is the job's `PeakProcessMemoryUsed` (peak process commit),
not working set. CPU is the worker's actual `GetProcessTimes` user/kernel accounting.

The launcher samples total CPU and wall time between concurrent pipe drains and
requests 5 ms waits. This is not a hard 5 ms response guarantee. A final CPU run
observed 5.015625 CPU seconds: 15.625 ms overshoot. Scheduling/accounting and cleanup
can add delay; CPU time is not wall time. Configuring a job CPU limit alone is not
treated as enforcement evidence.

## Native implementation and confinement

The server validates inputs, quotes each argument independently using the Windows
backslash/quote rules, and prepares private binary stdin and UTF-16 argv files.
The launcher opens stdin with delete-on-close, duplicates a read-only inheritable
handle, closes the original, and checks the exact prepared command file. It passes
only stdin, stdout-write and stderr-write in `PROC_THREAD_ATTRIBUTE_HANDLE_LIST`.
The workspace lease, job, parent pipe ends and configuration handles are excluded.

`CreateProcessW` receives an explicit artifact path, checked attribute list,
capability-less AppContainer, explicit environment, and the job handle through
`PROC_THREAD_ATTRIBUTE_JOB_LIST`. Membership is checked before resume. There is
no launch-then-assign gap. The job retains kill-on-close and one-process/memory
limits. Both output pipes are drained while the worker runs, with a combined byte
counter and no unbounded spool. Capture files and their 64-byte versioned resource
record are checked exactly, then removed before a successful response.

The supplied environment contains only OS-derived `LOCALAPPDATA` and `SystemRoot`.
Windows rewrites `LOCALAPPDATA` and injects container-local `TEMP`/`TMP`; the native
observer found exactly those four keys. Parent `XAX_MCP_*` values and PATH were
absent. Container-owned OS storage is part of AppContainer's existing policy; this
increment grants no additional paths. The native isolation probe observed an
AppContainer token, outside-file access denial, and no connection to a live
loopback peer that its native operator control reached. Initial assumptions that
the copied executable could be reopened/written by the child were false; no grant
was added to make that assertion pass.

## Source, transactions and verification

Authoritative sources are `native/xax-mcp-native-gen2.xax` and
`native/xax-mcp-sandbox-gen1.xax`. The [increment manifest](../native/transactions/20261101/manifest.json)
replays exact-root transactions after the historical 46-record server manifest.
Every candidate is natively verified. Shared unchanged objects retain their CIDs.
Review JSON is diagnostic semantic data; it is neither textual XAX nor an accepted
construction language.

The original sandbox is a resolved snapshot, whose direct edit is unsupported.
Two native transactions place its existing closure in its existing editable request
envelope and reproduce the original launcher byte-for-byte before the execution
change. Native editor supplied-object batches are at most 256; metadata imports
use verified intermediate roots within that bound. No XAX/BBC change or foreign
runtime helper was introduced. PowerShell/Node commands used for packing semantic
transport and external verification are operator orchestration, not installed code.

Acceptance covers binary EOF, all bytes, large simultaneous streams, independent
argv observation, exact/over-limit input/arguments/output/requests, malformed input,
authority denial, actual CPU and wall behavior, live-peer confinement, environment,
locked-file cleanup failure, launcher termination, stale roots, candidate rejection,
replay and deterministic builds. Failed candidates and mistaken test expectations
remain in the evidence. Status-only native fixtures exercise launcher failure
classification; they do not claim forced WinAPI measurement-failure coverage.

## Remaining gaps

No CUM transformations, typed entry/data layouts, registered external executables,
BBC tool registry, unrestricted launcher or full prepare workflow is implemented.
CUM payloads exceeding these bounds need a separately authorized capability change.
Cancellation during synchronous compiler work, server death during compiler/launcher
calls, host/kernel crashes, interrupted output publication and every process-creation
crash window are not fully certified. An idle/crashed workspace lease test does not
prove in-flight compiler orphan cleanup. Memory-pressure, disk/handle exhaustion,
escape review and current desktop-host interoperability remain release gates.
