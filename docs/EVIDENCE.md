# Evidence and claim labels

Labels: **PROVEN** (formal or exhaustive argument), **EXECUTED** (ran end to end and checked against an
independent oracle), **MEASURED** (raw samples recorded), **STRUCTURAL** (present and wired, but not exercised
end to end), **PROTOTYPE** (works for a narrow case), **UNIMPLEMENTED**.

| Claim | Label | Evidence |
|---|---|---|
| An MCP client initializes the STDIO server, discovers 8 tool schemas, and gets real compiler/target capabilities | EXECUTED | `test_initialize_discover_construct_build_execute_novel_program`, `test_stdout_carries_only_json_rpc` |
| A novel computation (coefficients and inputs drawn at run time) is constructed, verified, built, and executed, and the result matches an independent oracle | EXECUTED | same test; `test_novel_random_computation_runs_as_xax_generated_code`; `docs/evidence/*.json` |
| The result comes from XAX-generated code, not the adapter | EXECUTED | committing one constant-node edit changes the artifact digest and the native result (`test_semantic_edit_changes_the_executed_result`); the adapter has no arithmetic over inputs (`io_codec` only reframes bytes) |
| Edit/verify/commit/rollback and stale-root rejection through MCP | EXECUTED | `test_transaction_and_stale_root_through_mcp`, `test_stale_root_is_rejected_not_refreshed`, `test_verify_then_rollback_leaves_root_unchanged` |
| Previously verified stores reopen and run (path A) | EXECUTED | `test_two_clients_are_isolated_and_stores_reopen`; upstream xb64 gen0/gen1 (`test_upstream_store.py`, RFC 4648 vector and both wrap widths) |
| Sandbox denies filesystem access, enforces wall, CPU, and output limits, cancels, and dies with the server | EXECUTED | `tests/test_security.py`, `test_server_crash_kills_running_artifact` |
| Fails closed without isolation | EXECUTED | `test_execution_fails_closed_without_sandbox`; also observed for real when a launcher bug made the probe fail during development |
| Network denial | STRUCTURAL | empty network namespace and seccomp deny `socket`; no carrier entity can express a socket call, so there is no end-to-end test |
| Cold and warm tool latency | MEASURED | `docs/evidence/e2e-linux-x86_64-{cold,warm}.json` (cached execute median ≈ 34–39 ms; build miss ≈ 56–60 ms; construct ≈ 26 ms; first call waits 20–50 s for XAX warm-up) |
| Codex / Claude Code registration | STRUCTURAL | CLI registration verified; Claude Code health check connected; no model-driven session |
| Strings, JSON/CSV, files, network, other targets | UNIMPLEMENTED | not reachable through `xax-construct-v1` at the pinned XAX; reported by `xax_capabilities` |

The MCP latencies are tool round trips on one shared host. They are not XAX R4 generated-code benchmarks, and
they are not the deferred AI-token efficiency milestone.
