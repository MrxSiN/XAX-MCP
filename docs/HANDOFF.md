# Handoff

## State at 0.1.0 (2026-10-08)
- STDIO MCP server with 8 tools over the pinned XAX `01ad841`. Construct, query, transact, build, and
  sandboxed execute all run end to end.
- Tests: `tests/test_service.py`, `tests/test_security.py`, `tests/test_e2e_stdio.py`,
  `tests/test_compat.py`, `tests/test_upstream_store.py` (needs `XAX_SOURCE_DIR`). The full suite takes about
  3–4 minutes on the reference host, mostly XAX warm-up per launched server.
- Evidence: `docs/evidence/` (record new runs with `scripts/record_evidence.py`; never overwrite old files).

## Next steps, in order of leverage
1. Upstream P3 (persist verified component images) would remove the 20–50 s first-call delay.
2. Upstream P1 (startup entities in the carrier) would allow argv input; then add an `argv` input mode here.
3. Record a model-driven Codex or Claude Code session with authenticated accounts and add it to
   COMPATIBILITY.md.
4. When XAX exposes libraries (strings, JSON) through the carrier, add a capability and a gap test that fails
   until the semantics run end to end. Until then, keep them UNIMPLEMENTED.
5. Optional cgroup v2 limits when a delegated cgroup is available.

## Rules
- No workload logic in the adapter: no per-operation tools and no Python fallbacks.
- Keep XAX changes in `MrxSiN/XAX`, and keep this repository's dependency direction one-way.
- Update `compat.TESTED_XAX`, `pyproject.toml`, CI, and COMPATIBILITY.md together.
