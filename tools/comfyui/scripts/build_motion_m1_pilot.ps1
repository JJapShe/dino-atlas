param(
  [ValidateSet("oviraptor")]
  [string]$Sample = "oviraptor"
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$motionDir = Join-Path $repoRoot "assets\motion\m1"
[System.IO.Directory]::CreateDirectory($motionDir) | Out-Null

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
  throw "ffmpeg is required to build the M1 biological-motion pilot."
}

function Invoke-MotionFfmpeg {
  param([string[]]$Arguments)
  & ffmpeg @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "ffmpeg failed with exit code $LASTEXITCODE."
  }
}

function New-OviraptorHeadMask {
  param([string]$OutputPath)

  Add-Type -AssemblyName System.Drawing
  $bitmap = [System.Drawing.Bitmap]::new(960, 640, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
  $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
  $path = [System.Drawing.Drawing2D.GraphicsPath]::new()
  $white = [System.Drawing.Brushes]::White
  try {
    $graphics.Clear([System.Drawing.Color]::Black)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $path.StartFigure()
    $path.AddBezier(164, 36, 188, 24, 231, 24, 272, 36)
    $path.AddBezier(272, 36, 307, 46, 326, 69, 331, 105)
    $path.AddBezier(331, 105, 335, 130, 327, 151, 310, 166)
    $path.AddBezier(310, 166, 307, 205, 304, 245, 300, 279)
    $path.AddBezier(300, 279, 294, 302, 280, 316, 260, 316)
    $path.AddBezier(260, 316, 237, 312, 225, 291, 217, 260)
    $path.AddBezier(217, 260, 210, 220, 207, 187, 194, 166)
    $path.AddBezier(194, 166, 168, 165, 151, 154, 143, 133)
    $path.AddBezier(143, 133, 133, 106, 141, 76, 155, 55)
    $path.AddBezier(155, 55, 158, 48, 161, 42, 164, 36)
    $path.CloseFigure()
    $graphics.FillPath($white, $path)
    $bitmap.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
  } finally {
    $path.Dispose()
    $graphics.Dispose()
    $bitmap.Dispose()
  }
}

function Build-OviraptorM1Pilot {
  $source = Join-Path $repoRoot "assets\dinosaurs\oviraptor-philoceratops-robust-lowcrest-rostrum-representative-imagegen-v3.png"
  $closedEye = Join-Path $repoRoot "assets\motion\m1\overlays\oviraptor-philoceratops-closed-eye-overlay-imagegen-v1.png"
  $output = Join-Path $motionDir "oviraptor-philoceratops-blink-headtilt-biological-m1-v1.mp4"
  $mask = Join-Path ([System.IO.Path]::GetTempPath()) ("dino-atlas-oviraptor-m1-mask-{0}.png" -f [System.Guid]::NewGuid().ToString("N"))

  foreach ($requiredPath in @($source, $closedEye)) {
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
      throw "Required M1 input is missing: $requiredPath"
    }
  }

  try {
    New-OviraptorHeadMask -OutputPath $mask
    $filter = "[0:v]scale=960:640:flags=lanczos,format=rgba,split=2[base][actor0];[1:v]format=rgba,split=2[eye1][eye2];[eye1]fade=t=in:st=0.92:d=0.08:alpha=1,fade=t=out:st=1.08:d=0.08:alpha=1[blink1];[eye2]fade=t=in:st=3.02:d=0.08:alpha=1,fade=t=out:st=3.18:d=0.08:alpha=1[blink2];[actor0][blink1]overlay=x=198:y=50:format=auto:alpha=straight[a1];[a1][blink2]overlay=x=198:y=50:format=auto:alpha=straight[actorBlink];[actorBlink]crop=440:440:55:25[headRgb];[2:v]scale=960:640:flags=neighbor,format=gray,crop=440:440:55:25,gblur=sigma=1.4[headAlpha];[headRgb][headAlpha]alphamerge[head];[head]rotate='0.014*sin(2*PI*t/5)':ow=440:oh=440:c=none:bilinear=1[headMove];[base][headMove]overlay=x=55:y=25:format=auto:alpha=straight,scale=in_range=pc:out_range=tv,format=yuv420p[out]"

    Invoke-MotionFfmpeg @(
      "-hide_banner", "-loglevel", "error", "-y",
      "-loop", "1", "-framerate", "24", "-t", "5", "-i", $source,
      "-loop", "1", "-framerate", "24", "-t", "5", "-i", $closedEye,
      "-loop", "1", "-framerate", "24", "-t", "5", "-i", $mask,
      "-filter_complex", $filter, "-map", "[out]", "-an", "-r", "24", "-t", "5",
      "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
      "-movflags", "+faststart", $output
    )
  } finally {
    if (Test-Path -LiteralPath $mask) {
      Remove-Item -LiteralPath $mask -Force
    }
  }
}

if ($Sample -eq "oviraptor") { Build-OviraptorM1Pilot }
