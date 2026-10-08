"""``xax-mcp-io-v1``: typed transport framing between tool arguments and an artifact's stdin/stdout bytes.

The construct carrier's process entry takes no machine parameters (``validate_process_entry``), so the only runtime
data channels a constructed Linux program has are the ``linux.read``/``linux.write`` system calls on fds 0 and 1
plus its exit status.  This module only converts typed integers to and from little-endian bytes; it never
interprets, combines or computes over the values.  The XAX program decides what the bytes mean.
"""

from __future__ import annotations

import base64

from .errors import ToolError

INT_TYPES = {"b8": 8, "b16": 16, "b32": 32, "b64": 64}


def encode_input(spec: dict | None, limit: int) -> bytes:
    if not spec:
        return b""
    if len(spec) != 1:
        raise ToolError("invalid_request", "input takes exactly one of ints, bytes_base64, text")
    (mode, value), = spec.items()
    if mode == "ints":
        out = bytearray()
        for item in value:
            width = INT_TYPES[item["type"]]
            number = item["value"]
            if not -(1 << (width - 1)) <= number < (1 << width):
                raise ToolError("invalid_request", f"{number} does not fit {item['type']}")
            out += (number & ((1 << width) - 1)).to_bytes(width // 8, "little")
        data = bytes(out)
    elif mode == "bytes_base64":
        try:
            data = base64.b64decode(value, validate=True)
        except ValueError:
            raise ToolError("invalid_request", "bytes_base64 is not valid base64") from None
    elif mode == "text":
        data = value.encode("utf-8")
    else:
        raise ToolError("invalid_request", f"unknown input mode {mode!r}")
    if len(data) > limit:
        raise ToolError("resource_limit", f"input is {len(data)} bytes; the limit is {limit}")
    return data


def decode_output(spec, data: bytes, inline: int) -> dict:
    """Project stdout bytes through the caller's declared layout.  A length mismatch is reported, not repaired."""
    if spec is None or spec == "bytes":
        shown = data[:inline]
        return {"mode": "bytes", "base64": base64.b64encode(shown).decode(), "length": len(data), "inline_truncated": len(data) > inline}
    if spec == "text":
        shown = data[:inline]
        return {"mode": "text", "text": shown.decode("utf-8", errors="replace"), "length": len(data), "inline_truncated": len(data) > inline}
    types = spec["ints"]
    expected = sum(INT_TYPES[t] // 8 for t in types)
    if len(data) != expected:
        return {"mode": "ints", "layout_matched": False, "expected_length": expected, "length": len(data),
                "base64": base64.b64encode(data[:inline]).decode()}
    values, offset = [], 0
    for t in types:
        width = INT_TYPES[t]
        raw = int.from_bytes(data[offset:offset + width // 8], "little")
        offset += width // 8
        item = {"type": t, "value": raw}
        if raw >> (width - 1):
            item["signed"] = raw - (1 << width)
        values.append(item)
    return {"mode": "ints", "layout_matched": True, "values": values, "length": len(data)}
