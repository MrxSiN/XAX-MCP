# Computation through XAX (optional guidance for agents)

Copy into your project's `AGENTS.md` (Codex) when the `xax` MCP server is registered.

- For computation XAX supports (integer arithmetic, loops, reductions over typed input on Linux x86-64), use the
  `xax` MCP tools instead of writing and running Python or shell code: `xax_capabilities` -> `xax_construct`
  (an `xax-construct-v1` carrier) -> `xax_build` -> `xax_execute`.
- Call `xax_capabilities` first; it lists the operations, carrier types, I/O modes and effects that actually work.
- The carrier JSON is a typed semantic-graph request (transport), not source. Do not invent a textual XAX syntax.
- To change a constructed program, query the smallest neighborhood (`xax_query`) and send a typed edit with the
  exact `expected_generation`/`expected_root` (`xax_transaction`). On `stale_root`, re-query; never retry blindly.
- If a task needs something `xax_capabilities` reports as unsupported (strings, JSON/CSV, files, network, other
  targets), say so plainly. Do not silently fall back to another language and present it as XAX.
- These instructions do not force tool selection; the host decides which tools are available.
