"""Machine-readable tool errors.  Every failure a tool reports carries one of ``CODES``."""

from __future__ import annotations

CODES = {
    "unsupported": "the requested target, operation, input mode or effect is not implemented",
    "invalid_request": "arguments failed schema, type, range or size validation",
    "verification_failed": "the XAX verifier rejected the program or candidate",
    "stale_root": "the expected root/generation is not the workspace's current one",
    "conflict": "the transaction conflicts with the current semantic state",
    "build_error": "the XAX build service rejected the request",
    "denied_capability": "the server's host configuration does not grant this right or effect",
    "resource_limit": "a configured quota was exceeded",
    "runtime_failure": "the artifact ran but trapped, crashed or failed to start",
    "not_found": "unknown, expired, or foreign handle",
    "stale_artifact": "the artifact was built from a root that is no longer current",
    "sandbox_unavailable": "OS isolation could not be established; execution is refused",
    "incompatible_xax": "the installed XAX toolchain does not match the declared compatibility",
    "internal_error": "unexpected adapter failure (reported, never hidden)",
}


class ToolError(Exception):
    def __init__(self, code: str, message: str, *, repair: list[str] | None = None, diagnostic: dict | None = None,
                 details: dict | None = None):
        assert code in CODES, code
        super().__init__(message)
        self.code = code
        self.message = message
        self.repair = repair or []
        self.diagnostic = diagnostic
        self.details = details or {}

    def payload(self) -> dict:
        error = {"code": self.code, "message": self.message}
        if self.diagnostic is not None:
            error["xax_diagnostic"] = self.diagnostic
        if self.repair:
            error["repair"] = self.repair
        if self.details:
            error["details"] = self.details
        return {"ok": False, "error": error}
