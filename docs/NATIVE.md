# Native XAX server 0.10.0

The native executor accepts binary stdin and an explicit argument vector and
returns separate exact byte streams and resource observations. It remains a
Windows preview. [Execution contract and bounds](NATIVE_EXECUTION_INCREMENT.md),
[acceptance evidence](evidence/native-executor-input-argv-20261101.json), and
[remaining gates](WINDOWS_READINESS.md) define the supported scope.

Authoritative canonical sources:

| Program | Source | Root |
|---|---|---|
| Server | `native/xax-mcp-native-gen2.xax` | `16a25c0805b900e3bb45082b0ac88e1217cbf184c1bf739d29d1df1bc298eb83` |
| Launcher | `native/xax-mcp-sandbox-gen1.xax` | `d378055b3c4c490c667db8d7f61b2d871f4bb3b8701ae54e5dc5308037904dff` |

Older stores and construction JSON are historical references. Executable changes
were authored as semantic objects and applied through official exact-root native
transactions. Unchanged objects retain their identities. No textual XAX exists.
The [20261027 manifest](../native/transactions/20261027/manifest.json) reconstructs
the previous server; the [20261101 manifest](../native/transactions/20261101/manifest.json)
adds the server increment and reconstructs the new launcher. Native `edit` and
mandatory `verify` establish authority before atomic local promotion.

## Pinned dependency

XAX commit `af376e8a8a1ac5635bcad459cb7063ef0b326430` exports
`xax-native-file-v1`. The Windows compiler seed SHA-256 is
`aa72234d6dd8a111efde62b47ced8449a482c4c5506d876714ff7fbe0968ab79`.
[xax-dependency.json](../native/xax-dependency.json) pins that exact executable.
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
Asynchronous cancellation, in-flight server/compiler crash cleanup, exhaustive
resource pressure and independent escape review remain open. CUM transformations,
typed layouts, registered external tools and full prepare are separate capabilities.

[Installation/rebuild](INSTALL_WINDOWS.md) · [Security](SECURITY.md) ·
[Historical native observations](history/NATIVE_0_8.md).
