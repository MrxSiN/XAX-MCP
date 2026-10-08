# ADR-0002: Official MCP Python SDK, low-level server, STDIO only

**Status:** accepted (0.1.0)

**Decision.** Use `mcp` 2.3's low-level `Server` with hand-written draft-2020-12 input schemas, validated with
`jsonschema` before dispatch. That keeps the schemas narrow and versioned (`xax-mcp-tools-v1`), unlike
signature-derived schemas. Ship STDIO only, because an unauthenticated network-exposed native-code runner is
unacceptable and local agent hosts launch STDIO servers. File descriptor 1 is moved to a private duplicate at
startup so that only the protocol writer can reach STDOUT.

**Consequences.** Streamable HTTP is UNIMPLEMENTED. Adding it requires authentication, origin/host checks, TLS,
and per-session isolation (SECURITY.md).
