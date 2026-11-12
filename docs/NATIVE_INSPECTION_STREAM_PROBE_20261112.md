# Inspection stream feasibility — 2026-11-12

After completing the JVM target acceptance, external transport probes tested an
inspection-only route around writable workspace output files. Both the default
immutable compiler and the separately tested JVM compiler accept a Windows named
pipe as the output of their existing native `inspect` command. This requires no
compiler implementation change or canonical parsing in an adapter.

This is **EXECUTED transport feasibility**, not an implemented MCP feature or a
closed security gate. No MCP server was started by these probes and no application
source changed. The PowerShell/.NET orchestration remains outside the repository;
the inspection producer itself was the exact native XAX compiler. See the
[retained results](evidence/native-inspection-stream-probe-20261112.json).

Four positive cases used the two compiler seeds against the small canonical seed
and final JVM server source. Streams of 1,128 and 1,403,992 bytes matched each
compiler's regular-file output exactly, reached physical EOF, and reported the
expected native child PID through `GetNamedPipeClientProcessId`. The consumer held
its process object while checking identity. The endpoint used first-instance
creation and a single instance with a fresh name.

Eight negative controls rejected an existing server endpoint, distinguished five
controlled foreign client connections from the native producer before accepting
any bytes, and exercised producer death and consumer abort after 64 bytes. Native
producer death returned nonzero and physical EOF with incomplete output. Consumer
abort also produced a native failure. EOF alone therefore cannot establish a
complete successful inspection. The controlled impostor client was the external
test process, not an independent escape reviewer or another MCP user.

An eventual native implementation still needs all of the following:

- Create an exclusive local endpoint, explicitly reject remote clients, bind its
  producer to the held compiler process identity, and refuse unexpected clients.
- Drain concurrently with compiler/job supervision using bounded asynchronous
  reads. Integrate the existing cancellation, deadline, queue and descendant
  cleanup behavior. The external probe's whole-stream memory copy is not a
  production buffering design.
- Accept only a complete bounded native record, physical EOF and successful
  producer/measurement/cleanup outcomes. Cancellation and read failures must
  withhold all results even if a producer reports success.
- Retain the input file/volume/root identity contract; a protected output stream
  does not prevent source-path or DOS namespace substitution.
- Verify native integration with adversarial timing, oversized/malformed streams,
  impostor and remote clients, crashes, handle pressure and independent review.

This option is limited to inspection transport. Editing, resolve/build artifacts,
candidate verification and publication still require the reusable upstream
[handle/identity and atomic publication contract](NATIVE_HANDLE_CONTRACT.md).
None of the JVM, Android or inspection-pin server binaries has changed, and their
recorded trusted-host workspace boundaries remain in force.
