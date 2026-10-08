"""xax-construct-v1 carriers used by the tests.  They are typed semantic-graph requests sent through MCP exactly as
an agent would send them; the server has no knowledge of them.  Python here only *writes the request*; the
computation is performed by the XAX-generated executable."""

from __future__ import annotations

TYPES = {"mem": "linux.memory_effect", "proc": "linux.process_effect", "fs": "linux.filesystem_effect",
         "ptr": "linux.bytes_rw", "in": {"view": 4096}, "out": {"view": 16}}
LOOP = ["proc", "fs", "ptr", "in", "mem", "b32", "b64", "b64", "b32"]
ALL = [f"p{i}" for i in range(9)]


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


def poly_reduce(a: int, b: int, c: int, name: str = "polyreduce", wide: bool = True) -> dict:
    """Reads n little-endian u64 x_i from stdin; writes (sum_i a*x_i^2 + b*x_i + c mod 2^64, max_i x_i) as two u64."""
    return {
        "format": "xax-construct-v1", "platform": "linux-x86_64", "types": dict(TYPES),
        "functions": [
            load64("in", wide), store64("out", wide),
            {"name": "term", "params": ["b64"], "returns": ["b64"], "blocks": [{"params": ["b64"], "nodes": [
                ["mul.wrap", ["p0", "p0"], ["b64"]],
                ["mul.wrap", ["n0", ["b64", a]], ["b64"]],
                ["mul.wrap", ["p0", ["b64", b]], ["b64"]],
                ["add.wrap", ["n1", "n2"], ["b64"]],
                ["add.wrap", ["n3", ["b64", c]], ["b64"]]], "end": ["ret", ["n4"]]}]},
            {"name": "main", "params": ["proc", "fs", "mem"], "returns": ["b32", "proc", "fs", "mem"], "blocks": [
                {"params": ["proc", "fs", "mem"], "nodes": [
                    ["call.foreign", [["b64", 4096], "p2"], ["ptr", "linux.heap_owner", "mem"], {"entity": "linux.mmap_anonymous"}],
                    ["heap.view", ["n0", "n0.r1", "n0.r2"], ["ptr", "in", "mem"], {"attrs": [4096, 1]}],
                    ["call.foreign", [["b32", 0], "n1", ["b64", 4096], "p1", "n1.r2"], ["b64", "fs", "mem"], {"entity": "linux.read"}],
                    ["udiv", ["n2", ["b64", 8]], ["b64"]],
                    ["int.truncate", ["n3"], ["b32"]]],
                 "end": ["br", 1, ["p0", "n2.r1", "n1", "n1.r1", "n2.r2", ["b32", 0], ["b64", 0], ["b64", 0], "n4"]]},
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
                 "end": ["br", 1, ["p0", "p1", "n1.r1", "n1.r2", "n1.r3", "n9", "n3", "n8", "p8"]]},
                {"params": LOOP, "nodes": [
                    ["call.foreign", [["b64", 16], "p4"], ["ptr", "linux.heap_owner", "mem"], {"entity": "linux.mmap_anonymous"}],
                    ["heap.view", ["n0", "n0.r1", "n0.r2"], ["ptr", "out", "mem"], {"attrs": [16, 1]}],
                    ["call.direct", ["n1", "n1.r1", "n1.r2", ["b32", 0], "p6"], ["ptr", "out", "mem"], {"entity": {"fn": "store64_out"}}],
                    ["call.direct", ["n2", "n2.r1", "n2.r2", ["b32", 8], "p7"], ["ptr", "out", "mem"], {"entity": {"fn": "store64_out"}}],
                    ["pointer.cast", ["n3"], ["linux.bytes_read"]],
                    ["call.foreign", [["b32", 1], "n4", ["b64", 16], "p1", "n3.r2"], ["b64", "fs", "mem"], {"entity": "linux.write"}],
                    ["call.foreign", ["n3", "n3.r1", "n5.r2"], ["b64", "mem"], {"entity": {"linux.munmap_view": ["ptr", 16]}}],
                    ["call.foreign", ["p2", "p3", "n6.r1"], ["b64", "mem"], {"entity": {"linux.munmap_view": ["ptr", 4096]}}],
                    ["call.foreign", [["b32", 0], "p0"], ["proc"], {"entity": "linux.exit_group"}]],
                 "end": ["ret", [["b32", 0], "n8", "n5.r1", "n7.r1"]]}]}],
        "package": {"name": name, "entries": {"app": "main"}, "release": "app"}}


def poly_reduce_oracle(a: int, b: int, c: int, xs: list[int]) -> tuple[int, int]:
    """Test oracle only (never used by the server)."""
    mask = (1 << 64) - 1
    return sum(a * x * x + b * x + c for x in xs) & mask, max(xs, default=0)


def _package(name: str, functions: list, types: dict | None = None) -> dict:
    return {"format": "xax-construct-v1", "platform": "linux-x86_64", "types": {**TYPES, **(types or {})},
            "functions": functions, "package": {"name": name, "entries": {"app": "main"}, "release": "app"}}


def spin() -> dict:
    """A process that never terminates (for wall-time/CPU limit and cancellation tests)."""
    return _package("spin", [{"name": "main", "params": ["proc"], "returns": ["b32", "proc"], "blocks": [
        {"params": ["proc"], "nodes": [], "end": ["br", 1, ["p0", ["b64", 0]]]},
        {"params": ["proc", "b64"], "nodes": [["add.wrap", ["p1", ["b64", 1]], ["b64"]],
                                               ["int.compare", ["n0", ["b64", 0]], ["b1"], {"attrs": ["ne"]}]],
         "end": ["cbr", "n1", 1, ["p0", "n0"], 2, ["p0"]]},
        {"params": ["proc"], "nodes": [["call.foreign", [["b32", 0], "p0"], ["proc"], {"entity": "linux.exit_group"}]],
         "end": ["ret", [["b32", 0], "n0"]]}]}])


def open_file(path: bytes) -> dict:
    """Attempts openat(AT_FDCWD, path, O_RDONLY) and writes the raw 64-bit kernel result (fd or -errno) to stdout."""
    stores = [["checked.store.bits.le", ["n1", ["b32", i], ["b8", byte], "n1.r2" if i == 0 else f"n{1 + i}"], ["mem"], {"attrs": [1, 1]}]
              for i, byte in enumerate(path + b"\0")]
    last = 1 + len(stores)  # node index of the last store
    nodes = [
        ["call.foreign", [["b64", 4096], "p2"], ["ptr", "linux.heap_owner", "mem"], {"entity": "linux.mmap_anonymous"}],
        ["heap.view", ["n0", "n0.r1", "n0.r2"], ["ptr", "in", "mem"], {"attrs": [4096, 1]}],
        *stores,
        ["pointer.cast", ["n1"], ["linux.bytes_read"]],
        ["call.foreign", [["b32", (1 << 32) - 100], f"n{last + 1}", ["b32", 0], ["b32", 0], "p1", f"n{last}"],
         ["b64", "fs", "mem"], {"entity": "linux.openat"}],
        ["call.foreign", [["b64", 16], f"n{last + 2}.r2"], ["ptr", "linux.heap_owner", "mem"], {"entity": "linux.mmap_anonymous"}],
        ["heap.view", [f"n{last + 3}", f"n{last + 3}.r1", f"n{last + 3}.r2"], ["ptr", "out", "mem"], {"attrs": [16, 1]}],
        ["call.direct", [f"n{last + 4}", f"n{last + 4}.r1", f"n{last + 4}.r2", ["b32", 0], f"n{last + 2}"], ["ptr", "out", "mem"],
         {"entity": {"fn": "store64_out"}}],
        ["pointer.cast", [f"n{last + 5}"], ["linux.bytes_read"]],
        ["call.foreign", [["b32", 1], f"n{last + 6}", ["b64", 8], f"n{last + 2}.r1", f"n{last + 5}.r2"], ["b64", "fs", "mem"],
         {"entity": "linux.write"}],
        ["call.foreign", [f"n{last + 5}", f"n{last + 5}.r1", f"n{last + 7}.r2"], ["b64", "mem"], {"entity": {"linux.munmap_view": ["ptr", 16]}}],
        ["call.foreign", ["n1", "n1.r1", f"n{last + 8}.r1"], ["b64", "mem"], {"entity": {"linux.munmap_view": ["ptr", 4096]}}],
        ["call.foreign", [["b32", 0], "p0"], ["proc"], {"entity": "linux.exit_group"}],
    ]
    main = {"name": "main", "params": ["proc", "fs", "mem"], "returns": ["b32", "proc", "fs", "mem"],
            "blocks": [{"params": ["proc", "fs", "mem"], "nodes": nodes,
                        "end": ["ret", [["b32", 0], f"n{last + 10}", f"n{last + 7}.r1", f"n{last + 9}.r1"]]}]}
    return _package("openfile", [store64("out"), main])


def flood() -> dict:
    """Writes a 4096-byte zero buffer to stdout forever (output-quota test)."""
    loop = ["proc", "fs", "ptr", "in", "mem"]
    return _package("flood", [{"name": "main", "params": ["proc", "fs", "mem"], "returns": ["b32", "proc", "fs", "mem"], "blocks": [
        {"params": ["proc", "fs", "mem"], "nodes": [
            ["call.foreign", [["b64", 4096], "p2"], ["ptr", "linux.heap_owner", "mem"], {"entity": "linux.mmap_anonymous"}],
            ["heap.view", ["n0", "n0.r1", "n0.r2"], ["ptr", "in", "mem"], {"attrs": [4096, 1]}]],
         "end": ["br", 1, ["p0", "p1", "n1", "n1.r1", "n1.r2"]]},
        {"params": loop, "nodes": [
            ["pointer.cast", ["p2"], ["linux.bytes_read"]],
            ["call.foreign", [["b32", 1], "n0", ["b64", 4096], "p1", "p4"], ["b64", "fs", "mem"], {"entity": "linux.write"}],
            ["int.compare", ["n1", ["b64", 0]], ["b1"], {"attrs": ["ne"]}]],
         "end": ["cbr", "n2", 1, ["p0", "n1.r1", "p2", "p3", "n1.r2"], 2, ["p0", "n1.r1", "p2", "p3", "n1.r2"]]},
        {"params": loop, "nodes": [
            ["call.foreign", ["p2", "p3", "p4"], ["b64", "mem"], {"entity": {"linux.munmap_view": ["ptr", 4096]}}],
            ["call.foreign", [["b32", 0], "p0"], ["proc"], {"entity": "linux.exit_group"}]],
         "end": ["ret", [["b32", 0], "n1", "p1", "n0.r1"]]}]}])


def echo_argument() -> dict:
    """Writes argv[1] (at most 64 bytes) to stdout and exits with argc (linux.startup.* entities, XAX ADR-223)."""
    return _package("echo1", [{"name": "main", "params": ["proc", "fs", "mem"], "returns": ["b32", "proc", "fs", "mem"], "blocks": [
        {"params": ["proc", "fs", "mem"], "nodes": [
            ["call.foreign", [["b64", 64], "p2"], ["ptr", "linux.heap_owner", "mem"], {"entity": "linux.mmap_anonymous"}],
            ["heap.view", ["n0", "n0.r1", "n0.r2"], ["ptr", "out64", "mem"], {"attrs": [64, 1]}],
            ["call.foreign", [["b64", 1], "n1", "n1.r2"], ["b64", "mem"], {"entity": "linux.startup.arg_copy"}],
            ["pointer.cast", ["n1"], ["linux.bytes_read"]],
            ["call.foreign", [["b32", 1], "n3", "n2", "p1", "n2.r1"], ["b64", "fs", "mem"], {"entity": "linux.write"}],
            ["call.foreign", ["n1", "n1.r1", "n4.r2"], ["b64", "mem"], {"entity": {"linux.munmap_view": ["ptr", 64]}}],
            ["call.foreign", [], ["b64"], {"entity": "linux.startup.argc"}],
            ["int.truncate", ["n6"], ["b32"]],
            ["call.foreign", ["n7", "p0"], ["proc"], {"entity": "linux.exit_group"}]],
         "end": ["ret", ["n7", "n8", "n4.r1", "n5.r1"]]}]}], {"out64": {"view": 64}})
