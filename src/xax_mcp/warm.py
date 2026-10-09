"""Warm server: a per-user process that has already loaded the XAX components, and forks one child per MCP client.

Without it every ``xax-mcp`` launch pays Python imports plus the XAX component warm-up (seconds; tens of seconds with
an empty XAX image cache) before its first tool call can run.  With it, a launch is a small launcher process that
hands its own STDIO file descriptors to the warm server over a Unix socket; the warm server forks, and the child
serves MCP on those descriptors with the XAX components already in memory.

Authority does not move: the child parses the launcher's own command line into its policy, exactly as if the
launcher had served the client itself, and the warm server holds no rights and no client data.  Only processes of the
same user can connect (a 0700 directory and an ``SO_PEERCRED`` check).  Each child has its own memory, sessions and
handles.  A child exits when its client closes STDIN or when its launcher dies.  The warm server exits after
``XAX_MCP_WARM_IDLE_SECONDS`` (default 900) without children.

The socket name is keyed by everything that decides what a child would run (xax-mcp sources, the installed XAX
distribution record, the Python executable, the user, and every ``XAX_*`` environment variable other than the
per-launch ``XAX_MCP_*`` ones), so an upgraded or differently configured install never reaches a stale server.
"""

from __future__ import annotations

import array
import hashlib
import json
import os
import select
import signal
import socket
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path

DISABLE_ENV = "XAX_MCP_WARM_SERVER"  # "0" disables
IDLE_ENV = "XAX_MCP_WARM_IDLE_SECONDS"
DIR_ENV = "XAX_MCP_WARM_DIR"
# Per-launch settings forwarded from the launcher to its child; they do not change what XAX loads.
PER_LAUNCH_ENV = ("XAX_MCP_LOG", "XAX_MCP_REQUIRE_SANDBOX")
_MAX_HEADER = 64 * 1024
_ACK = b"+"
_RETRY_FAILED_SECONDS = 600
_KEEP_ENV = ("PATH", "HOME", "LANG", "LC_ALL", "LC_CTYPE", "TMPDIR", "XDG_RUNTIME_DIR", "XDG_CACHE_HOME", "PYTHONPATH")


def enabled() -> bool:
    return os.environ.get(DISABLE_ENV, "1") != "0" and sys.platform.startswith("linux") and hasattr(socket, "SCM_RIGHTS")


def _state_dir() -> Path:
    base = os.environ.get(DIR_ENV)
    if not base:
        runtime = os.environ.get("XDG_RUNTIME_DIR")
        base = os.path.join(runtime, "xax-mcp") if runtime else os.path.join(
            os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache"), "xax-mcp", "run")
    path = Path(base)
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = path.lstat()
    if not path.is_dir() or path.is_symlink() or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise OSError(f"warm server directory {path} must be a private (0700) directory owned by this user")
    return path


def _xax_record() -> bytes:
    """The installed XAX distribution's RECORD (it lists a sha256 for every installed file)."""
    import importlib.metadata

    try:
        distribution = importlib.metadata.distribution("xax-compiler")
    except importlib.metadata.PackageNotFoundError:
        return b"missing"
    return (distribution.read_text("RECORD") or "").encode() + str(distribution.locate_file("")).encode()


def key() -> str:
    digest = hashlib.sha256()
    package = Path(__file__).resolve().parent
    for source in sorted(package.glob("*.py")):
        digest.update(source.name.encode() + b"\0" + source.read_bytes() + b"\0")
    digest.update(_xax_record())
    env = sorted((k, v) for k, v in os.environ.items() if k.startswith("XAX_") and k not in PER_LAUNCH_ENV
                 and k not in (DISABLE_ENV, IDLE_ENV, DIR_ENV))
    digest.update(json.dumps([sys.executable, sys.version, os.getuid(), env]).encode())
    return digest.hexdigest()[:24]


def socket_path(directory: Path, server_key: str) -> Path:
    return directory / f"warm-{server_key}.sock"


class _Short:
    """A short alias for a path in ``directory``: AF_UNIX paths are limited to 108 bytes, so sockets are bound and
    connected through ``/proc/self/fd/<directory fd>/<name>``."""

    def __init__(self, directory: Path):
        self.fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)

    def __call__(self, path: Path) -> str:
        return f"/proc/self/fd/{self.fd}/{path.name}"

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        os.close(self.fd)


# -- launcher side ----------------------------------------------------------------------------------------------------
def launch(argv: list[str]) -> int | None:
    """Serve this client through the warm server.  Returns the child's exit status, or None when no warm server is
    ready (then a warm server is started in the background for later launches and the caller serves in-process)."""
    try:
        directory = _state_dir()
        server_key = key()
        path = socket_path(directory, server_key)
        connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            with _Short(directory) as short:
                connection.connect(short(path))
        except OSError:
            connection.close()
            _spawn(directory, server_key)
            return None
    except OSError:
        return None
    with connection:
        header = json.dumps({"argv": argv, "cwd": os.getcwd(),
                             "env": {k: os.environ[k] for k in PER_LAUNCH_ENV if k in os.environ}}).encode()
        try:
            connection.sendmsg([struct.pack("<I", len(header)) + header],
                               [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array("i", [0, 1, 2]))])
        except OSError:
            return None
        # The warm server acknowledges once a child owns the descriptors; until then this process can still serve.
        connection.settimeout(30)
        try:
            if connection.recv(1) != _ACK:
                return None
        except OSError:
            return None
        connection.settimeout(None)
        # Our STDIO now belongs to the child as well; close our copies so the client sees EOF only from the child.
        devnull = os.open(os.devnull, os.O_RDWR)
        for fd in (0, 1):
            os.dup2(devnull, fd)
        os.close(devnull)
        status = b""
        while True:
            try:
                chunk = connection.recv(16)
            except InterruptedError:
                continue
            except OSError:
                break
            if not chunk:
                break
            status += chunk
        try:
            return int(status.decode() or "1")
        except ValueError:
            return 1


def _spawn(directory: Path, server_key: str) -> None:
    lock = directory / f"warm-{server_key}.lock"
    failed = directory / f"warm-{server_key}.failed"
    try:  # a warm server for this configuration failed to start recently: do not keep paying for it
        if time.time() - failed.stat().st_mtime < _RETRY_FAILED_SECONDS:
            return
    except OSError:
        pass
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        try:  # a warm server is already starting, unless its lock is stale
            if time.time() - lock.stat().st_mtime < 600:
                return
            lock.unlink()
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except OSError:
            return
    os.close(fd)
    env = {k: v for k, v in os.environ.items() if k in _KEEP_ENV or (k.startswith("XAX_") and k not in PER_LAUNCH_ENV)}
    subprocess.Popen([sys.executable, "-m", "xax_mcp.warm", str(directory), server_key], stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env, start_new_session=True, close_fds=True)


def prepare(timeout: float = 900.0) -> dict:
    """Start the warm server (loading, and on first use lowering, every XAX component) and wait until it is ready."""
    directory = _state_dir()
    server_key = key()
    path = socket_path(directory, server_key)
    started = time.monotonic()
    if not path.exists():
        _spawn(directory, server_key)
    while not path.exists():
        if time.monotonic() - started > timeout:
            raise TimeoutError(f"the warm server did not become ready within {timeout:.0f} s")
        time.sleep(0.1)
    return {"warm_server": "ready", "socket": path.name, "waited_ms": round((time.monotonic() - started) * 1000),
            "idle_exit_seconds": int(os.environ.get(IDLE_ENV, "900"))}


# -- warm server side -------------------------------------------------------------------------------------------------
def _peer_uid(connection: socket.socket) -> int:
    credentials = connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
    return struct.unpack("3i", credentials)[1]


def _receive(connection: socket.socket) -> tuple[dict, list[int]]:
    connection.settimeout(5)
    fds = array.array("i")
    data, ancillary, _flags, _address = connection.recvmsg(_MAX_HEADER + 4, socket.CMSG_SPACE(3 * fds.itemsize))
    for level, kind, payload in ancillary:
        if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
            fds.frombytes(payload[:len(payload) - len(payload) % fds.itemsize])
    try:
        while len(data) >= 4 and len(data) < 4 + struct.unpack("<I", data[:4])[0]:
            more = connection.recv(_MAX_HEADER)
            if not more:
                break
            data += more
        length = struct.unpack("<I", data[:4])[0]
        if len(fds) != 3 or length > _MAX_HEADER or len(data) != 4 + length:
            raise ValueError("malformed launch request")
        header = json.loads(data[4:])
        if not (isinstance(header.get("argv"), list) and all(isinstance(a, str) for a in header["argv"])
                and isinstance(header.get("cwd"), str) and isinstance(header.get("env"), dict)):
            raise ValueError("malformed launch request")
    except (ValueError, struct.error):
        for fd in fds:
            os.close(fd)
        raise
    connection.settimeout(None)
    return header, list(fds)


def _child(connection: socket.socket, header: dict, fds: list[int], warm) -> None:
    """In the forked child: become the launcher's server.  Never returns."""
    code = 1
    try:
        connection.sendall(_ACK)  # first, so that it always precedes the exit status
        for target, fd in enumerate(fds):
            os.dup2(fd, target)
            os.close(fd)
        signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        os.chdir(header["cwd"])
        os.environ.update({k: str(v) for k, v in header["env"].items() if k in PER_LAUNCH_ENV})
        def watch_launcher():  # the launcher holds the other end; it closing means the client is gone
            try:
                while connection.recv(1):
                    pass
            except OSError:
                pass
            os._exit(0)

        threading.Thread(target=watch_launcher, name="xax-launcher-watch", daemon=True).start()
        from .server import main

        code = main(header["argv"], warm=warm)
    except SystemExit as exit_:  # as the interpreter would: a message goes to stderr with status 1
        if exit_.code is None or isinstance(exit_.code, int):
            code = exit_.code or 0
        else:
            print(exit_.code, file=sys.stderr)
            code = 1
    except BaseException:
        code = 70
    finally:
        try:
            sys.stderr.flush()
            connection.sendall(str(code).encode())
        except BaseException:
            pass
        os._exit(code)


def serve(directory: Path, server_key: str) -> None:
    """Warm the XAX components, then accept launchers until idle.  Runs single-threaded so that fork is safe."""
    lock = directory / f"warm-{server_key}.lock"
    path = socket_path(directory, server_key)
    try:
        from .server import preload

        preload()  # the MCP SDK and schemas, so children start without imports
        from .service import warm_state

        warm = warm_state()
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        temporary = directory / f".w{os.getpid()}.sock"
        with _Short(directory) as short:
            listener.bind(short(temporary))
        os.chmod(temporary, 0o600)
        listener.listen(16)
        os.replace(temporary, path)  # launchers only ever see a ready server
        identity = path.stat().st_ino
    except BaseException:
        (directory / f"warm-{server_key}.failed").touch(mode=0o600)
        raise
    finally:
        try:
            lock.unlink()
        except OSError:
            pass
    idle = max(1, int(os.environ.get(IDLE_ENV, "900")))
    children: set[int] = set()
    last_activity = time.monotonic()
    try:
        while True:
            for pid in list(children):
                try:
                    done, _ = os.waitpid(pid, os.WNOHANG)
                except ChildProcessError:
                    done = pid
                if done:
                    children.discard(pid)
                    last_activity = time.monotonic()
            if not children and time.monotonic() - last_activity > idle:
                return
            try:
                if path.stat().st_ino != identity:
                    return  # replaced by another warm server
            except OSError:
                return
            ready, _, _ = select.select([listener], [], [], 1.0)
            if not ready:
                continue
            connection, _ = listener.accept()
            last_activity = time.monotonic()
            try:
                if _peer_uid(connection) != os.getuid():
                    connection.close()
                    continue
                header, fds = _receive(connection)
            except (OSError, ValueError):
                connection.close()
                continue
            if threading.active_count() != 1:  # forking a multi-threaded process is unsafe; the launcher serves itself
                for fd in fds:
                    os.close(fd)
                connection.close()
                return
            try:
                pid = os.fork()
            except OSError:
                for fd in fds:
                    os.close(fd)
                connection.close()  # no acknowledgement: the launcher serves itself
                continue
            if pid == 0:
                listener.close()
                _child(connection, header, fds, warm)
            for fd in fds:
                os.close(fd)
            connection.close()
            children.add(pid)
    finally:
        try:
            if path.stat().st_ino == identity:
                path.unlink()
        except OSError:
            pass
        listener.close()


if __name__ == "__main__":
    serve(Path(sys.argv[1]), sys.argv[2])
