# Canonical JVM fixtures

`wordcount-v0.xax` and `wordcount-v1.xax` are byte-exact imports of the upstream
canonical XAX snapshots identified in [the fixture manifest](manifest.json).
The retained JARs and provenance are native compiler outputs, rebuilt twice and
checked against an independent reference backend. There is no Java application
source or runtime helper here.

Both count LF, words and raw input bytes and print three width-seven decimal
fields. Whitespace bytes 9–13 and 32 end words. Version 0 starts words on printable
ASCII bytes; version 1 additionally starts words on high bytes. Other controls
do not start or end words. Acceptance checks empty input, every byte value,
UTF-8, buffer boundaries and the 262,144-byte input limit with an independent
byte-counting oracle.

`snapshot-mutation-decline.edit` requests one exact-root constant change. The
native editor currently declines snapshot ancestry with `XAX.WORKSPACE.TOPOLOGY`;
the source stays unchanged and no mutation is published. This is a negative
boundary fixture, not an implemented JVM mutation example.

See the [JVM preview contract](../../docs/NATIVE_JVM_20261112.md) for the tested
compiler/runtime, explicit launch profile and remaining limits.
