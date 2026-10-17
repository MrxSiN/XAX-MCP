# Native XAX server (`xax-mcp-native`)

Status: **phase 2 of the native rewrite** (October 2026). The MCP protocol layer is an XAX program: a verified
canonical store that XAX builds into a Windows x86-64 PE32+ executable. Python is not on its request path. The seven
tools that need the XAX compiler (workspace, query, construct, transaction, build, execute, result) are **not
implemented natively yet**. Each answers with a structured `unsupported` error once the host-rights check has passed.
The blockers are listed below. The Python server (`src/xax_mcp`) is still the production server.

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
| `native/dsl.py`, `native/server.py` | Python development tooling that writes the carrier | not source, not on the request path |
| `xax-mcp-native.exe` | PE32+ built from the store by `xax_build` (not committed; rebuilt byte-identically) | build product |

There is no textual XAX: `server.py` emits typed graph nodes through the carrier, the same way upstream's R6
applications (`xb64`, `xwc`, `xcksum`) were constructed. Upstream's own compiler stores are built by Python
builders in the same way.

## Build

```bash
git -C ../XAX archive 6885f89 compiler/src | tar -x -C /tmp/xax-6885f89
python native/server.py /tmp/xax-6885f89/compiler/src native
```

This writes `construction_request.json`, the store and `xax-mcp-native.exe`. The store and request must equal the
committed files; `tests/test_native_stdio.py` checks this. The build is reproducible: XAX `6885f89` (main) and
`0876b59` (`android-libxposed-jvm`) produce byte-identical stores and executables (PE SHA-256
`39e5d9f4…412df8c`, 224 256 bytes). The construction request does not depend on the XAX revision; it reads the tool
schemas from `src/xax_mcp/schemas.py` and the version from `src/xax_mcp/__init__.py`.

## Client setup

```json
{"mcpServers": {"xax-native": {"type": "stdio", "command": "C:/path/to/xax-mcp-native.exe", "args": ["--read-only"]}}}
```

Accepted flags: `--allow-execute`, `--read-only`, `--deny RIGHT`, `--deny=RIGHT`, and `--no-warm-server` (a no-op).
The rights are computed as in `policy.from_args`. Any other argument, or any quote inside an argument, makes the
server write one line to stderr and exit with status 2 **before reading stdin**. Running with authority the host did
not intend would be worse than not starting. The Python-only flags (`--store-root`, `--wall-ms`, limits) are
therefore rejected rather than ignored.

## Protocol behaviour and documented differences from the Python server

`tests/test_native_stdio.py::test_differential_against_python_server` sends the same requests to this tree's Python
server and to the native one. It compares the parsed responses, normalizing only `serverInfo.version` (`0.5.1+native`).
The cases are: initialize (with a supported version and with an unknown one), ping, tools/list (identical tool
list), unknown method, unknown tool, `xax_capabilities` with an extra property, and a denied `xax_execute`.

Deliberate differences:

- **Malformed input gets an answer.** The Python SDK silently drops unparsable lines, non-object messages and
  messages without a method. The native server follows JSON-RPC 2.0 instead: `-32700` (parse error) or `-32600`
  (invalid request) with `id: null`, or with the id when the id was valid. Oversized lines (> 4 MiB) get `-32600`,
  and the stream resynchronizes at the next newline.
- **Handshake versions only.** It negotiates `2024-11-05`, `2025-03-26`, `2025-06-18` and `2025-11-25` (an unknown
  offer gets `2025-11-25`, as in the Python SDK). The stateless `2026-07-28` envelope is not implemented;
  `server/discover` is answered with method-not-found. The mcp 2.3 SDK client (`mcp.Client`) connects and calls
  tools (`test_standard_sdk_client`).
- **Requests are served in order, one at a time.** `notifications/cancelled` is accepted and ignored: no native
  request runs long enough to cancel. Requests are not refused before `initialize`.
- **Argument size** is the raw byte length of the `arguments` value, not its compact re-serialization. A request
  with extra whitespace can hit the 1 MiB limit sooner.
- **Schema validation** is native only for `xax_capabilities` (no properties). For the other tools, the rights
  check comes first and the result is `unsupported`. With more than one extra property the message reads
  `(N properties were unexpected)` instead of listing the names. Key and name matching is on the raw JSON text, so
  a key spelled with escapes (`"\u0069d"`) is not recognized as `id`. Duplicate keys: the last one wins, as in
  `json.loads`.
- **Echoed text.** Ids are echoed as their exact JSON text. Unknown tool names and unexpected keys are quoted
  `'like this'`, which matches Python's `repr` for ordinary names but not for names containing quotes,
  backslashes or non-ASCII characters.

## Measurements (same host, raw samples in `docs/evidence/native-windows-x86_64-protocol-6885f89.json`)

AMD family 25 model 80, 16 logical CPUs, Windows 11 Pro 26300. 15 interleaved launches per arm, 50 round trips per
call per launch; medians shown. The Python arm is this tree's server on CPython 3.12 with mcp 2.3.0, started in
process (`--no-warm-server`; the warm server is Linux-only).

| Measure | Native XAX | Python | Ratio |
|---|---|---|---|
| process start to initialize response | 12.7 ms | 1 329 ms | 0.0095x |
| ping round trip | 18 µs | 553 µs | 0.033x |
| tools/list round trip | 90 µs | 935 µs | 0.096x |
| xax_capabilities round trip | 34 µs | 2 437 µs | 0.014x |
| peak working set | 8.6 MB | 107.9 MB | 0.080x |

These numbers cover only the protocol layer. The Python server's capabilities call also probes the sandbox and
reports toolchain state, so that row compares more work against less. No compiler or execution latency is compared, because
the native server has neither.

## Audit: migration matrix

Classification: **N** supported natively (in the store, executed), **I** supported upstream but needing
integration, **M** missing and requiring implementation, **U** unsupported on this host.

| Existing component | Current implementation | Native XAX implementation | Upstream requirement | Test coverage | Status |
|---|---|---|---|---|---|
| STDIO transport, framing | mcp SDK 2.3 `stdio_server`, anyio | `main`: ReadFile chunks, line assembly, WriteFile | none | framing, limits, EOF, CRLF, 500 sequential | **N** |
| JSON parse/serialize | `json`, pydantic | `scan`, `scan_string`, `scan_number`, `skip_ws`; literal writers | none | 1500-case randomized differential vs strict `json.loads` | **N** (validation and extraction; no general DOM) |
| JSON-RPC envelope | mcp SDK | `handle` | none | 15 error cases | **N** |
| initialize / version negotiation | mcp SDK | `handle` | none | all handshake versions, unknown offers | **N** (no 2026-07-28) |
| tools/list, schemas | `schemas.py`, SDK | literal from `schemas.py` at construction time | none | identical to Python | **N** |
| tool dispatch, error taxonomy | `server.App.call` | `handle` | none | every tool | **N** |
| argument schema validation | jsonschema 2020-12 | `xax_capabilities` only | none | extra-property cases | **M** for 7 tools |
| host rights, launch flags | argparse, `policy.py` | `parse_args`, fail closed | none | 7 flag sets, 8 rejected forms, tool arguments never grant | **N** |
| session handles (96-bit random) | `secrets`, `service.Session` | none yet | a randomness source: `BCryptGenRandom` through ADR-260 imports | — | **M** |
| `xax_workspace`/`xax_query`/`xax_transaction` | `xax_workspace.Workspace`, `LocalMutationSession` (Python) | — | a native compiler service exposing open/verify/query/edit | — | **M** (B1, B2) |
| `xax_construct` | `xax_construct.construct` (Python) | — | native carrier decoding: no native `construct` command exists | — | **M** (B1, B2) |
| `xax_build` + cache | `xax_build.build` (Python; XAX-hosted components) | — | native `build` exists only in the Linux compiler `xaxc-linux-x86_64` | — | **U** here (B1), **I** on Linux |
| `xax_execute`, typed I/O | `sandbox.py`, `_sandbox_exec.py`, `_sandbox_win.py`, `io_codec.py` | — | Windows: CreateProcess with an LPAC AppContainer, job objects, ACLs via ADR-260 imports; Linux: clone/unshare/seccomp syscalls | — | **M** (B3, B4) |
| `xax_result` | `service` result tables | — | needs session tables first | — | **M** |
| warm server | `warm.py` (Linux fork server) | not needed: 12.7 ms cold start | none | benchmark | not ported (measured unnecessary) |
| audit log on stderr | `logging` | none | none | stderr is empty in tests | **M** (no logging yet; stdout purity holds) |

### Blockers (exact, verified on this host)

- **B1. No native XAX compiler on Windows hosts.** The only native compiler is `compiler/bootstrap/seed/xaxc-linux-x86_64`,
  a static Linux ELF (ADR-286). This host has no Linux (no WSL, no containers, no VM). On Windows, XAX itself is
  Python. A native server here could reach construct/verify/build only by starting Python, which this rewrite
  forbids. The seven tools therefore report `unsupported`.
- **B2. The native compiler's command set is not a service.** `xaxc` offers `lower`, `build`, `verify`, `inspect`,
  `resolve`, `edit` and `resolve-trusted` (`xax_selfhost_driver.COMMANDS`), on files and with exit status only. It has
  no `construct` (carrier decoding), no bounded workspace queries, no generation/root-checked transactions, and
  no structured diagnostics on stdout. A native MCP server needs a versioned request/response protocol for those
  (upstream work in `MrxSiN/XAX`, kept independent of MCP).
- **B3. Linux sandbox and Linux build of this server are untested here.** The same program can target
  `linux-x86_64` by swapping the 8 kernel32 imports for `linux.read`/`linux.write`/`mmap`/`exit_group` and argv
  for `linux.startup.*`. That work is not done, because nothing could execute it on this host.
- **B4. Windows sandbox primitives.** ADR-260 lets a carrier declare any `win64-c` import, so CreateProcessW,
  CreateAppContainerProfile, job objects and SetNamedSecurityInfoW are reachable. The structures they need
  (SECURITY_CAPABILITIES, STARTUPINFOEX attribute lists) have to be laid out by hand in heap views. Not started.

### XAX backend facts found while building (reported for upstream)

- Win64 register-resident lowering takes at most **4 machine arguments** and **1 machine return** per function.
  Beyond that, a function falls to the frame lowering, which does not know the extents of heap-view parameters and
  raises `KeyError` instead of a diagnostic (`xax_x86_64._compile_function`, `pointer_extents[...]`). Every helper
  here therefore keeps to four arguments (views merged, spans packed as `start | end << 32`).
- On `0876b59`, a branch on a byte predicate of three or more operations (an OR of `c == k` tests, or
  `(c - 48) <u 10` compared to zero) fails with `XAX.NATIVE.VALUE`: a table read replaces the predicate, but the
  fused `cmp+jcc` still reads its operands. Main fixed this in ADR-284. The store avoids the pattern (compare
  chains) and is byte-identical under both revisions.
- The verifier tracks one memory-effect chain per heap view (`MEMORY-EFFECT-PROVENANCE`). A process entry may take
  several memory-effect parameters, one per view it allocates.

## Next steps

1. Upstream (`MrxSiN/XAX`): a versioned native compiler service (`xaxc serve`: length-prefixed typed requests for
   construct/open/verify/query/edit/build on stdin/stdout, structured diagnostics), first on Linux x86-64, where the
   native compiler exists.
2. Here: a `linux-x86_64` build of this program (B3), then a session/handle table backed by OS randomness, then
   proxying the compiler tools to that service.
3. Native sandbox: on Linux, clone with new namespaces, a seccomp filter matching `_sandbox_exec.py`, rlimits; on
   Windows, the LPAC AppContainer and job object of `_sandbox_win.py`. Both fail closed.
4. Maintain the server's own store through workspace transactions from generation 0, as upstream's R6
   applications are maintained.

## Migrating from the Python server

Not yet: the native server cannot construct, build or run programs. Keep the Python `xax-mcp` as the configured
server. The native binary is useful today as a protocol-conformance and startup-cost reference.
