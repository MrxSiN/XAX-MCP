# Native STDIO fixtures

`readonly.requests.ndjson` and `readonly.responses.ndjson` are the 0.9.0 native protocol golden fixture: handshake,
notification, discovery, capabilities, denied operations, unsupported methods/tools, malformed JSON and resync.
The emitted schema is `schemas/tools-v2.json`; the v1 file is historical.

`native-sessions.json` contains five isolated compiler-backed client sessions with 46 exchanges and selected expected
response fields. Together they exercise new graph construction through xax_construct, native build/confined execution
(40 then 136), staleness, rights, schema rejection, candidate verification and zero-root rejection. CI adds five
concurrent-process exchanges to check exclusive shared-workdir ownership and crash release (51 total).

The workflow's PowerShell is external transport/assertion orchestration only; it is never a production runtime helper.
Every operation runs in the native XAX server/compiler/launcher. Timeout fixture execution is separately checked.
