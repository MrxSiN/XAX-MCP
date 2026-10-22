# Native XAX server (`xax-mcp-native`)

Status: **0.8.0, native protocol layer complete; compiler- and decoder-backed tools a host-granted prototype; Windows
execution a measured prototype** (2026-10-22, XAX `3e9b0c2`). The MCP protocol layer is an XAX program: a verified
canonical store that XAX builds into a Windows x86-64 PE32+ executable. The deployed server starts no Python, no MCP
SDK, and no shell. Five
tools (`xax_workspace`, `xax_query`, `xax_transaction`, `xax_build`, `xax_execute`) are a **PROTOTYPE** over a
host-granted native XAX compiler (`XAX_MCP_COMPILER`/`XAX_MCP_WORK`/`XAX_MCP_STORE`): they fail closed with
`denied_capability` when the host grants no compiler. `xax_execute` also needs `--allow-execute` and a second native XAX
program, `xax-mcp-sandbox.exe`, installed beside the server. `xax_construct` is a **PROTOTYPE** over a host-granted
native carrier decoder (`XAX_MCP_CONSTRUCT`/`XAX_MCP_WORK`): the decoder is the `construct <carrier> <store>` command
from `compiler/integration/construct` in XAX. `xax_result` is **UNIMPLEMENTED natively** and fails closed. The Python
0.5.x server has been removed from the deployed path.

The prototype was exercised end to end on 2026-10-19, 2026-10-20 and 2026-10-22: describe the seed store, resolve
and build it (a 1536-byte PE plus a 268-byte provenance object), apply a 78-byte `XAXEDIT1` constant mutation with the
compiler's native `edit` command, observe the new root, then run the edited artifact under OS confinement and read back
its exit code, wall time and captured output. Raw results: `docs/evidence/native-windows-x86_64-chain-f79b532.json`,
`docs/evidence/native-windows-x86_64-chain-3e9b0c2.json` (the 0.8.0 re-run) and
`docs/evidence/native-windows-x86_64-sandbox-f79b532.json`. On 2026-10-22 the construct tool was executed over STDIO:
`native/sandbox_request.json` produced the committed `native/xax-mcp-sandbox-gen0.xax` byte for byte (74 434 B, root
`7ef7099d...`) through the native decoder, and became the work directory's current store; the compiler, sandbox and
decoder used were local XAX-built prototypes outside the pinned tree, so committing reproducible native builds is
still upstream work.

On 2026-10-22 the pin moved from `0a0b1c4` (compiler `f79b532`) to XAX `main` `3e9b0c2`. Both committed stores were
re-decoded from their carriers by the native decoder and matched byte for byte, and the server store was rebuilt
(1 103 602 B, root `18ceecd9...`); the executor store is byte-identical to the 0.7.0 one. Python was not involved in
either check; it is the external test client and the offline carrier author only, and the author is now blocker B5.

On the same day the chain was re-run at 0.8.0 against a native compiler rebuilt from the pinned tree
(`compiler/integration/windows_helpers/driver.xax`: 11 890 688 B, SHA-256 `110a76...`): 45 passed, 0 skipped, and the
edited artifact executed with exit 41 and empty output. That closes the 0.7.0 gap in which the chain test was skipped
for lack of a compiler; the compiler is still a local build, not a committed one (B1). Raw results:
`docs/evidence/native-windows-x86_64-chain-3e9b0c2.json`.

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
                                                      ├─ decoder: _spawnv xax-construct.exe <carrier> <store>
                                                      ├─ sandbox: _spawnv xax-mcp-sandbox.exe <artifact> <work\exec>
                                                      └─ kernel32 + msvcrt: ReadFile WriteFile VirtualAlloc
                                                         VirtualFree ExitProcess GetCommandLineA
                                                         GetEnvironmentVariableA GetFileAttributesA
                                                         MoveFileExA lstrcpynA; _open _read _write _close
                                                         _lseek _spawnv
```

| Part | Form | Authority |
|---|---|---|
| Server program | `native/xax-mcp-native-gen0.xax`, a verified canonical XAX store (181 functions) | authoritative program |
| Sandbox program | `native/xax-mcp-sandbox-gen0.xax`, a second verified canonical store (8 functions) built by `compiler/integration/mcp/sandbox.py` in XAX | authoritative executor |
| Carrier decoder | the `construct <carrier> <store>` program from `compiler/integration/construct` in XAX (a separate native XAX program, host-granted as `XAX_MCP_CONSTRUCT`) | authoritative decoder |
| Construction carrier | `native/construction_request.json` (`xax-construct-v1`) | transport, decoded once by the decoder; the server's own request |
| `compiler/integration/mcp/{dsl,server,schemas}.py` (in XAX) | Python build tooling that writes the carrier | not source, not on the request path, not in this repository |
| `xax-mcp-native.exe` | PE32+ built from the store by `xax_build` (not committed; rebuilt from the store) | build product |

There is no textual XAX: the emitter in XAX (`compiler/integration/mcp/server.py`) writes typed graph nodes through
the carrier, the same way upstream's R6 applications (`xb64`, `xwc`, `xcksum`) were constructed. Upstream's own
compiler stores are built by Python builders in the same way. None of that tooling ships here: this repository holds
the carriers, the canonical stores, the evidence and the docs.

## Build

The build tooling lives in XAX at `compiler/integration/mcp`; nothing is built from this repository's contents. The
first stage runs with no interpreter; the second needs a native Windows compiler, which the pinned tree does not
commit (B1).

```text
<decoder> <carrier> <store>                       # carrier -> verified store     (verified byte-identical here)
<xaxc>    resolve <request-store> <snapshot>      # build request -> resolved snapshot
<xaxc>    build <snapshot> <artifact> <prov>      # resolved request -> PE + provenance
```

The decoder is `construct <carrier> <store>`, built from `compiler/integration/construct` in XAX; the compiler is a
native `xaxc` that the server also drives (`resolve`, `build`, `edit`). On 2026-10-22 the native decoder reproduced
both committed stores from the committed carriers byte for byte
(`docs/evidence/native-windows-x86_64-build-3e9b0c2.json`). The 0.8.0 PEs were produced by the pinned XAX build
tooling during carrier re-emission, because no reproducible native Windows compiler exists on this host to run the
`resolve`/`build` stage (B1); the stores they were built from are the decoded, byte-verified ones above. A native
compiler rebuilt at `3e9b0c2` does run `resolve`, `build` and `edit` on a build-request store, which is what the
chain test drives; it cannot rebuild the committed *program* stores from this repository, because those are the
decoder's output, not build requests, and the author's request stores are not committed.

The two requests, both stores and the seed are committed and checked byte for byte by
`compiler/integration/mcp/tests/test_native_stdio.py` in XAX; each PE is rebuilt deterministically from its committed
store. `xax-mcp-sandbox.exe` must end up in the same directory as `xax-mcp-native.exe` (the server derives its own
directory with `GetModuleFileNameA`); without it `xax_execute` answers `sandbox_unavailable`.

XAX pin: `3e9b0c2b3f88d2193caae72a5fe8eefa83d1995b` (XAX `main`, 2026-10-22; host contract `xax-host-contract-v1` r10;
toolchain fingerprint `ba009daa933c33ba124f2dc2fcb7a09995553b867bc68289555871b2f47eb740`, 125 files). The authoring
tooling and the tests are at `6b6c35939ff02c365a58c3534cf1b75a2281d393` on `integration/mcp-on-main-3e9b0c2`, which is
`3e9b0c2` plus the MCP commits; its `compiler/src` is byte-identical to `3e9b0c2` (`git diff 3e9b0c2 6b6c359 --
compiler/src` is empty), which is why the store embeds `3e9b0c2` as its pin.

Build identity for this revision (new evidence, not a rewrite of older files):

| Field | Value |
|---|---|
| Server store root | `18ceecd9fe284e16919bb5f0f40bdf52cf5a90407ad007d218f30d3235024b07` |
| Server release request | `06d1330bbe87630c815c568b14899cc98b2876e2ef40f25e1b4b8c2efc6d0110` |
| Server store bytes / SHA-256 | 1 103 602 / `0a698799883375955a421c0f0f5526862e941cc01f6e2738749a6fc61f0bdcab` |
| Server artifact bytes / SHA-256 | 359 424 / `9f6e272bbbc938d3493a98b7c68409de31a09ffc4cc958bb41be7447b65c076a` |
| Server functions / store objects | 181 / 3 621 |
| Sandbox store root | `7ef7099d5358bf022715faff1ef26387c1486c554ed2f7d9145bd9d8953ef8b6` |
| Sandbox store bytes / SHA-256 | 74 434 / `588f57c0fa69eb175b6e06e88c73977292d42c06dfc5b814ec48cc5710bab2b8` |
| Sandbox artifact bytes / SHA-256 | 25 600 / `6d563e0f23e4f402d55c82b200d42bce91c41c98aab101267e67d3645a1d37e2` |
| Sandbox functions / store objects | 8 / 271 |
| Seed store root / bytes / SHA-256 | `572f683e22d94efe404b5b73f59b85edfd3e6ccbd2614342fdf58fe66cb61587` / 1 852 / `25db5e19257e81e99a79e1b0311b65c8f534507ced0607ad4c5e2f0a81821532` |

The server store changed relative to 0.7.0 (pin `0a0b1c4` / compiler `f79b532`: 1 103 601 B,
root `9493014f...`, artifact SHA-256 `2c72ea0f...`) because the pin moved to compiler `3e9b0c2` and the embedded
version string became `0.8.0+native`. One byte and the whole root changed; the function count is unchanged (181).
The executor store, its artifact and the seed are byte-identical to 0.7.0: `sandbox.py`'s program does not embed
either string. The native decoder reproduced both new stores from the committed carriers, so the same bytes are both
the author's output and the decoder's output. The old evidence files are unchanged; the identities above are recorded
in `native-windows-x86_64-build-3e9b0c2.json`.

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
`572f683e22d94efe404b5b73f59b85edfd3e6ccbd2614342fdf58fe66cb61587`, 1852 bytes);
`compiler/integration/mcp/chain.py` in XAX authors the `XAXEDIT1` carrier used by the chain test. That author is
offline Python test tooling (B5), never on the request path.

### Host-granted carrier decoder (`xax_construct`)

`xax_construct` reads two environment variables of its own. Both must be present and non-empty, or the call answers
`denied_capability` before writing anything. It does not need the compiler trio: constructing a new store is a
different capability from driving the compiler over an existing one.

| Variable | Meaning |
|---|---|
| `XAX_MCP_CONSTRUCT` | absolute path to the native carrier decoder (`construct <carrier> <store>`, built from `compiler/integration/construct` in XAX) |
| `XAX_MCP_WORK` | a writable directory; the server writes `construct-request.json` there, the decoder writes `constructed.xax`, and a successful call replaces `current.xax` |

The tool copies the `request` value's JSON text verbatim (it never re-serializes or interprets it), writes it to
`<work>\construct-request.json`, deletes any stale `<work>\constructed.xax`, and spawns the decoder with a fixed
three-word argv (`<decoder> <work>\construct-request.json <work>\constructed.xax`) through `_spawnv`. The store
becomes current only after the decoder exits 0 and the file is at least 39 bytes; a refusal leaves `current.xax`
exactly as it was. The carrier is bounded by the 1 MiB `arguments` limit, so the decoder sees one bounded file.
Paths must not contain spaces: the native decoder splits its command line on spaces, so such a work directory fails
closed at open rather than being misread.

Executed on 2026-10-22: `native/sandbox_request.json` (66 322 bytes) produced `native/xax-mcp-sandbox-gen0.xax` byte
for byte (74 434 B, SHA-256 `588f57c0...`, root `7ef7099d...`) through a decoder built at XAX `feat/native-construct`
`486fa9d`; a carrier with an unknown `format` answered `construct_rejected` and left the current store unchanged
(`docs/evidence/native-windows-x86_64-construct-0a0b1c4.json`). After the pin moved to `3e9b0c2`, the same decoder
reproduced **both** carriers again — the 1 103 602 B server store (`0a698799...`) and the unchanged executor store
(`588f57c0...`) — with no Python involved (`docs/evidence/native-windows-x86_64-build-3e9b0c2.json`).

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
servers, and the official `mcp.Client` SDK. The gated `test_native_construct_over_stdio` drives the decoder path
(carrier → committed store byte for byte, refusals and missing grants).

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
  check comes first; the five compiler-backed tools then require the host compiler grant, `xax_construct` requires the
  decoder grant, and `xax_result` answers `unsupported`.
- **Key matching** is on raw JSON text, so a key spelled with escapes (`"\u0069d"`) is not recognized as `id`.
  Duplicate keys: the last one wins, as in `json.loads`.

## Measurements

Same host as the 6885f89 evidence: AMD Ryzen 9 5900HS, 16 logical CPUs, Windows 11 Pro 26300. 15 launches, 50
round trips per call per launch; medians shown. Raw samples:
`docs/evidence/native-windows-x86_64-protocol-f79b532.json`. These samples are from the 0.6.0 artifact; the protocol
code is unchanged in 0.7.0 and 0.8.0, and the current artifact is the one in the build table above.

| Measure | Native XAX 0.6.0 |
|---|---|
| process start to initialize response | 11.5 ms |
| ping round trip | 17.5 µs |
| tools/list round trip | 97.1 µs |
| xax_capabilities round trip | 43.0 µs |
| peak working set | 8.16 MB |

### Compiler-backed chain (0.7.0)

Measured at 0.7.0; the 0.8.0 store differs only in its embedded pin and version string, and the chain code is
unchanged. One server process, 10 `xax_query` calls, 5 `xax_build` calls (each two compiler spawns), then 5
`xax_transaction` calls (each one compiler spawn) on successive constants 41..45. Medians of the raw samples; details
in `docs/evidence/native-windows-x86_64-chain-f79b532.json`.

Re-executed at 0.8.0 with the rebuilt native compiler on 2026-10-22: the same single chain produced byte-identical
step values (the same 268-byte provenance object and transaction root `8c01664c...`), `xax_execute` exited 41 in
16 ms, and the gated chain test passed in 26.63 s. That run is `docs/evidence/native-windows-x86_64-chain-3e9b0c2.json`;
the medians below are still the 0.7.0 samples, not a new timing series.

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
| `xax_construct` | inline carrier text -> `<work>\construct-request.json` -> `_spawnv <decoder> <carrier> <store>` -> replace `current.xax`; reports root and bytes | >1 MiB carriers (handles), candidate stores, rollback, a Linux decoder | `test_native_construct_over_stdio` | **P** (B1, B2) |
| `xax_build` | native `resolve` then `build` of the current store; reports root, artifact bytes, provenance | artifact handles, entry selection, digest report, cache | same test | **P** (B1, B2) |
| `xax_execute`, sandboxed run | resolve+build, then `xax-mcp-sandbox.exe`: LPAC AppContainer + job object, pipes, wall/output limits | typed input/output layouts, argv, per-call limits, artifact handles; Linux clone/unshare/seccomp | `test_native_compiler_chain_over_stdio`, `test_native_sandbox_launcher_runs_artifact_confined` | **P** on Windows (B1, B3) |
| `xax_result` | — | needs session tables first | — | **M** |
| audit log on stderr | none | none | stderr is empty in tests | **M** (no logging yet; stdout purity holds) |

### Blockers (exact, verified on this host)

- **B1. No reproducible native XAX compiler or carrier decoder in the pinned Windows tree.** The only committed native
  compiler is `compiler/bootstrap/seed/xaxc-linux-x86_64`, a static Linux ELF (ADR-286). This host has no Linux (no
  WSL, no containers, no VM). On Windows, XAX itself is Python. The prototype therefore takes a compiler path and a
  decoder path from the host and fails closed when they are not granted; it does not embed an interpreter, and it
  cannot ship a program it cannot reproduce. The compiler used for the 0.7.0 measurements lived in an untracked
  `build/windows_helpers` directory of the previous checkout and did not survive the move to `3e9b0c2`; that is the
  blocker, observed directly. A fresh native compiler rebuilt from the pinned `driver.xax` on 2026-10-22 ran the whole
  chain (45 passed, 0 skipped, execute exit 41), so what is missing is reproduction and commitment in XAX, not
  capability. Committing reproducible native Windows builds of both programs is upstream work.
- **B2. The native compiler's command set is not a service.** `xaxc` offers `lower`, `build`, `verify`, `inspect`,
  `resolve`, `edit` and `resolve-trusted` (`xax_selfhost_driver.COMMANDS`), on files and with exit status only. The
  general driver has no `construct`: carrier decoding is a separate `construct <carrier> <store>` program with the
  same file/exit-status shape, not a driver command. There are no bounded workspace queries, no generation/root-checked
  transactions, and no structured diagnostics on stdout. The server consumes the file commands; a versioned
  request/response protocol for construct/open/query remains upstream work (kept independent of MCP).
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
- **B5. The carrier authors are Python.** `compiler/integration/mcp/{server,sandbox,seed,dsl,schemas}.py` walk a typed
  description and emit the `xax-construct-v1` carrier. They are offline build tooling: the carrier is committed, the
  native decoder turns it into the verified store, and nothing on the request path imports them. Rebuilding this
  repository therefore needs no Python, but *changing* what the server means still does. The smallest general
  replacement is an upstream native XAX carrier author (a verified program that emits a carrier from a typed
  description); until that exists, this is the one disclosed non-XAX dependency in the authoring loop. Decoding and
  checking every committed store therefore needs no Python. Rebuilding the PEs needs a native Windows `xaxc`, and
  producing that compiler reproducibly is B1 (the local bootstrap used on 2026-10-22 is disclosed). Changing the
  semantics still needs the Python authors until a native one replaces them.

### Local native programs

The carrier decoder is a local prototype outside the pinned tree,
`D:\GitHub\XAX\build\construct_cmd\construct.exe` (2 852 352 bytes, SHA-256
`a6bd67fddce407e348c23604434d536690f87e0cfe0e7a6c7c1f8a073dc4c94f`, built from XAX `feat/native-construct`
`486fa9d`). It implements `construct <carrier> <store>` and nothing else. It reproduced both committed stores at the
`3e9b0c2` pin in 0.38 s and 0.04 s, which is the byte-identity check recorded in
`docs/evidence/native-windows-x86_64-build-3e9b0c2.json`.

The compiler is the other local prototype. At the 0.7.0 pin it was
`D:\GitHub\XAX\build\windows_helpers\xaxc-windows.exe` (11 857 408 bytes, SHA-256 `e2b73064...`; 508 functions;
kernel32/msvcrt), and the 0.7.0 chain measurements were taken against exactly that executable. That directory was
never committed and is not in the `3e9b0c2` tree; on 2026-10-22 it was rebuilt from
`compiler/integration/windows_helpers/driver.xax` at the pin (30 655 635 B, SHA-256 `796c6bb9...`) over 1 201.9 s:
11 890 688 bytes, SHA-256 `110a76a2578f5f55777e6b0438b05642013e9587cae902ef3729229af8e5420e`, imports
kernel32/msvcrt only, commands `resolve`, `build`, `edit` (plus `lower`, `verify`, `inspect`, `resolve-trusted`). It
ran the full chain on 2026-10-22. It is likewise not committed. Neither program is a dependency of this repository, is
shipped, or proves a general construct/build/execute loop: they are the narrow path that B1/B2 must replace with
reproducible, versioned programs.

## Next steps

1. Upstream (`MrxSiN/XAX`): commit reproducible native Windows builds of the compiler and the carrier decoder for the
   pinned tree, then a versioned native compiler service (`xaxc serve`: length-prefixed typed requests for
   construct/open/verify/query/edit/build on stdin/stdout, structured diagnostics).
2. Upstream: replace the Python carrier authors with a native XAX carrier author so the authoring loop is XAX-only
   (B5). The carriers are already committed and verified, so this is authoring work, not a runtime dependency.
3. Here: grow the prototype behind the same tool names - bounded graph queries, expected-generation/root-checked
   transactions, artifact handles and `xax_result` - and add a `linux-x86_64` build of this program (B3).
4. Native sandbox hardening: on Linux, clone with new namespaces and a seccomp filter matching the retired Python
   sandbox; on Windows, add the typed I/O contract (input/output layouts, argv, per-call limits) on top of the existing
   LPAC AppContainer and job object, and get the executor reviewed as a security boundary.
5. Maintain the server's own store through workspace transactions from generation 0, as upstream's R6 applications
   are maintained.

## Retired Python server

The 0.5.x Python adapter (`src/xax_mcp`) is removed from the tree. Its documentation is marked historical:
[ARCHITECTURE.md](ARCHITECTURE.md), [TOOLS.md](TOOLS.md), [SECURITY.md](SECURITY.md),
[PERFORMANCE.md](PERFORMANCE.md), [HOSTS.md](HOSTS.md). Git history retains the implementation for the porting work.
No Python server, sidecar, or fallback is launched by `xax-mcp-native.exe`.
