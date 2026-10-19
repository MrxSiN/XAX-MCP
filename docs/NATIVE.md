# Native XAX server (`xax-mcp-native`)

Status: **0.7.0, native protocol layer complete; compiler-backed tools a host-granted prototype** (2026-10-19). The
MCP protocol layer is an XAX program: a verified canonical store that XAX builds into a Windows x86-64 PE32+
executable. The deployed server starts no Python, no MCP SDK, and no shell. Four tools (`xax_workspace`,
`xax_query`, `xax_transaction`, `xax_build`) are a **PROTOTYPE** over a host-granted native XAX compiler
(`XAX_MCP_COMPILER`/`XAX_MCP_WORK`/`XAX_MCP_STORE`): they fail closed with `denied_capability` when the host grants no
compiler. `xax_construct`, `xax_execute` and `xax_result` are **UNIMPLEMENTED natively** and fail closed. The Python
0.5.x server has been removed from the deployed path.

The prototype was exercised end to end on 2026-10-19: describe the seed store, resolve and build it (a 1536-byte PE
plus a 268-byte provenance object), apply a 78-byte `XAXEDIT1` constant mutation with the compiler's native `edit`
command, and observe the new root. Raw results:
`docs/evidence/native-windows-x86_64-chain-f79b532.json`. The compiler used was a local XAX-built prototype outside
the pinned tree; committing a reproducible native compiler is still upstream work.

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
                                                      ├─ host-granted native compiler: spawn resolve/build/edit
                                                      └─ kernel32 + msvcrt: ReadFile WriteFile VirtualAlloc
                                                         VirtualFree ExitProcess GetCommandLineA
                                                         GetEnvironmentVariableA GetFileAttributesA
                                                         MoveFileExA lstrcpynA; _open _read _write _close
                                                         _lseek _spawnv
```

| Part | Form | Authority |
|---|---|---|
| Server program | `native/xax-mcp-native-gen0.xax`, a verified canonical XAX store (153 functions) | authoritative program |
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
| Store root | `9a511d007a27851f3a638bdff31e629068cf8faa4a50b98a2e14ed5d2d601f1a` |
| Release request | `5b816185eee02d91a5712b3350f881b07030a5bac97873da1e611fbfd242adbc` |
| Store bytes / SHA-256 | 978 518 / `0bd08c0ed56fb30861cb1c525a9736a4ea0b52f509bdfc149e16b51a5132154b` |
| Artifact bytes / SHA-256 | 284 672 / `2c244f566fb0cbd7459cce5ddb79576c7e5505c531151b4a1e8a34001a4b1dd8` |
| Functions | 153 |

The store changed relative to the earlier `f79b532` build because the tool schemas were narrowed to the implemented
prototype and the compiler tools gained fail-closed checks (unreadable stores, incomplete writes, failed replaces).
The old evidence file `native-windows-x86_64-build-f79b532.json` is unchanged; the build identity above is recorded
in `native-windows-x86_64-build-f79b532-r2.json`.

### Host-granted native compiler

The four compiler-backed tools read three environment variables. All three must be present and non-empty; otherwise
they answer `denied_capability` and do nothing:

| Variable | Meaning |
|---|---|
| `XAX_MCP_COMPILER` | absolute path to a native XAX compiler executable (`xaxc`) |
| `XAX_MCP_WORK` | a writable directory; the server keeps `current.xax`, `snapshot.xax`, `artifact.exe`, `artifact.prov` and the transaction record there |
| `XAX_MCP_STORE` | absolute path to a canonical build-request store used until the work directory has a `current.xax` |

The server only spawns that executable (`_spawnv`) and reads the files it writes. It does not import, embed, or start
Python. `native/xax-mcp-seed.xax` is a committed form-2 build-request seed (root
`572f683e22d94efe404b5b73f59b85edfd3e6ccbd2614342fdf58fe66cb61587`, 1852 bytes); `native/chain.py` is build/test
tooling that authors an `XAXEDIT1` carrier with the pinned XAX Python tooling.

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
- **Schema validation** is native only for `xax_capabilities` (no properties). For the other tools the host-rights
  check comes first; the four compiler-backed tools then require the host compiler grant, and the remaining three
  answer `unsupported`.
- **Key matching** is on raw JSON text, so a key spelled with escapes (`"\u0069d"`) is not recognized as `id`.
  Duplicate keys: the last one wins, as in `json.loads`.

## Measurements

Same host as the 6885f89 evidence: AMD Ryzen 9 5900HS, 16 logical CPUs, Windows 11 Pro 26300. 15 launches, 50
round trips per call per launch; medians shown. Raw samples:
`docs/evidence/native-windows-x86_64-protocol-f79b532.json`. These samples are from the 0.6.0 artifact; the protocol
code is unchanged in 0.7.0, but the artifact SHA-256 is the one in the build table above.

| Measure | Native XAX 0.6.0 |
|---|---|
| process start to initialize response | 11.5 ms |
| ping round trip | 17.5 µs |
| tools/list round trip | 97.1 µs |
| xax_capabilities round trip | 43.0 µs |
| peak working set | 8.16 MB |

### Compiler-backed chain (0.7.0)

One server process, 10 `xax_query` calls, 5 `xax_build` calls (each two compiler spawns), then 5 `xax_transaction`
calls (each one compiler spawn) on successive constants 41..45. Medians of the raw samples; details in
`docs/evidence/native-windows-x86_64-chain-f79b532.json`.

| Measure | 0.7.0 prototype |
|---|---|
| process start to initialize response | 18.0 ms |
| `xax_query` round trip (read the current store) | 0.140 ms |
| `xax_build` round trip (resolve + build) | 44.1 ms |
| `xax_transaction` round trip (edit + replace) | 22.0 ms |
| peak working set | 9.14 MB |

Build and transaction latency is almost entirely the native compiler child process; the server's own handling is
sub-millisecond. No execution latency exists because `xax_execute` is refused.

## Audit: migration matrix

Classification: **N** supported natively (in the store, executed), **P** prototype over a host-granted native compiler
(narrow case, measured), **I** supported upstream but needing integration, **M** missing and requiring implementation,
**U** unsupported on this host.

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
| `xax_workspace`/`xax_query` | same store description (root + byte size) on both tool names | query kinds beyond `root` need a native query service | `test_native_compiler_chain_over_stdio` | **P** (B1, B2) |
| `xax_transaction` | hex `XAXEDIT1` record -> native `edit` -> replace `current.xax` | typed mutations, expected generation/root, verify/rollback | same test; record authored by `native/chain.py` | **P** (B1, B2) |
| `xax_construct` | — | native carrier decoding: no native `construct` command exists | — | **M** (B1, B2) |
| `xax_build` | native `resolve` then `build` of the current store; reports root, artifact bytes, provenance | artifact handles, entry selection, digest report, cache | same test | **P** (B1, B2) |
| `xax_execute`, typed I/O | — | Windows: CreateProcess with an LPAC AppContainer and job objects; Linux: clone/unshare/seccomp | — | **M** (B3, B4) |
| `xax_result` | — | needs session tables first | — | **M** |
| audit log on stderr | none | none | stderr is empty in tests | **M** (no logging yet; stdout purity holds) |

### Blockers (exact, verified on this host)

- **B1. No reproducible native XAX compiler in the pinned Windows tree.** The only committed native compiler is
  `compiler/bootstrap/seed/xaxc-linux-x86_64`, a static Linux ELF (ADR-286). This host has no Linux (no WSL, no
  containers, no VM). On Windows, XAX itself is Python. The 0.7.0 prototype therefore takes a compiler path from the
  host and fails closed when it is not granted; it does not embed an interpreter, and it cannot ship a compiler it
  cannot reproduce. Committing a reproducible native Windows compiler is upstream work.
- **B2. The native compiler's command set is not a service.** `xaxc` offers `lower`, `build`, `verify`, `inspect`,
  `resolve`, `edit` and `resolve-trusted` (`xax_selfhost_driver.COMMANDS`), on files and with exit status only. It
  has no `construct` (carrier decoding), no bounded workspace queries, no generation/root-checked transactions, and
  no structured diagnostics on stdout. The 0.7.0 server consumes the file commands; a versioned request/response
  protocol for construct/open/query remains upstream work (kept independent of MCP).
- **B3. Linux sandbox and Linux build of this server are untested here.** The same program can target
  `linux-x86_64` by swapping the kernel32/msvcrt file and process calls for `linux.read`/`linux.write`/`mmap`/
  `exit_group` and argv for `linux.startup.*`. That work is not done, because nothing could execute it on this host.
- **B4. Windows sandbox primitives.** ADR-260 lets a carrier declare any `win64-c` import, so CreateProcessW,
  CreateAppContainerProfile, job objects and SetNamedSecurityInfoW are reachable. The structures they need
  (`SECURITY_CAPABILITIES`, `STARTUPINFOEX` attribute lists) have to be laid out by hand in heap views. Not started.

### Local observation, now consumed as a host grant

A local XAX-built prototype compiler exists outside the pinned tree at
`D:\GitHub\XAX\build\windows_helpers\xaxc-windows.exe` (11 857 408 bytes, SHA-256
`e2b730647e5005321166513c68c51223b7e8b4ee78222197f99dcf2725016d43`; 508 functions; imports kernel32/msvcrt). It
runs `verify`, `inspect`, `build`, `resolve`, `lower` and `edit` on Windows, and it is **not** part of XAX
`f79b532` and has no committed build script. It does not implement `construct`.

The 0.7.0 prototype was exercised against exactly this executable as `XAX_MCP_COMPILER` (see
`docs/evidence/native-windows-x86_64-chain-f79b532.json`). It is not a dependency of the repository, not shipped,
and not evidence of a general construct/build/execute loop: it is the narrow path that B1/B2 must replace with a
reproducible, versioned service.

## Next steps

1. Upstream (`MrxSiN/XAX`): commit a reproducible native Windows compiler build for the pinned tree, then a
   versioned native compiler service (`xaxc serve`: length-prefixed typed requests for construct/open/verify/query/
   edit/build on stdin/stdout, structured diagnostics).
2. Here: grow the prototype behind the same tool names - bounded graph queries, expected-generation/root-checked
   transactions, artifact handles and `xax_result` - and add a `linux-x86_64` build of this program (B3).
3. Native sandbox: on Linux, clone with new namespaces, a seccomp filter matching the retired Python sandbox; on
   Windows, the LPAC AppContainer and job object. Both fail closed until they exist.
4. Maintain the server's own store through workspace transactions from generation 0, as upstream's R6 applications
   are maintained.

## Retired Python server

The 0.5.x Python adapter (`src/xax_mcp`) is removed from the tree. Its documentation is marked historical:
[ARCHITECTURE.md](ARCHITECTURE.md), [TOOLS.md](TOOLS.md), [SECURITY.md](SECURITY.md),
[PERFORMANCE.md](PERFORMANCE.md), [HOSTS.md](HOSTS.md). Git history retains the implementation for the porting work.
No Python server, sidecar, or fallback is launched by `xax-mcp-native.exe`.
