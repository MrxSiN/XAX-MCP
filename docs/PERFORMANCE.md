# Start-up performance

These are MCP tool round trips on one host. They are not XAX generated-code (R4) benchmarks, and they are not the
AI-token efficiency milestone.

## Where the time goes

A new `xax-mcp` process must import the MCP SDK (about 0.5 s) and load XAX's XAX-hosted compiler components
before its first verification. With a populated XAX image cache (`XAX_NATIVE_CACHE`, default
`~/.cache/xax-native`), loading takes 2–7 s at XAX `6c2df90`. Profiled shares of one warm-cache load:

| Cost | Share | Owner |
|---|---|---|
| Zero-filling 2 × (64 MiB + 256 MiB) `ctypes` buffers for the typing program and store verifier | ~2.4 s | XAX (P6) |
| BLAKE3 digests of the two stores over 1 MiB, one `ctypes` call per 64-byte block (~95k calls) | ~2.5 s | XAX (P7) |
| Store decoding, `linux_api`, file reads | rest | XAX |

With an empty cache, every component image is lowered first: about 42 s, mostly Python-side parsing and
verification of the typing store (≈30 s under the profiler) and store-verifier store (≈12 s). The components are
independent and are lowered one after another (P8).

## What XAX-MCP does about it (0.4.0)

1. **Warm server** ([ADR-0008](adr/0008-per-user-warm-server.md)). Launches fork from a per-user process that
   already loaded everything, so the cost is paid once per install/configuration, not once per launch.
   Run `xax-mcp --prepare` after installing to pay it before the first client connects.
2. **In-process path.** When no warm server is ready, the server finishes its own imports before starting the
   XAX warm-up thread, so `initialize` no longer waits behind the warm-up (5.3 s → 1.0 s at 0.3.1 → 0.4.0).

## Measured (Linux 6.18 x86-64, Python 3.13, XAX `6c2df90`; one run each)

| Mode | XAX image cache | launch → initialize | launch → first construct+build+execute | `--prepare` |
|---|---|---|---|---|
| 0.3.1, in-process | populated | 5.3 s | 6.7 s | — |
| 0.4.0, in-process (`--no-warm-server`) | populated | 1.0 s | 3.1 s | — |
| 0.4.0, in-process | empty | 1.0 s | 43.0 s | — |
| **0.4.0, warm server** | populated | **0.10 s** | **0.20 s** | 3.2 s |
| **0.4.0, warm server** | empty | **0.12 s** | **0.23 s** | 43.5 s |

Raw records: `docs/evidence/e2e-linux-x86_64-{warm,cold}-{in-process,warm-server}-0.4.0.json`, recorded with
`python scripts/record_evidence.py [--cold-cache] --mode {in-process,warm-server}`. After the first result, calls
cost the same in every mode (construct ≈ 20 ms, build ≈ 20 ms, execute ≈ 30 ms including the sandbox).

## What remains, and where

The remaining first-start cost is inside XAX. UPSTREAM_PROPOSALS.md P6–P8 list the changes, measured here, that
would shorten both the `--prepare` time and the in-process path. They would also cut the warm server's resident
memory from about 800 MB.
