# ADR-0008: Per-user warm server for fast starts

**Status:** accepted (0.4.0)

**Context.** MCP hosts launch one STDIO server per client, and often per conversation. Every launch paid Python
imports (about 0.5 s) and the XAX component warm-up (2–7 s with a populated XAX image cache, about 42 s with an
empty one) before the first construct could run. That cost is upstream XAX work done identically in every
process. XAX-MCP cannot make it faster without changing XAX (see UPSTREAM_PROPOSALS.md, P6–P8), but it can
avoid repeating it.

**Decision.** `xax-mcp` is a small launcher. It connects to a per-user warm server (`xax_mcp.warm`) over a Unix
socket in a private 0700 directory, passes its own STDIN/STDOUT/STDERR descriptors (`SCM_RIGHTS`) and its command
line, and waits. The warm server has already imported the MCP SDK and loaded the XAX components; it checks the
peer's uid (`SO_PEERCRED`), forks, and the child serves MCP on the launcher's descriptors with a policy parsed
from the launcher's command line. The child acknowledges before anything else, so a launcher that gets no
acknowledgement keeps its descriptors and serves in-process.

- When no warm server is ready, the launch serves in-process (as before) and starts one in the background for
  later launches. `xax-mcp --prepare` starts it and waits, for use right after installation.
- The socket name is a hash of the xax-mcp sources, the installed XAX distribution's `RECORD`, the Python
  executable and version, the uid, and every `XAX_*` variable except the per-launch `XAX_MCP_LOG` and
  `XAX_MCP_REQUIRE_SANDBOX`. A changed install or configuration never reaches an old server.
- The warm server holds no rights and no client data, forks only while single-threaded, and exits after
  `XAX_MCP_WARM_IDLE_SECONDS` (default 900) without children. A child exits on STDIN EOF or when its launcher's
  connection closes (including `SIGKILL` of the launcher).
- Opt out with `--no-warm-server` or `XAX_MCP_WARM_SERVER=0`.

**Consequences.** With a prepared warm server, launch-to-initialize is about 0.1 s and launch to the first
construct+build+execute result about 0.2 s (was about 6.7 s at 0.3.1), independent of the XAX image cache.
The warm server stays resident (about 800 MB RSS at XAX `6c2df90`, most of it XAX's eagerly zeroed buffers; see
P6) until it has been idle for the timeout. Children share its pages copy-on-write. The children are not
descendants of the host process; their lifetime is tied to the launcher through the socket instead.
Considered and rejected: snapshotting XAX's in-memory state (it holds executable mappings and is not
serializable), and a long-lived shared server that multiplexes clients (it would share memory between clients).
