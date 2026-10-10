"""Declared XAX compatibility: the exact upstream revision this release is tested against.

XAX publishes no release tags and its distribution version (``xax-compiler 0.1.0``) does not change between
commits, so compatibility is pinned to an immutable commit and checked through a content fingerprint of the
installed toolchain (every Python module and canonical bootstrap store of the ``xax-compiler`` distribution).
"""

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import os
from dataclasses import dataclass
from pathlib import Path

XAX_REPOSITORY = "https://github.com/MrxSiN/XAX"
XAX_DISTRIBUTION = "xax-compiler"
XAX_DISTRIBUTION_VERSION = "0.1.0"
# Tested pins: commit -> sha256 fingerprint of the installed toolchain files (see ``toolchain_fingerprint``).
# 0.1.0 tested 01ad841c76416fc741dd1386b12124904924c10d (fingerprint 2d5b1f3b...), which predates xax_contract;
# 0.2.0 tested f38cbeea2b90e9b6a580417ce7efaa7d3d75a183 (fingerprint cdf3e586...), host contract r1;
# 0.3.0 tested b0ec772a954a6b7932c6e3c1d44794c036a9b7ab (fingerprint 636b268c...), host contract r2;
# 0.3.1 and 0.4.0 tested 6c2df90b5972dcf6f44ae6d32f828f355d30d2de (fingerprint 41d0f5d6...), host contract r2;
# 0.5.0 tested 13a6843200c42f319ede02968773031fe6bca55f (fingerprint bd0c1ef6...), host contract r3.
TESTED_XAX = {
    "f0aa191424f6e404004f96422eb8a032ef8a1bb2": "80d8966ec3d78cb7f40ecb05f09dff5f871260fbbccb8ef18068072a242ba659",
}
PINNED_XAX_COMMIT = "f0aa191424f6e404004f96422eb8a032ef8a1bb2"
# Upstream interfaces this adapter consumes (within xax-host-contract-v1; see docs/XAX_CONTRACT.md).
REQUIRED_API = {
    "xax_construct": ("construct", "FORMAT"),
    "xax_build": ("build", "build_request", "resolve_packages", "snapshot_store", "decode_snapshot", "decode_request",
                  "decode_package", "decode_provenance", "ArtifactKind"),
    "xax_workspace": ("Workspace", "RootRef", "Transaction"),
    "xax_local_protocol": ("LocalMutationSession", "edit_grammar_id"),
    "xax_compiler": ("StoreReader", "XaxError", "Diagnostic", "Kind", "Operation", "IntCompare", "decode_native_target",
                     "X86_64_LINUX_ELF_EXEC_FORMAT", "X86_64_LINUX_ABI", "verify_store"),
    "xax_linux": ("linux_api",),
    "xax_artifact": ("BOOTSTRAP_COMPILER_IDENTITY_V1",),
    "xax_contract": ("HOST_CONTRACT", "HOST_CONTRACT_MINOR", "describe", "missing"),
    "xax_native": ("prepare", "PREPARE_COMPONENTS"),
}
# The upstream host contract this release consumes (xax_contract, ADR-225) and the oldest minor revision it needs:
# r2 (ADR-231) adds checked accesses of 1/2/4/8 bytes on bits<8> views, which carriers may now rely on;
# r3 (ADR-250) adds xax_native.prepare, which the warm server and --prepare use to ready the XAX components.
HOST_CONTRACT = "xax-host-contract-v1"
HOST_CONTRACT_MINOR = 3
ALLOW_UNPINNED_ENV = "XAX_MCP_ALLOW_UNTESTED_XAX"


@dataclass(frozen=True)
class Compatibility:
    status: str  # "tested" | "untested" | "incompatible"
    distribution_version: str | None
    fingerprint: str | None
    commit: str | None
    reason: str | None

    def as_dict(self) -> dict:
        return {"status": self.status, "distribution": XAX_DISTRIBUTION, "distribution_version": self.distribution_version,
                "toolchain_fingerprint": self.fingerprint, "matched_commit": self.commit, "pinned_commit": PINNED_XAX_COMMIT,
                "repository": XAX_REPOSITORY, "reason": self.reason}


def _toolchain_files() -> list[Path]:
    files: list[Path] = []
    try:
        for entry in importlib.metadata.files(XAX_DISTRIBUTION) or ():
            name = str(entry)
            if "__pycache__" in name or ".dist-info" in name:
                continue
            if name.endswith(".py") or name.endswith(".xax"):
                files.append(Path(entry.locate()))
    except importlib.metadata.PackageNotFoundError:
        pass
    if not any(path.name == "xax_compiler.py" for path in files):
        # Editable or source-tree use: the module directory and its bootstrap stores.
        module_dir = Path(importlib.import_module("xax_compiler").__file__).parent
        files = [p for p in module_dir.iterdir() if p.suffix == ".py" and (p.name.startswith("xax_") or p.name == "blake3.py")]
        from xax_native import bootstrap_dir

        files += sorted(bootstrap_dir().glob("*.xax"))
    return files


def toolchain_fingerprint() -> str:
    """sha256 over (relative name, sha256(content)) of every toolchain module and bootstrap store, name-sorted."""
    digest = hashlib.sha256()
    for path in sorted(_toolchain_files(), key=lambda p: (p.suffix, p.name)):
        digest.update(path.name.encode() + b"\0" + hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def check() -> Compatibility:
    try:
        version = importlib.metadata.version(XAX_DISTRIBUTION)
    except importlib.metadata.PackageNotFoundError:
        version = None
    missing = []
    for module, names in REQUIRED_API.items():
        try:
            loaded = importlib.import_module(module)
        except ImportError:
            missing.append(module)
            continue
        missing += [f"{module}.{name}" for name in names if not hasattr(loaded, name)]
    if missing:
        return Compatibility("incompatible", version, None, None, f"missing XAX interfaces: {', '.join(missing)}")
    contract = importlib.import_module("xax_contract")
    if contract.HOST_CONTRACT != HOST_CONTRACT or contract.HOST_CONTRACT_MINOR < HOST_CONTRACT_MINOR:
        return Compatibility("incompatible", version, None, None,
                             f"XAX host contract {contract.HOST_CONTRACT} r{contract.HOST_CONTRACT_MINOR}; "
                             f"this release needs {HOST_CONTRACT} r{HOST_CONTRACT_MINOR} or later")
    if contract.missing():
        return Compatibility("incompatible", version, None, None, f"XAX host contract names missing: {', '.join(contract.missing())}")
    if importlib.import_module("xax_construct").FORMAT != "xax-construct-v1":
        return Compatibility("incompatible", version, None, None, "xax_construct.FORMAT is not xax-construct-v1")
    fingerprint = toolchain_fingerprint()
    commit = next((c for c, f in TESTED_XAX.items() if f == fingerprint), None)
    if commit is not None:
        return Compatibility("tested", version, fingerprint, commit, None)
    return Compatibility("untested", version, fingerprint, None,
                         f"installed XAX toolchain fingerprint matches no tested commit (pinned {PINNED_XAX_COMMIT}); "
                         f"install the pinned revision or set {ALLOW_UNPINNED_ENV}=1 to run untested")


def allow_untested() -> bool:
    return os.environ.get(ALLOW_UNPINNED_ENV) == "1"
