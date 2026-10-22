# Computation through XAX (optional guidance for agents)

Copy into your project's `CLAUDE.md` (Claude Code) when the `xax` MCP server is registered.

- Call `xax_capabilities` first. It reports the exact XAX pin, rights, targets, and honest maturity labels for this
  server build. The current native build implements the MCP protocol and capability reporting; the compiler- and
  decoder-backed tools are prototypes that need a host grant (`XAX_MCP_COMPILER`/`XAX_MCP_STORE` or
  `XAX_MCP_CONSTRUCT`) and fail closed without one.
- When the server reports a tool as implemented, use it for computation it supports instead of writing and running
  Python or shell code: `xax_construct` (a typed `xax-construct-v1` carrier) -> `xax_build` -> `xax_execute`.
- The carrier JSON is a typed semantic-graph request (transport), not source. Do not invent a textual XAX syntax.
- To change a constructed program, query the smallest neighborhood (`xax_query`) and send a typed edit with the
  exact `expected_generation`/`expected_root` (`xax_transaction`). On `stale_root`, re-query; never retry blindly.
- If a task needs something `xax_capabilities` reports as unsupported, say so plainly. Do not silently fall back to
  another language and present it as XAX.
- These instructions do not force tool selection; the host decides which tools are available.
