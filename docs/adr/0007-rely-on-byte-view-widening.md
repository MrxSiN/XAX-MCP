# ADR-0007: Rely on byte-view widening (XAX host contract r2)

**Status:** accepted (0.3.0)

**Context.** XAX ADR-231 (`b0ec772`) lets `checked.load.bits.le` / `checked.store.bits.le` move 1, 2, 4 or 8 bytes
at a byte offset of a `bits<8>` view, and publishes the widths as
`xax_contract.FORMATS["checked_byte_view_widths"]` with `HOST_CONTRACT_MINOR = 2`. This was this project's
proposal P4.

**Decision.** Pin `b0ec772` and require host contract revision ≥ 2. Report the widths in `xax_capabilities` as
`targets[0].checked_byte_view_widths`, so agents emit one wide access instead of composing bytes. Test carriers
use the wide form by default and keep the byte-composed form to check that both compute the same values.

**Consequences.** Typical carriers are about half the size, and the generated executables are smaller
(`poly_reduce`: 647 vs 1,668 bytes). XAX builds without r2 are `incompatible`. On RISC-V and SPIR-V targets,
which this adapter does not offer, upstream rejects the wide form.
