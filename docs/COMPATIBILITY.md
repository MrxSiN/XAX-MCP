# Compatibility matrix

## Windows audit — 2026-10-27

| Server | Native compiler tested | Protocol | Result and limit |
|---|---|---|---|
| Unchanged `0.8.0+native`, embedded XAX pin `3e9b0c2` | Recovered Windows prototype SHA-256 `ff0355c5bf148bc79cf463748a285c3f982b6c8e47faf8d2d25bd3571b2ad638`, canonical source root `2b8136a8...3d17`; not certified as the embedded pin | `2025-11-25` handshake | Seven native transactions, each independently verified, then build and sandbox execute of a new arithmetic graph: exit 136. Stale-root and launch-right checks passed. Candidate-publication and query/build schema checks failed. Decoder absent; no full mission or release-readiness claim. |

The XAX checkout was updated to `fdc7312d60e12b6e784d920217f09df535090d55`; its compiler sources differ from
the embedded pin. Syncing the checkout does not declare that revision compatible or silently repin the server.
The native compiler used above is recorded by exact digest, not represented as current `main`.

Current CI checks this repository's native artifacts and transport data without installing Python or SDKs.
It does not rebuild against XAX or rerun the historical SDK suite. Current MCP `2026-07-28` is unsupported;
Codex/Claude current-version adoption has not been re-certified. The following release rows are historical
certifications, retained unchanged. See [current readiness](WINDOWS_READINESS.md) and
[raw observations](evidence/native-windows-x86_64-transaction-construction-20261027.json).

## Current release

| xax-mcp | XAX commit | XAX host contract | Toolchain fingerprint (sha256) | mcp SDK (test client) | Python (test client and offline authors only) | OS / arch | Result |
|---|---|---|---|---|---|---|---|
| 0.8.0 | `3e9b0c2b3f88d2193caae72a5fe8eefa83d1995b` (XAX `main`, 2026-10-22) | `xax-host-contract-v1` r10 | `ba009daa933c33ba124f2dc2fcb7a09995553b867bc68289555871b2f47eb740` (125 files) | 2.3.0 | 3.12.10 | Windows 11 x86-64 | native protocol suite: 44 passed, 1 skipped without a compiler path, and 45 passed, 0 skipped with a native `xaxc` rebuilt at the pin (the full chain, execute exit 41); the native decoder reproduced both committed stores byte for byte; the native `build` reproduced the executor PE byte for byte and produced a same-size server PE that passes every test except the byte-identity assertion but omits the reference guard-page stack probe (native/self-hosted parity open); compiler- and decoder-backed tools PROTOTYPE over host-granted native programs (docs/NATIVE.md) |

The 0.8.0 authoring tooling and tests are at `6b6c35939ff02c365a58c3534cf1b75a2281d393` on branch
`integration/mcp-on-main-3e9b0c2`. That commit is `3e9b0c2` plus the MCP commits, and its `compiler/src` is
byte-identical to `3e9b0c2` (`git diff 3e9b0c2 6b6c359 -- compiler/src` is empty), so the store's embedded pin and
the certified compiler revision are both `3e9b0c2`. Fetch the branch, or use `3e9b0c2` for the compiler and this
commit for the tooling.

On 2026-10-23 the carrier authors were retired at tooling commit
`7ed308f001544dff8cdf4bb825a6811d00b2027f`; the authoritative programs are the verified stores in
`compiler/integration/mcp/programs`. The 0.8.0 row above is the author-era run and is unchanged. Current CI verifies
the committed executables by SHA-256 and drives the external suite directly; no author runs. The remaining Python in
the tooling directory is `chain.py`, `bench.py`, `fingerprint.py` and the test client (the B5 remainder).

Declared support for 0.8.0: exactly `3e9b0c2b3f88d2193caae72a5fe8eefa83d1995b` as the compiler revision, with
`xax-host-contract-v1` at revision 10. The
fingerprint covers every Python module and bootstrap `.xax` store of the `xax-compiler` distribution at that
commit. It is used by the **build** to identify the compiler that produced the committed store; the deployed
server has no embedded compiler and no runtime Python, so it does not probe a toolchain at startup. The
compiler-backed tools drive a compiler only when the host grants `XAX_MCP_COMPILER`, `XAX_MCP_WORK` and
`XAX_MCP_STORE`; `xax_construct` drives a native carrier decoder only when the host grants `XAX_MCP_CONSTRUCT`
and `XAX_MCP_WORK`. Those native programs' own versions are the host's responsibility.

### Earlier native release (0.7.0)

| xax-mcp | XAX commit | XAX host contract | Toolchain fingerprint (sha256) | mcp SDK (test client) | Python (test client only) | OS / arch | Result |
|---|---|---|---|---|---|---|---|
| 0.7.0 | `0a0b1c4f1b217ce3a46917e93c1a1b7a66ee9bd8` (`feat/mcp-tooling`: its parent `4c3e60bef96c56162003838b36d6756295b1de41` moved `compiler/integration/mcp` into XAX; this tip wires `xax_construct`; its `compiler/src` is byte-identical to `f79b532fd4651ba808676d02f4b038e2cc271e6a`, XAX `main`, 2026-10-19) | `xax-host-contract-v1` r10 | `0ab800baf79464895bceeb0ccdaa13f4b8d1969fc627644f01e447575731f5d9` | 2.3.0 | 3.12.10 | Windows 11 x86-64 | native protocol suite: 43 passed, 2 skipped on the host (no `mcp` 2.x client, no native `xaxc`); compiler- and decoder-backed tools PROTOTYPE over host-granted native programs |

The native server embeds the pin it was built with (`xax.pinned_commit` in `xax_capabilities`). Rebuilding the
store at another XAX revision is not a supported configuration: the committed store/request equality check in
`compiler/integration/mcp/tests/test_native_stdio.py` fails with an informative mismatch.

### What r8-r10 add upstream

- r8 (ADR-259 to ADR-261): Windows PE32+ DLL export/forward/DllMain contracts.
- r9 (ADR-260): arbitrary `win64-c` imports and COM method calls in carriers.
- r10 (ADR-317): Windows PE32+ forwards and DllMain details; the Windows hosted profile.

XAX-MCP consumes r8-r10: the native server declares `win32.import` entities (r9/ADR-260) for its kernel32 and msvcrt
calls and is built with the Windows hosted profile (r10/ADR-317). The same r9 mechanism lets the executor declare
`userenv`/`advapi32` sandbox primitives, so a Windows-only sandbox prototype now exists (B4, see
`docs/evidence/native-windows-x86_64-sandbox-f79b532.json`); Linux confinement does not.

## Historical Python adapter (0.1.0 - 0.5.1)

These rows describe releases whose deployed server was Python. They are kept for provenance and for the porting
work, not as descriptions of 0.7.0. The implementation remains in git history.

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
| Official MCP Python SDK client (`mcp.Client`, STDIO) | mcp 2.3.0 | initialize, `tools/list`, `xax_capabilities`, `xax_construct` denied under `--read-only` (`test_standard_sdk_client`, 0.8.0) |
| Raw JSON-RPC (handshake 2025-11-25) | — | initialize, `tools/list`, `tools/call`, stdout purity, 1500-case JSON differential |
| MCP Inspector CLI | 2.10.1 | not re-run against the native 0.8.0 build; the 0.5.1 result is historical |
| Claude Code | 2.1.294 | registration and `claude mcp list` health check only (0.5.1, historical); no model-driven run |
| Codex CLI | 0.161.0 | `codex mcp add/list/get/remove` configuration syntax (0.5.1, historical) |
| Claude Desktop | — | not run here |

No model-driven host session (an agent choosing the tools) has been recorded. The compiler-backed tools work only
for the narrow seed/edit case, `xax_construct` needs a host-granted decoder and is exercised on Windows only, and
execution is a Windows prototype, so a model-driven construct/build/execute loop cannot be claimed.

## Upgrading XAX

1. Check out the new immutable XAX commit (it must carry `compiler/integration/mcp`) and record its full hash.
2. Verify the host contract (`xax_contract.HOST_CONTRACT`, `HOST_CONTRACT_MINOR`) and the interfaces the build
   consumes (`xax_construct`, `xax_build`, `xax_workspace`, `xax_local_protocol`, `xax_compiler`, `xax_contract`).
3. Compute the toolchain fingerprint with the same file set and LF normalization as the 0.8.0 row
   (`fingerprint.py` in `compiler/integration/mcp` recomputes it from a checkout).
4. Rebuild with native programs, not an interpreter: decode each committed carrier with the native decoder, then build
   each PE with `xaxc build <store> <artifact> <prov>` directly on the decoded store (the store root is a resolved
   snapshot, so no request needs to be committed). The exact commands are in [NATIVE.md](NATIVE.md#build). At 0.8.0 the
   executor artifact rebuilt byte for byte this way; the server artifact is the same size and behaviorally equivalent
   but not byte-identical because it omits the reference guard-page stack probe (that codegen parity is the narrowed
   B1 item), so the committed server PE remains the reference `xax_build.build` output. Changing a program is a
   typed `xaxc edit` on its store, not a regeneration from the retired Python emitters.
5. Run the external suite: `XAX_MCP_HOME=$PWD XAX_NATIVE_SRC=../XAX/compiler/src python -m pytest -q
   ../XAX/compiler/integration/mcp/tests`; the committed store/request equality check must pass. Set
   `XAX_MCP_TEST_CONSTRUCT` to a native decoder to also run the carrier test, and `XAX_MCP_TEST_COMPILER` to a
   native `xaxc` to also run the compiler-backed chain.
6. Add a **new** evidence file under `docs/evidence/`; never edit an older one. Update this matrix, the README pin,
   the programs' embedded pin upstream, and the CI checkout ref, in the same change.

If the new revision changes the store bytes, that is expected; record the new root, store SHA-256, and artifact
SHA-256. If it removes an interface the build needs, the build fails with an import or attribute error and no store
is written.
