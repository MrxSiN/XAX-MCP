# Windows readiness — 2026-10-27

**Mission status: incomplete. Release gate: failing.** This is a new audit, not a rewrite of earlier evidence.

## Checkouts and authority

XAX-MCP was an exported tree without `.git`. Its contents matched remote `main`
`f7bf817073df6788c357426fad93bd2cda13b979`; Git metadata and upstream tracking were restored without changing
those files. XAX's initial branch was `feat/native-construct` at `2c020a72c5c7d0907cfbef31dbc8845cbf1a38f6`.
Its tracked contents and 229 untracked additions matched the corresponding files on current remote `main`.
The old working state was preserved with `git stash push --include-untracked`, named
`Preserve pre-sync Windows checkout 2026-10-27`. Local `main` was then fast-forwarded to
`fdc7312d60e12b6e784d920217f09df535090d55`. The stash and old branch were retained.

This sync does not repin the unchanged MCP server. Its embedded XAX identity remains
`3e9b0c2b3f88d2193caae72a5fe8eefa83d1995b`, host contract r10. Current XAX `compiler/src` differs from that pin.

The build document was read as task material. Its allowance for non-XAX implementation tooling does not override
the user's restriction. No interpreter-based compiler, Python bootstrap, SDK server or non-XAX application source
was introduced or run in this work. Git/PowerShell provided external OS and test orchestration. Existing upstream
Python/bootstrap/reference code and old MCP integration helpers were preserved; neither repository-wide migration
nor deletion of those dependencies is claimed.

## Executed native path

The recovered Windows XAX compiler is 11,864,576 bytes, SHA-256
`ff0355c5bf148bc79cf463748a285c3f982b6c8e47faf8d2d25bd3571b2ad638`. Its saved build record identifies canonical
source root `2b8136a8e052ccefd88f31b5d906dc986a070f2ca6e370668b73b17783ed3d17`, source SHA-256
`35d08af4641143eae2169a9e9972db9a183cb13fd4a03d7c6e6b1d685164adb6`. Its historical bootstrap used Python;
the audit reused its existing native executable. It is neither shipped by XAX-MCP nor certified as the server pin.

It successfully verified, resolved and built the seed and built the server snapshot. The resulting server is
359,424 bytes, SHA-256 `a87fdd10042b6717d098af7e1014e612f460dabbe725320eeb781c388fd2a2b9`.
This repeats the historically documented nonidentical native build; the committed server executable was retained.
Building the current upstream Windows driver store returned exit 2, a decline. No compiler self-build is claimed.

Over actual MCP STDIO, the unchanged committed server and recovered compiler performed:

1. Initialization at protocol `2025-11-25`, eight-tool discovery, capability reporting and root query.
2. Native resolve/build and sandbox execution of the seed, returning exit result 40.
3. Seven exact-root transactions inserting constants 7, 3 and 5, add/multiply/subtract nodes, and a changed
   `ExitProcess` operand. Each intermediate store was separately verified by the native compiler.
4. Native build and sandbox execution of the new root, returning 136; another execution also returned 136.
5. A rejected stale record with the final root retained, read-only permission checks, an execution-grant denial,
   and distinct-root checks with two separately configured work directories.

The arithmetic result is an exit-status integer, not a typed runtime output payload. The final canonical graph,
seven mutation carriers, executable, provenance and replay requests are in
[`examples/native-arithmetic`](../examples/native-arithmetic/README.md). Raw observations, including failures,
are in [the audit evidence](evidence/native-windows-x86_64-transaction-construction-20261027.json).

## Reproduced release failures

### Candidate publication precedes verification

`tests/security/invalid-add-operand.edit` expects the seed root and inserts a wrapping add of a bits32 constant
and parameter 0, which is an effect token. `xax_transaction` returned `ok: true`, generation 1, and published root
`7bec5eaef6572a53e32165274ec50041520568e3f325d28d1f139975ae6814a4`. Native `verify` then rejected the current
store with exit 1 and `XAX.STRUCT.OP_TYPE / GRAPH-OP-TYPE`. The exact native diagnostic is preserved beside
the record. This was an isolated scratch workspace. The invalid candidate was never built or executed.

The adapter must stage a candidate, run the native verifier successfully, recheck the expected current root,
and only then atomically publish it. Rejection, decline, timeout or I/O failure must retain the old store and
generation and remove scratch artifacts. Merely having an expected-root field in `XAXEDIT1` is insufficient.

### Schemas are not enforced consistently

With compiler grants, `xax_query({"path":"../../private"})` returned the current seed's root and byte count;
`xax_build({"command":"cmd.exe"})` built the current seed. Neither property influenced the selected path or
launched the named command. Both violate `additionalProperties: false` and must return `invalid_request`
before invoking the compiler. Fix workspace, query and build consistently and test all unknown properties.

## Remaining implementation gates

| Gate | Present state | Required next action |
|---|---|---|
| Native-only Windows construction | Decoder missing; `xax_construct` denies the request | Upstream commits the verified decoder store, a native Windows seed and a reproducible native-only build recipe |
| Verified atomic commit | Invalid candidate published in the test above | Add the XAX-native candidate verify/recheck/publish sequence and failure cleanup |
| Complete schema validation | Query/build accept forbidden fields | Fix native dispatch before invoking compiler commands |
| Reproducible toolchain | Recovered compiler is not the embedded pin; current driver declines | Establish a versioned native Windows seed/contract and verify source/artifact identities |
| Workspace/query service | Root and byte count only | Consume a host-independent upstream bounded query and transactional workspace API |
| Session/artifact handles | Fixed `ws_0`; host chooses work directory | Add process/session ownership, generations, opaque handles and checked artifact provenance |
| Runtime I/O/results | Exit status and bounded byte captures only | Add a verified entry ABI and bounded typed input/result transport |
| Execution supervision | Existing AppContainer/job prototype | Recheck process-tree, quota, output saturation, cancellation and cleanup behavior; retain fail-closed launch |
| Current MCP | Legacy handshake through 2025-11-25 | Implement and test the 2026-07-28 stateless/per-request capability protocol in XAX |
| Current host adoption | Historical Codex/Claude configuration examples | Test current host versions and independent current SDK interoperability after protocol work |
| XAX-only repositories | Upstream still has non-XAX bootstrap/test implementations | Continue the upstream native migration without deleting the only usable bootstrap or adding another-language replacement |

The smallest upstream requirements are tracked in XAX's
`docs/proposals/native-windows-workspace.md`. No MCP protocol or application implementation is added upstream.

The official references reviewed were the [2025-11-25 STDIO transport](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports),
[tool schema/results](https://modelcontextprotocol.io/specification/2025-11-25/server/tools),
[current 2026-07-28 specification](https://modelcontextprotocol.io/specification/2026-07-28) and
[maintained SDK catalogue](https://modelcontextprotocol.io/docs/2026-07-28/sdk). No SDK is a server dependency.

## CI scope

The revised workflow checks native artifact identities, a 15-response STDIO smoke fixture and confined execution
of the committed arithmetic executable. It has no upstream source checkout, Python setup, source emitter or SDK
installation. It does not recompile the program or close the failing security gates. Earlier Python-suite and
SDK-client counts remain historical observations, not the current CI's test count.

The independent smoke workflow subsequently passed on the configured `windows-2022` GitHub runner in
[run 40443571319](https://github.com/MrxSiN/XAX-MCP/actions/runs/40443571319) at commit `7eb687d`.
[The recorded job steps](evidence/native-windows-ci-smoke-40443571319.json) confirm artifact hashes, STDIO
replay and confined exit result 136. The release failures above remain unresolved.
