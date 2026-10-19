# Native XAX server (`xax-mcp-native`)

Status: **0.6.0, protocol layer complete; compiler-backed tools blocked upstream** (2026-10-19). The MCP protocol
layer is an XAX program: a verified canonical store that XAX builds into a Windows x86-64 PE32+ executable. The
deployed server starts no Python, no MCP SDK, and no shell. The seven tools that need the XAX compiler are
**UNIMPLEMENTED natively**; each answers with a structured `unsupported` error after the host-rights check. The
Python 0.5.x server has been removed from the deployed path.

Evidence terms follow [EVIDENCE.md](EVIDENCE.md): *implemented* (in the store), *compiled* (XAX built it),
*executed* (ran), *integration-tested* (a test drove it over STDIO), *benchmarked* (raw samples recorded). Nothing
here is *security-tested* in the sandbox sense, because the native server has no sandbox and executes nothing.

## What is XAX and what is not

```text
MCP client ──newline-delimited JSON-RPC over STDIO──► xax-mcp-native.exe  (XAX-generated x86-64 machine code)
                                                      ├─ STDIO framing, 4 MiB line limit, resync after oversize lines
                                                      ├─ RFC 8259 JSON validation with strict UTF-8, depth limit 64
                                                      ├─ JSON-RPC 2.0 envelope checks and error codes
                                                      ├─ MCP initialize/ping/tools/list/tools/call, notifications
                                                      ├─ tool dispatch, host rights from the command line
                                                      └─ kernel32 only: GetStdHandle ReadFile WriteFile VirtualAlloc
                                                         VirtualFree ExitProcess GetCommandLineA lstrcpynA
```

| Part | Form | Authority |
|---|---|---|
| Server program | `native/xax-mcp-native-gen0.xax`, a verified canonical XAX store (117 functions) | authoritative program |
| Construction carrier | `native/construction_request.json` (`xax-construct-v1`) | transport, decoded once by `xax_construct` |
| `native/dsl.py`, `native/server.py`, `native/schemas.py` | Python development tooling that writes the carrier | not source, not on the request path |
| `xax-mcp-native.exe` | PE32+ built from the store by `xax_build` (not committed; rebuilt from the store) | build product |

There is no textual XAX: `server.py` emits typed graph nodes through the carrier, the same way upstream's R6
applications (`xb64`, `xwc`, `xcksum`) were constructed. Upstream's own compiler stores are built by Python builders
in the same way.

## Build

```bash
git -C ../XAX checkout f79b532fd4651ba808676d02f4b038e2cc271e6a
python native/server.py ../XAX/compiler/src native
```

This writes `construction_request.json`, the store and `xax-mcp-native.exe`. The store and request are checked byte
for byte by `tests/test_native_stdio.py`; the PE is rebuilt deterministically from the committed store. The pinned
XAX revision is `f79b532fd4651ba808676d02f4b038e2cc271e6a` (XAX `main`, 2026-10-19; host contract
`xax-host-contract-v1` r10; toolchain fingerprint
`0ab800baf79464895bceeb0ccdaa13f4b8d1969fc627644f01e447575731f5d9`).

Build identity for this revision (new evidence, not a rewrite of older files):

| Field | Value |
|---|---|
| Store root | `2a87c9e5b92b9ee2acd5db04e9889bcb5b1feebc3c5717b9f33f244ed015a238` |
| Release request | `88cf99ae9ac9fac6b79b73bc1c45b6bfdfadf1421754193fe21a4eb9a1c57fa3` |
| Store bytes / SHA-256 | 923 675 / `c367233a7b05e517e4e4d8829f2f57a904826392a5f75b08abe3b175b294917e` |
| Artifact bytes / SHA-256 | 234 496 / `b98ea0715498eca82d3ebee521176c5cf2e2013e8d1836d1ef47f3269ea323d6` |
| Functions | 117 |

The store grew relative to the 6885f89 build because the tool schemas and capability text are embedded at
construction time and because XAX r10's canonical writer/lowering changed. The 6885f89 evidence file remains
unchanged.

## Client setup

```json
{"mcpServers": {"xax-native": {"type": "stdio", "command": "C:/path/to/xax-mcp-native.exe", "args": ["--read-only"]}}}
```

Accepted flags: `--allow-execute`, `--read-only`, `--deny RIGHT`, `--deny=RIGHT`, and `--no-warm-server` (a no-op).
Any other argument, or any quote inside an argument, makes the server write one line to stderr and exit with status
2 **before reading stdin**. Running with authority the host did not intend would be worse than not starting.

## Protocol behaviour

`tests/test_native_stdio.py` drives the real executable. It covers the four handshake versions, unknown offers,
ping, `tools/list` (identical to `native/schemas.py`), unknown methods and tools, malformed and oversized lines,
exact id echo, strict JSON UTF-8 validation against Python's parser (1500 randomized cases), CRLF framing, 500
sequential requests, EOF without a final newline, host-right combinations, rejected launch flags, concurrent
servers, and the official `mcp.Client` SDK.

Deliberate differences from the retired Python server:

- **Malformed input gets an answer.** The Python SDK silently dropped unparsable lines, non-object messages and
  messages without a method. The native server follows JSON-RPC 2.0 instead: `-32700` (parse error) or `-32600`
  (invalid request) with `id: null`, or with the id when the id was valid. Oversized lines (> 4 MiB) get `-32600`,
  and the stream resynchronizes at the next newline.
- **Handshake versions only.** It negotiates `2024-11-05`, `2025-03-26`, `2025-06-18` and `2025-11-25`. An unknown
  offer gets `2025-11-25`. The stateless `2026-07-28` envelope is not implemented; `server/discover` is answered
  with method-not-found.
- **Requests are served in order, one at a time.** `notifications/cancelled` is accepted and ignored: no native
  request runs long enough to cancel. Requests are not refused before `initialize`.
- **Argument size** is the raw byte length of the `arguments` value, not its compact re-serialization.
- **Schema validation** is native only for `xax_capabilities` (no properties). For the other tools, the rights check
  comes first and the result is `unsupported` or `denied_capability`.
- **Key matching** is on raw JSON text, so a key spelled with escapes (`"\u0069d"`) is not recognized as `id`.
  Duplicate keys: the last one wins, as in `json.loads`.

## Measurements

Same host as the 6885f89 evidence: AMD family 25 model 80, 16 logical CPUs, Windows 11 Pro 26300. 15 launches, 50
round trips per call per launch; medians shown. Raw samples:
`docs/evidence/native-windows-x86_64-protocol-f79b532.json`.

| Measure | Native XAX 0.6.0 |
|---|---|
| process start to initialize response | 11.5 ms |
| ping round trip | 17.5 µs |
| tools/list round trip | 97.1 µs |
| xax_capabilities round trip | 43.0 µs |
| peak working set | 8.16 MB |

These numbers cover only the protocol layer. No compiler or execution latency is compared, because the native
server has neither.

## Audit: migration matrix

Classification: **N** supported natively (in the store, executed), **I** supported upstream but needing integration,
**M** missing and requiring implementation, **U** unsupported on this host.

| Existing component | Native XAX implementation | Upstream requirement | Test coverage | Status |
|---|---|---|---|---|
| STDIO transport, framing | `main`: ReadFile chunks, line assembly, WriteFile | none | framing, limits, EOF, CRLF, 500 sequential | **N** |
| JSON parse/serialize | `scan`, `scan_string`, `scan_number`, `skip_ws`; literal writers | none | 1500-case randomized differential vs strict `json.loads` | **N** (validation and extraction; no general DOM) |
| JSON-RPC envelope | `handle` | none | 15 error cases | **N** |
| initialize / version negotiation | `handle` | none | all handshake versions, unknown offers | **N** (no 2026-07-28) |
| tools/list, schemas | literal from `native/schemas.py` at construction time | none | identical to the schema module | **N** |
| tool dispatch, error taxonomy | `handle` | none | every tool | **N** |
| argument schema validation | `xax_capabilities` only | none | extra-property cases | **M** for 7 tools |
| host rights, launch flags | `parse_args`, fail closed | none | 7 flag sets, 8 rejected forms, tool arguments never grant | **N** |
| session handles | none yet | a randomness source (`BCryptGenRandom` through ADR-260 imports) | — | **M** |
| `xax_workspace`/`xax_query`/`xax_transaction` | — | a native compiler service exposing open/verify/query/edit | — | **M** (B1, B2) |
| `xax_construct` | — | native carrier decoding: no native `construct` command exists | — | **M** (B1, B2) |
| `xax_build` + cache | — | native `build` exists only in the Linux compiler `xaxc-linux-x86_64` | — | **U** here (B1), **I** on Linux |
| `xax_execute`, typed I/O | — | Windows: CreateProcess with an LPAC AppContainer and job objects; Linux: clone/unshare/seccomp | — | **M** (B3, B4) |
| `xax_result` | — | needs session tables first | — | **M** |
| audit log on stderr | none | none | stderr is empty in tests | **M** (no logging yet; stdout purity holds) |

### Blockers (exact, verified on this host)

- **B1. No native XAX compiler in the pinned Windows tree.** The only committed native compiler is
  `compiler/bootstrap/seed/xaxc-linux-x86_64`, a static Linux ELF (ADR-286). This host has no Linux (no WSL, no
  containers, no VM). On Windows, XAX itself is Python. A native server here could reach construct/verify/build only
  by starting Python, which this rewrite forbids. The seven tools therefore report `unsupported`.
- **B2. The native compiler's command set is not a service.** `xaxc` offers `lower`, `build`, `verify`, `inspect`,
  `resolve`, `edit` and `resolve-trusted` (`xax_selfhost_driver.COMMANDS`), on files and with exit status only. It
  has no `construct` (carrier decoding), no bounded workspace queries, no generation/root-checked transactions, and
  no structured diagnostics on stdout. A native MCP server needs a versioned request/response protocol for those
  (upstream work in `MrxSiN/XAX`, kept independent of MCP).
- **B3. Linux sandbox and Linux build of this server are untested here.** The same program can target
  `linux-x86_64` by swapping the 8 kernel32 imports for `linux.read`/`linux.write`/`mmap`/`exit_group` and argv for
  `linux.startup.*`. That work is not done, because nothing could execute it on this host.
- **B4. Windows sandbox primitives.** ADR-260 lets a carrier declare any `win64-c` import, so CreateProcessW,
  CreateAppContainerProfile, job objects and SetNamedSecurityInfoW are reachable. The structures they need
  (`SECURITY_CAPABILITIES`, `STARTUPINFOEX` attribute lists) have to be laid out by hand in heap views. Not started.

### Local observation, not an integrated dependency

A local XAX-built prototype compiler exists outside the pinned tree at
`D:\GitHub\XAX\build\windows_helpers\xaxc-windows.exe` (11 857 408 bytes, SHA-256
`e2b730647e5005321166513c68c51223b7e8b4ee78222197f99dcf2725016d43`; 508 functions; imports kernel32/msvcrt). It
runs `verify`, `inspect`, `build`, `resolve`, `lower` and `edit` on Windows, and it is **not** part of XAX
`f79b532` and has no committed build script. It does not implement `construct`. It is recorded here as a concrete
path to B1/B2, not as a dependency of this release and not as evidence for any XAX-MCP capability.

## Next steps

1. Upstream (`MrxSiN/XAX`): commit a reproducible native Windows compiler build for the pinned tree, then a
   versioned native compiler service (`xaxc serve`: length-prefixed typed requests for construct/open/verify/query/
   edit/build on stdin/stdout, structured diagnostics).
2. Here: a `linux-x86_64` build of this program (B3), then a session/handle table backed by OS randomness, then
   proxying the compiler tools to that service.
3. Native sandbox: on Linux, clone with new namespaces, a seccomp filter matching the retired Python sandbox; on
   Windows, the LPAC AppContainer and job object. Both fail closed.
4. Maintain the server's own store through workspace transactions from generation 0, as upstream's R6 applications
   are maintained.

## Retired Python server

The 0.5.x Python adapter (`src/xax_mcp`) is removed from the tree. Its documentation is marked historical:
[ARCHITECTURE.md](ARCHITECTURE.md), [TOOLS.md](TOOLS.md), [SECURITY.md](SECURITY.md),
[PERFORMANCE.md](PERFORMANCE.md), [HOSTS.md](HOSTS.md). Git history retains the implementation for the porting work.
No Python server, sidecar, or fallback is launched by `xax-mcp-native.exe`.
