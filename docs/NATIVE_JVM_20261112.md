# JVM snapshot build and execution preview — 2026-11-12

The explicit JVM preview builds authorized canonical XAX snapshots into executable
JARs with the native XAX compiler and runs those JARs through a native Windows
AppContainer supervisor. The server, launcher and application sources are XAX.
The JVM is a required host platform runtime. No Java source helper, Python
interpreter, `javac`, reference backend or foreign adapter runs on the MCP request
path. The independent acceptance utilities stay outside this repository.

See the [acceptance index](evidence/native-jvm-20261112.json),
[source identities](../native/candidates/20261112-jvm/checkpoints.json),
[exact-root replay](../native/transactions/20261112-jvm/manifest.json),
[tool schema](../schemas/tools-v5.json), and separate
[tested compiler/runtime dependency](../native/jvm-dependency.json).
The implementation status is **EXECUTED** and toolchain status is **TESTED** for
this bounded profile. This does not select it as the default deployment or change
the user's existing MCP connection.

## Supported profile

The target is `jvm`, profile `jvm-classfile-memory-v1`, artifact
`JVM_EXECUTABLE_JAR` (kind 6), classfile major 61. The tested runtime is Microsoft
OpenJDK 17.0.20.1+1-LTS on Windows x86-64, system ANSI code page 1252. Its
[runtime inventory](evidence/native-jvm-runtime-inventory-20261112.json) records
the launcher, modules, native runtime libraries and configuration. Other JDK
versions and code pages are outside this acceptance.

The newer immutable native compiler is pinned only for this preview. The
default dependency, default CI job, Gen3 sources and binaries retain their prior
pin and identities. Upstream records a native compiler self-build; this local
application acceptance does not reproduce that bootstrap.

Build accepts an already resolved snapshot. Native Win32 byte copying stages the
snapshot; the native compiler's build operation verifies the complete graph and
emits the JAR and provenance. The adapter does not parse canonical state.
Unresolved build requests decline. Native snapshot mutation currently declines
with `XAX.WORKSPACE.TOPOLOGY` / `WORKSPACE-SUPPORTED-USER`; no changed snapshot is
published. Generic request-graph editing in the shared protocol does not establish
JVM snapshot construction or mutation. Two byte-exact upstream XAX word-count
snapshots are retained as [fixtures](../tests/jvm/manifest.json), with distinct
ASCII/high-byte word behavior and independently checked outputs.

## Explicit host launch

Use a fresh trusted work directory for each process. Set absolute host-controlled
`XAX_MCP_COMPILER`, `XAX_MCP_STORE`, `XAX_MCP_WORK` and `XAX_MCP_JAVA` paths; select
the compiler in the JVM dependency manifest and the tested Java executable.
Run `native/candidates/20261112-jvm/xax-mcp-native.exe --allow-execute --deny mutate`.
The matching `xax-mcp-sandbox.exe` must remain beside the server. Java is installed
separately and is not bundled. `server-runtime.xax` is a construction checkpoint
with historical Android metadata; use the final `server.xax`, snapshot and matching
binaries from the checkpoint manifest.

The fixed launch command uses `-Xverify:all`, a 16 MiB initial/64 MiB maximum heap,
1 MiB thread stack, bounded class/metaspace/code caches, serial GC, one active
processor, disabled perf data and attach mechanism, followed by `-jar` and the
absolute copied artifact path. Clients cannot set Java paths, JVM options,
classpath, environment, agents or budgets. Option-like strings after the fixed
JAR argument, including `@file` and `-version`, remain application arguments on
the tested runtime. Parent Java option variables, classpath, PATH and JAVA_HOME
are not inherited. The child receives the supervisor's minimal Windows environment.

Java 17's Windows launcher loses arguments outside Windows-1252 on this host.
The native launcher therefore rejects a non-1252 host or command line requiring
lossy conversion before starting Java. Empty strings, Windows-1252 text, quoting,
backslashes and newlines were independently observed at Java `main`. Limits are
64 arguments and 8,192 UTF-16 units per argument, within the existing command-line
bound. The XAX memory-profile entry does not expose a startup argument reader;
argument delivery at Java `main` does not claim that missing XAX API. Binary stdin
is byte-exact and has no text encoding restriction, including UTF-8 emoji.

## Confinement, limits and cleanup

The native supervisor launches Java suspended with its existing explicit handle
list, zero-capability AppContainer and launch-time job membership. It supplies
binary stdin and physical EOF, concurrently drains separate stdout/stderr, and
measures actual CPU, wall time and peak process commit. Fixed host limits are
5 seconds total user/kernel CPU, 10 seconds wall time, 256 MiB process commit,
one active process and 1 MiB combined output. Heap size and job commit are
different limits. Budget exhaustion withholds partial streams. Java exceptions
and heap exhaustion remain raw process exits/stderr; they are not classified as
native traps or job-memory exhaustion. Negative exits use the existing raw u32
Windows exit representation.

Java needs read access to the staged JAR. Native ACL operations temporarily grant
read/execute access on that invocation's copied artifact, then restore its prior
DACL during normal cleanup. The JDK installation's ACLs are unchanged. Traffic
files are removed after normal MCP execution, but the existing private artifact
cache at `exec/sandbox-run/prog.exe` remains; its extension is immaterial to Java.
Supervisor death kills the observed JVM through the job and publishes no successful
result. Forced termination can leave the AppContainer read ACE on that owned
cached JAR. Full crash ACL/cache cleanup remains open.

Independent temporary Java probes checked exact arguments, environment, raw exits,
CPU/wall/output limits, heap exhaustion and denied outside file access, live
loopback networking and child-process creation, each with an unconfined positive
control. They are test oracles, never shipped application code or runtime helpers.
The MCP workload itself is generated from the two retained canonical XAX fixtures.

## Remaining boundaries

This preview branches from the accepted Android server and does not incorporate
the separate inspection-output pin preview. It retains the trusted-host workspace
boundary. Content authentication, reusable compiler handle/identity transport,
atomic publication, same-user aliases, DOS remapping, exhaustive crash/pressure
coverage and independent escape review remain open under the
[required upstream contract](NATIVE_HANDLE_CONTRACT.md). Default Gen3, candidate
promotion, `release_ready` and `full_mission_complete` remain unchanged/false.

The separate JVM CI job pins the newer compiler and checks native replay and
deterministic host/JAR rebuilds. It makes no hosted Java execution claim. Local
execution is bound to the inventoried runtime; hosted results and promotion are
separate gates. Continue content integrity, atomic publication and broader
security only after this JVM increment's acceptance is recorded.
