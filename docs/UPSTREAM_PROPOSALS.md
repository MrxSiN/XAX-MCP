# Upstream XAX proposals and their status

These were the smallest general upstream interfaces that would remove limitations of this adapter. They are now
upstream decisions in `MrxSiN/XAX`, committed as `f38cbeea2b90e9b6a580417ce7efaa7d3d75a183` and merged into XAX `main`
by `5c9ba68` (2026-10-08; renumbered ADR-222 to ADR-225 in the merge). XAX-MCP 0.2.0 pins `f38cbee`.

| # | Proposal | Status | Upstream record |
|---|---|---|---|
| P1 | `linux.startup.*` entities (argc/argv/env/auxv) in `xax-construct-v1` | DONE; XAX-MCP adds the `argv` input mode | ADR-223, `tests/test_xax_construct.py` |
| P2 | Versioned host-facing process contract | DONE: `xax_linux.process_contract()` = `linux-x86_64-process-v1` | ADR-224, ABI §19.4, `tests/test_xax_linux_process_contract.py` |
| P3 | Faster cold start: memoize component-store verification | DONE: first construct with a warm image cache went from 21.9 s to 2.7 s (MEASURED upstream) | ADR-222, `tests/test_verified_component_store.py` |
| P4 | Wide checked loads on byte views | NOT DONE (see below) | — |
| P5 | Versioned contract identity | DONE: `xax_contract` = `xax-host-contract-v1` r1; XAX-MCP refuses to start without it | ADR-225, `tests/test_xax_contract.py` |

## P4 (not implemented)
`checked.load/store.bits.le` require the access size to equal the pointer element size, and `pointer.cast` must
keep the element type (`MEMORY-POINTER-CAST-NO-AUTHORITY-GAIN`). Allowing wider accesses on byte views would
change a kernel verification rule. That rule is mirrored by the XAX-hosted typing program and lowered by every
backend (x86-64, AArch64, RISC-V, JVM, plus the register allocators). It is a semantic decision for the XAX
maintainers, not an integration fix. Carriers keep assembling multi-byte values from byte loads
(`tests/programs.py:load64`). This is verbose but correct.

## Remaining upstream cold-start cost
With an empty `XAX_NATIVE_CACHE`, every component image is still lowered once (about 50 s on the reference
host). The remaining 2.7 s is the native store verifier's table setup and BLAKE3 CID checks.
