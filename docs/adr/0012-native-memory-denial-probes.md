# Observe job commit-memory denial with native XAX controls

Date: 2026-11-10. Status: locally executed; release acceptance false.

The preview configured a 256 MiB process-commit cap, but retained memory-pressure
coverage as a blocker. Add two canonical XAX probes that request 64 MiB and
320 MiB through the existing foreign `VirtualAlloc` declaration, compare the
returned address and report a probe-specific observed exit. No allocation is
dereferenced. Process exit returns its allocation to Windows.

Author the small function through the upstream native workspace's exact-root
definition/replacement operation. Record the authoring executable by SHA-256,
separately from the older Windows deployment/compiler pin. Verify and build both
programs with that pinned Windows seed. The integer-only low-to-high XAXEDIT1
carrier contains no supplied semantic objects; native edit constructs the changed
constant and affected graph. Independent native batch construction of the high
program must produce identical canonical bytes.

Run both through the real native MCP server and existing AppContainer/job launcher,
three times each, and run unconfined positive controls. Also evolve one workspace
from low to high through MCP, execute before/after, reject the stale record and
verify the preserved root. This tests the actual allocation boundary and native
mutation path without adding another-language implementation to XAX-MCP.

Only the bounded allocation-denial case is established. Gradual pressure, physical
page pressure, exhaustion under concurrency, exhaustive cleanup/crash windows,
trap classification and independent escape review remain open. The existing
server reports a raw u32 child exit; a successful transport does not prove that
the program behaved correctly. No release status, general typed ABI, compiler
self-hosting or modern MCP claim follows from these probes.
