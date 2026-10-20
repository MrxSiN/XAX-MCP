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

## Status (0.7.0)

| Capability | Status |
|---|---|
| STDIO transport, framing, JSON validation, JSON-RPC, MCP lifecycle, tool dispatch, host rights | **EXECUTED**: `compiler/integration/mcp/tests/test_native_stdio.py` in XAX over the real PE32+ (44 passed, 1 skipped) |
| Official MCP Python SDK client (`mcp.Client`) interoperability | **EXECUTED**: handshake, `tools/list`, `tools/call` |
| `xax_capabilities` | **EXECUTED** (native, reports the exact blockers below) |
| `xax_workspace`, `xax_query`, `xax_build`, `xax_transaction` | **PROTOTYPE** over a host-granted native XAX compiler: describe the current store, `resolve`+`build`, one `XAXEDIT1` edit |
| `xax_construct` (new canonical program from a typed carrier) | **UNIMPLEMENTED natively**: XAX has the native decoder through step 5a (`compiler/integration/construct`; both committed carriers' listings are byte-identical), but no `construct` command is served (blocker B2) |
| `xax_execute` in an OS sandbox | **PROTOTYPE, MEASURED on windows-x86_64** (also reproduced on a clean windows-2022 CI runner): a second XAX program (authored by `compiler/integration/mcp/sandbox.py` in XAX) runs the built artifact as a capability-less AppContainer in a job object; Linux and typed I/O are open (B3, B4) |
| `xax_result` (bounded result retrieval) | **UNIMPLEMENTED natively**: needs session state |
| Streamable HTTP transport | **UNIMPLEMENTED** (STDIO only) |

The protocol layer is real and measured, and the narrow compiler chain was executed end to end: a committed seed
store is described, resolved and built (1536-byte PE + 268-byte provenance), a 78-byte `XAXEDIT1` record sets a
constant from 40 to 41 with the compiler's native `edit`, and the edited artifact is then run under OS confinement
(`exit_code 41`, 32 ms reported sandbox duration). Without
`XAX_MCP_COMPILER`/`XAX_MCP_WORK`/`XAX_MCP_STORE` the five compiler-backed tools answer `denied_capability`;
`xax_execute` additionally needs `--allow-execute` and a `xax-mcp-sandbox.exe` beside the server. The unimplemented
tools answer `unsupported`. No result is fabricated, and no Python server is used as a fallback. See
[docs/NATIVE.md](docs/NATIVE.md) for the exact upstream gaps and the proposed native compiler service.

## Build

This repository contains no source code. The carriers, canonical stores and executables under `native/` are the
build products; the tooling that produces them lives in XAX at
[`compiler/integration/mcp`](https://github.com/MrxSiN/XAX/tree/4c3e60bef96c56162003838b36d6756295b1de41/compiler/integration/mcp):

```bash
git clone https://github.com/MrxSiN/XAX ../XAX
git -C ../XAX checkout 4c3e60bef96c56162003838b36d6756295b1de41
python ../XAX/compiler/integration/mcp/server.py  ../XAX/compiler/src native   # server store + xax-mcp-native.exe
python ../XAX/compiler/integration/mcp/sandbox.py ../XAX/compiler/src native  # executor store + xax-mcp-sandbox.exe
python ../XAX/compiler/integration/mcp/seed.py    ../XAX/compiler/src native  # editable seed, snapshot and exe
```

This writes `native/construction_request.json` and `native/sandbox_request.json` (transport),
`native/xax-mcp-native-gen0.xax` and `native/xax-mcp-sandbox-gen0.xax` (the authoritative stores), and the
executables (the build products). Put `xax-mcp-sandbox.exe` in the same directory as `xax-mcp-native.exe`. The six
carriers, stores and snapshots are committed and deterministic: CI regenerates them from the pinned tooling and fails
unless every one matches the committed bytes. The three executables are rebuilt from the committed stores on every
run; they are not committed. The tool schemas the server embeds come from the same upstream tooling.

The XAX pin is `4c3e60bef96c56162003838b36d6756295b1de41`, the first commit that carries that tooling. Its
`compiler/src` is byte-identical to `f79b532fd4651ba808676d02f4b038e2cc271e6a` (XAX `main`, 2026-10-19), the
compiler that lowered the committed stores: host contract `xax-host-contract-v1` r10, toolchain fingerprint
`0ab800baf79464895bceeb0ccdaa13f4b8d1969fc627644f01e447575731f5d9`. See
[docs/COMPATIBILITY.md](docs/COMPATIBILITY.md).

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
| `xax_construct` | carrier → verified canonical root | UNIMPLEMENTED (decoder through step 5a in XAX; no command or tool wiring yet) |
| `xax_transaction` | verify/commit/rollback exact-root edits | PROTOTYPE: one `XAXEDIT1` hex record → native `edit` |
| `xax_build` | build an exact root/entry/target | PROTOTYPE: native `resolve` + `build` of the current store |
| `xax_execute` | run an artifact in an OS sandbox | PROTOTYPE (Windows): rebuilds the current store, runs the artifact in `xax-mcp-sandbox.exe`, returns exit code, wall time, flags, stdout/stderr hex |
| `xax_result` | bounded result/artifact retrieval | UNIMPLEMENTED |

## What this is not

- It is not a complete XAX agent execution plugin yet. The native server negotiates MCP, reports capabilities,
  describes and builds the current store, applies one record-shaped edit, and runs the result under Windows OS
  confinement. It cannot construct a new program from a typed carrier, cannot query the graph beyond the root, and
  cannot feed typed input to an artifact or read typed output back. That is stated in every capability response, not
  hidden.
- It is not a Python server, and this repository contains no Python. The 0.5.x Python adapter is retired; it remains
  in git history and in the historical documents marked "Python prototype". No Python is packaged or launched by the
  server, and the build tooling lives in XAX (`compiler/integration/mcp`), not here. The compiler the server spawns
  is a native executable granted by the host.
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
porting work that remains; they are not descriptions of the deployed 0.7.0 server.

## Development

There is nothing to install or run in this repository: it holds the carriers, stores and executables, and their
checks live in XAX.

```bash
git clone https://github.com/MrxSiN/XAX ../XAX
git -C ../XAX checkout 4c3e60bef96c56162003838b36d6756295b1de41
pip install pytest anyio "mcp>=2.3.0,<2.4" -e ../XAX/compiler
XAX_MCP_HOME=$PWD XAX_NATIVE_SRC=../XAX/compiler/src \
  pytest -q ../XAX/compiler/integration/mcp/tests
```

Set `XAX_MCP_TEST_COMPILER=/path/to/native/xaxc` as well to run the gated end-to-end chain test (seed → build →
transaction). The tests are external MCP clients. They regenerate the committed store, check it byte for byte, build
the PE, and drive it over STDIO. Python is not imported by the server.
