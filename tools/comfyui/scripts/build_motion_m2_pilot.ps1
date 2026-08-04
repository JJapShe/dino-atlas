param(
  [ValidateSet("oviraptor")]
  [string]$Sample = "oviraptor"
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$motionDir = Join-Path $repoRoot "assets\motion\m2"
$maskDir = Join-Path $repoRoot "tools\comfyui\motion_masks"
[System.IO.Directory]::CreateDirectory($motionDir) | Out-Null
[System.IO.Directory]::CreateDirectory($maskDir) | Out-Null

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
  throw "ffmpeg is required to build the M2 controlled partial-body pilot."
}

function Invoke-MotionFfmpeg {
  param([string[]]$Arguments)
  & ffmpeg @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "ffmpeg failed with exit code $LASTEXITCODE."
  }
}

function New-OviraptorHeadPath {
  $path = [System.Drawing.Drawing2D.GraphicsPath]::new()
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
  return $path
}

function Save-Mask {
  param(
    [System.Drawing.Drawing2D.GraphicsPath]$Path,
    [string]$OutputPath
  )

  $bitmap = [System.Drawing.Bitmap]::new(960, 640, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
  $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
  try {
    $graphics.Clear([System.Drawing.Color]::Black)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.FillPath([System.Drawing.Brushes]::White, $Path)
    $bitmap.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
  } finally {
    $graphics.Dispose()
    $bitmap.Dispose()
  }
}

function Save-SweepAndLockedMasks {
  param(
    [System.Drawing.Drawing2D.GraphicsPath]$Path,
    [string]$SweepOutputPath,
    [string]$LockedOutputPath
  )

  $sweepBitmap = [System.Drawing.Bitmap]::new(960, 640, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
  $sweepGraphics = [System.Drawing.Graphics]::FromImage($sweepBitmap)
  $lockedBitmap = [System.Drawing.Bitmap]::new(960, 640, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
  $lockedGraphics = [System.Drawing.Graphics]::FromImage($lockedBitmap)
  try {
    $sweepGraphics.Clear([System.Drawing.Color]::Black)
    $lockedGraphics.Clear([System.Drawing.Color]::White)
    foreach ($graphics in @($sweepGraphics, $lockedGraphics)) {
      $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    }
    for ($angle = -4.0; $angle -le 4.001; $angle += 0.25) {
      foreach ($item in @(
        @{ Graphics = $sweepGraphics; Brush = [System.Drawing.Brushes]::White },
        @{ Graphics = $lockedGraphics; Brush = [System.Drawing.Brushes]::Black }
      )) {
        $item.Graphics.ResetTransform()
        $item.Graphics.TranslateTransform(260, 316)
        $item.Graphics.RotateTransform([single]$angle)
        $item.Graphics.TranslateTransform(-260, -316)
        $item.Graphics.FillPath($item.Brush, $Path)
      }
    }
    $sweepGraphics.ResetTransform()
    $lockedGraphics.ResetTransform()
    $sweepBitmap.Save($SweepOutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $lockedBitmap.Save($LockedOutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
  } finally {
    $sweepGraphics.Dispose()
    $sweepBitmap.Dispose()
    $lockedGraphics.Dispose()
    $lockedBitmap.Dispose()
  }
}

function Build-OviraptorM2Pilot {
  Add-Type -AssemblyName System.Drawing
  $source = Join-Path $repoRoot "assets\dinosaurs\oviraptor-philoceratops-robust-lowcrest-rostrum-representative-imagegen-v3.png"
  $cleanPlate = Join-Path $repoRoot "assets\dinosaurs\oviraptor-philoceratops-head-tail-clean-plate-motion-imagegen-v1.png"
  $headMask = Join-Path $maskDir "oviraptor-philoceratops-head-actor-partial-m2-v1.png"
  $headSweepMask = Join-Path $maskDir "oviraptor-philoceratops-head-sweep-partial-m2-v1.png"
  $lockedBodyMask = Join-Path $maskDir "oviraptor-philoceratops-locked-body-partial-m2-v1.png"
  $output = Join-Path $motionDir "oviraptor-philoceratops-rigid-head-sweep-biological-m2-v1.mp4"

  foreach ($requiredPath in @($source, $cleanPlate)) {
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
      throw "Required M2 input is missing: $requiredPath"
    }
  }

  $headPath = New-OviraptorHeadPath
  try {
    Save-Mask -Path $headPath -OutputPath $headMask
    Save-SweepAndLockedMasks -Path $headPath -SweepOutputPath $headSweepMask -LockedOutputPath $lockedBodyMask
  } finally {
    $headPath.Dispose()
  }

  $filter = "[0:v]scale=960:640:flags=lanczos,format=rgba,split=2[srcBase][headSource];[1:v]scale=960:640:flags=lanczos,format=rgb24[cleanRgb];[3:v]scale=960:640:flags=neighbor,format=gray,gblur=sigma=0.4[fillAlpha];[cleanRgb][fillAlpha]alphamerge[cleanPatch];[srcBase][cleanPatch]overlay=x=0:y=0:format=auto:alpha=straight[baseClean];[headSource]pad=1020:644:60:4:color=0x00000000,crop=640:640:0:0[headRgb];[2:v]scale=960:640:flags=neighbor,format=gray,pad=1020:644:60:4:color=black,crop=640:640:0:0,gblur=sigma=0.4[headAlpha];[headRgb][headAlpha]alphamerge[head];[head]rotate='0.0698131701*sin(2*PI*t/5)':ow=640:oh=640:c=none:bilinear=1[headMove];[baseClean][headMove]overlay=x=-60:y=-4:format=auto:alpha=straight,scale=in_range=pc:out_range=tv,format=yuv420p[out]"

  Invoke-MotionFfmpeg @(
    "-hide_banner", "-loglevel", "error", "-y",
    "-loop", "1", "-framerate", "24", "-t", "5", "-i", $source,
    "-loop", "1", "-framerate", "24", "-t", "5", "-i", $cleanPlate,
    "-loop", "1", "-framerate", "24", "-t", "5", "-i", $headMask,
    "-loop", "1", "-framerate", "24", "-t", "5", "-i", $headSweepMask,
    "-filter_complex", $filter, "-map", "[out]", "-an", "-r", "24", "-t", "5",
    "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
    "-movflags", "+faststart", $output
  )
}

if ($Sample -eq "oviraptor") { Build-OviraptorM2Pilot }
