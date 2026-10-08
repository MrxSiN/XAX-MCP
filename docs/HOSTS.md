# Agent hosts: register, use, remove, troubleshoot

Install first ([README](../README.md#install)). In the examples, `XAX=~/.venvs/xax-mcp/bin/xax-mcp`. Use an
absolute path when the host does not inherit your shell `PATH`.

Launch flags (the host owner's policy):

| Flag | Effect |
|---|---|
| `--allow-execute` | grant sandboxed execution (otherwise construct/edit/build only) |
| `--read-only` / `--deny RIGHT` | withhold rights (`read`, `mutate`, `build`, `execute`) |
| `--store-root DIR` | allow opening `.xax` stores under DIR by relative name (repeatable) |
| `--wall-ms`, `--cpu-seconds`, `--memory-mb`, `--max-output-bytes`, `--max-request-bytes` | limits (tools can only lower them) |
| `--check` | print compatibility and sandbox status, then exit |

Environment variables: `XAX_MCP_LOG` (log level on stderr), `XAX_NATIVE_CACHE` (XAX's component image cache;
keep it warm for fast starts), `XAX_MCP_ALLOW_UNTESTED_XAX=1` (run against an untested XAX build).

## Claude Code (verified with 2.1.294)

```bash
claude mcp add --scope user xax -- "$XAX" --allow-execute      # or --scope project to write .mcp.json
claude mcp list                                                 # health check: "xax: … √ Connected"
claude mcp remove xax -s user
```

The project-scope file is [`examples/hosts/claude-code.mcp.json`](../examples/hosts/claude-code.mcp.json).
Claude Code asks you to approve project-scoped servers on first use.

## Claude Desktop

Add [`examples/hosts/claude_desktop_config.json`](../examples/hosts/claude_desktop_config.json) to
`claude_desktop_config.json` (Settings → Developer → Edit Config) with an absolute command path, then restart.
To remove it, delete the `xax` entry. Execution needs Linux x86-64, so on macOS and Windows the server
constructs and builds but reports `sandbox_unavailable` for execution. This host was not run in this
verification.

## Codex (verified with codex-cli 0.161.0)

```bash
codex mcp add xax -- "$XAX" --allow-execute
codex mcp list
codex mcp remove xax
```

Then add the timeouts from [`examples/hosts/codex-config.toml`](../examples/hosts/codex-config.toml) to the
`[mcp_servers.xax]` table in `~/.codex/config.toml`. The first XAX call after a server start waits for the XAX
component warm-up (about 3 s with a warm `XAX_NATIVE_CACHE`, about 50 s with an empty one). The cold case is
longer than Codex's default tool timeout.

## Generic clients

- Official SDK: `python examples/generic_client.py` (full loop).
- MCP Inspector: `npx @modelcontextprotocol/inspector "$XAX" --allow-execute` (UI), or
  `npx @modelcontextprotocol/inspector --cli "$XAX" --method tools/list`. Each CLI invocation starts a new
  server, so handles do not carry over between invocations.
- Any client: STDIO, newline-delimited JSON-RPC. Protocol versions 2024-11-05 … 2025-11-25 (handshake) and
  2026-07-28 are supported by the SDK.

## Steering agents to XAX

Registering the server makes XAX available. It does not make a model choose it. To steer agents:

- add [`agent-guidance/AGENTS.md`](../agent-guidance/AGENTS.md) or [`CLAUDE.md`](../agent-guidance/CLAUDE.md)
  to the project (advisory only);
- where the host supports it, the host owner can disable competing execution tools. In Claude Code, add
  `"Bash"` and other execution tools to `permissions.deny` in `.claude/settings.json`. In Codex, use a
  restrictive `sandbox_mode`/approval policy. Check your host's current documentation, because these settings
  change.

Hosted chat products' built-in Python tools are not affected by this server.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `sandbox_unavailable: … unshare: Operation not permitted` | unprivileged user namespaces are disabled. Ubuntu 23.10+: `sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0` (or an AppArmor profile for the Python binary); others: `sysctl kernel.unprivileged_userns_clone=1` |
| `sandbox_unavailable` on macOS/Windows | execution is Linux x86-64 only; construct/build still work |
| `denied_capability … execute` | add `--allow-execute` to the host config |
| server exits: `incompatible XAX toolchain` | install the pinned XAX (reinstall xax-mcp in a fresh venv) or see [COMPATIBILITY.md](COMPATIBILITY.md) |
| first call times out | raise the host tool timeout; keep `XAX_NATIVE_CACHE` writable so later starts are faster |
| `stale_root` | the workspace changed; re-query and resend the edit with the new generation and root |
| `stale_artifact` | rebuild, or pass `require_current: false` to run an older immutable build |
| nothing on stdout, logs on stderr | expected: stdout carries JSON-RPC only |

`xax-mcp --check --allow-execute` prints the XAX pin, the fingerprint, and the sandbox probe details.
