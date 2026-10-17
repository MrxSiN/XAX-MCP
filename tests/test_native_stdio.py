"""The native XAX server (native/server.py) over its real STDIO transport, as a Windows x86-64 executable.

The executable is the PE32+ that XAX builds from the committed canonical store.  Set XAX_NATIVE_SRC to a checkout's
``compiler/src`` at ``NATIVE_XAX_COMMIT`` (the test rebuilds the store, checks it byte for byte against the committed
one, and builds the PE), or XAX_MCP_NATIVE_EXE to an already built executable.  XAX_MCP_REFERENCE_PYTHON (an
interpreter with this repository's dependencies) adds the differential run against this tree's Python server.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import platform
import queue
import random
import subprocess
import sys
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "native"
WINDOWS_X86_64 = sys.platform == "win32" and platform.machine().lower() in ("amd64", "x86_64")
pytestmark = pytest.mark.skipif(not WINDOWS_X86_64, reason="the native server is a windows-x86_64 PE32+ executable")
VERSIONS = ("2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25")
TOOLS = ("xax_capabilities", "xax_workspace", "xax_query", "xax_construct", "xax_transaction", "xax_build",
         "xax_execute", "xax_result")
RIGHT_OF = {"xax_workspace": "read", "xax_query": "read", "xax_construct": "mutate", "xax_transaction": "mutate",
            "xax_build": "build", "xax_execute": "execute", "xax_result": "read"}
LMAX = 4 * 1024 * 1024


def _schemas():
    spec = importlib.util.spec_from_file_location("native_test_schemas", ROOT / "src/xax_mcp/schemas.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def exe(tmp_path_factory) -> str:
    if os.environ.get("XAX_MCP_NATIVE_EXE"):
        return os.environ["XAX_MCP_NATIVE_EXE"]
    source = os.environ.get("XAX_NATIVE_SRC")
    if not source:
        pytest.skip("set XAX_NATIVE_SRC (XAX compiler/src at NATIVE_XAX_COMMIT) or XAX_MCP_NATIVE_EXE")
    out = tmp_path_factory.mktemp("native")
    subprocess.run([sys.executable, str(NATIVE / "server.py"), source, str(out)], check=True, capture_output=True, timeout=900)
    for name in ("xax-mcp-native-gen0.xax", "construction_request.json"):  # the committed store is its builder's output
        assert (out / name).read_bytes() == (NATIVE / name).read_bytes(), name
    return str(out / "xax-mcp-native.exe")


class Server:
    """One native server process; ``exchange`` sends a line and waits for exactly one response line."""

    def __init__(self, exe: str, *args: str):
        self.process = subprocess.Popen([exe, *args], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.lines: queue.Queue = queue.Queue()
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        for line in self.process.stdout:
            self.lines.put(line)
        self.lines.put(None)

    def send(self, message) -> None:
        data = message if isinstance(message, bytes) else json.dumps(message, separators=(",", ":")).encode()
        self.process.stdin.write(data if data.endswith(b"\n") else data + b"\n")
        self.process.stdin.flush()

    def receive(self, timeout: float = 30) -> dict:
        line = self.lines.get(timeout=timeout)
        assert line is not None, "server closed stdout"
        return json.loads(line)

    def exchange(self, message, timeout: float = 30) -> dict:
        self.send(message)
        return self.receive(timeout)

    def request(self, method: str, params=None, id_=1) -> dict:
        message = {"jsonrpc": "2.0", "id": id_, "method": method}
        if params is not None:
            message["params"] = params
        return self.exchange(message)

    def call(self, name: str, arguments=None, id_=1) -> dict:
        params = {"name": name} if arguments is None else {"name": name, "arguments": arguments}
        result = self.request("tools/call", params, id_)["result"]
        payload = result["structuredContent"]
        assert json.loads(result["content"][0]["text"]) == payload and result["content"][0]["type"] == "text"
        assert result["isError"] == (not payload["ok"])
        return payload

    def close(self, timeout: float = 30):
        self.process.stdin.close()
        rest = []
        while (line := self.lines.get(timeout=timeout)) is not None:
            rest.append(line)
        code = self.process.wait(timeout)
        return code, rest, self.process.stderr.read()


@pytest.fixture
def server(exe):
    s = Server(exe)
    yield s
    if s.process.poll() is None:
        s.process.kill()


def test_initialize_negotiates_handshake_versions(server):
    for k, version in enumerate(VERSIONS):
        result = server.request("initialize", {"protocolVersion": version, "capabilities": {},
                                               "clientInfo": {"name": "t", "version": "0"}}, k)["result"]
        assert result["protocolVersion"] == version
    for params in ({"protocolVersion": "1999-01-01"}, {"protocolVersion": 7}, {}, None, [1]):
        result = server.request("initialize", params)["result"]
        assert result["protocolVersion"] == "2025-11-25", params
    assert result["capabilities"] == {"tools": {"listChanged": False}}
    assert result["serverInfo"]["name"] == "xax-mcp" and result["serverInfo"]["version"].endswith("+native")
    assert "xax_capabilities -> xax_construct" in result["instructions"]
    assert server.close()[0] == 0


def test_ping_and_tools_list(server):
    assert server.request("ping", id_="p") == {"jsonrpc": "2.0", "id": "p", "result": {}}
    tools = server.request("tools/list")["result"]["tools"]
    schemas = _schemas()
    assert [tool["name"] for tool in tools] == list(TOOLS) == list(schemas.TOOLS)
    for tool in tools:
        spec = schemas.TOOLS[tool["name"]]
        assert (tool["title"], tool["description"], tool["inputSchema"], tool["annotations"]) == (
            spec["title"], spec["description"], spec["inputSchema"], spec["annotations"])
        assert tool["_meta"] == {"xax-mcp/schema": schemas.SCHEMA_VERSION}


def test_notifications_and_client_responses_get_no_reply(server):
    for message in ({"jsonrpc": "2.0", "method": "notifications/initialized"},
                    {"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 1}},
                    {"jsonrpc": "2.0", "method": "notifications/unknown"},
                    {"jsonrpc": "2.0", "id": 5, "result": {}},
                    {"jsonrpc": "2.0", "id": 6, "error": {"code": 1, "message": "x"}}):
        server.send(message)
    server.send(b"   \t ")  # blank lines are not messages
    assert server.request("ping", id_=9)["id"] == 9  # the next line is the ping's: nothing was answered before it
    code, rest, _ = server.close()
    assert (code, rest) == (0, [])


@pytest.mark.parametrize("line, code, has_id", [
    (b'{"jsonrpc":"2.0","id":4,"method":"nope"}', -32601, True),
    (b"not json", -32700, False),
    (b'{"jsonrpc":"2.0","id":1,"method":"ping"', -32700, False),
    (b"[1,2]", -32600, False),
    (b"42", -32600, False),
    (b'{"id":1,"method":"ping"}', -32600, True),
    (b'{"jsonrpc":"1.0","id":1,"method":"ping"}', -32600, True),
    (b'{"jsonrpc":2.0,"id":1,"method":"ping"}', -32600, True),
    (b'{"jsonrpc":"2.0","id":null,"method":"ping"}', -32600, False),
    (b'{"jsonrpc":"2.0","id":{"a":1},"method":"ping"}', -32600, False),
    (b'{"jsonrpc":"2.0","id":1,"method":7}', -32600, True),
    (b'{"jsonrpc":"2.0","id":1}', -32600, True),
    (b'{"jsonrpc":"2.0","id":1,"method":"tools/call"}', -32602, True),
    (b'{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":3}}', -32602, True),
    (b'{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"xax_query","arguments":[1]}}', -32602, True),
])
def test_jsonrpc_errors(server, line, code, has_id):
    response = server.exchange(line)
    assert response["jsonrpc"] == "2.0" and response["error"]["code"] == code
    assert (response["id"] is not None) == has_id
    if code == -32601:
        assert response["error"]["data"] == "nope"
    assert server.request("ping", id_=2)["result"] == {}  # the stream stays usable


def test_ids_are_echoed_exactly(server):
    for raw in (b'"a\\"b\\u00e9\xc3\xa9"', b"18446744073709551621", b"-9223372036854775809", b"1.5e3", b"0", b'""'):
        response = server.exchange(b'{"jsonrpc":"2.0","method":"ping","id":' + raw + b"}")
        assert response["id"] == json.loads(raw.decode()) and response["result"] == {}


def test_tool_dispatch_under_default_rights(server):
    payload = server.call("xax_capabilities", {})
    assert payload["ok"] and payload["authority"]["rights"] == ["build", "mutate", "read"]
    assert payload["server"]["python_on_request_path"] is False
    assert server.call("xax_capabilities") == payload  # arguments may be omitted
    for tool in TOOLS[1:]:
        payload = server.call(tool, {})
        if tool == "xax_execute":
            assert payload["error"]["code"] == "denied_capability"
            assert payload["error"]["repair"] == ["the host owner may add --allow-execute to the server launch command"]
        else:
            assert payload["error"]["code"] == "unsupported" and tool in payload["error"]["message"]
    assert server.call("bogus", {})["error"] == {"code": "unsupported", "message": "unknown tool 'bogus'"}


def test_capabilities_rejects_properties(server):
    error = server.call("xax_capabilities", {"x": 1})["error"]
    assert error == {"code": "invalid_request", "details": {"errors": 1},
                     "message": "(root): Additional properties are not allowed ('x' was unexpected)"}
    error = server.call("xax_capabilities", {"a": 1, "b": {"c": [2]}})["error"]
    assert error["code"] == "invalid_request" and "2 properties were unexpected" in error["message"]


@pytest.mark.parametrize("args, rights", [
    ((), ["build", "mutate", "read"]),
    (("--allow-execute",), ["build", "execute", "mutate", "read"]),
    (("--read-only",), ["read"]),
    (("--read-only", "--allow-execute"), ["read"]),
    (("--deny", "read"), ["build", "mutate"]),
    (("--deny=build", "--allow-execute", "--deny", "mutate"), ["execute", "read"]),
    (("--no-warm-server", "--deny=read", "--deny=mutate", "--deny=build"), []),
])
def test_host_rights_come_from_launch_flags(exe, args, rights):
    server = Server(exe, *args)
    try:
        assert server.call("xax_capabilities", {})["authority"]["rights"] == rights
        for tool, right in RIGHT_OF.items():
            # a tool argument never grants a right
            error = server.call(tool, {"rights": ["execute"], "allow_execute": True})["error"]
            assert error["code"] == ("unsupported" if right in rights else "denied_capability"), (tool, error)
    finally:
        server.process.kill()


@pytest.mark.parametrize("args", [("--grant", "read"), ("--wall-ms", "5"), ("--deny",), ("--deny", "everything"),
                                  ("--deny=exec",), ("--allow-execute-now",), ('--read-only"x',), ("-h",)])
def test_unknown_flags_fail_closed(exe, args):
    completed = subprocess.run([exe, *args], input=b'{"jsonrpc":"2.0","id":1,"method":"ping"}\n', capture_output=True, timeout=30)
    assert completed.returncode == 2 and completed.stdout == b""
    assert b"unsupported command-line argument" in completed.stderr


def test_limits(server):
    huge = b'{"jsonrpc":"2.0","id":1,"method":"ping","params":{"x":"' + b"a" * LMAX + b'"}}'
    response = server.exchange(huge)
    assert response["id"] is None and response["error"]["code"] == -32600 and str(LMAX) in response["error"]["message"]
    assert server.request("ping", id_=2)["id"] == 2
    big = "a" * (1024 * 1024)
    error = server.call("xax_query", {"x": big})["error"]
    size = len(json.dumps({"x": big}, separators=(",", ":")))
    assert error == {"code": "resource_limit", "message": f"arguments are {size} bytes; the limit is 1048576"}
    for depth, ok in ((63, True), (64, False)):  # the envelope object is one level; 64 levels in all are accepted
        line = b'{"jsonrpc":"2.0","id":3,"method":"ping","params":' + b"[" * depth + b"]" * depth + b"}"
        assert ("result" in server.exchange(line)) == ok, depth


def test_framing(server):
    assert server.exchange(b'{"jsonrpc":"2.0","id":1,"method":"ping"}\r\n')["id"] == 1  # CRLF clients
    for k in range(500):
        server.send({"jsonrpc": "2.0", "id": k, "method": "ping"})
    assert [server.receive()["id"] for _ in range(500)] == list(range(500))
    server.process.stdin.write(b'{"jsonrpc":"2.0","id":"last","method":"ping"}')  # no newline before EOF
    code, rest, stderr = server.close()
    assert code == 0 and [json.loads(line)["id"] for line in rest] == ["last"] and stderr == b""


def _random_json(rng: random.Random, depth: int = 0) -> bytes:
    ws = lambda: rng.choice([b"", b"", b" ", b"\t", b"\r", b" \t "])  # noqa: E731
    kind = rng.randrange(8 if depth < 12 else 5)
    if kind == 0:
        return rng.choice([b"true", b"false", b"null"])
    if kind == 1:
        number = rng.choice([b"0", b"-0", str(rng.randrange(10 ** rng.randrange(1, 25))).encode()])
        if rng.random() < 0.3:
            number += b"." + str(rng.randrange(1000)).encode()
        if rng.random() < 0.3:
            number += rng.choice([b"e", b"E"]) + rng.choice([b"", b"+", b"-"]) + str(rng.randrange(400)).encode()
        return number
    if kind in (2, 3, 4):
        parts = []
        for _ in range(rng.randrange(6)):
            choice = rng.randrange(6)
            if choice == 0:
                parts.append(rng.choice([b'\\"', b"\\\\", b"\\/", b"\\b", b"\\f", b"\\n", b"\\r", b"\\t"]))
            elif choice == 1:
                parts.append(b"\\u%04x" % rng.randrange(0x10000))
            elif choice == 2:
                parts.append(chr(rng.choice([rng.randrange(0x80, 0x800), rng.randrange(0x800, 0xD800),
                                             rng.randrange(0xE000, 0x10000), rng.randrange(0x10000, 0x110000)])).encode())
            else:
                parts.append(bytes(rng.choice(b"abcXYZ019 ~{}[]:,'")))
        return b'"' + b"".join(parts) + b'"'
    if kind == 5:
        return b"[" + ws() + (b"," + ws()).join(_random_json(rng, depth + 1) for _ in range(rng.randrange(4))) + ws() + b"]"
    members = [b'"' + rng.choice([b"id", b"name", b"k", b"method", b"\\u0069d"]) + b'"' + ws()
               + b":" + ws() + _random_json(rng, depth + 1) for _ in range(rng.randrange(4))]
    return b"{" + ws() + (b"," + ws()).join(members) + ws() + b"}"


def _python_accepts(line: bytes) -> bool:
    """Python's strict reading: UTF-8 (RFC 3629) and RFC 8259 JSON without the NaN/Infinity extensions."""
    def reject(constant):
        raise ValueError(constant)

    try:
        json.loads(line.decode("utf-8"), parse_constant=reject)
        return True
    except (UnicodeDecodeError, ValueError):
        return False


def test_json_validation_matches_python_strict_parser(server):
    """Randomized differential: the native validator accepts a line exactly when Python's strict parser does."""
    seed = int(os.environ.get("XAX_NATIVE_FUZZ_SEED", random.randrange(1 << 32)))
    rng = random.Random(seed)
    mutations = [b"\x00", b"\x1f", b"\x7f", b"\x80", b"\xc0", b"\xc2", b"\xe0", b"\xed\xa0\x80", b"\xf4\x90\x80\x80",
                 b"\xf5", b"\xff", b'"', b"\\", b",", b"]", b"}", b"[", b"{", b":", b"-", b"+", b".", b"e", b"0",
                 b"\\u12", b"\\x", b"tru", b"nul", b"NaN", b"Infinity", b"\xef\xbb\xbf"]
    accepted = rejected = 0
    for trial in range(1500):
        value = _random_json(rng)
        if trial % 2:
            at = rng.randrange(len(value) + 1)
            cut = rng.randrange(3)
            value = value[:at] + rng.choice(mutations) + value[at + cut:]
        line = b'{"jsonrpc":"2.0","id":' + str(trial).encode() + b',"method":"ping","params":' + value + b"}"
        response = server.exchange(line)
        native = response.get("error", {}).get("code") != -32700
        assert native == _python_accepts(line), (seed, line)
        accepted += native
        rejected += not native
    assert accepted > 300 and rejected > 300, (accepted, rejected)


def test_concurrent_servers_are_independent(exe):
    servers = [Server(exe, *args) for args in ((), ("--read-only",), ("--allow-execute",))]
    try:
        rights = [s.call("xax_capabilities", {})["authority"]["rights"] for s in servers]
        assert rights == [["build", "mutate", "read"], ["read"], ["build", "execute", "mutate", "read"]]
    finally:
        for s in servers:
            s.process.kill()


@pytest.mark.skipif(not os.environ.get("XAX_MCP_REFERENCE_PYTHON"), reason="set XAX_MCP_REFERENCE_PYTHON")
def test_differential_against_python_server(exe):
    """Same requests to both servers; only documented differences are normalized (docs/NATIVE.md)."""
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                                                                        "clientInfo": {"name": "t", "version": "0"}}},
        {"jsonrpc": "2.0", "id": 2, "method": "initialize", "params": {"protocolVersion": "1999-01-01", "capabilities": {},
                                                                        "clientInfo": {"name": "t", "version": "0"}}},
        {"jsonrpc": "2.0", "id": 3, "method": "ping"},
        {"jsonrpc": "2.0", "id": "s4", "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 5, "method": "nope"},
        {"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "bogus", "arguments": {}}},
        {"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "xax_capabilities", "arguments": {"x": 1}}},
        {"jsonrpc": "2.0", "id": 8, "method": "tools/call", "params": {"name": "xax_execute", "arguments": {"artifact": "art_x"}}},
    ]
    env = {**os.environ, "XAX_MCP_ALLOW_UNTESTED_XAX": "1", "XAX_MCP_WARM_SERVER": "0", "XAX_MCP_LOG": "WARNING",
           "PYTHONPATH": os.pathsep.join([str(ROOT / "src"), *filter(None, [os.environ.get("XAX_NATIVE_SRC")])])}
    reference = subprocess.Popen([os.environ["XAX_MCP_REFERENCE_PYTHON"], "-m", "xax_mcp", "--no-warm-server"], stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env)
    native = Server(exe)
    try:
        for message in requests:
            reference.stdin.write(json.dumps(message).encode() + b"\n")
            reference.stdin.flush()
            expected, actual = json.loads(reference.stdout.readline()), native.exchange(message)
            if message["method"] == "initialize":  # documented: the version string carries "+native"
                expected["result"]["serverInfo"].pop("version")
                actual["result"]["serverInfo"].pop("version")
            assert actual == expected, message
    finally:
        reference.kill()
        native.process.kill()


def test_standard_sdk_client(exe):
    """The official MCP Python SDK client (``mcp.Client``) negotiates with the native server and calls its tools."""
    mcp = pytest.importorskip("mcp")
    anyio = pytest.importorskip("anyio")
    if not hasattr(mcp, "Client"):
        pytest.skip("needs the mcp 2.x SDK client")
    from mcp.client.stdio import StdioServerParameters

    async def run():
        async with mcp.Client(StdioServerParameters(command=exe, args=["--read-only"]), read_timeout_seconds=60) as client:
            listed = await client.list_tools()
            capabilities = await client.call_tool("xax_capabilities", {})
            denied = await client.call_tool("xax_construct", {"request": {}})
            return listed, capabilities, denied

    listed, capabilities, denied = anyio.run(run)
    assert [tool.name for tool in listed.tools] == list(TOOLS)
    assert capabilities.structured_content["authority"]["rights"] == ["read"] and not capabilities.is_error
    assert denied.is_error and denied.structured_content["error"]["code"] == "denied_capability"


def test_build_is_deterministic(exe, tmp_path):
    """The committed store builds to the same PE every time (two independent rebuilds from the store's builder)."""
    source = os.environ.get("XAX_NATIVE_SRC")
    if not source:
        pytest.skip("needs XAX_NATIVE_SRC")
    subprocess.run([sys.executable, str(NATIVE / "server.py"), source, str(tmp_path)], check=True, capture_output=True, timeout=900)
    assert hashlib.sha256((tmp_path / "xax-mcp-native.exe").read_bytes()).digest() == hashlib.sha256(Path(exe).read_bytes()).digest()
