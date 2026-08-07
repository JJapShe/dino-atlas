import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..", "..");
const MANIFEST_PATH = path.join(ROOT, "tools", "comfyui", "motion-m2-i2v-recognition-expansion-candidates-20260806.json");
const CATALOG_PATH = path.join(ROOT, "motion-m2-i2v-samples.js");
const METADATA_PATH = path.join(ROOT, "tools", "comfyui", "motion-m2-i2v-pilot-batch-20260804.json");

const errors = [];
const warnings = [];
const fail = (message) => errors.push(message);
const isSha256 = (value) => /^[a-f0-9]{64}$/.test(value || "");
const normalize = (value) => String(value || "").replace(/\s+/g, " ").trim();
const slash = (value) => String(value || "").replace(/\\/g, "/");

function projectFile(relativePath, owner) {
  if (typeof relativePath !== "string" || !relativePath
    || path.isAbsolute(relativePath) || relativePath.includes("..")
    || /\.codex[\\/]generated_images/i.test(relativePath)) {
    fail(`${owner}: unsafe or missing project path`);
    return null;
  }
  const absolutePath = path.resolve(ROOT, relativePath);
  const relativeCheck = path.relative(ROOT, absolutePath);
  if (relativeCheck.startsWith("..") || path.isAbsolute(relativeCheck)
    || !fs.existsSync(absolutePath) || !fs.statSync(absolutePath).isFile()) {
    fail(`${owner}: missing project file ${relativePath}`);
    return null;
  }
  return absolutePath;
}

function sha256(filePath) {
  return crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");
}

function checkFile(relativePath, expectedHash, expectedBytes, owner) {
  const filePath = projectFile(relativePath, owner);
  if (!filePath) return null;
  if (!isSha256(expectedHash) || !Number.isInteger(expectedBytes) || expectedBytes <= 0) {
    fail(`${owner}: invalid SHA-256 or byte count`);
    return filePath;
  }
  const stat = fs.statSync(filePath);
  const actualHash = sha256(filePath);
  if (actualHash !== expectedHash) fail(`${owner}: SHA-256 mismatch`);
  if (stat.size !== expectedBytes) fail(`${owner}: byte-count mismatch`);
  return filePath;
}

function probeVideo(filePath, owner) {
  if (!filePath) return;
  const ffprobe = process.env.FFPROBE_PATH || "ffprobe";
  const result = spawnSync(ffprobe, [
    "-v", "error", "-count_frames", "-show_streams", "-show_format", "-of", "json", filePath,
  ], { encoding: "utf8", windowsHide: true });
  if (result.error?.code === "ENOENT") {
    warnings.push(`${owner}: ffprobe unavailable`);
    return;
  }
  if (result.status !== 0) {
    fail(`${owner}: ffprobe failed`);
    return;
  }
  const payload = JSON.parse(result.stdout);
  const video = payload.streams?.filter((stream) => stream.codec_type === "video") || [];
  const audio = payload.streams?.filter((stream) => stream.codec_type === "audio") || [];
  const stream = video[0];
  if (video.length !== 1 || audio.length !== 0 || stream?.codec_name !== "h264"
    || stream?.pix_fmt !== "yuv420p" || Number(stream?.width) !== 800
    || Number(stream?.height) !== 448 || Number(stream?.nb_read_frames || stream?.nb_frames) !== 81
    || stream?.r_frame_rate !== "16/1" || Math.abs(Number(payload.format?.duration) - 5.0625) > 0.001) {
    fail(`${owner}: stream must be silent H.264 yuv420p, 800x448, 81 frames, 16 fps, 5.0625 s`);
  }
}

const manifestSource = fs.readFileSync(MANIFEST_PATH, "utf8");
const catalogSource = fs.readFileSync(CATALOG_PATH, "utf8");
const metadataSource = fs.readFileSync(METADATA_PATH, "utf8");
if (/\.codex[\\/]generated_images/i.test(manifestSource + catalogSource + metadataSource)) {
  fail("generator-area path leak");
}

const manifest = JSON.parse(manifestSource);
const metadata = JSON.parse(metadataSource);
const sandbox = { window: {} };
new vm.Script(catalogSource, { filename: CATALOG_PATH }).runInNewContext(sandbox);
const catalog = sandbox.window.motionM2I2VSampleCatalog;
const samples = new Map((catalog?.samples || []).map((sample) => [sample.id, sample]));

const candidates = Array.isArray(manifest.candidates) ? manifest.candidates : [];
const specHistory = new Map((manifest.generationSpecHistory || []).map((item) => [item.candidateId, item.sha256]));
if (manifest.schemaVersion !== 1 || manifest.status !== "review-complete-replacement-retired"
  || candidates.length !== 3 || specHistory.size !== candidates.length
  || manifest.reviewSummary?.nativeCandidatesAccepted !== 0
  || manifest.reviewSummary?.nativeCandidatesRejected !== 3
  || manifest.reviewSummary?.safeReplacementsPublished !== 0
  || manifest.reviewSummary?.safeReplacementsRetiredBySubjectMotionPolicy !== 1) {
  fail("manifest status, counts, or generation-spec history is incomplete");
}
if (manifest.policy?.representativePromotion !== "prohibited"
  || manifest.policy?.galleryPromotion !== "prohibited"
  || manifest.policy?.anatomyPromotion !== "prohibited"
  || manifest.policy?.autoplay !== "prohibited"
  || manifest.policy?.loop !== "prohibited"
  || manifest.policy?.audio !== "prohibited"
  || !String(manifest.policy?.publicationRule || "").includes("readable dinosaur subject motion")
  || !String(manifest.policy?.publicationRule || "").includes("omit the public sample")) {
  fail("manifest subject-motion, playback, or promotion policy is incomplete");
}

let retiredReplacementCount = 0;
for (const candidate of candidates) {
  const owner = `candidate ${candidate.id || "(blank)"}`;
  if (!/^[a-z0-9][a-z0-9-]*$/.test(candidate.id || "")
    || candidate.taxonId !== "triceratops-horridus" || candidate.sceneRole !== "solo-action"
    || !Number.isSafeInteger(candidate.seed) || !candidate.positivePrompt || !candidate.negativePrompt) {
    fail(`${owner}: identity, role, seed, or prompts are incomplete`);
  }
  const source = projectFile(candidate.sourcePoster, `${owner}: source poster`);
  if (source && sha256(source) !== candidate.sourcePosterSha256) {
    fail(`${owner}: source poster SHA-256 mismatch`);
  }
  const runPath = checkFile(
    candidate.record,
    candidate.recordSha256,
    fs.existsSync(path.resolve(ROOT, candidate.record)) ? fs.statSync(path.resolve(ROOT, candidate.record)).size : 0,
    `${owner}: run record`,
  );
  if (runPath) {
    const run = JSON.parse(fs.readFileSync(runPath, "utf8"));
    const expectedSettings = { ...manifest.settings, ...(candidate.settings || {}) };
    const output = run.history?.outputs?.["12"]?.images?.[0];
    const outputPath = ["output", slash(output?.subfolder).replace(/^\/+|\/+$/g, ""), output?.filename]
      .filter(Boolean).join("/");
    if (run.schemaVersion !== 2 || run.candidateId !== candidate.id
      || run.taxonId !== candidate.taxonId || run.status?.status_str !== "success"
      || run.status?.completed !== true || run.queueResponse?.prompt_id !== run.promptId
      || run.provenance?.specSha256 !== candidate.generationSpecSha256
      || specHistory.get(candidate.id) !== candidate.generationSpecSha256
      || run.provenance?.comfyInputSha256 !== candidate.sourcePosterSha256
      || outputPath !== candidate.nativeOutput?.path) {
      fail(`${owner}: run identity, success, spec lineage, source, or output path differs`);
    }
    for (const field of [
      "width", "height", "frames", "fps", "steps", "cfg", "sampler", "scheduler", "shift", "denoise",
    ]) {
      if (run.runConfig?.[field] !== expectedSettings[field]) fail(`${owner}: run ${field} differs`);
    }
    if (run.runConfig?.seed !== candidate.seed || run.runConfig?.inputName !== candidate.inputName
      || normalize(run.runConfig?.positivePrompt) !== normalize(candidate.positivePrompt)
      || normalize(run.runConfig?.negativePrompt)
        !== normalize(`${manifest.commonNegativePrompt}, ${candidate.negativePrompt}`)) {
      fail(`${owner}: run seed, input, or prompts differ`);
    }
  }
  if (!isSha256(candidate.nativeOutput?.sha256)
    || !Number.isInteger(candidate.nativeOutput?.bytes) || candidate.nativeOutput.bytes <= 0
    || !/^output\/dino_atlas\/.+\.mp4$/i.test(candidate.nativeOutput?.path || "")) {
    fail(`${owner}: native output record is incomplete`);
  }
  if (candidate.nativeOutput?.reviewCopy !== undefined) {
    checkFile(
      candidate.nativeOutput.reviewCopy,
      candidate.nativeOutput.sha256,
      candidate.nativeOutput.bytes,
      `${owner}: native review copy`,
    );
  }
  if (candidate.reviewStatus !== "rejected" || candidate.review?.allFrames !== "rejected"
    || candidate.review?.usableSafePrefix !== "none" || !candidate.review?.firstClearDefect
    || !candidate.review?.reason) {
    fail(`${owner}: native rejection gate is incomplete`);
  }

  if (candidate.safeReplacement !== null && candidate.safeReplacement !== undefined) {
    retiredReplacementCount += 1;
    const replacement = candidate.safeReplacement;
    const sample = samples.get(replacement.id);
    const record = metadata.samples?.[replacement.id];
    if (replacement.tier !== "M2"
      || replacement.reviewStatus !== "retired-after-subject-motion-policy-20260807"
      || !sample || !record || sample.reviewStatus !== "retired"
      || sample.review?.publication?.status !== "retired"
      || record.review?.publication?.status !== "retired"
      || sample.src !== replacement.projectAsset || record.projectAsset !== replacement.projectAsset
      || sample.file?.sha256 !== replacement.sha256 || record.file?.sha256 !== replacement.sha256
      || sample.representativeEligible !== false || sample.galleryEligible !== false
      || sample.anatomyEligible !== false) {
      fail(`${owner}: retired replacement is not the matching non-promotable audit sample`);
    }
    const replacementFile = checkFile(
      replacement.projectAsset,
      replacement.sha256,
      sample?.file?.bytes,
      `${owner}: safe replacement`,
    );
    probeVideo(replacementFile, `${owner}: safe replacement`);
    if (record?.postProcess?.type !== "full-range-deterministic-safe-overlay"
      || record.postProcess.rawOutput?.sha256 !== candidate.nativeOutput?.sha256
      || record.postProcess.rawOutput?.bytes !== candidate.nativeOutput?.bytes
      || record.postProcess.effect?.intersectsDinosaur !== false
      || record.postProcess.effect?.reverseMotion !== false
      || record.postProcess.effect?.returnMotion !== false) {
      fail(`${owner}: deterministic safe-overlay lineage or boundary differs`);
    }
  }
}

if (retiredReplacementCount !== 1) {
  fail(`expected exactly one subject-motion-policy-retired replacement, found ${retiredReplacementCount}`);
}

const report = {
  schemaVersion: manifest.schemaVersion,
  candidateCount: candidates.length,
  nativeAccepted: manifest.reviewSummary?.nativeCandidatesAccepted,
  nativeRejected: manifest.reviewSummary?.nativeCandidatesRejected,
  safeReplacementsPublished: 0,
  safeReplacementsRetiredBySubjectMotionPolicy: retiredReplacementCount,
  warnings,
  errors,
};
console.log(JSON.stringify(report, null, 2));
if (errors.length) {
  throw new Error(`recognition motion batch verification failed with ${errors.length} error(s)`);
}
