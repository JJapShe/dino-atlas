import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..", "..");
const CATALOG_RELATIVE_PATH = "motion-m1-samples.js";
const METADATA_RELATIVE_PATH = "tools/comfyui/motion-m1-pilot-batch-20260803.json";
const CATALOG_PATH = path.join(ROOT, CATALOG_RELATIVE_PATH);
const METADATA_PATH = path.join(ROOT, ...METADATA_RELATIVE_PATH.split("/"));
const EXPECTED_ID = "oviraptor-philoceratops-blink-headtilt-biological-m1-v1";
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

function probeMedia(filePath) {
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

function validateFramePair(frames, owner, label) {
  const valid =
    Array.isArray(frames) && frames.length === 2 && frames.every(Number.isInteger) &&
    frames[0] >= 0 && frames[0] < frames[1] && frames[1] < 120;
  if (!valid) fail(`${owner}: invalid ${label}`);
  return valid ? frames : null;
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

function calculatePairQa(first, second, width, effectZone, protectedExclusionZone, differenceFloor) {
  const protectedHistogram = new Uint32Array(256);
  let protectedCount = 0;
  let protectedSum = 0;
  let protectedMax = 0;
  let significantEnergy = 0;
  let effectSignificantEnergy = 0;
  let allDifferenceSum = 0;

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

    allDifferenceSum += difference;
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
    significantEnergyInsideZone: effectSignificantEnergy,
    significantChangeEnergyInsideZonePercent:
      significantEnergy ? (effectSignificantEnergy / significantEnergy) * 100 : 0,
    protectedRegionDifference: {
      mean: protectedCount ? protectedSum / protectedCount : 0,
      p99: percentileFromHistogram(protectedHistogram, protectedCount, 0.99),
      max: protectedMax,
    },
    wholeFrameMeanDifference: first.length ? allDifferenceSum / first.length : 0,
  };
}

function compareNumber(actual, recorded, tolerance, owner) {
  if (!Number.isFinite(recorded) || Math.abs(actual - recorded) > tolerance) {
    fail(`${owner}: recorded ${recorded} does not match decoded ${actual}`);
  }
}

function checkFileRecord(relativePath, record, owner) {
  const absolutePath = projectPath(relativePath, owner);
  if (!absolutePath || !fs.existsSync(absolutePath)) {
    fail(`${owner}: missing ${relativePath}`);
    return null;
  }
  const stat = fs.statSync(absolutePath);
  if (sha256(absolutePath) !== record?.sha256 || stat.size !== record?.bytes) {
    fail(`${owner}: hash or byte count mismatch`);
  }
  return absolutePath;
}

const catalogSource = fs.readFileSync(CATALOG_PATH, "utf8");
const metadataSource = fs.readFileSync(METADATA_PATH, "utf8");
const sandbox = { window: {} };
new vm.Script(catalogSource, { filename: CATALOG_PATH }).runInNewContext(sandbox);
const catalog = sandbox.window.motionM1SampleCatalog;
const metadata = JSON.parse(metadataSource);

if (!catalog || typeof catalog !== "object") throw new Error("motionM1SampleCatalog was not exported");
if (/\.codex[\\/]generated_images/i.test(catalogSource) || /\.codex[\\/]generated_images/i.test(metadataSource)) {
  fail("generator-area path leak");
}
if (catalog.schemaVersion !== 1 || metadata.schemaVersion !== 1) fail("schemaVersion must be 1");
for (const policy of [catalog.policy, metadata.policy]) {
  if (policy?.tier !== "M1") fail("policy tier must be M1");
  if (policy?.representativePromotion !== "prohibited") fail("representative promotion must be prohibited");
  if (policy?.galleryPromotion !== "prohibited") fail("gallery promotion must be prohibited");
  if (policy?.autoplay !== "prohibited") fail("autoplay must be prohibited");
  if (policy?.locomotion !== "prohibited in M1") fail("locomotion must be prohibited in M1");
  if (!Array.isArray(policy?.allowedMotion) || !policy.allowedMotion.includes("natural blink")
    || !policy.allowedMotion.includes("sub-degree rigid head-and-neck tilt")) {
    fail("M1 allowed-motion policy is incomplete");
  }
}
if (catalog.policy?.loop !== "prohibited" || catalog.policy?.clickToPlay !== "required"
  || catalog.policy?.audio !== "prohibited") {
  fail("M1 catalog must require click-to-play and prohibit audio and looping");
}

const samples = Array.isArray(catalog.samples) ? catalog.samples : [];
if (samples.length !== 1 || samples[0]?.id !== EXPECTED_ID) {
  fail(`catalog must contain exactly ${EXPECTED_ID}`);
}

let calculatedQa = null;
let publishedVideos = 0;
for (const sample of samples) {
  const owner = sample?.id || "sample:(blank)";
  const record = metadata.samples?.[sample.id];
  if (!record) {
    fail(`${owner}: missing metadata record`);
    continue;
  }
  if (sample.tier !== "M1" || sample.motionClass !== "biological-micro" || sample.sceneRole !== "solo") {
    fail(`${owner}: must remain an M1 biological-micro solo sample`);
  }
  if (sample.representativeEligible !== false || sample.galleryEligible !== false
    || record.review?.representativeEligible !== false || record.review?.galleryEligible !== false) {
    fail(`${owner}: representative and gallery eligibility must both be false`);
  }
  if (!isNonEmptyString(sample.title) || !isNonEmptyString(sample.description)
    || !isNonEmptyString(sample.motionLabel) || !isNonEmptyString(sample.lockedParts)) {
    fail(`${owner}: user-facing motion fields are incomplete`);
  }
  if (!/^assets\/dinosaurs\/[a-z0-9][a-z0-9.-]*\.png$/i.test(sample.poster || "")) {
    fail(`${owner}: poster must be a project PNG under assets/dinosaurs`);
  }
  if (!/^assets\/motion\/m1\/[a-z0-9][a-z0-9.-]*-m1-v[0-9]+\.mp4$/i.test(sample.src || "")) {
    fail(`${owner}: video must be a versioned M1 MP4 under assets/motion/m1`);
  }
  if (!/^assets\/motion\/m1\/overlays\/[a-z0-9][a-z0-9.-]*-v[0-9]+\.png$/i.test(record.motionOverlay || "")) {
    fail(`${owner}: overlay must be a versioned PNG under assets/motion/m1/overlays`);
  }
  if (!/^tools\/comfyui\/motion_masks\/[a-z0-9][a-z0-9.-]*-v[0-9]+\.svg$/i.test(record.maskSource || "")) {
    fail(`${owner}: mask source must be a versioned SVG under tools/comfyui/motion_masks`);
  }
  if (record.sourcePoster !== sample.poster || record.projectAsset !== sample.src
    || record.motionClass !== sample.motionClass || record.sceneRole !== sample.sceneRole) {
    fail(`${owner}: catalog and metadata paths or roles differ`);
  }
  if (sample.provenance?.metadataRecord !== `${METADATA_RELATIVE_PATH}#/samples/${sample.id}`) {
    fail(`${owner}: invalid metadataRecord pointer`);
  }
  if (!isNonEmptyString(sample.provenance?.sourceLicense) || !isNonEmptyString(sample.provenance?.workflow)
    || !isNonEmptyString(record.motionLayer) || !isNonEmptyString(record.lockedRegions)
    || !isNonEmptyString(record.evidenceBoundary) || !Array.isArray(record.identityCuesPreserved)
    || record.identityCuesPreserved.length < 6) {
    fail(`${owner}: provenance, evidence boundary, or identity cues are incomplete`);
  }

  for (const gate of ["anatomy", "frameAnatomy", "motionPlausibility", "backgroundIntegrity", "responsive", "publication"]) {
    if (!isNonEmptyString(sample.review?.[gate]?.status) || !isNonEmptyString(sample.review?.[gate]?.note)) {
      fail(`${owner}: incomplete ${gate} review gate`);
    }
    if (sample.review?.[gate]?.status !== record.review?.[gate]?.status) {
      fail(`${owner}: catalog and metadata ${gate} status differ`);
    }
  }

  const posterPath = checkFileRecord(record.sourcePoster, record.sourceFiles?.poster, `${owner}: poster`);
  const overlayPath = checkFileRecord(record.motionOverlay, record.sourceFiles?.overlay, `${owner}: overlay`);
  const maskPath = projectPath(record.maskSource, `${owner}: mask`);
  if (!maskPath || !fs.existsSync(maskPath)) fail(`${owner}: missing mask source`);
  const videoPath = checkFileRecord(record.projectAsset, sample.file, `${owner}: video`);
  if (posterPath) {
    const probe = probeMedia(posterPath);
    if (!probe.unavailable && !probe.error &&
      (probe.width !== record.sourceFiles.poster.width || probe.height !== record.sourceFiles.poster.height)) {
      fail(`${owner}: poster dimensions differ from metadata`);
    }
  }
  if (overlayPath) {
    const probe = probeMedia(overlayPath);
    if (!probe.unavailable && !probe.error &&
      (probe.width !== record.sourceFiles.overlay.width || probe.height !== record.sourceFiles.overlay.height)) {
      fail(`${owner}: overlay dimensions differ from metadata`);
    }
  }

  if (JSON.stringify(sample.file) !== JSON.stringify(record.file)) {
    fail(`${owner}: catalog and metadata file records differ`);
  }
  if (videoPath) {
    const probe = probeMedia(videoPath);
    if (probe.unavailable) {
      warn(`${owner}: ffprobe unavailable; stream properties were not independently checked`);
    } else if (probe.error) {
      fail(`${owner}: ${probe.error}`);
    } else {
      if (probe.audio) fail(`${owner}: M1 pilot must not contain audio`);
      if (probe.pixelFormat !== "yuv420p") fail(`${owner}: pixel format must be yuv420p`);
      if (sample.file.width !== probe.width || sample.file.height !== probe.height
        || Math.abs(sample.file.durationSeconds - probe.durationSeconds) > 0.05
        || Math.abs(sample.file.fps - probe.fps) > 0.05 || sample.file.codec !== probe.codec) {
        fail(`${owner}: recorded stream properties do not match ffprobe`);
      }
    }
    const bytes = fs.readFileSync(videoPath);
    const moovIndex = bytes.indexOf(Buffer.from("moov"));
    const mdatIndex = bytes.indexOf(Buffer.from("mdat"));
    if (moovIndex < 0 || mdatIndex < 0 || moovIndex > mdatIndex) {
      fail(`${owner}: MP4 faststart layout is missing`);
    }
  }

  const qa = record.motionQa;
  const width = sample.file?.width;
  const height = sample.file?.height;
  const blinkFrames = validateFramePair(qa?.blinkComparisonFrames, owner, "blinkComparisonFrames");
  const tiltFrames = validateFramePair(qa?.tiltComparisonFrames, owner, "tiltComparisonFrames");
  const returnFrames = validateFramePair(qa?.returnComparisonFrames, owner, "returnComparisonFrames");
  const eyeZone = validateZone(qa?.eyeZone, width, height, owner, "eyeZone");
  const headZone = validateZone(qa?.headZone, width, height, owner, "headZone");
  const exclusionZone = validateZone(qa?.protectedExclusionZone, width, height, owner, "protectedExclusionZone");
  if (eyeZone && headZone) {
    const eyeInsideHead = eyeZone.x1 >= headZone.x1 && eyeZone.x2 <= headZone.x2
      && eyeZone.y1 >= headZone.y1 && eyeZone.y2 <= headZone.y2;
    if (!eyeInsideHead) fail(`${owner}: eyeZone must fit inside headZone`);
  }
  if (headZone && exclusionZone) {
    const headInsideExclusion = headZone.x1 >= exclusionZone.x1 && headZone.x2 <= exclusionZone.x2
      && headZone.y1 >= exclusionZone.y1 && headZone.y2 <= exclusionZone.y2;
    if (!headInsideExclusion) fail(`${owner}: headZone must fit inside protectedExclusionZone`);
  }

  const thresholds = metadata.workflow?.motionQaThresholds;
  const requiredThresholds = [
    "significantChannelDifferenceFloor", "headZoneSignificantEnergyMin",
    "blinkEyeZoneSignificantEnergyMin", "significantChangeEnergyInsideHeadZoneMinPercent",
    "significantChangeEnergyInsideEyeZoneMinPercent", "protectedRegionMeanMax",
    "protectedRegionP99Max", "protectedRegionMaxMax", "returnFrameMeanMax",
  ];
  if (!thresholds || requiredThresholds.some((field) => !Number.isFinite(thresholds[field]) || thresholds[field] < 0)) {
    fail(`${owner}: complete non-negative motion QA thresholds are required`);
  }

  if (videoPath && blinkFrames && tiltFrames && returnFrames && eyeZone && headZone && exclusionZone && thresholds) {
    const decode = (frames) => extractComparisonFrames(videoPath, frames, width, height);
    const blinkDecoded = decode(blinkFrames);
    const tiltDecoded = decode(tiltFrames);
    const returnDecoded = decode(returnFrames);
    for (const [label, decoded] of [["blink", blinkDecoded], ["tilt", tiltDecoded], ["return", returnDecoded]]) {
      if (decoded.unavailable) warn(`${owner}: ffmpeg unavailable; ${label} frames were not checked`);
      if (decoded.error) fail(`${owner}: ${label} frame extraction failed: ${decoded.error}`);
    }
    if (blinkDecoded.first && tiltDecoded.first && returnDecoded.first) {
      const blink = calculatePairQa(
        blinkDecoded.first, blinkDecoded.second, width, eyeZone, exclusionZone,
        thresholds.significantChannelDifferenceFloor,
      );
      const tilt = calculatePairQa(
        tiltDecoded.first, tiltDecoded.second, width, headZone, exclusionZone,
        thresholds.significantChannelDifferenceFloor,
      );
      const returned = calculatePairQa(
        returnDecoded.first, returnDecoded.second, width, headZone, exclusionZone,
        thresholds.significantChannelDifferenceFloor,
      );
      calculatedQa = { blink, tilt, returnFrameMeanDifference: returned.wholeFrameMeanDifference };

      if (blink.significantEnergyInsideZone < thresholds.blinkEyeZoneSignificantEnergyMin) {
        fail(`${owner}: blink energy is too small`);
      }
      if (blink.significantChangeEnergyInsideZonePercent < thresholds.significantChangeEnergyInsideEyeZoneMinPercent) {
        fail(`${owner}: blink change is insufficiently localized to the eye zone`);
      }
      if (tilt.significantEnergyInsideZone < thresholds.headZoneSignificantEnergyMin) {
        fail(`${owner}: head-tilt energy is too small`);
      }
      if (tilt.significantChangeEnergyInsideZonePercent < thresholds.significantChangeEnergyInsideHeadZoneMinPercent) {
        fail(`${owner}: head-tilt change is insufficiently localized to the head zone`);
      }
      for (const [label, pair] of [["blink", blink], ["tilt", tilt]]) {
        if (pair.protectedRegionDifference.mean > thresholds.protectedRegionMeanMax
          || pair.protectedRegionDifference.p99 > thresholds.protectedRegionP99Max
          || pair.protectedRegionDifference.max > thresholds.protectedRegionMaxMax) {
          fail(`${owner}: ${label} protected region changed beyond threshold`);
        }
      }
      if (returned.wholeFrameMeanDifference > thresholds.returnFrameMeanMax) {
        fail(`${owner}: final frame does not return close enough to the poster`);
      }

      if (qa.calculated === null) {
        warn(`${owner}: decoded motion QA is not recorded yet: ${JSON.stringify(calculatedQa)}`);
      } else {
        for (const label of ["blink", "tilt"]) {
          compareNumber(calculatedQa[label].significantEnergyInsideZone, qa.calculated[label]?.significantEnergyInsideZone, 0.5, `${owner}: ${label} significantEnergyInsideZone`);
          compareNumber(calculatedQa[label].significantChangeEnergyInsideZonePercent, qa.calculated[label]?.significantChangeEnergyInsideZonePercent, 0.05, `${owner}: ${label} significantChangeEnergyInsideZonePercent`);
          compareNumber(calculatedQa[label].protectedRegionDifference.mean, qa.calculated[label]?.protectedRegionDifference?.mean, 0.005, `${owner}: ${label} protected mean`);
          compareNumber(calculatedQa[label].protectedRegionDifference.p99, qa.calculated[label]?.protectedRegionDifference?.p99, 0, `${owner}: ${label} protected p99`);
          compareNumber(calculatedQa[label].protectedRegionDifference.max, qa.calculated[label]?.protectedRegionDifference?.max, 0, `${owner}: ${label} protected max`);
        }
        compareNumber(calculatedQa.returnFrameMeanDifference, qa.calculated.returnFrameMeanDifference, 0.005, `${owner}: return frame mean`);
      }
    }
  }

  const published = sample.review?.publication?.status === "published";
  if (published) {
    publishedVideos += 1;
    const subject = sample.subjectMotion;
    if (subject?.status !== "supported" || subject.evidenceGate !== "review.motionPlausibility"
      || !Array.isArray(subject.taxonIds) || !subject.taxonIds.includes(sample.taxonId)
      || !Array.isArray(subject.movingParts) || !subject.movingParts.length) {
      fail(`${owner}: published M1 sample lacks supported dinosaur subject motion`);
    }
    for (const gate of ["frameAnatomy", "motionPlausibility", "backgroundIntegrity", "responsive"]) {
      if (sample.review?.[gate]?.status !== "supported") fail(`${owner}: published without ${gate} support`);
    }
    if (qa?.visualStatus !== "pass" || qa?.calculated === null) {
      fail(`${owner}: published without visual and decoded frame QA`);
    }
    if (!isNonEmptyString(metadata.workflow?.commands?.[sample.id])) {
      fail(`${owner}: published without an exact workflow command`);
    }
  }
}

const report = {
  schemaVersion: catalog.schemaVersion,
  sampleCount: samples.length,
  publishedVideos,
  policy: {
    tier: catalog.policy?.tier,
    scope: catalog.policy?.scope,
    representativePromotion: catalog.policy?.representativePromotion,
    galleryPromotion: catalog.policy?.galleryPromotion,
    autoplay: catalog.policy?.autoplay,
  },
  calculatedQa,
  warnings,
  errors,
};

console.log(JSON.stringify(report, null, 2));
if (errors.length) process.exitCode = 1;
