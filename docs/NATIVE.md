# Native XAX server (`xax-mcp-native`)

Status: **0.7.0, native protocol layer complete; compiler-backed tools a host-granted prototype; Windows execution a
measured prototype** (2026-10-20). The MCP protocol layer is an XAX program: a verified canonical store that XAX builds
into a Windows x86-64 PE32+ executable. The deployed server starts no Python, no MCP SDK, and no shell. Five tools
(`xax_workspace`, `xax_query`, `xax_transaction`, `xax_build`, `xax_execute`) are a **PROTOTYPE** over a host-granted
native XAX compiler (`XAX_MCP_COMPILER`/`XAX_MCP_WORK`/`XAX_MCP_STORE`): they fail closed with `denied_capability` when
the host grants no compiler. `xax_execute` also needs `--allow-execute` and a second native XAX program,
`xax-mcp-sandbox.exe`, installed beside the server. `xax_construct` and `xax_result` are **UNIMPLEMENTED natively** and
fail closed. The Python 0.5.x server has been removed from the deployed path.

The prototype was exercised end to end on 2026-10-19 and 2026-10-20: describe the seed store, resolve and build it (a
1536-byte PE plus a 268-byte provenance object), apply a 78-byte `XAXEDIT1` constant mutation with the compiler's native
`edit` command, observe the new root, then run the edited artifact under OS confinement and read back its exit code,
wall time and captured output. Raw results: `docs/evidence/native-windows-x86_64-chain-f79b532.json` and
`docs/evidence/native-windows-x86_64-sandbox-f79b532.json`. The compiler used was a local XAX-built prototype outside
the pinned tree; committing a reproducible native compiler is still upstream work.

Evidence terms follow [EVIDENCE.md](EVIDENCE.md): *implemented* (in the store), *compiled* (XAX built it), *executed*
(ran), *integration-tested* (a test drove it over STDIO), *benchmarked* (raw samples recorded). The Windows confinement
in `xax-mcp-sandbox` is *measured* behaviorally (the process token is an AppContainer token, an outside write is
refused, a sleeping artifact is killed) but it has not been reviewed by anyone else; the evidence file lists what it
does **not** claim.

## What is XAX and what is not

```text
MCP client ──newline-delimited JSON-RPC over STDIO──► xax-mcp-native.exe  (XAX-generated x86-64 machine code)
                                                      ├─ STDIO framing, 4 MiB line limit, resync after oversize lines
                                                      ├─ RFC 8259 JSON validation with strict UTF-8, depth limit 64
                                                      ├─ JSON-RPC 2.0 envelope checks and error codes
                                                      ├─ MCP initialize/ping/tools/list/tools/call, notifications
                                                      ├─ tool dispatch, host rights from the command line
                                                      ├─ host-granted native compiler: spawn resolve/build/edit
                                                      ├─ sandbox: _spawnv xax-mcp-sandbox.exe <artifact> <work\exec>
                                                      └─ kernel32 + msvcrt: ReadFile WriteFile VirtualAlloc
                                                         VirtualFree ExitProcess GetCommandLineA
                                                         GetEnvironmentVariableA GetFileAttributesA
                                                         MoveFileExA lstrcpynA; _open _read _write _close
                                                         _lseek _spawnv
```

| Part | Form | Authority |
|---|---|---|
| Server program | `native/xax-mcp-native-gen0.xax`, a verified canonical XAX store (171 functions) | authoritative program |
| Sandbox program | `native/xax-mcp-sandbox-gen0.xax`, a second verified canonical store (8 functions) built by `compiler/integration/mcp/sandbox.py` in XAX | authoritative executor |
| Construction carrier | `native/construction_request.json` (`xax-construct-v1`) | transport, decoded once by `xax_construct` |
| `compiler/integration/mcp/{dsl,server,schemas}.py` (in XAX) | Python build tooling that writes the carrier | not source, not on the request path, not in this repository |
| `xax-mcp-native.exe` | PE32+ built from the store by `xax_build` (not committed; rebuilt from the store) | build product |

There is no textual XAX: the emitter in XAX (`compiler/integration/mcp/server.py`) writes typed graph nodes through
the carrier, the same way upstream's R6 applications (`xb64`, `xwc`, `xcksum`) were constructed. Upstream's own
compiler stores are built by Python builders in the same way. None of that tooling ships here: this repository holds
the carriers, the canonical stores, the evidence and the docs.

## Build

The build tooling lives in XAX at `compiler/integration/mcp`; nothing is built from this repository's contents.

```bash
git -C ../XAX checkout 4c3e60bef96c56162003838b36d6756295b1de41
python ../XAX/compiler/integration/mcp/server.py  ../XAX/compiler/src native   # server store + xax-mcp-native.exe
python ../XAX/compiler/integration/mcp/sandbox.py ../XAX/compiler/src native  # executor store + xax-mcp-sandbox.exe
```

This writes `construction_request.json`, `sandbox_request.json`, both stores and both executables. The stores and
requests are committed and checked byte for byte by `compiler/integration/mcp/tests/test_native_stdio.py` in XAX;
each PE is rebuilt deterministically from its committed store. `xax-mcp-sandbox.exe` must end up in the same
directory as `xax-mcp-native.exe` (the server derives its own directory with `GetModuleFileNameA`); without it
`xax_execute` answers `sandbox_unavailable`. The XAX pin is `4c3e60bef96c56162003838b36d6756295b1de41`, the first
commit that carries the tooling; its `compiler/src` is byte-identical to `f79b532fd4651ba808676d02f4b038e2cc271e6a`
(XAX `main`, 2026-10-19; host contract `xax-host-contract-v1` r10; toolchain fingerprint
`0ab800baf79464895bceeb0ccdaa13f4b8d1969fc627644f01e447575731f5d9`).

Build identity for this revision (new evidence, not a rewrite of older files):

| Field | Value |
|---|---|
| Server store root | `baec162e4bfb177fff18c3d36efdbd6e2ad0a0dec6cb412874fcbd18c12dd442` |
| Server release request | `9c3d4d22496286e8ff7c8ea0255ad404227509c5af58e662015b395a8d2c2e05` |
| Server store bytes / SHA-256 | 1 020 614 / `bbe28c1e5568abf40cb2d38a354f4dcbaae09b231abeb04f87674d5f1a70e25f` |
| Server artifact bytes / SHA-256 | 318 464 / `0493e7964deacf47c257850cdbd513aceae09bd9211776caf2b810ff01fd0521` |
| Server functions | 171 |
| Sandbox store root | `7ef7099d5358bf022715faff1ef26387c1486c554ed2f7d9145bd9d8953ef8b6` |
| Sandbox store bytes / SHA-256 | 74 434 / `588f57c0fa69eb175b6e06e88c73977292d42c06dfc5b814ec48cc5710bab2b8` |
| Sandbox artifact bytes / SHA-256 | 25 600 / `6d563e0f23e4f402d55c82b200d42bce91c41c98aab101267e67d3645a1d37e2` |
| Sandbox functions | 8 |

The server store changed relative to the earlier `f79b532` build because the tool schemas were narrowed to the
implemented prototype, the compiler tools gained fail-closed checks, and `xax_execute` was wired to the executor. The
old evidence files for `f79b532` are unchanged; the identities above are recorded in
`native-windows-x86_64-build-f79b532-r3.json` and `native-windows-x86_64-sandbox-f79b532.json`.

### Host-granted native compiler

The five compiler-backed tools read three environment variables. All three must be present and non-empty; otherwise
they answer `denied_capability` and do nothing:

| Variable | Meaning |
|---|---|
| `XAX_MCP_COMPILER` | absolute path to a native XAX compiler executable (`xaxc`) |
| `XAX_MCP_WORK` | a writable directory; the server keeps `current.xax`, `snapshot.xax`, `artifact.exe`, `artifact.prov` and the transaction record there |
| `XAX_MCP_STORE` | absolute path to a canonical build-request store used until the work directory has a `current.xax` |

The server only spawns that executable (`_spawnv`) and reads the files it writes. It does not import, embed, or start
Python. `native/xax-mcp-seed.xax` is a committed form-2 build-request seed (root
`572f683e22d94efe404b5b73f59b85edfd3e6ccbd2614342fdf58fe66cb61587`, 1852 bytes); `compiler/integration/mcp/chain.py` in XAX is build/test
tooling that authors an `XAXEDIT1` carrier with the pinned XAX Python tooling.

### Sandboxed execution (`xax_execute`)

`xax_execute` has no arguments yet: it resolves and builds the current store with the host-granted compiler, then runs
that artifact and returns `exit_code`, `duration_ms`, `flags` (bit 0 timeout, bit 2 output truncated) and the artifact's
stdout/stderr as hex. Any argument is refused with `invalid_request` rather than silently ignored.

The run happens in `xax-mcp-sandbox.exe`, a **separate XAX program** built from `compiler/integration/mcp/sandbox.py` in XAX with the same
compiler. The server spawns it with a fixed three-word argv (`<artifact> <work>\exec`) through `_spawnv`, so no shell
parse and no caller-controlled argument reaches the executor. The executor:

1. creates a capability-less `AppContainer` profile (`CreateAppContainerProfile`, falling back to
   `DeriveAppContainerSidFromAppContainerName`) and exits 51 rather than running unconfined if it cannot;
2. grants that SID read and execute (`0xA0000000`) on the run directory only;
3. starts the artifact **suspended** with `EXTENDED_STARTUPINFO_PRESENT`, a `SECURITY_CAPABILITIES` attribute,
   `CHILD_PROCESS_RESTRICTED` and an explicit inheritable-handle list (NUL, stdout, stderr);
4. assigns it to a job object (5 s CPU, one process, 256 MiB, kill-on-close), confirms `IsProcessInJob` and exits 41
   if the process is not confined, then resumes the only thread;
5. waits 10 s, then `TerminateJobObject` and reports `FLAG_TIMEOUT`;
6. drains both pipes into 1 MiB buffers and sets `FLAG_TRUNCATED` when more was available;
7. writes `sandbox-out.bin`, `sandbox-err.bin` and a 16-byte `sandbox-result.bin` (exit code, flags, wall ms).

Measured on 2026-10-20 (details and controls in `docs/evidence/native-windows-x86_64-sandbox-f79b532.json`): a
`GetTokenInformation(TokenIsAppContainer)` probe answers `1` inside and `0` outside; a write to a path the host user
can freely create is refused inside and succeeds outside; `Sleep(60000)` is killed at the 10 s wall limit with
`FLAG_TIMEOUT`; a talker artifact's 14 stdout bytes and 5 stderr bytes come back intact with exit code 7. The seed
artifact run through MCP answered `exit_code 40, flags 0, duration_ms 16`.

The same confinement was then reproduced on a clean GitHub-hosted `windows-2022` runner (ci run 39291600926): both
committed stores matched byte for byte and the seed artifact exited 40 with flags 0
(`docs/evidence/native-windows-ci-sandbox-0137179.json`). That run also found that a CRLF-normalizing checkout had
rewritten `native/sandbox_request.json`; `.gitattributes` now keeps every `native/*.json` byte exact.

## Client setup

```json
{"mcpServers": {"xax-native": {"type": "stdio", "command": "C:/path/to/xax-mcp-native.exe", "args": ["--read-only"]}}}
```

Accepted flags: `--allow-execute`, `--read-only`, `--deny RIGHT`, `--deny=RIGHT`, and `--no-warm-server` (a no-op).
Any other argument, or any quote inside an argument, makes the server write one line to stderr and exit with status
2 **before reading stdin**. Running with authority the host did not intend would be worse than not starting.

## Protocol behaviour

`compiler/integration/mcp/tests/test_native_stdio.py` in XAX drives the real executable. It covers the four handshake versions, unknown offers,
ping, `tools/list` (identical to `compiler/integration/mcp/schemas.py`), unknown methods and tools, malformed and oversized lines,
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
  check comes first; the five compiler-backed tools then require the host compiler grant, and the remaining two
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
| `xax_execute` round trip (build + confined run) | 148 ms wall for a fresh server process; 16 ms reported sandbox duration |
| peak working set | 9.14 MB |

Build and transaction latency is almost entirely the native compiler child process; the server's own handling is
sub-millisecond. `xax_execute` adds one more `resolve`+`build` (two compiler spawns) and then one confined child
process, whose own wall time is reported separately in `duration_ms`.

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
| tools/list, schemas | literal from `compiler/integration/mcp/schemas.py` at construction time | none | identical to the schema module | **N** |
| tool dispatch, error taxonomy | `handle` | none | every tool | **N** |
| argument schema validation | `xax_capabilities` only | none | extra-property cases | **M** for 7 tools |
| host rights, launch flags | `parse_args`, fail closed | none | 7 flag sets, 8 rejected forms, tool arguments never grant | **N** |
| session handles | none yet | a randomness source (`BCryptGenRandom` through ADR-260 imports) | — | **M** |
| `xax_workspace`/`xax_query` | same store description (root + byte size) on both tool names | query kinds beyond `root` need a native query service | `test_native_compiler_chain_over_stdio` | **P** (B1, B2) |
| `xax_transaction` | hex `XAXEDIT1` record -> native `edit` -> replace `current.xax` | typed mutations, expected generation/root, verify/rollback | same test; record authored by `chain.py` in XAX | **P** (B1, B2) |
| `xax_construct` | — | native carrier decoding: no native `construct` command exists | — | **M** (B1, B2) |
| `xax_build` | native `resolve` then `build` of the current store; reports root, artifact bytes, provenance | artifact handles, entry selection, digest report, cache | same test | **P** (B1, B2) |
| `xax_execute`, sandboxed run | resolve+build, then `xax-mcp-sandbox.exe`: LPAC AppContainer + job object, pipes, wall/output limits | typed input/output layouts, argv, per-call limits, artifact handles; Linux clone/unshare/seccomp | `test_native_compiler_chain_over_stdio`, `test_native_sandbox_launcher_runs_artifact_confined` | **P** on Windows (B1, B3) |
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
- **B4. Windows sandbox: prototype, not a hardened boundary.** ADR-260 lets a carrier declare any `win64-c` import, so
  `CreateProcessW`, `CreateAppContainerProfile`, job objects and `SetNamedSecurityInfoW` are reachable; `compiler/integration/mcp/sandbox.py`
  lays out `SECURITY_CAPABILITIES`, `STARTUPINFOEX` attribute lists, `JOBOBJECT_EXTENDED_LIMIT_INFORMATION` and
  `EXPLICIT_ACCESS_W` by hand in heap views. Measured on this host (AppContainer token `1` inside / `0` outside, an
  outside write refused, a 60 s sleep killed at 10 s, exact pipe capture), so this is no longer "not started". It is
  still a prototype: Windows only, no independent security review, no fuzzing, the run-directory ACL grant is repeated
  on every run, and artifacts cannot use the network at all. Linux (B3) and the typed I/O contract remain open.

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
3. Native sandbox hardening: on Linux, clone with new namespaces and a seccomp filter matching the retired Python
   sandbox; on Windows, add the typed I/O contract (input/output layouts, argv, per-call limits) on top of the existing
   LPAC AppContainer and job object, and get the executor reviewed as a security boundary.
4. Maintain the server's own store through workspace transactions from generation 0, as upstream's R6 applications
   are maintained.

## Retired Python server

The 0.5.x Python adapter (`src/xax_mcp`) is removed from the tree. Its documentation is marked historical:
[ARCHITECTURE.md](ARCHITECTURE.md), [TOOLS.md](TOOLS.md), [SECURITY.md](SECURITY.md),
[PERFORMANCE.md](PERFORMANCE.md), [HOSTS.md](HOSTS.md). Git history retains the implementation for the porting work.
No Python server, sidecar, or fallback is launched by `xax-mcp-native.exe`.
