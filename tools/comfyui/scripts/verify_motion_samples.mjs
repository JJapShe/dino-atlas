import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..", "..");
const CATALOG_PATH = path.join(ROOT, "motion-samples.js");
const METADATA_RELATIVE_PATHS = [
  "tools/comfyui/motion-pilot-batch-20260803.json",
  "tools/comfyui/motion-scene-role-batch-20260803.json",
];
const METADATA_PATHS = METADATA_RELATIVE_PATHS.map((relativePath) => path.join(ROOT, ...relativePath.split("/")));
const EXPECTED_IDS = [
  "yutyrannus-huali-cold-breath-ambient-m0-v1",
  "tyrannosaurus-rex-ground-mist-ambient-m0-v1",
  "brachiosaurus-altithorax-skylight-ambient-m0-v1",
  "psittacosaurus-mongoliensis-water-shimmer-solo-m0-v1",
  "maiasaura-peeblesorum-nesting-ground-pollen-ecology-m0-v1",
  "velociraptor-protoceratops-dustfront-interaction-m0-v1",
];
const ALLOWED_SCENE_ROLES = new Set(["solo", "ecology-activity", "interspecies-interaction"]);
const errors = [];
const warnings = [];

function fail(message) {
  errors.push(message);
}

function warn(message) {
  warnings.push(message);
}

function isNonEmptyString(value) {
  return typeof value === "string" && value.trim().length > 0;
}

function projectPath(relativePath, owner) {
  if (!isNonEmptyString(relativePath)) {
    fail(`${owner}: missing project path`);
    return null;
  }
  if (/\.codex[\\/]generated_images/i.test(relativePath)) {
    fail(`${owner}: generator-area path is prohibited`);
    return null;
  }
  const absolutePath = path.resolve(ROOT, relativePath);
  const relativeCheck = path.relative(ROOT, absolutePath);
  if (relativeCheck.startsWith("..") || path.isAbsolute(relativeCheck)) {
    fail(`${owner}: path escapes project root`);
    return null;
  }
  return absolutePath;
}

function sha256(filePath) {
  return crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");
}

function probeVideo(filePath) {
  const result = spawnSync(
    process.env.FFPROBE_PATH || "ffprobe",
    ["-v", "error", "-show_streams", "-show_format", "-of", "json", filePath],
    { encoding: "utf8", windowsHide: true },
  );
  if (result.error?.code === "ENOENT") return { unavailable: true };
  if (result.status !== 0) return { error: result.stderr.trim() || `ffprobe exited ${result.status}` };
  try {
    const payload = JSON.parse(result.stdout);
    const video = payload.streams?.find((stream) => stream.codec_type === "video");
    const audio = payload.streams?.find((stream) => stream.codec_type === "audio");
    const [numerator, denominator] = String(video?.avg_frame_rate || "0/1").split("/").map(Number);
    return {
      width: video?.width,
      height: video?.height,
      fps: denominator ? numerator / denominator : 0,
      codec: video?.codec_name,
      pixelFormat: video?.pix_fmt,
      durationSeconds: Number(payload.format?.duration ?? video?.duration),
      audio: Boolean(audio),
    };
  } catch (error) {
    return { error: `invalid ffprobe JSON: ${error.message}` };
  }
}

function validateZone(zone, width, height, owner, label) {
  const x = zone?.x;
  const y = zone?.y;
  const valid =
    Array.isArray(x) && x.length === 2 && x.every(Number.isInteger) &&
    Array.isArray(y) && y.length === 2 && y.every(Number.isInteger) &&
    x[0] >= 0 && x[0] < x[1] && x[1] <= width &&
    y[0] >= 0 && y[0] < y[1] && y[1] <= height;
  if (!valid) {
    fail(`${owner}: invalid ${label} for ${width}x${height}`);
    return null;
  }
  return { x1: x[0], x2: x[1], y1: y[0], y2: y[1] };
}

function extractComparisonFrames(filePath, frames, width, height) {
  const result = spawnSync(
    process.env.FFMPEG_PATH || "ffmpeg",
    [
      "-v", "error", "-i", filePath,
      "-vf", `select=eq(n\\,${frames[0]})+eq(n\\,${frames[1]}),format=rgb24`,
      "-fps_mode", "vfr", "-frames:v", "2", "-an", "-f", "rawvideo", "pipe:1",
    ],
    {
      encoding: null,
      windowsHide: true,
      maxBuffer: width * height * 3 * 3,
    },
  );
  if (result.error?.code === "ENOENT") return { unavailable: true };
  if (result.status !== 0) {
    return { error: result.stderr?.toString("utf8").trim() || `ffmpeg exited ${result.status}` };
  }
  const frameBytes = width * height * 3;
  if (result.stdout.length !== frameBytes * 2) {
    return { error: `expected ${frameBytes * 2} raw RGB bytes, received ${result.stdout.length}` };
  }
  return {
    first: result.stdout.subarray(0, frameBytes),
    second: result.stdout.subarray(frameBytes),
  };
}

function percentileFromHistogram(histogram, count, percentile) {
  const target = Math.ceil(count * percentile);
  let cumulative = 0;
  for (let value = 0; value < histogram.length; value += 1) {
    cumulative += histogram[value];
    if (cumulative >= target) return value;
  }
  return histogram.length - 1;
}

function calculateMotionQa(first, second, width, effectZone, protectedExclusionZone, differenceFloor) {
  const protectedHistogram = new Uint32Array(256);
  let protectedCount = 0;
  let protectedSum = 0;
  let protectedMax = 0;
  let significantEnergy = 0;
  let effectSignificantEnergy = 0;

  for (let offset = 0; offset < first.length; offset += 1) {
    const pixel = Math.floor(offset / 3);
    const y = Math.floor(pixel / width);
    const x = pixel - y * width;
    const difference = Math.abs(second[offset] - first[offset]);
    const insideEffect =
      x >= effectZone.x1 && x < effectZone.x2 && y >= effectZone.y1 && y < effectZone.y2;
    const insideProtectedExclusion =
      x >= protectedExclusionZone.x1 && x < protectedExclusionZone.x2 &&
      y >= protectedExclusionZone.y1 && y < protectedExclusionZone.y2;

    if (difference > differenceFloor) {
      significantEnergy += difference;
      if (insideEffect) effectSignificantEnergy += difference;
    }
    if (!insideProtectedExclusion) {
      protectedCount += 1;
      protectedSum += difference;
      protectedHistogram[difference] += 1;
      if (difference > protectedMax) protectedMax = difference;
    }
  }

  return {
    protectedMean: protectedCount ? protectedSum / protectedCount : 0,
    protectedP99: percentileFromHistogram(protectedHistogram, protectedCount, 0.99),
    protectedMax,
    significantChangeEnergyInsideEffectZonePercent:
      significantEnergy ? (effectSignificantEnergy / significantEnergy) * 100 : 0,
  };
}

const catalogSource = fs.readFileSync(CATALOG_PATH, "utf8");
const metadataSources = METADATA_PATHS.map((metadataPath) => fs.readFileSync(metadataPath, "utf8"));
const sandbox = { window: {} };
new vm.Script(catalogSource, { filename: CATALOG_PATH }).runInNewContext(sandbox);
const catalog = sandbox.window.motionSampleCatalog;
const metadataBatches = metadataSources.map((source, index) => ({
  relativePath: METADATA_RELATIVE_PATHS[index],
  metadata: JSON.parse(source),
}));

if (!catalog || typeof catalog !== "object") throw new Error("motionSampleCatalog was not exported");
if (/\.codex[\\/]generated_images/i.test(catalogSource)) fail("catalog: generator-area path leak");
for (const [index, metadataSource] of metadataSources.entries()) {
  if (/\.codex[\\/]generated_images/i.test(metadataSource)) {
    fail(`${METADATA_RELATIVE_PATHS[index]}: generator-area path leak`);
  }
}
if (catalog.schemaVersion !== 1 || metadataBatches.some(({ metadata }) => metadata.schemaVersion !== 1)) {
  fail("schemaVersion must be 1");
}
if (catalog.policy?.tier !== "M0" || metadataBatches.some(({ metadata }) => metadata.policy?.tier !== "M0")) {
  fail("policy tier must be M0");
}
for (const policy of [catalog.policy, ...metadataBatches.map(({ metadata }) => metadata.policy)]) {
  if (policy?.representativePromotion !== "prohibited") fail("representative promotion must be prohibited");
  if (policy?.galleryPromotion !== "prohibited") fail("gallery promotion must be prohibited");
  if (policy?.autoplay !== "prohibited") fail("autoplay must be prohibited");
  if (policy?.biologicalMotion !== "prohibited in M0") fail("biological motion must be prohibited in M0");
  if (JSON.stringify(policy?.sceneRoles) !== JSON.stringify([...ALLOWED_SCENE_ROLES])) {
    fail("sceneRoles policy must match the M0 allowlist");
  }
}

const motionQaThresholds = metadataBatches[0]?.metadata?.workflow?.motionQaThresholds;
const requiredMotionQaThresholds = [
  "significantChannelDifferenceFloor",
  "significantChangeEnergyInsideEffectZoneMinPercent",
  "protectedRegionMeanMax",
  "protectedRegionP99Max",
  "protectedRegionMaxMax",
];
if (!motionQaThresholds || requiredMotionQaThresholds.some(
  (field) => !Number.isFinite(motionQaThresholds[field]) || motionQaThresholds[field] < 0,
)) {
  fail("metadata: complete non-negative motion QA thresholds are required");
}
for (const { relativePath, metadata } of metadataBatches.slice(1)) {
  if (JSON.stringify(metadata.workflow?.motionQaThresholds) !== JSON.stringify(motionQaThresholds)) {
    fail(`${relativePath}: motion QA thresholds must match the primary M0 batch`);
  }
}

const samples = Array.isArray(catalog.samples) ? catalog.samples : [];
const ids = samples.map((sample) => sample.id);
if (JSON.stringify(ids) !== JSON.stringify(EXPECTED_IDS)) {
  fail(`catalog samples must be ordered as ${EXPECTED_IDS.join(", ")}`);
}

const seenSources = new Set();
let existingVideos = 0;
let fullyRecordedVideos = 0;
let publishedVideos = 0;

for (const sample of samples) {
  const owner = sample?.id || "sample:(blank)";
  let motionQaContext = null;
  if (!EXPECTED_IDS.includes(sample.id)) fail(`${owner}: unexpected id`);
  if (sample.tier !== "M0" || sample.motionClass !== "environment-only") {
    fail(`${owner}: must remain an M0 environment-only sample`);
  }
  if (!ALLOWED_SCENE_ROLES.has(sample.sceneRole) || !isNonEmptyString(sample.sceneRoleLabel)) {
    fail(`${owner}: valid sceneRole and sceneRoleLabel are required`);
  }
  if (sample.representativeEligible !== false || sample.galleryEligible !== false) {
    fail(`${owner}: representative and gallery eligibility must both be false`);
  }
  if (!isNonEmptyString(sample.title) || !isNonEmptyString(sample.description)
    || !isNonEmptyString(sample.motionLabel)) {
    fail(`${owner}: user-facing title, description, and motion label are required`);
  }
  if (!/^assets\/dinosaurs\/[a-z0-9][a-z0-9.-]*\.png$/i.test(sample.poster || "")) {
    fail(`${owner}: poster must be a project PNG under assets/dinosaurs`);
  }
  if (!/^assets\/motion\/[a-z0-9][a-z0-9.-]*-m0-v[0-9]+\.mp4$/i.test(sample.src || "")) {
    fail(`${owner}: video must be a versioned M0 MP4 under assets/motion`);
  }
  if (seenSources.has(sample.src)) fail(`${owner}: duplicate video source ${sample.src}`);
  seenSources.add(sample.src);

  const posterPath = projectPath(sample.poster, `${owner}: poster`);
  if (posterPath && !fs.existsSync(posterPath)) fail(`${owner}: missing poster ${sample.poster}`);
  const videoPath = projectPath(sample.src, `${owner}: video`);
  const metadataBatch = metadataBatches.find(({ metadata }) => metadata.samples?.[sample.id]);
  const record = metadataBatch?.metadata?.samples?.[sample.id];
  if (!record) {
    fail(`${owner}: missing metadata record`);
    continue;
  }
  if (record.sourcePoster !== sample.poster || record.projectAsset !== sample.src) {
    fail(`${owner}: catalog and metadata paths differ`);
  }
  if (record.motionClass !== sample.motionClass || record.sceneRole !== sample.sceneRole
    || record.review?.representativeEligible !== false
    || record.review?.galleryEligible !== false) {
    fail(`${owner}: catalog and metadata role gates differ`);
  }
  if (!isNonEmptyString(record.prompt) || !isNonEmptyString(record.motionLayer)) {
    fail(`${owner}: prompt and motion-layer records are required`);
  }
  const metadataRecord = sample.provenance?.metadataRecord || "";
  if (metadataRecord !== `${metadataBatch.relativePath}#/samples/${sample.id}`) {
    fail(`${owner}: invalid metadataRecord pointer`);
  }
  for (const gate of ["anatomy", "motion", "responsive", "publication"]) {
    if (!isNonEmptyString(sample.review?.[gate]?.status) || !isNonEmptyString(sample.review?.[gate]?.note)) {
      fail(`${owner}: incomplete ${gate} review gate`);
    }
    if (sample.review?.[gate]?.status !== record.review?.[gate]?.status) {
      fail(`${owner}: catalog and metadata ${gate} status differ`);
    }
  }

  const isPublished = sample.review?.publication?.status === "published";
  if (isPublished) {
    publishedVideos += 1;
    if (sample.review?.motion?.status !== "supported" || sample.review?.responsive?.status !== "supported") {
      fail(`${owner}: published without motion and responsive support`);
    }
    if (!isNonEmptyString(metadataBatch.metadata.workflow?.commands?.[sample.id])) {
      fail(`${owner}: published without an exact workflow command`);
    }
    const motionQa = record.motionQa;
    const frames = motionQa?.comparisonFrames;
    const fileWidth = sample.file?.width;
    const fileHeight = sample.file?.height;
    const validFrames =
      Array.isArray(frames) && frames.length === 2 && frames.every(Number.isInteger) &&
      frames[0] >= 0 && frames[0] < frames[1];
    if (!motionQa || motionQa.visualStatus !== "pass" || !validFrames) {
      fail(`${owner}: published without a passing motionQa record and comparison frames`);
    } else if (!Number.isFinite(fileWidth) || !Number.isFinite(fileHeight)) {
      fail(`${owner}: motionQa zones require recorded video dimensions`);
    } else {
      const effectZone = validateZone(motionQa.effectZone, fileWidth, fileHeight, owner, "effectZone");
      const protectedExclusionZone = validateZone(
        motionQa.protectedExclusionZone,
        fileWidth,
        fileHeight,
        owner,
        "protectedExclusionZone",
      );
      const protectedDifference = motionQa.protectedRegionDifference;
      const recordedMetricsValid =
        Number.isFinite(protectedDifference?.mean) && protectedDifference.mean >= 0 &&
        Number.isFinite(protectedDifference?.p99) && protectedDifference.p99 >= 0 &&
        Number.isFinite(protectedDifference?.max) && protectedDifference.max >= 0 &&
        Number.isFinite(motionQa.significantChangeEnergyInsideEffectZonePercent) &&
        motionQa.significantChangeEnergyInsideEffectZonePercent >= 0 &&
        motionQa.significantChangeEnergyInsideEffectZonePercent <= 100;
      if (!recordedMetricsValid) fail(`${owner}: motionQa metrics are incomplete or out of range`);
      if (effectZone && protectedExclusionZone) {
        const effectInsideExclusion =
          effectZone.x1 >= protectedExclusionZone.x1 && effectZone.x2 <= protectedExclusionZone.x2 &&
          effectZone.y1 >= protectedExclusionZone.y1 && effectZone.y2 <= protectedExclusionZone.y2;
        if (!effectInsideExclusion) fail(`${owner}: effectZone must fit inside protectedExclusionZone`);
      }
      if (recordedMetricsValid && motionQaThresholds) {
        if (motionQa.significantChangeEnergyInsideEffectZonePercent <
          motionQaThresholds.significantChangeEnergyInsideEffectZoneMinPercent) {
          fail(`${owner}: recorded significant-change energy misses the motion QA threshold`);
        }
        if (protectedDifference.mean > motionQaThresholds.protectedRegionMeanMax ||
          protectedDifference.p99 > motionQaThresholds.protectedRegionP99Max ||
          protectedDifference.max > motionQaThresholds.protectedRegionMaxMax) {
          fail(`${owner}: recorded protected-region differences miss the motion QA thresholds`);
        }
        const percentLabel = motionQa.significantChangeEnergyInsideEffectZonePercent.toFixed(2);
        if (!sample.review.motion.note.includes(percentLabel)) {
          fail(`${owner}: catalog motion note does not cite the recorded ${percentLabel}% result`);
        }
      }
      if (effectZone && protectedExclusionZone && recordedMetricsValid) {
        motionQaContext = { motionQa, frames, effectZone, protectedExclusionZone };
      }
    }
  }

  if (!videoPath || !fs.existsSync(videoPath)) {
    if (isPublished) fail(`${owner}: published video is missing`);
    else warn(`${owner}: draft video is not present yet`);
    continue;
  }
  existingVideos += 1;
  const stat = fs.statSync(videoPath);
  const digest = sha256(videoPath);
  const fileRecord = sample.file || {};
  const metadataFile = record.file || {};
  const requiredFileFields = ["sha256", "bytes", "width", "height", "durationSeconds", "fps", "codec"];
  const fileComplete = requiredFileFields.every((field) => fileRecord[field] !== null && fileRecord[field] !== undefined);
  if (!fileComplete) {
    if (isPublished) fail(`${owner}: published file metadata is incomplete`);
    else warn(`${owner}: video exists but final file metadata is pending`);
  } else {
    fullyRecordedVideos += 1;
    if (fileRecord.sha256 !== digest || fileRecord.bytes !== stat.size) fail(`${owner}: hash or byte count mismatch`);
    for (const field of requiredFileFields) {
      if (metadataFile[field] !== fileRecord[field]) fail(`${owner}: metadata file.${field} differs from catalog`);
    }
  }

  const probe = probeVideo(videoPath);
  if (probe.unavailable) {
    warn(`${owner}: ffprobe unavailable; stream properties were not independently checked`);
  } else if (probe.error) {
    fail(`${owner}: ${probe.error}`);
  } else {
    if (probe.audio) fail(`${owner}: M0 pilot must not contain audio`);
    if (probe.pixelFormat !== "yuv420p") fail(`${owner}: pixel format must be yuv420p`);
    if (fileComplete) {
      if (fileRecord.width !== probe.width || fileRecord.height !== probe.height
        || Math.abs(fileRecord.durationSeconds - probe.durationSeconds) > 0.05
        || Math.abs(fileRecord.fps - probe.fps) > 0.05
        || fileRecord.codec !== probe.codec) {
        fail(`${owner}: recorded stream properties do not match ffprobe`);
      }
    }
  }

  if (motionQaContext && motionQaThresholds) {
    const decoded = extractComparisonFrames(
      videoPath,
      motionQaContext.frames,
      sample.file.width,
      sample.file.height,
    );
    if (decoded.unavailable) {
      warn(`${owner}: ffmpeg unavailable; motionQa pixels were not independently recalculated`);
    } else if (decoded.error) {
      fail(`${owner}: motionQa frame extraction failed: ${decoded.error}`);
    } else {
      const calculated = calculateMotionQa(
        decoded.first,
        decoded.second,
        sample.file.width,
        motionQaContext.effectZone,
        motionQaContext.protectedExclusionZone,
        motionQaThresholds.significantChannelDifferenceFloor,
      );
      const recorded = motionQaContext.motionQa;
      const recordedProtected = recorded.protectedRegionDifference;
      if (Math.abs(calculated.protectedMean - recordedProtected.mean) > 0.005 ||
        calculated.protectedP99 !== recordedProtected.p99 ||
        calculated.protectedMax !== recordedProtected.max ||
        Math.abs(
          calculated.significantChangeEnergyInsideEffectZonePercent -
          recorded.significantChangeEnergyInsideEffectZonePercent
        ) > 0.05) {
        fail(`${owner}: recorded motionQa metrics do not match decoded comparison frames (${JSON.stringify(calculated)})`);
      }
      if (calculated.significantChangeEnergyInsideEffectZonePercent <
        motionQaThresholds.significantChangeEnergyInsideEffectZoneMinPercent ||
        calculated.protectedMean > motionQaThresholds.protectedRegionMeanMax ||
        calculated.protectedP99 > motionQaThresholds.protectedRegionP99Max ||
        calculated.protectedMax > motionQaThresholds.protectedRegionMaxMax) {
        fail(`${owner}: decoded comparison frames miss the motion QA thresholds`);
      }
    }
  }
}

for (const { relativePath, metadata } of metadataBatches) {
  const orphanMetadata = Object.keys(metadata.samples || {}).filter((id) => !ids.includes(id));
  if (orphanMetadata.length) fail(`${relativePath}: orphan samples ${orphanMetadata.join(", ")}`);
}

const report = {
  schemaVersion: catalog.schemaVersion,
  sampleCount: samples.length,
  existingVideos,
  fullyRecordedVideos,
  publishedVideos,
  policy: {
    tier: catalog.policy?.tier,
    scope: catalog.policy?.scope,
    representativePromotion: catalog.policy?.representativePromotion,
    galleryPromotion: catalog.policy?.galleryPromotion,
    autoplay: catalog.policy?.autoplay,
  },
  warnings,
  errors,
};

console.log(JSON.stringify(report, null, 2));
if (errors.length) process.exitCode = 1;
