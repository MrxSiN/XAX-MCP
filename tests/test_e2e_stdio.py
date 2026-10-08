"""End to end over the real MCP STDIO transport with the official SDK client (a standards-compliant generic client)."""
from __future__ import annotations

import base64
import json
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path

import anyio
import pytest

import programs
from conftest import needs_sandbox

pytestmark = pytest.mark.anyio
TOOLS = {"xax_capabilities", "xax_workspace", "xax_query", "xax_construct", "xax_transaction", "xax_build", "xax_execute", "xax_result"}


@pytest.fixture
def anyio_backend():
    return "asyncio"


def server_params(*extra: str):
    from mcp.client.stdio import StdioServerParameters

    return StdioServerParameters(command=sys.executable, args=["-m", "xax_mcp", "--allow-execute", *extra],
                                 env={"XAX_MCP_LOG": "WARNING"})


async def call(client, name, arguments=None):
    result = await client.call_tool(name, arguments or {})
    payload = result.structured_content
    assert payload is not None
    assert json.loads(result.content[0].text) == payload  # text mirror of the structured payload
    assert result.is_error == (not payload["ok"])
    return payload


@needs_sandbox
async def test_initialize_discover_construct_build_execute_novel_program():
    from mcp import Client

    a, b, c = (secrets.randbelow(1 << 40) for _ in range(3))
    xs = [secrets.randbelow(1 << 64) for _ in range(17)]
    async with Client(server_params(), read_timeout_seconds=600) as client:
        tools = (await client.list_tools()).tools
        assert {t.name for t in tools} == TOOLS
        for tool in tools:
            assert tool.input_schema["type"] == "object" and tool.input_schema.get("additionalProperties") is False
        caps = await call(client, "xax_capabilities")
        assert caps["xax"]["status"] == "tested" and caps["targets"][0]["execute"]["available"]
        started = time.perf_counter()
        built = await call(client, "xax_construct", {"request": programs.poly_reduce(a, b, c)})
        artifact = await call(client, "xax_build", {"workspace": built["workspace"]})
        run = await call(client, "xax_execute", {"artifact": artifact["artifact"],
                                                 "input": {"ints": [{"type": "b64", "value": x} for x in xs]},
                                                 "output": {"ints": ["b64", "b64"]}})
        cold = time.perf_counter() - started
        assert [v["value"] for v in run["stdout"]["values"]] == list(programs.poly_reduce_oracle(a, b, c, xs))
        assert run["evidence"]["label"] == "EXECUTED"
        started = time.perf_counter()
        again = await call(client, "xax_execute", {"artifact": artifact["artifact"], "input": {"ints": [{"type": "b64", "value": 2}]},
                                                   "output": {"ints": ["b64", "b64"]}})
        warm = time.perf_counter() - started
        assert again["stdout"]["values"][0]["value"] == (4 * a + 2 * b + c) % (1 << 64)
        # Errors are structured, never transport failures.
        bad = await call(client, "xax_execute", {"artifact": "art_" + "f" * 24})
        assert bad["error"]["code"] == "not_found"
        invalid = await call(client, "xax_query", {"workspace": built["workspace"], "kind": "sql"})
        assert invalid["error"]["code"] == "invalid_request"
    print(json.dumps({"cold_construct_build_run_s": round(cold, 3), "cached_execute_s": round(warm, 3)}))


@needs_sandbox
async def test_two_clients_are_isolated_and_stores_reopen(tmp_path):
    """Path A: a verified store exported by one client is reopened by another server and executed."""
    from mcp import Client

    stores = tmp_path / "stores"
    stores.mkdir()
    async with Client(server_params(), read_timeout_seconds=600) as first:
        built = await call(first, "xax_construct", {"request": programs.poly_reduce(7, 0, 1)})
        chunks, offset = [], 0
        while offset is not None:
            part = await call(first, "xax_result", {"handle": built["workspace"], "offset": offset, "length": 65536})
            chunks.append(base64.b64decode(part["base64"]))
            offset = part["continuation"]
        (stores / "poly.xax").write_bytes(b"".join(chunks))
        async with Client(server_params("--store-root", str(stores)), read_timeout_seconds=600) as second:
            foreign = await call(second, "xax_query", {"workspace": built["workspace"], "kind": "root"})
            assert foreign["error"]["code"] == "not_found"
            opened = await call(second, "xax_workspace", {"action": "open", "store": "poly.xax"})
            assert opened["root"] == built["root"]
            escaped = await call(second, "xax_workspace", {"action": "open", "store": "../poly.xax"})
            assert escaped["error"]["code"] == "invalid_request"
            art = await call(second, "xax_build", {"workspace": opened["workspace"]})
            run = await call(second, "xax_execute", {"artifact": art["artifact"], "input": {"ints": [{"type": "b64", "value": 3}]},
                                                     "output": {"ints": ["b64", "b64"]}})
            assert run["stdout"]["values"][0]["value"] == 7 * 9 + 1


async def test_transaction_and_stale_root_through_mcp():
    from mcp import Client

    async with Client(server_params(), read_timeout_seconds=600) as client:
        built = await call(client, "xax_construct", {"request": programs.poly_reduce(1, 1, 1)})
        ws, term = built["workspace"], built["function_handles"]["term"]
        nodes = (await call(client, "xax_query", {"workspace": ws, "kind": "function_nodes", "handle": term}))["result"]["entities"]
        constant = [n for n in nodes if n["operation"] == "constant"][0]["handle"]
        edit = {"workspace": ws, "mode": "commit", "expected_generation": 0, "expected_root": built["root"],
                "mutations": [{"op": "set_constant", "node": constant, "value": 5}]}
        assert (await call(client, "xax_transaction", edit))["committed"]
        stale = await call(client, "xax_transaction", edit)
        assert stale["error"]["code"] == "stale_root"
        diff = await call(client, "xax_query", {"workspace": ws, "kind": "diff", "from_generation": 0})
        assert diff["ok"]


def test_stdout_carries_only_json_rpc():
    """Raw protocol check: every stdout line is a JSON-RPC message; diagnostics go to stderr."""
    process = subprocess.Popen([sys.executable, "-m", "xax_mcp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env={**os.environ, "XAX_MCP_LOG": "INFO"})
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25", "capabilities": {},
                                                                     "clientInfo": {"name": "raw", "version": "0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "xax_capabilities", "arguments": {}}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "xax_construct", "arguments": {"request": "print(1)"}}},
        {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "xax_construct", "arguments": {"request": programs.poly_reduce(1, 2, 3)}}},
    ]
    for message in messages:
        process.stdin.write((json.dumps(message) + "\n").encode())
    process.stdin.flush()
    responses = []
    while len([r for r in responses if "id" in r]) < 5:
        line = process.stdout.readline()
        assert line, "server closed stdout early"
        responses.append(json.loads(line))  # any non-JSON byte on stdout fails here
    process.stdin.close()
    process.wait(timeout=60)
    rest, stderr = process.stdout.read(), process.stderr.read()
    assert rest.strip() == b""
    assert all(r.get("jsonrpc") == "2.0" for r in responses)
    by_id = {r["id"]: r for r in responses if "id" in r}
    assert by_id[1]["result"]["serverInfo"]["name"] == "xax-mcp"
    assert len(by_id[2]["result"]["tools"]) == 8
    assert by_id[3]["result"]["structuredContent"]["ok"] is True
    assert by_id[4]["result"]["isError"] is True
    assert by_id[4]["result"]["structuredContent"]["error"]["code"] == "invalid_request"
    assert by_id[5]["result"]["structuredContent"]["verified"] is True
    assert b"audit" in stderr


@needs_sandbox
def test_server_crash_kills_running_artifact():
    """SIGKILL the server mid-execution: the sandboxed process dies with it (PR_SET_PDEATHSIG)."""
    process = subprocess.Popen([sys.executable, "-m", "xax_mcp", "--allow-execute", "--wall-ms", "60000", "--cpu-seconds", "60"],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    def send(message):
        process.stdin.write((json.dumps(message) + "\n").encode())
        process.stdin.flush()

    def receive(expected_id):
        while True:
            reply = json.loads(process.stdout.readline())
            if reply.get("id") == expected_id:
                return reply

    send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25", "capabilities": {},
                                                                      "clientInfo": {"name": "raw", "version": "0"}}})
    receive(1)
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})
    send({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "xax_construct", "arguments": {"request": programs.spin()}}})
    ws = receive(2)["result"]["structuredContent"]["workspace"]
    send({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "xax_build", "arguments": {"workspace": ws}}})
    art = receive(3)["result"]["structuredContent"]["artifact"]
    before = _sandboxed_programs()
    send({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "xax_execute", "arguments": {"artifact": art}}})
    deadline = time.time() + 10
    while time.time() < deadline and not (_sandboxed_programs() - before):
        time.sleep(0.05)
    running = _sandboxed_programs() - before
    assert running, "artifact did not start"
    process.kill()
    process.wait()
    deadline = time.time() + 5
    while time.time() < deadline and running & _sandboxed_programs():
        time.sleep(0.05)
    assert not running & _sandboxed_programs()


def _sandboxed_programs() -> set[int]:
    found = set()
    for entry in Path("/proc").iterdir():
        if entry.name.isdigit():
            try:
                if (entry / "cmdline").read_bytes() == b"/prog\0":
                    found.add(int(entry.name))
            except OSError:
                pass
    return found
