# Native STDIO fixtures

`readonly.requests.ndjson` and `readonly.responses.ndjson` are the 0.10.0 native protocol golden fixture: handshake,
notification, discovery, capabilities, denied operations, unsupported methods/tools, malformed JSON and resync.
The emitted schema is `schemas/tools-v2.json`; the v1 file is historical.

`native-sessions.json` contains five isolated compiler-backed client sessions with 46 exchanges and selected expected
response fields. Together they exercise new graph construction through xax_construct, native build/confined execution
(40 then 136), staleness, rights, schema rejection, candidate verification and zero-root rejection. CI adds five
concurrent-process exchanges to check exclusive shared-workdir ownership and crash release (51 baseline total).
The 0.10 executor cases in the same workflow extend that total to 92 exchanges;
they cover binary stdin/argv, malformed/over-limit requests, exact stream separation,
CPU/output budgets, environment, confinement and launcher-failure classification.

The workflow's PowerShell is external transport/assertion orchestration only; it is never a production runtime helper.
Every operation runs in the native XAX server/compiler/launcher. Timeout fixture execution is separately checked.

`tests/security/executor-input/` contains replayable canonical native probes for
binary EOF/streams, independent argv, CPU/output boundaries, token/filesystem/network
and environment observations, plus simulated launcher-status fixtures. These are
synthetic data and XAX programs; no foreign runtime helper implements the executor.

[Hosted run 41314738774](../../docs/evidence/native-executor-ci-41314738774.json)
passed the golden responses and all 92 client exchanges. Timeout and live-worker
launcher termination are separate workflow gates, not additional client exchanges.
