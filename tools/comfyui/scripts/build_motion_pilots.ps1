param(
  [ValidateSet("all", "yutyrannus", "tyrannosaurus", "brachiosaurus")]
  [string]$Sample = "all"
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$motionDir = Join-Path $repoRoot "assets\motion"
[System.IO.Directory]::CreateDirectory($motionDir) | Out-Null

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
  throw "ffmpeg is required to build the M0 motion pilots."
}

function Invoke-MotionFfmpeg {
  param([string[]]$Arguments)
  & ffmpeg @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "ffmpeg failed with exit code $LASTEXITCODE."
  }
}

function Build-YutyrannusPilot {
  $source = Join-Path $repoRoot "assets\dinosaurs\yutyrannus-huali-yixian-white-mottled-feathered-representative-imagegen-v1.png"
  $output = Join-Path $motionDir "yutyrannus-huali-white-feather-cold-breath-ambient-m0-v1.mp4"
  $whiteA = "color=c=white:s=120x80:r=24:d=5"
  $maskA = "color=c=black:s=120x80:r=24:d=5,format=gray,drawbox=x=92:y=34:w=24:h=12:color=white@0.84:t=fill,drawbox=x=58:y=27:w=48:h=25:color=white@0.55:t=fill,drawbox=x=20:y=18:w=60:h=42:color=white@0.30:t=fill,gblur=sigma=10"
  $whiteB = "color=c=white:s=112x76:r=24:d=5"
  $maskB = "color=c=black:s=112x76:r=24:d=5,format=gray,drawbox=x=86:y=32:w=22:h=11:color=white@0.76:t=fill,drawbox=x=54:y=26:w=44:h=23:color=white@0.49:t=fill,drawbox=x=18:y=17:w=56:h=39:color=white@0.27:t=fill,gblur=sigma=9"
  $filter = "[0:v]scale=960:640:flags=lanczos,format=rgba[base];[1:v]format=rgb24[w1];[2:v]format=gray[m1];[w1][m1]alphamerge,fade=t=in:st=0.12:d=0.38:alpha=1,fade=t=out:st=1.62:d=0.68:alpha=1[breath1];[3:v]format=rgb24[w2];[4:v]format=gray[m2];[w2][m2]alphamerge,fade=t=in:st=2.50:d=0.42:alpha=1,fade=t=out:st=4.10:d=0.72:alpha=1[breath2];[base][breath1]overlay=x='-11-15*t':y='99-2*t':format=auto:alpha=straight[b1];[b1][breath2]overlay=x='18-12.5*t':y='102-1.5*t':format=auto:alpha=straight,scale=in_range=pc:out_range=tv,format=yuv420p[out]"

  Invoke-MotionFfmpeg @(
    "-hide_banner", "-loglevel", "error", "-y",
    "-loop", "1", "-framerate", "24", "-t", "5", "-i", $source,
    "-f", "lavfi", "-t", "5", "-i", $whiteA,
    "-f", "lavfi", "-t", "5", "-i", $maskA,
    "-f", "lavfi", "-t", "5", "-i", $whiteB,
    "-f", "lavfi", "-t", "5", "-i", $maskB,
    "-filter_complex", $filter, "-map", "[out]", "-an", "-r", "24", "-t", "5",
    "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
    "-movflags", "+faststart", $output
  )
}

function Build-TyrannosaurusPilot {
  $source = Join-Path $repoRoot "assets\dinosaurs\tyrannosaurus-rex-hell-creek-deepskull-twofinger-representative-imagegen-v1.png"
  $output = Join-Path $motionDir "tyrannosaurus-rex-hell-creek-ground-mist-ambient-m0-v1.mp4"
  $mistRgb = "color=c=0xe8eef0:s=360x120:r=24:d=5"
  $mistMask = "color=c=black:s=360x120:r=24:d=5,format=gray,drawbox=x=28:y=34:w=118:h=46:color=white@0.15:t=fill,drawbox=x=116:y=24:w=142:h=58:color=white@0.20:t=fill,drawbox=x=238:y=38:w=96:h=42:color=white@0.13:t=fill,gblur=sigma=19"
  $mistRgb2 = "color=c=0xdde7e9:s=250x90:r=24:d=5"
  $mistMask2 = "color=c=black:s=250x90:r=24:d=5,format=gray,drawbox=x=22:y=30:w=96:h=32:color=white@0.11:t=fill,drawbox=x=102:y=20:w=126:h=45:color=white@0.15:t=fill,gblur=sigma=16"
  $filter = "[0:v]split=2[bg0][fg0];[bg0]scale=960:640:force_original_aspect_ratio=increase:flags=lanczos,crop=960:640,gblur=sigma=18[bg];[fg0]scale=960:640:force_original_aspect_ratio=decrease:flags=lanczos[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,format=rgba[base];[1:v]format=rgb24[mw1];[2:v]format=gray[mm1];[mw1][mm1]alphamerge[mist1];[3:v]format=rgb24[mw2];[4:v]format=gray[mm2];[mw2][mm2]alphamerge[mist2];[base][mist1]overlay=x='580+10*t':y='396+3*sin(1.3*t)':format=auto:alpha=straight[m1];[m1][mist2]overlay=x='680-5*t':y='430+2*sin(1.8*t)':format=auto:alpha=straight,scale=in_range=pc:out_range=tv,format=yuv420p[out]"

  Invoke-MotionFfmpeg @(
    "-hide_banner", "-loglevel", "error", "-y",
    "-loop", "1", "-framerate", "24", "-t", "5", "-i", $source,
    "-f", "lavfi", "-t", "5", "-i", $mistRgb,
    "-f", "lavfi", "-t", "5", "-i", $mistMask,
    "-f", "lavfi", "-t", "5", "-i", $mistRgb2,
    "-f", "lavfi", "-t", "5", "-i", $mistMask2,
    "-filter_complex", $filter, "-map", "[out]", "-an", "-r", "24", "-t", "5",
    "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
    "-movflags", "+faststart", $output
  )
}

function Build-BrachiosaurusPilot {
  $source = Join-Path $repoRoot "assets\dinosaurs\brachiosaurus-altithorax-nasal-mound-fullbody-imagegen-v18.png"
  $output = Join-Path $motionDir "brachiosaurus-altithorax-high-shoulder-skylight-ambient-m0-v1.mp4"
  $hazeRgb = "color=c=0xfff1d8:s=360x180:r=24:d=5"
  $hazeMask = "color=c=black:s=360x180:r=24:d=5,format=gray,drawbox=x=42:y=42:w=122:h=72:color=white@0.10:t=fill,drawbox=x=132:y=28:w=142:h=98:color=white@0.14:t=fill,drawbox=x=252:y=48:w=74:h=62:color=white@0.08:t=fill,gblur=sigma=31"
  $hazeRgb2 = "color=c=0xeaf5ff:s=240x140:r=24:d=5"
  $hazeMask2 = "color=c=black:s=240x140:r=24:d=5,format=gray,drawbox=x=34:y=34:w=164:h=70:color=white@0.075:t=fill,gblur=sigma=27"
  $filter = "[0:v]scale=960:640:flags=lanczos,format=rgba[base];[1:v]format=rgb24[hw1];[2:v]format=gray[hm1];[hw1][hm1]alphamerge,fade=t=in:st=0:d=0.55:alpha=1,fade=t=out:st=4.25:d=0.75:alpha=1[haze1];[3:v]format=rgb24[hw2];[4:v]format=gray[hm2];[hw2][hm2]alphamerge,fade=t=in:st=0.25:d=0.75:alpha=1,fade=t=out:st=4.0:d=0.9:alpha=1[haze2];[base][haze1]overlay=x='355+11*t':y='18+3*sin(0.8*t)':format=auto:alpha=straight[h1];[h1][haze2]overlay=x='510-7*t':y='52+2*sin(1.1*t)':format=auto:alpha=straight,scale=in_range=pc:out_range=tv,format=yuv420p[out]"

  Invoke-MotionFfmpeg @(
    "-hide_banner", "-loglevel", "error", "-y",
    "-loop", "1", "-framerate", "24", "-t", "5", "-i", $source,
    "-f", "lavfi", "-t", "5", "-i", $hazeRgb,
    "-f", "lavfi", "-t", "5", "-i", $hazeMask,
    "-f", "lavfi", "-t", "5", "-i", $hazeRgb2,
    "-f", "lavfi", "-t", "5", "-i", $hazeMask2,
    "-filter_complex", $filter, "-map", "[out]", "-an", "-r", "24", "-t", "5",
    "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
    "-movflags", "+faststart", $output
  )
}

if ($Sample -in @("all", "yutyrannus")) { Build-YutyrannusPilot }
if ($Sample -in @("all", "tyrannosaurus")) { Build-TyrannosaurusPilot }
if ($Sample -in @("all", "brachiosaurus")) { Build-BrachiosaurusPilot }
