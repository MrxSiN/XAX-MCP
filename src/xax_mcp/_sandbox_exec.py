"""Fixed sandbox executor for one XAX-built Linux x86-64 static executable.

This file is the whole audited executor boundary.  It is launched by ``xax_mcp.sandbox`` as a fresh,
single-threaded interpreter (``python -I -S <this file> ...``) with an empty environment and a constrained
argument vector (no shell).  It confines itself and then ``execve``\\ s ``/prog`` inside an empty read-only root:

1. new user, mount, network, IPC, UTS and cgroup namespaces (the network namespace has no interfaces);
   the caller's uid/gid map to 65534 inside, so the executed program holds no capabilities;
2. the artifact directory is bind-mounted read-only/nosuid/nodev onto itself and becomes the root (``chroot``);
3. resource limits: address space, CPU seconds, zero file size, three file descriptors, no core dumps;
4. ``no_new_privs`` and a seccomp-BPF allowlist: read, write, close, mmap, munmap, brk, rt_sigreturn,
   execve, exit, exit_group.  Every other system call (open, socket, fork/clone, ptrace, ...) fails with EPERM;
   a foreign architecture or the x32 ABI kills the process.

It holds no XAX semantics and never computes a workload; it only confines and launches.  If any step fails, it
reports the failure on the status pipe and exits 125 without running the artifact (fail closed).  It uses only
the standard library so that ``-S`` (no site-packages) keeps the executor independent of installed packages.
"""

import ctypes
import json
import os
import resource
import signal
import struct
import sys

CLONE_NEWNS, CLONE_NEWCGROUP, CLONE_NEWUTS, CLONE_NEWIPC, CLONE_NEWUSER, CLONE_NEWNET = (
    0x00020000, 0x02000000, 0x04000000, 0x08000000, 0x10000000, 0x40000000)
MS_RDONLY, MS_NOSUID, MS_NODEV, MS_REMOUNT, MS_BIND, MS_REC, MS_PRIVATE = 1, 2, 4, 32, 4096, 16384, 1 << 18
PR_SET_PDEATHSIG, PR_SET_NO_NEW_PRIVS, PR_SET_SECCOMP, SECCOMP_MODE_FILTER = 1, 38, 22, 2
AUDIT_ARCH_X86_64 = 0xC000003E
SECCOMP_RET_KILL_PROCESS, SECCOMP_RET_ERRNO, SECCOMP_RET_ALLOW = 0x80000000, 0x00050000, 0x7FFF0000
EPERM = 1
INNER_ID = 65534
# x86-64 system call numbers the confined program may use.
ALLOWED_SYSCALLS = {"read": 0, "write": 1, "close": 3, "mmap": 9, "munmap": 11, "brk": 12, "rt_sigreturn": 15,
                    "execve": 59, "exit": 60, "exit_group": 231}

_libc = ctypes.CDLL(None, use_errno=True)


def _check(result, step):
    if result != 0:
        error = ctypes.get_errno()
        raise OSError(error, f"{step}: {os.strerror(error)}")


def _write(path, text):
    fd = os.open(path, os.O_WRONLY)
    try:
        os.write(fd, text.encode())
    finally:
        os.close(fd)


def seccomp_program():
    """Classic BPF allowlist over ``struct seccomp_data`` (nr at offset 0, arch at offset 4)."""
    ld_abs, jeq, jge, ret = 0x20, 0x15, 0x35, 0x06
    out = [(ld_abs, 0, 0, 4), (jeq, 1, 0, AUDIT_ARCH_X86_64), (ret, 0, 0, SECCOMP_RET_KILL_PROCESS),
           (ld_abs, 0, 0, 0), (jge, 0, 1, 0x40000000), (ret, 0, 0, SECCOMP_RET_KILL_PROCESS)]
    for number in sorted(ALLOWED_SYSCALLS.values()):
        out += [(jeq, 0, 1, number), (ret, 0, 0, SECCOMP_RET_ALLOW)]
    out.append((ret, 0, 0, SECCOMP_RET_ERRNO | EPERM))
    return b"".join(struct.pack("<HBBI", *item) for item in out), len(out)


def confine(directory, memory_bytes, cpu_seconds, parent):
    uid, gid = os.getuid(), os.getgid()
    # Die with the server: the program is killed if the launching server thread/process goes away.
    _check(_libc.prctl(PR_SET_PDEATHSIG, signal.SIGKILL, 0, 0, 0), "parent-death signal")
    if os.getppid() != parent:
        raise OSError(0, "server exited before the sandbox was established")
    _check(_libc.unshare(CLONE_NEWUSER | CLONE_NEWNS | CLONE_NEWNET | CLONE_NEWIPC | CLONE_NEWUTS | CLONE_NEWCGROUP), "unshare")
    _write("/proc/self/setgroups", "deny")
    _write("/proc/self/uid_map", f"{INNER_ID} {uid} 1")
    _write("/proc/self/gid_map", f"{INNER_ID} {gid} 1")
    namespaces = {name: os.readlink(f"/proc/self/ns/{name}") for name in ("user", "mnt", "net", "ipc", "uts", "cgroup")}
    path = directory.encode()
    _check(_libc.mount(None, b"/", None, MS_REC | MS_PRIVATE, None), "mount private")
    _check(_libc.mount(path, path, None, MS_BIND, None), "bind mount")
    _check(_libc.mount(None, path, None, MS_REMOUNT | MS_BIND | MS_RDONLY | MS_NOSUID | MS_NODEV, None), "read-only remount")
    _check(_libc.chroot(path), "chroot")
    os.chdir("/")
    namespaces["root_entries"] = sorted(os.listdir("/"))
    # CPU: SIGXCPU at the soft limit (reported as a quota), SIGKILL one second later at the hard limit.
    limits = ((resource.RLIMIT_AS, memory_bytes, memory_bytes), (resource.RLIMIT_CPU, cpu_seconds, cpu_seconds + 1),
              (resource.RLIMIT_FSIZE, 0, 0), (resource.RLIMIT_CORE, 0, 0), (resource.RLIMIT_NPROC, 1, 1),
              (resource.RLIMIT_MEMLOCK, 0, 0), (resource.RLIMIT_NOFILE, 3, 3))
    for kind, soft, hard in limits:
        resource.setrlimit(kind, (soft, hard))
    _check(_libc.prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0), "no_new_privs")
    return namespaces


def install_seccomp():
    program, length = seccomp_program()
    buffer = ctypes.create_string_buffer(program, len(program))

    class SockFprog(ctypes.Structure):
        _fields_ = [("len", ctypes.c_ushort), ("filter", ctypes.c_void_p)]

    fprog = SockFprog(length, ctypes.addressof(buffer))
    _check(_libc.prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, ctypes.byref(fprog), 0, 0), "seccomp")


def main(argv):
    # argv: --status FD --dir DIR --memory BYTES --cpu SECONDS --parent PID [--probe] [-- PROGRAM_ARGUMENT...]
    program_arguments = argv[argv.index("--") + 1:] if "--" in argv else []
    argv = argv[:argv.index("--")] if "--" in argv else argv
    probe = "--probe" in argv
    pairs = [item for item in argv if item != "--probe"]
    options = dict(zip(pairs[0::2], pairs[1::2]))
    status = int(options["--status"])
    os.set_inheritable(status, False)  # closed by execve: the program never sees the status pipe
    try:
        namespaces = confine(options["--dir"], int(options["--memory"]), int(options["--cpu"]), int(options["--parent"]))
        if probe:
            root_entries = namespaces.pop("root_entries")
            report = {"ok": True, "uid": os.getuid(), "root_entries": root_entries, "namespaces": namespaces}
            install_seccomp()
            # Under the filter, opening a file must fail with EPERM.
            fd = _libc.syscall(257, -100, b"/prog", 0, 0)
            report["openat_denied"] = fd == -1 and ctypes.get_errno() == EPERM
            os.write(status, json.dumps(report).encode())
            os._exit(0)
        install_seccomp()
        vector = [b"/prog", *(os.fsencode(item) for item in program_arguments)]
        args = (ctypes.c_char_p * (len(vector) + 1))(*vector, None)
        envp = (ctypes.c_char_p * 1)(None)
        _libc.execve(b"/prog", args, envp)
        raise OSError(ctypes.get_errno(), "execve: " + os.strerror(ctypes.get_errno()))
    except BaseException as error:  # report every setup failure, never run unconfined
        try:
            os.write(status, json.dumps({"ok": False, "error": f"{type(error).__name__}: {error}"}).encode())
        finally:
            os._exit(125)


if __name__ == "__main__":
    main(sys.argv[1:])
