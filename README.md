# XAX-MCP

Work paused on 2026-11-10. The [continuation prompt](CONTINUE_NATIVE_EVOLUTION.md)
records unfinished file-race, compiler-cancellation, semantic API and modern MCP
work. Archived experimental candidates are not the default gen3 deployment.

2026-11-10: the [native configured-path guard](docs/NATIVE_HOST_PATH_GUARD.md)
rejects configured reparse/ambiguous paths before compiler-backed work and
rechecks them on every call. Preview packaging now includes source replay
carriers and refuses existing staging/output. Release readiness remains false.

2026-11-10: [native commit-memory probes](tests/security/memory-commit/README.md)
observe a 320 MiB allocation denied by the 256 MiB job cap, with 64 MiB confined
and unconfined positive controls. This is local test evidence; the server,
dependency pin and preview release status are unchanged.

A Windows x86-64 STDIO MCP server implemented as canonical XAX semantic programs. Version **0.10.0+native**.
The supported construction/build/run loop works; this is a **preview**, and the full execution-plugin mission
remains incomplete. See [remaining gates](docs/WINDOWS_READINESS.md).

Meaning is source: `native/*.xax` contains the authoritative application programs. JSON schemas, MCP messages
and `XAXEDIT1` records are transport. XAX alone owns semantic editing, verification and compilation.
The deployed server, compiler, sandbox launcher and computation are native XAX executables using Windows system
DLLs. No interpreter, SDK server, shell wrapper or non-XAX runtime helper handles requests.

## What works

An external STDIO client discovered eight tools, queried the current root/function, constructed a new graph through
seven `xax_construct` calls, built it and ran its actual executable in a capability-less Windows AppContainer/job:

```text
((40 + 7) * 3) - 5 -> exit_code 136
```

`xax_execute` now accepts optional `stdin_hex` and `args` (excluding argv[0]),
preserves exact separate stdout/stderr bytes and reports measured resources. Native
probes cover binary EOF, difficult argv, concurrent streams, CPU/wall/output budgets
and confinement. See [the contract and CUM integration gaps](docs/NATIVE_EXECUTION_INCREMENT.md).

The server stages native edits, verifies candidates before atomic publication, rejects stale or zero expected roots,
cleans rejected candidates and refuses forbidden query/build properties. An exclusive Windows directory lease
prevents concurrent processes from sharing compiler scratch and releases automatically on exit or crash.

**EXECUTED:** retained native 0.10 acceptance and failure observations are in
[the increment evidence](docs/evidence/native-executor-input-argv-20261101.json).
The 0.10 Windows CI run passed 92 client exchanges, 64 verified source-transaction
replays, 15 native probes and two byte-identical builds of each executor. It also
checked wall timeout and live-worker cleanup after launcher termination. The
[recorded run and artifact identities](docs/evidence/native-executor-ci-41314738774.json)
remain separate from full release acceptance and complete sandbox hardening.

[New graph and replay](examples/native-arithmetic/README.md) ·
[Recorded client evidence](docs/evidence/native-windows-x86_64-verified-construction-20261027.json) ·
[Native source and build](docs/NATIVE.md) · [Windows installation](docs/INSTALL_WINDOWS.md).

## Install and run

Use a repository checkout or the Windows preview ZIP produced by the
[native workflow](https://github.com/MrxSiN/XAX-MCP/actions/workflows/ci.yml).
The ZIP includes the native compiler seed; the source checkout pins XAX at
the commit in [`native/xax-dependency.json`](native/xax-dependency.json).
Only this immutable native seed is certified for this preview. It historically used the upstream Python SDK for
bootstrap; no bootstrap interpreter was run for these changes. Its own-source build still declines, so this is
reproducible application building from a trusted seed, not a Windows compiler fixed point.

```powershell
& .\native\xax-mcp-native.exe --read-only
```

Compiler-backed tools need host-controlled `XAX_MCP_COMPILER`, `XAX_MCP_STORE` and a private, pre-created
`XAX_MCP_WORK`. Construction uses typed `XAXEDIT1` hexadecimal records through the same native compiler;
`XAX_MCP_CONSTRUCT` and a JSON decoder are unnecessary. Execution additionally requires `--allow-execute`
and `xax-mcp-sandbox.exe` beside the server. [Complete launch and rebuild commands](docs/INSTALL_WINDOWS.md).

## Supported scope and limits

* Windows x86-64; handshake MCP through `2025-11-25`. MCP `2026-07-28` and HTTP are unsupported.
* Construction constants, native integer graph edits, fixed target builds and observed unsigned process-exit results.
* One host-granted workspace; query returns root, bytes and first function CID from bounded native inspection.
* No general typed runtime inputs, general semantic query/pagination, result paging, portable opaque workspace handles,
  compiler-call cancellation or certified arbitrary native-code security. `xax_result` fails closed.
* Codex configuration syntax is checked with the installed CLI; current Claude apps were unavailable. The generic
  STDIO client is the executed interoperability proof. [Host setup and exact test scope](docs/HOSTS.md).

The server is an optional integration outside [XAX](https://github.com/MrxSiN/XAX). It cannot change a hosted
model's private inference engine or guarantee that an agent chooses XAX over other enabled tools.
No new non-XAX implementation has been added to either repository; upstream's historical bootstrap/test sources
remain outside this deployed path. [Compatibility](docs/COMPATIBILITY.md) · [Security](docs/SECURITY.md) ·
[Evidence](docs/EVIDENCE.md) · [Handoff](docs/HANDOFF.md) · [Release status](native/release-status.json).

The [0.10 clean-package check](docs/evidence/native-executor-clean-package-20261101.json)
passed after local extraction with the bundled native seed and an empty parent PATH.
[Windows CI run 41314738774](https://github.com/MrxSiN/XAX-MCP/actions/runs/41314738774)
also passed and uploaded the 0.10 preview ZIP. The extracted local package and the
hosted artifact have separately recorded identities; neither is a production release.
