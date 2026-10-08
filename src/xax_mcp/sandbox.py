"""Parent side of the sandbox: probe, launch the fixed executor, enforce wall time and output quotas.

The artifact bytes are written to a fresh private directory as ``prog`` (mode 0500) and launched by
``_sandbox_exec.py`` through a constrained argument vector.  Nothing here interprets the artifact.
"""

from __future__ import annotations

import json
import os
import platform
import selectors
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

HELPER = Path(__file__).with_name("_sandbox_exec.py")
SETUP_FAILURE_STATUS = 125


@dataclass(frozen=True)
class Limits:
    wall_ms: int = 5000
    cpu_seconds: int = 5
    memory_bytes: int = 256 * 1024 * 1024
    max_stdout_bytes: int = 1024 * 1024
    max_stderr_bytes: int = 64 * 1024
    max_stdin_bytes: int = 1024 * 1024

    def as_dict(self) -> dict:
        return {"wall_ms": self.wall_ms, "cpu_seconds": self.cpu_seconds, "memory_bytes": self.memory_bytes,
                "max_stdout_bytes": self.max_stdout_bytes, "max_stderr_bytes": self.max_stderr_bytes,
                "max_stdin_bytes": self.max_stdin_bytes, "file_size_bytes": 0, "file_descriptors": 3, "processes": 1}


@dataclass
class RunOutcome:
    exit_status: int | None
    signal: str | None
    stdout: bytes
    stderr: bytes
    stdout_truncated: bool
    stderr_truncated: bool
    timed_out: bool
    cancelled: bool
    output_limit_exceeded: bool
    wall_ms: float
    setup_error: str | None = None


@dataclass
class ProbeResult:
    available: bool
    reason: str | None
    details: dict = field(default_factory=dict)


def _helper_argv(directory: str, status_fd: int, limits: Limits, probe: bool) -> list[str]:
    argv = [sys.executable, "-I", "-S", str(HELPER), "--status", str(status_fd), "--dir", directory,
            "--memory", str(limits.memory_bytes), "--cpu", str(limits.cpu_seconds), "--parent", str(os.getpid())]
    return argv + ["--probe"] if probe else argv


class Sandbox:
    """OS-enforced confinement for Linux x86-64; fails closed when it cannot be established."""

    mechanism = "linux-userns+chroot+seccomp+rlimit"

    def __init__(self) -> None:
        self._probe: ProbeResult | None = None
        self._lock = threading.Lock()

    def probe(self) -> ProbeResult:
        with self._lock:
            if self._probe is None:
                self._probe = self._run_probe()
            return self._probe

    def _run_probe(self) -> ProbeResult:
        if not (sys.platform.startswith("linux") and platform.machine().lower() in ("x86_64", "amd64")):
            return ProbeResult(False, f"sandbox requires Linux x86-64 (host: {sys.platform} {platform.machine()})")
        directory = tempfile.mkdtemp(prefix="xax-mcp-probe-")
        try:
            Path(directory, "prog").write_bytes(b"")
            os.chmod(directory, 0o500)
            read_fd, write_fd = os.pipe()
            try:
                process = subprocess.Popen(_helper_argv(directory, write_fd, Limits(), True), stdin=subprocess.DEVNULL,
                                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, env={}, pass_fds=(write_fd,),
                                           start_new_session=True)
            finally:
                os.close(write_fd)
            with os.fdopen(read_fd, "rb") as status:
                report = status.read(65536)
            _, stderr = process.communicate(timeout=10)
            try:
                details = json.loads(report or b"{}")
            except ValueError:
                details = {}
            if not details.get("ok"):
                reason = details.get("error") or stderr.decode(errors="replace")[-500:] or f"executor exited {process.returncode}"
                return ProbeResult(False, f"sandbox setup failed: {reason}", details)
            own = {name: os.readlink(f"/proc/self/ns/{name}") for name in details.get("namespaces", {})}
            isolated = all(details["namespaces"][name] != own[name] for name in own) and len(own) == 6
            if not (isolated and details.get("openat_denied") and details.get("root_entries") == ["prog"]):
                return ProbeResult(False, "sandbox probe did not observe the required isolation", details)
            return ProbeResult(True, None, {"namespaces": sorted(own), "inner_uid": details.get("uid"),
                                            "root_entries": details.get("root_entries"), "openat_denied": True})
        except (OSError, subprocess.SubprocessError) as error:
            return ProbeResult(False, f"sandbox probe failed: {error}")
        finally:
            os.chmod(directory, 0o700)
            shutil.rmtree(directory, ignore_errors=True)

    def run(self, artifact: bytes, stdin: bytes, limits: Limits, cancel: threading.Event | None = None) -> RunOutcome:
        probe = self.probe()
        if not probe.available:
            raise SandboxUnavailable(probe.reason or "sandbox unavailable")
        if len(stdin) > limits.max_stdin_bytes:
            raise ValueError("stdin exceeds the configured limit")
        directory = tempfile.mkdtemp(prefix="xax-mcp-run-")
        try:
            path = Path(directory, "prog")
            with open(path, "xb") as handle:
                handle.write(artifact)
            os.chmod(path, 0o500)
            os.chmod(directory, 0o500)
            return self._launch(directory, stdin, limits, cancel or threading.Event())
        finally:
            os.chmod(directory, 0o700)
            shutil.rmtree(directory, ignore_errors=True)

    def _launch(self, directory: str, stdin: bytes, limits: Limits, cancel: threading.Event) -> RunOutcome:
        read_fd, write_fd = os.pipe()
        started = time.perf_counter()
        try:
            process = subprocess.Popen(_helper_argv(directory, write_fd, limits, False), stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={}, pass_fds=(write_fd,),
                                       start_new_session=True)
        finally:
            os.close(write_fd)
        caps = {process.stdout: limits.max_stdout_bytes, process.stderr: limits.max_stderr_bytes}
        buffers = {process.stdout: bytearray(), process.stderr: bytearray()}
        truncated = {process.stdout: False, process.stderr: False}
        timed_out = cancelled = output_exceeded = False
        status_bytes = bytearray()
        selector = selectors.DefaultSelector()
        os.set_blocking(read_fd, False)
        selector.register(read_fd, selectors.EVENT_READ, "status")
        for stream in (process.stdout, process.stderr):
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, "out")
        pending = memoryview(stdin)
        if pending:
            os.set_blocking(process.stdin.fileno(), False)
            selector.register(process.stdin, selectors.EVENT_WRITE, "in")
        else:
            process.stdin.close()
        deadline = started + limits.wall_ms / 1000
        try:
            while selector.get_map():
                remaining = deadline - time.perf_counter()
                if remaining <= 0:
                    timed_out = True
                    break
                if cancel.is_set():
                    cancelled = True
                    break
                for key, _events in selector.select(min(remaining, 0.05)):
                    if key.data == "in":
                        try:
                            written = os.write(process.stdin.fileno(), pending[:65536])
                            pending = pending[written:]
                        except (BrokenPipeError, OSError):
                            pending = pending[:0]
                        if not pending:
                            selector.unregister(process.stdin)
                            process.stdin.close()
                        continue
                    fd = key.fd if key.data == "status" else key.fileobj.fileno()
                    try:
                        chunk = os.read(fd, 65536)
                    except BlockingIOError:
                        continue
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    if key.data == "status":
                        status_bytes += chunk[: 65536 - len(status_bytes)]
                        continue
                    stream = key.fileobj
                    room = caps[stream] - len(buffers[stream])
                    buffers[stream] += chunk[:max(room, 0)]
                    if len(chunk) > room:
                        truncated[stream] = True
                        if stream is process.stdout:
                            output_exceeded = True
                if output_exceeded:
                    break
        finally:
            if process.poll() is None and (timed_out or cancelled or output_exceeded or selector.get_map()):
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            selector.close()
            for stream in (process.stdin, process.stdout, process.stderr):
                try:
                    stream.close()
                except OSError:
                    pass
            os.close(read_fd)
            returncode = process.wait()
        wall_ms = (time.perf_counter() - started) * 1000
        setup_error = None
        if status_bytes:
            try:
                setup_error = json.loads(bytes(status_bytes)).get("error", "sandbox setup failed")
            except ValueError:
                setup_error = "sandbox setup failed"
        exit_status = returncode if returncode >= 0 else None
        signal_name = signal.Signals(-returncode).name if returncode < 0 else None
        return RunOutcome(exit_status, signal_name, bytes(buffers[process.stdout]), bytes(buffers[process.stderr]),
                          truncated[process.stdout], truncated[process.stderr], timed_out, cancelled, output_exceeded,
                          wall_ms, setup_error)


class SandboxUnavailable(RuntimeError):
    pass
