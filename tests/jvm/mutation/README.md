# Native JVM mutation fixtures

Each `.edit` is an exact-root typed carrier for the base bound in `manifest.json`.
Most use `../wordcount-v1.xax`; deletion and result-type cases use the native
insertion/rebinding result. Its matching
canonical `.xax`, executable JAR and provenance were produced by the mutation
preview's pinned native compiler, with mandatory verification and two identical
builds. `manifest.json` binds every byte and records the independently checked
Java output. The application is canonical XAX; there is no Java source helper.

The positive cases cover all nine operation kinds: a delimiter, wrapping
arithmetic, references, an operand, insertion/rebinding, deletion of an unused
node, a valid result-type change, and a value passed across a reconnected edge.
The negative cases retain the source. A wrong result type can produce an edited
candidate, but native verification rejects it before the MCP server publishes it.
Reusing a positive record against its changed snapshot also rejects as stale.

These fixtures exercise unsigned resolved memory-profile snapshots. They do not
authorize signing, provenance rewriting, recursion-group editing, arbitrary
package selection or unresolved-request building. The earlier JVM preview and its
snapshot-mutation decline fixture retain their separately pinned historical scope.
