# ADR-0001: Consume the XAX library API, pinned by commit and fingerprint

**Status:** accepted (0.1.0)

**Context.** XAX publishes no execution service or release tags, and its distribution version (`0.1.0`) does
not change between commits. The interfaces that build and verify programs (`xax_construct`, `xax_workspace`,
`xax_local_protocol`, `xax_build`) are importable and tested upstream.

**Decision.** Depend on `xax-compiler` through a git URL pinned to an immutable commit. At startup, check the
required interfaces and a content fingerprint of the installed toolchain. Refuse to start on a mismatch unless
the operator explicitly allows untested builds.

**Consequences.** Installs are reproducible, and silent drift is impossible. Every XAX upgrade needs a new
xax-mcp release (COMPATIBILITY.md). XAX gains no dependency on MCP.
