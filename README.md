# XAX-MCP

A native XAX STDIO MCP server for Windows x86-64. **Prototype; the full execution-plugin mission is not complete
and the release security gate is failing.** The executable version remains `0.8.0+native`.

The authoritative application source is the canonical semantic state in `native/*.xax`. XAX semantics,
verification, construction, editing and compilation belong to [XAX](https://github.com/MrxSiN/XAX).
JSON schemas, MCP messages and construction/edit carriers are transport data, never authoritative XAX source.

The deployed server, sandbox launcher and generated computation execute XAX machine code. They start no Python,
JavaScript, MCP SDK server or shell helper. Windows system DLL imports are operating-system interfaces. No new
implementation in another programming language is part of this repository.

## Windows result — 2026-10-27

A client initialized the actual server over STDIO, discovered all eight tools, and built and executed the seed
program with exit result `40`. Seven exact-root XAX semantic transactions then inserted three integer constants,
three arithmetic operations and a changed use into a new graph:

```text
((40 + 7) * 3) - 5  ->  136
```

Every intermediate store passed the native XAX verifier. The server built the final root
`236b15c2acc1ac10246b06ac5e23707cd3ffbb144507ca9bc52dd86286d6d8fb` and ran its actual executable through
the XAX Windows AppContainer/job-object launcher. It returned `exit_code: 136`, `flags: 0`, empty stdout/stderr,
and native build provenance. A repeated run also returned `136`. Replaying the first transaction after the edits
was rejected and retained the final root. This is new semantic graph construction by native transactions; it is
not evidence that the separate JSON carrier decoder works on this host, or that a general typed result ABI exists.

[Canonical example and replay](examples/native-arithmetic/README.md) ·
[Complete request/response evidence](docs/evidence/native-windows-x86_64-transaction-construction-20261027.json) ·
[Windows findings and remaining work](docs/WINDOWS_READINESS.md).

## Release blockers

* **Invalid candidates can be published.** A native transaction inserting an add with an effect-token operand
  returned success and replaced the current store. Independent native verification rejected that store with
  `XAX.STRUCT.OP_TYPE / GRAPH-OP-TYPE`. It was never executed. Verification must precede publication.
* `xax_query` and `xax_build` ignore some properties forbidden by their schemas. The tested `path` and `command`
  properties did not grant filesystem or shell access, but they should have been rejected.
* There is no native carrier decoder installed on this Windows host. `xax_construct` fails closed with
  `denied_capability`. The upstream decoder's canonical store and reproducible Windows executable are not committed.
* The recovered native compiler is a local prototype, identified separately from the server's embedded pin. It
  builds these small programs, but declines the current Windows compiler store itself. It is not a reproducible
  Windows self-hosting toolchain.
* Bounded semantic queries, session-scoped opaque handles, typed runtime I/O, result paging, cancellation during
  compiler calls and hardened sandbox coverage remain unfinished. Separate host work directories were tested;
  sharing one directory between clients is not session isolation.
* The latest [MCP specification is 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28).
  This server implements the older handshake protocol through `2025-11-25`; current-protocol support is open.

The full mission must remain incomplete until these gates pass. Historical successful tests do not override the
new negative results. Use read-only operation for evaluation; the mutation/execution configuration is experimental.

## Run

From a Windows checkout:

```powershell
& .\native\xax-mcp-native.exe --read-only
```

The process reads newline-delimited JSON-RPC from stdin and writes protocol messages to stdout. It requires no
language interpreter or SDK. Stop it by closing stdin. Supported launch flags are `--read-only`, `--allow-execute`,
`--deny RIGHT`, `--deny=RIGHT` and the compatibility no-op `--no-warm-server`; unknown flags exit with status 2.

The compiler-backed prototype additionally uses host-controlled `XAX_MCP_COMPILER`, `XAX_MCP_WORK` and
`XAX_MCP_STORE`; the carrier tool uses `XAX_MCP_CONSTRUCT`. Execution additionally requires `--allow-execute` and
`xax-mcp-sandbox.exe` beside the server. Tool arguments cannot grant these capabilities. Give every client its
own empty work directory. The work directory contains program state, artifacts and bounded execution captures.

## Tools

| Tool | Current behavior |
|---|---|
| `xax_capabilities` | Native identity, legacy protocol versions, launch rights and explicit maturity labels |
| `xax_workspace`, `xax_query` | Current store root and byte count only; full workspace/query operations are open |
| `xax_construct` | Host-granted native decoder prototype; unavailable on this recording host |
| `xax_transaction` | Native `XAXEDIT1` mutation; exact-root preconditions work, candidate verification before publication is defective |
| `xax_build` | Native `resolve` and `build`; returns artifact size and provenance |
| `xax_execute` | Rebuild and run current artifact in the native Windows sandbox; exit status and captured bytes only |
| `xax_result` | Unsupported; result handles are unfinished |

The schema transport snapshot is owned here at [schemas/tools-v1.json](schemas/tools-v1.json). It retains the
existing wire descriptions, including stale references to retired authors; changing a schema file alone does not
change an executable or fix validation.

## Dependency and reproduction

The unchanged server embeds XAX compiler commit `3e9b0c2b3f88d2193caae72a5fe8eefa83d1995b`, host contract r10.
Earlier certification is in [COMPATIBILITY.md](docs/COMPATIBILITY.md). Updating the XAX checkout to current `main`
does not change this pin or certify a different compiler.

The new example was constructed and compiled with a recovered XAX native Windows compiler, SHA-256
`ff0355c5bf148bc79cf463748a285c3f982b6c8e47faf8d2d25bd3571b2ad638`, source root
`2b8136a8e052ccefd88f31b5d906dc986a070f2ca6e370668b73b17783ed3d17`.
It is not shipped here or declared equivalent to the embedded pin. No Python bootstrap was run for this work.
Its historical bootstrap used Python, as the evidence discloses. Upstream still contains non-XAX bootstrap and
test implementations; a repository-wide XAX-only migration has not been completed.

For a compatible native compiler, the existing file commands are:

```text
xaxc verify <store> <diagnostic>
xaxc edit <store> <XAXEDIT1-record> <candidate>
xaxc resolve <request-store> <snapshot>
xaxc build <snapshot> <artifact> <provenance>
```

Always verify a candidate before accepting it. The native editor and MCP prototype currently do not provide that
guarantee together. A compiler exit 2 is a decline, not a validity or build-success claim.

## Checks

CI now depends only on this repository: it checks native artifact hashes, replays a fixed STDIO smoke fixture and
executes the committed arithmetic artifact under confinement. Git and PowerShell provide external CI orchestration;
no SDK, interpreter-based compiler, source emitter or non-XAX runtime helper is installed. These are smoke checks,
not a complete protocol, security, compiler or rebuild suite. The prior Python/SDK suite results remain historical;
that suite is no longer the current CI path.

The full native transaction experiment used an external PowerShell process client, stored outside both repositories.
It supplied typed mutation carriers, decoded the native inspection record and checked observed results; all program
mutation, verification, compilation and execution ran in native XAX executables. No external test client belongs
to the deployed request path.

## Documentation

[Windows readiness](docs/WINDOWS_READINESS.md) · [Native implementation/history](docs/NATIVE.md) ·
[Compatibility](docs/COMPATIBILITY.md) · [Handoff](docs/HANDOFF.md) · [Evidence](docs/EVIDENCE.md) ·
[Repository ownership decision](docs/adr/0009-canonical-programs-are-application-source.md).

Existing [host configuration examples](examples/hosts) are historical and were not re-certified against current
Codex or Claude versions in this audit. Making XAX tools available does not force agents to choose them or change
a hosted model's internal tools. The 0.5.x architecture/security/performance documents describe a retired adapter.
