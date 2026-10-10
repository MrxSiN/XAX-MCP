"""Windows side of the sandbox: one XAX-built PE32+ executable in a less privileged AppContainer inside a job object.

This file is the whole audited executor boundary on Windows.  It holds no XAX semantics and never computes a
workload; it only confines and launches the artifact bytes, through ``CreateProcessW`` with a fixed command line (no
shell), an empty environment, and exactly three inherited handles (the stdin/stdout/stderr pipes):

1. a less privileged AppContainer token (LPAC) with no capabilities: no network, no named objects of other
   processes, and file access only where an ACL names the container (the private artifact directory) or "all
   restricted application packages" (system DLLs the loader needs);
2. a job object: committed-memory and CPU-time limits, one active process, kill on close, die on unhandled
   exception, and every UI restriction;
3. process mitigations: child-process creation blocked, dynamic code prohibited, win32k system calls disabled,
   extension points disabled, no remote or low-label images.

The process is created suspended; it is resumed only after its token is confirmed to be a less privileged
AppContainer and the process is confirmed to be in the job.  Any failure refuses to run the artifact (fail closed).
"""

from __future__ import annotations

import ctypes
import os
import platform
import shutil
import sys
import tempfile
import threading
import time
from ctypes import wintypes as w
from pathlib import Path

from . import sandbox  # module, not names: sandbox.py imports this module at its end

CONTAINER_NAME = "xax-mcp.sandbox"
# NTSTATUS exit codes of a process killed by an exception.  ud2 (a failed XAX check) gives the first.
_EXCEPTIONS = {0xC000001D: "STATUS_ILLEGAL_INSTRUCTION", 0x80000003: "STATUS_BREAKPOINT",
               0xC0000005: "STATUS_ACCESS_VIOLATION", 0xC00000FD: "STATUS_STACK_OVERFLOW",
               0xC0000409: "STATUS_STACK_BUFFER_OVERRUN", 0xC0000094: "STATUS_INTEGER_DIVIDE_BY_ZERO"}

_JOB_LIMITS = 0x2 | 0x8 | 0x100 | 0x400 | 0x2000  # process time, active process, process memory, die on exception, kill on close
_MITIGATIONS = (1 << 28) | (1 << 32) | (1 << 36) | (1 << 52) | (1 << 56)  # win32k off, no extension points, no dynamic
# code, no remote images, no low-label images
_ATTR_HANDLE_LIST, _ATTR_MITIGATION, _ATTR_CHILD_POLICY, _ATTR_SECURITY_CAPS, _ATTR_PACKAGES_POLICY = (
    0x20002, 0x20007, 0x2000E, 0x20009, 0x2000F)


class _StartupInfoEx(ctypes.Structure):
    _fields_ = [("cb", w.DWORD), ("lpReserved", w.LPWSTR), ("lpDesktop", w.LPWSTR), ("lpTitle", w.LPWSTR),
                ("dwX", w.DWORD), ("dwY", w.DWORD), ("dwXSize", w.DWORD), ("dwYSize", w.DWORD),
                ("dwXCountChars", w.DWORD), ("dwYCountChars", w.DWORD), ("dwFillAttribute", w.DWORD),
                ("dwFlags", w.DWORD), ("wShowWindow", w.WORD), ("cbReserved2", w.WORD), ("lpReserved2", ctypes.c_void_p),
                ("hStdInput", w.HANDLE), ("hStdOutput", w.HANDLE), ("hStdError", w.HANDLE),
                ("lpAttributeList", ctypes.c_void_p)]


class _ProcessInformation(ctypes.Structure):
    _fields_ = [("hProcess", w.HANDLE), ("hThread", w.HANDLE), ("dwProcessId", w.DWORD), ("dwThreadId", w.DWORD)]


class _SecurityCapabilities(ctypes.Structure):
    _fields_ = [("AppContainerSid", ctypes.c_void_p), ("Capabilities", ctypes.c_void_p), ("CapabilityCount", w.DWORD),
                ("Reserved", w.DWORD)]


class _BasicLimits(ctypes.Structure):
    _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                ("LimitFlags", w.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", w.DWORD),
                ("Affinity", ctypes.c_size_t), ("PriorityClass", w.DWORD), ("SchedulingClass", w.DWORD)]


class _ExtendedLimits(ctypes.Structure):
    _fields_ = [("BasicLimitInformation", _BasicLimits), ("IoInfo", ctypes.c_uint64 * 6),
                ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]


class _Trustee(ctypes.Structure):
    _fields_ = [("pMultipleTrustee", ctypes.c_void_p), ("MultipleTrusteeOperation", ctypes.c_int),
                ("TrusteeForm", ctypes.c_int), ("TrusteeType", ctypes.c_int), ("ptstrName", ctypes.c_void_p)]


class _ExplicitAccess(ctypes.Structure):
    _fields_ = [("grfAccessPermissions", w.DWORD), ("grfAccessMode", ctypes.c_int), ("grfInheritance", w.DWORD),
                ("Trustee", _Trustee)]


def _api():
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    userenv = ctypes.WinDLL("userenv", use_last_error=True)
    for name, restype, argtypes in (
            ("CreateJobObjectW", w.HANDLE, (ctypes.c_void_p, w.LPCWSTR)),
            ("SetInformationJobObject", w.BOOL, (w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD)),
            ("AssignProcessToJobObject", w.BOOL, (w.HANDLE, w.HANDLE)),
            ("TerminateJobObject", w.BOOL, (w.HANDLE, w.UINT)),
            ("IsProcessInJob", w.BOOL, (w.HANDLE, w.HANDLE, ctypes.POINTER(w.BOOL))),
            ("InitializeProcThreadAttributeList", w.BOOL, (ctypes.c_void_p, w.DWORD, w.DWORD, ctypes.POINTER(ctypes.c_size_t))),
            ("UpdateProcThreadAttribute", w.BOOL, (ctypes.c_void_p, w.DWORD, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t,
                                                   ctypes.c_void_p, ctypes.c_void_p)),
            ("DeleteProcThreadAttributeList", None, (ctypes.c_void_p,)),
            ("CreateProcessW", w.BOOL, (w.LPCWSTR, w.LPWSTR, ctypes.c_void_p, ctypes.c_void_p, w.BOOL, w.DWORD,
                                        ctypes.c_void_p, w.LPCWSTR, ctypes.c_void_p, ctypes.c_void_p)),
            ("ResumeThread", w.DWORD, (w.HANDLE,)),
            ("TerminateProcess", w.BOOL, (w.HANDLE, w.UINT)),
            ("WaitForSingleObject", w.DWORD, (w.HANDLE, w.DWORD)),
            ("GetExitCodeProcess", w.BOOL, (w.HANDLE, ctypes.POINTER(w.DWORD))),
            ("GetProcessTimes", w.BOOL, (w.HANDLE, *(ctypes.POINTER(ctypes.c_uint64),) * 4)),
            ("CloseHandle", w.BOOL, (w.HANDLE,))):
        function = getattr(kernel32, name)
        function.restype, function.argtypes = restype, argtypes
    for name, restype, argtypes in (
            ("OpenProcessToken", w.BOOL, (w.HANDLE, w.DWORD, ctypes.POINTER(w.HANDLE))),
            ("GetTokenInformation", w.BOOL, (w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD, ctypes.POINTER(w.DWORD))),
            ("GetNamedSecurityInfoW", w.DWORD, (w.LPCWSTR, ctypes.c_int, w.DWORD, ctypes.c_void_p, ctypes.c_void_p,
                                                ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))),
            ("SetEntriesInAclW", w.DWORD, (w.ULONG, ctypes.POINTER(_ExplicitAccess), ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))),
            ("SetNamedSecurityInfoW", w.DWORD, (w.LPWSTR, ctypes.c_int, w.DWORD, ctypes.c_void_p, ctypes.c_void_p,
                                                ctypes.c_void_p, ctypes.c_void_p)),
            ("FreeSid", ctypes.c_void_p, (ctypes.c_void_p,))):
        function = getattr(advapi32, name)
        function.restype, function.argtypes = restype, argtypes
    for name, argtypes in (
            ("CreateAppContainerProfile", (w.LPCWSTR, w.LPCWSTR, w.LPCWSTR, ctypes.c_void_p, w.DWORD, ctypes.POINTER(ctypes.c_void_p))),
            ("DeriveAppContainerSidFromAppContainerName", (w.LPCWSTR, ctypes.POINTER(ctypes.c_void_p)))):
        function = getattr(userenv, name)
        function.restype, function.argtypes = ctypes.c_long, argtypes
    kernel32.LocalFree.restype, kernel32.LocalFree.argtypes = ctypes.c_void_p, (ctypes.c_void_p,)
    return kernel32, advapi32, userenv


def _check(ok, step: str):
    if not ok:
        error = ctypes.get_last_error()
        raise OSError(error, f"{step}: {ctypes.FormatError(error).strip()}")
    return ok


class WindowsSandbox:
    """OS-enforced confinement for Windows x86-64; fails closed when it cannot be established."""

    mechanism = "windows-lpac-appcontainer+job+mitigations"
    platform = "windows-x86_64"
    argv_supported = False  # the windows-x86_64 carrier has no command-line reads (XAX ADR-252)

    def __init__(self) -> None:
        self._probe: sandbox.ProbeResult | None = None
        self._lock = threading.Lock()
        self._sid = None

    def probe(self) -> sandbox.ProbeResult:
        with self._lock:
            if self._probe is None:
                self._probe = self._run_probe()
            return self._probe

    def _container_sid(self, userenv):
        if self._sid is None:
            sid = ctypes.c_void_p()
            result = userenv.CreateAppContainerProfile(CONTAINER_NAME, CONTAINER_NAME, "xax-mcp artifact sandbox", None, 0,
                                                       ctypes.byref(sid))
            if result == -2147024713:  # HRESULT_FROM_WIN32(ERROR_ALREADY_EXISTS)
                result = userenv.DeriveAppContainerSidFromAppContainerName(CONTAINER_NAME, ctypes.byref(sid))
            if result != 0:
                raise OSError(result, f"AppContainer profile: HRESULT {result & 0xFFFFFFFF:#010x}")
            self._sid = sid
        return self._sid

    def _run_probe(self) -> sandbox.ProbeResult:
        if not (sys.platform == "win32" and platform.machine().lower() in ("amd64", "x86_64")):
            return sandbox.ProbeResult(False, f"sandbox requires Windows x86-64 (host: {sys.platform} {platform.machine()})")
        # A system image the loader can map, launched suspended through the exact run path and never resumed.
        image = Path(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "whoami.exe")
        try:
            outcome = self._execute(image.read_bytes(), b"", sandbox.Limits(), threading.Event(), resume=False)
        except (OSError, sandbox.SandboxUnavailable) as error:
            return sandbox.ProbeResult(False, f"sandbox setup failed: {error}")
        return sandbox.ProbeResult(True, None, outcome)

    def run(self, artifact: bytes, stdin: bytes, limits: sandbox.Limits, cancel: threading.Event | None = None,
            arguments: tuple[str, ...] = ()) -> sandbox.RunOutcome:
        probe = self.probe()
        if not probe.available:
            raise sandbox.SandboxUnavailable(probe.reason or "sandbox unavailable")
        if arguments:
            raise ValueError("the Windows sandbox passes no command-line arguments")
        if len(stdin) > limits.max_stdin_bytes:
            raise ValueError("stdin exceeds the configured limit")
        try:
            return self._execute(artifact, stdin, limits, cancel or threading.Event(), resume=True)
        except OSError as error:
            return sandbox.RunOutcome(None, None, b"", b"", False, False, False, False, 0.0, setup_error=str(error))

    def _execute(self, artifact: bytes, stdin: bytes, limits: sandbox.Limits, cancel: threading.Event, resume: bool):
        kernel32, advapi32, userenv = _api()
        sid = self._container_sid(userenv)
        directory = tempfile.mkdtemp(prefix="xax-mcp-run-")
        job = attributes = None
        pipes: list[int] = []
        info = _ProcessInformation()
        try:
            _grant(advapi32, kernel32, directory, sid)  # first, so the artifact file inherits the grant
            path = Path(directory, "prog.exe")
            with open(path, "xb") as handle:
                handle.write(artifact)
            job = _check(kernel32.CreateJobObjectW(None, None), "CreateJobObject")
            limits_info = _ExtendedLimits()
            limits_info.BasicLimitInformation.LimitFlags = _JOB_LIMITS
            limits_info.BasicLimitInformation.ActiveProcessLimit = 1
            limits_info.BasicLimitInformation.PerProcessUserTimeLimit = limits.cpu_seconds * 10_000_000
            limits_info.ProcessMemoryLimit = limits.memory_bytes
            _check(kernel32.SetInformationJobObject(job, 9, ctypes.byref(limits_info), ctypes.sizeof(limits_info)), "job limits")
            ui = w.DWORD(0xFF)  # every JOB_OBJECT_UILIMIT_* restriction
            _check(kernel32.SetInformationJobObject(job, 4, ctypes.byref(ui), ctypes.sizeof(ui)), "job UI limits")

            import _winapi
            import msvcrt

            child_in, parent_in = _winapi.CreatePipe(None, 0)
            parent_out, child_out = _winapi.CreatePipe(None, 0)
            parent_err, child_err = _winapi.CreatePipe(None, 0)
            pipes = [child_in, parent_in, parent_out, child_out, parent_err, child_err]
            for child_end in (child_in, child_out, child_err):
                os.set_handle_inheritable(child_end, True)
            handles = (w.HANDLE * 3)(child_in, child_out, child_err)

            size = ctypes.c_size_t()
            kernel32.InitializeProcThreadAttributeList(None, 5, 0, ctypes.byref(size))
            attributes = ctypes.create_string_buffer(size.value)
            _check(kernel32.InitializeProcThreadAttributeList(attributes, 5, 0, ctypes.byref(size)), "attribute list")
            capabilities = _SecurityCapabilities(sid.value, None, 0, 0)
            lpac, child_policy, mitigations = w.DWORD(1), w.DWORD(1), ctypes.c_uint64(_MITIGATIONS)
            for attribute, value, length in ((_ATTR_SECURITY_CAPS, ctypes.byref(capabilities), ctypes.sizeof(capabilities)),
                                             (_ATTR_PACKAGES_POLICY, ctypes.byref(lpac), ctypes.sizeof(lpac)),
                                             (_ATTR_CHILD_POLICY, ctypes.byref(child_policy), ctypes.sizeof(child_policy)),
                                             (_ATTR_MITIGATION, ctypes.byref(mitigations), ctypes.sizeof(mitigations)),
                                             (_ATTR_HANDLE_LIST, handles, ctypes.sizeof(handles))):
                _check(kernel32.UpdateProcThreadAttribute(attributes, 0, attribute, value, length, None, None), f"attribute {attribute:#x}")
            startup = _StartupInfoEx()
            startup.cb = ctypes.sizeof(startup)
            startup.dwFlags = 0x100  # STARTF_USESTDHANDLES
            startup.hStdInput, startup.hStdOutput, startup.hStdError = child_in, child_out, child_err
            startup.lpAttributeList = ctypes.addressof(attributes)
            command = ctypes.create_unicode_buffer('"prog.exe"')
            # An AppContainer launch needs LOCALAPPDATA (which Windows redirects to the container's own folder) and fails
            # with ERROR_ENVVAR_NOT_FOUND without it; SystemRoot is what the loader reads.  Nothing else is passed.
            environment = ctypes.create_unicode_buffer(
                "".join(f"{name}={os.environ[name]}\0" for name in ("LOCALAPPDATA", "SystemRoot") if name in os.environ) + "\0")
            # DETACHED_PROCESS: no console, so no conhost.exe child (the job allows one process); the pipes are the std handles.
            flags = 0x80000 | 0x4 | 0x8 | 0x400  # extended startup info, suspended, detached, unicode environment
            _check(kernel32.CreateProcessW(str(path), command, None, None, True, flags, environment, directory,
                                           ctypes.byref(startup), ctypes.byref(info)), "CreateProcess")
            for child_end in (child_in, child_out, child_err):
                kernel32.CloseHandle(child_end)
                pipes.remove(child_end)
            _check(kernel32.AssignProcessToJobObject(job, info.hProcess), "AssignProcessToJobObject")
            evidence = _confirm(kernel32, advapi32, job, info.hProcess)
            if not resume:
                return evidence
            started = time.perf_counter()
            _check(kernel32.ResumeThread(info.hThread) != 0xFFFFFFFF, "ResumeThread")
            streams = {"in": os.fdopen(msvcrt.open_osfhandle(parent_in, 0), "wb", buffering=0),
                       "out": os.fdopen(msvcrt.open_osfhandle(parent_out, 0), "rb", buffering=0),
                       "err": os.fdopen(msvcrt.open_osfhandle(parent_err, 0), "rb", buffering=0)}
            pipes = []  # now owned by the file objects
            return self._supervise(kernel32, job, info.hProcess, streams, stdin, limits, cancel, started)
        finally:
            if info.hProcess:
                kernel32.TerminateProcess(info.hProcess, 1)  # no-op once exited; kills a never-resumed probe
                kernel32.WaitForSingleObject(info.hProcess, 5000)
                kernel32.CloseHandle(info.hProcess)
                kernel32.CloseHandle(info.hThread)
            if job:
                kernel32.CloseHandle(job)  # kill on close
            if attributes is not None:
                kernel32.DeleteProcThreadAttributeList(attributes)
            for handle in pipes:
                kernel32.CloseHandle(handle)
            shutil.rmtree(directory, ignore_errors=True)

    @staticmethod
    def _supervise(kernel32, job, process, streams, stdin, limits, cancel, started) -> sandbox.RunOutcome:
        caps = {"out": limits.max_stdout_bytes, "err": limits.max_stderr_bytes}
        buffers = {"out": bytearray(), "err": bytearray()}
        truncated = {"out": False, "err": False}
        exceeded = threading.Event()

        def feed():
            try:
                streams["in"].write(stdin)
            except OSError:
                pass  # the program exited or closed stdin
            finally:
                streams["in"].close()

        def drain(name):
            stream = streams[name]
            while chunk := stream.read(65536):
                room = caps[name] - len(buffers[name])
                buffers[name] += chunk[:max(room, 0)]
                if len(chunk) > room:
                    truncated[name] = True
                    if name == "out":
                        exceeded.set()
            stream.close()

        threads = [threading.Thread(target=feed, daemon=True), *(threading.Thread(target=drain, args=(n,), daemon=True) for n in caps)]
        for thread in threads:
            thread.start()
        deadline = started + limits.wall_ms / 1000
        cpu_budget = limits.cpu_seconds * 10_000_000  # 100 ns units
        times = [ctypes.c_uint64() for _ in range(4)]  # creation, exit, kernel, user

        def cpu_used() -> int:
            kernel32.GetProcessTimes(process, *(ctypes.byref(t) for t in times))
            return times[2].value + times[3].value

        timed_out = cancelled = cpu_exceeded = False
        # The job's own CPU limit is checked only periodically by Windows, so it is the backstop; this loop enforces
        # wall time, CPU time, cancellation and the output quota at a 50 ms granularity.
        while kernel32.WaitForSingleObject(process, 50) != 0:  # WAIT_OBJECT_0
            if time.perf_counter() >= deadline:
                timed_out = True
            elif cancel.is_set():
                cancelled = True
            elif cpu_used() >= cpu_budget:
                cpu_exceeded = True
            elif not exceeded.is_set():
                continue
            kernel32.TerminateJobObject(job, 1)
            kernel32.WaitForSingleObject(process, 5000)
            break
        wall_ms = (time.perf_counter() - started) * 1000
        for thread in threads:
            thread.join(5)
        code = w.DWORD()
        _check(kernel32.GetExitCodeProcess(process, ctypes.byref(code)), "GetExitCodeProcess")
        killed = timed_out or cancelled or exceeded.is_set()
        cpu_exceeded = cpu_exceeded or (not killed and cpu_used() >= cpu_budget)
        killed = killed or cpu_exceeded
        name = None if killed or code.value < 0x80000000 else _EXCEPTIONS.get(code.value, f"NTSTATUS_{code.value:#010x}")
        return sandbox.RunOutcome(None if name or killed else code.value, name, bytes(buffers["out"]), bytes(buffers["err"]),
                          truncated["err"], timed_out, cancelled, exceeded.is_set(), wall_ms,
                          cpu_limit_exceeded=cpu_exceeded)


def _grant(advapi32, kernel32, directory: str, sid) -> None:
    """Add read/execute for the container SID to the private run directory (inherited by the artifact file)."""
    old, descriptor = ctypes.c_void_p(), ctypes.c_void_p()
    status = advapi32.GetNamedSecurityInfoW(directory, 1, 4, None, None, ctypes.byref(old), None, ctypes.byref(descriptor))
    if status:
        raise OSError(status, "GetNamedSecurityInfo")
    access = _ExplicitAccess(0xA0000000, 1, 3, _Trustee(None, 0, 0, 0, sid.value))  # GENERIC_READ|EXECUTE, GRANT, inherit
    new = ctypes.c_void_p()
    try:
        status = advapi32.SetEntriesInAclW(1, ctypes.byref(access), old, ctypes.byref(new))
        if status:
            raise OSError(status, "SetEntriesInAcl")
        status = advapi32.SetNamedSecurityInfoW(directory, 1, 4, None, None, new, None)
        if status:
            raise OSError(status, "SetNamedSecurityInfo")
    finally:
        kernel32.LocalFree(new)
        kernel32.LocalFree(descriptor)


def _token_attributes(advapi32, token) -> set[str]:
    """Names of the token's security attributes (TokenSecurityAttributes).  A less privileged AppContainer carries
    ``WIN://NOALLAPPPKG``; the TokenIsLessPrivilegedAppContainer query class is not served on every Windows build."""
    length = w.DWORD()
    advapi32.GetTokenInformation(token, 39, None, 0, ctypes.byref(length))
    buffer = ctypes.create_string_buffer(length.value)
    _check(advapi32.GetTokenInformation(token, 39, buffer, length, ctypes.byref(length)), "TokenSecurityAttributes")
    # TOKEN_SECURITY_ATTRIBUTES_INFORMATION: WORD version, WORD reserved, DWORD count, pointer to 40-byte
    # TOKEN_SECURITY_ATTRIBUTE_V1 records that start with a UNICODE_STRING name (USHORT length, pointer at +8).
    count = int.from_bytes(buffer.raw[4:8], "little")
    records = ctypes.c_void_p.from_buffer(buffer, 8).value
    return {ctypes.wstring_at(ctypes.c_void_p.from_address(records + 40 * i + 8).value,
                              ctypes.c_ushort.from_address(records + 40 * i).value // 2) for i in range(count)}


def _confirm(kernel32, advapi32, job, process) -> dict:
    """Observe the confinement of the suspended process before it may run; raise when any part is missing."""
    token = w.HANDLE()
    _check(advapi32.OpenProcessToken(process, 0x8, ctypes.byref(token)), "OpenProcessToken")  # TOKEN_QUERY
    try:
        value, length = w.DWORD(), w.DWORD()
        _check(advapi32.GetTokenInformation(token, 29, ctypes.byref(value), 4, ctypes.byref(length)), "TokenIsAppContainer")
        observed = {"app_container": bool(value.value), "less_privileged": "WIN://NOALLAPPPKG" in _token_attributes(advapi32, token)}
    finally:
        kernel32.CloseHandle(token)
    in_job = w.BOOL()
    _check(kernel32.IsProcessInJob(process, job, ctypes.byref(in_job)), "IsProcessInJob")
    observed["in_job"] = bool(in_job.value)
    if not all(observed.values()):
        raise sandbox.SandboxUnavailable(f"sandbox probe did not observe the required isolation: {observed}")
    return {"token": "less privileged AppContainer, no capabilities", "job": "memory, CPU time, 1 process, kill on close, UI",
            "mitigations": "child processes, dynamic code, win32k, extension points, remote/low-label images"}
