# Handoff

## 2026-10-27 — 0.9 verified native construction and rebuild (current)

XAX `af376e8a8a1ac5635bcad459cb7063ef0b326430` is committed/pushed separately: it publishes a pinned native Windows
compiler seed and general native hash build request, with source/bootstrap identities and a versioned file contract.
No MCP application code was added upstream and no replacement/self-host levels changed.

XAX-MCP source is `native/xax-mcp-native-gen1.xax` (root `edd555239cd0bec3dd5457b882e83e0f341149fa44447878c1633600d854539d`).
Every change went through native edit+verify; 46 carrier records reconstruct it from the seed without regenerating
unchanged graphs. Current native executable SHA-256 is `a9400a65c6194bbc52128a22da0b59a2feabdfcf0dbb64666bc2807b000b7f1b`.
Candidate verification/cleanup, strict query/build guards, native construction dispatch, exact nonzero roots,
bounded function discovery and process-lifetime exclusive workdir leases are implemented and tested.

28 external-client checks pass. Local CI orchestration passes 46 source edit replays, two matching server/provenance
builds, sandbox rebuild and 51 protocol exchanges. A separate XAX Sleep(60000) fixture hits the 10-second wall limit.
The supported non-hard-coded construction loop returns actual exit 136. Codex registration commands pass in an
isolated config. New append-only evidence is under `docs/evidence/*20261027.json`; historical evidence stays intact.

Full mission/security readiness remains false. Next work: native general semantic query/handles, typed runtime ABI
and result paging, compiler cancellation and quota/escape coverage, current MCP protocol, actual current Claude and
model-driven host tests, and compiler self-build. Do not replace these with non-XAX runtime helpers or inflated claims.
The upstream legacy bootstrap/test sources remain; no new non-XAX implementation was added.

Earlier dated sections below are historical. See [installation](INSTALL_WINDOWS.md), [native guide](NATIVE.md),
[readiness](WINDOWS_READINESS.md) and [dependency manifest](../native/xax-dependency.json).


## 2026-10-27 — Clean Windows CI smoke passed

Run [40443571319](https://github.com/MrxSiN/XAX-MCP/actions/runs/40443571319) at MCP commit `7eb687d` completed
successfully on the configured `windows-2022` runner. Native artifact identity checks, the 15-response STDIO
fixture and confined execution of the new arithmetic artifact all passed. The job installed no Python, SDK
or compiler implementation and checked out no upstream application tooling. Exact job/step results are in
`docs/evidence/native-windows-ci-smoke-40443571319.json`. This updates the earlier local-only CI observation
below; release remains blocked by the independently reproduced failures and native toolchain gaps.

## 2026-10-27 — Windows native construction evidence; release blocked

Both checkouts were synchronized with remote `main`. XAX's previous local state was preserved in the stash
named `Preserve pre-sync Windows checkout 2026-10-27`; the old `feat/native-construct` branch remains.
The server executable/version/pin are unchanged. Canonical programs are application source owned by this
repository, not "no source code". `schemas/tools-v1.json` is now the local schema transport snapshot.

Seven native `XAXEDIT1` records constructed a new add/multiply/subtract graph. Native verification passed for
each intermediate store; MCP build and sandbox execution returned 136. The source, transactions, artifact,
provenance and replay are in `examples/native-arithmetic`; full positive and negative results are in
`docs/evidence/native-windows-x86_64-transaction-construction-20261027.json`.

Fix the failing release gates first: `xax_transaction` publishes a candidate containing a type-invalid add;
query/build ignore forbidden schema properties. The invalid program was never executed. The current Windows
host has no native carrier decoder, and the recovered native compiler declines the current Windows driver
store. Do not invoke the upstream Python builders to work around the XAX-only instruction. Typed I/O, bounded
queries, opaque handles, compiler-call cancellation and current MCP 2026-07-28 support remain unfinished.

CI is now an independent native artifact/protocol/sandbox smoke workflow. It has no upstream source checkout,
Python setup or SDK installation. This deliberately narrows the automated scope: historical 44/46-test and
SDK-interoperability counts are not current CI results. No Windows runner result is claimed until that workflow
actually executes. See `docs/WINDOWS_READINESS.md` for precise next work and upstream native-only requirements.

## State at 2026-10-23: the verified stores are the programs

- XAX tooling is at `7ed308f001544dff8cdf4bb825a6811d00b2027f` on `integration/mcp-on-main-3e9b0c2`; its
  `compiler/src` is still byte-identical to the certified pin `3e9b0c2`. The five Python carrier emitters
  (`server.py`, `sandbox.py`, `seed.py`, `dsl.py`, `schemas.py`) are retired. Their outputs are the authoritative
  programs in `compiler/integration/mcp/programs`: `xax-mcp-native.xax`, `xax-mcp-sandbox.xax`, `xax-mcp-seed.xax`,
  the committed seed snapshot, both carriers and `tool-schemas.json`.
- No author runs on any build or test path. The external suite reads `programs/` and drives the committed
  executables; with every gate it is 46 passed, 1 skipped on this host, without the optional gates 43 passed,
  4 skipped, and on the clean windows-2022 CI runner 44 passed, 3 skipped (mcp 2.3, no compiler/decoder gates).
  The suite checks `programs/*` byte for byte against `native/*`.
- The three executables are now committed canonical artifacts (`native/xax-mcp-native.exe` `9f6e272b...`,
  `native/xax-mcp-sandbox.exe` `6d563e0f...`, `native/xax-mcp-seed.exe` `8faaeb7e...`). CI verifies those SHA-256
  values and no longer rebuilds them from an author. The server PE remains the author build because the native
  backend still omits the guard-page probe (B1).
- Remaining Python in the XAX directory is `chain.py`, `bench.py`, `fingerprint.py` and the external test client.
  They are tooling only, never shipped and never on the request path; porting them to XAX is the remainder of the
  full-directory port.
- Evidence: `native-windows-x86_64-author-retirement-7ed308f.json` (local suite and bench) and
  `native-windows-ci-author-retirement-39945240009.json` (clean windows-2022 CI run 39945240009, success).

## State at 0.8.0 (2026-10-22): XAX `main` `3e9b0c2`, no Python in this repository or its build path

- Certified XAX pin: `3e9b0c2b3f88d2193caae72a5fe8eefa83d1995b` (XAX `main`, 2026-10-22), host contract
  `xax-host-contract-v1` r10, toolchain fingerprint
  `ba009daa933c33ba124f2dc2fcb7a09995553b867bc68289555871b2f47eb740` (125 files). The authoring tooling and tests
  are at `6b6c35939ff02c365a58c3534cf1b75a2281d393` on branch `integration/mcp-on-main-3e9b0c2` (pushed to
  `MrxSiN/XAX`); that commit is the pin plus the MCP commits and its `compiler/src` is byte-identical to `3e9b0c2`.
- The deployed server is `native/xax-mcp-native.exe` built from `native/xax-mcp-native-gen0.xax`
  (root `18ceecd9fe284e16919bb5f0f40bdf52cf5a90407ad007d218f30d3235024b07`, 1 103 602 B, 181 functions), which the
  native decoder reproduces byte for byte from `native/construction_request.json`. Artifact: 359 424 B, SHA-256
  `9f6e272bbbc938d3493a98b7c68409de31a09ffc4cc958bb41be7447b65c076a`. It reports `0.8.0+native` and pin `3e9b0c2`.
- The executor store, its artifact, the seed store and its snapshot are byte-identical to 0.7.0 (root `7ef7099d...`,
  74 434 B; seed root `572f683e...`, 1 852 B). `sandbox.py` embeds neither the version nor the commit.
- Nothing in this repository is Python. Decoding the committed carriers to their committed stores needs no interpreter:
  a host-granted native decoder (`construct <carrier> <store>`) did exactly that, byte for byte. The PE stage also
  runs natively: `xaxc build` on the committed snapshot stores reproduced the executor artifact byte for byte and
  produced a working server artifact (same 359 424 B) that is not byte-identical to the author-built one (it omits the
  reference Windows guard-page stack probe, shifting the image and changing 231 313 bytes), so the committed server PE
  remains the pinned author build and that omission is the narrowed B1 item. The compiler is not committed (B1).
  Python otherwise remains only as the offline carrier authors (B5) and the external MCP test client.
- Tests: 45 passed, 0 skipped in 58 s on this host with both gates set (`XAX_MCP_TEST_CONSTRUCT` and
  `XAX_MCP_TEST_COMPILER`, the latter a native `xaxc` rebuilt from the pinned `driver.xax`). The official MCP SDK
  client test ran and passed; the chain executed its edited artifact with exit 41. Without the compiler gate the same
  suite is 44 passed, 1 skipped in 55 s. Chain evidence:
  `docs/evidence/native-windows-x86_64-chain-3e9b0c2.json`. With the native-built server PE as `XAX_MCP_NATIVE_EXE`
  the suite is 44 passed, 1 failed in 26 s, the single failure being `test_build_is_deterministic`'s byte comparison.
- Evidence: new files `docs/evidence/native-windows-x86_64-build-3e9b0c2.json` (pin move, new identities, the native
  decoder's byte-identity check on both carriers, and the test counts) and
  `docs/evidence/native-windows-x86_64-native-build-parity-3e9b0c2.json` (the native PE stage and the measured
  parity). Every earlier evidence file is unchanged.
- The 0.5.1 Python adapter remains retired, and its documents remain marked historical.

### Exact blockers

- **B1**: neither a reproducible native Windows compiler nor a reproducible native Windows carrier decoder is
  committed in the pinned tree. The committed `xaxc-linux-x86_64` is a Linux ELF and this host has no Linux. The
  decoder used here is the local prototype `D:\GitHub\XAX\build\construct_cmd\construct.exe` (2 852 352 B,
  SHA-256 `a6bd67fddce407e348c23604434d536690f87e0cfe0e7a6c7c1f8a073dc4c94f`, `feat/native-construct` `486fa9d`).
  The compiler used for the 0.7.0 measurements was an untracked `build/windows_helpers/xaxc-windows.exe` that did not
  survive the move to `3e9b0c2`; on 2026-10-22 it was rebuilt locally from
  `compiler/integration/windows_helpers/driver.xax` (11 890 688 B, SHA-256 `110a76...`) and ran the full chain. It
  also ran `build` on both committed snapshot stores: the executor artifact matched byte for byte, the server
  artifact did not (same size; the native image omits the reference guard-page stack probe;
  `native-windows-x86_64-native-build-parity-3e9b0c2.json`), so the build stage needs that codegen fix as well as
  commitment. Neither program is committed, shipped, or a dependency.
- **B2**: the native programs' contract is files and exit status, not a versioned service. Carrier decoding is a
  separate `construct <carrier> <store>` program, not a driver command; there is no bounded query and no
  generation/root-checked transaction interface.
- **B3**: no Linux build/run of the native server was tested here.
- **B4**: the Windows sandbox is a prototype (LPAC AppContainer + job object in the executor store
  `compiler/integration/mcp/programs/xax-mcp-sandbox.xax` in XAX), measured but not reviewed as a security boundary;
  Linux confinement and the typed I/O contract are missing.
- **B5**: the carrier authors are retired (2026-10-23). The programs are the verified stores in
  `compiler/integration/mcp/programs`; a carrier is transport. The remaining Python in that directory
  (`chain.py`, `bench.py`, `fingerprint.py`, the external test client) is tooling only and is the remainder of the
  full-directory port to XAX.

### Next steps, in order of leverage

1. Upstream: commit reproducible native Windows builds of the compiler and the decoder for the pinned tree, and emit
   the same guard-page stack probe as `xax_build.build` in the native backend (the executor already matches
   byte-for-byte), then a versioned `xaxc serve` interface (construct/open/verify/query/edit/build, length-prefixed
   typed requests, structured diagnostics).
2. Upstream: port the remaining tooling (`chain.py`, `bench.py`, `fingerprint.py`, the test client) to XAX programs
   so the authoring directory is Python-free (B5 remainder). The carriers and stores are committed and verified.
3. Here: grow the prototype behind the same tool names - bounded queries, expected-generation/root transactions,
   artifact handles and `xax_result` - without reimplementing graph construction or the compiler in the server.
4. Sandbox: harden the Windows executor (typed I/O, argv, per-call limits, independent review), and port the Linux
   sandbox after a Linux build.
5. Record a model-driven Codex/Claude session only after a novel construct -> build -> execute loop actually works.

## Historical: 0.7.0 (2026-10-22)

- XAX pin: `0a0b1c4f1b217ce3a46917e93c1a1b7a66ee9bd8` (`feat/mcp-tooling`: its parent
  `4c3e60bef96c56162003838b36d6756295b1de41` moved the authoring tooling (`compiler/integration/mcp`) into XAX;
  the pin adds the `xax_construct` wiring). Its `compiler/src` is byte-identical to
  `f79b532fd4651ba808676d02f4b038e2cc271e6a` (XAX `main`, 2026-10-19), host contract `xax-host-contract-v1` r10,
  toolchain fingerprint `0ab800baf79464895bceeb0ccdaa13f4b8d1969fc627644f01e447575731f5d9`.
- The deployed server is `native/xax-mcp-native.exe`: a canonical XAX store (`native/xax-mcp-native-gen0.xax`)
  built from `native/construction_request.json`. It implements STDIO framing, strict JSON validation, JSON-RPC 2.0,
  MCP initialize/ping/tools/list/tools/call, tool dispatch, and host rights. It imports kernel32 and msvcrt and
  starts no Python.
- This repository holds no source code: carriers, canonical stores, executables, evidence and docs only. The build
  tooling (`server.py`, `sandbox.py`, `dsl.py`, `schemas.py`, `seed.py`, `chain.py`, `bench.py`,
  `fingerprint.py`) is in XAX under `compiler/integration/mcp`. It is not on the request path.
- `native/xax-mcp-seed.xax` is a committed form-2 build-request seed; `compiler/integration/mcp/chain.py` in XAX
  authors `XAXEDIT1` carriers and drives the native compiler for tests.
- Five tools are a **PROTOTYPE** over a host-granted native compiler: `xax_workspace` and `xax_query` describe the
  current store's root and byte size, `xax_build` runs `resolve` + `build`, `xax_transaction` applies one
  `XAXEDIT1` record with `edit`, and `xax_execute` runs the built artifact under Windows OS confinement. Without
  `XAX_MCP_COMPILER`/`XAX_MCP_WORK`/`XAX_MCP_STORE` they fail closed with `denied_capability`; `xax_execute` also
  needs `--allow-execute` and `xax-mcp-sandbox.exe` beside the server.
- `compiler/integration/mcp/sandbox.py` in XAX builds `xax-mcp-sandbox.exe`, a **separate** native XAX program: a capability-less AppContainer
  inside a job object (5 s CPU, 256 MiB, one process, 10 s wall, 1 MiB per stream). The server spawns it with a fixed
  three-word argv and reads back stdout, stderr and a 16-byte result record.
- `xax_construct` is a **PROTOTYPE** over a host-granted native carrier decoder: it copies the inline
  `xax-construct-v1` request verbatim to `<work>\construct-request.json`, spawns the decoder
  (`XAX_MCP_CONSTRUCT`) with a fixed three-word argv, and makes the verified store current only after exit 0 and a
  readable store. It executed over STDIO on 2026-10-22: the committed sandbox carrier produced the committed
  74 434 B store byte for byte (root `7ef7099d...`). Without `XAX_MCP_CONSTRUCT`/`XAX_MCP_WORK` it fails closed.
- `xax_result` is **UNIMPLEMENTED natively** and returns a structured `unsupported` error. Upstream, the native
  decoder `compiler/integration/construct` (branch `feat/native-construct`, step 6) also reproduces the new
  server store from `native/construction_request.json` byte for byte (1 103 601 B / `afa5b600...`, root
  `9493014f...`). The general driver does not dispatch the command: the decoder is a separate native program.
- Tests: `compiler/integration/mcp/tests/test_native_stdio.py` in XAX, 43 passed and 2 skipped on this host
  (the `mcp` 2.x SDK client and a native Windows `xaxc` were absent), 28 s on Windows 11, Python 3.12.10 (test
  client only), with `XAX_MCP_TEST_CONSTRUCT` set. The suite rebuilds both committed stores, checks them byte for
  byte, builds both PEs, drives the server over STDIO, and (when granted) runs the carrier -> decoder path and the
  seed -> build -> transaction -> confined execute chain.
- Evidence: new file `docs/evidence/native-windows-x86_64-construct-0a0b1c4.json` (new server identity, native
  decoder oracle match, `xax_construct` results, test counts), alongside
  `docs/evidence/native-windows-x86_64-build-f79b532-r3.json` (build identity),
  `docs/evidence/native-windows-x86_64-sandbox-f79b532.json` (confinement results and measurements),
  `docs/evidence/native-windows-x86_64-construct-dabf730.json` (native construct step 5a: both carriers'
  listings byte-identical), `docs/evidence/native-windows-x86_64-construct-ae85b8d.json` (native construct
  step 5b: target, module, package, profile, policy and build request included),
  `docs/evidence/native-windows-x86_64-construct-f0fc9c9.json` (native construct step 5c root: the snapshot
  CID is the reference store root), `docs/evidence/native-windows-x86_64-construct-1e78168.json` (native
  construct step 5c container: both stores byte-identical to the committed files),
  `docs/evidence/native-windows-x86_64-construct-486fa9d.json` (native construct step 6: the
  `construct <carrier> <store>` command reproduces both stores) and
  `docs/evidence/native-windows-ci-tooling-9746e8d.json` (this revision on a clean windows-2022 runner: every
  committed carrier and store reproduced, 43 passed / 2 skipped) plus
  `docs/evidence/native-windows-ci-sandbox-0137179.json` (the confinement
  reproduced on a clean GitHub windows-2022 runner), alongside the earlier
  `native-windows-x86_64-chain-f79b532.json`. The earlier `f79b532` and 6885f89 evidence files are unchanged.
- The retired 0.5.1 Python adapter (`src/xax_mcp`) is removed. Its docs are marked historical; git history retains
  the implementation for the porting work.

### Exact blockers

- **B1**: no reproducible native compiler or carrier decoder is committed for the pinned Windows tree. The committed
  `xaxc-linux-x86_64` is a Linux ELF and this host has no Linux. The prototype therefore consumes a host-granted
  `xaxc-windows.exe` at `D:\GitHub\XAX\build\windows_helpers` (verify/inspect/build/resolve/lower/edit, no
  `construct`, no committed build script) and a host-granted `construct.exe`
  (`D:\GitHub\XAX\build\construct_cmd\construct.exe`, 2 852 352 B, SHA-256 `a6bd67fd...`, built from
  `feat/native-construct` `486fa9d`). Neither is committed, shipped, or a dependency.
- **B2**: the native programs' command set is files and exit status, not a versioned service. The carrier decoder is
  a separate `construct <carrier> <store>` program, not a driver command; there is no bounded query and no
  generation/root-checked transaction interface.
- **B3**: no Linux build/run of the native server was tested here.
- **B4**: the Windows sandbox is a prototype (LPAC AppContainer + job object in `compiler/integration/mcp/sandbox.py` in XAX), measured but not
  reviewed as a security boundary; Linux confinement and the typed I/O contract are missing.

### Next steps, in order of leverage

1. Upstream: commit reproducible native Windows builds of the compiler (for `f79b532`) and the carrier decoder
   (for `486fa9d`), then a versioned `xaxc serve` interface (construct/open/verify/query/edit/build,
   length-prefixed typed requests, structured diagnostics).
2. Here: grow the prototype behind the same tool names - bounded queries, expected-generation/root transactions,
   artifact handles and `xax_result` - without reimplementing graph construction or the compiler in the server.
3. Sandbox: harden the Windows executor (typed I/O, argv, per-call limits, independent review), and port the Linux
   sandbox after a Linux build.
4. Record a model-driven Codex/Claude session only after a novel construct -> build -> execute loop actually works.

## Historical: 0.5.1 and earlier (Python adapter)

These releases used a Python server (`src/xax_mcp`). They are recorded for provenance, not as descriptions of the
current server.

- 0.5.1 (2026-10-10): XAX `f0aa191`, host contract r3. 49/49 tests on Python 3.11/3.13. Warm-server first result
  0.17 s; in-process populated cache 1.1 s; empty-cache `--prepare` 20.1 s.
- 0.5.0 (2026-10-09): XAX `13a6843`, host contract r3. `xax_native.prepare`; warm server; 49/49 tests.
- 0.4.0 (2026-10-09): XAX `6c2df90`, host contract r2. Per-user warm server; 49 tests.
- 0.3.1 / 0.3.0 / 0.2.0 / 0.1.0: see the compatibility matrix and `docs/evidence/`.
- Unreleased Windows WIP (2026-10-10): XAX `44b5f3c`, host contract r7; Windows construct/build/run in an LPAC
  AppContainer; 39 pass, 12 platform skips. This was the last Python implementation.

## Rules

- The deployed server and every runtime component are XAX, and this repository contains no Python and no source
  code. Build tooling lives in `MrxSiN/XAX` (`compiler/integration/mcp`); the committed carriers can be decoded and
  built with native XAX programs alone (B1: the compiler is not committed and large-store byte parity is open), and
  the Python authors that write the carriers are offline (B5).
- No workload logic in the server or build tooling: no per-operation tools, no adapter-side computation.
- Keep XAX changes in `MrxSiN/XAX`; dependency direction is one-way (`XAX-MCP -> XAX`).
- When the pin changes, update the CI checkout ref, `README.md`, `docs/NATIVE.md`, `docs/COMPATIBILITY.md`,
  `CLAUDE.md` and this file together. Check that the new pin's `compiler/src` is byte-identical to the recorded
  `NATIVE_XAX_COMMIT`; if it is not, update `NATIVE_XAX_COMMIT` in `compiler/integration/mcp/{server,sandbox}.py`,
  regenerate both stores, and record the new fingerprint upstream too.
  Add new evidence; never overwrite old evidence files.
