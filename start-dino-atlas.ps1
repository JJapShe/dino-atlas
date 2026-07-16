$ErrorActionPreference = "Stop"

$port = 8020
$reviewPort = 8792
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue |
  Select-Object -First 1

if (-not $listener) {
  $python = (Get-Command python -ErrorAction Stop).Source
  Start-Process -FilePath $python -ArgumentList @("-m", "http.server", "$port", "--bind", "127.0.0.1") `
    -WorkingDirectory $root -WindowStyle Hidden

  for ($attempt = 0; $attempt -lt 20; $attempt += 1) {
    Start-Sleep -Milliseconds 300
    try {
      $response = Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:$port/" -TimeoutSec 2
      if ($response.StatusCode -eq 200) { break }
    } catch {
      if ($attempt -eq 19) { throw }
    }
  }
}

$reviewListener = Get-NetTCPConnection -LocalPort $reviewPort -State Listen -ErrorAction SilentlyContinue |
  Select-Object -First 1

if (-not $reviewListener) {
  $reviewRoot = Join-Path $root "tools\dino-review"
  $node = Get-ChildItem (Join-Path $env:LOCALAPPDATA "OpenAI\Codex\runtimes\cua_node") -Recurse -Filter "node.exe" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1 -ExpandProperty FullName

  if (-not $node) {
    $node = (Get-Command node -ErrorAction Stop).Source
  }

  Start-Process -FilePath $node -ArgumentList @("server.js") -WorkingDirectory $reviewRoot -WindowStyle Hidden

  for ($attempt = 0; $attempt -lt 20; $attempt += 1) {
    Start-Sleep -Milliseconds 300
    try {
      $response = Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:$reviewPort/" -TimeoutSec 2
      if ($response.StatusCode -eq 200) { break }
    } catch {
      if ($attempt -eq 19) { throw }
    }
  }
}

Start-Process "http://127.0.0.1:$port/"
