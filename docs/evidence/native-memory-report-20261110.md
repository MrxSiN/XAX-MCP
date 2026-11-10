# Development report — 2026-11-10

| Status | Scope | Executed evidence |
|---|---|---|
| Completed | Revalidate Windows baseline | 64 verified source replays, 15 native probe rebuilds, two identical application builds each, 92 client exchanges, golden STDIO, timeout and launcher-termination cleanup |
| Completed | New XAX implementation | Two canonical native memory-allocation probes; native definition/replacement and exact-root integer carriers; pinned Windows verification and two identical builds each |
| Completed | Bounded memory-denial test | Three confined trials each: 64 MiB succeeds, 320 MiB denied; both unconfined controls succeed |
| Completed | Persistent MCP replay | Eight exchanges: query, low execution, exact-root edit, high execution, stale rejection and preserved verified root |
| Partially completed | P0 security/reliability | New bounded allocation evidence; broad pressure, cancellation, hostile-path races, traps, crash windows and independent escape review remain open |
| Blocked / incomplete | Full semantic-evolution mission | Pinned Windows interface lacks general queries/native definition batches; typed mutations/candidates/results, modern MCP, current model-driven hosts and AI comparisons are not delivered |

Only XAX implementation was retained in XAX-MCP. Other new files are native
transaction carriers, declarative test data, evidence and documentation. External
PowerShell orchestration resides outside the repository. The initial packaging
scripts were withdrawn under the user's explicit XAX-only rule; the workflow was
restored to its entry contents. No packaging fix is claimed.

The [entry audit](mission-audit-20261110.md) records both exact HEADs and their
large pre-existing dirty trees. The 0.10 implementation cited in existing guides
is not in this local Git object database. Changes are left uncommitted: committing
or pushing the existing tree would combine unrelated pre-existing work, while a
probe-only commit would reference baseline sources absent from HEAD. No upstream
files, compiler/deployment pin, server/launcher root or tool schema were changed.

## Reproduction

Run from `D:\GitHub\XAX-MCP`. These are native compiler argument vectors. Use
fresh output names in the existing external scratch directory; do not overwrite
canonical inputs. The authoring executable's exact SHA-256 is in the
[transaction manifest](../../native/transactions/20261110/manifest.json).

```text
wsl -d Ubuntu -- /mnt/d/GitHub/XAX/compiler/bootstrap/seed/xaxc-linux-x86_64 edit /mnt/d/GitHub/XAX-MCP/tests/security/executor-input/io-echo-probe.xax /mnt/d/GitHub/XAX-MCP/native/transactions/20261110/memory-low.batch /mnt/c/Users/User/.codex/scratch/xax-mcp-20261110/repro-low.xax
D:\GitHub\XAX\compiler\bootstrap\windows\xaxc-windows-x86_64.exe verify C:\Users\User\.codex\scratch\xax-mcp-20261110\repro-low.xax C:\Users\User\.codex\scratch\xax-mcp-20261110\repro-low.diag
D:\GitHub\XAX\compiler\bootstrap\windows\xaxc-windows-x86_64.exe edit tests/security/memory-commit/memory-low.xax native/transactions/20261110/memory-high.edit C:\Users\User\.codex\scratch\xax-mcp-20261110\repro-high.xax
D:\GitHub\XAX\compiler\bootstrap\windows\xaxc-windows-x86_64.exe verify C:\Users\User\.codex\scratch\xax-mcp-20261110\repro-high.xax C:\Users\User\.codex\scratch\xax-mcp-20261110\repro-high.diag
D:\GitHub\XAX\compiler\bootstrap\windows\xaxc-windows-x86_64.exe resolve C:\Users\User\.codex\scratch\xax-mcp-20261110\repro-high.xax C:\Users\User\.codex\scratch\xax-mcp-20261110\repro-high-snapshot.xax
D:\GitHub\XAX\compiler\bootstrap\windows\xaxc-windows-x86_64.exe build C:\Users\User\.codex\scratch\xax-mcp-20261110\repro-high-snapshot.xax C:\Users\User\.codex\scratch\xax-mcp-20261110\repro-high.exe C:\Users\User\.codex\scratch\xax-mcp-20261110\repro-high.prov
```

Require compiler exit 0 and empty verification diagnostics; compare exact bytes
against the manifest. Repeat resolve/build for each source and build twice into
different outputs. Replaying `memory-high.edit` against the high source must return
exit 1; its output is a diagnostic. Native independent `memory-high.batch`
construction must yield the same canonical bytes as the pinned low-to-high edit.

For the MCP evolution, configure the trusted host's `XAX_MCP_COMPILER` to the
pinned Windows executable, `XAX_MCP_STORE` to the absolute path of
`tests/security/memory-commit/memory-low.xax`, and `XAX_MCP_WORK` to a fresh private
directory. Start `D:\GitHub\XAX-MCP\native\xax-mcp-native.exe --allow-execute`.
Send [the request transcript](../../tests/security/memory-commit/evolution.requests.ndjson)
through a standard legacy STDIO client and assert
[expected fields](../../tests/security/memory-commit/evolution.expected.json).
The actual [eight responses](native-memory-evolution-20261110.ndjson) are recorded.
This replay uses only the public MCP tool surface; initial probe authorship was
through the upstream native workspace, not through an MCP typed-authoring tool.

The [machine evidence](native-memory-commit-20261110.json) records source,
compiler and artifact hashes, resource observations, failed attempts, raw baseline
transcript hash and external harness location. The unchanged entry workflow's
first four run blocks reproduce the older baseline; orchestration is external to
the deployed native path. No new hosted workflow run is claimed.

## Residual risks and next work

1. The server reports raw u32 exits. An early failed probe trapped with
   `0xC000001D` while tool `ok` remained true. Final probes explicitly observe
   allocation success/denial without a heap view or dereference; general trap
   classification remains unresolved. Do not infer behavioral success from `ok`.
2. The observed memory case does not establish gradual/physical-page pressure,
   concurrency exhaustion or every termination/cleanup window. Compiler-call
   cancellation and hostile same-user path replacement remain security blockers.
3. ZIP assembly still excludes native transactions. A future fix must respect
   XAX-only implementation; no withdrawn external-script fix is presented as done.
4. The narrow upstream step for P1/P2 is a separately tested native Windows
   graph-inspection/authoring contract and controlled seed compatibility audit.
   The available Linux native authoring interface does not silently upgrade the
   deployed Windows seed or establish Windows compiler self-hosting.
5. Current model-driven Codex/Claude use, modern MCP, candidate lifecycle, result
   paging and fair AI reliability comparisons remain untested/unimplemented.

`release_ready` and `full_mission_complete` remain false. No independent security
review or release acceptance is claimed.
