$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ComfyExe = Join-Path $Root ".venv\Scripts\comfy.exe"

if (-not (Test-Path $ComfyExe)) {
  throw "comfy-cli not found. Run setup-comfyui.cmd first."
}

& $ComfyExe model download `
  --url "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors" `
  --relative-path "models/checkpoints"
