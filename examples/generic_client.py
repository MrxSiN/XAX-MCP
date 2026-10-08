"""Generic MCP client walkthrough (official `mcp` SDK, STDIO): discover -> construct -> build -> execute.

    python examples/generic_client.py [--server xax-mcp] [CARRIER.json] [x1 x2 ...]

The default carrier (examples/carriers/poly_reduce.json) reads n little-endian u64 values from stdin and writes
(sum 3x^2+5x+7 mod 2^64, max x).  The carrier is a typed semantic-graph request (transport), not source code.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import anyio
from mcp import Client
from mcp.client.stdio import StdioServerParameters

HERE = Path(__file__).resolve().parent


async def main(args) -> int:
    server = StdioServerParameters(command=args.server, args=["--allow-execute"])
    async with Client(server, read_timeout_seconds=600) as client:
        async def call(name, arguments=None):
            payload = (await client.call_tool(name, arguments or {})).structured_content
            print(f"-> {name}: ok={payload.get('ok')}", file=sys.stderr)
            if not payload.get("ok"):
                print(json.dumps(payload["error"], indent=1), file=sys.stderr)
                raise SystemExit(1)
            return payload

        print("tools:", [t.name for t in (await client.list_tools()).tools], file=sys.stderr)
        caps = await call("xax_capabilities")
        print("xax:", caps["xax"]["status"], caps["xax"]["pinned_commit"][:12], "sandbox:",
              caps["targets"][0]["execute"]["available"], file=sys.stderr)
        built = await call("xax_construct", {"request": json.loads(Path(args.carrier).read_text())})
        artifact = await call("xax_build", {"workspace": built["workspace"]})
        run = await call("xax_execute", {"artifact": artifact["artifact"],
                                         "input": {"ints": [{"type": "b64", "value": int(x)} for x in args.values]},
                                         "output": {"ints": ["b64", "b64"]}})
        print(json.dumps({"root": built["root"], "artifact_blake3": artifact["artifact_digest_blake3"],
                          "exit_status": run["exit_status"], "values": run["stdout"]["values"],
                          "evidence": run["evidence"]["label"]}, indent=1))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default=shutil.which("xax-mcp") or "xax-mcp")
    parser.add_argument("carrier", nargs="?", default=str(HERE / "carriers" / "poly_reduce.json"))
    parser.add_argument("values", nargs="*", default=["1", "2", "3"])
    raise SystemExit(anyio.run(main, parser.parse_args()))
