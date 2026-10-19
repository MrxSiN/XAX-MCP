# XAX-MCP

An optional [Model Context Protocol](https://modelcontextprotocol.io) server for
[XAX](https://github.com/MrxSiN/XAX), implemented as a **native XAX program**: a verified canonical
`xax-construct-v1` store that XAX builds into a Windows x86-64 PE32+ executable. The deployed server does not start
Python, an MCP SDK, a shell wrapper, or another language.

```text
MCP client ──newline-delimited JSON-RPC over STDIO──► xax-mcp-native.exe  (XAX-generated native code)
                                                      ├─ STDIO framing, 4 MiB line limit, resync
                                                      ├─ RFC 8259 JSON validation, UTF-8, depth 64
                                                      ├─ JSON-RPC 2.0, MCP initialize/ping/tools
                                                      ├─ tool dispatch and host-granted rights
                                                      └─ kernel32 only
```

XAX's invariant holds: **meaning is source.** The canonical store is the authoritative program. Tool schemas and
capability text are transport, embedded at construction time; they are never XAX source.

## Status (0.6.0)

| Capability | Status |
|---|---|
| STDIO transport, framing, JSON validation, JSON-RPC, MCP lifecycle, tool dispatch, host rights | **EXECUTED**: `tests/test_native_stdio.py` over the real PE32+ (42 tests) |
| Official MCP Python SDK client (`mcp.Client`) interoperability | **EXECUTED**: handshake, `tools/list`, `tools/call` |
| `xax_capabilities` | **EXECUTED** (native, reports the exact blockers below) |
| `xax_workspace`, `xax_query`, `xax_transaction`, `xax_build`, `xax_result` | **UNIMPLEMENTED natively**: no native XAX compiler service (blocker B1/B2) |
| `xax_construct` (new canonical program from a typed carrier) | **UNIMPLEMENTED natively**: no native carrier decoder (blocker B2) |
| `xax_execute` in an OS sandbox | **UNIMPLEMENTED natively**: no native sandbox (blocker B4); fails closed |
| Streamable HTTP transport | **UNIMPLEMENTED** (STDIO only) |

The protocol layer is real and measured. The compiler-backed tools are not: they answer with a structured
`unsupported` error (or `denied_capability` before the host grants the right). No result is fabricated, and no Python
server is used as a fallback. See [docs/NATIVE.md](docs/NATIVE.md) for the exact upstream gaps and the proposed
native compiler service.

## Build

The build is development tooling and is not on the server's runtime path. It requires a checkout of XAX at the pinned
commit and Python 3.11+ only to emit the construction carrier and invoke `xax_construct`/`xax_build`.

```bash
git clone https://github.com/MrxSiN/XAX ../XAX
git -C ../XAX checkout f79b532fd4651ba808676d02f4b038e2cc271e6a
python native/server.py ../XAX/compiler/src native
```

This writes `native/construction_request.json` (transport), `native/xax-mcp-native-gen0.xax` (the authoritative
store), and `native/xax-mcp-native.exe` (the build product). The store and request are reproducible; the PE depends
on the pinned XAX lowering. The script reads the tool schemas from [`native/schemas.py`](native/schemas.py), which is
build tooling, not part of the server.

The pinned XAX revision is `f79b532fd4651ba808676d02f4b038e2cc271e6a` (XAX `main`, 2026-10-19; host contract
`xax-host-contract-v1` r10; toolchain fingerprint
`0ab800baf79464895bceeb0ccdaa13f4b8d1969fc627644f01e447575731f5d9`). See
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

`--allow-execute` is the host owner's grant for `xax_execute`. Tool arguments can never grant a right. With the
current native build the grant changes only the error: execution remains refused because no native sandbox exists.

## Tools

The schemas are versioned as `xax-mcp-tools-v1` and are identical to the interface the project has exposed since
0.5.x. The native dispatch accepts all eight names; only `xax_capabilities` has a native implementation.

| Tool | Intended capability | Current native status |
|---|---|---|
| `xax_capabilities` | identity, pin, rights, targets, sandbox, maturity | EXECUTED |
| `xax_workspace` | open/identify/close a bounded store | UNIMPLEMENTED |
| `xax_query` | bounded graph queries | UNIMPLEMENTED |
| `xax_construct` | carrier → verified canonical root | UNIMPLEMENTED |
| `xax_transaction` | verify/commit/rollback exact-root edits | UNIMPLEMENTED |
| `xax_build` | build an exact root/entry/target | UNIMPLEMENTED |
| `xax_execute` | run an artifact in an OS sandbox | UNIMPLEMENTED (fails closed) |
| `xax_result` | bounded result/artifact retrieval | UNIMPLEMENTED |

## What this is not

- It is not a working XAX execution plugin yet. The native server can negotiate MCP and report capabilities, but it
  cannot construct, build, query, or run a program. That is stated in every capability response, not hidden.
- It is not a Python server. The 0.5.x Python adapter is retired; it remains in git history and in the historical
  documents marked "Python prototype". No Python is packaged or launched by the server.
- It does not contain workload logic. `native/server.py` only emits the construction carrier; the server's logic is
  the canonical store.
- It does not claim sandboxing. Execution is refused until an OS-enforced sandbox is implemented in XAX.

## Documentation

[Native server](docs/NATIVE.md) · [Compatibility](docs/COMPATIBILITY.md) · [Handoff](docs/HANDOFF.md) ·
[Evidence](docs/EVIDENCE.md) · [XAX contract](docs/XAX_CONTRACT.md) ·
[Upstream proposals](docs/UPSTREAM_PROPOSALS.md) · [Architecture (historical)](docs/ARCHITECTURE.md) ·
[Tools (historical)](docs/TOOLS.md) · [Security (historical)](docs/SECURITY.md) ·
[Performance (historical)](docs/PERFORMANCE.md) · [Hosts (historical)](docs/HOSTS.md)

Documents marked historical describe the retired 0.5.x Python adapter. They are kept for provenance and for the
porting work that remains; they are not descriptions of the deployed 0.6.0 server.

## Development

```bash
pip install pytest anyio "mcp>=2.3.0,<2.4"
XAX_NATIVE_SRC=/path/to/XAX/compiler/src pytest -q -rs
```

The tests are external MCP clients. They rebuild the committed store, check it byte for byte, build the PE, and drive
it over STDIO. Python is not imported by the server.
