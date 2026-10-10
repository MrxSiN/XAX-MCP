"""The per-user warm server (src/xax_mcp/warm.py): launches fork from a process with the XAX components loaded.

Each test checks a property the in-process server already has: real XAX results, per-launch authority, isolated
sessions, and cleanup when a client goes away.
"""
from __future__ import annotations

import json
import os
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import anyio
import pytest

import programs
from conftest import needs_sandbox

pytestmark = pytest.mark.skipif(not sys.platform.startswith("linux"), reason="the warm server is Linux-only")


def _env(directory: str, **extra: str) -> dict:
    keep = {k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "LANG", "TMPDIR") or
            (k.startswith("XAX_") and not k.startswith("XAX_MCP_"))}
    return {**keep, "XAX_MCP_WARM_SERVER": "1", "XAX_MCP_WARM_DIR": directory, "XAX_MCP_WARM_IDLE_SECONDS": "120",
            "XAX_MCP_LOG": "WARNING", **extra}


def _warm_pids(directory: str) -> list[int]:
    pids = []
    for entry in Path("/proc").iterdir():
        if entry.name.isdigit():
            try:
                argv = (entry / "cmdline").read_bytes().split(b"\0")
            except OSError:
                continue
            if b"xax_mcp.warm" in argv and directory.encode() in argv:
                pids.append(int(entry.name))
    return pids


def _children(pid: int) -> set[int]:
    found = set()
    for entry in Path("/proc").iterdir():
        if entry.name.isdigit():
            try:
                stat = (entry / "stat").read_text()
            except OSError:
                continue
            if int(stat.rsplit(")", 1)[1].split()[1]) == pid:
                found.add(int(entry.name))
    return found


@pytest.fixture(scope="module")
def warm_dir():
    directory = tempfile.mkdtemp(prefix="xw-")
    os.chmod(directory, 0o700)
    prepared = subprocess.run([sys.executable, "-m", "xax_mcp", "--prepare"], env=_env(directory), capture_output=True,
                              timeout=900)
    assert prepared.returncode == 0, prepared.stderr.decode()[-2000:]
    report = json.loads(prepared.stdout)
    assert report["warm_server"] == "ready"
    # Through the host contract (xax_native.prepare, ADR-250): every component XAX names, each readied or reported.
    from xax_native import PREPARE_COMPONENTS

    assert set(report["xax_components"]) == set(PREPARE_COMPONENTS)
    assert set(report["xax_components"].values()) <= {"cached", "lowered", "unavailable"}
    yield directory
    for pid in _warm_pids(directory):
        os.kill(pid, signal.SIGTERM)
    shutil.rmtree(directory, ignore_errors=True)


def _params(directory: str, *args: str, **env: str):
    from mcp.client.stdio import StdioServerParameters

    return StdioServerParameters(command=sys.executable, args=["-m", "xax_mcp", *args], env=_env(directory, **env))


async def _call(client, name, arguments=None):
    return (await client.call_tool(name, arguments or {})).structured_content


@needs_sandbox
def test_launches_fork_from_the_warm_server_with_isolated_sessions_and_their_own_rights(warm_dir):
    from mcp import Client

    a, b, c = (secrets.randbelow(1 << 40) for _ in range(3))
    xs = [secrets.randbelow(1 << 64) for _ in range(9)]

    async def scenario():
        started = time.perf_counter()
        async with Client(_params(warm_dir, "--allow-execute"), read_timeout_seconds=600) as first:
            caps = await _call(first, "xax_capabilities")
            assert caps["server"]["started_from"] == "warm-server" and caps["server"]["xax_components_loaded"]
            assert set(caps["server"]["xax_components"].values()) <= {"cached", "loaded", "unavailable"}
            assert caps["xax"]["status"] == "tested" and "execute" in caps["authority"]["rights"]
            built = await _call(first, "xax_construct", {"request": programs.poly_reduce(a, b, c)})
            artifact = await _call(first, "xax_build", {"workspace": built["workspace"]})
            run = await _call(first, "xax_execute", {"artifact": artifact["artifact"],
                                                     "input": {"ints": [{"type": "b64", "value": x} for x in xs]},
                                                     "output": {"ints": ["b64", "b64"]}})
            first_result_s = time.perf_counter() - started
            assert [v["value"] for v in run["stdout"]["values"]] == list(programs.poly_reduce_oracle(a, b, c, xs))
            # A second launch through the same warm server: no execute right, and none of the first client's handles.
            async with Client(_params(warm_dir), read_timeout_seconds=600) as second:
                caps2 = await _call(second, "xax_capabilities")
                assert caps2["server"]["started_from"] == "warm-server"
                assert "execute" not in caps2["authority"]["rights"]
                foreign = await _call(second, "xax_query", {"workspace": built["workspace"], "kind": "root"})
                assert foreign["error"]["code"] == "not_found"
                own = await _call(second, "xax_construct", {"request": programs.poly_reduce(a, b, c)})
                assert own["root"] == built["root"] and own["workspace"] != built["workspace"]
                art2 = await _call(second, "xax_build", {"workspace": own["workspace"]})
                denied = await _call(second, "xax_execute", {"artifact": art2["artifact"]})
                assert denied["error"]["code"] == "denied_capability"
        return first_result_s

    first_result_s = anyio.run(scenario)
    print(json.dumps({"warm_server_first_construct_build_execute_s": round(first_result_s, 3)}))


def test_child_exits_when_its_launcher_dies(warm_dir):
    [server] = _warm_pids(warm_dir)
    before = _children(server)
    launcher = subprocess.Popen([sys.executable, "-m", "xax_mcp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, env=_env(warm_dir))
    hello = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "raw", "version": "0"}}}
    launcher.stdin.write((json.dumps(hello) + "\n").encode())
    launcher.stdin.flush()
    assert json.loads(launcher.stdout.readline())["id"] == 1  # answered by the forked child
    new = _children(server) - before
    assert len(new) == 1
    launcher.kill()  # SIGKILL: the launcher cannot clean up; the child must notice on its own
    launcher.wait()
    deadline = time.monotonic() + 10
    while new & _children(server) and time.monotonic() < deadline:
        time.sleep(0.05)
    assert not new & _children(server)
    launcher.stdin.close()
    launcher.stdout.close()


def test_stdin_eof_ends_the_child_and_the_launcher_reports_its_status(warm_dir):
    done = subprocess.run([sys.executable, "-m", "xax_mcp"], input=b"", capture_output=True, env=_env(warm_dir), timeout=60)
    assert done.returncode == 0 and done.stdout == b""


def test_launch_errors_reach_the_client_stderr(warm_dir):
    done = subprocess.run([sys.executable, "-m", "xax_mcp", "--wall-ms", "1"], input=b"", capture_output=True,
                          env=_env(warm_dir), timeout=60)
    assert done.returncode == 1 and b"--wall-ms must be within" in done.stderr and done.stdout == b""


def test_different_xax_configuration_never_reaches_this_server(warm_dir):
    from xax_mcp import warm

    old = os.environ.get("XAX_NATIVE_CACHE")
    try:
        first = warm.key()
        os.environ["XAX_NATIVE_CACHE"] = "/nonexistent-other-cache"
        assert warm.key() != first
    finally:
        if old is None:
            os.environ.pop("XAX_NATIVE_CACHE", None)
        else:
            os.environ["XAX_NATIVE_CACHE"] = old


def test_shared_or_foreign_directory_is_refused(tmp_path):
    from xax_mcp import warm

    shared = tmp_path / "shared"
    shared.mkdir(mode=0o755)
    os.chmod(shared, 0o755)
    old = os.environ.get(warm.DIR_ENV)
    os.environ[warm.DIR_ENV] = str(shared)
    try:
        with pytest.raises(OSError):
            warm._state_dir()
        assert warm.launch([]) is None  # falls back to serving in-process, and starts nothing
        assert list(shared.iterdir()) == []
    finally:
        if old is None:
            os.environ.pop(warm.DIR_ENV, None)
        else:
            os.environ[warm.DIR_ENV] = old


@pytest.mark.skipif(getattr(os, "geteuid", lambda: -1)() != 0, reason="needs root to connect as another user")
def test_another_user_cannot_connect(warm_dir):
    from xax_mcp import warm

    path = warm.socket_path(Path(warm_dir), _key_for(warm_dir))
    assert path.exists()
    probe = ("import os, socket, sys\nos.setgid(65534)\nos.setuid(65534)\ns = socket.socket(socket.AF_UNIX)\n"
             "try:\n    s.connect(sys.argv[1])\nexcept PermissionError:\n    sys.exit(0)\nsys.exit(1)\n")
    done = subprocess.run([sys.executable, "-I", "-c", probe, str(path)], timeout=30)
    assert done.returncode == 0


def _key_for(directory: str) -> str:
    out = subprocess.run([sys.executable, "-c", "from xax_mcp import warm; print(warm.key())"], capture_output=True,
                         env=_env(directory), check=True)
    return out.stdout.decode().strip()


def test_launcher_serves_itself_when_the_warm_server_does_not_acknowledge(tmp_path):
    """A socket that takes the descriptors but never forks a child must not swallow the client."""
    import socket
    import threading

    from xax_mcp import warm

    directory = Path(tempfile.mkdtemp(prefix="xn-"))
    os.chmod(directory, 0o700)
    old = os.environ.get(warm.DIR_ENV)
    os.environ[warm.DIR_ENV] = str(directory)
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        with warm._Short(directory) as short:
            listener.bind(short(warm.socket_path(directory, warm.key())))
        listener.listen(1)

        def refuse():
            connection, _ = listener.accept()
            connection.recv(65536)
            connection.close()

        threading.Thread(target=refuse, daemon=True).start()
        before = [(os.fstat(fd).st_dev, os.fstat(fd).st_ino) for fd in (0, 1)]
        assert warm.launch(["--allow-execute"]) is None
        assert [(os.fstat(fd).st_dev, os.fstat(fd).st_ino) for fd in (0, 1)] == before  # STDIO was not given away
    finally:
        listener.close()
        shutil.rmtree(directory, ignore_errors=True)
        if old is None:
            os.environ.pop(warm.DIR_ENV, None)
        else:
            os.environ[warm.DIR_ENV] = old
