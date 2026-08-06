param(
  [ValidateSet("all", "mononykus-rainsquall", "therizinosaurus-tarbosaurus-ripples")]
  [string]$Sample = "all",
  [string]$FfmpegPath = "ffmpeg"
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$motionDir = Join-Path $repoRoot "assets\motion"
[System.IO.Directory]::CreateDirectory($motionDir) | Out-Null

if (-not (Get-Command $FfmpegPath -ErrorAction SilentlyContinue)) {
  throw "ffmpeg is required to build the safe M0 motion batch. Pass -FfmpegPath when it is not on PATH."
}

function Invoke-MotionFfmpeg {
  param([string[]]$Arguments)
  & $FfmpegPath @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "ffmpeg failed with exit code $LASTEXITCODE."
  }
}

function Build-MononykusDistantRainsquallSample {
  # M0 safety route: preserve the approved 4:3 poster at its original aspect
  # ratio and translate only one soft, distant rain-curtain layer. The layer
  # stays above the complete animal and foreground throughout the shot.
  $source = Join-Path $repoRoot "assets\dinosaurs\mononykus-olecranus-rainsquall-alert-ecology-imagegen-v3.png"
  $output = Join-Path $motionDir "mononykus-olecranus-distant-rainsquall-environment-m0-v1.mp4"
  $rainRgb = "color=c=0x71808a:s=260x145:r=24:d=5"
  $rainMask = "color=c=black:s=260x145:r=24:d=5,format=gray,drawbox=x=5:y=5:w=250:h=135:color=white@0.075:t=fill,drawbox=x=24:y=8:w=3:h=124:color=white@0.24:t=fill,drawbox=x=48:y=16:w=2:h=116:color=white@0.18:t=fill,drawbox=x=76:y=5:w=3:h=132:color=white@0.26:t=fill,drawbox=x=106:y=13:w=2:h=120:color=white@0.19:t=fill,drawbox=x=136:y=7:w=3:h=128:color=white@0.23:t=fill,drawbox=x=168:y=18:w=2:h=111:color=white@0.17:t=fill,drawbox=x=198:y=9:w=3:h=125:color=white@0.25:t=fill,drawbox=x=228:y=15:w=2:h=114:color=white@0.18:t=fill,gblur=sigma=2.4"
  $filter = "[0:v]split=2[bg0][fg0];[bg0]scale=960:640:force_original_aspect_ratio=increase:flags=lanczos,crop=960:640,gblur=sigma=18[bg];[fg0]scale=960:640:force_original_aspect_ratio=decrease:flags=lanczos[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,format=rgba[base];[1:v]format=rgb24[rw];[2:v]format=gray[rm];[rw][rm]alphamerge[rain];[base][rain]overlay=x='110+10*t':y='60+2*t':eval=frame:format=auto:alpha=straight,scale=in_range=pc:out_range=tv,format=yuv420p[out]"

  Invoke-MotionFfmpeg @(
    "-hide_banner", "-loglevel", "error", "-y",
    "-loop", "1", "-framerate", "24", "-t", "5", "-i", $source,
    "-f", "lavfi", "-t", "5", "-i", $rainRgb,
    "-f", "lavfi", "-t", "5", "-i", $rainMask,
    "-filter_complex", $filter, "-map", "[out]", "-an", "-r", "24", "-t", "5",
    "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
    "-movflags", "+faststart", $output
  )
}

function Build-TherizinosaurusTarbosaurusWatergapRipplesSample {
  # M0 safety route: both animals and every diagnostic limb stay in the fixed
  # poster. Only a narrow ripple patch in the open water gap moves rightward.
  $source = Join-Path $repoRoot "assets\dinosaurs\therizinosaurus-cheloniformis-bilateral-triclaw-tarbosaurus-watergap-ecology-imagegen-v4.png"
  $output = Join-Path $motionDir "therizinosaurus-cheloniformis-tarbosaurus-watergap-ripples-interaction-m0-v1.mp4"
  $rippleRgb = "color=c=0xd6e1df:s=150x32:r=24:d=5"
  $rippleMask = "color=c=black:s=150x32:r=24:d=5,format=gray,drawbox=x=6:y=5:w=106:h=2:color=white@0.38:t=fill,drawbox=x=30:y=14:w=112:h=2:color=white@0.31:t=fill,drawbox=x=12:y=24:w=118:h=2:color=white@0.35:t=fill,gblur=sigma=1.0"
  $filter = "[0:v]scale=960:640:flags=lanczos,format=rgba[base];[1:v]format=rgb24[ww];[2:v]format=gray[wm];[ww][wm]alphamerge[ripples];[base][ripples]overlay=x='165+5*t':y='310+0.6*t':eval=frame:format=auto:alpha=straight,scale=in_range=pc:out_range=tv,format=yuv420p[out]"

  Invoke-MotionFfmpeg @(
    "-hide_banner", "-loglevel", "error", "-y",
    "-loop", "1", "-framerate", "24", "-t", "5", "-i", $source,
    "-f", "lavfi", "-t", "5", "-i", $rippleRgb,
    "-f", "lavfi", "-t", "5", "-i", $rippleMask,
    "-filter_complex", $filter, "-map", "[out]", "-an", "-r", "24", "-t", "5",
    "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
    "-movflags", "+faststart", $output
  )
}

if ($Sample -in @("all", "mononykus-rainsquall")) { Build-MononykusDistantRainsquallSample }
if ($Sample -in @("all", "therizinosaurus-tarbosaurus-ripples")) { Build-TherizinosaurusTarbosaurusWatergapRipplesSample }
