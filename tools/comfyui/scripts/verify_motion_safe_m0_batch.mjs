import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..", "..");
const FFMPEG = process.env.FFMPEG_PATH || "ffmpeg";
const FFPROBE = process.env.FFPROBE_PATH || "ffprobe";
const WIDTH = 960;
const HEIGHT = 640;
const FRAME_BYTES = WIDTH * HEIGHT * 3;
const THRESHOLDS = {
  significantChannelDifferenceFloor: 3,
  significantChangeEnergyInsideEffectZoneMinPercent: 95,
  protectedRegionMeanMax: 0.3,
  protectedRegionP99Max: 3,
  protectedRegionMaxMax: 13,
};
const SAMPLES = [
  {
    id: "mononykus-olecranus-distant-rainsquall-environment-m0-v1",
    relativePath: "assets/motion/mononykus-olecranus-distant-rainsquall-environment-m0-v1.mp4",
    comparisonFrames: [0, 119],
    effectZone: { x: [100, 430], y: [50, 225] },
    protectedExclusionZone: { x: [90, 440], y: [40, 235] },
  },
  {
    id: "therizinosaurus-cheloniformis-tarbosaurus-watergap-ripples-interaction-m0-v1",
    relativePath: "assets/motion/therizinosaurus-cheloniformis-tarbosaurus-watergap-ripples-interaction-m0-v1.mp4",
    comparisonFrames: [0, 119],
    effectZone: { x: [160, 345], y: [300, 350] },
    protectedExclusionZone: { x: [150, 350], y: [295, 355] },
  },
];

function sha256(filePath) {
  return crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");
}

function probeVideo(filePath) {
  const result = spawnSync(
    FFPROBE,
    ["-v", "error", "-show_streams", "-show_format", "-of", "json", filePath],
    { encoding: "utf8", windowsHide: true },
  );
  if (result.status !== 0) throw new Error(result.stderr.trim() || `ffprobe exited ${result.status}`);
  const payload = JSON.parse(result.stdout);
  const video = payload.streams.find((stream) => stream.codec_type === "video");
  const audio = payload.streams.find((stream) => stream.codec_type === "audio");
  const [numerator, denominator] = String(video.avg_frame_rate).split("/").map(Number);
  return {
    width: video.width,
    height: video.height,
    fps: numerator / denominator,
    codec: video.codec_name,
    pixelFormat: video.pix_fmt,
    durationSeconds: Number(payload.format.duration),
    audio: Boolean(audio),
  };
}

function extractFrames(filePath, frames) {
  const result = spawnSync(
    FFMPEG,
    [
      "-v", "error", "-i", filePath,
      "-vf", `select=eq(n\\,${frames[0]})+eq(n\\,${frames[1]}),format=rgb24`,
      "-fps_mode", "vfr", "-frames:v", "2", "-an", "-f", "rawvideo", "pipe:1",
    ],
    { encoding: null, windowsHide: true, maxBuffer: FRAME_BYTES * 3 },
  );
  if (result.status !== 0) {
    throw new Error(result.stderr?.toString("utf8").trim() || `ffmpeg exited ${result.status}`);
  }
  if (result.stdout.length !== FRAME_BYTES * 2) {
    throw new Error(`expected ${FRAME_BYTES * 2} RGB bytes, received ${result.stdout.length}`);
  }
  return [result.stdout.subarray(0, FRAME_BYTES), result.stdout.subarray(FRAME_BYTES)];
}

function inside(zone, x, y) {
  return x >= zone.x[0] && x < zone.x[1] && y >= zone.y[0] && y < zone.y[1];
}

function percentile(histogram, count, fraction) {
  const target = Math.ceil(count * fraction);
  let total = 0;
  for (let value = 0; value < histogram.length; value += 1) {
    total += histogram[value];
    if (total >= target) return value;
  }
  return histogram.length - 1;
}

function calculate(first, second, sample) {
  const protectedHistogram = new Uint32Array(256);
  let protectedCount = 0;
  let protectedSum = 0;
  let protectedMax = 0;
  let significantEnergy = 0;
  let effectSignificantEnergy = 0;
  let effectCount = 0;
  let effectSum = 0;
  let effectSignificantCount = 0;

  for (let offset = 0; offset < first.length; offset += 1) {
    const pixel = Math.floor(offset / 3);
    const y = Math.floor(pixel / WIDTH);
    const x = pixel - y * WIDTH;
    const difference = Math.abs(second[offset] - first[offset]);
    const isInsideEffect = inside(sample.effectZone, x, y);
    if (isInsideEffect) {
      effectCount += 1;
      effectSum += difference;
    }
    if (difference > THRESHOLDS.significantChannelDifferenceFloor) {
      significantEnergy += difference;
      if (isInsideEffect) {
        effectSignificantEnergy += difference;
        effectSignificantCount += 1;
      }
    }
    if (!inside(sample.protectedExclusionZone, x, y)) {
      protectedCount += 1;
      protectedSum += difference;
      protectedHistogram[difference] += 1;
      if (difference > protectedMax) protectedMax = difference;
    }
  }

  return {
    protectedRegionDifference: {
      mean: Number((protectedSum / protectedCount).toFixed(5)),
      p99: percentile(protectedHistogram, protectedCount, 0.99),
      max: protectedMax,
    },
    effectRegionDifference: {
      mean: Number((effectSum / effectCount).toFixed(5)),
      significantChannelPercent: Number(((effectSignificantCount / effectCount) * 100).toFixed(5)),
    },
    significantChangeEnergyInsideEffectZonePercent: Number(
      ((effectSignificantEnergy / significantEnergy) * 100).toFixed(5),
    ),
  };
}

const results = [];
let failed = false;
for (const sample of SAMPLES) {
  const filePath = path.join(ROOT, ...sample.relativePath.split("/"));
  if (!fs.existsSync(filePath)) throw new Error(`${sample.id}: output is missing`);
  const stat = fs.statSync(filePath);
  const probe = probeVideo(filePath);
  const [first, last] = extractFrames(filePath, sample.comparisonFrames);
  const metrics = calculate(first, last, sample);
  const streamPass = probe.width === WIDTH && probe.height === HEIGHT && probe.codec === "h264"
    && probe.pixelFormat === "yuv420p" && Math.abs(probe.durationSeconds - 5) <= 0.05
    && Math.abs(probe.fps - 24) <= 0.05 && probe.audio === false;
  const motionPass = metrics.significantChangeEnergyInsideEffectZonePercent
      >= THRESHOLDS.significantChangeEnergyInsideEffectZoneMinPercent
    && metrics.protectedRegionDifference.mean <= THRESHOLDS.protectedRegionMeanMax
    && metrics.protectedRegionDifference.p99 <= THRESHOLDS.protectedRegionP99Max
    && metrics.protectedRegionDifference.max <= THRESHOLDS.protectedRegionMaxMax;
  if (!streamPass || !motionPass) failed = true;
  results.push({
    id: sample.id,
    file: { sha256: sha256(filePath), bytes: stat.size, ...probe },
    motionQa: {
      comparisonFrames: sample.comparisonFrames,
      effectZone: sample.effectZone,
      protectedExclusionZone: sample.protectedExclusionZone,
      ...metrics,
    },
    status: streamPass && motionPass ? "pass" : "fail",
  });
}

console.log(JSON.stringify({ thresholds: THRESHOLDS, results }, null, 2));
if (failed) process.exitCode = 1;
