"""Measure the native server against the Python server on this host (raw samples; development tooling).

    python native/bench.py <native exe> <python with xax-mcp's dependencies> [<XAX compiler/src>] > evidence.json

Per launch: wall time from process creation to the initialize response (cold start), then the median latency of
ping, tools/list and xax_capabilities round trips, and the process's peak working set (Windows).
"""
from __future__ import annotations

import ctypes
import json
import os
import platform
import statistics
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT = {"jsonrpc": "2.0", "id": 0, "method": "initialize",
        "params": {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "bench", "version": "0"}}}
CALLS = {"ping": {"method": "ping"}, "tools_list": {"method": "tools/list"},
         "capabilities": {"method": "tools/call", "params": {"name": "xax_capabilities", "arguments": {}}}}


class Counters(ctypes.Structure):
    _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD), ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t), ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t), ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t), ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t)]


def peak_working_set(pid: int) -> int:
    kernel32, psapi = ctypes.WinDLL("kernel32"), ctypes.WinDLL("psapi")
    handle = kernel32.OpenProcess(0x1000 | 0x0010, False, pid)  # QUERY_LIMITED_INFORMATION | VM_READ
    counters = Counters()
    counters.cb = ctypes.sizeof(Counters)
    psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb)
    kernel32.CloseHandle(handle)
    return counters.PeakWorkingSetSize


def session(command: list[str], env: dict, rounds: int) -> dict:
    started = time.perf_counter()
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env)

    def exchange(message: dict) -> dict:
        process.stdin.write(json.dumps(message).encode() + b"\n")
        process.stdin.flush()
        return json.loads(process.stdout.readline())

    assert "result" in exchange(INIT)
    sample = {"initialize_s": time.perf_counter() - started}
    for name, body in CALLS.items():
        times = []
        for k in range(rounds):
            t = time.perf_counter()
            assert "result" in exchange({"jsonrpc": "2.0", "id": k + 1, **body})
            times.append(time.perf_counter() - t)
        sample[f"{name}_median_s"] = statistics.median(times)
    sample["peak_working_set_bytes"] = peak_working_set(process.pid)
    process.stdin.close()
    process.wait(60)
    return sample


def main(argv: list[str]) -> int:
    native, python = argv[1], argv[2]
    # A Windows venv's python.exe is a redirector that starts the base interpreter as a child; measure that interpreter
    # directly with the venv's packages on its path, so the peak working set is the server's own.
    probe = "import site, sys; print(sys._base_executable); print(site.getsitepackages()[-1])"
    base, packages = subprocess.run([python, "-c", probe], capture_output=True, text=True, check=True).stdout.splitlines()[:2]
    python = base
    env = {**os.environ, "XAX_MCP_ALLOW_UNTESTED_XAX": "1", "XAX_MCP_WARM_SERVER": "0", "XAX_MCP_LOG": "WARNING",
           "PYTHONPATH": os.pathsep.join([str(ROOT / "src"), *argv[3:4], packages])}
    arms = {"native": [native], "python": [python, "-m", "xax_mcp", "--no-warm-server"]}
    launches, rounds = 15, 50
    samples = {arm: [] for arm in arms}
    for _ in range(launches):  # interleaved, so drift affects both arms alike
        for arm, command in arms.items():
            samples[arm].append(session(command, env, rounds))
    summary = {arm: {key: statistics.median(s[key] for s in rows) for key in rows[0]} for arm, rows in samples.items()}
    print(json.dumps({"python_arm": [python, "-m", "xax_mcp", "--no-warm-server"], "host": {"platform": platform.platform(), "machine": platform.machine(),
                               "processor": platform.processor(), "cpu_count": os.cpu_count()},
                      "method": f"{launches} interleaved launches per arm; per launch {rounds} round trips per call; "
                                "initialize_s is process creation to initialize response",
                      "summary_medians": summary, "samples": samples}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
