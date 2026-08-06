import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..", "..");
const SOURCE_RELATIVE = "tools/comfyui/outputs/triceratops-horridus-calm-head-lift-wan22-s260806301-f81-v1-candidate.mp4";
const FINAL_RELATIVE = "assets/motion/m2/triceratops-horridus-dust-exhale-wan22-safe-overlay-i2v-m2-v1.mp4";
const WIDTH = 800;
const HEIGHT = 448;
const FRAME_COUNT = 81;
const CHANNELS = 3;
const EFFECT = { x0: 0, y0: 200, x1: 71, y1: 280, startFrame: 10, endFrame: 73 };
const SIGNIFICANT_FLOOR = 5;
const THRESHOLDS = {
  protectedMeanMax: 1.25,
  protectedP99Max: 6,
  protectedMaxMax: 24,
  activeEffectMeanMin: 1.0,
  significantChangeEnergyInsideEffectZoneMinPercent: 8,
};

const errors = [];
const fail = (message) => errors.push(message);
const sha256 = (filePath) => crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");

function percentileFromHistogram(histogram, count, quantile) {
  const target = Math.max(1, Math.ceil(count * quantile));
  let cumulative = 0;
  for (let value = 0; value < histogram.length; value += 1) {
    cumulative += histogram[value];
    if (cumulative >= target) return value;
  }
  return histogram.length - 1;
}

function decodeRgbFile(filePath, owner) {
  if (!fs.existsSync(filePath)) {
    fail(`${owner}: missing ${filePath}`);
    return null;
  }
  const ffmpeg = process.env.FFMPEG_PATH || "ffmpeg";
  const result = spawnSync(ffmpeg, [
    "-v", "error", "-i", filePath, "-map", "0:v:0", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1",
  ], { windowsHide: true, maxBuffer: 256 * 1024 * 1024 });
  if (result.error?.code === "ENOENT") {
    fail(`${owner}: ffmpeg unavailable`);
    return null;
  }
  if (result.status !== 0) {
    fail(`${owner}: ffmpeg decode failed: ${String(result.stderr || "").trim()}`);
    return null;
  }
  const expectedBytes = WIDTH * HEIGHT * FRAME_COUNT * CHANNELS;
  if (result.stdout.length !== expectedBytes) {
    fail(`${owner}: decoded ${result.stdout.length} bytes, expected ${expectedBytes}`);
    return null;
  }
  return { filePath, bytes: result.stdout };
}

function projectPath(relativePath) {
  return path.join(ROOT, ...relativePath.split("/"));
}

function buildTransparentOverlayControl(sourcePath, outputPath) {
  const ffmpeg = process.env.FFMPEG_PATH || "ffmpeg";
  const transparentInput = `color=c=black@0.0:s=${WIDTH}x${HEIGHT}:r=16:d=5.0625,format=rgba`;
  const result = spawnSync(ffmpeg, [
    "-hide_banner", "-loglevel", "error", "-y",
    "-i", sourcePath,
    "-f", "lavfi", "-i", transparentInput,
    "-filter_complex", "[0:v][1:v]overlay=0:0:shortest=1:format=auto,format=yuv420p",
    "-frames:v", String(FRAME_COUNT),
    "-an", "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-movflags", "+faststart",
    outputPath,
  ], { encoding: "utf8", windowsHide: true });
  if (result.error?.code === "ENOENT") fail("control re-encode: ffmpeg unavailable");
  else if (result.status !== 0) fail(`control re-encode failed: ${String(result.stderr || "").trim()}`);
}

const tempRoot = path.resolve(os.tmpdir());
const tempDirectory = fs.mkdtempSync(path.join(tempRoot, "dino-atlas-triceratops-exhale-qa-"));
const controlPath = path.join(tempDirectory, "transparent-overlay-control.mp4");
const sourcePath = projectPath(SOURCE_RELATIVE);
const finalPath = projectPath(FINAL_RELATIVE);
if (!fs.existsSync(sourcePath)) fail(`source base: missing ${SOURCE_RELATIVE}`);
if (!fs.existsSync(finalPath)) fail(`final overlay: missing ${FINAL_RELATIVE}`);
if (fs.existsSync(sourcePath)) buildTransparentOverlayControl(sourcePath, controlPath);
const source = fs.existsSync(controlPath) ? decodeRgbFile(controlPath, "transparent-overlay control") : null;
const final = fs.existsSync(finalPath) ? decodeRgbFile(finalPath, "final overlay") : null;
let metrics = null;

if (source && final) {
  const protectedHistogram = new Uint32Array(256);
  let protectedCount = 0;
  let protectedSum = 0;
  let protectedMax = 0;
  let activeEffectCount = 0;
  let activeEffectSum = 0;
  let significantEffectEnergy = 0;
  let significantTotalEnergy = 0;
  const framePixels = WIDTH * HEIGHT;

  for (let frame = 0; frame < FRAME_COUNT; frame += 1) {
    const active = frame >= EFFECT.startFrame && frame <= EFFECT.endFrame;
    const frameOffset = frame * framePixels * CHANNELS;
    for (let y = 0; y < HEIGHT; y += 1) {
      for (let x = 0; x < WIDTH; x += 1) {
        const insideEffect = x >= EFFECT.x0 && x <= EFFECT.x1
          && y >= EFFECT.y0 && y <= EFFECT.y1;
        const pixelOffset = frameOffset + ((y * WIDTH + x) * CHANNELS);
        for (let channel = 0; channel < CHANNELS; channel += 1) {
          const difference = Math.abs(final.bytes[pixelOffset + channel] - source.bytes[pixelOffset + channel]);
          if (insideEffect && active) {
            activeEffectCount += 1;
            activeEffectSum += difference;
          } else if (!insideEffect) {
            protectedCount += 1;
            protectedSum += difference;
            protectedHistogram[difference] += 1;
            protectedMax = Math.max(protectedMax, difference);
          }
          if (difference >= SIGNIFICANT_FLOOR) {
            significantTotalEnergy += difference;
            if (insideEffect && active) significantEffectEnergy += difference;
          }
        }
      }
    }
  }

  const protectedMean = protectedSum / protectedCount;
  const protectedP99 = percentileFromHistogram(protectedHistogram, protectedCount, 0.99);
  const activeEffectMean = activeEffectSum / activeEffectCount;
  const effectEnergyPercent = significantTotalEnergy
    ? (100 * significantEffectEnergy) / significantTotalEnergy
    : 0;
  metrics = {
    source: {
      path: SOURCE_RELATIVE,
      sha256: sha256(sourcePath),
      bytes: fs.statSync(sourcePath).size,
    },
    final: {
      path: FINAL_RELATIVE,
      sha256: sha256(final.filePath),
      bytes: fs.statSync(final.filePath).size,
    },
    effectZone: EFFECT,
    protectedRegionDifference: {
      mean: Number(protectedMean.toFixed(5)),
      p99: protectedP99,
      max: protectedMax,
    },
    activeEffectDifference: {
      mean: Number(activeEffectMean.toFixed(5)),
      significantChannelDifferenceFloor: SIGNIFICANT_FLOOR,
      significantChangeEnergyInsideEffectZonePercent: Number(effectEnergyPercent.toFixed(5)),
    },
  };

  if (protectedMean > THRESHOLDS.protectedMeanMax) fail("protected-region mean difference exceeds threshold");
  if (protectedP99 > THRESHOLDS.protectedP99Max) fail("protected-region p99 difference exceeds threshold");
  if (protectedMax > THRESHOLDS.protectedMaxMax) fail("protected-region max difference exceeds threshold");
  if (activeEffectMean < THRESHOLDS.activeEffectMeanMin) fail("active effect is too faint");
  if (effectEnergyPercent < THRESHOLDS.significantChangeEnergyInsideEffectZoneMinPercent) {
    fail("significant change energy is not sufficiently concentrated inside the effect zone");
  }
}

const resolvedTempDirectory = path.resolve(tempDirectory);
const tempPrefix = tempRoot.endsWith(path.sep) ? tempRoot : `${tempRoot}${path.sep}`;
if (resolvedTempDirectory.startsWith(tempPrefix)
  && path.basename(resolvedTempDirectory).startsWith("dino-atlas-triceratops-exhale-qa-")) {
  fs.rmSync(resolvedTempDirectory, { recursive: true, force: true });
} else {
  fail("refused to remove an unsafe temporary QA directory");
}

console.log(JSON.stringify({
  schemaVersion: 1,
  stream: { width: WIDTH, height: HEIGHT, frames: FRAME_COUNT, fps: 16, durationSeconds: 5.0625 },
  thresholds: THRESHOLDS,
  metrics,
  errors,
}, null, 2));
if (errors.length) throw new Error(`Triceratops safe-exhale verification failed with ${errors.length} error(s)`);
