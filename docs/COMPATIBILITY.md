# Compatibility matrix

| xax-mcp | XAX commit | XAX toolchain fingerprint (sha256) | mcp SDK | Python | OS / arch | Result |
|---|---|---|---|---|---|---|
| 0.3.0 | `b0ec772a954a6b7932c6e3c1d44794c036a9b7ab` (2026-10-08; host contract `xax-host-contract-v1` r2) | `636b268c755e16e5cba71022ac1847f5dc0c96471e4a81b49853f035f13224ee` | 2.3.0 | 3.13.16, 3.11.17 | Linux 6.18 x86-64 | 41/41 tests pass on both, sandbox required |
| 0.2.0 | `f38cbeea2b90e9b6a580417ce7efaa7d3d75a183` (2026-10-08; host contract `xax-host-contract-v1` r1) | `cdf3e5868810fb47884391cbe60fe7c79589ca8c0d14979644223f1dce012a7b` | 2.3.0 | 3.13.16, 3.11.17 | Linux 6.18 x86-64 | 38/38 tests pass on both, sandbox required |
| 0.1.0 | `01ad841c76416fc741dd1386b12124904924c10d` (2026-10-08) | `2d5b1f3be0c6c40f394a1e6a109239d38e2b9abc2634b02fbb21cffae172392f` | 2.3.0 | 3.13.16, 3.11.17 | Linux 6.18 x86-64 | 36/36 tests pass on both, sandbox required |

Declared support for 0.3.0: exactly `b0ec772` (XAX `main`), and XAX must provide `xax-host-contract-v1` at
revision ≥ 2, because carriers now use byte-view widening (ADR-231). Earlier XAX commits are `incompatible`.

Declared support for 0.2.0 (historical): exactly `f38cbee`, and XAX must provide `xax-host-contract-v1` at revision ≥ 1
(earlier commits, including 0.1.0's `01ad841`, are `incompatible`). `f38cbee` is reachable from XAX
`main` through merge commit `5c9ba68`.

Declared support for 0.1.0 (historical): exactly the `01ad841` commit above (the `xax-compiler` version string is `0.1.0` at every
upstream commit, so it identifies nothing). `mcp>=2.3.0,<2.4`. Python ≥ 3.11 is declared; 3.11 and 3.13 were tested,
and CI runs both.

The fingerprint is a sha256 over the name and content hash of every Python module and bootstrap `.xax` store
in the installed `xax-compiler` distribution (`compat.toolchain_fingerprint`). It is the same whether XAX was
installed from git or from a local checkout of that commit (checked with a clean virtual environment installing
`xax-mcp` from GitHub).

## Behaviour on mismatch

- Missing upstream interface → `incompatible`, and the server refuses to start with the missing names.
- Unknown fingerprint → `untested`, and the server refuses to start unless `XAX_MCP_ALLOW_UNTESTED_XAX=1`.
  `xax_capabilities` then reports `status: untested`, and provenance carries the actual fingerprint.

## Hosts

| Host | Version | Verified |
|---|---|---|
| Official MCP Python SDK client (STDIO) | mcp 2.3.0 | full loop, two clients, transactions (tests/test_e2e_stdio.py) |
| Raw JSON-RPC (handshake 2025-11-25) | — | initialize, tools/list, tools/call, stdout purity |
| MCP Inspector CLI | 2.10.1 | `tools/list`, `tools/call xax_capabilities` |
| Claude Code | 2.1.294 | `claude mcp add` (user and project scope), `claude mcp list` health check: connected |
| Codex CLI | 0.161.0 | `codex mcp add/list/get/remove` writes the `[mcp_servers.xax]` table shown in HOSTS.md; no health check available |
| Claude Desktop | — | not run here; the config uses the documented `mcpServers` format |

No model-driven host session (an agent choosing the tools) was recorded. That needs authenticated host accounts.

## Upgrading XAX

1. Check out the new XAX commit and run its tests.
2. Install it into a fresh venv with xax-mcp. Run `xax-mcp --check`, which reports `untested` and the new
   fingerprint.
3. Run this repository's tests with `XAX_MCP_ALLOW_UNTESTED_XAX=1 XAX_SOURCE_DIR=<checkout>`.
4. If they pass, add `{commit: fingerprint}` to `compat.TESTED_XAX`, update `PINNED_XAX_COMMIT`, the git pin in
   `pyproject.toml`, the CI checkout ref, and this table, then release a new xax-mcp version.
