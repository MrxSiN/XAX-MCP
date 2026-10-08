# ADR-0003: A fixed, single-file sandbox executor that fails closed

**Status:** accepted (0.1.0)

**Context.** Verified XAX programs are still untrusted native code. Upstream's runner is a test harness. The
container had no bubblewrap/nsjail. Linux user namespaces, chroot, rlimits, and seccomp are available without
privileges on mainstream kernels.

**Decision.** `_sandbox_exec.py` is a standard-library-only launcher, started as `python -I -S` with an empty
environment and a fixed argv. It applies the isolation in order (PDEATHSIG, namespaces, read-only chroot,
rlimits, no_new_privs, seccomp allowlist) and then `execve`s the artifact. The server probes it at startup and
refuses execution when the probe fails. The launcher runs in its own process, never through `preexec_fn`
inside the multithreaded server.

**Consequences.** About 30 ms of interpreter start per execution. Linux x86-64 only. Effects other than stdio
need explicit new host grants and a matching seccomp/mount policy.
