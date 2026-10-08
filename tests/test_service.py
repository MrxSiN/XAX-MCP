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
    target = caps["targets"][0]
    assert target["id"] == "linux-x86_64" and target["profile"] == "x86_64-linux-elf-exec-v1"
    assert "add.wrap" in target["operations"] and "checked.load.bits.le" in target["operations"]
    assert caps["io"]["argv"] is False and caps["effects"]["supported"] == ["stdio"]


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
    built = service.construct(session, {"request": programs.poly_reduce(1, 2, 3)})
    ws = built["workspace"]
    page = service.query(session, {"workspace": ws, "kind": "function_nodes", "handle": built["function_handles"]["load64_in"], "limit": 5})
    assert len(page["result"]["entities"]) == 5 and page["result"]["truncated"] and page["result"]["continuation"] == 5
    view = service.query(session, {"workspace": ws, "kind": "function_view", "handle": built["function_handles"]["term"]})
    assert "not XAX source" in view["result"]["classification"]
    functions = service.query(session, {"workspace": ws, "kind": "functions"})["result"]["entities"]
    assert any(f.get("entries") == ["app"] for f in functions)
    exported = service.result(session, {"handle": ws, "length": 64})
    assert exported["kind"] == "canonical_store" and exported["continuation"] == 64
