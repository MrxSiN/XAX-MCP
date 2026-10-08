# Proposed upstream XAX interfaces (not implemented here)

This session had read-only access to `MrxSiN/XAX`, so nothing upstream was changed. Each proposal below is the
smallest general interface that would remove a limitation. Each belongs in a separately tracked XAX change, not
in this adapter.

## P1. Startup data in the construction carrier
**Gap.** `xax-construct-v1` exposes `linux_api()` entities only, so constructed programs get runtime data only
from stdin. `xax_linux.linux_startup_api()` (argc/argv/env, ADR-094) exists but is unreachable from the carrier.
**Proposal.** Accept `"linux.startup.<name>"` entities in `xax_construct._Builder.entity`. This is a few lines in
the carrier decoder with no new semantics. XAX-MCP could then offer an `argv` input mode.

## P2. A supported host-independent run contract
**Gap.** `xax_linux.run_linux_executable` is documented as "test harness only", so every integrator writes its
own launcher.
**Proposal.** Document the process contract that exists today (entry validation, exit status, trap = SIGILL,
stdin/stdout fds) as a versioned target fact (for example `linux-x86_64-process-v1`) without adding a runner.
Sandboxing stays a host concern.

## P3. Persist verified component images
**Gap.** The first verification in each process spends 20–50 s decoding and verifying the XAX-hosted typing
and verifier programs in Python, even with `XAX_NATIVE_CACHE` populated, because the cache stores machine code
images, not the decoded programs.
**Proposal.** Cache the verified component's decoded state, keyed by its store CID, next to the native image.
That would make an agent-launched server usable within a second.

## P4. Wide checked loads on byte views
**Observation.** `checked.load/store.bits.le` require the access size to equal the pointer element size, so a
u64 read from a `bytes_rw` view takes 8 loads (see `tests/programs.py:load64`). This is correct and verified,
just verbose. A documented element-retyping view cast would shrink carriers. This is low priority.

## P5. A versioned contract identity
`xax-compiler` reports version `0.1.0` at every commit. A contract version for the interfaces in
[XAX_CONTRACT.md](XAX_CONTRACT.md), or release tags, would let integrators declare ranges instead of exact
commits.
