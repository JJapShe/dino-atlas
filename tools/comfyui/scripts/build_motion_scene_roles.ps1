param(
  [ValidateSet("all", "psittacosaurus", "maiasaura", "velociraptor-protoceratops")]
  [string]$Sample = "all"
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$motionDir = Join-Path $repoRoot "assets\motion"
[System.IO.Directory]::CreateDirectory($motionDir) | Out-Null

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
  throw "ffmpeg is required to build the M0 scene-role motion samples."
}

function Invoke-MotionFfmpeg {
  param([string[]]$Arguments)
  & ffmpeg @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "ffmpeg failed with exit code $LASTEXITCODE."
  }
}

function Build-PsittacosaurusSoloSample {
  $source = Join-Path $repoRoot "assets\dinosaurs\psittacosaurus-mongoliensis-genus-tail-bristle-anatomy-imagegen-v1.png"
  $output = Join-Path $motionDir "psittacosaurus-mongoliensis-tail-bristle-water-shimmer-solo-m0-v1.mp4"
  $glintRgbA = "color=c=0xe7f4f5:s=210x90:r=24:d=5"
  $glintMaskA = "color=c=black:s=210x90:r=24:d=5,format=gray,drawbox=x=22:y=27:w=132:h=6:color=white@0.38:t=fill,drawbox=x=58:y=47:w=112:h=5:color=white@0.28:t=fill,drawbox=x=104:y=64:w=74:h=4:color=white@0.20:t=fill,gblur=sigma=7"
  $glintRgbB = "color=c=0xd6ecef:s=150x70:r=24:d=5"
  $glintMaskB = "color=c=black:s=150x70:r=24:d=5,format=gray,drawbox=x=18:y=22:w=96:h=5:color=white@0.30:t=fill,drawbox=x=46:y=42:w=82:h=4:color=white@0.22:t=fill,gblur=sigma=6"
  $filter = "[0:v]scale=960:640:flags=lanczos,format=rgba[base];[1:v]format=rgb24[gw1];[2:v]format=gray[gm1];[gw1][gm1]alphamerge,fade=t=in:st=0.35:d=0.75:alpha=1,fade=t=out:st=4.10:d=0.70:alpha=1[glint1];[3:v]format=rgb24[gw2];[4:v]format=gray[gm2];[gw2][gm2]alphamerge,fade=t=in:st=1.10:d=0.70:alpha=1,fade=t=out:st=3.85:d=0.75:alpha=1[glint2];[base][glint1]overlay=x='738+7*t':y='392+2*sin(1.4*t)':format=auto:alpha=straight[g1];[g1][glint2]overlay=x='808-4*t':y='425+2*sin(1.8*t)':format=auto:alpha=straight,scale=in_range=pc:out_range=tv,format=yuv420p[out]"

  Invoke-MotionFfmpeg @(
    "-hide_banner", "-loglevel", "error", "-y",
    "-loop", "1", "-framerate", "24", "-t", "5", "-i", $source,
    "-f", "lavfi", "-t", "5", "-i", $glintRgbA,
    "-f", "lavfi", "-t", "5", "-i", $glintMaskA,
    "-f", "lavfi", "-t", "5", "-i", $glintRgbB,
    "-f", "lavfi", "-t", "5", "-i", $glintMaskB,
    "-filter_complex", $filter, "-map", "[out]", "-an", "-r", "24", "-t", "5",
    "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
    "-movflags", "+faststart", $output
  )
}

function Build-MaiasauraEcologySample {
  $source = Join-Path $repoRoot "assets\dinosaurs\maiasaura-peeblesorum-two-medicine-nesting-ground-egg-hypothesis-portrait-imagegen-v1.png"
  $output = Join-Path $motionDir "maiasaura-peeblesorum-nesting-ground-pollen-ecology-m0-v1.mp4"
  $pollenRgbA = "color=c=0xf2dda8:s=250x92:r=24:d=5"
  $pollenMaskA = "color=c=black:s=250x92:r=24:d=5,format=gray,drawbox=x=8:y=42:w=218:h=16:color=white@0.07:t=fill,drawbox=x=16:y=18:w=7:h=7:color=white@0.48:t=fill,drawbox=x=44:y=53:w=5:h=5:color=white@0.36:t=fill,drawbox=x=78:y=29:w=8:h=8:color=white@0.44:t=fill,drawbox=x=112:y=66:w=5:h=5:color=white@0.34:t=fill,drawbox=x=146:y=35:w=7:h=7:color=white@0.46:t=fill,drawbox=x=184:y=20:w=5:h=5:color=white@0.35:t=fill,drawbox=x=220:y=58:w=8:h=8:color=white@0.40:t=fill,gblur=sigma=2.8"
  $pollenRgbB = "color=c=0xffedc5:s=190x76:r=24:d=5"
  $pollenMaskB = "color=c=black:s=190x76:r=24:d=5,format=gray,drawbox=x=20:y=45:w=7:h=7:color=white@0.36:t=fill,drawbox=x=55:y=18:w=5:h=5:color=white@0.32:t=fill,drawbox=x=92:y=51:w=8:h=8:color=white@0.40:t=fill,drawbox=x=130:y=27:w=5:h=5:color=white@0.34:t=fill,drawbox=x=166:y=58:w=7:h=7:color=white@0.37:t=fill,gblur=sigma=2.6"
  $filter = "[0:v]split=2[bg0][fg0];[bg0]scale=960:640:force_original_aspect_ratio=increase:flags=lanczos,crop=960:640,gblur=sigma=18[bg];[fg0]scale=960:640:force_original_aspect_ratio=decrease:flags=lanczos[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,format=rgba[base];[1:v]format=rgb24[pw1];[2:v]format=gray[pm1];[pw1][pm1]alphamerge,fade=t=in:st=0.30:d=0.70:alpha=1,fade=t=out:st=4.20:d=0.65:alpha=1[pollen1];[3:v]format=rgb24[pw2];[4:v]format=gray[pm2];[pw2][pm2]alphamerge,fade=t=in:st=1.00:d=0.70:alpha=1,fade=t=out:st=3.90:d=0.70:alpha=1[pollen2];[base][pollen1]overlay=x='338+14*t':y='301-3*sin(1.2*t)':format=auto:alpha=straight[p1];[p1][pollen2]overlay=x='420+9*t':y='327-3*sin(1.5*t)':format=auto:alpha=straight,scale=in_range=pc:out_range=tv,format=yuv420p[out]"

  Invoke-MotionFfmpeg @(
    "-hide_banner", "-loglevel", "error", "-y",
    "-loop", "1", "-framerate", "24", "-t", "5", "-i", $source,
    "-f", "lavfi", "-t", "5", "-i", $pollenRgbA,
    "-f", "lavfi", "-t", "5", "-i", $pollenMaskA,
    "-f", "lavfi", "-t", "5", "-i", $pollenRgbB,
    "-f", "lavfi", "-t", "5", "-i", $pollenMaskB,
    "-filter_complex", $filter, "-map", "[out]", "-an", "-r", "24", "-t", "5",
    "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
    "-movflags", "+faststart", $output
  )
}

function Build-VelociraptorProtoceratopsInteractionSample {
  $source = Join-Path $repoRoot "assets\dinosaurs\velociraptor-mongoliensis-protoceratops-standoff-ecology-imagegen-v1.png"
  $output = Join-Path $motionDir "velociraptor-mongoliensis-protoceratops-dustfront-interaction-m0-v1.mp4"
  $dustRgbA = "color=c=0xd7b07c:s=210x118:r=24:d=5"
  $dustMaskA = "color=c=black:s=210x118:r=24:d=5,format=gray,drawbox=x=24:y=28:w=74:h=48:color=white@0.20:t=fill,drawbox=x=78:y=18:w=92:h=66:color=white@0.28:t=fill,drawbox=x=150:y=35:w=38:h=40:color=white@0.18:t=fill,gblur=sigma=21"
  $dustRgbB = "color=c=0xe6c291:s=165x96:r=24:d=5"
  $dustMaskB = "color=c=black:s=165x96:r=24:d=5,format=gray,drawbox=x=18:y=24:w=62:h=42:color=white@0.15:t=fill,drawbox=x=62:y=16:w=82:h=54:color=white@0.23:t=fill,gblur=sigma=18"
  $filter = "[0:v]split=2[bg0][fg0];[bg0]scale=960:640:force_original_aspect_ratio=increase:flags=lanczos,crop=960:640,gblur=sigma=18[bg];[fg0]scale=960:640:force_original_aspect_ratio=decrease:flags=lanczos[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,format=rgba[base];[1:v]format=rgb24[dw1];[2:v]format=gray[dm1];[dw1][dm1]alphamerge,fade=t=in:st=0.20:d=0.75:alpha=1,fade=t=out:st=4.15:d=0.75:alpha=1[dust1];[3:v]format=rgb24[dw2];[4:v]format=gray[dm2];[dw2][dm2]alphamerge,fade=t=in:st=0.85:d=0.70:alpha=1,fade=t=out:st=3.90:d=0.80:alpha=1[dust2];[base][dust1]overlay=x='505-10*t':y='48+3*sin(1.0*t)':format=auto:alpha=straight[d1];[d1][dust2]overlay=x='555-8*t':y='78+2*sin(1.35*t)':format=auto:alpha=straight,scale=in_range=pc:out_range=tv,format=yuv420p[out]"

  Invoke-MotionFfmpeg @(
    "-hide_banner", "-loglevel", "error", "-y",
    "-loop", "1", "-framerate", "24", "-t", "5", "-i", $source,
    "-f", "lavfi", "-t", "5", "-i", $dustRgbA,
    "-f", "lavfi", "-t", "5", "-i", $dustMaskA,
    "-f", "lavfi", "-t", "5", "-i", $dustRgbB,
    "-f", "lavfi", "-t", "5", "-i", $dustMaskB,
    "-filter_complex", $filter, "-map", "[out]", "-an", "-r", "24", "-t", "5",
    "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
    "-movflags", "+faststart", $output
  )
}

if ($Sample -in @("all", "psittacosaurus")) { Build-PsittacosaurusSoloSample }
if ($Sample -in @("all", "maiasaura")) { Build-MaiasauraEcologySample }
if ($Sample -in @("all", "velociraptor-protoceratops")) { Build-VelociraptorProtoceratopsInteractionSample }
