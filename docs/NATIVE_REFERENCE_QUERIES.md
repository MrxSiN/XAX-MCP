# Public reference queries

This contract applies to the experimental native control preview. The default
Gen3 server retains its older schema. The executable schema for this preview is
[`schemas/tools-v3.json`](../schemas/tools-v3.json).

Start with `xax_capabilities` to inspect the compiler identity and granted rights.
The host chooses the workspace; query arguments cannot change paths or authority.

```json
{"select":"objects","object_kind":3,"limit":1}
```

This locates function CIDs through the public kind tag 3. Kind 7 denotes a graph
fragment. Both tags are exercised by the retained fixture. Objects are visited in
the compiler record's CID order. Object rows contain `cid`, `kind` and
`referenceCount`; they do not imply an entry function or a textual name.

Repeat the same selectors and add the returned cursor to fetch another page:

```json
{"select":"objects","object_kind":3,"limit":1,"cursor":{"root":"<returned root CID>","offset":1}}
```

Cursors bind to the current root. A changed root returns `cursor_root_mismatch`.
The offset counts matching rows. Clients must repeat selectors; a cursor is not
an opaque session handle or a binding to the previous filter. An offset beyond
the available matching inventory is rejected.

```json
{"select":"entity","cid":"<function CID>"}
{"select":"dependencies","cid":"<function CID>","limit":2}
{"select":"users","cid":"<entity CID>","limit":2}
{"select":"neighborhood","cid":"<body graph CID>","limit":1}
```

`entity` returns the matching object descriptor. A missing CID returns
`not_found` only when the inventory is complete; otherwise it returns
`inspection_incomplete`. `dependencies` selects outgoing reference edges, `users`
selects incoming edges, and `neighborhood` selects their union at one hop. Edge
rows contain `source` and `target`. `object_kind` filters the source object in
all edge queries. It never invents a role for an edge.

To inspect an unfamiliar multi-function program, page its function objects,
follow each function's dependencies, look up the referenced kinds, then page a
body graph's neighborhood. The retained fixture independently checks that two
of its discovered graph references are actual native `CALL_DIRECT` uses. The
public record itself does not label calls, operands or other semantic roles.

`limit` is an integer from 1 through 64, defaulting to 16. CID strings accept
uppercase/lowercase hexadecimal and normal JSON escaping. Numeric arguments are
validated by value, so whole-valued forms such as `1.0` and `10e-1` are accepted;
fractions, negative nonzero values and values outside each field's range are
rejected. Unknown properties, duplicate fields and invalid selector combinations
are rejected. `objects` does not accept `cid`; the other selectors require it.

Responses include `ok`, `root`, `selection`, `rows`, `nextCursor`,
`inventoryComplete` and `complete`. At most 4,194,304 public inspection bytes are
read. Incomplete records are not emitted. A truncated inventory can end with
`nextCursor:null` and `complete:false`: there is no continuation beyond that
prefix. A page with more available rows returns a root-bound cursor. Result
rows and the fixed row formats bound each selected response independently of
the inventory's total edge count.

`{}` retains the legacy bounded root/size/first-function/inventory response.
`xax_workspace` still takes no arguments. Typed function signatures, operations,
effect facts, deeper semantic traversals and candidate comparisons need the
upstream inspection extension described below; they are not synthesized from
canonical-store internals.

The smallest required upstream extension is a verified public, root-bound
inspection API with explicit reference roles, function signatures, block and
operation records, typed/effect facts, bounded result budgets and continuation
over the complete inventory. Its page identity and completeness must be
independently tested against canonical programs before integration or repinning.
The dependency remains XAX-MCP to XAX.
