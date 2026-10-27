# Install and rebuild on Windows

This is a native-only **preview**, version 0.9.0+native. Use Windows x86-64. Full release readiness remains false;
read [the remaining gates](WINDOWS_READINESS.md) before granting mutation or execution.

## Preview ZIP

Download `xax-mcp-0.9.0-windows-x86_64-preview` from a successful
[native-windows workflow run](https://github.com/MrxSiN/XAX-MCP/actions/workflows/ci.yml) and extract its inner ZIP
to a private directory such as `D:/Tools/XAX-MCP`. Keep `native/xax-mcp-native.exe` and `native/xax-mcp-sandbox.exe`
together. The ZIP has the pinned native compiler at `xax/xaxc-windows-x86_64.exe`; no language runtime is required.

Check file identities against `native/release-status.json` and `native/xax-dependency.json`. The compiler seed's
SHA-256 must be `aa72234d6dd8a111efde62b47ced8449a482c4c5506d876714ff7fbe0968ab79`.
The package includes canonical sources and provenance; no PowerShell production wrapper is installed.

## Source checkout

```powershell
git clone https://github.com/MrxSiN/XAX-MCP D:/Tools/XAX-MCP
git clone https://github.com/MrxSiN/XAX D:/Tools/XAX
git -C D:/Tools/XAX checkout --detach af376e8a8a1ac5635bcad459cb7063ef0b326430
```

Do not substitute moving upstream `main`. The dependency contract is `xax-native-file-v1`; only the pinned seed is
tested. XAX stays independently usable and contains no MCP application dependency.

## Launch

The following is host setup/launch orchestration, not server implementation. Choose a private work directory under
your own account. Tool parameters cannot set these paths. For the ZIP, change the compiler path to
`D:/Tools/XAX-MCP/xax/xaxc-windows-x86_64.exe`.

```powershell
New-Item -ItemType Directory -Force D:/Private/XAX-MCP-work | Out-Null
$env:XAX_MCP_COMPILER = 'D:/Tools/XAX/compiler/bootstrap/windows/xaxc-windows-x86_64.exe'
$env:XAX_MCP_STORE = 'D:/Tools/XAX-MCP/native/xax-mcp-seed.xax'
$env:XAX_MCP_WORK = 'D:/Private/XAX-MCP-work'
& D:/Tools/XAX-MCP/native/xax-mcp-native.exe --read-only
```

Use no flag to grant the default read/mutate/build rights. Add `--allow-execute` only when the host owner grants
sandboxed execution. Closing stdin ends the server and releases its work-directory lease. Supported policy flags:
`--read-only`, `--allow-execute`, `--deny RIGHT` or `--deny=RIGHT` (`read`, `mutate`, `build`, `execute`).
`--no-warm-server` is a compatibility no-op. Unknown flags exit 2. Limits are fixed, not configurable per call.

Keep compiler, seed and work-directory permissions under host control. Different clients should use different
private directories. A second live server targeting the same directory gets `workspace_busy`; retry after the owner
exits. The OS removes its lock on crash. No public tool opens paths or grants shell, network or arbitrary effects.

## Reproduce construction/build/run

From the checkout, in a **fresh** work directory with the environment above:

```powershell
Get-Content D:/Tools/XAX-MCP/examples/native-arithmetic/requests.ndjson |
  & D:/Tools/XAX-MCP/native/xax-mcp-native.exe --allow-execute
```

The replay discovers tools, runs the seed (40), constructs seven exact-root edits, builds/runs the new graph (136),
repeats it, and tests expected rejection cases. The full client fixture/assertions are
`tests/protocol/native-sessions.json`. The generic external client uses PowerShell for transport only; native XAX
performs the computation, semantic mutation, verification, build and confinement.

## Rebuild native programs

Use the checkout layout below; for the ZIP point `$xaxCompiler` at its `xax` directory. Stop on **any** nonzero
compiler exit. In particular status 2 is a decline, never success.

```powershell
$xaxCompiler = 'D:/Tools/XAX/compiler/bootstrap/windows/xaxc-windows-x86_64.exe'
Set-Location D:/Tools/XAX-MCP
New-Item -ItemType Directory -Force build/rebuild | Out-Null
& $xaxCompiler verify native/xax-mcp-native-gen1.xax build/rebuild/server.diag
if ($LASTEXITCODE -ne 0) { throw 'Server verification rejected/declined' }
& $xaxCompiler resolve native/xax-mcp-native-gen1.xax build/rebuild/server-snapshot.xax
if ($LASTEXITCODE -ne 0) { throw 'Server resolve rejected/declined' }
& $xaxCompiler build build/rebuild/server-snapshot.xax build/rebuild/server.exe build/rebuild/server.prov
if ($LASTEXITCODE -ne 0) { throw 'Server build rejected/declined' }
Get-FileHash native/xax-mcp-native.exe,build/rebuild/server.exe
& $xaxCompiler verify native/xax-mcp-sandbox-gen0.xax build/rebuild/sandbox.diag
if ($LASTEXITCODE -ne 0) { throw 'Sandbox verification rejected/declined' }
& $xaxCompiler build native/xax-mcp-sandbox-gen0.xax build/rebuild/sandbox.exe build/rebuild/sandbox.prov
if ($LASTEXITCODE -ne 0) { throw 'Sandbox build rejected/declined' }
Get-FileHash native/xax-mcp-sandbox.exe,build/rebuild/sandbox.exe
```

Both pairs must match byte for byte. CI additionally replays all 46 semantic transactions from the seed and compares
the canonical source, resolved snapshot, executable and provenance. The trusted native compiler seed has a
historical Python bootstrap, disclosed upstream; these application rebuilds invoke only native XAX.

## Remove

Remove the `xax` registration from your agent host ([host commands](HOSTS.md)), close its running STDIO process,
and delete only the installation/private work directories you created. No service or interpreter is installed.
