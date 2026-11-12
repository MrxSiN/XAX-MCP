# Required native file and inspection contracts

These are **required upstream contracts, not implemented APIs**. The dependency
direction remains XAX-MCP to XAX. The deployment pin is unchanged. Any compiler
extension belongs in a separate verified upstream change, independently tested
before integration and repinning.

The [2026-11-12 inspection output-name pin](NATIVE_INSPECTION_PINS_20261112.md)
is a bounded application-side increment: exclusive creation and a lifetime-held
output handle prevent the tested inspection name substitutions. Existing outputs
are refused, including after restart. A controlled writer can still alter the
output contents, and mutation/build/publication retain their previous contracts.
The full upstream contracts below therefore remain required and unimplemented.

## File inputs, outputs and publication

The experimental server pins configured files and ancestors, but the pinned
compiler opens workspace inputs and outputs by filename. Controlled
[pre-existing and concurrent `edit.rec` aliases](evidence/native-candidate-aliases-20261111.json)
overwrite disposable outside files. Configured-file hard-link rejection and source
preservation pass in the same tests. The remaining trusted-host boundary includes
writable workspace child names and DOS drive aliases.

A reusable upstream native invocation contract must provide these guarantees:

1. Inputs are already opened file handles plus bounded lengths, expected file
   identities and expected canonical roots. The compiler consumes those exact
   objects without reopening an input pathname. The caller seals mutation carriers
   before compiler access. Explicit handle transfer grants only the required
   access; unlisted server handles remain non-inheritable.
2. Outputs are caller-created, exclusive new objects bound to held directory and
   volume identities. The caller refuses existing objects, reparse points, wrong
   types and unexpected hard-link aliases before any output truncation. The compiler
   writes only supplied output handles and returns their identities, exact lengths,
   completion status and root/artifact/provenance identities. It cannot pick an
   output pathname or independently reopen one.
3. Verification reads the same sealed candidate object that was produced. Publication
   replaces the expected current object relative to a held directory identity,
   checks both expected current file identity and root, and publishes the verified
   candidate identity atomically. A prior pathname check is insufficient. Validation
   and publication must not be separated by an attacker-controlled name lookup.
4. Identity covers the volume and file, not a DOS drive letter. A drive alias change
   cannot redirect an accepted input, output or publication. If the platform cannot
   provide this property, the operation declines before creating/writing outputs.
5. Cancellation, compiler failure, missing completion, timeout and crashes publish
   nothing. Cleanup touches only objects owned by that invocation; it cannot follow
   a substituted cleanup name. Live compiler descendants must be confirmed dead
   before scratch can be reused. Recovery preserves the last published source/root
   and allows a later exclusive lease without accepting incomplete outputs.

The versioned transport must describe handle representation/ownership, permitted
access and inheritance, lengths/budgets, identity representation, expected roots,
completion and decline diagnostics, publication preconditions and cleanup. The
compiler's file contract must support resolve, edit, verify, inspect and build;
the adapter must not reimplement canonical parsing or verification to compensate.

Independent acceptance must cover configured and child-file hard-link aliases,
directory replacement, pre-existing output files, input/output swaps while the
compiler runs, DOS alias remapping, crashes at each create/seal/verify/publish step,
matching/unknown/late cancellation, descendant cleanup and lease recovery. Tests
must compare source bytes/root before and after every rejection and check outside
sentinels for writes. A passing no-attacker run or repeated path check cannot close
these gates. Current [case data](../tests/security/host-paths/candidate-alias-cases.json)
distinguishes executed denials from executed outside-write failures and untested
windows.

## Public semantic inspection extension

The existing public record supplies kind tags, stable CIDs and CID-ordered reference
arrays. MCP can use those edges, but they do not identify which edge is a call or
provide typed function facts. The smallest general extension should add a
versioned bounded public record for a requested function CID: parameter/result
types, blocks and typed operations, direct call targets, effects and their stable
object identities. The compiler owns decoding, typing and verification.

Each page must bind to an exact root and selector, expose an unambiguous continuation,
bound bytes and entities, and distinguish completion from truncation. Unknown CIDs,
unsupported kinds, stale roots and insufficient budgets need explicit diagnostics.
Call/dependency/user/neighborhood queries can then consume public facts without
reading canonical internals. Independently compare this record with an unfamiliar
native-authored multi-function program and a real call edge before integrating it.
P1 also requires locating that program through documented tools and obtaining a
bounded paginated neighborhood; it remains incomplete.
