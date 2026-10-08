# ADR-0004: `xax-mcp-io-v1`, typed framing over stdin/stdout

**Status:** accepted (0.1.0)

**Context.** The pinned XAX Linux process entry takes no machine parameters, and the carrier reaches only the
read/write syscalls, so typed tool inputs must reach a program as bytes.

**Decision.** Encode `ints` (b8/b16/b32/b64, little-endian) and raw bytes or text onto stdin. Decode stdout only
by a caller-declared layout. A length mismatch is reported, never padded or reinterpreted. The program defines
the meaning of the bytes, and the adapter never combines values.

**Consequences.** Typed I/O works without upstream changes. argv/env input waits for upstream proposal P1.
