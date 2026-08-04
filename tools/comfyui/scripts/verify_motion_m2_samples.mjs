import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..", "..");
const CATALOG_RELATIVE_PATH = "motion-m2-samples.js";
const METADATA_RELATIVE_PATH = "tools/comfyui/motion-m2-pilot-batch-20260804.json";
const CATALOG_PATH = path.join(ROOT, CATALOG_RELATIVE_PATH);
const METADATA_PATH = path.join(ROOT, ...METADATA_RELATIVE_PATH.split("/"));
const EXPECTED_ID = "oviraptor-philoceratops-rigid-head-sweep-biological-m2-v1";
const EXPECTED_VISUAL_CHECKPOINTS = [0, 12, 24, 36, 48, 60, 72, 84, 96, 108, 119];
const EXPECTED_SEAM_CHECKPOINTS = [0, 24, 48, 72, 96];
const EXPECTED_IMAGE_EDIT_PROMPT = [
  "Use case: precise-object-edit.",
  "Asset type: motion-production clean plate for a scientific educational dinosaur atlas.",
  "Input image: the attached approved Oviraptor philoceratops still is the edit target.",
  "Primary request: remove only (1) the entire head and neck above their connection to the torso and (2) the entire tail from its connection at the rear of the torso to the tail tip. Reconstruct the hidden pale blue sky, small clouds, distant orange dunes, shrubs, and ground naturally behind those two removed regions.",
  "Critical invariants: keep the torso, shoulder line, hip, both feathered arms and every visible finger, both hind legs and feet, body feathers, ground shadow, vegetation outside the removed regions, lighting, camera, crop, perspective, resolution, and every other pixel-like visual detail as close to the source as possible. Do not alter or move any retained body part. The resulting body is intentionally headless/neckless and tailless because it is a clean background plate used only beneath separately animated original parts.",
  "Avoid: no new animal parts, no replacement head or neck, no replacement tail, no anatomy invention, no text, no watermark, no camera or color change.",
].join("\n");
const REQUIRED_REVIEW_GATES = [
  "anatomy",
  "frameAnatomy",
  "maskIntegrity",
  "cleanPlateIntegrity",
  "motionPlausibility",
  "backgroundIntegrity",
  "temporalIntegrity",
  "responsive",
  "publication",
];
const REQUIRED_PUBLIC_GATES = [
  "frameAnatomy",
  "maskIntegrity",
  "cleanPlateIntegrity",
  "motionPlausibility",
  "backgroundIntegrity",
  "temporalIntegrity",
  "responsive",
];
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

function parseRate(value) {
  const [numerator, denominator] = String(value || "0/1").split("/").map(Number);
  return denominator ? numerator / denominator : 0;
}

function probeMedia(filePath) {
  const executable = globalThis.process?.env?.FFPROBE_PATH || "ffprobe";
  const result = spawnSync(
    executable,
    ["-v", "error", "-count_frames", "-show_streams", "-show_format", "-of", "json", filePath],
    { encoding: "utf8", windowsHide: true },
  );
  if (result.error?.code === "ENOENT") return { unavailable: true };
  if (result.status !== 0) return { error: result.stderr.trim() || `ffprobe exited ${result.status}` };
  try {
    const payload = JSON.parse(result.stdout);
    const videoStreams = payload.streams?.filter((stream) => stream.codec_type === "video") || [];
    const audioStreams = payload.streams?.filter((stream) => stream.codec_type === "audio") || [];
    const video = videoStreams[0];
    const sideRotation = video?.side_data_list?.find((entry) => Number.isFinite(Number(entry.rotation)))?.rotation;
    return {
      width: video?.width,
      height: video?.height,
      fps: parseRate(video?.avg_frame_rate),
      realFps: parseRate(video?.r_frame_rate),
      codec: video?.codec_name,
      pixelFormat: video?.pix_fmt,
      durationSeconds: Number(payload.format?.duration ?? video?.duration),
      frameCount: Number(video?.nb_read_frames ?? video?.nb_frames),
      startSeconds: Number(payload.format?.start_time ?? video?.start_time ?? 0),
      sampleAspectRatio: video?.sample_aspect_ratio,
      rotation: Number(sideRotation ?? video?.tags?.rotate ?? 0),
      videoStreamCount: videoStreams.length,
      audioStreamCount: audioStreams.length,
      streamCount: payload.streams?.length || 0,
      formatName: payload.format?.format_name || "",
    };
  } catch (error) {
    return { error: `invalid ffprobe JSON: ${error.message}` };
  }
}

function checkFileRecord(relativePath, record, owner, kind = "asset") {
  const absolutePath = projectPath(relativePath, owner);
  if (!absolutePath || !fs.existsSync(absolutePath)) {
    fail(`${owner}: missing ${relativePath}`);
    return null;
  }
  if (!record || !/^[a-f0-9]{64}$/.test(record.sha256 || "")
    || !Number.isInteger(record.bytes) || record.bytes <= 0) {
    fail(`${owner}: incomplete sha256/bytes record`);
    return null;
  }
  const stat = fs.statSync(absolutePath);
  const digest = sha256(absolutePath);
  if (digest !== record.sha256 || stat.size !== record.bytes) {
    if (kind === "video") {
      fail(
        `${owner}: video metadata stale after rebuild; expected sha256 ${record.sha256} / ${record.bytes} bytes, `
        + `actual sha256 ${digest} / ${stat.size} bytes. Refresh both ${CATALOG_RELATIVE_PATH} and `
        + `${METADATA_RELATIVE_PATH} file records after the final rebuild.`,
      );
    } else {
      fail(
        `${owner}: ${kind} hash or byte count mismatch; expected sha256 ${record.sha256} / ${record.bytes} bytes, `
        + `actual sha256 ${digest} / ${stat.size} bytes`,
      );
    }
  }
  return { absolutePath, digest, bytes: stat.size };
}

function verifyImageDimensions(checkedFile, record, owner, expectedWidth, expectedHeight) {
  if (!checkedFile) return;
  const probe = probeMedia(checkedFile.absolutePath);
  if (probe.unavailable) {
    warn(`${owner}: ffprobe unavailable; image dimensions were not independently checked`);
    return;
  }
  if (probe.error) {
    fail(`${owner}: ${probe.error}`);
    return;
  }
  if (probe.codec !== "png" || probe.width !== expectedWidth || probe.height !== expectedHeight) {
    fail(`${owner}: expected a ${expectedWidth}x${expectedHeight} PNG, got ${probe.codec} ${probe.width}x${probe.height}`);
  }
  if (record.width !== expectedWidth || record.height !== expectedHeight) {
    fail(`${owner}: recorded dimensions must be ${expectedWidth}x${expectedHeight}`);
  }
}

function decodeGrayMask(filePath, width, height) {
  const executable = globalThis.process?.env?.FFMPEG_PATH || "ffmpeg";
  const result = spawnSync(
    executable,
    ["-v", "error", "-i", filePath, "-vf", "format=gray", "-frames:v", "1", "-f", "rawvideo", "pipe:1"],
    { encoding: null, windowsHide: true, maxBuffer: width * height * 2 },
  );
  if (result.error?.code === "ENOENT") return { unavailable: true };
  if (result.status !== 0) {
    return { error: result.stderr?.toString("utf8").trim() || `ffmpeg exited ${result.status}` };
  }
  if (result.stdout.length !== width * height) {
    return { error: `expected ${width * height} gray bytes, received ${result.stdout.length}` };
  }
  return { pixels: result.stdout };
}

function extractFrames(filePath, frameIndices, width, height) {
  const executable = globalThis.process?.env?.FFMPEG_PATH || "ffmpeg";
  const selector = frameIndices.map((frame) => `eq(n\\,${frame})`).join("+");
  const result = spawnSync(
    executable,
    [
      "-v", "error", "-i", filePath,
      "-vf", `select=${selector},format=rgb24`,
      "-fps_mode", "vfr", "-frames:v", String(frameIndices.length),
      "-an", "-f", "rawvideo", "pipe:1",
    ],
    {
      encoding: null,
      windowsHide: true,
      maxBuffer: width * height * 3 * (frameIndices.length + 1),
    },
  );
  if (result.error?.code === "ENOENT") return { unavailable: true };
  if (result.status !== 0) {
    return { error: result.stderr?.toString("utf8").trim() || `ffmpeg exited ${result.status}` };
  }
  const frameBytes = width * height * 3;
  const expectedBytes = frameBytes * frameIndices.length;
  if (result.stdout.length !== expectedBytes) {
    return { error: `expected ${expectedBytes} raw RGB bytes, received ${result.stdout.length}` };
  }
  const frames = new Map();
  for (let index = 0; index < frameIndices.length; index += 1) {
    frames.set(frameIndices[index], result.stdout.subarray(index * frameBytes, (index + 1) * frameBytes));
  }
  return { frames };
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

function maskStats(mask) {
  let positive = 0;
  let partial = 0;
  for (const value of mask) {
    if (value > 127) positive += 1;
    if (value > 0 && value < 255) partial += 1;
  }
  return {
    pixels: positive,
    percent: (positive / mask.length) * 100,
    partialPixels: partial,
  };
}

function dilateSquare(mask, width, height, radius) {
  const horizontal = new Uint8Array(width * height);
  const output = new Uint8Array(width * height);
  for (let y = 0; y < height; y += 1) {
    let count = 0;
    for (let x = 0; x < width; x += 1) {
      const addX = x + radius;
      const removeX = x - radius - 1;
      if (addX < width && mask[y * width + addX] > 127) count += 1;
      if (removeX >= 0 && mask[y * width + removeX] > 127) count -= 1;
      if (count > 0) horizontal[y * width + x] = 1;
    }
  }
  for (let x = 0; x < width; x += 1) {
    let count = 0;
    for (let y = 0; y < height; y += 1) {
      const addY = y + radius;
      const removeY = y - radius - 1;
      if (addY < height && horizontal[addY * width + x]) count += 1;
      if (removeY >= 0 && horizontal[removeY * width + x]) count -= 1;
      if (count > 0) output[y * width + x] = 1;
    }
  }
  return output;
}

function calculatePairQa(first, second, width, actorMask, sweepMask, lockedMask, dilatedSweep, differenceFloor) {
  const protectedHistogram = new Uint32Array(256);
  let protectedCount = 0;
  let protectedSum = 0;
  let protectedMax = 0;
  let protectedChangedGt6 = 0;
  let allSignificantEnergy = 0;
  let sweepSignificantEnergy = 0;
  let actorSignificantEnergy = 0;
  let wholeFrameDifference = 0;

  for (let offset = 0; offset < first.length; offset += 1) {
    const pixel = Math.floor(offset / 3);
    const difference = Math.abs(second[offset] - first[offset]);
    wholeFrameDifference += difference;
    if (difference > differenceFloor) {
      allSignificantEnergy += difference;
      if (sweepMask[pixel] > 127) sweepSignificantEnergy += difference;
      if (actorMask[pixel] > 127) actorSignificantEnergy += difference;
    }
    if (lockedMask[pixel] > 127 && !dilatedSweep[pixel]) {
      protectedCount += 1;
      protectedSum += difference;
      protectedHistogram[difference] += 1;
      if (difference > protectedMax) protectedMax = difference;
      if (difference > 6) protectedChangedGt6 += 1;
    }
  }

  return {
    allSignificantEnergy,
    headSweepSignificantEnergy: sweepSignificantEnergy,
    headActorSignificantEnergy: actorSignificantEnergy,
    significantChangeEnergyInsideHeadSweepPercent:
      allSignificantEnergy ? (sweepSignificantEnergy / allSignificantEnergy) * 100 : 0,
    protectedRegionDifference: {
      mean: protectedCount ? protectedSum / protectedCount : 0,
      p99: percentileFromHistogram(protectedHistogram, protectedCount, 0.99),
      max: protectedMax,
      changedGt6Percent: protectedCount ? (protectedChangedGt6 / protectedCount) * 100 : 0,
    },
    wholeFrameMeanDifference: first.length ? wholeFrameDifference / first.length : 0,
  };
}

function compareNumber(actual, recorded, tolerance, owner) {
  if (!Number.isFinite(recorded) || Math.abs(actual - recorded) > tolerance) {
    fail(`${owner}: recorded ${recorded} does not match decoded ${actual}`);
  }
}

function comparePairQa(actual, recorded, owner) {
  for (const field of [
    "allSignificantEnergy",
    "headSweepSignificantEnergy",
    "headActorSignificantEnergy",
  ]) {
    compareNumber(actual[field], recorded?.[field], 0.5, `${owner}.${field}`);
  }
  compareNumber(
    actual.significantChangeEnergyInsideHeadSweepPercent,
    recorded?.significantChangeEnergyInsideHeadSweepPercent,
    0.05,
    `${owner}.significantChangeEnergyInsideHeadSweepPercent`,
  );
  compareNumber(
    actual.protectedRegionDifference.mean,
    recorded?.protectedRegionDifference?.mean,
    0.005,
    `${owner}.protectedRegionDifference.mean`,
  );
  compareNumber(
    actual.protectedRegionDifference.p99,
    recorded?.protectedRegionDifference?.p99,
    0,
    `${owner}.protectedRegionDifference.p99`,
  );
  compareNumber(
    actual.protectedRegionDifference.max,
    recorded?.protectedRegionDifference?.max,
    0,
    `${owner}.protectedRegionDifference.max`,
  );
  compareNumber(
    actual.protectedRegionDifference.changedGt6Percent,
    recorded?.protectedRegionDifference?.changedGt6Percent,
    0.001,
    `${owner}.protectedRegionDifference.changedGt6Percent`,
  );
  compareNumber(
    actual.wholeFrameMeanDifference,
    recorded?.wholeFrameMeanDifference,
    0.005,
    `${owner}.wholeFrameMeanDifference`,
  );
}

function validateFramePair(frames, frameCount, owner, label) {
  const valid = Array.isArray(frames) && frames.length === 2
    && frames.every(Number.isInteger) && frames[0] >= 0 && frames[0] < frames[1]
    && frames[1] < frameCount;
  if (!valid) fail(`${owner}: invalid ${label}`);
  return valid ? frames : null;
}

const catalogSource = fs.readFileSync(CATALOG_PATH, "utf8");
const metadataSource = fs.readFileSync(METADATA_PATH, "utf8");
const sandbox = { window: {} };
new vm.Script(catalogSource, { filename: CATALOG_PATH }).runInNewContext(sandbox);
const catalog = sandbox.window.motionM2SampleCatalog;
const metadata = JSON.parse(metadataSource);

if (!catalog || typeof catalog !== "object") throw new Error("motionM2SampleCatalog was not exported");
if (/\.codex[\\/]generated_images/i.test(catalogSource) || /\.codex[\\/]generated_images/i.test(metadataSource)) {
  fail("generator-area path leak");
}
if (catalog.schemaVersion !== 1 || metadata.schemaVersion !== 1) fail("schemaVersion must be 1");

for (const policy of [catalog.policy, metadata.policy]) {
  if (policy?.tier !== "M2") fail("policy tier must be M2");
  if (policy?.representativePromotion !== "prohibited") fail("representative promotion must be prohibited");
  if (policy?.galleryPromotion !== "prohibited") fail("gallery promotion must be prohibited");
  if (policy?.anatomyPromotion !== "prohibited") fail("anatomy promotion must be prohibited");
  if (policy?.autoplay !== "prohibited" || policy?.clickToPlay !== "required") {
    fail("M2 playback policy must be click-only with autoplay prohibited");
  }
  if (policy?.audio !== "prohibited" || policy?.cameraMotion !== "prohibited") {
    fail("M2 audio and camera motion must be prohibited");
  }
  if (policy?.locomotion !== "prohibited in M2" || policy?.tailMotion !== "prohibited in this M2 pilot") {
    fail("M2 locomotion and tail motion policy is incomplete");
  }
  if (!Array.isArray(policy?.allowedMotion)
    || policy.allowedMotion.length !== 1
    || policy.allowedMotion[0] !== "rigid head-and-neck sinusoidal rotation up to plus or minus 4 degrees") {
    fail("M2 allowed-motion policy must contain only the rigid plus-or-minus four-degree head-and-neck sweep");
  }
}

const samples = Array.isArray(catalog.samples) ? catalog.samples : [];
const catalogIds = samples.map((sample) => sample?.id);
const metadataIds = Object.keys(metadata.samples || {});
if (JSON.stringify(catalogIds) !== JSON.stringify(metadataIds)) {
  fail(`catalog-metadata one-to-one mismatch: catalog=${catalogIds.join(",")} metadata=${metadataIds.join(",")}`);
}
if (catalogIds.length !== 1 || catalogIds[0] !== EXPECTED_ID) {
  fail(`catalog must contain exactly ${EXPECTED_ID}`);
}

const workflow = metadata.workflow || {};
if (workflow.imageEdit?.generatorCallId !== "exec-90dba4e4-c4df-4ee8-b808-1cd1afd4dadd") {
  fail("metadata: incorrect clean-plate imagegen call id");
}
if (workflow.imageEdit?.seed !== "unavailable") fail("metadata: imagegen seed must be recorded as unavailable");
if (workflow.imageEdit?.prompt !== EXPECTED_IMAGE_EDIT_PROMPT) fail("metadata: clean-plate imagegen prompt is not the exact approved prompt");
if (workflow.fillMaskBlurSigma !== 0.4 || workflow.headMaskBlurSigma !== 0.4) {
  fail("metadata: final fill/head mask gblur sigma must both be 0.4");
}
const motionProfile = workflow.motionProfile || {};
if (motionProfile.type !== "sinusoidal rigid rotation"
  || motionProfile.movingPart !== "head and neck as one rigid 2D actor"
  || motionProfile.amplitudeDegrees !== 4
  || Math.abs(motionProfile.amplitudeRadians - 0.0698131701) > 1e-12
  || motionProfile.periodSeconds !== 5
  || motionProfile.expression !== "0.0698131701*sin(2*PI*t/5)"
  || motionProfile.tailMotion !== false
  || motionProfile.pivot?.x !== 260 || motionProfile.pivot?.y !== 316) {
  fail("metadata: M2 motion profile must be the fixed ±4-degree, five-second, head-neck-only sine contract");
}
const lockedParts = new Set(motionProfile.lockedParts || []);
for (const part of ["torso", "tail", "arms", "fingers", "legs", "feet", "ground", "background", "camera"]) {
  if (!lockedParts.has(part)) fail(`metadata: motion profile does not lock ${part}`);
}
if (workflow.targetDimensions?.width !== 960 || workflow.targetDimensions?.height !== 640
  || workflow.targetDurationSeconds !== 5 || workflow.targetFps !== 24
  || workflow.targetFrameCount !== 120 || workflow.audio !== "none"
  || workflow.targetVideoCodec !== "H.264" || workflow.targetPixelFormat !== "yuv420p") {
  fail("metadata: target stream contract must be 960x640, H.264/yuv420p, 5 seconds, 24 fps, 120 frames, no audio");
}

let publishedVideos = 0;
let calculatedQa = null;
for (const sample of samples) {
  const owner = sample?.id || "sample:(blank)";
  const record = metadata.samples?.[sample.id];
  if (!record) {
    fail(`${owner}: missing metadata record`);
    continue;
  }
  if (sample.tier !== "M2" || sample.motionClass !== "controlled-partial-body" || sample.sceneRole !== "solo") {
    fail(`${owner}: must remain an M2 controlled-partial-body solo sample`);
  }
  if (sample.representativeEligible !== false || sample.galleryEligible !== false || sample.anatomyEligible !== false
    || record.review?.representativeEligible !== false || record.review?.galleryEligible !== false
    || record.review?.anatomyEligible !== false) {
    fail(`${owner}: representative, gallery, and anatomy eligibility must all be false`);
  }
  for (const field of [
    "taxon", "commonName", "title", "scientificName", "summary", "description",
    "motionLabel", "lockedParts", "evidenceBoundary", "credits",
  ]) {
    if (!isNonEmptyString(sample[field])) fail(`${owner}: missing user-facing ${field}`);
  }
  if (!/^assets\/dinosaurs\/[a-z0-9][a-z0-9.-]*\.png$/i.test(sample.poster || "")) {
    fail(`${owner}: poster must be a project PNG under assets/dinosaurs`);
  }
  if (!/^assets\/motion\/m2\/[a-z0-9][a-z0-9.-]*-m2-v[0-9]+\.mp4$/i.test(sample.src || "")) {
    fail(`${owner}: video must be a versioned M2 MP4 under assets/motion/m2`);
  }
  if (!/^assets\/dinosaurs\/[a-z0-9][a-z0-9.-]*-motion-imagegen-v[0-9]+\.png$/i.test(record.cleanPlate || "")) {
    fail(`${owner}: clean plate must be a species-prefixed, versioned motion PNG under assets/dinosaurs`);
  }
  const expectedMaskPatterns = {
    authoringSource: /^tools\/comfyui\/motion_masks\/[a-z0-9][a-z0-9.-]*-partial-m2-v[0-9]+\.svg$/i,
    headActor: /^tools\/comfyui\/motion_masks\/[a-z0-9][a-z0-9.-]*-partial-m2-v[0-9]+\.png$/i,
    headSweep: /^tools\/comfyui\/motion_masks\/[a-z0-9][a-z0-9.-]*-partial-m2-v[0-9]+\.png$/i,
    lockedBody: /^tools\/comfyui\/motion_masks\/[a-z0-9][a-z0-9.-]*-partial-m2-v[0-9]+\.png$/i,
  };
  for (const [key, pattern] of Object.entries(expectedMaskPatterns)) {
    if (!pattern.test(record.masks?.[key] || "")) fail(`${owner}: invalid ${key} mask path`);
  }
  if (!isNonEmptyString(record.masks?.authority)
    || !record.masks.authority.includes("three 960x640 PNG files are the authoritative compositor and QA inputs")) {
    fail(`${owner}: mask authority must distinguish the authoring SVG from the three authoritative PNG inputs`);
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
    fail(`${owner}: provenance, evidence boundary, locked regions, or identity cues are incomplete`);
  }

  for (const gate of REQUIRED_REVIEW_GATES) {
    if (!isNonEmptyString(sample.review?.[gate]?.status) || !isNonEmptyString(sample.review?.[gate]?.note)) {
      fail(`${owner}: incomplete ${gate} review gate`);
    }
    if (sample.review?.[gate]?.status !== record.review?.[gate]?.status) {
      fail(`${owner}: catalog and metadata ${gate} status differ`);
    }
  }

  if (JSON.stringify(sample.file) !== JSON.stringify(record.file)) {
    fail(`${owner}: catalog and metadata video file records differ; refresh both after a rebuild`);
  }
  const requiredFileFields = [
    "sha256", "bytes", "width", "height", "durationSeconds", "fps", "frameCount",
    "codec", "pixelFormat", "container", "audio",
  ];
  if (requiredFileFields.some((field) => sample.file?.[field] === undefined || sample.file?.[field] === null)) {
    fail(`${owner}: video file record is incomplete`);
  }

  const posterFile = checkFileRecord(record.sourcePoster, record.sourceFiles?.poster, `${owner}: poster`, "poster");
  const cleanPlateFile = checkFileRecord(record.cleanPlate, record.sourceFiles?.cleanPlate, `${owner}: clean plate`, "clean plate");
  const authoringSvgFile = checkFileRecord(
    record.masks?.authoringSource,
    record.sourceFiles?.authoringSvg,
    `${owner}: authoring SVG`,
    "authoring SVG",
  );
  const headActorFile = checkFileRecord(
    record.masks?.headActor,
    record.sourceFiles?.headActorMask,
    `${owner}: head actor mask`,
    "head actor mask",
  );
  const headSweepFile = checkFileRecord(
    record.masks?.headSweep,
    record.sourceFiles?.headSweepMask,
    `${owner}: head sweep mask`,
    "head sweep mask",
  );
  const lockedBodyFile = checkFileRecord(
    record.masks?.lockedBody,
    record.sourceFiles?.lockedBodyMask,
    `${owner}: locked body mask`,
    "locked body mask",
  );
  const buildScriptFile = checkFileRecord(
    workflow.buildScript,
    record.sourceFiles?.buildScript,
    `${owner}: build script`,
    "build script",
  );
  const videoFile = checkFileRecord(record.projectAsset, sample.file, `${owner}: video`, "video");

  verifyImageDimensions(posterFile, record.sourceFiles?.poster, `${owner}: poster`, 1536, 1024);
  verifyImageDimensions(cleanPlateFile, record.sourceFiles?.cleanPlate, `${owner}: clean plate`, 1536, 1024);
  verifyImageDimensions(headActorFile, record.sourceFiles?.headActorMask, `${owner}: head actor mask`, 960, 640);
  verifyImageDimensions(headSweepFile, record.sourceFiles?.headSweepMask, `${owner}: head sweep mask`, 960, 640);
  verifyImageDimensions(lockedBodyFile, record.sourceFiles?.lockedBodyMask, `${owner}: locked body mask`, 960, 640);
  if (authoringSvgFile && !fs.readFileSync(authoringSvgFile.absolutePath, "utf8").includes("<svg")) {
    fail(`${owner}: authoring mask is not an SVG document`);
  }

  if (buildScriptFile) {
    const buildSource = fs.readFileSync(buildScriptFile.absolutePath, "utf8");
    if (/\.codex[\\/]generated_images/i.test(buildSource)) fail(`${owner}: build script leaks a generator-area path`);
    if (!buildSource.includes("0.0698131701*sin(2*PI*t/5)")) {
      fail(`${owner}: build script does not contain the approved ±4-degree five-second sine expression`);
    }
    if ((buildSource.match(/rotate=/g) || []).length !== 1) {
      fail(`${owner}: build script must contain exactly one rotation stage`);
    }
    if ((buildSource.match(/gblur=sigma=0\.4/g) || []).length !== 2) {
      fail(`${owner}: build script must use final sigma=0.4 for both fill and head masks`);
    }
    for (const token of ["-an", "-r", "24", "-t", "5", "libx264", "yuv420p", "+faststart"]) {
      if (!buildSource.includes(token)) fail(`${owner}: build script is missing required stream token ${token}`);
    }
    if (/\[(?:tailMove|tailActor)\]|tail[^\r\n]*rotate=/i.test(buildSource)) {
      fail(`${owner}: build script contains prohibited tail animation`);
    }
  }

  if (videoFile) {
    const probe = probeMedia(videoFile.absolutePath);
    if (probe.unavailable) {
      warn(`${owner}: ffprobe unavailable; video stream properties were not independently checked`);
    } else if (probe.error) {
      fail(`${owner}: ${probe.error}`);
    } else {
      if (probe.videoStreamCount !== 1 || probe.audioStreamCount !== 0 || probe.streamCount !== 1) {
        fail(`${owner}: video must contain exactly one video stream and no audio or extra streams`);
      }
      if (probe.codec !== "h264" || probe.pixelFormat !== "yuv420p"
        || probe.width !== 960 || probe.height !== 640
        || Math.abs(probe.fps - 24) > 0.01 || Math.abs(probe.realFps - 24) > 0.01
        || Math.abs(probe.durationSeconds - 5) > 0.05 || probe.frameCount !== 120
        || Math.abs(probe.startSeconds) > 0.001 || probe.rotation !== 0
        || !probe.formatName.split(",").includes("mp4")) {
        fail(`${owner}: stream contract mismatch (${JSON.stringify(probe)})`);
      }
      if (sample.file.width !== probe.width || sample.file.height !== probe.height
        || Math.abs(sample.file.durationSeconds - probe.durationSeconds) > 0.05
        || Math.abs(sample.file.fps - probe.fps) > 0.01 || sample.file.frameCount !== probe.frameCount
        || sample.file.codec !== probe.codec || sample.file.pixelFormat !== probe.pixelFormat
        || sample.file.container !== "mp4" || sample.file.audio !== false) {
        fail(`${owner}: recorded file fields do not match ffprobe`);
      }
    }
    const bytes = fs.readFileSync(videoFile.absolutePath);
    const moovIndex = bytes.indexOf(Buffer.from("moov"));
    const mdatIndex = bytes.indexOf(Buffer.from("mdat"));
    if (moovIndex < 0 || mdatIndex < 0 || moovIndex > mdatIndex) {
      fail(`${owner}: MP4 faststart layout is missing`);
    }
  }

  const thresholds = workflow.motionQaThresholds;
  const requiredThresholds = [
    "significantChannelDifferenceFloor",
    "sweepMaskDilationPixels",
    "headActorCoverageMinPercent",
    "headActorCoverageMaxPercent",
    "headSweepCoverageMinPercent",
    "headSweepCoverageMaxPercent",
    "headSweepSignificantEnergyMin",
    "significantChangeEnergyInsideHeadSweepMinPercent",
    "protectedRegionMeanMax",
    "protectedRegionP99Max",
    "protectedRegionMaxMax",
    "protectedRegionChangedGt6MaxPercent",
    "returnFrameMeanMax",
    "returnSweepSignificantEnergyMax",
  ];
  if (!thresholds || requiredThresholds.some(
    (field) => !Number.isFinite(thresholds[field]) || thresholds[field] < 0,
  )) {
    fail(`${owner}: complete non-negative M2 QA thresholds are required`);
  }

  const qa = record.motionQa;
  const positivePair = validateFramePair(qa?.positivePeakComparisonFrames, sample.file.frameCount, owner, "positivePeakComparisonFrames");
  const negativePair = validateFramePair(qa?.negativePeakComparisonFrames, sample.file.frameCount, owner, "negativePeakComparisonFrames");
  const returnPair = validateFramePair(qa?.returnComparisonFrames, sample.file.frameCount, owner, "returnComparisonFrames");
  if (JSON.stringify(positivePair) !== JSON.stringify([0, 30])
    || JSON.stringify(negativePair) !== JSON.stringify([0, 90])
    || JSON.stringify(returnPair) !== JSON.stringify([0, 119])) {
    fail(`${owner}: comparison frames must be [0,30], [0,90], and [0,119]`);
  }
  if (JSON.stringify(qa?.visualCheckpoints) !== JSON.stringify(EXPECTED_VISUAL_CHECKPOINTS)
    || JSON.stringify(qa?.seamCheckpoints) !== JSON.stringify(EXPECTED_SEAM_CHECKPOINTS)) {
    fail(`${owner}: manual full-frame or seam checkpoint contract differs from the approved review`);
  }
  if (!isNonEmptyString(qa?.contactSheetPolicy)
    || !qa.contactSheetPolicy.includes("temporary QA-only")) {
    fail(`${owner}: temporary contact-sheet evidence boundary is missing`);
  }

  if (headActorFile && headSweepFile && lockedBodyFile && thresholds) {
    const actorDecoded = decodeGrayMask(headActorFile.absolutePath, 960, 640);
    const sweepDecoded = decodeGrayMask(headSweepFile.absolutePath, 960, 640);
    const lockedDecoded = decodeGrayMask(lockedBodyFile.absolutePath, 960, 640);
    for (const [label, decoded] of [
      ["head actor mask", actorDecoded],
      ["head sweep mask", sweepDecoded],
      ["locked body mask", lockedDecoded],
    ]) {
      if (decoded.unavailable) warn(`${owner}: ffmpeg unavailable; ${label} pixels were not checked`);
      if (decoded.error) fail(`${owner}: ${label} decode failed: ${decoded.error}`);
    }
    if (actorDecoded.pixels && sweepDecoded.pixels && lockedDecoded.pixels) {
      const actorStats = maskStats(actorDecoded.pixels);
      const sweepStats = maskStats(sweepDecoded.pixels);
      const lockedStats = maskStats(lockedDecoded.pixels);
      let actorOutsideSweep = 0;
      let sweepLockedOverlap = 0;
      let uncovered = 0;
      for (let index = 0; index < actorDecoded.pixels.length; index += 1) {
        const actor = actorDecoded.pixels[index] > 127;
        const sweep = sweepDecoded.pixels[index] > 127;
        const locked = lockedDecoded.pixels[index] > 127;
        if (actor && !sweep) actorOutsideSweep += 1;
        if (sweep && locked) sweepLockedOverlap += 1;
        if (!sweep && !locked) uncovered += 1;
      }
      if (actorOutsideSweep || sweepLockedOverlap || uncovered) {
        fail(`${owner}: invalid mask nesting actorOutsideSweep=${actorOutsideSweep} sweepLockedOverlap=${sweepLockedOverlap} uncovered=${uncovered}`);
      }
      if (actorStats.percent < thresholds.headActorCoverageMinPercent
        || actorStats.percent > thresholds.headActorCoverageMaxPercent
        || sweepStats.percent < thresholds.headSweepCoverageMinPercent
        || sweepStats.percent > thresholds.headSweepCoverageMaxPercent) {
        fail(`${owner}: actor or sweep mask coverage falls outside the M2 contract`);
      }
      const dilatedSweep = dilateSquare(
        sweepDecoded.pixels,
        960,
        640,
        thresholds.sweepMaskDilationPixels,
      );
      let dilatedPixels = 0;
      for (const value of dilatedSweep) dilatedPixels += value;
      const maskCoverage = {
        headActorPixels: actorStats.pixels,
        headActorPercent: actorStats.percent,
        headSweepPixels: sweepStats.pixels,
        headSweepPercent: sweepStats.percent,
        lockedBodyPixels: lockedStats.pixels,
        lockedBodyPercent: lockedStats.percent,
        dilatedHeadSweepPixels: dilatedPixels,
        dilatedHeadSweepPercent: (dilatedPixels / (960 * 640)) * 100,
      };
      for (const [field, tolerance] of [
        ["headActorPixels", 0],
        ["headActorPercent", 0.000001],
        ["headSweepPixels", 0],
        ["headSweepPercent", 0.000001],
        ["lockedBodyPixels", 0],
        ["lockedBodyPercent", 0.000001],
        ["dilatedHeadSweepPixels", 0],
        ["dilatedHeadSweepPercent", 0.000001],
      ]) {
        compareNumber(maskCoverage[field], qa?.maskCoverage?.[field], tolerance, `${owner}: maskCoverage.${field}`);
      }

      if (videoFile && positivePair && negativePair && returnPair) {
        const decodedFrames = extractFrames(videoFile.absolutePath, [0, 30, 90, 119], 960, 640);
        if (decodedFrames.unavailable) {
          warn(`${owner}: ffmpeg unavailable; decoded M2 frame QA was not checked`);
        } else if (decodedFrames.error) {
          fail(`${owner}: M2 frame extraction failed: ${decodedFrames.error}`);
        } else {
          const base = decodedFrames.frames.get(0);
          const positivePeak = calculatePairQa(
            base,
            decodedFrames.frames.get(30),
            960,
            actorDecoded.pixels,
            sweepDecoded.pixels,
            lockedDecoded.pixels,
            dilatedSweep,
            thresholds.significantChannelDifferenceFloor,
          );
          const negativePeak = calculatePairQa(
            base,
            decodedFrames.frames.get(90),
            960,
            actorDecoded.pixels,
            sweepDecoded.pixels,
            lockedDecoded.pixels,
            dilatedSweep,
            thresholds.significantChannelDifferenceFloor,
          );
          const returned = calculatePairQa(
            base,
            decodedFrames.frames.get(119),
            960,
            actorDecoded.pixels,
            sweepDecoded.pixels,
            lockedDecoded.pixels,
            dilatedSweep,
            thresholds.significantChannelDifferenceFloor,
          );
          calculatedQa = { maskCoverage, positivePeak, negativePeak, return: returned };

          for (const [label, peak] of [["positive peak", positivePeak], ["negative peak", negativePeak]]) {
            if (peak.headSweepSignificantEnergy < thresholds.headSweepSignificantEnergyMin) {
              fail(`${owner}: ${label} head-sweep energy is too small`);
            }
            if (peak.significantChangeEnergyInsideHeadSweepPercent
              < thresholds.significantChangeEnergyInsideHeadSweepMinPercent) {
              fail(`${owner}: ${label} is insufficiently localized to the persisted head-sweep mask`);
            }
            if (peak.protectedRegionDifference.mean > thresholds.protectedRegionMeanMax
              || peak.protectedRegionDifference.p99 > thresholds.protectedRegionP99Max
              || peak.protectedRegionDifference.max > thresholds.protectedRegionMaxMax
              || peak.protectedRegionDifference.changedGt6Percent
                > thresholds.protectedRegionChangedGt6MaxPercent) {
              fail(`${owner}: ${label} changes the protected torso/tail/limb/background region beyond threshold`);
            }
          }
          if (returned.wholeFrameMeanDifference > thresholds.returnFrameMeanMax
            || returned.headSweepSignificantEnergy > thresholds.returnSweepSignificantEnergyMax) {
            fail(`${owner}: frame 119 does not return close enough to the source pose`);
          }

          if (!qa?.calculated) {
            warn(`${owner}: decoded M2 QA is not recorded yet: ${JSON.stringify(calculatedQa)}`);
          } else {
            comparePairQa(positivePeak, qa.calculated.positivePeak, `${owner}: positivePeak`);
            comparePairQa(negativePeak, qa.calculated.negativePeak, `${owner}: negativePeak`);
            comparePairQa(returned, qa.calculated.return, `${owner}: return`);
          }
        }
      }
    }
  }

  const published = sample.review?.publication?.status === "published";
  if (published) {
    publishedVideos += 1;
    for (const gate of REQUIRED_PUBLIC_GATES) {
      if (sample.review?.[gate]?.status !== "supported") {
        fail(`${owner}: published without ${gate} support`);
      }
    }
    if (qa?.visualStatus !== "pass" || !qa?.calculated) {
      fail(`${owner}: published without passing manual and decoded frame QA`);
    }
    if (sample.reviewStatus !== "published") {
      fail(`${owner}: published catalog entry must also expose reviewStatus \"published\" to the UI renderer`);
    }
    if (!isNonEmptyString(workflow.commands?.[sample.id])) {
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
    anatomyPromotion: catalog.policy?.anatomyPromotion,
    autoplay: catalog.policy?.autoplay,
    clickToPlay: catalog.policy?.clickToPlay,
  },
  calculatedQa,
  warnings,
  errors,
};

console.log(JSON.stringify(report, null, 2));
if (errors.length) {
  throw new Error(`M2 verification failed with ${errors.length} error(s):\n${errors.join("\n")}`);
}
