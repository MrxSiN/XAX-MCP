# Security model

Agent-supplied programs and tool arguments are untrusted. Passing the XAX verifier proves semantic
well-formedness, not that it is safe to run native code. Execution is therefore a separate host grant, and it
happens only inside OS-enforced isolation.

## Authority

- Rights (`read`, `mutate`, `build`, `execute`) come only from launch flags in the host configuration. The
  defaults are `read`, `mutate` and `build`; `--allow-execute` adds execution; `--read-only` and `--deny RIGHT`
  restrict. No tool argument changes rights.
- Executed programs get the `stdio` effect only. Filesystem, network, process, environment, and clock effects are
  denied (`denied_capability`), and the sandbox enforces this even if a program attempts the system calls.
- Opening stores needs a host-granted `--store-root`. Names must be relative `.xax` paths without `..`, and
  symlinks are refused. The resolved file must stay inside the root and within 16 MiB, and it is verified by
  XAX before use.
- Handles are random (96 bits), session-scoped, and bounded in number. Forged, guessed, expired, or foreign
  handles get `not_found`.

## Sandbox (Linux x86-64)

`_sandbox_exec.py` is the entire executor boundary. The server starts it as `python -I -S <file> --status FD
--dir DIR --memory N --cpu N --parent PID` with an empty environment and no shell. Before `execve("/prog")` it:

1. sets `PR_SET_PDEATHSIG=SIGKILL` (the program dies with the server);
2. `unshare`s user, mount, network, IPC, UTS, and cgroup namespaces and maps the caller to uid/gid 65534, so the
   executed program has no capabilities and an interface-less network namespace;
3. bind-mounts the artifact directory read-only/nosuid/nodev onto itself and `chroot`s into it (the root
   contains only `prog`);
4. sets limits: address space (256 MiB by default), CPU seconds (SIGXCPU, then SIGKILL one second later), zero
   file size, no core dumps, 3 file descriptors, 1 process, no locked memory;
5. sets `no_new_privs` and installs a seccomp-BPF allowlist: `read write close mmap munmap brk rt_sigreturn
   execve exit exit_group`. Every other syscall returns EPERM. A non-x86-64 arch or an x32 syscall kills the
   process.

Any failure is reported on a close-on-exec status pipe, and the launcher exits 125 without running the artifact.
The parent enforces wall time, stdout/stderr quotas, and cancellation by SIGKILL of the process group. It also
removes the temporary directory. At startup the server probes the sandbox and checks that the namespaces
differ from its own, that the root holds only `prog`, and that `openat` is denied. If the probe fails, execution
is refused with `sandbox_unavailable` and nothing runs unconfined.

## Regression tests (`tests/test_security.py`, `tests/test_e2e_stdio.py`, `tests/test_warm.py`)

| Threat | Test |
|---|---|
| filesystem read from artifact | `test_filesystem_is_unreachable_from_artifacts` (openat → -EPERM), with an unconfined positive control |
| execution without isolation | `test_execution_fails_closed_without_sandbox` |
| rights via arguments | `test_rights_come_from_host_policy_not_arguments` |
| undeclared effects | `test_undeclared_effects_are_denied` |
| forged/foreign handles, cross-client leakage | `test_forged_and_foreign_handles_are_rejected`, `test_two_clients_are_isolated_and_stores_reopen`, `test_concurrent_executions_and_sessions_are_isolated` |
| stale or tampered artifacts | `test_semantic_edit_changes_the_executed_result`, `test_tampered_artifact_is_refused` |
| oversized or malformed requests | `test_oversized_and_malformed_requests_are_rejected_before_compilation` |
| edit injection | `test_mutation_tokens_cannot_inject_extra_edits` |
| path traversal and symlink escape | `test_store_roots_block_traversal_and_symlinks`, `test_store_open_verifies_bytes` |
| runaway programs | `test_wall_time_limit_kills_spinning_artifact`, `test_cpu_limit_is_enforced`, `test_output_quota_kills_flooding_artifact` |
| cancellation and server crash | `test_cancellation_kills_the_process`, `test_server_crash_kills_running_artifact` |
| arbitrary shell/Python | no such tool or code path; `test_construct_rejects_semantic_errors_with_diagnostics` rejects non-XAX operations |
| STDOUT corruption | `test_stdout_carries_only_json_rpc` (fd 1 is redirected to stderr at startup) |

## Warm server (`warm.py`, ADR-0008)

- The socket lives in a directory that must be owned by the user and mode 0700 (`$XDG_RUNTIME_DIR/xax-mcp`, else
  `~/.cache/xax-mcp/run`, or `XAX_MCP_WARM_DIR`); otherwise the launcher serves in-process and starts nothing. The
  socket file is 0600 and the server also checks the peer uid with `SO_PEERCRED`.
- Authority is unchanged: the forked child parses the launcher's own command line, exactly as an in-process
  server would. The warm server itself holds no rights, no sessions, and no client data, and children do not share
  memory with each other after the fork.
- The warm server runs with a reduced environment (`PATH`, `HOME`, locale, temporary and XDG directories, and
  `XAX_*`). Only `XAX_MCP_LOG` and `XAX_MCP_REQUIRE_SANDBOX` are forwarded per launch.
- It forks only while single-threaded, accepts at most a 64 KiB launch header, and exactly three descriptors.
- A child exits on STDIN EOF or when the launcher's connection closes, including when the launcher is killed
  (`tests/test_warm.py::test_child_exits_when_its_launcher_dies`). Sandboxed programs still die with the child that
  launched them (`PR_SET_PDEATHSIG`).
- `--no-warm-server` or `XAX_MCP_WARM_SERVER=0` disables it.

## Audit

Each tool call writes one JSON line to stderr: the tool, whether it succeeded, the error code, and the request
size. Payloads, inputs, outputs, and file contents are never logged.

## Known limits

- Only Linux x86-64 is supported. Elsewhere the probe fails and execution is refused.
- The sandbox needs unprivileged user namespaces. Ubuntu 23.10+ restricts them through AppArmor (see
  [HOSTS.md](HOSTS.md#troubleshooting)).
- The cgroup namespace is created but no cgroup controller limits are applied. Memory and CPU are bounded by
  rlimits.
- `execve` stays in the allowlist because the launcher needs it. Inside the chroot the only executable is the
  artifact itself.
- The warm server stays resident until idle for `XAX_MCP_WARM_IDLE_SECONDS` (default 900), with about 800 MB
  RSS at XAX `6c2df90`.
- No HTTP transport is shipped. An HTTP deployment would need authentication, origin/host validation, TLS, and
  per-session isolation before it could be offered.
