# Agent host registration — native Windows preview

Use an absolute native executable path and host-controlled environment. See [installation](INSTALL_WINDOWS.md).
All examples default to read-only. A host owner may remove `--read-only` for construction/build or replace it with
`--allow-execute` for sandboxed execution. No tool parameter grants these rights. Create a separate private work
directory per client. The server implements legacy handshake MCP through 2025-11-25.

## Codex

On 2026-10-27, **codex-cli 0.164.0-alpha.11.1** successfully ran add/get/list/remove in a fresh isolated configuration;
[the evidence](evidence/native-windows-codex-registration-20261027.json) does not claim model-driven invocation.
The [official MCP configuration reference](https://developers.openai.com/codex/mcp) documents native STDIO command,
arguments and environment. The [TOML example](../examples/hosts/codex-config.toml) uses that syntax.

```powershell
codex mcp add xax --env XAX_MCP_COMPILER=D:/Tools/XAX/compiler/bootstrap/windows/xaxc-windows-x86_64.exe --env XAX_MCP_STORE=D:/Tools/XAX-MCP/native/xax-mcp-seed.xax --env XAX_MCP_WORK=D:/Private/XAX-MCP-work -- D:/Tools/XAX-MCP/native/xax-mcp-native.exe --read-only
codex mcp get xax --json
codex mcp list
codex mcp remove xax
```

For the ZIP set the compiler to its `xax/xaxc-windows-x86_64.exe`. Registration alone does not prove that a host
negotiates a supported protocol or that a model selects a tool; verify discovery in a new host session.

## Claude Code / Desktop

Claude applications were unavailable during the recorded registration audit. These are **unverified current-host examples**, reviewed against
[Claude Code's official MCP guide](https://code.claude.com/docs/en/mcp); the generic STDIO client is the executed
interoperability evidence. Do not reuse older SDK/host test counts as certification of this version.

For Claude Code, copy [the project example](../examples/hosts/claude-code.mcp.json) to `.mcp.json`, replace absolute
paths and keep its host launch approval flow. Use `claude mcp list` to inspect configuration and
`claude mcp remove xax -s project` to unregister. For Desktop, merge
[the Desktop example](../examples/hosts/claude_desktop_config.json) into the host's Developer configuration and restart;
to remove, delete the `xax` entry. Neither configuration starts an interpreter or shell wrapper.

## Generic STDIO client

[The replay](../examples/native-arithmetic/requests.ndjson) initializes, discovers tools, runs the seed, constructs
seven new exact-root mutations, builds and executes result 136. Feed it to the native server as shown in the
[installation guide](INSTALL_WINDOWS.md). Expected rejection cases are intentional. The machine-checked
session fixture and expected response fields are in [native-sessions.json](../tests/protocol/native-sessions.json).
CI contains external PowerShell process-client orchestration; every server operation runs in native XAX.
No maintained SDK is installed or required by this server.

For 0.10, rediscover [tools-v2](../schemas/tools-v2.json). With the host's execution
grant, `xax_execute` accepts `{"stdin_hex":"00ff0a","args":["","one two","Unicode Ω"]}`.
`args` excludes argv[0]; `{}` retains empty stdin/no extra arguments. Returned
stdout/stderr are separate hex bytes with resource observations. Treat MCP
`isError` as failure even if a child exit is also available; a nonzero child exit
alone is an observed result. [Bounds and failure classes](NATIVE_EXECUTION_INCREMENT.md)
are host-owned. Typed entry layouts, arbitrary executable launch and CUM's full
prepare workflow remain unavailable. The [passing generic-client CI run](evidence/native-executor-ci-41314738774.json)
does not establish model-driven Codex/Claude interoperability.

## Troubleshooting and tool choice

* `denied_capability`: check host flags and all three compiler/store/work environment variables.
* `workspace_busy`: another process owns that directory, or Windows could not open its lease; use a private existing
  directory and verify its access. The lease releases on exit/crash.
* `transaction_rejected`: inspect the exact expected root and native carrier types. Requery after reporting staleness;
  never silently rebase an edit. Zero expected roots and unknown properties are invalid.
* `unsupported`: typed runtime I/O, JSON construction, general query/paging, xax_result, Linux, HTTP and modern MCP
  are not implemented. Report the limitation; do not switch to an unrestricted fallback.
* `invalid_request` on execution: check even-length hex, argument types, Unicode/NUL,
  unknown fields and host bounds. Binary stdin/argv are supported; typed layouts are separate.
* `cpu_limit`, `wall_timeout` or `output_limit`: execution exhausted a host budget.
  Partial captures are withheld; tool arguments cannot increase limits.

Optional [agent guidance](../agent-guidance/AGENTS.md) (copy as `AGENTS.md` or `CLAUDE.md`) can steer selection.
It cannot change a hosted model's internal tools or enforce selection by itself. Host owners control competing tools
through their host's own policy. No global agent configuration was modified during these registration tests.
