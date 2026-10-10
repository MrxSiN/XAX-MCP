# Upstream XAX proposals and their status

These were the smallest general upstream interfaces that would remove limitations of this adapter. They are now
upstream decisions in `MrxSiN/XAX`, committed as `f38cbeea2b90e9b6a580417ce7efaa7d3d75a183` and merged into XAX `main`
by `5c9ba68` (2026-10-08; renumbered ADR-222 to ADR-225 in the merge). XAX-MCP 0.2.0 pinned `f38cbee`.
P4 followed as ADR-231 in `b0ec772`, which XAX-MCP 0.3.0 pins. P6–P8 followed as ADR-248 to ADR-250 in `a6f0eb6`,
`6d1de1c` and `13a6843` (host contract r3), which XAX-MCP 0.5.0 pins. XAX-MCP 0.5.1 pins `f0aa191` (S8, ADR-251;
host contract r3 unchanged).

| # | Proposal | Status | Upstream record |
|---|---|---|---|
| P1 | `linux.startup.*` entities (argc/argv/env/auxv) in `xax-construct-v1` | DONE; XAX-MCP adds the `argv` input mode | ADR-223, `tests/test_xax_construct.py` |
| P2 | Versioned host-facing process contract | DONE: `xax_linux.process_contract()` = `linux-x86_64-process-v1` | ADR-224, ABI §19.4, `tests/test_xax_linux_process_contract.py` |
| P3 | Faster cold start: memoize component-store verification | DONE: first construct with a warm image cache went from 21.9 s to 2.7 s (MEASURED upstream) | ADR-222, `tests/test_verified_component_store.py` |
| P4 | Wide checked loads on byte views | DONE: on a `bits<8>` view, `checked.load/store.bits.le` move 1/2/4/8 bytes at a byte offset (`xax_contract.FORMATS["checked_byte_view_widths"]`, host contract r2); RISC-V and SPIR-V reject | ADR-231, `tests/test_xax_byte_view_widening.py` |
| P5 | Versioned contract identity | DONE: `xax_contract` = `xax-host-contract-v1` r1; XAX-MCP refuses to start without it | ADR-225, `tests/test_xax_contract.py` |
| P6 | Lazily zeroed native buffers | DONE: every large component view is an anonymous mapping; the warm server's RSS fell from about 800 MB to about 100 MB (MEASURED here) | ADR-248, `tests/test_native_startup.py` |
| P7 | One-call BLAKE3 for inputs over 1 MiB | DONE: `INPUT_EXTENT` is 16 MiB; with P6, loading the components from a populated cache takes about 0.4 s (was 2–7 s; MEASURED here) | ADR-249, `tests/test_xax_native_blake3.py` |
| P8 | Parallel or prebuilt component images | DONE (parallel; prebuilt images declined): `xax_native.prepare(parallel=True)`, host contract r3. XAX-MCP's warm server and `--prepare` call it; empty-cache `--prepare` 43.5 s → 24.4 s (MEASURED here) | ADR-250, `tests/test_native_startup.py`, `tests/test_xax_contract.py` |

## P4 (done in ADR-231)
Earlier, a `u64` read from a byte view took eight 1-byte checked loads plus multiplies and adds. Now it takes one
`["checked.load.bits.le", [PTR, OFFSET, MEM], ["b64", "mem"], {"attrs": [8, 1]}]`. The bounds check stays
`offset + size <= extent`, and initialization, permission and provenance rules are unchanged. In this repository's
`poly_reduce` carrier the request shrank from 19,810 to 9,267 bytes, the canonical store from 12,268 to 8,584 bytes,
and the executable from 1,668 to 647 bytes. Results are identical
(`test_wide_byte_view_access_matches_byte_composition_and_is_smaller`). The byte-composed form remains valid
(`programs.poly_reduce(..., wide=False)`).

## Remaining upstream cold-start cost (before P6–P8; see PERFORMANCE.md for the current numbers)
With an empty `XAX_NATIVE_CACHE`, every component image is still lowered once (about 50 s on the reference
host; one 0.3.1 sample at `6c2df90` took 41.7 s). With a warm cache, first construct took 2.7 s at `f38cbee`, about 3.5 s at
`b0ec772`, and 1.3 s in one sample at `6c2df90`. The time goes
to the native store verifier's table setup and BLAKE3 CID checks over the typing store, which grew with upstream
S8c.9–S8c.13. P4 did not cause it.

## P6–P8: first-start cost measured at `6c2df90` (proposed 2026-10-09; done in ADR-248 to ADR-250)

The proposal text below is kept as written. Upstream took option (a) for P7, the parallel option for P8, and declined
prebuilt images: an image is a deterministic function of its key, so shipping one only moves trust to the release
process, and every store change would add about 10 MB to the wheel (ADR-250 (4)). XAX-MCP 0.5.0 requires host
contract r3 and calls `xax_native.prepare` in place of its warm-up construct.

XAX-MCP 0.4.0 avoids repeating XAX's component load in every server launch (a per-user warm server, ADR-0008), but
it still pays that load once per install, and in-process launches pay it every time. The numbers below come from
cProfile runs of one `xax_construct.construct` of a minimal process in a fresh interpreter (Linux 6.18 x86-64,
Python 3.13). None of the three changes alters XAX semantics, a store, or a CID.

**P6: lazily zeroed native buffers (about 2.4 s and about 640 MB per process).** `NativeTyping.__init__`
(`xax_selfhost_typing.py`) and `NativeStoreVerifier.__init__` (`xax_selfhost_verify.py`) each allocate
`(ctypes.c_uint64 * IN_WORDS)()` and `(ctypes.c_uint64 * OUT_WORDS)()`: 64 MiB + 256 MiB, zero-filled eagerly. That
is 1.36 s and 1.34 s of the two constructors' own time, and the pages stay resident. An anonymous mapping is
zero-filled by the kernel on first touch: `buffer = mmap.mmap(-1, OUT_WORDS * 8)` and
`(ctypes.c_uint64 * OUT_WORDS).from_buffer(buffer)` give the same view with the same zero contents, at no cost until
a page is used. A standalone measurement of one 256 MiB `ctypes` array took 1.07 s.

**P7: one-call BLAKE3 for inputs over 1 MiB (about 2.5 s).** `blake3.blake3()` uses the XAX-hosted whole-input
hash only up to `xax_selfhost_blake3.INPUT_EXTENT` (1 MiB). The two largest component stores (3.56 MB and 2.09 MB)
fall back to the Python driver, which calls the XAX compression leaf once per 64-byte block: about 95k `ctypes`
calls costing 2.5 s, of which 1.5 s is argument marshalling in `NativeBlake3Compressor.compress`. Either option
works: raise `INPUT_EXTENT` (for example to 16 MiB, regenerating `xax_blake3_hash.xax`), or have the XAX hash
return chunk-subtree chaining values so the driver calls it once per 1 MiB subtree. Even the existing leaf path
would roughly halve its time with preallocated input/output arrays.

**P8: parallel or prebuilt component images (about 43 s with an empty cache).** With an empty `XAX_NATIVE_CACHE`
the components are lowered in sequence: typing (≈37 s under the profiler, of which `load_typing_program` ≈30 s
parses and verifies the typing store in Python because the native verifier does not exist yet), store verifier
(≈17 s), graph decoder (≈5 s), store decoder (≈2 s). They do not depend on each other's images. A public
`xax_native.prepare(parallel=True)` that lowers them in separate processes would bound the cold start by the
slowest component. Alternatively, images built and verified at package build time and shipped with their
digests would remove the cold start for every installed copy. A host could call such an API instead of the
warm-up construct; XAX-MCP will not call private loader functions (`_native_image`) outside the host contract.
