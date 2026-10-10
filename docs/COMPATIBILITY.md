# Compatibility matrix

| xax-mcp | XAX commit | XAX toolchain fingerprint (sha256) | mcp SDK | Python | OS / arch | Result |
|---|---|---|---|---|---|---|
| unreleased (Windows WIP) | `44b5f3c476e94095af8185aa37cf0e00dc368267` (2026-10-10; host contract `xax-host-contract-v1` r7) | `f58a316a3a4bad23010af87066632b5694c1aace766caf62bdd06ac543ea8509` | 2.3.0 | 3.12.10 | Windows 11 x86-64 | not a release: 39 pass, 12 skipped (Linux-only warm server, `argv`, file-open and xb64 tests), sandbox required; Linux suite not run on this host |
| 0.5.1 | `f0aa191424f6e404004f96422eb8a032ef8a1bb2` (2026-10-09; host contract `xax-host-contract-v1` r3) | `80d8966ec3d78cb7f40ecb05f09dff5f871260fbbccb8ef18068072a242ba659` | 2.3.0 | 3.13.16, 3.11.17 | Linux 6.18 x86-64 | 49/49 tests pass on both, sandbox required |
| 0.5.0 | `13a6843200c42f319ede02968773031fe6bca55f` (2026-10-09; host contract `xax-host-contract-v1` r3) | `bd0c1ef65d041924e4d524ff8f98c8c0afc2434ebd8dc758f6cf2021d7433c19` | 2.3.0 | 3.13.16, 3.11.17 | Linux 6.18 x86-64 | 49/49 tests pass on both, sandbox required |
| 0.4.0 | `6c2df90b5972dcf6f44ae6d32f828f355d30d2de` (2026-10-09; host contract `xax-host-contract-v1` r2) | `41d0f5d652756096522a7dfa8e1b04908a9849203daab50be5db3f650199eb96` | 2.3.0 | 3.13.16, 3.11.17 | Linux 6.18 x86-64 | 49/49 tests pass on both, sandbox required |
| 0.3.1 | `6c2df90b5972dcf6f44ae6d32f828f355d30d2de` (2026-10-09; host contract `xax-host-contract-v1` r2) | `41d0f5d652756096522a7dfa8e1b04908a9849203daab50be5db3f650199eb96` | 2.3.0 | 3.13.16, 3.11.17 | Linux 6.18 x86-64 | 41/41 tests pass on both, sandbox required |
| 0.3.0 | `b0ec772a954a6b7932c6e3c1d44794c036a9b7ab` (2026-10-08; host contract `xax-host-contract-v1` r2) | `636b268c755e16e5cba71022ac1847f5dc0c96471e4a81b49853f035f13224ee` | 2.3.0 | 3.13.16, 3.11.17 | Linux 6.18 x86-64 | 41/41 tests pass on both, sandbox required |
| 0.2.0 | `f38cbeea2b90e9b6a580417ce7efaa7d3d75a183` (2026-10-08; host contract `xax-host-contract-v1` r1) | `cdf3e5868810fb47884391cbe60fe7c79589ca8c0d14979644223f1dce012a7b` | 2.3.0 | 3.13.16, 3.11.17 | Linux 6.18 x86-64 | 38/38 tests pass on both, sandbox required |
| 0.1.0 | `01ad841c76416fc741dd1386b12124904924c10d` (2026-10-08) | `2d5b1f3be0c6c40f394a1e6a109239d38e2b9abc2634b02fbb21cffae172392f` | 2.3.0 | 3.13.16, 3.11.17 | Linux 6.18 x86-64 | 36/36 tests pass on both, sandbox required |

Work in progress after 0.5.1 (Windows x86-64 hosts): pins `44b5f3c` (XAX `main`, host contract r7) and requires
r5. r5 (ADR-256) adds the integer-completion operations (`bit.and/or`, `udiv/urem`, `int.truncate`,
`int.zero.extend`) on `windows-x86_64`, which the poly_reduce test carrier needs; with it the carrier constructs,
builds as a PE image and matches the oracle on Windows 11. r6 (ADR-257, `jvm`) and r7 (ADR-258, `linux-aarch64`) add
construct platforms the adapter does not consume yet. The fingerprint from a git install matches a local checkout.

Declared support for 0.5.1: exactly `f0aa191` (XAX `main`), with `xax-host-contract-v1` at revision ≥ 3. The 21
upstream commits since `13a6843` are S8 (ADR-251, verifier totality): every verifier rejection on the Linux x86-64
production path is now decided by an XAX-hosted component with the bootstrap's exact diagnostic. They change no
host-contract name, format, or revision (`xax_contract.py` is unchanged), and no XAX-MCP code changed. The typing and
store-verifier component stores changed, so the first start after upgrading re-lowers those images and re-verifies
the component stores once (run `xax-mcp --prepare`). 0.5.0's pin `13a6843` now reports `untested` under 0.5.1 (set
`XAX_MCP_ALLOW_UNTESTED_XAX=1` or install xax-mcp 0.5.0 to use it).

Declared support for 0.5.0 (historical): exactly `13a6843` (XAX `main`), with `xax-host-contract-v1` at revision ≥ 3, because the
warm server, `--prepare` and the in-process warm-up call `xax_native.prepare` (ADR-250) instead of constructing a
warm-up carrier. The 5 upstream commits since `6c2df90` are S8c.28 and S8c.29 (ADR-246, ADR-247: more typing
rejections decided by XAX-hosted programs) and P6–P8 (ADR-248 to ADR-250: lazily zeroed views, one-call BLAKE3 up to
16 MiB, `xax_native.prepare`). The BLAKE3 hash store changed (ADR-249), so the first start after upgrading re-lowers
that image and re-verifies the component stores once. XAX commits before r3, including 0.4.0's `6c2df90`, are now
`incompatible` (install xax-mcp 0.4.0 to use them).

Declared support for 0.4.0 (historical): the same as 0.3.1 (no upstream change; the warm server uses only the existing
interfaces).

Declared support for 0.3.1: exactly `6c2df90` (XAX `main`), with `xax-host-contract-v1` at revision ≥ 2. The 14 upstream
commits since `b0ec772` (S8c.14 to S8c.27, ADR-232 to ADR-245) move verifier and typing rejections into XAX-hosted
programs; they change no host-contract name or format, and no XAX-MCP code changed. 0.3.0's pin `b0ec772` now reports
`untested` under 0.3.1 (set `XAX_MCP_ALLOW_UNTESTED_XAX=1` or install xax-mcp 0.3.0 to use it).

Declared support for 0.3.0 (historical): exactly `b0ec772` (XAX `main`), and XAX must provide `xax-host-contract-v1` at
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
