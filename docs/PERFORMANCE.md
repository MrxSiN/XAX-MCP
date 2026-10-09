# Start-up performance

These are MCP tool round trips on one host. They are not XAX generated-code (R4) benchmarks, and they are not the
AI-token efficiency milestone.

## Where the time goes

A new `xax-mcp` process must import the MCP SDK (about 0.5 s) and load XAX's XAX-hosted compiler components
before its first verification. At XAX `13a6843` (host contract r3) the components load through the host contract,
`xax_native.prepare` (ADR-250). With a populated XAX image cache (`XAX_NATIVE_CACHE`, default
`~/.cache/xax-native`) loading takes about 0.4 s; at `6c2df90` it took 2–7 s. Upstream removed the two largest costs:

| Cost at `6c2df90` | Share | Upstream change |
|---|---|---|
| Zero-filling 2 × (64 MiB + 256 MiB) `ctypes` buffers for the typing program and store verifier | ~2.4 s | P6, ADR-248: lazily zeroed views |
| BLAKE3 digests of the two stores over 1 MiB, one `ctypes` call per 64-byte block (~95k calls) | ~2.5 s | P7, ADR-249: one call up to 16 MiB |

With an empty cache, every component image is lowered first. Loaded one after another, as a first verification
does, that takes about 42 s. `xax_native.prepare(parallel=True)` lowers them in three stages of child processes
and takes about 24 s here (P8, ADR-250). The critical path is now the typing store: verified by the Python
bootstrap, then lowered.

## What XAX-MCP does about it (0.5.0)

1. **Warm server** ([ADR-0008](adr/0008-per-user-warm-server.md)). Launches fork from a per-user process that
   already loaded everything, so the cost is paid once per install/configuration, not once per launch. The warm
   server calls `xax_native.prepare(parallel=True)` to fill the image cache, then `xax_native.prepare()` to load
   every component into itself before it forks. It stays at about 100 MB RSS (was about 800 MB at 0.4.0).
2. **`xax-mcp --prepare`** calls `xax_native.prepare(parallel=True)` itself, prints each component's status, then
   starts the warm server and waits for it. It fills the image cache even with the warm server turned off, which
   also speeds up in-process launches.
3. **In-process path.** When no warm server is ready, the server finishes its own imports and then loads the
   components with `xax_native.prepare()` in a background thread. It does not use the parallel pass, which costs
   about 1 s even when every image is cached.

The warm-up construct (a minimal process XAX-MCP constructed only to trigger the component loads) is gone.

## Measured (Linux 6.18 x86-64, Python 3.13, 4 vCPU; one run each)

| Mode | XAX | XAX image cache | launch → initialize | launch → first construct+build+execute | `--prepare` |
|---|---|---|---|---|---|
| 0.3.1, in-process | `6c2df90` | populated | 5.3 s | 6.7 s | — |
| 0.4.0, in-process (`--no-warm-server`) | `6c2df90` | populated | 1.0 s | 3.1 s | — |
| 0.4.0, in-process | `6c2df90` | empty | 1.0 s | 43.0 s | — |
| 0.4.0, warm server | `6c2df90` | populated | 0.10 s | 0.20 s | 3.2 s |
| 0.4.0, warm server | `6c2df90` | empty | 0.12 s | 0.23 s | 43.5 s |
| **0.5.0, in-process (`--no-warm-server`)** | `13a6843` | populated | 1.06 s | **1.30 s** | — |
| 0.5.0, in-process | `13a6843` | empty | 1.11 s | 41.8 s | — |
| **0.5.0, warm server** | `13a6843` | populated | **0.09 s** | **0.18 s** | 3.6 s |
| **0.5.0, warm server** | `13a6843` | empty | **0.09 s** | **0.19 s** | **24.4 s** |

Raw records: `docs/evidence/e2e-linux-x86_64-{warm,cold}-{in-process,warm-server}-0.5.0.json` (and `-0.4.0.json`),
recorded with `python scripts/record_evidence.py [--cold-cache] --mode {in-process,warm-server}`. The warm server
reported loading its components in 1.4 s, about 1.0 s of it in the parallel pass that found every image cached.
With a populated cache, `--prepare` runs that pass twice (once itself, once in the warm server), which is why it
takes 3.6 s rather than 3.2 s. After the first result, calls cost the same in every mode (construct ≈ 16–19 ms,
build ≈ 17–18 ms, execute ≈ 32–36 ms including the sandbox).

## What remains, and where

The empty-cache cost (about 24 s with `--prepare`, about 42 s for an in-process launch) is inside XAX. It is
bounded by verifying the typing store on the Python bootstrap and then lowering it. XAX decided not to ship
prebuilt images (ADR-250 (4)). The in-process path stays sequential, so an in-process launch with an empty cache
still pays the full sequential cost; run `xax-mcp --prepare` after installing or upgrading.
