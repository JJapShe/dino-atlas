param(
  [ValidateSet("all", "tyrannosaurus", "yutyrannus")]
  [string]$Sample = "all"
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$motionDir = Join-Path $repoRoot "assets\motion"
$motionM2Dir = Join-Path $motionDir "m2"
[System.IO.Directory]::CreateDirectory($motionDir) | Out-Null
[System.IO.Directory]::CreateDirectory($motionM2Dir) | Out-Null

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
  throw "ffmpeg is required to build the environment-event motion samples."
}

function Invoke-MotionFfmpeg {
  param([string[]]$Arguments)
  & ffmpeg @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "ffmpeg failed with exit code $LASTEXITCODE."
  }
}

function Build-TyrannosaurusMeteorSample {
  # Reuse the independently reviewed forward-only head-turn stream. The
  # dinosaur pixels are not regenerated; only one small sky object is added.
  $source = Join-Path $motionM2Dir "tyrannosaurus-rex-alert-head-turn-comfyui-wan22-forward-only-i2v-m2-v2.mp4"
  $output = Join-Path $motionM2Dir "tyrannosaurus-rex-distant-meteor-sky-glance-wan22-safe-overlay-i2v-m2-v1.mp4"
  $meteorRgb = "color=c=0xffd98a:s=72x28:r=16:d=5.0625"
  $meteorMask = "color=c=black:s=72x28:r=16:d=5.0625,format=gray,drawbox=x=4:y=13:w=40:h=2:color=white@0.16:t=fill,drawbox=x=20:y=11:w=28:h=4:color=white@0.34:t=fill,drawbox=x=43:y=9:w=10:h=8:color=white@0.72:t=fill,drawbox=x=49:y=10:w=7:h=7:color=white@0.98:t=fill,gblur=sigma=1.5"
  $filter = "[0:v]format=rgba[base];[1:v]format=rgb24[mw];[2:v]format=gray[mm];[mw][mm]alphamerge,rotate=0.15:ow=rotw(iw):oh=roth(ih):c=none,fade=t=in:st=0.85:d=0.20:alpha=1,fade=t=out:st=2.45:d=0.35:alpha=1[meteor];[base][meteor]overlay=x='if(between(t,0.85,2.80),360+58*(t-0.85),NAN)':y='3+5*(t-0.85)':eval=frame:format=auto:alpha=straight,scale=in_range=pc:out_range=tv,format=yuv420p[out]"

  Invoke-MotionFfmpeg @(
    "-hide_banner", "-loglevel", "error", "-y",
    "-i", $source,
    "-f", "lavfi", "-t", "5.0625", "-i", $meteorRgb,
    "-f", "lavfi", "-t", "5.0625", "-i", $meteorMask,
    "-filter_complex", $filter, "-map", "[out]", "-an", "-r", "16", "-t", "5.0625",
    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
    "-movflags", "+faststart", $output
  )
}

function Build-YutyrannusVolcanicPlumeSample {
  # M0 safety route: keep the complete approved ecology still fixed and move
  # only a soft ash-plume layer connected to the existing distant summit.
  $source = Join-Path $repoRoot "assets\dinosaurs\yutyrannus-huali-cool-conifer-ashplain-ecology-imagegen-v1.png"
  $output = Join-Path $motionDir "yutyrannus-huali-volcanic-plume-ecology-m0-v1.mp4"
  $plumeRgb = "color=c=0x6d6862:s=160x150:r=24:d=5"
  $plumeMask = "color=c=black:s=160x150:r=24:d=5,format=gray,drawbox=x=38:y=82:w=28:h=50:color=white@0.45:t=fill,drawbox=x=47:y=61:w=38:h=40:color=white@0.38:t=fill,drawbox=x=58:y=41:w=48:h=34:color=white@0.30:t=fill,drawbox=x=71:y=24:w=56:h=28:color=white@0.22:t=fill,gblur=sigma=10"
  $filter = "[0:v]scale=960:640:flags=lanczos,format=rgba[base];[1:v]format=rgb24[pw];[2:v]format=gray[pm];[pw][pm]alphamerge,fade=t=in:st=0:d=0.9:alpha=1[plume];[base][plume]overlay=x='2.5*t':y='-2*t':eval=frame:format=auto:alpha=straight,scale=in_range=pc:out_range=tv,format=yuv420p[out]"

  Invoke-MotionFfmpeg @(
    "-hide_banner", "-loglevel", "error", "-y",
    "-loop", "1", "-framerate", "24", "-t", "5", "-i", $source,
    "-f", "lavfi", "-t", "5", "-i", $plumeRgb,
    "-f", "lavfi", "-t", "5", "-i", $plumeMask,
    "-filter_complex", $filter, "-map", "[out]", "-an", "-r", "24", "-t", "5",
    "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
    "-movflags", "+faststart", $output
  )
}

if ($Sample -in @("all", "tyrannosaurus")) { Build-TyrannosaurusMeteorSample }
if ($Sample -in @("all", "yutyrannus")) { Build-YutyrannusVolcanicPlumeSample }
