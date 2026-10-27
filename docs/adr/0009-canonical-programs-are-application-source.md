# 0009 — Canonical programs are application source

Date: 2026-10-27. Status: accepted for repository ownership; native-only toolchain completion remains open.

`meaning is source`: a verified canonical `.xax` store is XAX source. Earlier wording that this repository
contained "no source code" while holding those stores was incorrect. The server, sandbox and application
fixtures belong in XAX-MCP. Their canonical stores in `native/` are authoritative application state.
The schema snapshot is `schemas/tools-v1.json`; messages and mutation records remain transport.

The dependency direction remains XAX-MCP -> XAX. Generic graph construction, verification, workspace mutation,
native compilation and file-command contracts belong upstream. Existing upstream `compiler/integration/mcp`
copies and Python test helpers are historical migration debt; this decision does not claim they were ported or
removed. Current CI uses this repository's native artifacts and data fixtures without that directory.

No new application implementation or bootstrap in another programming language is permitted. CI may invoke
native executables and compare transport files with operating-system shell commands; that orchestration is
outside the application/runtime path and is disclosed. Do not treat smoke replay as semantic verification,
full protocol conformance or completion of the release security gate.
