$ErrorActionPreference = "Stop"

$port = 8020
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$reviewRoot = Join-Path $root "tools\dino-review"
. (Join-Path $reviewRoot "review-launcher-lib.ps1")
$reviewConfig = Get-DinoReviewConfig -ReviewRoot $reviewRoot
$atlasUrl = "http://127.0.0.1:$port/index.html"

$listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue |
  Select-Object -First 1

if ($listener) {
  if (-not (Test-DinoAtlasHealth -Url $atlasUrl)) {
    $description = Get-DinoReviewListenerDescription -Listener $listener
    throw "Port $port is occupied, but it is not the Dino Atlas server. $description"
  }
} else {
  $python = (Get-Command python -ErrorAction Stop).Source
  $atlasStdout = Join-Path $reviewConfig.DataDir "atlas-server.stdout.log"
  $atlasStderr = Join-Path $reviewConfig.DataDir "atlas-server.stderr.log"
  $atlasProcess = Start-Process -FilePath $python -ArgumentList @("-m", "http.server", "$port", "--bind", "127.0.0.1") `
    -WorkingDirectory $root -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput $atlasStdout -RedirectStandardError $atlasStderr

  $atlasReady = $false
  for ($attempt = 0; $attempt -lt 20; $attempt += 1) {
    Start-Sleep -Milliseconds 300
    $atlasProcess.Refresh()
    if ($atlasProcess.HasExited) { break }
    if (Test-DinoAtlasHealth -Url $atlasUrl) {
      $atlasReady = $true
      break
    }
  }
  if (-not $atlasReady) {
    if (-not $atlasProcess.HasExited) {
      Stop-Process -Id $atlasProcess.Id -Force -ErrorAction SilentlyContinue
    }
    $details = if (Test-Path -LiteralPath $atlasStderr) {
      (Get-Content -LiteralPath $atlasStderr -Encoding UTF8 -Tail 20 -ErrorAction SilentlyContinue) -join [Environment]::NewLine
    } else { "No stderr log was written." }
    throw "Dino Atlas did not become healthy on port $port.`n$details"
  }
  Write-Host "Dino Atlas started (PID $($atlasProcess.Id))."
}

$reviewListener = Get-DinoReviewListener -Port $reviewConfig.Port

if ($reviewListener) {
  if (-not (Test-DinoReviewHealth -Config $reviewConfig)) {
    $description = Get-DinoReviewListenerDescription -Listener $reviewListener
    throw "Port $($reviewConfig.Port) is occupied, but it is not the authenticated Dino review server for this local key. $description"
  }
  Save-DinoReviewKey -Config $reviewConfig
} else {
  Save-DinoReviewKey -Config $reviewConfig
  $reviewProcess = Start-DinoReviewBackgroundServer -ReviewRoot $reviewRoot -Config $reviewConfig
  Write-Host "Dino review started (PID $($reviewProcess.Id))."
}

Write-Host "Dino review: http://127.0.0.1:$($reviewConfig.Port)/"
Start-Process "http://127.0.0.1:$port/"
