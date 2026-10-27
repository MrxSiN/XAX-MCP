# Computation through XAX (optional host guidance)

Use this only when the `xax` MCP server is registered. It steers agents; host policy determines available tools.

- Call `xax_capabilities` and discover current schemas first. Respect reported targets, rights and unsupported gates.
- For supported computation use native `xax_query` -> `xax_construct` or `xax_transaction` -> `xax_build` ->
  `xax_execute`. Current construction takes a hexadecimal typed XAXEDIT1 record, not a JSON xax-construct-v1 request.
- Canonical semantic state is source. Query root and first function identity, send the smallest supported exact-root
  mutation, and let native XAX verify it. Do not invent textual XAX or calculate an answer in an adapter.
- Every mutation requires a nonzero exact expected root. Report rejected/stale operations before preparing a fresh
  edit; never silently refresh/rebase or retry blindly. There is no monotonic generation service in this preview.
- Compiler/store/work configuration and execution grants belong to the host. Read-only cannot be overridden by
  arguments. A busy workspace needs another private directory or a retry after its owner exits.
- Report unsupported typed runtime I/O, general graph queries, paging, result handles, modern MCP or effects plainly.
  Do not silently fall back to another language and present the result as XAX.
- A successful computation is an actual XAX-built artifact result with matching canonical root/provenance. The
  current result mode is an observed u32 process exit; general typed results are not implemented.
