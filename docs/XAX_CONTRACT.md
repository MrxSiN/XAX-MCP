# The XAX interfaces this adapter consumes (contract `xax-mcp/xax-contract-v1`)

XAX has no separately versioned execution-service API. XAX-MCP consumes these library interfaces of the pinned
commit `01ad841c76416fc741dd1386b12124904924c10d`. They were found by inspecting the code and the tests
(`tests/test_xax_construct.py` and `benchmarks/bench_r6_xb64.py` upstream), and `compat.REQUIRED_API` checks
them at startup.

| Interface | Used for | Upstream evidence |
|---|---|---|
| `xax_construct.construct(request) -> Constructed`, `FORMAT == "xax-construct-v1"` | new programs (ADR-210) | `tests/test_xax_construct.py` |
| `xax_workspace.Workspace(reader, target)`: `function_nodes`, `operands`, `neighborhood`, `expand`, `callers`, `callees`, `type`, `effects`, `effect_summary`, `entity`, `proof`, `diff`, `repair_neighborhood`, `root_query`, `verify`, `commit`, `rollback`, `generation`, `root`, `reader` | queries and transactions | upstream workspace tests |
| `xax_local_protocol.LocalMutationSession(workspace, expected_generation=)`: `transaction`, `diagnostic_view`, `for_function`, `view`; `edit_grammar_id` | snapshot-bound edits (ADR-186/200) | `bench_r6_xb64` maintenance edit |
| `xax_build.build(reader, request_cid, producer_identity=)`, `build_request`, `resolve_packages`, `snapshot_store`, `decode_snapshot`, `decode_request`, `decode_package`, `decode_provenance`, `ArtifactKind` | builds and provenance | `bench_r6_xb64._builds` |
| `xax_compiler`: `StoreReader`, `XaxError`/`Diagnostic`, `Kind`, `Operation`, `decode_native_target`, `x86_64_linux_exec_target`, `X86_64_LINUX_ABI`, `X86_64_LINUX_ELF_EXEC_FORMAT` | identities, diagnostics, target facts | — |
| `xax_linux.linux_api()` | reporting carrier entities | — |
| `xax_native.AUTHORITY` | reporting which compiler components ran as XAX | — |

Two uses depend on implementation details, and the pinned tests exercise both: the function handle prefix is
read from `function_nodes` handles (`F<i>.B<b>.N<n>`), and `LocalMutationSession.for_function` is used for the
non-authoritative function view.

## Process and I/O contract (as implemented upstream)

- Linux x86-64 `x86_64-linux-elf-exec-v1` builds a static ELF whose entry is the XAX entry function. It takes
  no machine parameters, returns at most one integer, and must end with `linux.exit_group`
  (`xax_linux.validate_process_entry`).
- Runtime data reaches a constructed program only through the `linux.read`/`linux.write` system calls and the
  exit status. `xax_linux.linux_startup_api` (argv/env) exists upstream but is not reachable from the
  `xax-construct-v1` carrier.
- `xax_linux.run_linux_executable` is marked "test harness only" upstream, so XAX-MCP runs artifacts with its
  own sandbox instead.

XAX-MCP adds only transport framing on top (`xax-mcp-io-v1`, [TOOLS.md](TOOLS.md#xax_execute)). Gaps and the
smallest proposed upstream interfaces are in [UPSTREAM_PROPOSALS.md](UPSTREAM_PROPOSALS.md).
