"""MCP STDIO server (official ``mcp`` Python SDK, low-level server API).

STDOUT purity: before anything else runs, the protocol channel is moved to a private duplicate of fd 1 and fd 1 is
pointed at stderr, so no stray print, library output or child process can corrupt the JSON-RPC stream.
"""

from __future__ import annotations

import io
import json
import logging
import os
import sys
import threading
import weakref
from typing import Any

from . import __version__

log = logging.getLogger("xax_mcp")


def _isolate_stdout():
    protocol_fd = os.dup(1)
    os.dup2(2, 1)
    sys.stdout = sys.stderr
    return io.TextIOWrapper(os.fdopen(protocol_fd, "wb", buffering=0), encoding="utf-8", newline="\n", write_through=True)


def _audit(event: str, **fields) -> None:
    """Structured, redacted audit record on stderr: handles, codes, sizes and digests only, never payloads."""
    log.info(json.dumps({"audit": event, **fields}, sort_keys=True, default=str))


class App:
    def __init__(self, service):
        import jsonschema

        from .schemas import TOOLS

        self.service = service
        self.tools = TOOLS
        self.validators = {name: jsonschema.Draft202012Validator(spec["inputSchema"]) for name, spec in TOOLS.items()}
        self._sessions: "weakref.WeakKeyDictionary[Any, Any]" = weakref.WeakKeyDictionary()
        self._fallback: dict[int, Any] = {}
        self._lock = threading.Lock()

    def session_for(self, key) -> Any:
        from .service import Session

        with self._lock:
            try:
                session = self._sessions.get(key)
                if session is None:
                    session = self._sessions[key] = Session(self.service.policy)
            except TypeError:  # unhashable / not weak-referenceable transport object
                session = self._fallback.setdefault(id(key), Session(self.service.policy))
            return session

    def call(self, session, name: str, arguments: dict | None, cancel: threading.Event | None = None) -> dict:
        """Validate and dispatch one tool call; always returns a structured payload (errors included)."""
        from .errors import ToolError

        arguments = arguments if arguments is not None else {}
        try:
            if name not in self.tools:
                raise ToolError("unsupported", f"unknown tool {name!r}")
            size = len(json.dumps(arguments, separators=(",", ":")))
            if size > self.service.policy.max_request_bytes:
                raise ToolError("resource_limit", f"arguments are {size} bytes; the limit is {self.service.policy.max_request_bytes}")
            errors = sorted(self.validators[name].iter_errors(arguments), key=lambda e: list(e.absolute_path))
            if errors:
                first = errors[0]
                where = "/".join(str(p) for p in first.absolute_path) or "(root)"
                raise ToolError("invalid_request", f"{where}: {first.message[:200]}", details={"errors": len(errors)})
            handler = {
                "xax_capabilities": lambda: self.service.capabilities(session),
                "xax_workspace": lambda: self.service.workspace(session, arguments),
                "xax_query": lambda: self.service.query(session, arguments),
                "xax_construct": lambda: self.service.construct(session, arguments),
                "xax_transaction": lambda: self.service.transaction(session, arguments),
                "xax_build": lambda: self.service.build(session, arguments),
                "xax_execute": lambda: self.service.execute(session, arguments, cancel),
                "xax_result": lambda: self.service.result(session, arguments),
            }[name]
            if name != "xax_capabilities":
                self.service.ready()
            result = handler()
            if "ok" not in result:
                result = {"ok": True, **result}
            _audit("tool", tool=name, ok=result.get("ok"), request_bytes=size)
            return result
        except ToolError as error:
            _audit("tool", tool=name, ok=False, code=error.code)
            return error.payload()
        except Exception as error:  # never crash the server; report, never hide
            log.exception("internal error in %s", name)
            _audit("tool", tool=name, ok=False, code="internal_error")
            return ToolError("internal_error", f"{type(error).__name__}").payload()


def transport_key(ctx) -> Any:
    """The object that identifies one client transport connection.

    Handle state is scoped to the transport connection (for STDIO: the one client that launched this process).
    mcp 2.3 builds a fresh ServerSession per request and, on the 2026-07-28 protocol, a fresh Connection per request
    too; the transport-scoped ``outbound`` channel is the stable identity on both protocol eras.  Verified for the
    pinned SDK range by tests/test_e2e_stdio.py.
    """
    connection = getattr(ctx.session, "_connection", None)
    return getattr(connection, "outbound", None) or connection or ctx.session


def build_server(app: App):
    import anyio
    import mcp_types as types
    from mcp.server.lowlevel import Server

    from .schemas import SCHEMA_VERSION

    async def list_tools(ctx, params):
        return types.ListToolsResult.model_validate({"tools": [
            {"name": name, "title": spec["title"], "description": spec["description"], "inputSchema": spec["inputSchema"],
             "annotations": spec["annotations"], "_meta": {"xax-mcp/schema": SCHEMA_VERSION}}
            for name, spec in app.tools.items()]})

    async def call_tool(ctx, params):
        session = app.session_for(transport_key(ctx))
        cancel = threading.Event()
        try:
            payload = await anyio.to_thread.run_sync(app.call, session, params.name, params.arguments, cancel,
                                                     abandon_on_cancel=True)
        except anyio.get_cancelled_exc_class():
            cancel.set()  # the sandbox loop kills the artifact process within ~50 ms
            raise
        text = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        return types.CallToolResult.model_validate({"content": [{"type": "text", "text": text}],
                                                    "structuredContent": payload, "isError": not payload.get("ok", False)})

    return Server("xax-mcp", version=__version__, title="XAX MCP server",
                  instructions="Use XAX for supported computation: xax_capabilities -> xax_construct (xax-construct-v1) -> "
                               "xax_build -> xax_execute. Report unsupported functionality instead of silently using another "
                               "language. Carrier JSON is transport, never XAX source.",
                  on_list_tools=list_tools, on_call_tool=call_tool)


def preload() -> None:
    """Import everything a server needs before its first message (used by the warm server before it forks)."""
    import anyio  # noqa: F401
    import jsonschema  # noqa: F401
    import mcp_types  # noqa: F401
    from mcp.server.lowlevel import Server  # noqa: F401
    from mcp.server.stdio import stdio_server  # noqa: F401

    from . import schemas  # noqa: F401


def _prepare() -> int:
    """``--prepare``: lower every missing XAX component image into XAX's image cache (``xax_native.prepare``, in
    parallel child processes), then start the per-user warm server and wait until it has loaded them."""
    import time

    from . import compat, warm

    compatibility = compat.check()
    if not compatibility.usable:
        log.error("incompatible XAX toolchain: %s", compatibility.reason)
        return 2
    from xax_native import prepare

    started = time.perf_counter()
    prepared = prepare(parallel=True)
    report = {"xax_components": {name: result["status"] for name, result in prepared.items()},
              "prepare_ms": round((time.perf_counter() - started) * 1000)}
    failed = sorted(name for name, result in prepared.items() if result["status"] == "failed")
    if failed:
        log.error("XAX could not prepare %s: %s", ", ".join(failed), "; ".join(prepared[name].get("reason", "") for name in failed))
    if not warm.enabled():
        print(json.dumps({**report, "warm_server": "disabled"}))
        return 1 if failed else 0
    try:
        report.update(warm.prepare())
    except (OSError, TimeoutError) as error:
        log.error("%s", error)
        return 1
    print(json.dumps(report))
    return 1 if failed else 0


def _via_warm_server(argv: list[str]) -> int | None:
    """Hand this launch to the per-user warm server when one is ready (see warm.py); None: serve in-process."""
    if any(flag in argv for flag in ("--check", "--version", "--prepare", "-h", "--help", "--no-warm-server")):
        return None
    from . import warm

    if not warm.enabled():
        return None
    return warm.launch(argv)


def main(argv: list[str] | None = None, warm=None) -> int:
    """Entry point.  ``warm`` is set only inside a child forked by the warm server (``warm.py``)."""
    if warm is None:
        launched = _via_warm_server(sys.argv[1:] if argv is None else list(argv))
        if launched is not None:
            return launched
    from .policy import from_args, parser

    args = parser().parse_args(argv)
    logging.basicConfig(level=os.environ.get("XAX_MCP_LOG", "INFO"), stream=sys.stderr,
                        format="xax-mcp %(levelname)s %(message)s")
    if args.version:
        from . import compat

        print(json.dumps({"xax-mcp": __version__, "pinned_xax_commit": compat.PINNED_XAX_COMMIT}))
        return 0
    if args.prepare:
        return _prepare()
    policy = from_args(args)
    from .service import Service

    if args.check:
        from . import compat
        from .sandbox import Sandbox

        probe = Sandbox().probe()
        report = {"xax-mcp": __version__, "xax": compat.check().as_dict(),
                  "sandbox": {"available": probe.available, "reason": probe.reason, **probe.details},
                  "rights": sorted(policy.rights)}
        print(json.dumps(report, indent=2))
        return 0 if report["xax"]["status"] == "tested" and probe.available else 1
    protocol_out = _isolate_stdout()
    try:
        service = Service(policy, warm=warm)
    except RuntimeError as error:
        log.error("%s", error)
        return 2
    if warm is None:
        preload()  # finish the server's own imports first, so initialize never waits behind the warm-up's imports
        threading.Thread(target=service.warm_up, name="xax-warmup", daemon=True).start()
    probe = service.sandbox.probe()
    log.info("starting: rights=%s sandbox=%s%s", sorted(policy.rights), probe.available,
             "" if probe.available else f" ({probe.reason})")
    import anyio
    from mcp.server.stdio import stdio_server

    server = build_server(App(service))

    async def run():
        async with stdio_server(stdout=anyio.wrap_file(protocol_out)) as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    anyio.run(run)
    return 0
