"""Versioned JSON schemas (draft 2020-12) of the tool arguments: transport values only, never XAX source."""

from __future__ import annotations

SCHEMA_VERSION = "xax-mcp-tools-v1"

_HANDLE = {"type": "string", "minLength": 1, "maxLength": 64, "pattern": "^[A-Za-z0-9_.@-]+$"}
_GEN = {"type": "integer", "minimum": 0, "maximum": 2 ** 31}
_CID = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
_LIMIT = {"type": "integer", "minimum": 1, "maximum": 256}
_CONT = {"type": "integer", "minimum": 0, "maximum": 2 ** 31}
_INT_TYPE = {"enum": ["b8", "b16", "b32", "b64"]}
_SMALL = {"type": "integer", "minimum": 0, "maximum": 4096}
_INT64 = {"type": "integer", "minimum": -(2 ** 64) + 1, "maximum": 2 ** 64 - 1}
_TOKEN = {"type": "string", "maxLength": 64, "pattern": "^[A-Za-z@][A-Za-z0-9.@_-]*$"}

_MUTATION = {
    "type": "object",
    "required": ["op"],
    "additionalProperties": False,
    "properties": {
        "op": {"enum": ["set_constant", "set_operation", "replace_operand", "delete", "prune_dead", "move",
                        "insert_constant", "set_edge", "set_type", "set_signature"]},
        "node": _TOKEN, "anchor": _TOKEN, "before": _TOKEN, "function": _TOKEN, "target": _TOKEN, "type": _TOKEN,
        "value": {"anyOf": [_INT64, _TOKEN]},
        "index": _SMALL, "id": _SMALL, "edge": _SMALL, "argument": _SMALL, "result": _SMALL,
        "params": {"type": "array", "maxItems": 64, "items": _TOKEN},
        "returns": {"type": "array", "maxItems": 64, "items": _TOKEN},
    },
}

TOOLS: dict[str, dict] = {
    "xax_capabilities": {
        "title": "XAX capabilities",
        "description": "Server/compiler identity, pinned XAX revision, targets, operations, carrier types, I/O modes, "
                       "granted rights, sandbox status and honest maturity labels. Call first.",
        "annotations": {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False},
        "inputSchema": {"type": "object", "additionalProperties": False, "properties": {}},
    },
    "xax_workspace": {
        "title": "XAX workspace",
        "description": "list | describe | close a session-scoped workspace handle, or open a verified .xax store by "
                       "relative name inside a host-granted store root. Returns root identity and generation, not the program.",
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
        "inputSchema": {"type": "object", "additionalProperties": False, "required": ["action"], "properties": {
            "action": {"enum": ["open", "list", "describe", "close"]},
            "workspace": _HANDLE,
            "store": {"type": "string", "minLength": 5, "maxLength": 255},
        }},
    },
    "xax_query": {
        "title": "XAX bounded query",
        "description": "Bounded, paginated queries of the current root via the XAX workspace: root, functions, function_nodes, "
                       "function_view (tooling view, not source), operands, neighborhood, uses, callers, callees, type, effects, "
                       "effect_summary, entity, proof, diff, repair (diagnostic handle).",
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
        "inputSchema": {"type": "object", "additionalProperties": False, "required": ["workspace", "kind"], "properties": {
            "workspace": _HANDLE,
            "kind": {"enum": ["root", "functions", "function_nodes", "function_view", "operands", "neighborhood", "uses",
                              "callers", "callees", "type", "effects", "effect_summary", "entity", "proof", "diff", "repair"]},
            "handle": _HANDLE, "limit": _LIMIT, "continuation": _CONT, "from_generation": _GEN,
        }},
    },
    "xax_construct": {
        "title": "XAX construct",
        "description": "Construct and verify a NEW XAX program from one xax-construct-v1 carrier (typed semantic graph: types, "
                       "functions of blocks of [operation, operands, result types, extra] nodes, package entries). The carrier is "
                       "transport; the verified canonical store becomes a workspace. Platform: linux-x86_64.",
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
        "inputSchema": {"type": "object", "additionalProperties": False, "required": ["request"], "properties": {
            "request": {"type": "object", "required": ["format", "platform", "functions", "package"], "properties": {
                "format": {"const": "xax-construct-v1"},
                "platform": {"enum": ["linux-x86_64"]},
                "types": {"type": "object", "maxProperties": 256},
                "functions": {"type": "array", "minItems": 1, "maxItems": 256, "items": {"type": "object"}},
                "package": {"type": "object"},
            }},
        }},
    },
    "xax_transaction": {
        "title": "XAX transaction",
        "description": "Verify (private candidate), commit, or rollback typed mutations against an exact expected generation and "
                       "root. Handles must have been exposed by xax_query at that generation. Rejections return XAX diagnostics "
                       "and a diagnostic handle for the repair neighborhood; stale roots are rejected, never refreshed.",
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "openWorldHint": False},
        "inputSchema": {"type": "object", "additionalProperties": False, "required": ["workspace", "mode"], "properties": {
            "workspace": _HANDLE,
            "mode": {"enum": ["verify", "commit", "rollback"]},
            "expected_generation": _GEN, "expected_root": _CID,
            "mutations": {"type": "array", "minItems": 1, "maxItems": 256, "items": _MUTATION},
            "read_set": {"type": "array", "maxItems": 256, "items": _HANDLE},
            "candidate": _HANDLE,
        }, "allOf": [{"if": {"properties": {"mode": {"enum": ["verify", "commit"]}}},
                      "then": {"required": ["expected_generation", "expected_root", "mutations"]}},
                     {"if": {"properties": {"mode": {"const": "rollback"}}}, "then": {"required": ["candidate"]}}]},
    },
    "xax_build": {
        "title": "XAX build",
        "description": "Verify and compile the workspace's exact current root for one package entry with the canonical XAX build "
                       "service. Returns an opaque artifact handle, BLAKE3/SHA-256 digests and provenance. Cached per session by "
                       "(root, entry, toolchain fingerprint).",
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
        "inputSchema": {"type": "object", "additionalProperties": False, "required": ["workspace"], "properties": {
            "workspace": _HANDLE, "entry": {"type": "string", "pattern": "^[A-Za-z0-9_.-]{1,64}$"}, "expected_generation": _GEN,
        }},
    },
    "xax_execute": {
        "title": "XAX execute",
        "description": "Run a built artifact in the OS sandbox (new user/mount/net namespaces, empty read-only root, seccomp "
                       "allowlist, rlimits, wall timeout). Input is framed onto stdin (xax-mcp-io-v1) and optional argv strings reach "
                       "linux.startup.* reads; stdout is decoded by the "
                       "declared layout. Only the 'stdio' effect exists. Requires the host-granted execute right.",
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "openWorldHint": False},
        "inputSchema": {"type": "object", "additionalProperties": False, "required": ["artifact"], "properties": {
            "artifact": _HANDLE,
            "input": {"type": "object", "maxProperties": 1, "additionalProperties": False, "properties": {
                "ints": {"type": "array", "maxItems": 131072, "items": {"type": "object", "additionalProperties": False,
                                                                       "required": ["type", "value"],
                                                                       "properties": {"type": _INT_TYPE, "value": _INT64}}},
                "bytes_base64": {"type": "string", "maxLength": 1398104},
                "text": {"type": "string", "maxLength": 1048576},
            }},
            "output": {"anyOf": [{"enum": ["bytes", "text"]},
                                 {"type": "object", "additionalProperties": False, "required": ["ints"],
                                  "properties": {"ints": {"type": "array", "maxItems": 4096, "items": _INT_TYPE}}}]},
            "argv": {"type": "array", "maxItems": 64, "items": {"type": "string", "maxLength": 4096}},
            "effects": {"type": "array", "maxItems": 8, "items": {"enum": ["stdio", "filesystem.read", "filesystem.write",
                                                                           "network", "process", "environment", "clock"]}},
            "limits": {"type": "object", "additionalProperties": False, "properties": {
                "wall_ms": {"type": "integer", "minimum": 10, "maximum": 600000},
                "cpu_seconds": {"type": "integer", "minimum": 1, "maximum": 600},
                "memory_mb": {"type": "integer", "minimum": 16, "maximum": 65536},
                "max_output_bytes": {"type": "integer", "minimum": 1, "maximum": 67108864}}},
            "require_current": {"type": "boolean"},
        }},
    },
    "xax_result": {
        "title": "XAX result",
        "description": "Fetch a bounded chunk of a large result by opaque handle: execution stdout (res_), a workspace's canonical "
                       "store bytes (ws_), or a stored diagnostic (diag_). Never returns unbounded data.",
        "annotations": {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False},
        "inputSchema": {"type": "object", "additionalProperties": False, "required": ["handle"], "properties": {
            "handle": _HANDLE, "offset": _CONT, "length": {"type": "integer", "minimum": 1, "maximum": 65536},
        }},
    },
}
