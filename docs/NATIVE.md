# Native XAX server 0.9.0

The authoritative server source is `native/xax-mcp-native-gen1.xax`, canonical root
`edd555239cd0bec3dd5457b882e83e0f341149fa44447878c1633600d854539d`.
The old gen0 store and construction JSON remain historical inputs, not current source. Unchanged semantic objects
were retained by identity; a native transaction imported the existing snapshot closure into an editable build
request and subsequent exact-root transactions changed only affected graphs/constants. No textual XAX exists.

The [46-record manifest](../native/transactions/20261027/manifest.json) starts from the committed seed, imports the
unchanged application closure, then applies candidate verification, schema guards, native construction dispatch,
identity/schema literals, bounded inspection, exact-root checks, the exclusive directory lease and corrected metadata.
Records are transport; native `edit` plus `verify` are the authority. CI replays every record and compares the exact
final canonical bytes before building twice.

## Native dependency

[XAX af376e8a8a1ac5635bcad459cb7063ef0b326430](https://github.com/MrxSiN/XAX/tree/af376e8a8a1ac5635bcad459cb7063ef0b326430)
exports `xax-native-file-v1`. The committed Windows seed SHA-256 is
`aa72234d6dd8a111efde62b47ced8449a482c4c5506d876714ff7fbe0968ab79`.
Its source identity and historical bootstrap are recorded upstream in `compiler/bootstrap/windows/seed.json`;
[the dependency manifest](../native/xax-dependency.json) pins it independently from the application.
No compiler or verifier is reimplemented in XAX-MCP. The seed's own-source compilation declines (exit 2);
no self-hosting or language replacement-level promotion is claimed.

```text
xaxc verify  store.xax diagnostic
xaxc inspect store.xax inspection
xaxc edit    store.xax XAXEDIT1-record candidate.xax
xaxc resolve request.xax snapshot.xax
xaxc build   snapshot.xax artifact.exe provenance
```

Exit status 0 means success, 1 rejection, 2 unsupported/declined, 3 I/O or usage failure. Any nonzero status must
fail the operation. Native `edit` alone does not verify a candidate; the adapter explicitly does so before publication.

## Runtime and authority

Native XAX implements STDIO framing, UTF-8/JSON validation, JSON-RPC, handshake, tool schemas, dispatch, launch rights,
compiler argument arrays and the sandbox launcher. Windows/MSVCRT imports are OS interfaces. Launch flags and
host environment select authority; tool arguments cannot change the compiler, paths, rights or quotas.
The server has no interpreter, SDK or shell process in its request path.

Construction and transaction stage `next.xax`, call native `verify`, and publish with `MoveFileExA` only on success.
Every public carrier must have a nonzero exact expected root. The native editor checks freshness; invalid, declined
and stale candidates never replace current state. Verification rejection deletes the candidate.

Before any compiler-backed operation a native XAX helper obtains an exclusive `CreateFileA` lease in the work
directory: share mode zero, temporary/delete-on-close, non-inheritable handle retained until process exit. A second
process receives `workspace_busy`; a failed acquisition can retry after the owner exits. This excludes cooperating
server processes, not hostile processes with the same Windows user's filesystem authority. Private host directories
must not be writable by untrusted peers; filesystem links and host changes remain the owner's responsibility.

The one workspace label `ws_0` is descriptive, not an accepted cross-session capability. No tool accepts an arbitrary
path. The query scans at most 65,536 native inspection bytes and returns the first function in CID order, which is
not necessarily the program entry. General semantic queries and paging remain unsupported. Root identity is the
freshness token; the old constant `generation: 1` field has been removed.

## Verification and limits

All current server/sandbox bytes, source hashes and supported-path findings are in
[release-status.json](../native/release-status.json). Two native builds reproduce the shipped server and provenance
byte for byte; the sandbox also rebuilds identically. An external PowerShell client checked 28 cases, including new
construction result 136, invalid candidate rejection/cleanup, schema violations, stale/zero roots, authority denial,
isolated directories, shared-directory refusal and crash release. It performs transport/orchestration only.

The sandbox is the unchanged canonical XAX program `native/xax-mcp-sandbox-gen0.xax`: capability-less AppContainer,
job object, 5 seconds CPU, 256 MiB, one process, 10 seconds wall and 1 MiB per captured stream. The new native timeout
fixture confirms the wall limit. This does not certify output saturation, disk quotas, handle quotas, all escape
attempts or asynchronous cancellation. Full release readiness remains false.

[Installation/rebuild](INSTALL_WINDOWS.md) · [Current gates](WINDOWS_READINESS.md) ·
[Historical native observations](history/NATIVE_0_8.md).

The crash lease test covers an idle owner. In-flight compiler crash/orphan cleanup remains unimplemented; a compiler child can outlive a crashed server and the lease is deliberately not inherited. No complete in-flight crash isolation claim is made.
