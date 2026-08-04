import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..", "..");
const CATALOG_RELATIVE_PATH = "motion-m2-i2v-samples.js";
const METADATA_RELATIVE_PATH = "tools/comfyui/motion-m2-i2v-pilot-batch-20260804.json";
const EXPECTED_ID = "oviraptor-philoceratops-alert-head-turn-comfyui-wan22-i2v-m2-v1";
const EXPECTED_VIDEO_PATH = `assets/motion/m2/${EXPECTED_ID}.mp4`;
const CATALOG_PATH = path.join(ROOT, CATALOG_RELATIVE_PATH);
const METADATA_PATH = path.join(ROOT, ...METADATA_RELATIVE_PATH.split("/"));

const REQUIRED_REVIEW_GATES = [
  "sourceIntegrity",
  "workflowIntegrity",
  "frameAnatomy",
  "identityContinuity",
  "limbCountContinuity",
  "motionPlausibility",
  "backgroundIntegrity",
  "cameraIntegrity",
  "temporalIntegrity",
  "responsive",
  "publication",
];
const REQUIRED_PUBLIC_GATES = REQUIRED_REVIEW_GATES.filter((gate) => gate !== "publication");
const EXPECTED_NODE_TYPES = {
  1: "UNETLoader",
  2: "CLIPLoader",
  3: "VAELoader",
  4: "CLIPTextEncode",
  5: "CLIPTextEncode",
  6: "LoadImage",
  7: "Wan22ImageToVideoLatent",
  8: "ModelSamplingSD3",
  9: "KSampler",
  10: "VAEDecode",
  11: "CreateVideo",
  12: "SaveVideo",
};
const EXPECTED_MODELS = {
  diffusion: {
    name: "wan2.2_ti2v_5B_fp16.safetensors",
    sha256: "456f901338bd9eadbded3828b819109a9b68e8a525ca5cf8d0049a69fcfeca1e",
    bytes: 9999658848,
  },
  vae: {
    name: "wan2.2_vae.safetensors",
    sha256: "e40321bd36b9709991dae2530eb4ac303dd168276980d3e9bc4b6e2b75fed156",
    bytes: 1409400960,
  },
  "text-encoder": {
    name: "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
    sha256: "c3355d30191f1f066b26d93fba017ae9809dce6c627dda5f6a66eaa651204f68",
    bytes: 6735906897,
  },
};
const EXPECTED_STREAM = {
  width: 768,
  height: 512,
  durationSeconds: 2.041667,
  fps: 24,
  frameCount: 49,
  codec: "h264",
  pixelFormat: "yuv420p",
  container: "mp4",
  audio: false,
};

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

function isSha256(value) {
  return /^[a-f0-9]{64}$/.test(value || "");
}

function normalizeWhitespace(value) {
  return String(value || "").replace(/\s+/g, " ").trim();
}

function sameArray(actual, expected) {
  return JSON.stringify(actual) === JSON.stringify(expected);
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
  if (path.isAbsolute(relativePath)) {
    fail(`${owner}: absolute paths are prohibited`);
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

function checkHashedFile(relativePath, expectedHash, expectedBytes, owner) {
  const absolutePath = projectPath(relativePath, owner);
  if (!absolutePath || !fs.existsSync(absolutePath)) {
    fail(`${owner}: missing ${relativePath || "file"}`);
    return null;
  }
  if (!isSha256(expectedHash)) {
    fail(`${owner}: missing or invalid SHA-256 record`);
    return null;
  }
  if (expectedBytes !== undefined && (!Number.isInteger(expectedBytes) || expectedBytes <= 0)) {
    fail(`${owner}: invalid byte-count record`);
    return null;
  }
  const stat = fs.statSync(absolutePath);
  if (!stat.isFile()) {
    fail(`${owner}: expected a regular file`);
    return null;
  }
  const digest = sha256(absolutePath);
  if (digest !== expectedHash) {
    fail(`${owner}: SHA-256 mismatch; recorded ${expectedHash}, actual ${digest}`);
  }
  if (expectedBytes !== undefined && stat.size !== expectedBytes) {
    fail(`${owner}: byte-count mismatch; recorded ${expectedBytes}, actual ${stat.size}`);
  }
  return { absolutePath, sha256: digest, bytes: stat.size };
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
  if (result.error) return { error: result.error.message };
  if (result.status !== 0) return { error: result.stderr.trim() || `ffprobe exited ${result.status}` };
  try {
    const payload = JSON.parse(result.stdout);
    const streams = Array.isArray(payload.streams) ? payload.streams : [];
    const videoStreams = streams.filter((stream) => stream.codec_type === "video");
    const audioStreams = streams.filter((stream) => stream.codec_type === "audio");
    const video = videoStreams[0];
    const sideRotation = video?.side_data_list?.find(
      (entry) => Number.isFinite(Number(entry.rotation)),
    )?.rotation;
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
      rotation: Number(sideRotation ?? video?.tags?.rotate ?? 0),
      videoStreamCount: videoStreams.length,
      audioStreamCount: audioStreams.length,
      streamCount: streams.length,
      formatName: payload.format?.format_name || "",
      embeddedPrompt: payload.format?.tags?.prompt,
    };
  } catch (error) {
    return { error: `invalid ffprobe JSON: ${error.message}` };
  }
}

function checkPromotionPolicy(policy, owner) {
  for (const field of ["representativePromotion", "galleryPromotion", "anatomyPromotion"]) {
    if (policy?.[field] !== "prohibited") fail(`${owner}: ${field} must be prohibited`);
  }
  if (policy?.autoplay !== "prohibited") fail(`${owner}: autoplay must be prohibited`);
}

function checkModelRecords(models) {
  if (!Array.isArray(models) || models.length !== Object.keys(EXPECTED_MODELS).length) {
    fail("metadata: models must contain exactly the three pinned Wan2.2 dependencies");
    return;
  }
  const roles = models.map((model) => model?.role);
  if (new Set(roles).size !== roles.length) fail("metadata: duplicate model roles");
  for (const [role, expected] of Object.entries(EXPECTED_MODELS)) {
    const model = models.find((candidate) => candidate?.role === role);
    if (!model) {
      fail(`metadata: missing ${role} model record`);
      continue;
    }
    for (const field of ["name", "sha256", "bytes"]) {
      if (model[field] !== expected[field]) {
        fail(`metadata: ${role} ${field} does not match the pinned model record`);
      }
    }
    if (model.license !== "Apache-2.0" || !/^https:\/\/huggingface\.co\//.test(model.source || "")) {
      fail(`metadata: ${role} source or license record is incomplete`);
    }
  }
}

function checkWorkflowTopology(workflow, owner) {
  if (!workflow || typeof workflow !== "object" || Array.isArray(workflow)) {
    fail(`${owner}: missing workflow graph`);
    return false;
  }
  const actualIds = Object.keys(workflow).sort((left, right) => Number(left) - Number(right));
  const expectedIds = Object.keys(EXPECTED_NODE_TYPES);
  if (!sameArray(actualIds, expectedIds)) {
    fail(`${owner}: workflow must contain only core nodes 1-12`);
    return false;
  }
  for (const [id, classType] of Object.entries(EXPECTED_NODE_TYPES)) {
    if (workflow[id]?.class_type !== classType) {
      fail(`${owner}: node ${id} must be ${classType}`);
    }
  }
  return true;
}

function checkConfiguredWorkflow(workflow, metadataWorkflow, sampleRecord, models, owner) {
  if (!checkWorkflowTopology(workflow, owner)) return;
  const modelByRole = Object.fromEntries(models.map((model) => [model.role, model]));
  if (workflow["1"]?.inputs?.unet_name !== modelByRole.diffusion?.name
    || workflow["2"]?.inputs?.clip_name !== modelByRole["text-encoder"]?.name
    || workflow["3"]?.inputs?.vae_name !== modelByRole.vae?.name) {
    fail(`${owner}: workflow model filenames differ from pinned metadata`);
  }
  if (workflow["6"]?.inputs?.image !== sampleRecord.comfyInput) {
    fail(`${owner}: LoadImage does not use the recorded ComfyUI input`);
  }
  const latent = workflow["7"]?.inputs || {};
  if (latent.width !== metadataWorkflow.width || latent.height !== metadataWorkflow.height
    || latent.length !== metadataWorkflow.frames || latent.batch_size !== 1) {
    fail(`${owner}: I2V latent dimensions, frame count, or batch size differ from metadata`);
  }
  const sampling = workflow["9"]?.inputs || {};
  if (sampling.seed !== metadataWorkflow.seed || sampling.steps !== metadataWorkflow.steps
    || sampling.cfg !== metadataWorkflow.cfg || sampling.sampler_name !== metadataWorkflow.sampler
    || sampling.scheduler !== metadataWorkflow.scheduler || sampling.denoise !== metadataWorkflow.denoise) {
    fail(`${owner}: sampler configuration differs from metadata`);
  }
  if (workflow["8"]?.inputs?.shift !== metadataWorkflow.shift) {
    fail(`${owner}: ModelSamplingSD3 shift differs from metadata`);
  }
  if (workflow["11"]?.inputs?.fps !== metadataWorkflow.fps
    || workflow["11"]?.inputs?.bit_depth !== 8) {
    fail(`${owner}: CreateVideo must record 24 fps at 8-bit`);
  }
  if (workflow["12"]?.inputs?.format !== "mp4" || workflow["12"]?.inputs?.codec !== "h264") {
    fail(`${owner}: SaveVideo must use MP4/H.264`);
  }
  if (normalizeWhitespace(workflow["4"]?.inputs?.text)
    !== normalizeWhitespace(metadataWorkflow.positivePrompt)) {
    fail(`${owner}: positive prompt differs from metadata`);
  }
  if (normalizeWhitespace(workflow["5"]?.inputs?.text)
    !== normalizeWhitespace(metadataWorkflow.negativePrompt)) {
    fail(`${owner}: negative prompt differs from metadata`);
  }
}

function checkStreamRecord(record, owner) {
  for (const [field, expected] of Object.entries(EXPECTED_STREAM)) {
    const actual = record?.[field];
    if (field === "durationSeconds") {
      if (!Number.isFinite(actual) || Math.abs(actual - expected) > 0.000001) {
        fail(`${owner}: durationSeconds must be ${expected}`);
      }
    } else if (actual !== expected) {
      fail(`${owner}: ${field} must be ${expected}`);
    }
  }
  if (!isSha256(record?.sha256) || !Number.isInteger(record?.bytes) || record.bytes <= 0) {
    fail(`${owner}: video SHA-256 or byte-count record is incomplete`);
  }
}

function checkProbe(probe, owner) {
  if (probe.unavailable) {
    fail(`${owner}: ffprobe is required but unavailable`);
    return;
  }
  if (probe.error) {
    fail(`${owner}: ffprobe failed: ${probe.error}`);
    return;
  }
  if (probe.streamCount !== 1 || probe.videoStreamCount !== 1 || probe.audioStreamCount !== 0) {
    fail(`${owner}: expected exactly one video stream and no audio or extra streams`);
  }
  if (probe.width !== EXPECTED_STREAM.width || probe.height !== EXPECTED_STREAM.height
    || probe.codec !== EXPECTED_STREAM.codec || probe.pixelFormat !== EXPECTED_STREAM.pixelFormat) {
    fail(`${owner}: stream must be 768x512 H.264/yuv420p`);
  }
  if (Math.abs(probe.fps - EXPECTED_STREAM.fps) > 0.000001
    || Math.abs(probe.realFps - EXPECTED_STREAM.fps) > 0.000001
    || probe.frameCount !== EXPECTED_STREAM.frameCount) {
    fail(`${owner}: stream must contain exactly 49 frames at constant 24 fps`);
  }
  if (!Number.isFinite(probe.durationSeconds)
    || Math.abs(probe.durationSeconds - EXPECTED_STREAM.durationSeconds) > 0.000001) {
    fail(`${owner}: stream duration must be ${EXPECTED_STREAM.durationSeconds} seconds`);
  }
  if (Math.abs(probe.startSeconds) > 0.000001 || probe.rotation !== 0) {
    fail(`${owner}: stream must start at zero with no rotation metadata`);
  }
  if (!probe.formatName.split(",").includes("mp4")) {
    fail(`${owner}: container does not identify as MP4`);
  }
}

if (!fs.existsSync(CATALOG_PATH)) throw new Error(`missing ${CATALOG_RELATIVE_PATH}`);
if (!fs.existsSync(METADATA_PATH)) throw new Error(`missing ${METADATA_RELATIVE_PATH}`);

const catalogSource = fs.readFileSync(CATALOG_PATH, "utf8");
const metadataSource = fs.readFileSync(METADATA_PATH, "utf8");
const sandbox = { window: {} };
new vm.Script(catalogSource, { filename: CATALOG_PATH }).runInNewContext(sandbox);
const catalog = sandbox.window.motionM2I2VSampleCatalog;
const metadata = JSON.parse(metadataSource);

if (!catalog || typeof catalog !== "object") {
  throw new Error("motionM2I2VSampleCatalog was not exported");
}
if (/\.codex[\\/]generated_images/i.test(catalogSource)
  || /\.codex[\\/]generated_images/i.test(metadataSource)) {
  fail("generator-area path leak");
}
if (catalog.schemaVersion !== 1 || metadata.schemaVersion !== 1) {
  fail("catalog and metadata schemaVersion must both be 1");
}

checkPromotionPolicy(catalog.policy, "catalog policy");
checkPromotionPolicy(metadata.policy, "metadata policy");
if (catalog.policy?.tier !== "M2-I2V") fail("catalog policy tier must be M2-I2V");
if (catalog.policy?.clickToPlay !== "required" || catalog.policy?.audio !== "prohibited") {
  fail("catalog policy must require click-to-play and prohibit audio");
}
if (catalog.policy?.sourceFrame !== "approved project-owned still required") {
  fail("catalog policy must require an approved project-owned source still");
}
if (!sameArray(catalog.policy?.publicRequires, REQUIRED_REVIEW_GATES)) {
  fail("catalog publicRequires must list the complete I2V gate order");
}
if (!sameArray(metadata.policy?.publicationGateOrder, REQUIRED_REVIEW_GATES)) {
  fail("metadata publicationGateOrder must match catalog publicRequires");
}

const samples = Array.isArray(catalog.samples) ? catalog.samples : [];
const catalogIds = samples.map((sample) => sample?.id);
const metadataIds = Object.keys(metadata.samples || {});
if (!sameArray(catalogIds, metadataIds)) {
  fail(`catalog-metadata one-to-one mismatch: catalog=${catalogIds.join(",")} metadata=${metadataIds.join(",")}`);
}
if (catalogIds.length !== 1 || catalogIds[0] !== EXPECTED_ID) {
  fail(`catalog must contain exactly ${EXPECTED_ID}`);
}

checkModelRecords(metadata.models);
if (!isNonEmptyString(metadata.software?.comfyUiCommit)
  || metadata.software?.comfyUiVersion !== "0.25.0"
  || !metadata.software?.launchFlags?.includes("--disable-all-custom-nodes")) {
  fail("metadata: ComfyUI version, commit, or core-only launch flag is incomplete");
}

const metadataWorkflow = metadata.workflow || {};
const templateFile = checkHashedFile(
  metadataWorkflow.template,
  metadataWorkflow.templateSha256,
  undefined,
  "workflow template",
);
const runnerFile = checkHashedFile(
  metadataWorkflow.runner,
  metadataWorkflow.runnerSha256,
  undefined,
  "I2V runner",
);
const runRecordFile = checkHashedFile(
  metadataWorkflow.runRecord,
  metadataWorkflow.runRecordSha256,
  undefined,
  "I2V run record",
);

if (templateFile) {
  try {
    checkWorkflowTopology(JSON.parse(fs.readFileSync(templateFile.absolutePath, "utf8")), "workflow template");
  } catch (error) {
    fail(`workflow template: invalid JSON: ${error.message}`);
  }
}
if (runnerFile && !/\.py$/i.test(metadataWorkflow.runner || "")) {
  fail("I2V runner must be a project Python script");
}

let runRecord = null;
if (runRecordFile) {
  try {
    runRecord = JSON.parse(fs.readFileSync(runRecordFile.absolutePath, "utf8"));
  } catch (error) {
    fail(`I2V run record: invalid JSON: ${error.message}`);
  }
}

let publishedVideos = 0;
let probedStream = null;
for (const sample of samples) {
  const owner = sample?.id || "sample:(blank)";
  const record = metadata.samples?.[sample.id];
  if (!record) {
    fail(`${owner}: missing metadata record`);
    continue;
  }

  if (sample.tier !== "M2" || sample.motionClass !== "generative-i2v" || sample.sceneRole !== "solo") {
    fail(`${owner}: must remain an M2 generative-I2V solo candidate`);
  }
  if (sample.representativeEligible !== false || sample.galleryEligible !== false
    || sample.anatomyEligible !== false || record.review?.representativeEligible !== false
    || record.review?.galleryEligible !== false || record.review?.anatomyEligible !== false) {
    fail(`${owner}: representative, gallery, and anatomy eligibility must all be false`);
  }
  if (sample.src !== EXPECTED_VIDEO_PATH || record.projectAsset !== EXPECTED_VIDEO_PATH) {
    fail(`${owner}: catalog and metadata must use the expected versioned M2 asset path`);
  }
  if (!/^assets\/dinosaurs\/oviraptor-philoceratops-[a-z0-9.-]*-v[0-9]+\.png$/i.test(sample.poster || "")
    || sample.poster !== record.sourcePoster) {
    fail(`${owner}: source poster must be the same species-prefixed, versioned project PNG in both records`);
  }
  if (sample.provenance?.metadataRecord
      !== `${METADATA_RELATIVE_PATH}#/samples/${sample.id}`
    || sample.provenance?.runRecord !== metadataWorkflow.runRecord) {
    fail(`${owner}: metadata or run-record provenance pointer is invalid`);
  }
  for (const field of ["sourceLicense", "modelLicense", "workflow"]) {
    if (!isNonEmptyString(sample.provenance?.[field])) fail(`${owner}: incomplete provenance ${field}`);
  }
  if (!isNonEmptyString(record.sourceLicense) || !isNonEmptyString(record.motion)
    || !Array.isArray(record.identityCuesPreserved) || record.identityCuesPreserved.length < 8) {
    fail(`${owner}: source license, motion boundary, or identity cues are incomplete`);
  }

  const sourceFile = checkHashedFile(
    record.sourcePoster,
    record.sourcePosterSha256,
    record.sourcePosterBytes,
    `${owner}: source poster`,
  );
  if (sourceFile && sample.poster !== record.sourcePoster) {
    fail(`${owner}: source poster path mismatch`);
  }

  if (JSON.stringify(sample.file) !== JSON.stringify(record.file)) {
    fail(`${owner}: catalog and metadata video file records differ`);
  }
  checkStreamRecord(sample.file, `${owner}: catalog file record`);
  checkStreamRecord(record.file, `${owner}: metadata file record`);
  const videoFile = checkHashedFile(
    sample.src,
    sample.file?.sha256,
    sample.file?.bytes,
    `${owner}: video`,
  );
  if (videoFile) {
    probedStream = probeMedia(videoFile.absolutePath);
    checkProbe(probedStream, `${owner}: video`);
    if (!probedStream.unavailable && !probedStream.error) {
      const probeRecord = {
        width: probedStream.width,
        height: probedStream.height,
        durationSeconds: probedStream.durationSeconds,
        fps: probedStream.fps,
        frameCount: probedStream.frameCount,
        codec: probedStream.codec,
        pixelFormat: probedStream.pixelFormat,
        container: probedStream.formatName.split(",").includes("mp4") ? "mp4" : probedStream.formatName,
        audio: probedStream.audioStreamCount > 0,
      };
      for (const [field, actual] of Object.entries(probeRecord)) {
        const recorded = sample.file?.[field];
        const matches = field === "durationSeconds"
          ? Math.abs(actual - recorded) <= 0.000001
          : actual === recorded;
        if (!matches) fail(`${owner}: ${field} differs between ffprobe and file record`);
      }
    }
  }

  for (const gate of REQUIRED_REVIEW_GATES) {
    if (!isNonEmptyString(sample.review?.[gate]?.status)
      || !isNonEmptyString(sample.review?.[gate]?.note)
      || !isNonEmptyString(record.review?.[gate]?.status)
      || !isNonEmptyString(record.review?.[gate]?.note)) {
      fail(`${owner}: incomplete ${gate} review gate`);
    }
    if (sample.review?.[gate]?.status !== record.review?.[gate]?.status) {
      fail(`${owner}: catalog and metadata ${gate} status differ`);
    }
  }

  const publicationStatus = sample.review?.publication?.status;
  if (sample.reviewStatus !== publicationStatus
    || record.review?.publication?.status !== publicationStatus
    || metadata.status !== publicationStatus) {
    fail(`${owner}: catalog, metadata, and publication status must agree`);
  }
  const published = publicationStatus === "published" || publicationStatus === "public"
    || sample.public === true || record.public === true || metadata.public === true
    || sample.visibility === "public" || record.visibility === "public" || metadata.visibility === "public";
  if (published) {
    publishedVideos += 1;
    if (publicationStatus !== "published" && publicationStatus !== "public") {
      fail(`${owner}: public visibility requires a public or published publication gate`);
    }
    for (const gate of REQUIRED_PUBLIC_GATES) {
      if (sample.review?.[gate]?.status !== "supported"
        || record.review?.[gate]?.status !== "supported") {
        fail(`${owner}: published without supported ${gate} gate`);
      }
    }
  }

  if (runRecord) {
    if (runRecord.schemaVersion !== 1 || runRecord.promptId !== metadataWorkflow.promptId
      || runRecord.queueResponse?.prompt_id !== metadataWorkflow.promptId
      || runRecord.status?.status_str !== "success" || runRecord.status?.completed !== true
      || Object.keys(runRecord.queueResponse?.node_errors || {}).length !== 0) {
      fail(`${owner}: run record does not document a successful matching prompt`);
    }
    const successMessage = runRecord.status?.messages?.some(
      ([event, data]) => event === "execution_success" && data?.prompt_id === metadataWorkflow.promptId,
    );
    if (!successMessage) fail(`${owner}: run record lacks the matching execution_success event`);
    if (runRecord.history?.prompt?.[1] !== metadataWorkflow.promptId
      || runRecord.history?.status?.status_str !== "success"
      || runRecord.history?.status?.completed !== true) {
      fail(`${owner}: run history does not match the successful prompt`);
    }
    checkConfiguredWorkflow(runRecord.workflow, metadataWorkflow, record, metadata.models, `${owner}: run workflow`);
    const historyWorkflow = runRecord.history?.prompt?.[2];
    checkConfiguredWorkflow(historyWorkflow, metadataWorkflow, record, metadata.models, `${owner}: history workflow`);
    if (JSON.stringify(runRecord.workflow) !== JSON.stringify(historyWorkflow)) {
      fail(`${owner}: queued workflow and history workflow differ`);
    }
    const output = runRecord.history?.outputs?.["12"]?.images?.[0];
    if (!output || output.type !== "output" || !/\.mp4$/i.test(output.filename || "")) {
      fail(`${owner}: run record lacks the generated MP4 output record`);
    }
    if (probedStream && !probedStream.unavailable && !probedStream.error) {
      if (!isNonEmptyString(probedStream.embeddedPrompt)) {
        fail(`${owner}: MP4 lacks the embedded ComfyUI prompt graph`);
      } else {
        try {
          const embeddedWorkflow = JSON.parse(probedStream.embeddedPrompt);
          checkConfiguredWorkflow(
            embeddedWorkflow,
            metadataWorkflow,
            record,
            metadata.models,
            `${owner}: MP4 embedded workflow`,
          );
          if (embeddedWorkflow["6"]?.is_changed?.[0] !== record.sourcePosterSha256) {
            fail(`${owner}: MP4 embedded source-image hash differs from the approved source poster`);
          }
        } catch (error) {
          fail(`${owner}: MP4 embedded prompt is invalid JSON: ${error.message}`);
        }
      }
    }
  }
}

const report = {
  schemaVersion: catalog.schemaVersion,
  sampleCount: samples.length,
  publishedVideos,
  policy: {
    tier: catalog.policy?.tier,
    representativePromotion: catalog.policy?.representativePromotion,
    galleryPromotion: catalog.policy?.galleryPromotion,
    anatomyPromotion: catalog.policy?.anatomyPromotion,
    autoplay: catalog.policy?.autoplay,
    clickToPlay: catalog.policy?.clickToPlay,
  },
  stream: probedStream && !probedStream.unavailable && !probedStream.error ? {
    width: probedStream.width,
    height: probedStream.height,
    fps: probedStream.fps,
    frameCount: probedStream.frameCount,
    codec: probedStream.codec,
    pixelFormat: probedStream.pixelFormat,
    audioStreams: probedStream.audioStreamCount,
  } : null,
  warnings,
  errors,
};

console.log(JSON.stringify(report, null, 2));
if (errors.length) {
  throw new Error(`M2 I2V verification failed with ${errors.length} error(s):\n${errors.join("\n")}`);
}
