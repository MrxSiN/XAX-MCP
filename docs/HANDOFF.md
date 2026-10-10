# Handoff

## State at 0.1.0 (2026-10-08, historical)
- STDIO MCP server with 8 tools over the pinned XAX `01ad841`. Construct, query, transact, build, and
  sandboxed execute all run end to end.
- Tests: `tests/test_service.py`, `tests/test_security.py`, `tests/test_e2e_stdio.py`,
  `tests/test_compat.py`, `tests/test_upstream_store.py` (needs `XAX_SOURCE_DIR`). The full suite takes about
  3–4 minutes on the reference host, mostly XAX warm-up per launched server.
- Evidence: `docs/evidence/` (record new runs with `scripts/record_evidence.py`; never overwrite old files).

## Work in progress after 0.5.1 (2026-10-10): Windows x86-64 hosts
- Pins XAX `44b5f3c` (`main`, host contract r7); requires r5 (ADR-256, PE integer-completion operations), which
  unblocked poly_reduce on Windows: it constructs, builds as a PE image and matches the oracle. r6 (jvm) and r7
  (linux-aarch64) add construct platforms not consumed yet.
- The service constructs and builds both `linux-x86_64` and `windows-x86_64`; an artifact is executable when its
  target identity is the host sandbox's platform. `xax_capabilities` lists the host's target first.
- Windows 11, Python 3.12: 39 pass, 12 skipped (warm server, `argv`, file-open, xb64: all Linux-only by carrier or
  design). Evidence: `docs/evidence/e2e-windows-x86_64-warm-in-process-unreleased-44b5f3c.json` (first
  construct+build+execute 2.7 s from launch; every XAX component ran through the Python bootstrap on Windows).
- Not done: the Linux suite was not run for these changes (no Linux host in this session); CI covers it. No
  Windows CI job, no warm server on Windows, no model-driven Windows host run. Not released (version still 0.5.1).

## State at 0.5.1 (2026-10-10)
- Pins XAX `f0aa191` (`main`; S8 verifier totality, ADR-251; host contract r3 unchanged). Pin bump only: no adapter
  code changed. 49/49 tests on Python 3.11 and 3.13; the fingerprint from a git install matches a local checkout.
- One run per mode on one host (`docs/evidence/*-0.5.1.json`): warm server, launch to first result 0.17 s; in-process
  with a populated cache 1.1 s; empty-cache `--prepare` 20.1 s; empty-cache in-process 35.7 s. The host kernel build
  differs from the 0.5.0 runs, so the differences are not attributed to upstream.

## State at 0.5.0 (2026-10-09, historical)
- Pins XAX `13a6843` (`main`; host contract r3, ADR-250). The warm server, `--prepare` and the in-process warm-up
  call `xax_native.prepare` instead of constructing a warm-up carrier; `xax_capabilities` reports each component's
  status under `server.xax_components`.
- Upstream did P6–P8 (ADR-248 to ADR-250). Launch to first result: in-process 1.3 s with a populated image cache
  (0.4.0: 3.1 s); warm server 0.18 s. Empty-cache `--prepare`: 24.4 s (0.4.0: 43.5 s). Warm server RSS about
  100 MB (0.4.0: about 800 MB). 49/49 tests on Python 3.11 and 3.13. Evidence: `docs/evidence/*-0.5.0.json`.
- Remaining: the in-process path with an empty cache is still sequential (about 42 s); see PERFORMANCE.md.

## State at 0.4.0 (2026-10-09, historical)
- Per-user warm server (ADR-0008, `src/xax_mcp/warm.py`): launches fork from a process with XAX loaded. Launch to
  first construct+build+execute: 0.2 s (0.3.1: 6.7 s). `xax-mcp --prepare` pays the XAX load at install time.
- In-process path: imports finish before the warm-up thread starts, so `initialize` takes 1.0 s (was 5.3 s).
- 49 tests on Python 3.11 and 3.13 (`tests/test_warm.py` adds 8). Evidence: `docs/evidence/*-0.4.0.json`;
  summary in `docs/PERFORMANCE.md`.
- The rest of the first-start cost is upstream (P6–P8 in UPSTREAM_PROPOSALS.md). This session could not change
  `MrxSiN/XAX` (no write access), so they are proposals with measurements, not patches.

## State at 0.3.1 (2026-10-09, historical)
- Pins XAX `6c2df90` (`main`; host contract r2 unchanged). Pin bump only: no adapter code changed. 41/41 tests on
  Python 3.11 and 3.13; the fingerprint from a git install matches a local checkout.
- One warm-cache sample: first construct+build+execute 1.4 s (0.3.0: 3.7 s); one cold sample: 41.7 s (0.3.0: 47.6 s).
  Single runs on one host; `docs/evidence/*-0.3.1.json`.

## State at 0.3.0 (2026-10-08, historical)
- Pins XAX `b0ec772` (`main`; host contract r2, ADR-231 byte-view widening). Test carriers read and write u64s
  with one checked access. `xax_capabilities` reports `checked_byte_view_widths`. 41 tests in about 53 s on
  Python 3.11 and 3.13.
- Warm-cache first call is about 3.5 s, up from 0.84 s at 0.2.0, because upstream's typing store grew (S8c.9–13).
  A further upstream cold-start reduction would target the native verifier setup and BLAKE3 CID checks.

## State at 0.2.0 (2026-10-08, historical)
- Pins XAX `f38cbee` (upstream ADR-222 to ADR-225: memoized component verification, `linux.startup.*` carrier
  entities, `linux-x86_64-process-v1`, `xax-host-contract-v1`). Adds the `argv` input mode and the
  host-contract startup check. 38 tests in about 35 s.
- `f38cbee` is merged into XAX `main` (merge commit `5c9ba68`). The decisions it records are numbered ADR-222
  to ADR-225 on `main`; the commit message itself says 221 to 224.

## Next steps, in order of leverage
1. The remaining empty-cache cost is upstream: the typing store is verified by the Python bootstrap and then
   lowered (PERFORMANCE.md). P6–P8 are done (ADR-248 to ADR-250); XAX decided against prebuilt images.
2. Record a model-driven Codex or Claude Code session with authenticated accounts and add it to
   COMPATIBILITY.md.
3. When XAX exposes libraries (strings, JSON) through the carrier, add a capability and a gap test that fails
   until the semantics run end to end. Until then, keep them UNIMPLEMENTED.
4. Optional cgroup v2 limits when a delegated cgroup is available.

## Rules
- No workload logic in the adapter: no per-operation tools and no Python fallbacks.
- Keep XAX changes in `MrxSiN/XAX`, and keep this repository's dependency direction one-way.
- Update `compat.TESTED_XAX`, `pyproject.toml`, CI, and COMPATIBILITY.md together.
