# Native STDIO smoke fixture

`readonly.requests.ndjson` is non-authoritative MCP transport data. With no compiler/decoder environment grants,
feed it to `native/xax-mcp-native.exe --read-only`; compare the 15 response lines against
`readonly.responses.ndjson` in order. The initialization notification has no response. Malformed JSON produces
`-32700`, and the following ping confirms framing recovery. The fixture also covers eight-tool discovery,
capabilities, unknown method/tool, forbidden mutation/build/execution and unsupported result handles.

The expected responses preserve the unchanged 0.8.0 wire behavior. This is a regression smoke test, not complete
MCP conformance, schema-validation coverage, SDK interoperability or an XAX compiler verification test.
