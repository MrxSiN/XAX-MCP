"""XAX MCP service core: session-scoped handles over the upstream XAX construction, workspace, build and target
interfaces, plus sandboxed execution.  Independent of the MCP transport (``server.py`` adapts it).

Nothing here implements, evaluates or simulates a workload.  Programs are constructed and verified by
``xax_construct.construct``; queried and changed by ``xax_workspace.Workspace`` (through
``xax_local_protocol.LocalMutationSession``); built by ``xax_build.build``; and run as the built artifact bytes
under ``sandbox.Sandbox``.
"""

from __future__ import annotations

import base64
import dataclasses
import enum
import hashlib
import secrets
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any

from . import __version__, compat
from .errors import ToolError
from .io_codec import decode_output, encode_input
from .policy import Policy, resolve_store
from .sandbox import Limits, Sandbox, SandboxUnavailable

SUPPORTED_EFFECTS = ("stdio",)
KNOWN_EFFECTS = ("stdio", "filesystem.read", "filesystem.write", "network", "process", "environment", "clock")
_MUTATION_TOKEN = r"[A-Za-z@][A-Za-z0-9.@_-]{0,63}"
_BUILD_SLOTS = threading.BoundedSemaphore(2)
# Warm-up carrier: a process entry that only exits.  Not a workload; its result is discarded.
_WARMUP_PROGRAM = {
    "format": "xax-construct-v1", "platform": "linux-x86_64", "types": {"proc": "linux.process_effect"},
    "functions": [{"name": "main", "params": ["proc"], "returns": ["b32", "proc"], "blocks": [{"params": ["proc"], "nodes": [
        ["call.foreign", [["b32", 0], "p0"], ["proc"], {"entity": "linux.exit_group"}]], "end": ["ret", [["b32", 0], "n0"]]}]}],
    "package": {"name": "warmup", "entries": {"app": "main"}, "release": "app"}}


def to_json(value: Any) -> Any:
    """Transport projection of upstream views: bytes -> hex, enums -> lowercase names, tuples -> lists."""
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, enum.Enum):
        # Operations use the carrier spelling (add.wrap, checked.load.bits.le); other enums their lowercase name.
        return value.name.lower().replace("_", ".") if type(value).__name__ == "Operation" else value.name.lower()
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {f.name: to_json(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, dict):
        return {str(to_json(k)): to_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [to_json(item) for item in value]
    return value


def _diagnostic(error) -> dict:
    return to_json(error.diagnostic)


def _classify(code: str, default: str) -> str:
    if code in ("XAX.WORKSPACE.STALE_ROOT", "XAX.WORKSPACE.STALE_QUERY"):
        return "stale_root"
    if code.endswith("CONFLICT") or code == "XAX.WORKSPACE.DUPLICATE_MUTATION":
        return "conflict"
    if code == "XAX.WORKSPACE.RESPONSE_BUDGET":
        return "resource_limit"
    if code in ("XAX.WORKSPACE.HANDLE", "XAX.WORKSPACE.ENTITY", "XAX.WORKSPACE.CANDIDATE_HANDLE"):
        return "not_found"
    if code == "XAX.WORKSPACE.UNSUPPORTED_MUTATION":
        return "unsupported"
    return default


def _xax_error(error, default: str, message: str) -> ToolError:
    code = error.diagnostic.code
    diagnostic = _diagnostic(error)
    return ToolError(_classify(code, default), f"{message}: {code}", diagnostic=diagnostic,
                     repair=list(diagnostic.get("repair_neighborhood") or []))


def _handle(kind: str) -> str:
    return f"{kind}_{secrets.token_hex(12)}"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class WorkspaceEntry:
    handle: str
    workspace: Any
    target: Any
    origin: str
    construct_names: dict[str, str] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)


@dataclass
class ArtifactEntry:
    handle: str
    workspace: str
    generation: int
    root: str
    entry: str
    data: bytes
    blake3: str
    sha256: str
    executable: bool
    provenance: dict


@dataclass
class ResultEntry:
    handle: str
    kind: str
    data: bytes


class _Bounded(OrderedDict):
    """Per-session handle table with a hard size bound; the oldest entry is evicted first."""

    def __init__(self, limit: int):
        super().__init__()
        self.limit = limit

    def add(self, key: str, value) -> None:
        self[key] = value
        while len(self) > self.limit:
            self.popitem(last=False)


class Session:
    """All state of one MCP client connection.  Handles are random, unguessable, and never shared."""

    def __init__(self, policy: Policy):
        self.workspaces: _Bounded = _Bounded(policy.max_workspaces)
        self.artifacts: _Bounded = _Bounded(policy.max_artifacts)
        self.results: _Bounded = _Bounded(policy.max_results)
        self.build_cache: dict[tuple[str, str, str], ArtifactEntry] = {}
        self.lock = threading.Lock()

    def get(self, table: str, handle: Any, kind: str):
        if not isinstance(handle, str):
            raise ToolError("invalid_request", f"{kind} handle must be a string")
        with self.lock:
            value = getattr(self, table).get(handle)
        if value is None:
            raise ToolError("not_found", f"unknown {kind} handle in this session", repair=[f"open or create a {kind} first"])
        return value


class Service:
    def __init__(self, policy: Policy, sandbox: Sandbox | None = None):
        self.policy = policy
        self.sandbox = sandbox or Sandbox()
        self.compatibility = compat.check()
        if self.compatibility.status == "incompatible" or (
                self.compatibility.status == "untested" and not compat.allow_untested()):
            raise RuntimeError(f"incompatible XAX toolchain: {self.compatibility.reason}")
        self._ready = threading.Event()
        self.warmup_ms: float | None = None

    def warm_up(self) -> None:
        """Load the XAX-hosted compiler components once (about 20 s cold on the reference host) by constructing the
        smallest valid process (it only calls exit_group).  Tool calls that reach XAX wait for this to finish, so the
        native component loaders never race."""
        started = time.perf_counter()
        try:
            from xax_construct import construct

            construct(_WARMUP_PROGRAM)
        finally:
            self.warmup_ms = (time.perf_counter() - started) * 1000
            self._ready.set()

    def ready(self) -> None:
        if not self._ready.is_set():
            self._ready.wait()

    # -- capabilities -----------------------------------------------------------------------------------------
    def capabilities(self, session: Session) -> dict:
        self.policy.require("read")
        import importlib.metadata

        from xax_artifact import BOOTSTRAP_COMPILER_IDENTITY_V1
        from xax_compiler import Operation, decode_native_target, x86_64_linux_exec_target
        from xax_contract import describe
        from xax_linux import process_contract
        from xax_local_protocol import edit_grammar_id

        target = decode_native_target(x86_64_linux_exec_target())
        probe = self.sandbox.probe()
        execute = "execute" in self.policy.rights and probe.available
        try:
            sdk = importlib.metadata.version("mcp")
        except importlib.metadata.PackageNotFoundError:
            sdk = None
        return {
            "server": {"name": "xax-mcp", "version": __version__, "mcp_sdk": sdk, "transport": "stdio",
                       "adapter_language": "Python (bootstrap adapter; holds no workload logic)",
                       "xax_components_loaded": self._ready.is_set(),
                       "warmup_ms": None if self.warmup_ms is None else round(self.warmup_ms)},
            "xax": {**self.compatibility.as_dict(), "compiler_identity": BOOTSTRAP_COMPILER_IDENTITY_V1.hex(),
                    "host_contract": {key: describe()[key] for key in ("contract", "minor", "formats")},
                    "compiler_implementation": "XAX bootstrap compiler (Python, with XAX-hosted components where native)"},
            "authority": self.policy.as_dict(),
            "targets": [{
                "id": "linux-x86_64", "profile": target.identity.decode(), "artifact": "static ELF64 ET_EXEC (no libc, loader or runtime)",
                "construct": "xax-construct-v1", "build": True,
                "execute": {"available": execute, "granted": "execute" in self.policy.rights,
                            "sandbox": {"mechanism": self.sandbox.mechanism, "available": probe.available,
                                        "reason": probe.reason, **probe.details}},
                "operations": sorted(Operation(o).name.lower().replace("_", ".") for o in target.supported_operations),
                "carrier_types": ["b<N>", "{view: EXTENT}", "{ptr: [ELEMENT, r|rw, ALIGN, SPACE]}",
                                  *sorted(f"linux.{n}" for n in ("b8", "b32", "b64", "bytes_rw", "bytes_read", "memory_effect",
                                                                 "filesystem_effect", "process_effect", "heap_owner"))],
                "carrier_entities": sorted(f"linux.{n}" for n in ("read", "write", "openat", "close", "mmap_anonymous", "exit_group"))
                + sorted(f"linux.startup.{n}" for n in ("argc", "arg_length", "arg_copy", "envc", "env_length", "env_copy", "auxv_value"))
                + ["{linux.munmap_view: [TYPE, EXTENT]}", "{fn: NAME}"],
                "process_entry": "fn(proof...) -> (bits<N>?, proof...); ends with linux.exit_group; no machine parameters; "
                                 "linux.startup.* only in the entry function",
                "process_contract": process_contract(),
            }],
            "io": {"format": "xax-mcp-io-v1", "input": ["ints (b8|b16|b32|b64, little-endian on stdin)", "bytes_base64", "text",
                                                        "argv (strings, read with linux.startup.*)"],
                   "output": ["ints (declared layout decoded from stdout)", "bytes", "text"], "exit_status": True,
                   "argv": True, "environment": False, "files": False},
            "effects": {"supported": list(SUPPORTED_EFFECTS), "denied_by_default": [e for e in KNOWN_EFFECTS if e not in SUPPORTED_EFFECTS]},
            "edits": {"transport": "typed mutations rendered to the upstream local edit grammar", "grammar_id": edit_grammar_id(),
                      "ops": ["set_constant", "set_operation", "replace_operand", "delete", "prune_dead", "move",
                              "insert_constant", "set_edge", "set_type", "set_signature"],
                      "modes": ["verify", "commit", "rollback"]},
            "maturity": {
                "construct_build_execute linux-x86_64": "EXECUTED (tests/test_e2e_stdio.py)",
                "workspace query/transaction": "EXECUTED (delegates to xax_workspace)",
                "sandbox": "EXECUTED on Linux x86-64 with unprivileged user namespaces; fails closed elsewhere",
                "other XAX targets (jvm, android, wasm, aarch64, riscv64, windows)": "UNIMPLEMENTED in this adapter",
                "json/csv/strings/collections libraries": "UNIMPLEMENTED (no XAX library exposed through the carrier)",
                "filesystem/network/process effects": "UNIMPLEMENTED (denied)",
                "streamable HTTP transport": "UNIMPLEMENTED",
            },
        }

    # -- workspaces -------------------------------------------------------------------------------------------
    def _functions(self, entry: WorkspaceEntry) -> list[dict]:
        from xax_build import decode_package, decode_request, decode_snapshot
        from xax_compiler import Kind

        workspace = entry.workspace
        reader = workspace.reader
        resolve = reader.get
        snapshot = decode_snapshot(resolve(reader.root_cid), resolve)
        package = decode_package(resolve(decode_request(resolve(snapshot.request_root), resolve).package_root), resolve)
        entries = {}
        for name, cid in package.build_entries:
            entries.setdefault(cid, []).append(name.decode())
        out = []
        for obj in sorted((o for o in reader.objects() if o.kind == Kind.FUNCTION), key=lambda o: o.cid):
            page = workspace.function_nodes(obj.cid, 1)
            handle = page.entities[0].handle.split(".B", 1)[0] if page.entities else None
            item = {"handle": handle, "cid": obj.cid.hex()}
            if obj.cid in entries:
                item["entries"] = sorted(entries[obj.cid])
            out.append(item)
        return out

    def _workspace_summary(self, entry: WorkspaceEntry) -> dict:
        from xax_build import decode_package, decode_request, decode_snapshot

        workspace = entry.workspace
        reader = workspace.reader
        resolve = reader.get
        snapshot = decode_snapshot(resolve(reader.root_cid), resolve)
        request = decode_request(resolve(snapshot.request_root), resolve)
        package = decode_package(resolve(request.package_root), resolve)
        canonical = reader.canonical_bytes()
        return {"workspace": entry.handle, "root": reader.root_cid.hex(), "generation": workspace.generation,
                "origin": entry.origin, "target": entry.target.cid.hex(),
                "entries": sorted(name.decode() for name, _cid in package.build_entries),
                "release_entry": request.build_entry.decode(),
                "store": {"bytes": len(canonical), "sha256": _sha256(canonical)}}

    def _open(self, session: Session, reader, target, origin: str, names: dict | None = None) -> WorkspaceEntry:
        from xax_workspace import Workspace

        entry = WorkspaceEntry(_handle("ws"), Workspace(reader, target), target, origin, names or {})
        with session.lock:
            session.workspaces.add(entry.handle, entry)
        return entry

    def workspace(self, session: Session, args: dict) -> dict:
        action = args["action"]
        if action == "list":
            self.policy.require("read")
            with session.lock:
                entries = list(session.workspaces.values())
            return {"ok": True, "workspaces": [{"workspace": e.handle, "origin": e.origin, "generation": e.workspace.generation,
                                                "root": e.workspace.root.hex()} for e in entries]}
        if action == "close":
            self.policy.require("read")
            entry = session.get("workspaces", args.get("workspace"), "workspace")
            with session.lock:
                session.workspaces.pop(entry.handle, None)
                for handle in [h for h, a in session.artifacts.items() if a.workspace == entry.handle]:
                    session.artifacts[handle].workspace = ""
            return {"ok": True, "closed": entry.handle}
        if action == "describe":
            self.policy.require("read")
            entry = session.get("workspaces", args.get("workspace"), "workspace")
            return {"ok": True, **self._workspace_summary(entry), "functions": self._functions(entry)}
        if action == "open":
            self.policy.require("read")
            store = args.get("store")
            if not isinstance(store, str):
                raise ToolError("invalid_request", "open needs 'store': a relative .xax name in a granted store root")
            path = resolve_store(self.policy, store)
            from xax_build import decode_request, decode_snapshot
            from xax_compiler import StoreReader, XaxError

            try:
                reader = StoreReader(path.read_bytes())
                resolve = reader.get
                snapshot = decode_snapshot(resolve(reader.root_cid), resolve)
                target = resolve(decode_request(resolve(snapshot.request_root), resolve).target_root)
                entry = self._open(session, reader, target, f"store:{store}")
            except XaxError as error:
                raise _xax_error(error, "verification_failed", "store failed XAX verification") from None
            except (ValueError, KeyError, IndexError) as error:
                raise ToolError("verification_failed", f"store is not a verified XAX build snapshot: {type(error).__name__}") from None
            return {"ok": True, **self._workspace_summary(entry), "functions": self._functions(entry)}
        raise ToolError("invalid_request", f"unknown workspace action {action!r}")

    # -- construction -----------------------------------------------------------------------------------------
    def construct(self, session: Session, args: dict) -> dict:
        self.policy.require("mutate")
        request = args["request"]
        _check_carrier_bounds(request)
        from xax_compiler import XaxError
        from xax_construct import construct

        started = time.perf_counter()
        try:
            constructed = construct(request)
        except XaxError as error:
            raise _xax_error(error, "verification_failed", "XAX verification rejected the constructed program") from None
        except ValueError as error:
            raise ToolError("invalid_request", str(error)[:500]) from None
        except (KeyError, TypeError, IndexError, AttributeError, RecursionError) as error:
            raise ToolError("invalid_request", f"malformed xax-construct-v1 request ({type(error).__name__})") from None
        entry = self._open(session, constructed.reader, constructed.target, "construct")
        names = {}
        for name, function in constructed.functions.items():
            page = entry.workspace.function_nodes(function.cid, 1)
            names[name] = page.entities[0].handle.split(".B", 1)[0] if page.entities else function.cid.hex()
        entry.construct_names = names
        return {"ok": True, "verified": True, **self._workspace_summary(entry), "function_handles": names,
                "construct_ms": round((time.perf_counter() - started) * 1000, 1),
                "note": "the request was transport; the verified store is now authoritative and changes only by transactions"}

    # -- queries ----------------------------------------------------------------------------------------------
    def query(self, session: Session, args: dict) -> dict:
        self.policy.require("read")
        entry = session.get("workspaces", args["workspace"], "workspace")
        workspace = entry.workspace
        kind = args["kind"]
        handle = args.get("handle")
        limit = args.get("limit", 32)
        continuation = args.get("continuation", 0)
        budget = self.policy.query_byte_budget
        from xax_compiler import XaxError

        def function_cid(text):
            for item in self._functions(entry):
                if item["handle"] == text:
                    return bytes.fromhex(item["cid"])
            raise ToolError("not_found", f"no function {text!r} at the current root", repair=["query kind 'functions'"])

        def need_handle():
            if not isinstance(handle, str):
                raise ToolError("invalid_request", f"query kind {kind!r} needs 'handle'")
            return handle

        try:
            if kind == "root":
                result = workspace.root_query(byte_budget=budget)
            elif kind == "functions":
                items = self._functions(entry)
                page = items[continuation:continuation + limit]
                end = continuation + len(page)
                result = {"entities": page, "truncated": end < len(items), "continuation": end if end < len(items) else None}
            elif kind == "function_nodes":
                result = workspace.function_nodes(function_cid(need_handle()), limit, continuation, byte_budget=budget)
            elif kind == "function_view":
                from xax_local_protocol import LocalMutationSession

                cid = function_cid(need_handle())
                try:
                    local = LocalMutationSession.for_function(workspace, cid, 256)
                    text = local.view(functions=(cid,))
                except (KeyError, ValueError) as error:
                    raise ToolError("unsupported", f"upstream function view unavailable for this function ({type(error).__name__})",
                                    repair=["use function_nodes / operands / neighborhood"]) from None
                if len(text.encode()) > budget:
                    raise ToolError("resource_limit", "function view exceeds the response budget",
                                    repair=["use function_nodes / operands / neighborhood with pagination"])
                result = {"classification": "tooling view (diagnostic notation, not XAX source)", "view": text,
                          "aliases": local.aliases}
            elif kind == "callers":
                result = workspace.callers(function_cid(need_handle()), limit, continuation, byte_budget=budget)
            elif kind == "callees":
                result = workspace.callees(function_cid(need_handle()), limit, continuation, byte_budget=budget)
            elif kind == "effect_summary":
                result = workspace.effect_summary(need_handle(), byte_budget=budget)
            elif kind == "operands":
                result = workspace.operands(need_handle(), limit, continuation, byte_budget=budget)
            elif kind == "neighborhood":
                result = workspace.neighborhood(need_handle(), limit, continuation, byte_budget=budget)
            elif kind in ("uses", "users_of_value"):
                result = workspace.expand(need_handle(), "uses", limit, continuation, byte_budget=budget)
            elif kind == "type":
                result = workspace.type(need_handle(), byte_budget=budget)
            elif kind == "effects":
                result = workspace.effects(need_handle(), byte_budget=budget)
            elif kind == "entity":
                result = workspace.entity(need_handle(), byte_budget=budget)
            elif kind == "proof":
                result = workspace.proof(need_handle(), byte_budget=budget)
            elif kind == "diff":
                result = workspace.diff(int(args.get("from_generation", 0)), limit, continuation, byte_budget=budget)
            elif kind == "repair":
                diagnostic = session.get("results", need_handle(), "diagnostic")
                if diagnostic.kind != "diagnostic":
                    raise ToolError("invalid_request", "handle is not a diagnostic")
                result = workspace.repair_neighborhood(diagnostic.data, limit, continuation, byte_budget=budget)
            else:
                raise ToolError("unsupported", f"query kind {kind!r} is not supported")
        except XaxError as error:
            raise _xax_error(error, "invalid_request", "query rejected") from None
        except ValueError as error:
            raise ToolError("invalid_request", str(error)[:300]) from None
        return {"ok": True, "generation": workspace.generation, "result": to_json(result)}

    # -- transactions -----------------------------------------------------------------------------------------
    def transaction(self, session: Session, args: dict) -> dict:
        self.policy.require("mutate")
        entry = session.get("workspaces", args["workspace"], "workspace")
        workspace = entry.workspace
        mode = args["mode"]
        from xax_compiler import XaxError
        from xax_local_protocol import LocalMutationSession

        with entry.lock:
            if mode == "rollback":
                candidate = args.get("candidate")
                if not isinstance(candidate, str):
                    raise ToolError("invalid_request", "rollback needs 'candidate'")
                rolled = workspace.rollback(candidate)
                if not rolled.rolled_back:
                    raise ToolError("not_found", "no live candidate with that handle", diagnostic=to_json(rolled.diagnostic))
                return {"ok": True, "rolled_back": True, "root": rolled.root.hex(), "generation": workspace.generation}
            expected_generation, expected_root = args["expected_generation"], args["expected_root"]
            if workspace.generation != expected_generation or workspace.root.hex() != expected_root:
                raise ToolError("stale_root", "the workspace has moved past the expected root",
                                details={"current_generation": workspace.generation, "current_root": workspace.root.hex()},
                                repair=["re-query the affected functions at the current generation and rebuild the edit"])
            command = render_mutations(args["mutations"])
            try:
                local = LocalMutationSession(workspace, expected_generation=expected_generation)
                transaction = local.transaction(command)
                if args.get("read_set"):
                    transaction = dataclasses.replace(transaction, read_set=tuple(args["read_set"]))
            except XaxError as error:
                raise _xax_error(error, "invalid_request", "edit rejected") from None
            except ValueError as error:
                stale = "stale" in str(error)
                raise ToolError("stale_root" if stale else "invalid_request", str(error)[:300],
                                repair=["query the function with function_nodes so its handles are exposed at this generation"]) from None
            try:
                outcome = workspace.verify(transaction) if mode == "verify" else workspace.commit(transaction)
            except XaxError as error:
                raise _xax_error(error, "verification_failed", "transaction rejected") from None
            ok = outcome.verified if mode == "verify" else outcome.committed
            if not ok:
                diagnostic_handle = _handle("diag")
                with session.lock:
                    session.results.add(diagnostic_handle, ResultEntry(diagnostic_handle, "diagnostic", outcome.diagnostic))
                code = _classify(outcome.diagnostic.code, "verification_failed")
                raise ToolError(code, f"transaction rejected: {outcome.diagnostic.code}",
                                diagnostic={**local.diagnostic_view(outcome.diagnostic), "handle": diagnostic_handle},
                                repair=["query kind 'repair' with the diagnostic handle for the bounded repair neighborhood"],
                                details={"generation": workspace.generation, "root": workspace.root.hex()})
            result = {"ok": True, "mode": mode, "root": outcome.root.hex(), "generation": workspace.generation,
                      "transaction_bytes": outcome.transaction_bytes, "touched_objects": outcome.touched_objects,
                      "reused_objects": outcome.reused_objects, "verified_objects": outcome.verified_objects}
            if mode == "verify":
                result["candidate"] = outcome.candidate_handle
                result["note"] = "candidate verified privately; the canonical root is unchanged until commit"
            else:
                result["committed"] = True
                result["changed_entities"] = [cid.hex() for cid in outcome.changed_entities]
            return result

    # -- builds -----------------------------------------------------------------------------------------------
    def build(self, session: Session, args: dict) -> dict:
        self.policy.require("build")
        entry = session.get("workspaces", args["workspace"], "workspace")
        from xax_artifact import BOOTSTRAP_COMPILER_IDENTITY_V1
        from xax_build import (ArtifactKind, build, build_request, decode_package, decode_provenance, decode_request,
                               decode_snapshot, resolve_packages, snapshot_store)
        from xax_compiler import X86_64_LINUX_ABI, X86_64_LINUX_ELF_EXEC_FORMAT, XaxError, decode_native_target

        with entry.lock:
            workspace = entry.workspace
            generation, reader = workspace.generation, workspace.reader
        if "expected_generation" in args and args["expected_generation"] != generation:
            raise ToolError("stale_root", "the workspace has moved past the expected generation",
                            details={"current_generation": generation, "current_root": reader.root_cid.hex()})
        resolve = reader.get
        snapshot = decode_snapshot(resolve(reader.root_cid), resolve)
        release = resolve(snapshot.request_root)
        view = decode_request(release, resolve)
        package = decode_package(resolve(view.package_root), resolve)
        entry_name = args.get("entry") or view.build_entry.decode()
        if entry_name.encode() not in dict(package.build_entries):
            raise ToolError("invalid_request", f"package has no entry {entry_name!r}",
                            details={"entries": sorted(n.decode() for n, _ in package.build_entries)})
        key = (reader.root_cid.hex(), entry_name, self.compatibility.fingerprint or "")
        with session.lock:
            cached = session.build_cache.get(key)
        if cached is not None and cached.blake3 == _blake3(cached.data):
            return {"ok": True, **self._artifact_view(cached), "cache": "hit", "build_ms": 0.0}
        started = time.perf_counter()
        with _BUILD_SLOTS:
            try:
                if entry_name.encode() == view.build_entry:
                    build_reader, request = reader, release
                else:
                    request = build_request(resolve(view.package_root), entry_name.encode(), resolve(view.target_root),
                                            resolve(view.profile_root), requested_artifacts=(ArtifactKind.NATIVE_IMAGE,))
                    objects = (*reader.objects(), request)
                    build_reader = snapshot_store(resolve_packages(request, objects, resolve(snapshot.trust_policy_root),
                                                                   snapshot.resolver_identity), objects)
                result = build(build_reader, request.cid, producer_identity=b"xax-mcp")
            except XaxError as error:
                raise _xax_error(error, "build_error", "XAX build rejected the request") from None
            except ValueError as error:
                raise ToolError("build_error", str(error)[:300]) from None
        build_ms = (time.perf_counter() - started) * 1000
        target_object = resolve(view.target_root)
        description = decode_native_target(target_object)
        executable = description.abi == X86_64_LINUX_ABI and description.image_format == X86_64_LINUX_ELF_EXEC_FORMAT
        prov_resolve = {o.cid: o for o in (*build_reader.objects(), result.provenance)}.__getitem__
        provenance = to_json(decode_provenance(result.provenance, prov_resolve))
        artifact = ArtifactEntry(
            _handle("art"), entry.handle, generation, reader.root_cid.hex(), entry_name, result.artifact,
            result.artifact_digest.hex(), _sha256(result.artifact), executable,
            {"build_key": result.key.hex(), "provenance_cid": result.provenance.cid.hex(), "provenance": provenance,
             "target_profile": description.identity.decode(errors="replace"), "compiler_identity": BOOTSTRAP_COMPILER_IDENTITY_V1.hex(),
             "xax_toolchain_fingerprint": self.compatibility.fingerprint, "xax_commit": self.compatibility.commit,
             "xax_native_components": _native_authority(), "build_request": request.cid.hex(),
             "snapshot_root": build_reader.root_cid.hex(), "workspace_root": reader.root_cid.hex(), "generation": generation})
        with session.lock:
            session.artifacts.add(artifact.handle, artifact)
            session.build_cache[key] = artifact
        return {"ok": True, **self._artifact_view(artifact), "cache": "miss", "build_ms": round(build_ms, 1)}

    @staticmethod
    def _artifact_view(artifact: ArtifactEntry) -> dict:
        return {"artifact": artifact.handle, "entry": artifact.entry, "bytes": len(artifact.data),
                "artifact_digest_blake3": artifact.blake3, "artifact_sha256": artifact.sha256,
                "executable_here": artifact.executable, "provenance": artifact.provenance}

    # -- execution --------------------------------------------------------------------------------------------
    def execute(self, session: Session, args: dict, cancel: threading.Event | None = None) -> dict:
        self.policy.require("execute")
        artifact: ArtifactEntry = session.get("artifacts", args["artifact"], "artifact")
        effects = args.get("effects", ["stdio"])
        denied = [e for e in effects if e not in SUPPORTED_EFFECTS]
        if denied:
            raise ToolError("denied_capability", f"effects not granted: {', '.join(denied)}",
                            repair=["only 'stdio' (stdin/stdout/stderr, exit status) is available to executed artifacts"])
        if not artifact.executable:
            raise ToolError("unsupported", "this artifact's target is not executable by this server")
        if args.get("require_current", True):
            with session.lock:
                entry = session.workspaces.get(artifact.workspace)
            if entry is None or entry.workspace.root.hex() != artifact.root:
                raise ToolError("stale_artifact", "the artifact was built from a root that is no longer the workspace's current root",
                                repair=["rebuild with xax_build, or pass require_current=false to run this immutable older build"],
                                details={"artifact_root": artifact.root})
        if _blake3(artifact.data) != artifact.blake3:
            raise ToolError("stale_artifact", "artifact bytes no longer match their recorded digest; refusing to run")
        requested = args.get("limits", {})
        base = self.policy.limits
        limits = Limits(wall_ms=min(requested.get("wall_ms", base.wall_ms), base.wall_ms),
                        cpu_seconds=min(requested.get("cpu_seconds", base.cpu_seconds), base.cpu_seconds),
                        memory_bytes=min(requested.get("memory_mb", base.memory_bytes >> 20) << 20, base.memory_bytes),
                        max_stdout_bytes=min(requested.get("max_output_bytes", base.max_stdout_bytes), base.max_stdout_bytes),
                        max_stderr_bytes=base.max_stderr_bytes, max_stdin_bytes=base.max_stdin_bytes)
        stdin = encode_input(args.get("input"), limits.max_stdin_bytes)
        arguments = tuple(args.get("argv", ()))
        if any("\0" in item for item in arguments) or sum(len(item.encode()) + 1 for item in arguments) > 65536:
            raise ToolError("invalid_request", "argv strings must not contain NUL and must total at most 64 KiB")
        output_spec = args.get("output", "bytes")
        try:
            outcome = self.sandbox.run(artifact.data, stdin, limits, cancel, arguments)
        except SandboxUnavailable as error:
            raise ToolError("sandbox_unavailable", str(error),
                            repair=["run on Linux x86-64 with unprivileged user namespaces and seccomp enabled"]) from None
        if outcome.setup_error:
            raise ToolError("sandbox_unavailable", f"sandbox setup failed; artifact not run: {outcome.setup_error}")
        evidence = {"label": "EXECUTED", "sandbox": self.sandbox.mechanism, "limits": limits.as_dict(), "effects": ["stdio"],
                    "artifact_digest_verified": True, "artifact_digest_blake3": artifact.blake3,
                    "build_key": artifact.provenance["build_key"], "workspace_root": artifact.root, "wall_ms": round(outcome.wall_ms, 2)}
        if outcome.cancelled:
            raise ToolError("runtime_failure", "execution cancelled; the process was killed", details={"evidence": evidence})
        if outcome.timed_out:
            raise ToolError("resource_limit", f"wall-time limit of {limits.wall_ms} ms exceeded; the process was killed",
                            details={"evidence": evidence})
        if outcome.output_limit_exceeded:
            raise ToolError("resource_limit", f"stdout exceeded {limits.max_stdout_bytes} bytes; the process was killed",
                            details={"evidence": evidence})
        if outcome.signal == "SIGXCPU":  # soft CPU limit; the program cannot ignore it (rt_sigaction is not allowed)
            raise ToolError("resource_limit", f"CPU limit of {limits.cpu_seconds} s exceeded", details={"evidence": evidence})
        result = {"ok": outcome.exit_status == 0, "exit_status": outcome.exit_status, "signal": outcome.signal,
                  "stdout": decode_output(output_spec, outcome.stdout, self.policy.inline_output_bytes),
                  "evidence": evidence}
        if outcome.signal is not None:
            result["status"] = "trap" if outcome.signal in ("SIGILL", "SIGTRAP") else "crashed"
        else:
            result["status"] = "exited"
        if outcome.stderr:
            result["stderr"] = {"length": len(outcome.stderr), "text": outcome.stderr[:512].decode("utf-8", errors="replace"),
                                "truncated": outcome.stderr_truncated or len(outcome.stderr) > 512}
        if len(outcome.stdout) > self.policy.inline_output_bytes:
            handle = _handle("res")
            with session.lock:
                session.results.add(handle, ResultEntry(handle, "stdout", outcome.stdout))
            result["stdout_result"] = handle
        if outcome.signal is not None:
            result["error"] = {"code": "runtime_failure", "message": f"artifact terminated by {outcome.signal}"}
        return result

    # -- bounded result retrieval -----------------------------------------------------------------------------
    def result(self, session: Session, args: dict) -> dict:
        self.policy.require("read")
        handle = args["handle"]
        offset, length = args.get("offset", 0), args.get("length", 4096)
        if isinstance(handle, str) and handle.startswith("ws_"):
            entry = session.get("workspaces", handle, "workspace")
            data, kind = entry.workspace.reader.canonical_bytes(), "canonical_store"
        else:
            item = session.get("results", handle, "result")
            if item.kind == "diagnostic":
                return {"ok": True, "kind": "diagnostic", "diagnostic": to_json(item.data)}
            data, kind = item.data, item.kind
        chunk = data[offset:offset + length]
        end = offset + len(chunk)
        return {"ok": True, "kind": kind, "total_bytes": len(data), "offset": offset, "base64": base64.b64encode(chunk).decode(),
                "continuation": end if end < len(data) else None}


def _blake3(data: bytes) -> str:
    from blake3 import blake3

    return blake3(data).digest().hex()


def _native_authority() -> dict:
    try:
        from xax_native import AUTHORITY
    except ImportError:
        return {}
    return {name: entry.get("actual_authority") for name, entry in sorted(AUTHORITY.items())}


def _check_carrier_bounds(request: Any) -> None:
    """Bound the carrier before the compiler sees it: nesting, node counts, and integer magnitude."""
    if not isinstance(request, dict) or request.get("format") != "xax-construct-v1":
        raise ToolError("invalid_request", "request must be an xax-construct-v1 object",
                        repair=["set format to 'xax-construct-v1' and platform to 'linux-x86_64'"])
    if request.get("platform") != "linux-x86_64":
        raise ToolError("unsupported", "xax-construct-v1 supports only platform 'linux-x86_64' in the pinned XAX")
    totals = {"nodes": 0}

    def walk(value, depth):
        if depth > 12:
            raise ToolError("invalid_request", "request nesting exceeds 12 levels")
        if isinstance(value, bool):
            return
        if isinstance(value, int):
            if not -(1 << 64) < value < (1 << 64):
                raise ToolError("invalid_request", "integer literal outside the 64-bit carrier range")
        elif isinstance(value, float):
            raise ToolError("invalid_request", "floating-point numbers are not carrier values")
        elif isinstance(value, list):
            for item in value:
                walk(item, depth + 1)
        elif isinstance(value, dict):
            for item in value.values():
                walk(item, depth + 1)

    walk(request, 0)
    functions = request.get("functions", [])
    if not isinstance(functions, list) or len(functions) > 256:
        raise ToolError("invalid_request", "at most 256 functions")
    for function in functions:
        blocks = function.get("blocks", []) if isinstance(function, dict) else []
        if not isinstance(blocks, list) or len(blocks) > 4096:
            raise ToolError("invalid_request", "at most 4096 blocks per function")
        for block in blocks:
            nodes = block.get("nodes", []) if isinstance(block, dict) else []
            totals["nodes"] += len(nodes) if isinstance(nodes, list) else 0
    if totals["nodes"] > 100_000:
        raise ToolError("resource_limit", "at most 100000 nodes per construction request")
    for alias, spec in (request.get("types") or {}).items():
        if isinstance(spec, dict) and isinstance(spec.get("view"), int) and spec["view"] > (1 << 30):
            raise ToolError("resource_limit", f"view extent of {alias!r} exceeds 1 GiB")


def render_mutations(mutations: list[dict]) -> str:
    """Render typed mutations to the upstream local edit grammar (ADR-200).  Every token is validated first, so
    no argument can inject a separator or extra edit; the upstream session then binds and checks each handle."""
    import re

    token = re.compile(_MUTATION_TOKEN)
    types = re.compile(r"-|" + _MUTATION_TOKEN + r"(?:," + _MUTATION_TOKEN + r")*")
    operations = {"add.wrap", "sub.wrap", "mul.wrap"}

    def h(value, name):
        if not isinstance(value, str) or not token.fullmatch(value):
            raise ToolError("invalid_request", f"{name} must be a workspace handle")
        return value

    def n(value, name, low=-(1 << 64) + 1, high=(1 << 64) - 1):
        if not isinstance(value, int) or isinstance(value, bool) or not low <= value <= high:
            raise ToolError("invalid_request", f"{name} must be an integer in range")
        return str(value)

    def t(value, name):
        if isinstance(value, list):
            value = ",".join(value) if value else "-"
        if not isinstance(value, str) or not types.fullmatch(value):
            raise ToolError("invalid_request", f"{name} must be a type handle list")
        return value

    records = []
    for m in mutations:
        op = m.get("op")
        if op == "set_constant":
            parts = ["const", h(m.get("node"), "node"), n(m.get("value"), "value")]
        elif op == "set_operation":
            if m.get("value") not in operations:
                raise ToolError("unsupported", "set_operation supports add.wrap, sub.wrap, mul.wrap in the pinned XAX")
            parts = ["op", h(m.get("node"), "node"), m["value"]]
        elif op == "replace_operand":
            parts = ["operand", h(m.get("node"), "node"), n(m.get("index"), "index", 0, 4096), h(m.get("value"), "value")]
        elif op == "delete":
            parts = ["delete", h(m.get("node"), "node")]
        elif op == "prune_dead":
            parts = ["prune", h(m.get("node"), "node")]
        elif op == "move":
            parts = ["move", h(m.get("node"), "node"), "before", h(m.get("before"), "before")]
        elif op == "insert_constant":
            parts = ["insert-constant", h(m.get("anchor"), "anchor"), n(m.get("id"), "id", 0, 4096), n(m.get("value"), "value")]
        elif op == "set_edge":
            parts = ["edge", h(m.get("anchor"), "anchor"), n(m.get("edge"), "edge", 0, 4096), n(m.get("argument"), "argument", 0, 4096),
                     h(m.get("value"), "value")]
        elif op == "set_type":
            parts = ["type", h(m.get("target"), "target")]
            if "result" in m:
                parts.append(n(m["result"], "result", 0, 4096))
            parts.append(h(m.get("type"), "type"))
        elif op == "set_signature":
            parts = ["sig", h(m.get("function"), "function"), t(m.get("params"), "params"), t(m.get("returns"), "returns")]
        else:
            raise ToolError("unsupported", f"unknown mutation op {op!r}")
        records.append(" ".join(parts))
    if not records:
        raise ToolError("invalid_request", "a transaction needs at least one mutation")
    return "; ".join(records)
