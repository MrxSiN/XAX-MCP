"""Host-configured authority.  Rights and limits come only from the server's launch configuration (command-line
flags written by the host owner into the MCP client config), never from tool arguments."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass, field
from pathlib import Path

from .sandbox import Limits

RIGHTS = ("read", "mutate", "build", "execute")
DEFAULT_RIGHTS = frozenset({"read", "mutate", "build"})  # execution must be granted explicitly


@dataclass(frozen=True)
class Policy:
    rights: frozenset[str] = DEFAULT_RIGHTS
    store_roots: tuple[Path, ...] = ()
    limits: Limits = field(default_factory=Limits)
    max_request_bytes: int = 1024 * 1024
    max_store_bytes: int = 16 * 1024 * 1024
    max_workspaces: int = 16
    max_artifacts: int = 64
    max_results: int = 64
    inline_output_bytes: int = 4096
    query_byte_budget: int = 16 * 1024

    def require(self, right: str) -> None:
        from .errors import ToolError

        if right not in self.rights:
            flag = "--allow-execute" if right == "execute" else f"--grant {right}"
            raise ToolError("denied_capability", f"this server was not granted the '{right}' right by its host configuration",
                            repair=[f"the host owner may add {flag} to the server launch command"])

    def as_dict(self) -> dict:
        return {"rights": sorted(self.rights), "store_roots": len(self.store_roots), "limits": self.limits.as_dict(),
                "max_request_bytes": self.max_request_bytes, "max_store_bytes": self.max_store_bytes,
                "inline_output_bytes": self.inline_output_bytes, "effects_granted": ["stdio"]}


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="xax-mcp", description="XAX MCP server (STDIO transport).")
    p.add_argument("--allow-execute", action="store_true", help="grant the execute right (sandboxed native execution)")
    p.add_argument("--deny", action="append", default=[], choices=RIGHTS, help="withhold a right (repeatable)")
    p.add_argument("--read-only", action="store_true", help="grant only the read right")
    p.add_argument("--store-root", action="append", default=[], metavar="DIR",
                   help="directory whose .xax stores may be opened read-only by relative name (repeatable)")
    p.add_argument("--wall-ms", type=int, default=5000)
    p.add_argument("--cpu-seconds", type=int, default=5)
    p.add_argument("--memory-mb", type=int, default=256)
    p.add_argument("--max-output-bytes", type=int, default=1024 * 1024)
    p.add_argument("--max-request-bytes", type=int, default=1024 * 1024)
    p.add_argument("--check", action="store_true", help="print compatibility and sandbox status as JSON and exit")
    p.add_argument("--version", action="store_true", help="print version information and exit")
    p.add_argument("--prepare", action="store_true",
                   help="start the per-user warm server, wait until the XAX components are loaded, and exit")
    p.add_argument("--no-warm-server", action="store_true",
                   help="serve in this process instead of forking from the per-user warm server (see docs/PERFORMANCE.md)")
    return p


def from_args(args: argparse.Namespace) -> Policy:
    rights = set(DEFAULT_RIGHTS)
    if args.allow_execute:
        rights.add("execute")
    if args.read_only:
        rights = {"read"}
    rights -= set(args.deny)
    roots = []
    for root in args.store_root:
        path = Path(root).resolve(strict=True)
        if not path.is_dir():
            raise SystemExit(f"--store-root {root!r} is not a directory")
        roots.append(path)
    for name, value, low, high in (("--wall-ms", args.wall_ms, 10, 600_000), ("--cpu-seconds", args.cpu_seconds, 1, 600),
                                   ("--memory-mb", args.memory_mb, 16, 65536),
                                   ("--max-output-bytes", args.max_output_bytes, 1, 64 << 20),
                                   ("--max-request-bytes", args.max_request_bytes, 1024, 64 << 20)):
        if not low <= value <= high:
            raise SystemExit(f"{name} must be within [{low}, {high}]")
    limits = Limits(wall_ms=args.wall_ms, cpu_seconds=args.cpu_seconds, memory_bytes=args.memory_mb << 20,
                    max_stdout_bytes=args.max_output_bytes)
    return Policy(frozenset(rights), tuple(roots), limits, max_request_bytes=args.max_request_bytes)


def resolve_store(policy: Policy, name: str) -> Path:
    """Resolve a relative ``.xax`` name inside a granted root: no absolute paths, traversal, or symlink escape."""
    from .errors import ToolError

    if not policy.store_roots:
        raise ToolError("denied_capability", "no --store-root is granted to this server",
                        repair=["construct a program with xax_construct instead, or ask the host owner to grant a store root"])
    parts = Path(name).parts
    if (not name or name.startswith(("/", "\\")) or os.path.isabs(name) or ".." in parts or "\0" in name
            or not name.endswith(".xax") or len(name) > 255):
        raise ToolError("invalid_request", "store name must be a relative '.xax' path without '..'")
    for root in policy.store_roots:
        candidate = root / name
        # Every component must be a real directory/file under the root; symlinks are refused outright.
        current = root
        for part in parts:
            current = current / part
            if current.is_symlink():
                raise ToolError("denied_capability", "symbolic links are not followed in store roots")
        if candidate.is_file():
            real = candidate.resolve(strict=True)
            if root not in real.parents:
                raise ToolError("denied_capability", "store path escapes its granted root")
            if real.stat().st_size > policy.max_store_bytes:
                raise ToolError("resource_limit", "store exceeds the configured size limit")
            return real
    raise ToolError("not_found", "no such store in the granted roots")
