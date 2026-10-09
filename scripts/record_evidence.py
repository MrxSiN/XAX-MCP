"""Record end-to-end evidence for docs/evidence: versions, identities, results, limits and measured latencies.

Usage: python scripts/record_evidence.py [--cold-cache] [--mode in-process|warm-server] [--out docs/evidence/FILE.json]

Everything is measured through a real MCP STDIO client (the official SDK) against a freshly launched server.  The
latencies are MCP tool round trips on one host: they are NOT XAX generated-code (R4) benchmarks and NOT the AI-token
efficiency milestone.  --cold-cache points XAX_NATIVE_CACHE at an empty directory so the XAX-hosted compiler
components are rebuilt (true cold start).
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform
import secrets
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import anyio

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
import programs  # noqa: E402


async def record(cold_cache: bool, mode: str) -> dict:
    from mcp import Client
    from mcp.client.stdio import StdioServerParameters

    env = {"XAX_MCP_LOG": "WARNING", "XAX_MCP_WARM_SERVER": "0"}
    if cold_cache:
        env["XAX_NATIVE_CACHE"] = tempfile.mkdtemp(prefix="xax-native-cold-")
    prepare_ms = None
    if mode == "warm-server":
        # A private warm server, prepared first (as `xax-mcp --prepare` after install), then one measured launch.
        warm_dir = tempfile.mkdtemp(prefix="xw-")
        env.update({"XAX_MCP_WARM_SERVER": "1", "XAX_MCP_WARM_DIR": warm_dir, "XAX_MCP_WARM_IDLE_SECONDS": "30"})
        started = time.perf_counter()
        subprocess.run([sys.executable, "-m", "xax_mcp", "--prepare"], env={**os.environ, **env}, check=True,
                       stdout=subprocess.DEVNULL)
        prepare_ms = (time.perf_counter() - started) * 1000
    params = StdioServerParameters(command=sys.executable, args=["-m", "xax_mcp", "--allow-execute"], env=env)
    timings = {}

    async def call(client, name, arguments=None):
        started = time.perf_counter()
        result = (await client.call_tool(name, arguments or {})).structured_content
        timings.setdefault(name, []).append(round((time.perf_counter() - started) * 1000, 2))
        if not result.get("ok"):
            raise RuntimeError(f"{name}: {result}")
        return result

    a, b, c = (secrets.randbelow(1 << 32) for _ in range(3))
    xs = [secrets.randbelow(1 << 64) for _ in range(64)]
    launched = time.perf_counter()
    async with Client(params, read_timeout_seconds=900) as client:
        initialize_ms = (time.perf_counter() - launched) * 1000
        caps = await call(client, "xax_capabilities")
        first = time.perf_counter()
        built = await call(client, "xax_construct", {"request": programs.poly_reduce(a, b, c)})
        first_construct_ms = (time.perf_counter() - first) * 1000  # includes waiting for the XAX component warm-up
        art = await call(client, "xax_build", {"workspace": built["workspace"]})
        arguments = {"artifact": art["artifact"], "input": {"ints": [{"type": "b64", "value": x} for x in xs]},
                     "output": {"ints": ["b64", "b64"]}}
        run = await call(client, "xax_execute", arguments)
        cold_total_ms = (time.perf_counter() - first) * 1000
        launch_to_first_result_ms = (time.perf_counter() - launched) * 1000
        for _ in range(20):
            await call(client, "xax_execute", arguments)
        warm_construct = await call(client, "xax_construct", {"request": programs.poly_reduce(a + 1, b, c)})
        warm_build = await call(client, "xax_build", {"workspace": warm_construct["workspace"]})
        cached = await call(client, "xax_build", {"workspace": warm_construct["workspace"]})
        caps_after = await call(client, "xax_capabilities")
    expected = list(programs.poly_reduce_oracle(a, b, c, xs))
    got = [v["value"] for v in run["stdout"]["values"]]
    executes = timings["xax_execute"][1:]
    return {
        "format": "xax-mcp-evidence-v1",
        "label": "EXECUTED" if got == expected else "FAILED",
        "recorded_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "versions": {"xax-mcp": caps["server"]["version"], "mcp_sdk": caps["server"]["mcp_sdk"], "xax": caps["xax"],
                     "python": platform.python_version(), "os": f"{platform.system()} {platform.release()}", "machine": platform.machine()},
        "sandbox": caps["targets"][0]["execute"]["sandbox"], "limits": caps["authority"]["limits"],
        "workload": {"kind": "novel randomized polynomial reduction (tests/programs.py:poly_reduce), coefficients drawn at run time",
                     "coefficients": [a, b, c], "inputs": len(xs), "result": got, "oracle": expected, "matches": got == expected},
        "identities": {"workspace_root": built["root"], "store_sha256": built["store"]["sha256"],
                       "artifact_blake3": art["artifact_digest_blake3"], "artifact_sha256": art["artifact_sha256"],
                       "artifact_bytes": art["bytes"], "build_key": art["provenance"]["build_key"],
                       "provenance_cid": art["provenance"]["provenance_cid"], "target_profile": art["provenance"]["target_profile"],
                       "xax_native_components": art["provenance"]["xax_native_components"]},
        "measured_ms": {
            "native_cache": "cold (empty XAX_NATIVE_CACHE)" if cold_cache else "warm (existing XAX_NATIVE_CACHE)",
            "server_mode": mode, "started_from": caps["server"].get("started_from"),
            "warm_server_prepare": None if prepare_ms is None else round(prepare_ms, 1),
            "launch_to_first_construct_build_execute": round(launch_to_first_result_ms, 1),
            "launch_and_initialize": round(initialize_ms, 1),
            "server_warmup_reported": caps_after["server"]["warmup_ms"],
            "first_construct_including_warmup_wait": round(first_construct_ms, 1),
            "cold_construct_build_execute": round(cold_total_ms, 1),
            "warm_construct": timings["xax_construct"][1], "warm_build_miss": timings["xax_build"][1],
            "build_cache_hit": timings["xax_build"][2], "cached_execute_median": statistics.median(executes),
            "cached_execute_samples": executes, "server_reported_sandbox_wall_ms": run["evidence"]["wall_ms"],
            "build_cache": cached["cache"],
        },
        "not_measured_here": "R4 generated-code performance and the AI-token efficiency milestone are separate upstream XAX evidence",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cold-cache", action="store_true")
    parser.add_argument("--mode", choices=("in-process", "warm-server"), default="in-process")
    parser.add_argument("--out")
    args = parser.parse_args()
    evidence = anyio.run(record, args.cold_cache, args.mode)
    text = json.dumps(evidence, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(text)
    print(text)
    return 0 if evidence["label"] == "EXECUTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
