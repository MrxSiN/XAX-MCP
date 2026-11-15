# External test orchestration only: the native server and the native XAX compiler do all the work.
# 1. Replays the capability transaction from gen3 (native edit + verify per batch); the result must equal gen4.
#    (The default CI job rebuilds gen4 and the launcher twice and compares them with native/release-status.json.)
# 2. Through the deployed server: builds the minimal libxposed module, edits it with xax_construct, builds again,
#    rejects the stale record and reports android-libxposed with the acd4046 pin. Each APK and the published store
#    must equal XAX's own build of the same store byte for byte.
# Usage: $env:XAXC = <seed named by native/xax-dependency.json>; powershell -File tests/android-libxposed/check.ps1
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Set-Location $repo
$compiler = (Resolve-Path $env:XAXC).Path
$dependency = Get-Content native/xax-dependency.json -Raw | ConvertFrom-Json
if ((Get-FileHash -LiteralPath $compiler).Hash.ToLowerInvariant() -ne $dependency.seed_sha256) { throw 'Wrong XAX seed' }
function Identity($Row) { if ((Get-FileHash -LiteralPath $Row.path).Hash.ToLowerInvariant() -ne $Row.sha256 -or (Get-Item -LiteralPath $Row.path).Length -ne $Row.bytes) { throw "Identity differs: $($Row.path)" } }
function Same($Actual, $Expected) { if ((Get-FileHash -LiteralPath $Actual).Hash -ne (Get-FileHash -LiteralPath $Expected).Hash) { throw "Bytes differ: $Actual vs $Expected" } }
function Native([string[]]$Arguments) { & $compiler @Arguments; if ($LASTEXITCODE -ne 0) { throw "Native compiler rejected/declined: $($Arguments[0]) ($LASTEXITCODE)" } }
$out = Join-Path $repo 'build/android-libxposed'
if (Test-Path $out) { Remove-Item -Recurse -Force $out }
New-Item -ItemType Directory -Force $out | Out-Null

# 1. Transaction replay.
$manifest = Get-Content native/transactions/20261115-android-libxposed/manifest.json -Raw | ConvertFrom-Json
Identity $manifest.base
$current = "$out/current.xax"; Copy-Item -LiteralPath $manifest.base.path -Destination $current
foreach ($record in $manifest.records) {
  Identity $record
  Native @('edit', $current, $record.path, "$out/next.xax")
  Native @('verify', "$out/next.xax", "$out/verify.diag")
  if ((Get-FileHash -LiteralPath "$out/next.xax").Hash.ToLowerInvariant() -ne $record.result.sha256) { throw "Replay differs after $($record.path)" }
  Move-Item -LiteralPath "$out/next.xax" -Destination $current -Force
}
Identity $manifest.final; Same $current $manifest.final.path

# 2. The libxposed module through the deployed server.
$server = Join-Path $repo 'native/xax-mcp-native.exe'
$fixtures = Get-Content tests/android-libxposed/manifest.json -Raw | ConvertFrom-Json
foreach ($row in @($fixtures.base, $fixtures.base_apk, $fixtures.record, $fixtures.edited, $fixtures.edited_apk, $fixtures.session)) { Identity $row }
function Session([string]$Name, [int]$Lines) {
  $work = Join-Path $out $Name
  New-Item -ItemType Directory -Force $work | Out-Null
  $env:XAX_MCP_COMPILER = $compiler
  $env:XAX_MCP_STORE = Join-Path $repo $fixtures.base.path
  $env:XAX_MCP_WORK = $work
  $responses = @(Get-Content $fixtures.session.path -TotalCount $Lines | & $server)
  if ($LASTEXITCODE -ne 0) { throw 'Native server failed' }
  $byId = @{}
  foreach ($line in $responses) { $response = $line | ConvertFrom-Json; $byId[[int]$response.id] = $response.result }
  return @{ work = $work; results = $byId }
}
function Ok($Result, [string]$What) { if ($Result.isError -or -not $Result.structuredContent.ok) { throw "$What failed: $($Result.content[0].text)" } }

$first = Session 'build' 3
Ok $first.results[2] 'xax_build'
if ($first.results[2].structuredContent.root -ne $fixtures.base.root) { throw 'Build root differs' }
Same (Join-Path $first.work 'artifact.exe') $fixtures.base_apk.path

$second = Session 'construct' 7
Ok $second.results[2] 'first xax_build'
Ok $second.results[3] 'xax_construct'
if ($second.results[3].structuredContent.root -ne $fixtures.edited.root) { throw 'Constructed root differs' }
Same (Join-Path $second.work 'current.xax') $fixtures.edited.path
Ok $second.results[4] 'second xax_build'
if ($second.results[4].structuredContent.root -ne $fixtures.edited.root) { throw 'Edited build root differs' }
Same (Join-Path $second.work 'artifact.exe') $fixtures.edited_apk.path
if (-not $second.results[5].isError) { throw 'Stale record was not rejected' }
Same (Join-Path $second.work 'current.xax') $fixtures.edited.path
$capabilities = $second.results[6]
Ok $capabilities 'xax_capabilities'
if (($capabilities.content[0].text | ConvertFrom-Json).xax.pinned_commit -ne $capabilities.structuredContent.xax.pinned_commit) { throw 'Capability text and structured content differ' }
if ($capabilities.structuredContent.xax.pinned_commit -ne $dependency.commit) { throw 'Capabilities report the wrong XAX pin' }
$libxposed = @($capabilities.structuredContent.targets | Where-Object { $_.target -eq 'android-libxposed' })
if ($libxposed.Count -ne 1 -or $libxposed[0].execute -ne $false) { throw 'Capabilities do not report android-libxposed' }
Write-Output 'android-libxposed: 4 records replayed; build, construct, rebuild, stale rejection and capabilities match'
