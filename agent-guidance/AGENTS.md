# Computation through XAX (optional host guidance)

Copy this file into a project as `AGENTS.md` or `CLAUDE.md`. Use it only when the `xax` MCP server is registered. It steers agents; host policy determines available tools.

- Call `xax_capabilities` and discover current schemas first. Respect reported targets, rights and unsupported gates.
- For supported computation use native `xax_query` -> `xax_construct` or `xax_transaction` -> `xax_build` ->
  `xax_execute`. Current construction takes a hexadecimal typed XAXEDIT1 record, not a JSON xax-construct-v1 request.
- Canonical semantic state is source. Query root and first function identity, send the smallest supported exact-root
  mutation, and let native XAX verify it. Do not invent textual XAX or calculate an answer in an adapter.
- Every mutation requires a nonzero exact expected root. Report rejected/stale operations before preparing a fresh
  edit; never silently refresh/rebase or retry blindly. There is no monotonic generation service in this preview.
- Compiler/store/work configuration and execution grants belong to the host. Read-only cannot be overridden by
  arguments. A busy workspace needs another private directory or a retry after its owner exits.
- `xax_execute` accepts optional `stdin_hex` and `args` excluding executor-controlled argv[0]. Omission means
  empty input/no extra arguments. Use discovered host bounds; arguments grant no paths, environment or capabilities.
- Report unsupported typed runtime I/O, general graph queries, paging, result handles, modern MCP or effects plainly.
  Do not silently fall back to another language and present the result as XAX.
- A successful computation is an actual XAX-built artifact result with matching canonical root/provenance. Results
  include an observed u32 child exit, exact separate stdout/stderr hex and measured resources. Check `isError`/`ok`:
  budgets, launcher, measurement, transport and cleanup failures are errors. General typed results remain absent.
