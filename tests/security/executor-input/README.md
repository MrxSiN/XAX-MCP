# Native executor acceptance fixtures

These are synthetic canonical XAX programs, native executables/provenance and
official exact-root `XAXEDIT1` transactions from the committed seed. The manifest
records source roots and file identities. JSON cases describe external transport
and expected observations; they are not runtime helpers or textual XAX.

| Fixture | Independent observation |
|---|---|
| quote-probe | Reads UTF-16 bytes through EOF and emits the native quoting result |
| argv-probe | Windows `CommandLineToArgvW`: u32 argument count excluding argv[0], then u32 UTF-16-unit length and exact UTF-16 bytes per argument |
| io-echo-probe | Reads stdin through physical EOF, writes each chunk separately to both streams, exits 7 |
| stream-separation-probe | Writes distinct `OUT\n` and `ERR\n` markers to stdout/stderr |
| cpu-probe | Large finite native loop, long enough to require the CPU/wall supervisor; a no-return entry initially declined at native build |
| flood-out/err-probe | Continuously writes the selected stream until bounded execution stops it |
| output-boundary-0/1-probe | Writes exactly 1,048,576 / 1,048,577 bytes |
| confinement-read-network-probe | Outside-file denial, copied-file reopen observation, loopback connect outcome and AppContainer token flag |
| environment-probe | Exact UTF-16 environment block; assertions retain key names and hashes, not personal values |
| launcher-status-7/8/9/10-probe | Simulated launcher status for setup/measurement/transport/cleanup protocol classification; does not force actual WinAPI failure |

The isolation observer emits six little-endian u32 words: outside-open denied,
outside-open Windows error, copied-image reopen succeeded, connect result,
WSA error and `TokenIsAppContainer`. A live synthetic loopback peer on
127.0.0.1:9 receives no confined connection; the same native observer in an
explicit operator positive control reaches it. A closed port alone was not
accepted as network-isolation evidence. No new read/write grant was added when
copied-image reopen/write assumptions failed.

External CI PowerShell performs transport/assertions and invokes the pinned native
compiler. All worker/observer code is XAX. For each fixture, CI edits the seed,
verifies the candidate, compares canonical bytes, resolves/builds, and compares
the executable and provenance. Every nonzero compiler status is failure, including
decline 2; diagnostic files must not be executed as programs.

See [the contract](../../../docs/NATIVE_EXECUTION_INCREMENT.md) and
[retained failures and results](../../../docs/evidence/native-executor-input-argv-20261101.json).
