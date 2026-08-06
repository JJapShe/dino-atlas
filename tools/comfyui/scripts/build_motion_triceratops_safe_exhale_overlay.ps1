param(
    [Parameter(Mandatory = $true)]
    [string]$Source,

    [Parameter(Mandatory = $true)]
    [string]$Output,

    [string]$FfmpegPath = "ffmpeg"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$width = 800
$height = 448
$fps = 16
$frameCount = 81
$activeStartFrame = 10
$activeEndFrame = 73

$sourcePath = [System.IO.Path]::GetFullPath($Source)
$outputPath = [System.IO.Path]::GetFullPath($Output)
if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
    throw "Source video does not exist: $sourcePath"
}

$outputDirectory = [System.IO.Path]::GetDirectoryName($outputPath)
if (-not (Test-Path -LiteralPath $outputDirectory -PathType Container)) {
    New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
}

$tempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
$overlayDirectory = [System.IO.Path]::Combine(
    $tempRoot,
    "dino-atlas-triceratops-exhale-" + [System.Guid]::NewGuid().ToString("N")
)
$overlayDirectory = [System.IO.Path]::GetFullPath($overlayDirectory)
$tempPrefix = $tempRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
if (-not $overlayDirectory.StartsWith($tempPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Temporary overlay directory escaped the system temp root: $overlayDirectory"
}

Add-Type -AssemblyName System.Drawing

function Get-ClampedValue {
    param(
        [double]$Value,
        [double]$Minimum,
        [double]$Maximum
    )
    return [Math]::Max($Minimum, [Math]::Min($Maximum, $Value))
}

function Draw-SoftPuff {
    param(
        [System.Drawing.Graphics]$Graphics,
        [double]$CenterX,
        [double]$CenterY,
        [double]$Radius,
        [double]$Opacity
    )

    $rings = @(
        @{ Scale = 1.00; Alpha = 0.16 },
        @{ Scale = 0.78; Alpha = 0.22 },
        @{ Scale = 0.54; Alpha = 0.30 },
        @{ Scale = 0.30; Alpha = 0.34 }
    )
    foreach ($ring in $rings) {
        $ringRadius = $Radius * [double]$ring.Scale
        $alpha = [int](Get-ClampedValue -Value (255.0 * $Opacity * [double]$ring.Alpha) -Minimum 0 -Maximum 255)
        if ($alpha -le 0 -or $ringRadius -lt 0.4) {
            continue
        }
        $color = [System.Drawing.Color]::FromArgb($alpha, 224, 211, 180)
        $brush = [System.Drawing.SolidBrush]::new($color)
        try {
            $Graphics.FillEllipse(
                $brush,
                [single]($CenterX - $ringRadius),
                [single]($CenterY - 0.72 * $ringRadius),
                [single](2.0 * $ringRadius),
                [single](1.44 * $ringRadius)
            )
        }
        finally {
            $brush.Dispose()
        }
    }
}

New-Item -ItemType Directory -Path $overlayDirectory | Out-Null
try {
    for ($frame = 0; $frame -lt $frameCount; $frame++) {
        $bitmap = [System.Drawing.Bitmap]::new(
            $width,
            $height,
            [System.Drawing.Imaging.PixelFormat]::Format32bppArgb
        )
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        try {
            $graphics.Clear([System.Drawing.Color]::Transparent)
            $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
            $graphics.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
            $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic

            if ($frame -ge $activeStartFrame -and $frame -le $activeEndFrame) {
                $globalProgress = ($frame - $activeStartFrame) / [double]($activeEndFrame - $activeStartFrame)
                $envelope = [Math]::Min(1.0, ($frame - $activeStartFrame + 1) / 8.0)
                $fadeOut = [Math]::Min(1.0, ($activeEndFrame - $frame + 1) / 11.0)
                $envelope *= $fadeOut

                # Five staggered wisps form one continuous, forward-only exhale plume.
                # Every wisp stays entirely in the empty air left of the muzzle (x <= 71).
                for ($wisp = 0; $wisp -lt 5; $wisp++) {
                    $delay = 0.075 * $wisp
                    $localProgress = Get-ClampedValue -Value (($globalProgress - $delay) / (1.0 - $delay)) -Minimum 0 -Maximum 1
                    if ($globalProgress -lt $delay) {
                        continue
                    }
                    $x = 67.0 - (54.0 * $localProgress) - (2.0 * $wisp)
                    $y = 258.0 - (39.0 * $localProgress) + (2.3 * $wisp)
                    $radius = 3.0 + (13.0 * $localProgress) + (0.9 * $wisp)
                    $wispFade = 1.0 - [Math]::Pow($localProgress, 1.65)
                    $opacity = $envelope * $wispFade * (1.0 - 0.11 * $wisp)
                    Draw-SoftPuff -Graphics $graphics -CenterX $x -CenterY $y -Radius $radius -Opacity $opacity
                }
            }

            $framePath = [System.IO.Path]::Combine($overlayDirectory, ("frame-{0:D3}.png" -f $frame))
            $bitmap.Save($framePath, [System.Drawing.Imaging.ImageFormat]::Png)
        }
        finally {
            $graphics.Dispose()
            $bitmap.Dispose()
        }
    }

    $overlayPattern = [System.IO.Path]::Combine($overlayDirectory, "frame-%03d.png")
    $filter = "[0:v][1:v]overlay=0:0:shortest=1:format=auto,format=yuv420p"
    $arguments = @(
        "-hide_banner", "-loglevel", "error", "-y",
        "-i", $sourcePath,
        "-framerate", $fps,
        "-i", $overlayPattern,
        "-filter_complex", $filter,
        "-an",
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "slow",
        "-movflags", "+faststart",
        $outputPath
    )
    & $FfmpegPath @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "ffmpeg failed with exit code $LASTEXITCODE"
    }
}
finally {
    $resolvedOverlayDirectory = [System.IO.Path]::GetFullPath($overlayDirectory)
    $isInsideTemp = $resolvedOverlayDirectory.StartsWith(
        $tempPrefix,
        [System.StringComparison]::OrdinalIgnoreCase
    )
    $hasExpectedName = [System.IO.Path]::GetFileName($resolvedOverlayDirectory).StartsWith(
        "dino-atlas-triceratops-exhale-",
        [System.StringComparison]::OrdinalIgnoreCase
    )
    if ((Test-Path -LiteralPath $resolvedOverlayDirectory) -and $isInsideTemp -and $hasExpectedName) {
        Remove-Item -LiteralPath $resolvedOverlayDirectory -Recurse -Force
    }
}
