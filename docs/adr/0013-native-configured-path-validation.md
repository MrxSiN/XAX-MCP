# Reject configured reparse paths before compiler-backed operations

Date: 2026-11-10. Status: implemented and locally executed; release acceptance false.

The process-lifetime scratch lease excluded cooperating servers but allowed a
configured work directory, compiler or seed to traverse a junction. Rechecking
only when acquiring the lease would also miss ancestor replacement between calls.

Add canonical XAX path-validation functions, require existing drive-qualified
absolute configured names and inspect every component through the existing
Windows attribute foreign interface. Reject reparse/ambiguous paths and incorrect
final object kinds before leasing scratch or starting compiler work. Run the
checks on every compiler-backed tool, preserving busy-workspace and authority
behavior. Return the distinct bounded `unsafe_host_path` error without exposing
private path names.

Publish gen3 through an exact-root native transaction. The authoring compiler is
separate from the unchanged Windows deployment pin; native Windows edit/verify
replays the packed native-authored objects to identical canonical bytes. Keep
historical gen2 source/manifests and evidence. Existing CI changes select native
inputs and remove package exclusion/reuse options; no new other-language
implementation is added. Include replay carriers in fresh preview archives.

Tests cover configured junctions and other rejected path forms, valid paths, all
six compiler-backed tools, revalidation after lease acquisition, preservation of
the 92-exchange suite and clean-package reproduction. The guard does not provide
an identity-pinned filesystem operation, hard-link protection or complete
TOCTOU/crash/cancellation security. Those remain blockers.
