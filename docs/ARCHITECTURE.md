# Architecture

```text
Codex / Claude / any MCP client
  │  JSON-RPC over STDIO (mcp SDK 2.3, protocol 2025-11-25 handshake or 2026-07-28)
  ▼
server.py      tool list, JSON-schema validation, size cap, session keying, audit log (stderr), STDOUT isolation
  ▼
service.py     session-scoped opaque handles; maps tools to upstream calls; error classification; provenance
  ├─ xax_construct.construct ─────────► verified canonical build-snapshot store       (upstream XAX)
  ├─ xax_workspace.Workspace ─────────► bounded queries, verify/commit/rollback       (upstream XAX)
  ├─ xax_local_protocol.LocalMutationSession ─► snapshot-bound edit expansion          (upstream XAX)
  ├─ xax_build.build ─────────────────► static ELF64 + provenance object               (upstream XAX)
  └─ sandbox.py ──► _sandbox_exec.py (fixed launcher) ──► execve("/prog") in isolation
```

## Components

| File | Role | Holds workload logic? |
|---|---|---|
| `src/xax_mcp/server.py` | MCP transport adapter (low-level `mcp.server.lowlevel.Server`) | no |
| `src/xax_mcp/schemas.py` | versioned tool input schemas (`xax-mcp-tools-v1`) | no |
| `src/xax_mcp/service.py` | handle tables, upstream calls, errors, provenance | no |
| `src/xax_mcp/io_codec.py` | `xax-mcp-io-v1`: typed integers to/from little-endian stdin/stdout bytes | no (framing only) |
| `src/xax_mcp/policy.py` | rights and limits from launch flags; store-root path resolution | no |
| `src/xax_mcp/compat.py` | XAX pin and toolchain fingerprint check | no |
| `src/xax_mcp/sandbox.py` | probe, launch, wall time, output quotas, cancellation | no |
| `src/xax_mcp/_sandbox_exec.py` | single-purpose executor: namespaces, chroot, rlimits, seccomp, execve | no |

## Data flow of one computation

1. `xax_construct` receives an `xax-construct-v1` carrier (types, functions of blocks of typed nodes, package
   entries). After size and shape bounds checks, `xax_construct.construct` decodes it into canonical semantic
   objects and returns a verified store. The XAX verifier checks types, effects, linearity, memory facts, and so
   on. The store is opened as an upstream `Workspace` behind an opaque `ws_…` handle. The carrier is discarded.
2. `xax_query` and `xax_transaction` call the workspace's own bounded queries and its `verify`/`commit`/`rollback`.
   Typed mutations are rendered to the upstream local edit grammar (ADR-200) only after every token is validated.
   `LocalMutationSession` binds them to the queried generation, and `Workspace.commit` does the final atomic
   expected-root check.
3. `xax_build` reads the current root's build snapshot and calls `xax_build.build` for the selected package
   entry, deriving the build request for non-release entries exactly as upstream's `bench_r6_xb64._builds`
   does. Artifacts are cached per session by `(root, entry, toolchain fingerprint)`.
4. `xax_execute` re-hashes the artifact (BLAKE3), refuses it if the workspace has moved on (unless
   `require_current=false`), frames stdin, and runs the bytes through the sandbox. The stdout bytes are decoded
   only through the caller's declared layout.

## What is and is not XAX

| Part | Language | Notes |
|---|---|---|
| Program semantics, verification, code generation | XAX (upstream) | canonical store; the bootstrap compiler is Python with XAX-hosted hashing, decoding, typing and verifier components (`xax_native.AUTHORITY`, reported in provenance) |
| Executed computation | XAX-generated x86-64 machine code | static ELF; no libc, loader or runtime |
| MCP adapter, sandbox launcher, I/O framing | Python | bootstrap integration code, disclosed; no workload logic |
| Carrier JSON, edit grammar, function views | transport and tooling views | never authoritative source |

## Session model

The MCP SDK (2.3) builds a fresh session object per request, and on protocol 2026-07-28 a fresh `Connection`
too. Handle tables are therefore keyed on the transport's connection-scoped outbound channel
(`server.transport_key`). With STDIO this is the single client that launched the process. Handles are
`<kind>_<96 random bits>`, stored per session, never derived from content, and never accepted across sessions.
Tables are bounded (16 workspaces, 64 artifacts, 64 results, oldest evicted first).

## Startup and warm-up

On the first verification in a process, XAX loads its XAX-hosted compiler components (typing program, store
verifier, ...). On the reference host this took about 25 s with a populated `XAX_NATIVE_CACHE` and about 50 s
with an empty one. The server starts this warm-up in a background thread at launch, and tool calls that reach
XAX wait for it. Later calls take tens of milliseconds ([evidence](evidence)). This cost belongs to upstream
([UPSTREAM_PROPOSALS.md](UPSTREAM_PROPOSALS.md#p3-persist-verified-component-images)).
