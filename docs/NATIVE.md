# Native XAX server 0.10.0

Current server source is gen3 with the [configured-path guard](NATIVE_HOST_PATH_GUARD.md).
The gen2 stdin/argv increment remains the historical base of that exact-root chain.

2026-11-10: additional [canonical memory probes](../tests/security/memory-commit/README.md)
were natively authored, verified/built with the unchanged Windows seed and executed
through MCP. Native carriers and identities are in
`native/transactions/20261110/manifest.json`. No server/launcher root changed.

The native executor accepts binary stdin and an explicit argument vector and
returns separate exact byte streams and resource observations. It remains a
Windows preview. [Execution contract and bounds](NATIVE_EXECUTION_INCREMENT.md),
[acceptance evidence](evidence/native-executor-input-argv-20261101.json), and
[remaining gates](WINDOWS_READINESS.md) define the supported scope.

Authoritative canonical sources:

| Program | Source | Root |
|---|---|---|
| Server | `native/xax-mcp-native-gen3.xax` | `44f8e6b34a4bd3d50bfb670c1be6a73c9e5bfae7f701383f70eb51e37befd94d` |
| Launcher | `native/xax-mcp-sandbox-gen1.xax` | `d378055b3c4c490c667db8d7f61b2d871f4bb3b8701ae54e5dc5308037904dff` |

Older stores and construction JSON are historical references. Executable changes
were authored as semantic objects and applied through official exact-root native
transactions. Unchanged objects retain their identities. No textual XAX exists.
The [20261027 manifest](../native/transactions/20261027/manifest.json) reconstructs
the previous server; the [20261101 manifest](../native/transactions/20261101/manifest.json)
adds the server increment and reconstructs the new launcher. Native `edit` and
mandatory `verify` establish authority before atomic local promotion.
The [20261110-host-paths manifest](../native/transactions/20261110-host-paths/manifest.json)
extends that chain through the current gen3 server; gen2 remains its historical base.

## Pinned dependency

The pinned XAX commit exports `xax-native-file-v1`.
[xax-dependency.json](../native/xax-dependency.json) records the commit and the
exact Windows compiler seed SHA-256.
No XAX or BBC compiler changes were made. The seed has a disclosed historical
bootstrap; no bootstrap interpreter is invoked in these application builds or
requests. A compiler own-source fixed point is not claimed.

```text
xaxc verify  store.xax diagnostic
xaxc inspect store.xax inspection
xaxc edit    store.xax XAXEDIT1-record candidate.xax
xaxc resolve request.xax snapshot.xax
xaxc build   snapshot.xax artifact.exe provenance
```

Status 0 means success, 1 rejection, 2 unsupported/declined, 3 I/O/usage failure.
Every nonzero result fails the operation. A diagnostic can occupy an output path
after rejection; it is not a successful executable or canonical candidate.
The seed's `construct` command remains unsupported; supplied semantic objects in
native edit records provide the implemented authoring path.

## Runtime and authority

Native XAX implements STDIO/JSON-RPC, UTF-8/JSON validation, schemas, dispatch,
host rights, compiler argument arrays, exact-root edits and launcher supervision.
Windows/MSVCRT imports are explicit system interfaces. No interpreter, shell
wrapper, foreign implementation or PATH lookup handles requests.

Host configuration selects the compiler, seed, private work directory and rights.
Tool arguments cannot replace them or add grants, environment variables, arbitrary
executables or budgets. Execution rebuilds only the current authorized artifact.
`--allow-execute` and working AppContainer/job confinement are required.

Construction/transaction stages `next.xax`, calls native verification, and uses
`MoveFileExA` only on success. A nonzero exact root is mandatory; stale, invalid
and declined candidates never replace current state. The process-lifetime
share-mode-zero, delete-on-close workspace lease is non-inheritable. Competing
servers get `workspace_busy` and may retry after the owner exits. This coordinates
cooperating servers, not hostile peers with the same Windows user's authority.

The query reads at most 65,536 inspection bytes. Its first function is CID-ordered,
not necessarily entry. `ws_0` is descriptive, not a cross-session capability.
General graph queries, paging and portable scoped result handles remain absent.

## Verification scope

[release-status.json](../native/release-status.json) records source/compiler/artifact
identities and separate verification states. Both programs have native deterministic
rebuild and transaction-replay checks. Synthetic canonical probes independently
observe argv, binary EOF/streams, environment and confinement; CPU enforcement is
measured rather than inferred from configured job flags.

Source verification does not establish OS security or full release readiness.
The pushed implementation also passed [Windows CI run 41314738774](https://github.com/MrxSiN/XAX-MCP/actions/runs/41314738774),
including all source/probe replays, deterministic builds and runtime gates. The
[CI record](evidence/native-executor-ci-41314738774.json) preserves run/artifact
identities and downloaded observations separately from the earlier local evidence.
Asynchronous cancellation, in-flight server/compiler crash cleanup, exhaustive
resource pressure and independent escape review remain open. CUM transformations,
typed layouts, registered external tools and full prepare are separate capabilities.

[Installation/rebuild](INSTALL_WINDOWS.md) · [Security](SECURITY.md).
