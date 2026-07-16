$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$ComfyDir = Join-Path $Root "ComfyUI"

if (-not (Test-Path $Python)) {
  throw "ComfyUI venv not found. Run .\tools\comfyui\setup-comfyui.ps1 first."
}

if (-not (Test-Path $ComfyDir)) {
  throw "ComfyUI folder not found. Run .\tools\comfyui\setup-comfyui.ps1 first."
}

Push-Location $ComfyDir
try {
  & $Python main.py --listen 127.0.0.1 --port 8188 --disable-auto-launch
}
finally {
  Pop-Location
}
