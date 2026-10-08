"""Path A: open a previously verified upstream XAX store (xb64, ADR-210) read-only, build its entries, run them.

Needs an XAX source checkout at the pinned commit: set XAX_SOURCE_DIR (CI does).  Skipped otherwise.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from conftest import ALL_RIGHTS, needs_sandbox

SOURCE = os.environ.get("XAX_SOURCE_DIR")
STORES = Path(SOURCE, "compiler", "benchmarks", "r6_xb64") if SOURCE else None
pytestmark = pytest.mark.skipif(not (STORES and (STORES / "xb64-gen0.xax").is_file()), reason="set XAX_SOURCE_DIR to an XAX checkout")


@needs_sandbox
def test_xb64_release_and_xax_selftest_run_from_the_committed_store(service):
    from xax_mcp.policy import Policy
    from xax_mcp.service import Service, Session

    svc = Service(Policy(rights=ALL_RIGHTS, store_roots=(STORES.resolve(),)), service.sandbox)
    session = Session(svc.policy)
    for generation, width in (("xb64-gen0.xax", 76), ("xb64-gen1.xax", 64)):
        opened = svc.workspace(session, {"action": "open", "store": generation})
        assert set(opened["entries"]) == {"app", "test"}
        selftest = svc.build(session, {"workspace": opened["workspace"], "entry": "test"})
        assert svc.execute(session, {"artifact": selftest["artifact"]})["exit_status"] == 0
        app = svc.build(session, {"workspace": opened["workspace"], "entry": "app"})
        run = svc.execute(session, {"artifact": app["artifact"], "input": {"text": "foobar"}, "output": "text"})
        assert run["stdout"]["text"] == "Zm9vYmFy\n"
        long = svc.execute(session, {"artifact": app["artifact"], "input": {"text": "x" * 100}, "output": "text"})
        assert len(long["stdout"]["text"].splitlines()[0]) == width
