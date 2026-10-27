# XAX-MCP

A Windows x86-64 STDIO MCP server implemented as canonical XAX semantic programs. Version **0.9.0+native**.
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

The server stages native edits, verifies candidates before atomic publication, rejects stale or zero expected roots,
cleans rejected candidates and refuses forbidden query/build properties. An exclusive Windows directory lease
prevents concurrent processes from sharing compiler scratch and releases automatically on exit or crash.

**EXECUTED:** 28 local checks; CI orchestration replays 51 request/response exchanges, all 46 application-source
transactions, two byte-identical server rebuilds and a byte-identical sandbox rebuild. A native sleeping program
was terminated at approximately 10 seconds. These observations do not establish complete sandbox hardening.

[New graph and replay](examples/native-arithmetic/README.md) ·
[Recorded client evidence](docs/evidence/native-windows-x86_64-verified-construction-20261027.json) ·
[Native source and build](docs/NATIVE.md) · [Windows installation](docs/INSTALL_WINDOWS.md).

## Install and run

Use a repository checkout or the Windows preview ZIP produced by the
[native workflow](https://github.com/MrxSiN/XAX-MCP/actions/workflows/ci.yml).
The ZIP includes the native compiler seed; the source checkout pins XAX at
[`af376e8a8a1ac5635bcad459cb7063ef0b326430`](https://github.com/MrxSiN/XAX/tree/af376e8a8a1ac5635bcad459cb7063ef0b326430).
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

The [clean-package audit](docs/evidence/native-windows-clean-package-20261027.json) also passed all 28 checks after fresh extraction outside both checkouts, with the bundled native seed and an empty runtime PATH.

[Windows CI run 40451172993](https://github.com/MrxSiN/XAX-MCP/actions/runs/40451172993) passed from clean checkouts, including native rebuilds, 51 protocol exchanges, timeout enforcement and the downloadable preview ZIP.
