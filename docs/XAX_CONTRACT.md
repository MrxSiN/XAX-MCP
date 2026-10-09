# The XAX interfaces this adapter consumes

Since commit `f38cbeea2b90e9b6a580417ce7efaa7d3d75a183`, XAX publishes a versioned integration surface: `xax_contract`
(`xax-host-contract-v1`, ADR-225). XAX-MCP 0.3.0 and 0.3.1 require that contract at revision ≥ 2 (r2, ADR-231:
`FORMATS["checked_byte_view_widths"] = [1, 2, 4, 8]`, which `xax_capabilities` reports as
`targets[0].checked_byte_view_widths`); 0.2.0 required revision ≥ 1, checks
`xax_contract.missing()` at startup, and uses only names from it (`compat.REQUIRED_API`). XAX-MCP 0.1.0 pinned
`01ad841`, which predates the contract; the table below was its consumed surface, found by inspecting code and
tests.

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

## Process and I/O contract

Since `f38cbeea2b90e9b6a580417ce7efaa7d3d75a183`, this is upstream's `linux-x86_64-process-v1` (`xax_linux.process_contract()`, ADR-224), which
`xax_capabilities` reports verbatim. The facts below are what 0.1.0 relied on before the contract existed.

- Linux x86-64 `x86_64-linux-elf-exec-v1` builds a static ELF whose entry is the XAX entry function. It takes
  no machine parameters, returns at most one integer, and must end with `linux.exit_group`
  (`xax_linux.validate_process_entry`).
- Runtime data reaches a constructed program through `linux.read`/`linux.write`, the exit status, and (since
  `f38cbeea2b90e9b6a580417ce7efaa7d3d75a183`, ADR-223) `linux.startup.*` argv/env/auxv reads in the entry function.
- `xax_linux.run_linux_executable` is marked "test harness only" upstream, so XAX-MCP runs artifacts with its
  own sandbox instead.

XAX-MCP adds only transport framing on top (`xax-mcp-io-v1`, [TOOLS.md](TOOLS.md#xax_execute)). Gaps and the
smallest proposed upstream interfaces are in [UPSTREAM_PROPOSALS.md](UPSTREAM_PROPOSALS.md).
