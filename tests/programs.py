"""xax-construct-v1 carriers used by the tests.  They are typed semantic-graph requests sent through MCP exactly as
an agent would send them; the server has no knowledge of them.  Python here only *writes the request*; the
computation is performed by the XAX-generated executable.

The I/O nodes come from the host platform's carrier entities: ``linux.*`` system calls on Linux, ``win32.*`` kernel32
calls on Windows (XAX ADR-252).  ``_Nodes`` emits them inline (XAX's memory call contract keeps view allocation in the
function that owns the view); the computation is the same graph on both platforms."""

from __future__ import annotations

import sys

WINDOWS = sys.platform == "win32"
PLATFORM = "windows-x86_64" if WINDOWS else "linux-x86_64"
P = "win32." if WINDOWS else "linux."
TYPES = {"mem": P + "memory_effect", "proc": P + "process_effect", "fs": P + "filesystem_effect",
         "ptr": P + "bytes_rw", "in": {"view": 4096}, "out": {"view": 16},
         **({"cnt": {"view": 4}, "u32p": "win32.u32_rw"} if WINDOWS else {})}
# Windows programs carry a second memory proof for the transfer-count cells, so the data views keep their own
# memory-effect provenance across direct calls (as in XAX's PE fixture).
IO = ["mem"] if WINDOWS else []
LOOP = ["proc", "fs", "ptr", "in", "mem", "b32", "b64", "b64", "b32", *IO]
ALL = [f"p{i}" for i in range(len(LOOP))]
_STD_INPUT, _STD_OUTPUT = 0xFFFFFFF6, 0xFFFFFFF5  # (DWORD)-10, (DWORD)-11


class _Nodes(list):
    """The node list of one block; ``add`` appends a node and returns its value name."""

    def add(self, *node) -> str:
        self.append(list(node))
        return f"n{len(self) - 1}"

    def alloc(self, view: str, size: int, mem: str, ptr: str = "ptr", align: int = 1) -> tuple[str, str, str]:
        """Fresh zeroed pages as a checked heap view: (pointer, view, mem)."""
        if WINDOWS:
            pages = self.add("call.foreign", [["b64", 0], ["b64", size], ["b32", 0x3000], ["b32", 4], mem],
                             ["win32.heap_ptr_rw", "win32.heap_resource", "mem"], {"entity": "win32.virtual_alloc"})
        else:
            pages = self.add("call.foreign", [["b64", size], mem], ["ptr", "linux.heap_owner", "mem"], {"entity": "linux.mmap_anonymous"})
        v = self.add("heap.view", [pages, f"{pages}.r1", f"{pages}.r2"], [ptr, view, "mem"], {"attrs": [size, align]})
        return v, f"{v}.r1", f"{v}.r2"

    def free(self, size: int, pointer: str, view: str, mem: str, ptr: str = "ptr") -> str:
        """Release a view's pages; returns mem."""
        if WINDOWS:
            n = self.add("call.foreign", [pointer, ["b64", 0], ["b32", 0x8000], view, mem], ["b32", "mem"],
                         {"entity": {"win32.virtual_free_view": [ptr, size]}})
        else:
            n = self.add("call.foreign", [pointer, view, mem], ["b64", "mem"], {"entity": {"linux.munmap_view": [ptr, size]}})
        return f"{n}.r1"

    def transfer(self, write: bool, proc: str, fs: str, pointer: str, count, mem: str, io: str | None = None):
        """read(stdin) or write(stdout) of ``count`` bytes at ``pointer``: (b64 transferred, proc, fs, mem, io).

        On Linux the system call takes the data view's memory proof; on Windows the count cell lives on ``io``."""
        if not WINDOWS:
            buffer = self.add("pointer.cast", [pointer], ["linux.bytes_read"]) if write else pointer
            n = self.add("call.foreign", [["b32", int(write)], buffer, count, fs, mem], ["b64", "fs", "mem"],
                         {"entity": "linux.write" if write else "linux.read"})
            return n, proc, f"{n}.r1", f"{n}.r2", io
        handle = self.add("call.foreign", [["b32", _STD_OUTPUT if write else _STD_INPUT], proc], ["b64", "proc"],
                          {"entity": "win32.get_std_handle"})
        cell, cell_view, io = self.alloc("cnt", 4, io, "u32p", 4)
        dword = self.add("int.truncate", [count], ["b32"]) if isinstance(count, str) else ["b32", count[1]]
        buffer = self.add("pointer.cast", [pointer], ["win32.bytes_read"]) if write else pointer
        n = self.add("call.foreign", [handle, buffer, dword, cell, ["b64", 0], fs, io], ["b32", "fs", "mem"],
                     {"entity": "win32.write_file" if write else "win32.read_file"})
        done = self.add("checked.load.bits.le", [cell, ["b32", 0], f"{n}.r2"], ["b32", "mem"], {"attrs": [4, 1]})
        io = self.free(4, cell, cell_view, f"{done}.r1", "u32p")
        return self.add("int.zero.extend", [done], ["b64"]), f"{handle}.r1", f"{n}.r1", mem, io

    def exit(self, status, proc: str) -> str:
        return self.add("call.foreign", [status, proc], ["proc"], {"entity": P + ("exit_process" if WINDOWS else "exit_group")})


def load64(view: str, wide: bool = True) -> dict:
    """XAX function load64(ptr, VIEW, mem, b32 offset) -> (b64, ptr, VIEW, mem): the little-endian u64 at a byte offset.

    ``wide``: one checked 8-byte load on the byte view (XAX ADR-231, host contract r2).  Otherwise the pre-r2 form:
    eight 1-byte checked loads combined with multiplies and adds (kept to show both forms compute the same value)."""
    if wide:
        return {"name": f"load64_{view}", "params": ["ptr", view, "mem", "b32"], "returns": ["b64", "ptr", view, "mem"],
                "blocks": [{"params": ["ptr", view, "mem", "b32"],
                            "nodes": [["checked.load.bits.le", ["p0", "p3", "p2"], ["b64", "mem"], {"attrs": [8, 1]}]],
                            "end": ["ret", ["n0", "p0", "p1", "n0.r1"]]}]}
    nodes, mem = [], "p2"
    for k in range(8):
        base = len(nodes)
        nodes += [["add.wrap", ["p3", ["b32", k]], ["b32"]],
                  ["checked.load.bits.le", ["p0", f"n{base}", mem], ["b8", "mem"], {"attrs": [1, 1]}],
                  ["int.zero.extend", [f"n{base + 1}"], ["b64"]],
                  ["mul.wrap", [f"n{base + 2}", ["b64", 1 << (8 * k)]], ["b64"]]]
        mem = f"n{base + 1}.r1"
    terms = [f"n{4 * k + 3}" for k in range(8)]
    acc = terms[0]
    for term in terms[1:]:
        nodes.append(["add.wrap", [acc, term], ["b64"]])
        acc = f"n{len(nodes) - 1}"
    return {"name": f"load64_{view}", "params": ["ptr", view, "mem", "b32"], "returns": ["b64", "ptr", view, "mem"],
            "blocks": [{"params": ["ptr", view, "mem", "b32"], "nodes": nodes, "end": ["ret", [acc, "p0", "p1", mem]]}]}


def store64(view: str, wide: bool = True) -> dict:
    """XAX function store64(ptr, VIEW, mem, b32 offset, b64 x) -> (ptr, VIEW, mem): x as 8 little-endian bytes.

    ``wide``: one checked 8-byte store (ADR-231); otherwise eight 1-byte stores of x / 256^k."""
    if wide:
        return {"name": f"store64_{view}", "params": ["ptr", view, "mem", "b32", "b64"], "returns": ["ptr", view, "mem"],
                "blocks": [{"params": ["ptr", view, "mem", "b32", "b64"],
                            "nodes": [["checked.store.bits.le", ["p0", "p3", "p4", "p2"], ["mem"], {"attrs": [8, 1]}]],
                            "end": ["ret", ["p0", "p1", "n0"]]}]}
    nodes, mem = [], "p2"
    for k in range(8):
        base = len(nodes)
        nodes += [["udiv", ["p4", ["b64", 1 << (8 * k)]], ["b64"]],
                  ["int.truncate", [f"n{base}"], ["b8"]],
                  ["add.wrap", ["p3", ["b32", k]], ["b32"]],
                  ["checked.store.bits.le", ["p0", f"n{base + 2}", f"n{base + 1}", mem], ["mem"], {"attrs": [1, 1]}]]
        mem = f"n{base + 3}"
    return {"name": f"store64_{view}", "params": ["ptr", view, "mem", "b32", "b64"], "returns": ["ptr", view, "mem"],
            "blocks": [{"params": ["ptr", view, "mem", "b32", "b64"], "nodes": nodes, "end": ["ret", ["p0", "p1", mem]]}]}


ENTRY = ["proc", "fs", "mem", *IO]
_IO = "p3" if WINDOWS else None  # the entry's I/O memory proof


def _main(*blocks: dict) -> dict:
    return {"name": "main", "params": ENTRY, "returns": ["b32", *ENTRY], "blocks": list(blocks)}


def _ret(status, proc, fs, mem, io) -> list:
    return ["ret", [status, proc, fs, mem, *([io] if WINDOWS else [])]]


def poly_reduce(a: int, b: int, c: int, name: str = "polyreduce", wide: bool = True) -> dict:
    """Reads n little-endian u64 x_i from stdin; writes (sum_i a*x_i^2 + b*x_i + c mod 2^64, max_i x_i) as two u64."""
    start = _Nodes()
    ptr, view, mem = start.alloc("in", 4096, "p2")
    got, proc, fs, mem, io = start.transfer(False, "p0", "p1", ptr, ["b64", 4096], mem, _IO)
    count = start.add("int.truncate", [start.add("udiv", [got, ["b64", 8]], ["b64"])], ["b32"])
    done = _Nodes()
    out, out_view, mem_end = done.alloc("out", 16, "p4")
    stored = done.add("call.direct", [out, out_view, mem_end, ["b32", 0], "p6"], ["ptr", "out", "mem"], {"entity": {"fn": "store64_out"}})
    stored = done.add("call.direct", [stored, f"{stored}.r1", f"{stored}.r2", ["b32", 8], "p7"], ["ptr", "out", "mem"],
                      {"entity": {"fn": "store64_out"}})
    _, proc_end, fs_end, mem_end, io_end = done.transfer(True, "p0", "p1", stored, ["b64", 16], f"{stored}.r2",
                                                          "p9" if WINDOWS else None)
    mem_end = done.free(16, stored, f"{stored}.r1", mem_end)
    mem_end = done.free(4096, "p2", "p3", mem_end)
    exited = done.exit(["b32", 0], proc_end)
    return _package(name, [
        load64("in", wide), store64("out", wide),
        {"name": "term", "params": ["b64"], "returns": ["b64"], "blocks": [{"params": ["b64"], "nodes": [
            ["mul.wrap", ["p0", "p0"], ["b64"]],
            ["mul.wrap", ["n0", ["b64", a]], ["b64"]],
            ["mul.wrap", ["p0", ["b64", b]], ["b64"]],
            ["add.wrap", ["n1", "n2"], ["b64"]],
            ["add.wrap", ["n3", ["b64", c]], ["b64"]]], "end": ["ret", ["n4"]]}]},
        _main(
            {"params": ENTRY, "nodes": start,
             "end": ["br", 1, [proc, fs, ptr, view, mem, ["b32", 0], ["b64", 0], ["b64", 0], count, *([io] if WINDOWS else [])]]},
            {"params": LOOP, "nodes": [["int.compare", ["p5", "p8"], ["b1"], {"attrs": ["ult"]}]],
             "end": ["cbr", "n0", 2, ALL, 3, ALL]},
            {"params": LOOP, "nodes": [
                ["mul.wrap", ["p5", ["b32", 8]], ["b32"]],
                ["call.direct", ["p2", "p3", "p4", "n0"], ["b64", "ptr", "in", "mem"], {"entity": {"fn": "load64_in"}}],
                ["call.direct", ["n1"], ["b64"], {"entity": {"fn": "term"}}],
                ["add.wrap", ["p6", "n2"], ["b64"]],
                ["int.compare", ["n1", "p7"], ["b1"], {"attrs": ["ugt"]}],
                ["int.zero.extend", ["n4"], ["b64"]],
                ["sub.wrap", ["n1", "p7"], ["b64"]],
                ["mul.wrap", ["n5", "n6"], ["b64"]],
                ["add.wrap", ["p7", "n7"], ["b64"]],
                ["add.wrap", ["p5", ["b32", 1]], ["b32"]]],
             "end": ["br", 1, ["p0", "p1", "n1.r1", "n1.r2", "n1.r3", "n9", "n3", "n8", "p8", *ALL[9:]]]},
            {"params": LOOP, "nodes": done, "end": _ret(["b32", 0], exited, fs_end, mem_end, io_end)})])


def poly_reduce_oracle(a: int, b: int, c: int, xs: list[int]) -> tuple[int, int]:
    """Test oracle only (never used by the server)."""
    mask = (1 << 64) - 1
    return sum(a * x * x + b * x + c for x in xs) & mask, max(xs, default=0)


def _package(name: str, functions: list, types: dict | None = None) -> dict:
    return {"format": "xax-construct-v1", "platform": PLATFORM, "types": {**TYPES, **(types or {})},
            "functions": functions, "package": {"name": name, "entries": {"app": "main"}, "release": "app"}}


def spin() -> dict:
    """A process that never terminates (for wall-time/CPU limit and cancellation tests)."""
    end = _Nodes()
    exited = end.exit(["b32", 0], "p0")
    return _package("spin", [{"name": "main", "params": ["proc"], "returns": ["b32", "proc"], "blocks": [
        {"params": ["proc"], "nodes": [], "end": ["br", 1, ["p0", ["b64", 0]]]},
        {"params": ["proc", "b64"], "nodes": [["add.wrap", ["p1", ["b64", 1]], ["b64"]],
                                               ["int.compare", ["n0", ["b64", 0]], ["b1"], {"attrs": ["ne"]}]],
         "end": ["cbr", "n1", 1, ["p0", "n0"], 2, ["p0"]]},
        {"params": ["proc"], "nodes": end, "end": ["ret", [["b32", 0], exited]]}]}])


def open_file(path: bytes) -> dict:
    """Linux only: attempts openat(AT_FDCWD, path, O_RDONLY) and writes the raw 64-bit result (fd or -errno)."""
    assert not WINDOWS
    nodes = _Nodes()
    ptr, view, mem = nodes.alloc("in", 4096, "p2")
    for i, byte in enumerate(path + b"\0"):
        mem = nodes.add("checked.store.bits.le", [ptr, ["b32", i], ["b8", byte], mem], ["mem"], {"attrs": [1, 1]})
    name = nodes.add("pointer.cast", [ptr], ["linux.bytes_read"])
    opened = nodes.add("call.foreign", [["b32", (1 << 32) - 100], name, ["b32", 0], ["b32", 0], "p1", mem], ["b64", "fs", "mem"],
                       {"entity": "linux.openat"})
    out, out_view, mem = nodes.alloc("out", 16, f"{opened}.r2")
    stored = nodes.add("call.direct", [out, out_view, mem, ["b32", 0], opened], ["ptr", "out", "mem"], {"entity": {"fn": "store64_out"}})
    _, proc, fs, mem, _ = nodes.transfer(True, "p0", f"{opened}.r1", stored, ["b64", 8], f"{stored}.r2")
    mem = nodes.free(16, stored, f"{stored}.r1", mem)
    mem = nodes.free(4096, ptr, view, mem)
    exited = nodes.exit(["b32", 0], proc)
    return _package("openfile", [store64("out"), _main({"params": ["proc", "fs", "mem"], "nodes": nodes,
                                                         "end": ["ret", [["b32", 0], exited, fs, mem]]})])


def flood() -> dict:
    """Writes a 4096-byte zero buffer to stdout forever (output-quota test)."""
    loop = ["proc", "fs", "ptr", "in", "mem", *IO]
    start, body, end = _Nodes(), _Nodes(), _Nodes()
    ptr, view, mem = start.alloc("in", 4096, "p2")
    io = "p5" if WINDOWS else None
    wrote, proc, fs, mem_body, io_body = body.transfer(True, "p0", "p1", "p2", ["b64", 4096], "p4", io)
    more = body.add("int.compare", [wrote, ["b64", 0]], ["b1"], {"attrs": ["ne"]})
    state = [proc, fs, "p2", "p3", mem_body, *([io_body] if WINDOWS else [])]
    mem_end = end.free(4096, "p2", "p3", "p4")
    exited = end.exit(["b32", 0], "p0")
    return _package("flood", [_main(
        {"params": ENTRY, "nodes": start, "end": ["br", 1, ["p0", "p1", ptr, view, mem, *([_IO] if WINDOWS else [])]]},
        {"params": loop, "nodes": body, "end": ["cbr", more, 1, state, 2, state]},
        {"params": loop, "nodes": end, "end": _ret(["b32", 0], exited, "p1", mem_end, io)})])


def echo_argument() -> dict:
    """Linux only: writes argv[1] (at most 64 bytes) to stdout and exits with argc (linux.startup.*, XAX ADR-223)."""
    assert not WINDOWS
    nodes = _Nodes()
    ptr, view, mem = nodes.alloc("out64", 64, "p2")
    copied = nodes.add("call.foreign", [["b64", 1], ptr, mem], ["b64", "mem"], {"entity": "linux.startup.arg_copy"})
    _, proc, fs, mem, _ = nodes.transfer(True, "p0", "p1", ptr, copied, f"{copied}.r1")
    mem = nodes.free(64, ptr, view, mem)
    argc = nodes.add("int.truncate", [nodes.add("call.foreign", [], ["b64"], {"entity": "linux.startup.argc"})], ["b32"])
    exited = nodes.exit(argc, proc)
    return _package("echo1", [_main({"params": ["proc", "fs", "mem"], "nodes": nodes, "end": ["ret", [argc, exited, fs, mem]]})],
                    {"out64": {"view": 64}})


def echo_stdin() -> dict:
    """Copies up to 4096 bytes of stdin to stdout and exits with the byte count (both platforms)."""
    nodes = _Nodes()
    ptr, view, mem = nodes.alloc("in", 4096, "p2")
    got, proc, fs, mem, io = nodes.transfer(False, "p0", "p1", ptr, ["b64", 4096], mem, _IO)
    _, proc, fs, mem, io = nodes.transfer(True, proc, fs, ptr, got, mem, io)
    mem = nodes.free(4096, ptr, view, mem)
    status = nodes.add("int.truncate", [got], ["b32"])
    exited = nodes.exit(status, proc)
    return _package("echo", [_main({"params": ENTRY, "nodes": nodes, "end": _ret(status, exited, fs, mem, io)})])
