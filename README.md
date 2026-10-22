# XAX-MCP

An optional [Model Context Protocol](https://modelcontextprotocol.io) server for
[XAX](https://github.com/MrxSiN/XAX), implemented as a **native XAX program**: a verified canonical
`xax-construct-v1` store that XAX builds into a Windows x86-64 PE32+ executable. The deployed server does not start
Python, an MCP SDK, a shell wrapper, or another language.

This repository contains no source code: only carriers, canonical stores, executables, evidence and documents. The
tooling that produces them lives in XAX (`compiler/integration/mcp`), so nothing here has to be maintained or built
separately.

```text
MCP client ──newline-delimited JSON-RPC over STDIO──► xax-mcp-native.exe  (XAX-generated native code)
                                                      ├─ STDIO framing, 4 MiB line limit, resync
                                                      ├─ RFC 8259 JSON validation, UTF-8, depth 64
                                                      ├─ JSON-RPC 2.0, MCP initialize/ping/tools
                                                      ├─ tool dispatch and host-granted rights
                                                      ├─ spawn a host-granted native XAX compiler
                                                      └─ kernel32 + msvcrt only (no Python, no SDK)
```

XAX's invariant holds: **meaning is source.** The canonical store is the authoritative program. Tool schemas and
capability text are transport, embedded at construction time; they are never XAX source.

## Status (0.8.0)

| Capability | Status |
|---|---|
| STDIO transport, framing, JSON validation, JSON-RPC, MCP lifecycle, tool dispatch, host rights | **EXECUTED**: `compiler/integration/mcp/tests/test_native_stdio.py` in XAX over the real PE32+ (44 passed, 1 skipped without a compiler; 45 passed, 0 skipped with a native `xaxc` rebuilt at the pin) |
| Official MCP Python SDK client (`mcp.Client`) interoperability | **EXECUTED**: handshake, `tools/list`, `tools/call` |
| `xax_capabilities` | **EXECUTED** (native, reports the exact blockers below) |
| `xax_workspace`, `xax_query`, `xax_build`, `xax_transaction` | **PROTOTYPE** over a host-granted native XAX compiler: describe the current store, `resolve`+`build`, one `XAXEDIT1` edit |
| `xax_construct` (new canonical program from a typed carrier) | **PROTOTYPE on windows-x86_64**: the server copies the inline `xax-construct-v1` carrier to the work directory and spawns the host-granted native `construct <carrier> <store>` command (`XAX_MCP_CONSTRUCT`); the store it writes becomes the current store. `native/sandbox_request.json` decodes to `native/xax-mcp-sandbox-gen0.xax` byte for byte (74 434 B, root `7ef7099d...`). Linux, candidate stores, rollback and result handles are open |
| `xax_execute` in an OS sandbox | **PROTOTYPE, MEASURED on windows-x86_64** (also reproduced on a clean windows-2022 CI runner): a second XAX program (authored by `compiler/integration/mcp/sandbox.py` in XAX) runs the built artifact as a capability-less AppContainer in a job object; Linux and typed I/O are open (B3, B4) |
| `xax_result` (bounded result retrieval) | **UNIMPLEMENTED natively**: needs session state |
| Streamable HTTP transport | **UNIMPLEMENTED** (STDIO only) |

The protocol layer is real and measured, and the narrow compiler chain was executed end to end: a committed seed
store is described, resolved and built (1536-byte PE + 268-byte provenance), a 78-byte `XAXEDIT1` record sets a
constant from 40 to 41 with the compiler's native `edit`, and the edited artifact is then run under OS confinement
(`exit_code 41`, 16 ms reported sandbox duration in the 0.8.0 re-run). `xax_construct` was executed over the same
STDIO transport with a host-granted native decoder: the committed sandbox carrier produced the committed sandbox
store byte for byte and became the work directory's current store. Without
`XAX_MCP_COMPILER`/`XAX_MCP_WORK`/`XAX_MCP_STORE` the five compiler-backed tools answer `denied_capability`;
`xax_construct` needs `XAX_MCP_CONSTRUCT` plus `XAX_MCP_WORK`; `xax_execute` additionally needs `--allow-execute` and
a `xax-mcp-sandbox.exe` beside the server. Only `xax_result` remains unimplemented and answers `unsupported`. No
result is fabricated, and no Python server is used as a fallback. See [docs/NATIVE.md](docs/NATIVE.md) for the exact
upstream gaps and the proposed native compiler service.

## Build

This repository contains no source code and no Python. The carriers, canonical stores and executables under
`native/` are the build products; the tooling that produces them lives in XAX at
[`compiler/integration/mcp`](https://github.com/MrxSiN/XAX/tree/6b6c35939ff02c365a58c3534cf1b75a2281d393/compiler/integration/mcp).
Rebuilding has two stages. Both can run with no interpreter when a native decoder and compiler are granted; the
compiler is rebuilt locally from the pinned tree and is not committed (B1):

```text
carrier --> store      native XAX decoder, host-granted as XAX_MCP_CONSTRUCT      [verified: byte-identical]
store   --> PE + prov  native xaxc `build` on the committed snapshot store        [executor: byte-identical]
                                                                                 [server: same size, probe omitted]
```

The decoder is the `construct <carrier> <store>` program from `compiler/integration/construct` in XAX. The build
stage is the same `resolve`, `build` and `edit` command set the server drives; the server only ever spawns a native
`xaxc` granted as `XAX_MCP_COMPILER`, never Python. On this host the native compiler ran `build` directly on both
committed snapshot stores: the 8-function executor artifact is byte-identical to the committed PE, and the
181-function server artifact is the same 359 424 B and passes every external test except the byte-identity
assertion, but it omits the reference build's Windows guard-page stack probe, shifting the rest of the image and
changing 231 313 bytes. The committed server PE therefore remains the author-built one, which `xax_build.build`
reproduces exactly; fixing that omission is the narrowed B1 item
(`docs/evidence/native-windows-x86_64-native-build-parity-3e9b0c2.json`). The same `resolve`, `build` and `edit` chain
was executed against the native compiler: 45 passed, 0 skipped, with the edited artifact executed under confinement
(`exit_code 41`); `docs/evidence/native-windows-x86_64-chain-3e9b0c2.json`.
The six carriers, stores and snapshots are committed and deterministic: the decoder reproduces both stores from the
committed carriers byte for byte, and CI regenerates them from the pinned tooling and fails unless every one matches.
The three executables are rebuilt from the committed stores; they are not committed. The tool schemas the server
embeds come from the same upstream tooling.

The certified XAX pin is `3e9b0c2b3f88d2193caae72a5fe8eefa83d1995b` (XAX `main`, 2026-10-22): host contract
`xax-host-contract-v1` r10, toolchain fingerprint
`ba009daa933c33ba124f2dc2fcb7a09995553b867bc68289555871b2f47eb740`. The authoring tooling and tests live at
`6b6c35939ff02c365a58c3534cf1b75a2281d393` on branch `integration/mcp-on-main-3e9b0c2`, which is `3e9b0c2` plus the
MCP commits; its `compiler/src` is byte-identical to `3e9b0c2` (`git diff 3e9b0c2 6b6c359 -- compiler/src` is empty),
so the store embeds `3e9b0c2` as its pin. See [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md).

Python remains only outside this repository and off the request path: the offline carrier authors in
`compiler/integration/mcp` (used to *change* the program's semantics, not to rebuild it) and the external MCP test
client. Replacing those authors with native XAX code is upstream work (B5).

## Run

```bash
./native/xax-mcp-native.exe --read-only
```

The executable speaks newline-delimited JSON-RPC 2.0 on stdin/stdout. STDOUT is protocol-only; diagnostics, if any,
go to stderr. Accepted flags: `--allow-execute`, `--read-only`, `--deny RIGHT`, `--deny=RIGHT`, and
`--no-warm-server` (a no-op). Any other argument makes the server exit with status 2 before reading stdin.

Register the executable with an MCP client:

```json
{"mcpServers": {"xax": {"type": "stdio", "command": "C:/path/to/xax-mcp-native.exe", "args": ["--read-only"]}}}
```

The five compiler-backed tools also need a host grant: a native XAX compiler, a writable work directory, and a seed
build-request store. The server spawns that compiler; it does not embed one.

```json
{"mcpServers": {"xax": {"type": "stdio", "command": "C:/path/to/xax-mcp-native.exe", "args": ["--read-only"],
  "env": {"XAX_MCP_COMPILER": "C:/path/to/xaxc.exe",
          "XAX_MCP_WORK": "C:/path/to/work",
          "XAX_MCP_STORE": "C:/path/to/xax-mcp-seed.xax"}}}}
```

`--allow-execute` is the host owner's grant for `xax_execute`. Tool arguments can never grant a right. With the right
granted and a `xax-mcp-sandbox.exe` beside the server, execution resolves and builds the current store and runs the
artifact under Windows OS confinement; without either, it fails closed with `denied_capability` or
`sandbox_unavailable` and runs nothing.

## Tools

The schemas are versioned as `xax-mcp-tools-v1`. The native dispatch accepts all eight names; the compiler-backed
tools are narrowed to the implemented prototype.

| Tool | Intended capability | Current native status |
|---|---|---|
| `xax_capabilities` | identity, pin, rights, targets, sandbox, maturity | EXECUTED |
| `xax_workspace` | open/identify/close a bounded store | PROTOTYPE: describes the current store's root and size |
| `xax_query` | bounded graph queries | PROTOTYPE: `root` only (root + byte size) |
| `xax_construct` | carrier → verified canonical root | PROTOTYPE (Windows): one inline `xax-construct-v1` carrier → native `construct <carrier> <store>`, replaces the current store |
| `xax_transaction` | verify/commit/rollback exact-root edits | PROTOTYPE: one `XAXEDIT1` hex record → native `edit` |
| `xax_build` | build an exact root/entry/target | PROTOTYPE: native `resolve` + `build` of the current store |
| `xax_execute` | run an artifact in an OS sandbox | PROTOTYPE (Windows): rebuilds the current store, runs the artifact in `xax-mcp-sandbox.exe`, returns exit code, wall time, flags, stdout/stderr hex |
| `xax_result` | bounded result/artifact retrieval | UNIMPLEMENTED |

## What this is not

- It is not a complete XAX agent execution plugin yet. The native server negotiates MCP, reports capabilities,
  describes and builds the current store, applies one record-shaped edit, constructs a new program from one typed
  carrier with a host-granted decoder, and runs the result under Windows OS confinement. It cannot query the graph
  beyond the root, cannot construct on Linux, and cannot feed typed input to an artifact or read typed output back.
  That is stated in every capability response, not hidden.
- It is not a Python server, and this repository contains no Python. The 0.5.x Python adapter is retired; it remains
  in git history and in the historical documents marked "Python prototype". No Python is packaged, imported or
  launched by the server. The committed carriers decode to their committed stores with a native XAX decoder, and the
  build stage is the XAX compiler's `resolve`/`build`, not an interpreter; a committed reproducible native Windows
  compiler for that stage is still missing upstream (B1), and the native `build` omits the reference guard-page stack
  probe in the large server store (same size and behavior, not byte-identical). The carrier
  authors that emit the carriers are offline (B5).
- It does not contain workload logic. The carrier emitter in XAX only writes the construction request; the server's
  logic is the canonical store.
- It does not claim sandboxing. Execution is refused until an OS-enforced sandbox is implemented in XAX.

## Documentation

[Native server](docs/NATIVE.md) · [Compatibility](docs/COMPATIBILITY.md) · [Handoff](docs/HANDOFF.md) ·
[Evidence](docs/EVIDENCE.md) · [XAX contract](docs/XAX_CONTRACT.md) ·
[Upstream proposals](docs/UPSTREAM_PROPOSALS.md) · [Architecture (historical)](docs/ARCHITECTURE.md) ·
[Tools (historical)](docs/TOOLS.md) · [Security (historical)](docs/SECURITY.md) ·
[Performance (historical)](docs/PERFORMANCE.md) · [Hosts (historical)](docs/HOSTS.md)

Documents marked historical describe the retired 0.5.x Python adapter. They are kept for provenance and for the
porting work that remains; they are not descriptions of the deployed 0.8.0 server.

## Development

There is nothing to install or run in this repository: it holds the carriers, stores and executables, and their
checks live in XAX. The executable is the deliverable; the tests are **external MCP clients** that drive it over
STDIO and compare the committed bytes.

```bash
git clone https://github.com/MrxSiN/XAX ../XAX
git -C ../XAX fetch origin integration/mcp-on-main-3e9b0c2
git -C ../XAX checkout 6b6c35939ff02c365a58c3534cf1b75a2281d393
python -m pip install pytest anyio "mcp>=2.3.0,<2.4"
XAX_MCP_HOME=$PWD XAX_NATIVE_SRC=../XAX/compiler/src \
  python -m pytest -q ../XAX/compiler/integration/mcp/tests
```

Set `XAX_MCP_TEST_CONSTRUCT=/path/to/native/construct` to run the gated carrier → store test (it reproduced both
committed stores byte for byte on the recording host) and `XAX_MCP_TEST_COMPILER=/path/to/native/xaxc` to run the
gated end-to-end chain test (seed → build → transaction → confined execute). With both gates set the 0.8.0 suite is
45 passed, 0 skipped in 58 s. Those Python packages are the test
client and the upstream carrier authors; the server, the executor and the decoder that the tests drive are native
XAX programs. Nothing here is imported by, installed into, or launched by `xax-mcp-native.exe`.
