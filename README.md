# XAX-MCP

An optional [Model Context Protocol](https://modelcontextprotocol.io) server that lets Codex, Claude Code/Desktop,
and other MCP clients **construct, verify, edit, build, and run real XAX programs**: an agent sends a typed
semantic-graph request, the [XAX](https://github.com/MrxSiN/XAX) toolchain verifies and compiles it to a native
Linux x86-64 executable, and the server runs that executable in an OS sandbox and returns a typed result with
provenance.

```text
MCP client ─► xax-mcp (thin adapter) ─► XAX construct / workspace / build (pinned upstream)
                                           └► static ELF ─► sandbox (namespaces + seccomp + rlimits) ─► result + provenance
```

XAX's invariant holds: **meaning is source.** Tool arguments are transport. A construction request becomes a
verified canonical store, and after that the store changes only through verified XAX transactions. The adapter
never computes a workload: results come from XAX-generated machine code.

## Status (0.1.0)

| Capability | Status |
|---|---|
| STDIO server, 8 tools, structured errors | EXECUTED: real SDK client and raw JSON-RPC tests |
| Construct a new program (`xax-construct-v1`), build, run, typed result | EXECUTED: randomized novel computation each test run |
| Query, verify/commit/rollback edits, stale-root rejection | EXECUTED: delegates to `xax_workspace` |
| Reopen and run previously verified stores (path A) | EXECUTED: exported stores and upstream `xb64` |
| Sandbox (user/mount/net namespaces, empty read-only root, seccomp, rlimits) | EXECUTED on Linux x86-64; fails closed elsewhere |
| Codex 0.161.0 / Claude Code 2.1.294 registration | STRUCTURAL: registered; Claude Code health check connected; no model-driven run recorded |
| MCP Inspector 2.10.1 CLI | EXECUTED: `tools/list`, `xax_capabilities` |
| Targets other than Linux x86-64, strings/JSON/CSV, files, network | UNIMPLEMENTED (reported by `xax_capabilities`) |
| Streamable HTTP transport | UNIMPLEMENTED (STDIO only) |

Labels follow [docs/EVIDENCE.md](docs/EVIDENCE.md). Measured latencies are in [docs/evidence](docs/evidence).

## Install

Requires Linux x86-64 for execution (construction and builds work wherever the XAX toolchain does), Python 3.11+,
and unprivileged user namespaces with seccomp (most distributions; Ubuntu 24.04 needs the AppArmor sysctl shown
in [docs/HOSTS.md](docs/HOSTS.md#troubleshooting)).

```bash
python3 -m venv ~/.venvs/xax-mcp
~/.venvs/xax-mcp/bin/pip install "xax-mcp @ git+https://github.com/MrxSiN/XAX-MCP@main"
~/.venvs/xax-mcp/bin/xax-mcp --check --allow-execute   # prints XAX pin, toolchain fingerprint, sandbox probe
```

This installs the official `mcp` SDK (2.3.x) and the XAX toolchain **pinned to commit
[`01ad841`](https://github.com/MrxSiN/XAX/commit/01ad841c76416fc741dd1386b12124904924c10d)**. The server refuses
to start against any other XAX build unless you set `XAX_MCP_ALLOW_UNTESTED_XAX=1`
([docs/COMPATIBILITY.md](docs/COMPATIBILITY.md)). XAX itself never depends on MCP.

## Register with an agent

```bash
claude mcp add --scope user xax -- ~/.venvs/xax-mcp/bin/xax-mcp --allow-execute    # Claude Code
codex mcp add xax -- ~/.venvs/xax-mcp/bin/xax-mcp --allow-execute                  # Codex
```

Claude Desktop, Codex timeouts, removal, MCP Inspector, and troubleshooting: [docs/HOSTS.md](docs/HOSTS.md).
A complete generic-client walkthrough: `python examples/generic_client.py`.

`--allow-execute` is the host owner's grant to run sandboxed native code. Without it the server can construct,
edit and build, but not execute. Tool arguments cannot grant rights.

## Tools

| Tool | Purpose |
|---|---|
| `xax_capabilities` | compiler identity and pin, target, operations, carrier types, I/O modes, rights, sandbox, maturity |
| `xax_workspace` | open a verified `.xax` store from a host-granted root; list, describe, close workspaces |
| `xax_query` | bounded, paginated queries: functions, nodes, operands, uses, types, effects, proofs, diff, repair |
| `xax_construct` | verify a new program from an `xax-construct-v1` carrier; returns a workspace |
| `xax_transaction` | verify, commit, or roll back typed edits against an exact generation and root |
| `xax_build` | build one package entry of the current root; returns an artifact handle, digests, and provenance |
| `xax_execute` | run an artifact in the sandbox with typed stdin, a declared stdout layout, and limits |
| `xax_result` | fetch bounded chunks of large outputs, stored diagnostics, or canonical store bytes |

The reference with a worked example is in [docs/TOOLS.md](docs/TOOLS.md). There are no per-operation tools
(`sum`, `sort`, ...): computations are XAX programs.

## What this is not

- It does not change how a hosted model works internally, and it cannot make a host choose XAX over the host's
  own Python or shell tools. A host must expose this server, the model must choose it, and the host owner can
  disable competing tools where the host allows it ([docs/HOSTS.md](docs/HOSTS.md#steering-agents-to-xax)). The
  optional [`agent-guidance/`](agent-guidance) files suggest that behaviour to agents but do not enforce it.
- It is not XAX-hosted. The adapter is Python, and the XAX compiler is the upstream bootstrap compiler (Python
  with XAX-hosted components). The sandbox executor is a short audited Python launcher. None of them contains
  workload logic ([docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#what-is-and-is-not-xax)).
- It is not a general code runner. There is no shell, no Python execution, and no fallback interpreter.

## Documentation

[Architecture](docs/ARCHITECTURE.md) · [Tools](docs/TOOLS.md) · [Security](docs/SECURITY.md) ·
[XAX contract](docs/XAX_CONTRACT.md) · [Compatibility](docs/COMPATIBILITY.md) · [Hosts](docs/HOSTS.md) ·
[Evidence](docs/EVIDENCE.md) · [Upstream proposals](docs/UPSTREAM_PROPOSALS.md) · [Decisions](docs/adr) ·
[Handoff](docs/HANDOFF.md)

## Development

```bash
pip install -e '.[test]'
XAX_SOURCE_DIR=/path/to/XAX python -m pytest -q        # XAX_SOURCE_DIR enables the upstream-store test
python scripts/record_evidence.py --out docs/evidence/new.json
```
