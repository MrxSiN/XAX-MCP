# Handoff

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
