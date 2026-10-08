"""Declared XAX compatibility is checked, and a mismatch fails with an informative error."""
from __future__ import annotations

import pytest

from xax_mcp import compat
from xax_mcp.policy import Policy


def test_installed_toolchain_is_the_tested_pin():
    result = compat.check()
    assert result.status == "tested", result.reason
    assert result.commit == compat.PINNED_XAX_COMMIT


def test_untested_toolchain_is_refused_unless_explicitly_allowed(monkeypatch):
    from xax_mcp.service import Service

    monkeypatch.setattr(compat, "TESTED_XAX", {"0" * 40: "f" * 64})
    monkeypatch.delenv(compat.ALLOW_UNPINNED_ENV, raising=False)
    with pytest.raises(RuntimeError, match="fingerprint matches no tested commit"):
        Service(Policy())
    monkeypatch.setenv(compat.ALLOW_UNPINNED_ENV, "1")
    assert Service(Policy()).compatibility.status == "untested"


def test_missing_upstream_interface_is_incompatible(monkeypatch):
    monkeypatch.setitem(compat.REQUIRED_API, "xax_construct", ("construct", "construct_v2_that_does_not_exist"))
    result = compat.check()
    assert result.status == "incompatible" and "construct_v2_that_does_not_exist" in result.reason


def test_xax_core_does_not_depend_on_mcp():
    """Dependency direction is XAX-MCP -> XAX only: the XAX distribution declares no MCP requirement."""
    import importlib.metadata

    requirements = importlib.metadata.requires("xax-compiler") or []
    assert not [r for r in requirements if "mcp" in r.lower() and "extra" not in r]
