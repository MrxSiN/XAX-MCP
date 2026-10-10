"""Security regression tests: authority, handles, quotas, sandbox enforcement, fail-closed behaviour."""
from __future__ import annotations

import os
import threading

import pytest

import programs
from conftest import ALL_RIGHTS, needs_sandbox
from xax_mcp.errors import ToolError
from xax_mcp.policy import Policy
from xax_mcp.sandbox import ProbeResult, Sandbox
from xax_mcp.service import Session


def _code(callable_, *args):
    with pytest.raises(ToolError) as caught:
        callable_(*args)
    return caught.value.code


@pytest.fixture()
def built(service, session):
    def make(request):
        ws = service.construct(session, {"request": request})
        return service.build(session, {"workspace": ws["workspace"]})["artifact"]
    return make


def test_forged_and_foreign_handles_are_rejected(service, session):
    ws = service.construct(session, {"request": programs.poly_reduce(1, 1, 1)})["workspace"]
    other = Session(service.policy)
    assert _code(service.query, other, {"workspace": ws, "kind": "root"}) == "not_found"
    assert _code(service.query, session, {"workspace": "ws_" + "0" * 24, "kind": "root"}) == "not_found"
    assert _code(service.execute, session, {"artifact": "art_deadbeef"}) == "not_found"
    assert _code(service.result, other, {"handle": ws}) == "not_found"


def test_rights_come_from_host_policy_not_arguments(service, session):
    from xax_mcp.service import Service

    read_only = Service(Policy(rights=frozenset({"read"})), service.sandbox)
    s = Session(read_only.policy)
    assert _code(read_only.construct, s, {"request": programs.poly_reduce(1, 1, 1)}) == "denied_capability"
    no_exec = Service(Policy(rights=frozenset({"read", "mutate", "build"})), service.sandbox)
    s = Session(no_exec.policy)
    ws = no_exec.construct(s, {"request": programs.poly_reduce(1, 1, 1)})["workspace"]
    art = no_exec.build(s, {"workspace": ws})["artifact"]
    assert _code(no_exec.execute, s, {"artifact": art, "effects": ["stdio"]}) == "denied_capability"


@needs_sandbox
def test_undeclared_effects_are_denied(service, session, built):
    art = built(programs.poly_reduce(1, 1, 1))
    for effect in ("filesystem.read", "network", "process", "environment"):
        assert _code(service.execute, session, {"artifact": art, "effects": ["stdio", effect]}) == "denied_capability"


def test_execution_fails_closed_without_sandbox(service, session):
    from xax_mcp.service import Service

    class NoSandbox(Sandbox):
        def probe(self):
            return ProbeResult(False, "simulated: user namespaces disabled")

        def _launch(self, *args, **kwargs):  # pragma: no cover - must never be reached
            raise AssertionError("artifact launched without sandbox")

    svc = Service(Policy(rights=ALL_RIGHTS), NoSandbox())
    s = Session(svc.policy)
    ws = svc.construct(s, {"request": programs.poly_reduce(1, 1, 1)})["workspace"]
    art = svc.build(s, {"workspace": ws})["artifact"]
    assert _code(svc.execute, s, {"artifact": art}) == "sandbox_unavailable"
    assert svc.capabilities(s)["targets"][0]["execute"]["available"] is False


@needs_sandbox
@pytest.mark.skipif(programs.WINDOWS, reason="the windows-x86_64 carrier has no file-open entity; the probe checks the LPAC token")
def test_filesystem_is_unreachable_from_artifacts(service, session, built):
    art = built(programs.open_file(b"/etc/passwd"))
    run = service.execute(session, {"artifact": art, "output": {"ints": ["b64"]}})
    assert run["stdout"]["values"][0]["signed"] == -1  # -EPERM from the seccomp allowlist


def test_open_file_program_opens_files_when_unconfined(service, session, tmp_path):
    """Positive control for the test above: the same XAX program does open files outside the sandbox."""
    import sys

    if not sys.platform.startswith("linux"):
        pytest.skip("Linux only")
    from xax_linux import run_linux_executable

    ws = service.construct(session, {"request": programs.open_file(b"/etc/hostname")})
    data = session.artifacts[service.build(session, {"workspace": ws["workspace"]})["artifact"]].data
    completed = run_linux_executable(data, timeout=10)
    assert completed.returncode == 0 and int.from_bytes(completed.stdout, "little", signed=True) >= 0


@needs_sandbox
def test_wall_time_limit_kills_spinning_artifact(service, session, built):
    art = built(programs.spin())
    error = pytest.raises(ToolError, service.execute, session, {"artifact": art, "limits": {"wall_ms": 300}}).value
    assert error.code == "resource_limit" and "wall-time" in error.message


@needs_sandbox
def test_cpu_limit_is_enforced(service, session, built):
    art = built(programs.spin())
    error = pytest.raises(ToolError, service.execute, session, {"artifact": art, "limits": {"cpu_seconds": 1, "wall_ms": 5000}}).value
    assert error.code == "resource_limit"


@needs_sandbox
def test_output_quota_kills_flooding_artifact(service, session, built):
    art = built(programs.flood())
    error = pytest.raises(ToolError, service.execute, session, {"artifact": art, "limits": {"max_output_bytes": 100_000}}).value
    assert error.code == "resource_limit" and "stdout" in error.message


@needs_sandbox
def test_cancellation_kills_the_process(service, session, built):
    art = built(programs.spin())
    cancel = threading.Event()
    timer = threading.Timer(0.3, cancel.set)
    timer.start()
    error = pytest.raises(ToolError, service.execute, session, {"artifact": art, "limits": {"wall_ms": 20000}}, cancel).value
    assert error.code == "runtime_failure" and "cancelled" in error.message
    assert error.details["evidence"]["wall_ms"] < 5000


def test_requested_limits_cannot_exceed_policy(service, session):
    small = Policy(rights=ALL_RIGHTS)
    assert small.limits.wall_ms == 5000  # tool arguments may only lower limits (min() in Service.execute)


@needs_sandbox
def test_tampered_artifact_is_refused(service, session, built):
    art = built(programs.poly_reduce(1, 2, 3))
    entry = session.artifacts[art]
    entry.data = entry.data[:-1] + bytes([entry.data[-1] ^ 1])
    assert _code(service.execute, session, {"artifact": art}) == "stale_artifact"


def test_oversized_and_malformed_requests_are_rejected_before_compilation(service, session):
    huge = programs.poly_reduce(1, 1, 1)
    huge["functions"][2]["blocks"][0]["nodes"][0][1][1] = ["b64", 1 << 70]
    assert _code(service.construct, session, {"request": huge}) == "invalid_request"
    deep = programs.poly_reduce(1, 1, 1)
    deep["types"]["x"] = [[[[[[[[[[[[[[1]]]]]]]]]]]]]]
    assert _code(service.construct, session, {"request": deep}) == "invalid_request"
    big_view = programs.poly_reduce(1, 1, 1)
    big_view["types"]["in"] = {"view": 1 << 40}
    assert _code(service.construct, session, {"request": big_view}) == "resource_limit"
    assert _code(service.construct, session, {"request": {"format": "text", "source": "def f(): pass"}}) == "invalid_request"
    assert _code(service.construct, session, {"request": {**programs.poly_reduce(1, 1, 1), "platform": "jvm"}}) == "unsupported"


def test_mutation_tokens_cannot_inject_extra_edits(service, session):
    ws = service.construct(session, {"request": programs.poly_reduce(1, 1, 1)})
    edit = {"workspace": ws["workspace"], "mode": "commit", "expected_generation": 0, "expected_root": ws["root"],
            "mutations": [{"op": "set_constant", "node": "F1.B0.N1; delete F1.B0.N0", "value": 1}]}
    assert _code(service.transaction, session, edit) == "invalid_request"


def test_store_roots_block_traversal_and_symlinks(service, tmp_path):
    from xax_mcp.policy import resolve_store

    root = tmp_path / "root"
    root.mkdir()
    secret = tmp_path / "secret.xax"
    secret.write_bytes(b"x")
    try:
        (root / "link.xax").symlink_to(secret)
    except OSError:  # Windows without Developer Mode cannot create symbolic links; the other names still apply
        pass
    policy = Policy(rights=ALL_RIGHTS, store_roots=(root.resolve(),))
    for name in ("../secret.xax", "/etc/passwd", r"C:\Windows\win.ini", r"..\secret.xax", "C:secret.xax", str(secret), "link.xax",
                 "a/../../secret.xax", "x.txt"):
        with pytest.raises(ToolError) as caught:
            resolve_store(policy, name)
        assert caught.value.code in ("invalid_request", "denied_capability", "not_found")
    with pytest.raises(ToolError) as caught:
        resolve_store(Policy(rights=ALL_RIGHTS), "a.xax")
    assert caught.value.code == "denied_capability"


def test_store_open_verifies_bytes(service, tmp_path):
    from xax_mcp.service import Service

    root = tmp_path / "stores"
    root.mkdir()
    (root / "garbage.xax").write_bytes(os.urandom(256))
    svc = Service(Policy(rights=ALL_RIGHTS, store_roots=(root.resolve(),)), service.sandbox)
    s = Session(svc.policy)
    assert _code(svc.workspace, s, {"action": "open", "store": "garbage.xax"}) in ("verification_failed", "invalid_request")


@needs_sandbox
def test_concurrent_executions_and_sessions_are_isolated(service, built, session):
    import secrets

    from programs import poly_reduce, poly_reduce_oracle

    sessions = [Session(service.policy) for _ in range(3)]
    jobs = []
    for s in sessions:
        a, b, c = (secrets.randbelow(1000) for _ in range(3))
        ws = service.construct(s, {"request": poly_reduce(a, b, c)})
        jobs.append((s, service.build(s, {"workspace": ws["workspace"]})["artifact"], (a, b, c)))
    results, errors = {}, []

    def run(index, s, art, coefficients):
        try:
            xs = [index + 1, index + 2, 1000 + index]
            out = service.execute(s, {"artifact": art, "input": {"ints": [{"type": "b64", "value": x} for x in xs]},
                                      "output": {"ints": ["b64", "b64"]}})
            results[index] = ([v["value"] for v in out["stdout"]["values"]], list(poly_reduce_oracle(*coefficients, xs)))
        except Exception as error:  # pragma: no cover
            errors.append(error)

    threads = [threading.Thread(target=run, args=(i, *job)) for i, job in enumerate(jobs * 3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors and len(results) == len(threads)
    assert all(got == want for got, want in results.values())
    # Artifacts of one session are invisible to another.
    assert _code(service.execute, sessions[0], {"artifact": jobs[1][1]}) == "not_found"
