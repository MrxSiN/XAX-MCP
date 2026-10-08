from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

ALL_RIGHTS = frozenset({"read", "mutate", "build", "execute"})


@pytest.fixture(scope="session")
def service():
    from xax_mcp.policy import Policy
    from xax_mcp.service import Service

    svc = Service(Policy(rights=ALL_RIGHTS))
    svc.warm_up()
    return svc


@pytest.fixture()
def session(service):
    from xax_mcp.service import Session

    return Session(service.policy)


def sandbox_available() -> bool:
    from xax_mcp.sandbox import Sandbox

    return Sandbox().probe().available


# CI sets XAX_MCP_REQUIRE_SANDBOX=1 so that a missing sandbox fails the run instead of skipping execution tests.
if os.environ.get("XAX_MCP_REQUIRE_SANDBOX") == "1" and not sandbox_available():
    raise RuntimeError("XAX_MCP_REQUIRE_SANDBOX=1 but the OS sandbox probe failed")
needs_sandbox = pytest.mark.skipif(not sandbox_available(), reason="OS sandbox unavailable on this host (execution fails closed)")
