# Upstream XAX proposals and their status

These were the smallest general upstream interfaces that would remove limitations of this adapter. They are now
upstream decisions in `MrxSiN/XAX`, committed as `f38cbeea2b90e9b6a580417ce7efaa7d3d75a183` and merged into XAX `main`
by `5c9ba68` (2026-10-08; renumbered ADR-222 to ADR-225 in the merge). XAX-MCP 0.2.0 pinned `f38cbee`.
P4 followed as ADR-231 in `b0ec772`, which XAX-MCP 0.3.0 pins.

| # | Proposal | Status | Upstream record |
|---|---|---|---|
| P1 | `linux.startup.*` entities (argc/argv/env/auxv) in `xax-construct-v1` | DONE; XAX-MCP adds the `argv` input mode | ADR-223, `tests/test_xax_construct.py` |
| P2 | Versioned host-facing process contract | DONE: `xax_linux.process_contract()` = `linux-x86_64-process-v1` | ADR-224, ABI §19.4, `tests/test_xax_linux_process_contract.py` |
| P3 | Faster cold start: memoize component-store verification | DONE: first construct with a warm image cache went from 21.9 s to 2.7 s (MEASURED upstream) | ADR-222, `tests/test_verified_component_store.py` |
| P4 | Wide checked loads on byte views | DONE: on a `bits<8>` view, `checked.load/store.bits.le` move 1/2/4/8 bytes at a byte offset (`xax_contract.FORMATS["checked_byte_view_widths"]`, host contract r2); RISC-V and SPIR-V reject | ADR-231, `tests/test_xax_byte_view_widening.py` |
| P5 | Versioned contract identity | DONE: `xax_contract` = `xax-host-contract-v1` r1; XAX-MCP refuses to start without it | ADR-225, `tests/test_xax_contract.py` |

## P4 (done in ADR-231)
Earlier, a `u64` read from a byte view took eight 1-byte checked loads plus multiplies and adds. Now it takes one
`["checked.load.bits.le", [PTR, OFFSET, MEM], ["b64", "mem"], {"attrs": [8, 1]}]`. The bounds check stays
`offset + size <= extent`, and initialization, permission and provenance rules are unchanged. In this repository's
`poly_reduce` carrier the request shrank from 19,810 to 9,267 bytes, the canonical store from 12,268 to 8,584 bytes,
and the executable from 1,668 to 647 bytes. Results are identical
(`test_wide_byte_view_access_matches_byte_composition_and_is_smaller`). The byte-composed form remains valid
(`programs.poly_reduce(..., wide=False)`).

## Remaining upstream cold-start cost
With an empty `XAX_NATIVE_CACHE`, every component image is still lowered once (about 50 s on the reference
host). With a warm cache, first construct took 2.7 s at `f38cbee` and about 3.5 s at `b0ec772`. The time goes
to the native store verifier's table setup and BLAKE3 CID checks over the typing store, which grew with upstream
S8c.9–S8c.13. P4 did not cause it.
