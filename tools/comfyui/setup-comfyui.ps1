$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Venv = Join-Path $Root ".venv"
$ComfyDir = Join-Path $Root "ComfyUI"
$Python = Join-Path $Venv "Scripts\python.exe"

if (-not (Test-Path $Venv)) {
  python -m venv $Venv
}

& $Python -m pip install --upgrade pip
& $Python -m pip install comfy-cli

if (-not (Test-Path $ComfyDir)) {
  git clone https://github.com/comfyanonymous/ComfyUI.git $ComfyDir
}

Push-Location $ComfyDir
try {
  & $Python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
  & $Python -m pip install -r requirements.txt
}
finally {
  Pop-Location
}

Write-Host "ComfyUI setup complete: $ComfyDir"
Write-Host "Run .\tools\comfyui\start-comfyui.ps1"
