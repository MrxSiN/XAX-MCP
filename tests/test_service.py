"""In-process tests of the service core (the same code the MCP tools call)."""
from __future__ import annotations

import secrets

import pytest

import programs
from conftest import needs_sandbox
from xax_mcp.errors import ToolError


def _ints(values):
    return {"ints": [{"type": "b64", "value": v} for v in values]}


def _code(callable_, *args):
    with pytest.raises(ToolError) as caught:
        callable_(*args)
    return caught.value


def test_capabilities_report_real_compiler_and_target(service, session):
    caps = service.capabilities(session)
    assert caps["xax"]["status"] == "tested"
    assert caps["xax"]["matched_commit"] == caps["xax"]["pinned_commit"]
    target = caps["targets"][0]  # the host's platform comes first
    profile = "x86_64-windows-pe-v1" if programs.WINDOWS else "x86_64-linux-elf-exec-v1"
    assert target["id"] == programs.PLATFORM and target["profile"] == profile
    assert "add.wrap" in target["operations"] and "checked.load.bits.le" in target["operations"]
    assert {t["id"] for t in caps["targets"]} == {"linux-x86_64", "windows-x86_64"}
    assert not any(t["execute"]["available"] for t in caps["targets"][1:])
    assert caps["io"]["argv"] is not programs.WINDOWS and caps["effects"]["supported"] == ["stdio"]


@needs_sandbox
def test_novel_random_computation_runs_as_xax_generated_code(service, session):
    """Coefficients and inputs are drawn at test time: no server-side code can know the answer in advance."""
    a, b, c = (secrets.randbelow(1 << 32) for _ in range(3))
    xs = [secrets.randbelow(1 << 64) for _ in range(1 + secrets.randbelow(40))]
    built = service.construct(session, {"request": programs.poly_reduce(a, b, c)})
    assert built["verified"] is True
    artifact = service.build(session, {"workspace": built["workspace"]})
    assert artifact["executable_here"] and artifact["bytes"] > 0
    run = service.execute(session, {"artifact": artifact["artifact"], "input": _ints(xs), "output": {"ints": ["b64", "b64"]}})
    assert run["ok"] and run["status"] == "exited"
    assert [v["value"] for v in run["stdout"]["values"]] == list(programs.poly_reduce_oracle(a, b, c, xs))
    assert run["evidence"]["artifact_digest_blake3"] == artifact["artifact_digest_blake3"]


@needs_sandbox
def test_semantic_edit_changes_the_executed_result(service, session):
    """The result follows the committed XAX graph: editing one constant node changes the native output."""
    built = service.construct(session, {"request": programs.poly_reduce(1, 0, 0)})
    ws = built["workspace"]
    term = built["function_handles"]["term"]
    nodes = service.query(session, {"workspace": ws, "kind": "function_nodes", "handle": term, "limit": 32})["result"]["entities"]
    # In ``term`` the constants are a (multiplier of x^2), b, c in node order.
    constants = [n for n in nodes if n["operation"] == "constant"]
    assert [n["constant_value"] for n in constants] == [1, 0, 0]
    before = service.build(session, {"workspace": ws})
    run = lambda art: service.execute(session, {"artifact": art, "input": _ints([3, 4]), "output": {"ints": ["b64", "b64"]}})
    assert run(before["artifact"])["stdout"]["values"][0]["value"] == 25
    committed = service.transaction(session, {"workspace": ws, "mode": "commit", "expected_generation": 0,
                                             "expected_root": built["root"],
                                             "mutations": [{"op": "set_constant", "node": constants[2]["handle"], "value": 100}]})
    assert committed["committed"] and committed["generation"] == 1
    after = service.build(session, {"workspace": ws})
    assert after["artifact_digest_blake3"] != before["artifact_digest_blake3"]
    assert run(after["artifact"])["stdout"]["values"][0]["value"] == 225
    stale = _code(service.execute, session, {"artifact": before["artifact"], "input": _ints([3])})
    assert stale.code == "stale_artifact"
    old = service.execute(session, {"artifact": before["artifact"], "input": _ints([3, 4]), "output": {"ints": ["b64", "b64"]},
                                    "require_current": False})
    assert old["stdout"]["values"][0]["value"] == 25


def test_stale_root_is_rejected_not_refreshed(service, session):
    built = service.construct(session, {"request": programs.poly_reduce(2, 3, 4)})
    ws, root = built["workspace"], built["root"]
    term = built["function_handles"]["term"]
    nodes = service.query(session, {"workspace": ws, "kind": "function_nodes", "handle": term})["result"]["entities"]
    node = [n for n in nodes if n["operation"] == "constant"][0]["handle"]
    edit = {"workspace": ws, "mode": "commit", "expected_generation": 0, "expected_root": root,
            "mutations": [{"op": "set_constant", "node": node, "value": 9}]}
    assert service.transaction(session, edit)["committed"]
    again = _code(service.transaction, session, edit)
    assert again.code == "stale_root" and again.details["current_generation"] == 1
    wrong_root = _code(service.transaction, session, {**edit, "expected_generation": 1})
    assert wrong_root.code == "stale_root"


def test_verify_then_rollback_leaves_root_unchanged(service, session):
    built = service.construct(session, {"request": programs.poly_reduce(2, 3, 4)})
    ws = built["workspace"]
    term = built["function_handles"]["term"]
    nodes = service.query(session, {"workspace": ws, "kind": "function_nodes", "handle": term})["result"]["entities"]
    node = [n for n in nodes if n["operation"] == "constant"][1]["handle"]
    verified = service.transaction(session, {"workspace": ws, "mode": "verify", "expected_generation": 0, "expected_root": built["root"],
                                            "mutations": [{"op": "set_constant", "node": node, "value": 77}]})
    assert verified["candidate"]
    rolled = service.transaction(session, {"workspace": ws, "mode": "rollback", "candidate": verified["candidate"]})
    assert rolled["rolled_back"] and rolled["root"] == built["root"] and rolled["generation"] == 0
    assert _code(service.transaction, session, {"workspace": ws, "mode": "rollback", "candidate": verified["candidate"]}).code == "not_found"


def test_invalid_edit_reports_xax_diagnostic(service, session):
    built = service.construct(session, {"request": programs.poly_reduce(2, 3, 4)})
    ws = built["workspace"]
    term = built["function_handles"]["term"]
    nodes = service.query(session, {"workspace": ws, "kind": "function_nodes", "handle": term})["result"]["entities"]
    mul = nodes[0]["handle"]  # mul.wrap x*x
    error = _code(service.transaction, session, {"workspace": ws, "mode": "commit", "expected_generation": 0, "expected_root": built["root"],
                                                 "mutations": [{"op": "set_constant", "node": mul, "value": 1}]})
    assert error.code in ("invalid_request", "verification_failed", "unsupported")
    assert service.query(session, {"workspace": ws, "kind": "root"})["result"]["generation"] == 0


def test_construct_rejects_semantic_errors_with_diagnostics(service, session):
    request = programs.poly_reduce(1, 1, 1)
    request["functions"][3]["blocks"][3]["end"][1][1] = "p0"  # return a consumed process effect
    error = _code(service.construct, session, {"request": request})
    assert error.code in ("verification_failed", "invalid_request")
    bad_op = programs.poly_reduce(1, 1, 1)
    bad_op["functions"][2]["blocks"][0]["nodes"][0][0] = "python.eval"
    assert _code(service.construct, session, {"request": bad_op}).code == "invalid_request"


def test_build_is_cached_and_reproducible(service, session):
    built = service.construct(session, {"request": programs.poly_reduce(5, 6, 7)})
    first = service.build(session, {"workspace": built["workspace"]})
    second = service.build(session, {"workspace": built["workspace"]})
    assert first["cache"] == "miss" and second["cache"] == "hit" and first["artifact"] == second["artifact"]
    other = service.construct(session, {"request": programs.poly_reduce(5, 6, 7)})
    assert other["root"] == built["root"]  # canonical identity is deterministic
    rebuilt = service.build(session, {"workspace": other["workspace"]})
    assert rebuilt["artifact_digest_blake3"] == first["artifact_digest_blake3"]
    prov = first["provenance"]
    for key in ("build_key", "provenance_cid", "compiler_identity", "xax_toolchain_fingerprint", "xax_commit", "target_profile"):
        assert prov[key]


def test_query_kinds_are_bounded(service, session):
    # The byte-composed load64 has 39 nodes, enough to exercise pagination.
    built = service.construct(session, {"request": programs.poly_reduce(1, 2, 3, wide=False)})
    ws = built["workspace"]
    page = service.query(session, {"workspace": ws, "kind": "function_nodes", "handle": built["function_handles"]["load64_in"], "limit": 5})
    assert len(page["result"]["entities"]) == 5 and page["result"]["truncated"] and page["result"]["continuation"] == 5
    view = service.query(session, {"workspace": ws, "kind": "function_view", "handle": built["function_handles"]["term"]})
    assert "not XAX source" in view["result"]["classification"]
    functions = service.query(session, {"workspace": ws, "kind": "functions"})["result"]["entities"]
    assert any(f.get("entries") == ["app"] for f in functions)
    exported = service.result(session, {"handle": ws, "length": 64})
    assert exported["kind"] == "canonical_store" and exported["continuation"] == 64


@needs_sandbox
@pytest.mark.skipif(programs.WINDOWS, reason="the windows-x86_64 carrier has no startup reads (XAX ADR-252)")
def test_argv_reaches_startup_reads(service, session):
    built = service.construct(session, {"request": programs.echo_argument()})
    artifact = service.build(session, {"workspace": built["workspace"]})["artifact"]
    run = service.execute(session, {"artifact": artifact, "argv": ["meaning is source", "--probe", "--", "x"], "output": "text"})
    assert (run["exit_status"], run["stdout"]["text"]) == (5, "meaning is source")
    assert _code(service.execute, session, {"artifact": artifact, "argv": ["a\0b"]}).code == "invalid_request"


def test_capabilities_report_host_contract(service, session):
    caps = service.capabilities(session)
    assert caps["xax"]["host_contract"]["contract"] == "xax-host-contract-v1"
    linux = next(t for t in caps["targets"] if t["id"] == "linux-x86_64")
    assert linux["process_contract"]["identity"] == "linux-x86_64-process-v1"
    assert "linux.startup.arg_copy" in linux["carrier_entities"]
    windows = next(t for t in caps["targets"] if t["id"] == "windows-x86_64")
    assert "win32.read_file" in windows["carrier_entities"] and "win32.exit_process" in windows["carrier_entities"]


def test_windows_argv_is_refused_not_dropped(service, session):
    if not programs.WINDOWS:
        pytest.skip("Windows only")
    built = service.construct(session, {"request": programs.echo_stdin()})
    artifact = service.build(session, {"workspace": built["workspace"]})["artifact"]
    assert _code(service.execute, session, {"artifact": artifact, "argv": ["x"]}).code == "unsupported"


def test_other_platform_builds_but_does_not_run_here(service, session):
    other, prefix, exit_ = ("linux-x86_64", "linux.", "exit_group") if programs.WINDOWS else ("windows-x86_64", "win32.", "exit_process")
    request = {"format": "xax-construct-v1", "platform": other, "types": {"proc": prefix + "process_effect"},
               "functions": [{"name": "main", "params": ["proc"], "returns": ["b32", "proc"], "blocks": [
                   {"params": ["proc"], "nodes": [["call.foreign", [["b32", 7], "p0"], ["proc"], {"entity": prefix + exit_}]],
                    "end": ["ret", [["b32", 7], "n0"]]}]}],
               "package": {"name": "other", "entries": {"app": "main"}, "release": "app"}}
    built = service.construct(session, {"request": request})
    artifact = service.build(session, {"workspace": built["workspace"]})
    assert artifact["executable_here"] is False
    assert _code(service.execute, session, {"artifact": artifact["artifact"]}).code == "unsupported"


@needs_sandbox
def test_wide_byte_view_access_matches_byte_composition_and_is_smaller(service, session):
    """XAX ADR-231: one 8-byte checked load/store on a byte view computes what eight 1-byte accesses compute."""
    a, b, c = (secrets.randbelow(1 << 32) for _ in range(3))
    xs = [secrets.randbelow(1 << 64) for _ in range(9)]
    results, sizes = {}, {}
    for wide in (True, False):
        built = service.construct(session, {"request": programs.poly_reduce(a, b, c, wide=wide)})
        artifact = service.build(session, {"workspace": built["workspace"]})
        run = service.execute(session, {"artifact": artifact["artifact"], "input": _ints(xs), "output": {"ints": ["b64", "b64"]}})
        results[wide] = [v["value"] for v in run["stdout"]["values"]]
        sizes[wide] = artifact["bytes"]
    assert results[True] == results[False] == list(programs.poly_reduce_oracle(a, b, c, xs))
    assert sizes[True] < sizes[False]


def test_capabilities_report_checked_byte_view_widths(service, session):
    assert service.capabilities(session)["targets"][0]["checked_byte_view_widths"] == [1, 2, 4, 8]


def test_non_contract_byte_view_width_is_rejected_by_xax(service, session):
    request = programs.poly_reduce(1, 1, 1)
    load = request["functions"][0]["blocks"][0]["nodes"][0]
    load[2][0], load[3]["attrs"] = "b32", [3, 1]  # a 3-byte access: not in checked_byte_view_widths
    error = _code(service.construct, session, {"request": request})
    assert error.code == "verification_failed" and error.diagnostic["rule"] == "MEMORY-ACCESS-SIZE"
