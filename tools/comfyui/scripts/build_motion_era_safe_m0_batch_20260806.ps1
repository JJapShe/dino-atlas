param(
  [ValidateSet("all", "buriolestes-charcoal-haze", "ceratosaurus-water-ring")]
  [string]$Sample = "all",
  [string]$FfmpegPath = "ffmpeg"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$motionDir = Join-Path $repoRoot "assets\motion"
[System.IO.Directory]::CreateDirectory($motionDir) | Out-Null

if (-not (Get-Command $FfmpegPath -ErrorAction SilentlyContinue)) {
  throw "ffmpeg is required. Pass -FfmpegPath when it is not on PATH."
}

Add-Type -AssemblyName System.Drawing

$fps = 24
$frameCount = 132
$durationSeconds = 5.5
$encodeQp = 12

function Get-ClampedValue {
  param([double]$Value, [double]$Minimum, [double]$Maximum)
  return [Math]::Max($Minimum, [Math]::Min($Maximum, $Value))
}

function New-SafeTempDirectory {
  param([string]$NamePrefix)
  $tempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
  $directory = [System.IO.Path]::Combine($tempRoot, $NamePrefix + [System.Guid]::NewGuid().ToString("N"))
  $directory = [System.IO.Path]::GetFullPath($directory)
  $prefix = $tempRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
  if (-not $directory.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Temporary directory escaped the system temp root: $directory"
  }
  New-Item -ItemType Directory -Path $directory | Out-Null
  return $directory
}

function Remove-SafeTempDirectory {
  param([string]$Directory, [string]$ExpectedPrefix)
  $tempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
  $resolved = [System.IO.Path]::GetFullPath($Directory)
  $prefix = $tempRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
  $insideTemp = $resolved.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)
  $expectedName = [System.IO.Path]::GetFileName($resolved).StartsWith($ExpectedPrefix, [System.StringComparison]::OrdinalIgnoreCase)
  if ((Test-Path -LiteralPath $resolved) -and $insideTemp -and $expectedName) {
    Remove-Item -LiteralPath $resolved -Recurse -Force
  }
}

function Draw-SoftHazePuff {
  param(
    [System.Drawing.Graphics]$Graphics,
    [double]$CenterX,
    [double]$CenterY,
    [double]$Radius,
    [double]$Opacity
  )
  $rings = @(
    @{ Scale = 1.00; Alpha = 0.080 },
    @{ Scale = 0.78; Alpha = 0.120 },
    @{ Scale = 0.55; Alpha = 0.160 },
    @{ Scale = 0.32; Alpha = 0.200 }
  )
  foreach ($ring in $rings) {
    $ringRadius = $Radius * [double]$ring.Scale
    $alpha = [int](Get-ClampedValue -Value (255.0 * $Opacity * [double]$ring.Alpha) -Minimum 0 -Maximum 255)
    if ($alpha -le 0 -or $ringRadius -lt 0.5) { continue }
    $brush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb($alpha, 173, 174, 169))
    try {
      $Graphics.FillEllipse(
        $brush,
        [single]($CenterX - $ringRadius),
        [single]($CenterY - 0.50 * $ringRadius),
        [single](2.0 * $ringRadius),
        [single](1.00 * $ringRadius)
      )
    }
    finally {
      $brush.Dispose()
    }
  }
}

function Write-BuriolestesHazeFrames {
  param([string]$Directory)
  for ($frame = 0; $frame -lt $frameCount; $frame++) {
    $progress = $frame / [double]($frameCount - 1)
    $bitmap = [System.Drawing.Bitmap]::new(960, 640, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    try {
      $graphics.Clear([System.Drawing.Color]::Transparent)
      $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
      $graphics.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
      $graphics.SetClip([System.Drawing.Rectangle]::new(25, 250, 430, 245))
      $envelope = 0.58 + (0.42 * [Math]::Min(1.0, $progress / 0.18))
      $paths = @(
        @{ X0 = 90.0;  X1 = 130.0; Y0 = 440.0; Y1 = 315.0; R0 = 34.0; R1 = 68.0; O = 0.96 },
        @{ X0 = 230.0; X1 = 275.0; Y0 = 455.0; Y1 = 335.0; R0 = 28.0; R1 = 60.0; O = 0.82 },
        @{ X0 = 350.0; X1 = 390.0; Y0 = 430.0; Y1 = 300.0; R0 = 30.0; R1 = 64.0; O = 0.88 }
      )
      foreach ($path in $paths) {
        $x = [double]$path.X0 + (([double]$path.X1 - [double]$path.X0) * $progress)
        $y = [double]$path.Y0 + (([double]$path.Y1 - [double]$path.Y0) * $progress)
        $radius = [double]$path.R0 + (([double]$path.R1 - [double]$path.R0) * $progress)
        $opacity = $envelope * [double]$path.O
        Draw-SoftHazePuff -Graphics $graphics -CenterX $x -CenterY $y -Radius $radius -Opacity $opacity
        Draw-SoftHazePuff -Graphics $graphics -CenterX ($x - 0.34 * $radius) -CenterY ($y + 0.08 * $radius) -Radius (0.68 * $radius) -Opacity (0.55 * $opacity)
        Draw-SoftHazePuff -Graphics $graphics -CenterX ($x + 0.38 * $radius) -CenterY ($y + 0.04 * $radius) -Radius (0.62 * $radius) -Opacity (0.50 * $opacity)
      }
      $framePath = [System.IO.Path]::Combine($Directory, ("frame-{0:D3}.png" -f $frame))
      $bitmap.Save($framePath, [System.Drawing.Imaging.ImageFormat]::Png)
    }
    finally {
      $graphics.Dispose()
      $bitmap.Dispose()
    }
  }
}

function Write-CeratosaurusWaterRingFrames {
  param([string]$Directory)
  for ($frame = 0; $frame -lt $frameCount; $frame++) {
    $progress = $frame / [double]($frameCount - 1)
    $bitmap = [System.Drawing.Bitmap]::new(960, 540, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    try {
      $graphics.Clear([System.Drawing.Color]::Transparent)
      $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
      $graphics.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
      $graphics.SetClip([System.Drawing.Rectangle]::new(0, 410, 300, 60))
      $baseRadius = 12.0 + (82.0 * $progress)
      $fade = 1.0 - (0.43 * $progress)
      $offsets = @(0.0, 24.0, 48.0)
      for ($index = 0; $index -lt $offsets.Count; $index++) {
        $radiusX = $baseRadius + [double]$offsets[$index]
        $radiusY = 3.5 + (0.115 * $radiusX)
        $opacity = $fade * (0.42 - 0.060 * $index)
        $alpha = [int](Get-ClampedValue -Value (255.0 * $opacity) -Minimum 0 -Maximum 255)
        $pen = [System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb($alpha, 232, 221, 194), [single]3.0)
        try {
          $graphics.DrawEllipse(
            $pen,
            [single](130.0 - $radiusX),
            [single](435.0 - $radiusY),
            [single](2.0 * $radiusX),
            [single](2.0 * $radiusY)
          )
        }
        finally {
          $pen.Dispose()
        }
      }
      $framePath = [System.IO.Path]::Combine($Directory, ("frame-{0:D3}.png" -f $frame))
      $bitmap.Save($framePath, [System.Drawing.Imaging.ImageFormat]::Png)
    }
    finally {
      $graphics.Dispose()
      $bitmap.Dispose()
    }
  }
}

function Invoke-OverlayEncode {
  param(
    [string]$Source,
    [string]$OverlayDirectory,
    [string]$Output,
    [int]$Width,
    [int]$Height
  )
  $overlayPattern = [System.IO.Path]::Combine($OverlayDirectory, "frame-%03d.png")
  $filter = "[0:v]scale=${Width}:${Height}:flags=lanczos,format=rgba[base];[base][1:v]overlay=0:0:shortest=1:format=auto,format=yuv420p[out]"
  $arguments = @(
    "-hide_banner", "-loglevel", "error", "-y",
    "-loop", "1", "-framerate", $fps, "-i", $Source,
    "-framerate", $fps, "-i", $overlayPattern,
    "-filter_complex", $filter, "-map", "[out]", "-frames:v", $frameCount,
    "-an", "-c:v", "libx264", "-qp", $encodeQp, "-preset", "slow", "-profile:v", "high",
    "-pix_fmt", "yuv420p", "-movflags", "+faststart", $Output
  )
  & $FfmpegPath @arguments
  if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed with exit code $LASTEXITCODE" }
}

function Build-BuriolestesCharcoalHazeSample {
  $tempPrefix = "dino-atlas-buriolestes-haze-"
  $tempDirectory = New-SafeTempDirectory -NamePrefix $tempPrefix
  try {
    Write-BuriolestesHazeFrames -Directory $tempDirectory
    Invoke-OverlayEncode `
      -Source (Join-Path $repoRoot "assets\dinosaurs\buriolestes-schultzi-candelaria-macrocharcoal-wildfire-composite-ecology-imagegen-v1.png") `
      -OverlayDirectory $tempDirectory `
      -Output (Join-Path $motionDir "buriolestes-schultzi-candelaria-charcoal-ground-haze-environment-m0-v1.mp4") `
      -Width 960 -Height 640
  }
  finally {
    Remove-SafeTempDirectory -Directory $tempDirectory -ExpectedPrefix $tempPrefix
  }
}

function Build-CeratosaurusWaterRingSample {
  $tempPrefix = "dino-atlas-ceratosaurus-water-ring-"
  $tempDirectory = New-SafeTempDirectory -NamePrefix $tempPrefix
  try {
    Write-CeratosaurusWaterRingFrames -Directory $tempDirectory
    Invoke-OverlayEncode `
      -Source (Join-Path $repoRoot "assets\dinosaurs\ceratosaurus-nasicornis-horsetail-dawn-drinking-behavior-imagegen-v2.png") `
      -OverlayDirectory $tempDirectory `
      -Output (Join-Path $motionDir "ceratosaurus-nasicornis-horsetail-dawn-water-ring-solo-m0-v1.mp4") `
      -Width 960 -Height 540
  }
  finally {
    Remove-SafeTempDirectory -Directory $tempDirectory -ExpectedPrefix $tempPrefix
  }
}

if ($Sample -in @("all", "buriolestes-charcoal-haze")) { Build-BuriolestesCharcoalHazeSample }
if ($Sample -in @("all", "ceratosaurus-water-ring")) { Build-CeratosaurusWaterRingSample }
