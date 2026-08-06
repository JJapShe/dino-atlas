import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..", "..");
const FFMPEG = process.env.FFMPEG_PATH || "ffmpeg";
const FFPROBE = process.env.FFPROBE_PATH || "ffprobe";
const FPS = 24;
const FRAME_COUNT = 132;
const DURATION_SECONDS = 5.5;
const CHANNELS = 3;
const ENCODE_QP = 12;
const THRESHOLDS = {
  significantChannelDifferenceFloor: 3,
  significantChangeEnergyInsideEffectZoneMinPercent: 95,
  protectedRegionMeanMax: 0.3,
  protectedRegionP99Max: 3,
  protectedRegionMaxMax: 13,
  subjectRegionMeanMax: 0.3,
  subjectRegionP99Max: 3,
  subjectRegionMaxMax: 13,
  activeEffectMeanMin: 1.2,
  effectSignificantChannelPercentMin: 8,
  firstLastEffectMeanMin: 0.5,
};
const SAMPLES = [
  {
    id: "buriolestes-schultzi-candelaria-charcoal-ground-haze-environment-m0-v1",
    sourcePoster: "assets/dinosaurs/buriolestes-schultzi-candelaria-macrocharcoal-wildfire-composite-ecology-imagegen-v1.png",
    finalAsset: "assets/motion/buriolestes-schultzi-candelaria-charcoal-ground-haze-environment-m0-v1.mp4",
    width: 960,
    height: 640,
    effectZone: { x: [25, 455], y: [250, 495] },
    protectedExclusionZone: { x: [15, 465], y: [240, 505] },
    subjectRoi: { x: [575, 945], y: [175, 350] },
    minimumSubjectGap: 110,
  },
  {
    id: "ceratosaurus-nasicornis-horsetail-dawn-water-ring-solo-m0-v1",
    sourcePoster: "assets/dinosaurs/ceratosaurus-nasicornis-horsetail-dawn-drinking-behavior-imagegen-v2.png",
    finalAsset: "assets/motion/ceratosaurus-nasicornis-horsetail-dawn-water-ring-solo-m0-v1.mp4",
    width: 960,
    height: 540,
    effectZone: { x: [0, 300], y: [410, 470] },
    protectedExclusionZone: { x: [0, 310], y: [403, 477] },
    subjectRoi: { x: [80, 940], y: [100, 405] },
    minimumSubjectGap: 5,
  },
];

const errors = [];
const fail = (message) => errors.push(message);
const projectPath = (relativePath) => path.join(ROOT, ...relativePath.split("/"));
const sha256 = (filePath) => crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");

function run(command, args, owner) {
  const result = spawnSync(command, args, { encoding: "utf8", windowsHide: true });
  if (result.error?.code === "ENOENT") throw new Error(`${owner}: executable unavailable`);
  if (result.status !== 0) throw new Error(result.stderr.trim() || `${owner}: exited ${result.status}`);
  return result.stdout;
}

function probeVideo(filePath) {
  const payload = JSON.parse(run(
    FFPROBE,
    ["-v", "error", "-show_streams", "-show_format", "-of", "json", filePath],
    "ffprobe",
  ));
  const video = payload.streams.find((stream) => stream.codec_type === "video");
  const audio = payload.streams.find((stream) => stream.codec_type === "audio");
  const [numerator, denominator] = String(video?.avg_frame_rate || "0/1").split("/").map(Number);
  return {
    width: video?.width,
    height: video?.height,
    fps: denominator ? numerator / denominator : 0,
    frameCount: Number(video?.nb_frames),
    durationSeconds: Number(payload.format?.duration ?? video?.duration),
    codec: video?.codec_name,
    profile: video?.profile,
    pixelFormat: video?.pix_fmt,
    audio: Boolean(audio),
  };
}

function buildTransparentControl(sample, outputPath) {
  const sourcePath = projectPath(sample.sourcePoster);
  const transparentInput = `color=c=black@0.0:s=${sample.width}x${sample.height}:r=${FPS}:d=${DURATION_SECONDS},format=rgba`;
  const filter = `[0:v]scale=${sample.width}:${sample.height}:flags=lanczos,format=rgba[base];[base][1:v]overlay=0:0:shortest=1:format=auto,format=yuv420p[out]`;
  run(FFMPEG, [
    "-hide_banner", "-loglevel", "error", "-y",
    "-loop", "1", "-framerate", String(FPS), "-i", sourcePath,
    "-f", "lavfi", "-i", transparentInput,
    "-filter_complex", filter, "-map", "[out]", "-frames:v", String(FRAME_COUNT),
    "-an", "-c:v", "libx264", "-qp", String(ENCODE_QP), "-preset", "slow", "-profile:v", "high",
    "-pix_fmt", "yuv420p", "-movflags", "+faststart", outputPath,
  ], `${sample.id}: transparent control encode`);
}

function decodeToRaw(filePath, outputPath, owner) {
  run(FFMPEG, [
    "-hide_banner", "-loglevel", "error", "-y", "-i", filePath,
    "-map", "0:v:0", "-frames:v", String(FRAME_COUNT),
    "-pix_fmt", "rgb24", "-f", "rawvideo", outputPath,
  ], `${owner}: RGB decode`);
}

function percentile(histogram, count, fraction) {
  const target = Math.max(1, Math.ceil(count * fraction));
  let cumulative = 0;
  for (let value = 0; value < histogram.length; value += 1) {
    cumulative += histogram[value];
    if (cumulative >= target) return value;
  }
  return histogram.length - 1;
}

function inside(zone, x, y) {
  return x >= zone.x[0] && x < zone.x[1] && y >= zone.y[0] && y < zone.y[1];
}

function rectangleGap(a, b) {
  const horizontalGap = Math.max(a.x[0] - b.x[1], b.x[0] - a.x[1], 0);
  const verticalGap = Math.max(a.y[0] - b.y[1], b.y[0] - a.y[1], 0);
  if (horizontalGap === 0 && verticalGap === 0) return 0;
  return Math.max(horizontalGap, verticalGap);
}

function calculateMetrics(sample, controlRawPath, finalRawPath) {
  const frameBytes = sample.width * sample.height * CHANNELS;
  const expectedBytes = frameBytes * FRAME_COUNT;
  if (fs.statSync(controlRawPath).size !== expectedBytes || fs.statSync(finalRawPath).size !== expectedBytes) {
    throw new Error(`${sample.id}: decoded raw byte count mismatch`);
  }
  const controlHandle = fs.openSync(controlRawPath, "r");
  const finalHandle = fs.openSync(finalRawPath, "r");
  const controlFrame = Buffer.allocUnsafe(frameBytes);
  const finalFrame = Buffer.allocUnsafe(frameBytes);
  let firstFinalFrame = null;
  const protectedHistogram = new Uint32Array(256);
  const subjectHistogram = new Uint32Array(256);
  let protectedCount = 0;
  let protectedSum = 0;
  let protectedMax = 0;
  let subjectCount = 0;
  let subjectSum = 0;
  let subjectMax = 0;
  let effectCount = 0;
  let effectSum = 0;
  let effectSignificantCount = 0;
  let significantTotalEnergy = 0;
  let significantEffectEnergy = 0;
  let firstLastEffectCount = 0;
  let firstLastEffectSum = 0;
  const catalogProtectedHistogram = new Uint32Array(256);
  let catalogProtectedCount = 0;
  let catalogProtectedSum = 0;
  let catalogProtectedMax = 0;
  let catalogEffectCount = 0;
  let catalogEffectSum = 0;
  let catalogEffectSignificantCount = 0;
  let catalogSignificantTotalEnergy = 0;
  let catalogSignificantEffectEnergy = 0;

  try {
    for (let frame = 0; frame < FRAME_COUNT; frame += 1) {
      const position = frame * frameBytes;
      fs.readSync(controlHandle, controlFrame, 0, frameBytes, position);
      fs.readSync(finalHandle, finalFrame, 0, frameBytes, position);
      if (frame === 0) firstFinalFrame = Buffer.from(finalFrame);
      for (let y = 0; y < sample.height; y += 1) {
        for (let x = 0; x < sample.width; x += 1) {
          const isEffect = inside(sample.effectZone, x, y);
          const isExcluded = inside(sample.protectedExclusionZone, x, y);
          const isSubject = inside(sample.subjectRoi, x, y);
          const pixelOffset = (y * sample.width + x) * CHANNELS;
          for (let channel = 0; channel < CHANNELS; channel += 1) {
            const offset = pixelOffset + channel;
            const difference = Math.abs(finalFrame[offset] - controlFrame[offset]);
            if (!isExcluded) {
              protectedCount += 1;
              protectedSum += difference;
              protectedHistogram[difference] += 1;
              if (difference > protectedMax) protectedMax = difference;
            }
            if (isSubject) {
              subjectCount += 1;
              subjectSum += difference;
              subjectHistogram[difference] += 1;
              if (difference > subjectMax) subjectMax = difference;
            }
            if (isEffect) {
              effectCount += 1;
              effectSum += difference;
            }
            if (difference > THRESHOLDS.significantChannelDifferenceFloor) {
              significantTotalEnergy += difference;
              if (isEffect) {
                significantEffectEnergy += difference;
                effectSignificantCount += 1;
              }
            }
            if (frame === FRAME_COUNT - 1) {
              const temporalDifference = Math.abs(finalFrame[offset] - firstFinalFrame[offset]);
              if (!isExcluded) {
                catalogProtectedCount += 1;
                catalogProtectedSum += temporalDifference;
                catalogProtectedHistogram[temporalDifference] += 1;
                if (temporalDifference > catalogProtectedMax) catalogProtectedMax = temporalDifference;
              }
              if (isEffect) {
                firstLastEffectCount += 1;
                firstLastEffectSum += temporalDifference;
                catalogEffectCount += 1;
                catalogEffectSum += temporalDifference;
              }
              if (temporalDifference > THRESHOLDS.significantChannelDifferenceFloor) {
                catalogSignificantTotalEnergy += temporalDifference;
                if (isEffect) {
                  catalogSignificantEffectEnergy += temporalDifference;
                  catalogEffectSignificantCount += 1;
                }
              }
            }
          }
        }
      }
    }
  } finally {
    fs.closeSync(controlHandle);
    fs.closeSync(finalHandle);
  }

  return {
    protectedRegionDifference: {
      mean: Number((protectedSum / protectedCount).toFixed(5)),
      p99: percentile(protectedHistogram, protectedCount, 0.99),
      max: protectedMax,
    },
    subjectRegionDifference: {
      mean: Number((subjectSum / subjectCount).toFixed(5)),
      p99: percentile(subjectHistogram, subjectCount, 0.99),
      max: subjectMax,
    },
    activeEffectDifference: {
      mean: Number((effectSum / effectCount).toFixed(5)),
      significantChannelPercent: Number(((effectSignificantCount / effectCount) * 100).toFixed(5)),
      significantChangeEnergyInsideEffectZonePercent: Number(
        ((significantEffectEnergy / significantTotalEnergy) * 100).toFixed(5),
      ),
    },
    temporalDifference: {
      firstLastEffectMean: Number((firstLastEffectSum / firstLastEffectCount).toFixed(5)),
    },
    catalogComparison: {
      comparisonFrames: [0, FRAME_COUNT - 1],
      protectedRegionDifference: {
        mean: Number((catalogProtectedSum / catalogProtectedCount).toFixed(5)),
        p99: percentile(catalogProtectedHistogram, catalogProtectedCount, 0.99),
        max: catalogProtectedMax,
      },
      effectRegionDifference: {
        mean: Number((catalogEffectSum / catalogEffectCount).toFixed(5)),
        significantChannelPercent: Number(
          ((catalogEffectSignificantCount / catalogEffectCount) * 100).toFixed(5),
        ),
      },
      significantChangeEnergyInsideEffectZonePercent: Number(
        ((catalogSignificantEffectEnergy / catalogSignificantTotalEnergy) * 100).toFixed(5),
      ),
    },
    subjectGapPixels: rectangleGap(sample.effectZone, sample.subjectRoi),
  };
}

function evaluate(sample, stream, metrics) {
  const streamPass = stream.width === sample.width && stream.height === sample.height
    && Math.abs(stream.fps - FPS) <= 0.01 && stream.frameCount === FRAME_COUNT
    && Math.abs(stream.durationSeconds - DURATION_SECONDS) <= 0.05
    && stream.codec === "h264" && stream.profile === "High"
    && stream.pixelFormat === "yuv420p" && stream.audio === false;
  const protectedPass = metrics.protectedRegionDifference.mean <= THRESHOLDS.protectedRegionMeanMax
    && metrics.protectedRegionDifference.p99 <= THRESHOLDS.protectedRegionP99Max
    && metrics.protectedRegionDifference.max <= THRESHOLDS.protectedRegionMaxMax;
  const subjectPass = metrics.subjectRegionDifference.mean <= THRESHOLDS.subjectRegionMeanMax
    && metrics.subjectRegionDifference.p99 <= THRESHOLDS.subjectRegionP99Max
    && metrics.subjectRegionDifference.max <= THRESHOLDS.subjectRegionMaxMax;
  const effectPass = metrics.activeEffectDifference.mean >= THRESHOLDS.activeEffectMeanMin
    && metrics.activeEffectDifference.significantChannelPercent >= THRESHOLDS.effectSignificantChannelPercentMin
    && metrics.activeEffectDifference.significantChangeEnergyInsideEffectZonePercent
      >= THRESHOLDS.significantChangeEnergyInsideEffectZoneMinPercent;
  const temporalPass = metrics.temporalDifference.firstLastEffectMean >= THRESHOLDS.firstLastEffectMeanMin;
  const geometryPass = metrics.subjectGapPixels >= sample.minimumSubjectGap;
  return { streamPass, protectedPass, subjectPass, effectPass, temporalPass, geometryPass };
}

const tempRoot = path.resolve(os.tmpdir());
const tempDirectory = fs.mkdtempSync(path.join(tempRoot, "dino-atlas-era-safe-m0-qa-"));
const results = [];
try {
  for (const sample of SAMPLES) {
    const sourcePath = projectPath(sample.sourcePoster);
    const finalPath = projectPath(sample.finalAsset);
    if (!fs.existsSync(sourcePath)) throw new Error(`${sample.id}: source poster missing`);
    if (!fs.existsSync(finalPath)) throw new Error(`${sample.id}: final asset missing`);
    const controlPath = path.join(tempDirectory, `${sample.id}-control.mp4`);
    const controlRawPath = path.join(tempDirectory, `${sample.id}-control.rgb`);
    const finalRawPath = path.join(tempDirectory, `${sample.id}-final.rgb`);
    buildTransparentControl(sample, controlPath);
    decodeToRaw(controlPath, controlRawPath, sample.id);
    decodeToRaw(finalPath, finalRawPath, sample.id);
    const stream = probeVideo(finalPath);
    const metrics = calculateMetrics(sample, controlRawPath, finalRawPath);
    const gates = evaluate(sample, stream, metrics);
    const status = Object.values(gates).every(Boolean) ? "pass" : "fail";
    if (status === "fail") fail(`${sample.id}: ${JSON.stringify(gates)}`);
    results.push({
      id: sample.id,
      sourcePoster: {
        path: sample.sourcePoster,
        sha256: sha256(sourcePath),
        bytes: fs.statSync(sourcePath).size,
      },
      final: {
        path: sample.finalAsset,
        sha256: sha256(finalPath),
        bytes: fs.statSync(finalPath).size,
        ...stream,
      },
      effectZone: sample.effectZone,
      protectedExclusionZone: sample.protectedExclusionZone,
      subjectRoi: sample.subjectRoi,
      metrics,
      gates,
      status,
    });
  }
} finally {
  const resolved = path.resolve(tempDirectory);
  const tempPrefix = tempRoot.endsWith(path.sep) ? tempRoot : `${tempRoot}${path.sep}`;
  if (resolved.startsWith(tempPrefix) && path.basename(resolved).startsWith("dino-atlas-era-safe-m0-qa-")) {
    fs.rmSync(resolved, { recursive: true, force: true });
  } else {
    fail("refused to remove an unsafe temporary QA directory");
  }
}

console.log(JSON.stringify({
  schemaVersion: 1,
  expectedStream: { fps: FPS, frameCount: FRAME_COUNT, durationSeconds: DURATION_SECONDS },
  thresholds: THRESHOLDS,
  results,
  errors,
}, null, 2));
if (errors.length) throw new Error(`Era-safe M0 verification failed with ${errors.length} error(s)`);
