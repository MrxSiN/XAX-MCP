# ADR-0006: Adopt XAX's host contract, process contract, and startup entities

**Status:** accepted (0.2.0)

**Context.** Upstream XAX now publishes `xax-host-contract-v1` (`xax_contract`, ADR-224), the process contract
`linux-x86_64-process-v1` (ADR-223), and `linux.startup.*` carrier entities (ADR-222). It also memoizes
component-store verification (ADR-221). These were proposals P1, P2, P3 and P5 from this repository.

**Decision.** Pin the commit that contains them. Require `xax-host-contract-v1` r≥1 and an empty
`xax_contract.missing()` at startup, so a build without the contract is `incompatible`. Report the contract and
the process contract in `xax_capabilities`. Add the `argv` input mode: the strings follow a `--` separator in
the sandbox launcher's argv and become the program's `argv[1:]`, with no shell involved.

**Consequences.** XAX-MCP 0.2.0 no longer runs against `01ad841`. The first-call delay with a warm cache
falls from about 25 s to about 3 s.
