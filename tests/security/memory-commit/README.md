# Native Windows commit-memory denial probes

These are canonical XAX test programs, authored through the upstream native
workspace. No other-language implementation or graph emitter is included.
The native transaction manifest is
`native/transactions/20261110/manifest.json`; batch files are native workspace
transport, not authoritative textual XAX source.

Both programs call Windows `VirtualAlloc` with `MEM_RESERVE | MEM_COMMIT` and
`PAGE_READWRITE`, compare the actual returned address with zero, release the
semantic allocator token and call `ExitProcess`. They do not dereference the
allocation. The process exit releases its OS allocation. Exit 1 means allocation
succeeded; exit 0 means allocation was denied. These meanings belong only to this
probe; general child exit codes are not typed XAX results.

| Program | Requested commit | Outside sandbox | Native MCP/AppContainer/job |
|---|---:|---:|---:|
| memory-low.xax | 67,108,864 bytes | 1 (succeeded) | 1 in three trials |
| memory-high.xax | 335,544,320 bytes | 1 (succeeded) | 0 in three trials |

The host job cap remains 268,435,456 bytes. Confined peak process commit was
68,894,720–68,907,008 bytes for the low probe and 1,646,592–1,667,072 bytes for
the high probe. Positive controls show that the high request is valid and can
succeed outside confinement. This establishes this bounded allocation-denial
case; it is not exhaustive memory-pressure or escape testing.

The [evolution requests](evolution.requests.ndjson) run one persistent program:
initialize, query, execute the low probe, apply the exact-root integer mutation,
query, execute the high probe, reject a stale replay, and requery the preserved
root. Configure the host-owned store to `memory-low.xax`, a fresh private work
directory and the pinned compiler; grant execution at native server startup.
Use a standard legacy STDIO client and send `notifications/initialized` as shown.
Expected tool fields are in `evolution.expected.json`; actual responses are in
`docs/evidence/native-memory-evolution-20261110.ndjson`.

For native construction replay, use the exact authoring executable identified in
the manifest. It supports native batch definitions; the older Windows seed does
not. The authoring compiler is not a deployed dependency or a release pin change.
The following are native CLI argument vectors, not source code:

```text
<authoring-xaxc> edit tests/security/executor-input/io-echo-probe.xax native/transactions/20261110/memory-low.batch <candidate.xax>
<pinned-windows-xaxc> verify <candidate.xax> <diagnostic>
<pinned-windows-xaxc> edit tests/security/memory-commit/memory-low.xax native/transactions/20261110/memory-high.edit <high-candidate.xax>
<pinned-windows-xaxc> verify <high-candidate.xax> <diagnostic>
<pinned-windows-xaxc> resolve <candidate.xax> <snapshot.xax>
<pinned-windows-xaxc> build <snapshot.xax> <artifact.exe> <provenance>
```

Require exit 0 for each compiler operation, an empty verification diagnostic and
the manifest's exact source/artifact hashes. Resolve/build each source twice in
fresh output paths. A stale replay returns compiler exit 1, and its output is a
diagnostic rather than an acceptable candidate. Through MCP it currently returns
`transaction_rejected`, not a precise `stale_root` code.

External PowerShell orchestrated the local tests from outside this repository.
It is disclosed in the evidence and is not required by the deployed server or
probes. No new other-language implementation or CI workflow code was retained
in XAX-MCP. These new probes were executed locally; they are not yet a hosted CI
memory-enforcement gate. Existing historical evidence and application roots are
unchanged. Release acceptance remains false.
