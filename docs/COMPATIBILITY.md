# Compatibility matrix

## Current release

| xax-mcp | XAX commit | XAX host contract | Toolchain fingerprint (sha256) | mcp SDK (test client) | Python (build/test only) | OS / arch | Result |
|---|---|---|---|---|---|---|---|
| 0.6.0 | `f79b532fd4651ba808676d02f4b038e2cc271e6a` (XAX `main`, 2026-10-19) | `xax-host-contract-v1` r10 | `0ab800baf79464895bceeb0ccdaa13f4b8d1969fc627644f01e447575731f5d9` | 2.3.0 | 3.12.10 | Windows 11 x86-64 | native protocol suite: 42 passed; compiler-backed tools UNIMPLEMENTED (docs/NATIVE.md) |

Declared support for 0.6.0: exactly `f79b532` (XAX `main`), with `xax-host-contract-v1` at revision 10. The
fingerprint covers every Python module and bootstrap `.xax` store of the `xax-compiler` distribution at that
commit. It is used by the **build** to identify the compiler that produced the committed store; the deployed
server has no compiler and no runtime Python, so it does not probe a toolchain at startup.

The native server embeds the pin it was built with (`xax.pinned_commit` in `xax_capabilities`). Rebuilding the
store at another XAX revision is not a supported configuration: the committed store/request equality check in
`tests/test_native_stdio.py` fails with an informative mismatch.

### What r8-r10 add upstream

- r8 (ADR-259 to ADR-261): Windows PE32+ DLL export/forward/DllMain contracts.
- r9 (ADR-260): arbitrary `win64-c` imports and COM method calls in carriers.
- r10 (ADR-317): Windows PE32+ forwards and DllMain details; the Windows hosted profile.

XAX-MCP does not consume r8-r10 yet. They are prerequisites for the native sandbox (B4), not evidence of it.

## Historical Python adapter (0.1.0 - 0.5.1)

These rows describe releases whose deployed server was Python. They are kept for provenance and for the porting
work, not as descriptions of 0.6.0. The implementation remains in git history.

| xax-mcp | XAX commit | XAX host contract | Toolchain fingerprint (sha256) | mcp SDK | Python | OS / arch | Result |
|---|---|---|---|---|---|---|---|
| unreleased (Windows WIP) | `44b5f3c476e94095af8185aa37cf0e00dc368267` (2026-10-10) | r7 | `f58a316a3a4bad23010af87066632b5694c1aace766caf62bdd06ac543ea8509` | 2.3.0 | 3.12.10 | Windows 11 x86-64 | 39 pass, 12 skipped (Linux-only warm server, `argv`, file-open and xb64 tests); sandbox required; Linux suite not run on this host |
| 0.5.1 | `f0aa191424f6e404004f96422eb8a032ef8a1bb2` (2026-10-09) | r3 | `80d8966ec3d78cb7f40ecb05f09dff5f871260fbbccb8ef18068072a242ba659` | 2.3.0 | 3.13.16, 3.11.17 | Linux 6.18 x86-64 | 49/49 tests pass on both, sandbox required |
| 0.5.0 | `13a6843200c42f319ede02968773031fe6bca55f` (2026-10-09) | r3 | `bd0c1ef65d041924e4d524ff8f98c8c0afc2434ebd8dc758f6cf2021d7433c19` | 2.3.0 | 3.13.16, 3.11.17 | Linux 6.18 x86-64 | 49/49 tests pass on both, sandbox required |
| 0.4.0 | `6c2df90b5972dcf6f44ae6d32f828f355d30d2de` (2026-10-09) | r2 | `41d0f5d652756096522a7dfa8e1b04908a9849203daab50be5db3f650199eb96` | 2.3.0 | 3.13.16, 3.11.17 | Linux 6.18 x86-64 | 49/49 tests pass on both, sandbox required |
| 0.3.1 | `6c2df90b5972dcf6f44ae6d32f828f355d30d2de` (2026-10-09) | r2 | `41d0f5d652756096522a7dfa8e1b04908a9849203daab50be5db3f650199eb96` | 2.3.0 | 3.13.16, 3.11.17 | Linux 6.18 x86-64 | 41/41 tests pass on both, sandbox required |
| 0.3.0 | `b0ec772a954a6b7932c6e3c1d44794c036a9b7ab` (2026-10-08) | r2 | `636b268c755e16e5cba71022ac1847f5dc0c96471e4a81b49853f035f13224ee` | 2.3.0 | 3.13.16, 3.11.17 | Linux 6.18 x86-64 | 41/41 tests pass on both, sandbox required |
| 0.2.0 | `f38cbeea2b90e9b6a580417ce7efaa7d3d75a183` (2026-10-08) | r1 | `cdf3e5868810fb47884391cbe60fe7c79589ca8c0d14979644223f1dce012a7b` | 2.3.0 | 3.13.16, 3.11.17 | Linux 6.18 x86-64 | 38/38 tests pass on both, sandbox required |
| 0.1.0 | `01ad841c76416fc741dd1386b12124904924c10d` (2026-10-08) | — | `2d5b1f3be0c6c40f394a1e6a109239d38e2b9abc2634b02fbb21cffae172392f` | 2.3.0 | 3.13.16, 3.11.17 | Linux 6.18 x86-64 | 36/36 tests pass on both, sandbox required |

## Hosts

| Host | Version | Verified |
|---|---|---|
| Official MCP Python SDK client (`mcp.Client`, STDIO) | mcp 2.3.0 | initialize, `tools/list`, `xax_capabilities`, denied `xax_construct` (tests/test_native_stdio.py) |
| Raw JSON-RPC (handshake 2025-11-25) | — | initialize, `tools/list`, `tools/call`, stdout purity, 1500-case JSON differential |
| MCP Inspector CLI | 2.10.1 | not re-run against the native 0.6.0 build; the 0.5.1 result is historical |
| Claude Code | 2.1.294 | registration and `claude mcp list` health check only (0.5.1, historical); no model-driven run |
| Codex CLI | 0.161.0 | `codex mcp add/list/get/remove` configuration syntax (0.5.1, historical) |
| Claude Desktop | — | not run here |

No model-driven host session (an agent choosing the tools) has been recorded. The compiler-backed tools are not
implemented, so a model-driven full loop cannot be claimed.

## Upgrading XAX

1. Check out the new immutable XAX commit and record its full hash.
2. Verify the host contract (`xax_contract.HOST_CONTRACT`, `HOST_CONTRACT_MINOR`) and the interfaces the build
   consumes (`xax_construct`, `xax_build`, `xax_workspace`, `xax_local_protocol`, `xax_compiler`, `xax_contract`).
3. Compute the toolchain fingerprint with the same file set and LF normalization as the 0.6.0 row.
4. Rebuild: `python native/server.py ../XAX/compiler/src native`.
5. Run `XAX_NATIVE_SRC=../XAX/compiler/src pytest -q -rs`; the committed store/request equality check must pass.
6. Add a **new** evidence file under `docs/evidence/`; never edit an older one. Update this matrix, the README pin,
   `native/server.py`'s `NATIVE_XAX_COMMIT`, and the CI checkout ref in the same change.

If the new revision changes the store bytes, that is expected; record the new root, store SHA-256, and artifact
SHA-256. If it removes an interface the build needs, the build fails with an import or attribute error and no store
is written.
