param(
  [Parameter(Mandatory = $true)]
  [string]$RootDir
)

$ErrorActionPreference = "Stop"

if (!(Test-Path -LiteralPath $RootDir)) {
  exit 0
}

$Pyproject = Join-Path $RootDir ".temporiki/pyproject.toml"
if (!(Test-Path -LiteralPath $Pyproject)) {
  exit 0
}

$RawDir = Join-Path $RootDir "raw"
if (!(Test-Path -LiteralPath $RawDir)) {
  exit 0
}

$StateDir = Join-Path $env:LOCALAPPDATA "temporiki"
$StateDir = Join-Path $StateDir "state"
New-Item -ItemType Directory -Force -Path $StateDir | Out-Null

$HashInput = [System.Text.Encoding]::UTF8.GetBytes($RootDir.ToLowerInvariant())
$Sha = [System.Security.Cryptography.SHA256]::Create()
$HashBytes = $Sha.ComputeHash($HashInput)
$HashHex = -join ($HashBytes | ForEach-Object { $_.ToString("x2") })
$StateFile = Join-Path $StateDir ("win-scheduler-" + $HashHex + ".json")

$LastRunTicks = 0L
if (Test-Path -LiteralPath $StateFile) {
  try {
    $State = Get-Content -LiteralPath $StateFile -Raw | ConvertFrom-Json
    if ($State.last_run_ticks) {
      $LastRunTicks = [int64]$State.last_run_ticks
    }
  } catch {
    $LastRunTicks = 0L
  }
}

$Measure = Get-ChildItem -LiteralPath $RawDir -Recurse -File -ErrorAction SilentlyContinue |
  Measure-Object -Property LastWriteTimeUtc -Maximum
$LatestTicks = 0L
if ($Measure.Maximum) {
  $LatestTicks = [int64]$Measure.Maximum.Ticks
}

if ($LatestTicks -le $LastRunTicks) {
  exit 0
}

Push-Location $RootDir
try {
  & uv --project ".temporiki" run temporiki palace-event --root "$RootDir" | Out-Null
} finally {
  Pop-Location
}

@{
  last_run_ticks = [int64](Get-Date).ToUniversalTime().Ticks
} | ConvertTo-Json | Set-Content -LiteralPath $StateFile -Encoding UTF8
