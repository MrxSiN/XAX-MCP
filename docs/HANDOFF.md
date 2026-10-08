# Handoff

## State at 0.1.0 (2026-10-08, historical)
- STDIO MCP server with 8 tools over the pinned XAX `01ad841`. Construct, query, transact, build, and
  sandboxed execute all run end to end.
- Tests: `tests/test_service.py`, `tests/test_security.py`, `tests/test_e2e_stdio.py`,
  `tests/test_compat.py`, `tests/test_upstream_store.py` (needs `XAX_SOURCE_DIR`). The full suite takes about
  3–4 minutes on the reference host, mostly XAX warm-up per launched server.
- Evidence: `docs/evidence/` (record new runs with `scripts/record_evidence.py`; never overwrite old files).

## State at 0.3.0 (2026-10-08)
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
1. Upstream P4 (wide checked loads) is a semantic decision for the XAX maintainers; see UPSTREAM_PROPOSALS.md.
2. Cold image-cache start is still about 40 s (every component image is lowered once).
3. Record a model-driven Codex or Claude Code session with authenticated accounts and add it to
   COMPATIBILITY.md.
4. When XAX exposes libraries (strings, JSON) through the carrier, add a capability and a gap test that fails
   until the semantics run end to end. Until then, keep them UNIMPLEMENTED.
5. Optional cgroup v2 limits when a delegated cgroup is available.

## Rules
- No workload logic in the adapter: no per-operation tools and no Python fallbacks.
- Keep XAX changes in `MrxSiN/XAX`, and keep this repository's dependency direction one-way.
- Update `compat.TESTED_XAX`, `pyproject.toml`, CI, and COMPATIBILITY.md together.
