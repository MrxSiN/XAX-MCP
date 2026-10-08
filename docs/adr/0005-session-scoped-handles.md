# ADR-0005: Session-scoped random handles keyed by transport connection

**Status:** accepted (0.1.0)

**Decision.** All server state (workspaces, artifacts, results, the build cache) lives in a per-connection
`Session` keyed by the SDK transport's connection-scoped outbound channel. A fresh connection object is
created per request on protocol 2026-07-28, so that object cannot be the key. Handles are random and
unguessable. Builds are cached per session, never shared across clients.

**Consequences.** A reconnecting client starts empty: it can re-open stores or re-construct, and identities
are deterministic (the same carrier gives the same root and artifact digest). Cross-client leakage is not
possible by design, and tests cover it.
