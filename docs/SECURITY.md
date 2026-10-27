# Security — native preview

Version 0.9.0 fixes the previously observed unverified-publication and argument-validation defects. It remains a
preview with incomplete security coverage. Passing XAX verification establishes semantic validity, not permission
to run arbitrary native code. [Remaining release gates](WINDOWS_READINESS.md) are normative for current claims.

Host-only configuration supplies compiler, seed, private work directory and rights. Tools cannot choose arbitrary
paths, commands, interpreters, network grants or effects. Read-only clients cannot acquire mutate/build/execute by
changing arguments. Execution requires `--allow-execute`, the native launcher and working Windows confinement.
There is no unrestricted fallback. STDOUT contains only JSON-RPC responses; closing stdin releases resources.

Public construction/edit requires a nonzero exact expected root. Native edit checks freshness; native verify must
succeed on the staged candidate before atomic publication. Verification rejection deletes the candidate and retains
the valid current store. Native compiler nonzero exits are failures, including unsupported/declined status 2.

A share-mode-zero, delete-on-close `CreateFileA` handle leases the host work directory for the server lifetime.
It is not inherited by child processes. Competing server processes get `workspace_busy`; retries after normal exit
or crash are tested. This does not defend against hostile peers running with the same Windows user's filesystem
rights. The host must keep compiler/store/work directories private and prevent untrusted link or file replacement.

The native XAX launcher runs generated code in a capability-less Windows AppContainer inside a job object. Fixed
limits are 5 seconds CPU, 256 MiB memory, one process, 10 seconds wall and 1 MiB capture per stream. Missing launcher
or confinement failure refuses execution. The timeout fixture is current evidence of wall-limit enforcement;
older AppContainer/outside-write observations retain their recorded historical scope.

Unfinished security work includes asynchronous compiler cancellation, comprehensive disk/handle/output saturation
quotas, current host interoperability and independent sandbox/escape review. No HTTP service, remote authority,
general effectful workload, scoped result store or typed runtime-data ABI is exposed. No blanket security certification
or full release readiness is claimed.

Current evidence covers invalid candidate rejection/cleanup, stale/zero roots, schema path/command probes, forged
result handle rejection, read-only and execution grants, separate directories, same-directory refusal and crash
lease release. External test/CI PowerShell handles transport and assertions only; every runtime component is XAX.
