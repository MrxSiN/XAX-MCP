# Handoff

## 2026-11-11 — resumed experimental checkpoint

Continue from [the repaired candidate](NATIVE_CANDIDATE_20261111.md) and its
[exact-root manifest](../native/transactions/20261111-capabilities/manifest.json).
Capabilities framing, complete discovery versions, identity and cache hints pass
new native/client checks; nine Windows records reproduce the candidate. The
default gen3 deployment and compiler pin are unchanged. Controlled pre-existing
and concurrent workspace `edit.rec` hard links overwrite outside disposable files;
those failures remain open. The [required upstream contract](NATIVE_HANDLE_CONTRACT.md)
and remaining cancellation, semantic paging and desktop-client gates are explicit.
No unimplemented candidate feature is released.

## 2026-11-10 — user-requested pause

Continue from [the remaining-work prompt](../CONTINUE_NATIVE_EVOLUTION.md).
Native handle-pinning, compiler-process, modern protocol and bounded object-inventory
checkpoints are retained in `native/candidates/20261110/` with separate evidence.
They are experimental and are not selected by the default executable or workflow.
The subsequent capabilities-literal candidate verifies/builds but produces malformed
JSON; its exact failing response is retained. Do not promote it without fixing and
testing framing. Request-level compiler cancellation, complete replacement-race
protection, paginated semantic APIs and final integration remain unfinished.

The Git entry-state observations below are historical. Before this pause, HEAD/index
were aligned to published `a2677d7cfa08c4d0ad9608d4cd397fa1b523e485` without changing
working-file contents. The default gen3 work and experimental checkpoints are
committed together at the user's request; release readiness remains false.

## 2026-11-10 — native configured-path guard and package inputs

Current authoritative server source is gen3, root
`44f8e6b34a4bd3d50bfb670c1be6a73c9e5bfae7f701383f70eb51e37befd94d`.
[Native path validation](NATIVE_HOST_PATH_GUARD.md) rejects configured compiler,
seed and workspace reparse/ambiguous paths before scratch leasing or compiler work,
and rechecks after lease acquisition. The distinct error is `unsafe_host_path`.
The deployment compiler and launcher are unchanged. Host paths now require
existing drive-qualified absolute files/directories; UNC/device/relative and
ambiguous names fail closed. Workspace child-file substitution and TOCTOU races
remain open.

`native/transactions/20261110-host-paths/manifest.json` extends the historical chain
to gen3: 65 source records total. The complete native batch and packed immutable
native objects both reproduce the same verified canonical source. New native
helpers and the existing paths are exercised by local negative and 92-exchange
regression tests. [New evidence](evidence/native-host-path-guard-20261110.json)
separates failures, final source/build identities, package checks and remaining
blockers. No new hosted CI run or release approval is claimed.

The existing workflow's native source/manifest configuration selects gen3. Package
assembly now includes transactions and refuses pre-existing staging/output; no
new other-language implementation or test script is retained in the repository.
Historical evidence and gen2 remain unchanged. Semantic queries/typed authoring,
candidate lifecycle, modern MCP, compiler cancellation and full release review
still require work.

## 2026-11-10 — native memory-denial tests

Added canonical [memory-commit probes](../tests/security/memory-commit/README.md),
native exact-root carriers and an MCP low-to-high evolution replay. The pinned
Windows compiler verifies and builds both probes twice identically. Six confined
trials and two unconfined controls establish bounded commit-allocation denial.
The Linux native compiler was used only to author the new function; its hash and
dirty-checkout context are recorded separately, with no deployment pin upgrade.

The existing 64 source edits, 15 native probes, 92 client exchanges and timeout/
launcher-termination gates passed locally. See the
[entry gap matrix](evidence/mission-audit-20261110.md) and
[new evidence](evidence/native-memory-commit-20261110.json). Server/launcher roots
are unchanged. Only XAX implementation is added; external test orchestration is
outside this repository. No new hosted CI result is claimed.

The checkout was heavily modified on entry; its HEAD does not contain the 0.10
implementation commit cited below. Packaging still excludes replay records; the
initial other-language packaging changes were withdrawn under the user's XAX-only
constraint. General pressure, trap classification, compiler cancellation, semantic
queries/typed authoring/candidates/results, modern MCP and release review remain open.

## 2026-11-01 — 0.10 binary stdin and argv (current)

The executor increment is canonical/native XAX. Authoritative server gen2 root is
`16a25c0805b900e3bb45082b0ac88e1217cbf184c1bf739d29d1df1bc298eb83`;
launcher gen1 root is `d378055b3c4c490c667db8d7f61b2d871f4bb3b8701ae54e5dc5308037904dff`.
The XAX pin/seed is unchanged. The 20261101 manifest replays 15 server edits after
the 46-record base and three launcher edits from the seed. Review data is not source
authority. No textual XAX, compiler modification or foreign runtime helper was added.

`xax_execute` accepts optional binary `stdin_hex` and Unicode `args` excluding argv[0].
The launcher uses a read-only inherited stdin duplicate, explicit Windows quoting,
concurrent bounded output drains, creation-time job membership and actual total CPU
sampling. Legacy result fields remain; unknown observations are omitted on failure.
The supplied environment is explicit; Windows adds container-local TEMP/TMP.

Read [the execution contract](NATIVE_EXECUTION_INCREMENT.md),
[acceptance/failure evidence](evidence/native-executor-input-argv-20261101.json),
and [release identities](../native/release-status.json) before extending it.
Source-written/verified/compiled/executed/measured are not release acceptance.
Keep CUM transformations/full prepare, registered external tools, typed data layouts,
compiler cancellation and comprehensive crash/pressure/escape work separate.
Implementation commit `1e584cdfb00fe3230855b82b92eda3c63a50e807` is pushed to `main`.
[Windows CI run 41314738774](https://github.com/MrxSiN/XAX-MCP/actions/runs/41314738774)
passed all steps and uploaded the 0.10 preview and evidence artifacts. The
[new CI record](evidence/native-executor-ci-41314738774.json) supplements the original
local-only evidence without rewriting it: 92 client exchanges, 64 source records,
15 probes, deterministic builds, timeout and launcher-termination cleanup passed.
Release acceptance remains false. Review [ADR-0011](adr/0011-binary-stdin-and-explicit-argv.md)
before changing input, argument or resource supervision semantics.

## Earlier state

Earlier handoff notes (0.9 and before, including the retired Python tooling) are in git history.
[EVIDENCE.md](EVIDENCE.md) and `docs/evidence/` keep the recorded results. Current developer rules are in
[CLAUDE.md](../CLAUDE.md). See also [installation](INSTALL_WINDOWS.md), [native guide](NATIVE.md),
[readiness](WINDOWS_READINESS.md) and the [dependency manifest](../native/xax-dependency.json).

Open work: native general semantic query/handles, typed runtime ABI and result paging, compiler cancellation,
quota/escape coverage, current MCP protocol, model-driven Codex/Claude host tests and compiler self-build.
