# External test orchestration only: the native server and the native XAX compiler do all the work.
# Builds the minimal libxposed module through xax_build, edits it through xax_construct, builds again, and compares
# each APK and the published store byte for byte with XAX's own build of the same store.
# Usage: $env:XAXC = <seed named by native/android-libxposed-dependency.json>; powershell -File tests/android-libxposed/check.ps1
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Set-Location $repo
$dependency = Get-Content native/android-libxposed-dependency.json -Raw | ConvertFrom-Json
if ((Get-FileHash -LiteralPath $env:XAXC).Hash.ToLowerInvariant() -ne $dependency.seed_sha256) { throw 'Wrong android-libxposed compiler seed' }
$fixtures = Get-Content tests/android-libxposed/manifest.json -Raw | ConvertFrom-Json
foreach ($row in @($fixtures.base, $fixtures.base_apk, $fixtures.record, $fixtures.edited, $fixtures.edited_apk, $fixtures.session)) {
  if ((Get-FileHash -LiteralPath $row.path).Hash.ToLowerInvariant() -ne $row.sha256 -or (Get-Item -LiteralPath $row.path).Length -ne $row.bytes) { throw "Identity differs: $($row.path)" }
}
function Same($Actual, $Expected) { if ((Get-FileHash -LiteralPath $Actual).Hash -ne (Get-FileHash -LiteralPath $Expected).Hash) { throw "Bytes differ: $Actual vs $Expected" } }
function Session([string]$Name, [int]$Lines) {
  $work = Join-Path $repo "build/android-libxposed/$Name"
  if (Test-Path $work) { Remove-Item -Recurse -Force $work }
  New-Item -ItemType Directory -Force $work | Out-Null
  $env:XAX_MCP_COMPILER = (Resolve-Path $env:XAXC).Path
  $env:XAX_MCP_STORE = Join-Path $repo $fixtures.base.path
  $env:XAX_MCP_WORK = $work
  $responses = @(Get-Content $fixtures.session.path -TotalCount $Lines | & (Join-Path $repo 'native/xax-mcp-native.exe'))
  if ($LASTEXITCODE -ne 0) { throw 'Native server failed' }
  $byId = @{}
  foreach ($line in $responses) { $response = $line | ConvertFrom-Json; $byId[[int]$response.id] = $response.result }
  return @{ work = $work; results = $byId }
}
function Ok($Result, [string]$What) { if ($Result.isError -or -not $Result.structuredContent.ok) { throw "$What failed: $($Result.content[0].text)" } }

# Build the unedited module.
$first = Session 'build' 3
Ok $first.results[2] 'xax_build'
if ($first.results[2].structuredContent.root -ne $fixtures.base.root) { throw 'Build root differs' }
Same (Join-Path $first.work 'artifact.exe') $fixtures.base_apk.path

# Construct (exact-root edit, native verify, publish), build the edited module, then replay the stale record.
$second = Session 'construct' 6
Ok $second.results[2] 'first xax_build'
Ok $second.results[3] 'xax_construct'
if ($second.results[3].structuredContent.root -ne $fixtures.edited.root) { throw 'Constructed root differs' }
Same (Join-Path $second.work 'current.xax') $fixtures.edited.path
Ok $second.results[4] 'second xax_build'
if ($second.results[4].structuredContent.root -ne $fixtures.edited.root) { throw 'Edited build root differs' }
Same (Join-Path $second.work 'artifact.exe') $fixtures.edited_apk.path
if (-not $second.results[5].isError) { throw 'Stale record was not rejected' }
Same (Join-Path $second.work 'current.xax') $fixtures.edited.path
Write-Output 'android-libxposed: build, construct, rebuild and stale rejection match XAX''s own builds byte for byte'
