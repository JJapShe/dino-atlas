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
const EVENT_CANDIDATES_RELATIVE_PATH = "tools/comfyui/motion-m2-i2v-event-candidates-20260806.json";
const CATALOG_PATH = path.join(ROOT, CATALOG_RELATIVE_PATH);
const METADATA_PATH = path.join(ROOT, ...METADATA_RELATIVE_PATH.split("/"));
const EVENT_CANDIDATES_PATH = path.join(ROOT, ...EVENT_CANDIDATES_RELATIVE_PATH.split("/"));

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
const REQUIRED_STREAM_ENCODING = {
  codec: "h264",
  pixelFormat: "yuv420p",
  container: "mp4",
  audio: false,
};
const STREAM_RECORD_FIELDS = [
  "sha256",
  "bytes",
  "width",
  "height",
  "durationSeconds",
  "fps",
  "frameCount",
  "codec",
  "pixelFormat",
  "container",
  "audio",
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

function isSha256(value) {
  return /^[a-f0-9]{64}$/.test(value || "");
}

function normalizeWhitespace(value) {
  return String(value || "").replace(/\s+/g, " ").trim();
}

function sameArray(actual, expected) {
  return JSON.stringify(actual) === JSON.stringify(expected);
}

function sameStringSet(actual, expected) {
  return sameArray([...actual].sort(), [...expected].sort());
}

function nearlyEqual(actual, expected, tolerance = 0.000001) {
  return Number.isFinite(actual) && Number.isFinite(expected)
    && Math.abs(actual - expected) <= tolerance;
}

function normalizeProjectSlashes(value) {
  return String(value || "").replace(/\\/g, "/");
}

function isSafeCatalogId(value) {
  return /^[a-z0-9][a-z0-9-]*$/i.test(value || "");
}

function hasPortablePlaceholder(command, placeholder) {
  return String(command || "").includes(`{${placeholder}}`);
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

function checkMp4FastStart(filePath, owner, { required = true } = {}) {
  const bytes = fs.readFileSync(filePath);
  const moovIndex = bytes.indexOf(Buffer.from("moov"));
  const mdatIndex = bytes.indexOf(Buffer.from("mdat"));
  if (moovIndex < 0 || mdatIndex < 0 || moovIndex > mdatIndex) {
    const message = `${owner}: MP4 faststart layout is missing (moov must precede mdat)`;
    if (required) fail(message);
    else warn(`${message}; allowed only for the legacy top-level-workflow sample`);
  }
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
    fail(`${owner}: CreateVideo must record ${metadataWorkflow.fps} fps at 8-bit`);
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

function checkStreamRecord(record, owner, { requireFileIdentity = true } = {}) {
  if (!record || typeof record !== "object" || Array.isArray(record)) {
    fail(`${owner}: missing stream record`);
    return false;
  }
  if (requireFileIdentity
    && (!isSha256(record.sha256) || !Number.isInteger(record.bytes) || record.bytes <= 0)) {
    fail(`${owner}: video SHA-256 or byte-count record is incomplete`);
  }
  if (!Number.isInteger(record.width) || record.width <= 0 || record.width % 32 !== 0
    || !Number.isInteger(record.height) || record.height <= 0 || record.height % 32 !== 0) {
    fail(`${owner}: width and height must be positive multiples of 32`);
  }
  if (!Number.isInteger(record.frameCount) || record.frameCount <= 0
    || (record.frameCount - 1) % 4 !== 0) {
    fail(`${owner}: Wan frameCount must be a positive 4n+1 integer`);
  }
  if (!Number.isFinite(record.fps) || record.fps <= 0) {
    fail(`${owner}: fps must be positive`);
  }
  const calculatedDuration = record.frameCount / record.fps;
  if (!Number.isFinite(record.durationSeconds)
    || !nearlyEqual(record.durationSeconds, calculatedDuration)) {
    fail(`${owner}: durationSeconds must equal frameCount/fps (${calculatedDuration})`);
  }
  for (const [field, expected] of Object.entries(REQUIRED_STREAM_ENCODING)) {
    if (record[field] !== expected) {
      fail(`${owner}: ${field} must be ${expected}`);
    }
  }
  return true;
}

function compareStreamRecords(actual, expected, owner) {
  for (const field of STREAM_RECORD_FIELDS) {
    const matches = field === "durationSeconds"
      ? nearlyEqual(actual?.[field], expected?.[field])
      : actual?.[field] === expected?.[field];
    if (!matches) fail(`${owner}: ${field} differs between catalog and metadata records`);
  }
}

function checkProbe(probe, expected, owner) {
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
  if (probe.width !== expected.width || probe.height !== expected.height
    || probe.codec !== expected.codec || probe.pixelFormat !== expected.pixelFormat) {
    fail(`${owner}: stream geometry or H.264/yuv420p encoding differs from its file record`);
  }
  if (!nearlyEqual(probe.fps, expected.fps)
    || !nearlyEqual(probe.realFps, expected.fps)
    || probe.frameCount !== expected.frameCount) {
    fail(`${owner}: frame count or constant frame rate differs from its file record`);
  }
  if (!nearlyEqual(probe.durationSeconds, expected.durationSeconds)) {
    fail(`${owner}: stream duration must be ${expected.durationSeconds} seconds`);
  }
  if (Math.abs(probe.startSeconds) > 0.000001 || probe.rotation !== 0) {
    fail(`${owner}: stream must start at zero with no rotation metadata`);
  }
  if (!probe.formatName.split(",").includes("mp4")) {
    fail(`${owner}: container does not identify as MP4`);
  }
}

function resolveSampleWorkflow(metadata, record, sample, owner) {
  if (record?.workflow && typeof record.workflow === "object" && !Array.isArray(record.workflow)) {
    return record.workflow;
  }
  const fallback = metadata.workflow;
  if (fallback && sample.provenance?.runRecord === fallback.runRecord) return fallback;
  fail(`${owner}: missing per-sample workflow and no matching legacy workflow fallback`);
  return null;
}

function loadWorkflowArtifacts(metadataWorkflow, owner) {
  if (!metadataWorkflow) return { runRecord: null };
  const templateFile = checkHashedFile(
    metadataWorkflow.template,
    metadataWorkflow.templateSha256,
    undefined,
    `${owner}: workflow template`,
  );
  const runnerFile = checkHashedFile(
    metadataWorkflow.runner,
    metadataWorkflow.runnerSha256,
    undefined,
    `${owner}: I2V runner`,
  );
  const runRecordFile = checkHashedFile(
    metadataWorkflow.runRecord,
    metadataWorkflow.runRecordSha256,
    undefined,
    `${owner}: I2V run record`,
  );

  if (templateFile) {
    try {
      checkWorkflowTopology(
        JSON.parse(fs.readFileSync(templateFile.absolutePath, "utf8")),
        `${owner}: workflow template`,
      );
    } catch (error) {
      fail(`${owner}: workflow template contains invalid JSON: ${error.message}`);
    }
  }
  if (runnerFile && !/\.py$/i.test(metadataWorkflow.runner || "")) {
    fail(`${owner}: I2V runner must be a project Python script`);
  }

  let runRecord = null;
  if (runRecordFile) {
    try {
      runRecord = JSON.parse(fs.readFileSync(runRecordFile.absolutePath, "utf8"));
    } catch (error) {
      fail(`${owner}: I2V run record contains invalid JSON: ${error.message}`);
    }
  }
  return { runRecord };
}

function checkGenerationStreamConfig(metadataWorkflow, stream, owner) {
  if (!metadataWorkflow || !stream) return;
  const expected = {
    width: stream.width,
    height: stream.height,
    frames: stream.frameCount,
    fps: stream.fps,
  };
  for (const [field, value] of Object.entries(expected)) {
    if (metadataWorkflow[field] !== value) {
      fail(`${owner}: workflow ${field} must match the generated stream (${value})`);
    }
  }
}

function checkPostProcess(postProcess, sample, owner) {
  if (!postProcess) return null;
  if (!postProcess || typeof postProcess !== "object" || Array.isArray(postProcess)) {
    fail(`${owner}: postProcess must be an object`);
    return null;
  }
  const allowedTypes = new Set([
    "safe-prefix-last-frame-hold",
    "safe-prefix-slow-forward",
    "safe-prefix-reverse-return",
    "safe-prefix-slow-hold-reverse-return",
    "safe-prefix-double-reverse-return",
    "full-range-deterministic-safe-overlay",
  ]);
  if (!allowedTypes.has(postProcess.type)) {
    fail(`${owner}: unsupported postProcess.type`);
  }

  const rawOutput = postProcess.rawOutput;
  if (!rawOutput || typeof rawOutput !== "object" || Array.isArray(rawOutput)) {
    fail(`${owner}: postProcess.rawOutput is required`);
    return null;
  }
  const rawPath = normalizeProjectSlashes(rawOutput.path);
  if (!/^output\/dino_atlas\/[a-z0-9][a-z0-9._/-]*\.mp4$/i.test(rawPath)
    || rawPath.includes("..") || rawPath.includes("//") || rawOutput.path !== rawPath) {
    fail(`${owner}: rawOutput.path must be a portable ComfyUI-root path under output/dino_atlas`);
  }
  if (!isSha256(rawOutput.sha256) || !Number.isInteger(rawOutput.bytes) || rawOutput.bytes <= 0) {
    fail(`${owner}: rawOutput SHA-256 or byte-count record is incomplete`);
  }
  checkStreamRecord(rawOutput.stream, `${owner}: raw output stream`, { requireFileIdentity: false });

  const range = postProcess.acceptedFrameRange;
  const validRange = Array.isArray(range) && range.length === 2
    && range.every(Number.isInteger) && range[0] === 0
    && range[1] >= range[0] && range[1] < (rawOutput.stream?.frameCount ?? 0);
  if (!validRange) {
    fail(`${owner}: acceptedFrameRange must be [0, endInclusive] inside the raw stream`);
  }
  const acceptedEnd = validRange ? range[1] : null;
  const acceptedFrameCount = acceptedEnd === null ? null : acceptedEnd + 1;
  let expectedFilter = null;
  let expectedFinalFrames = null;
  if (postProcess.type === "safe-prefix-last-frame-hold") {
    if (!Number.isInteger(postProcess.trimEndFrameExclusive)
      || postProcess.trimEndFrameExclusive !== acceptedFrameCount) {
      fail(`${owner}: trimEndFrameExclusive must equal accepted endInclusive + 1`);
    }
    if (!Number.isInteger(postProcess.holdFrames) || postProcess.holdFrames <= 0) {
      fail(`${owner}: holdFrames must be a positive integer`);
    }
    const expectedHoldSeconds = postProcess.holdFrames / rawOutput.stream?.fps;
    if (!nearlyEqual(postProcess.holdSeconds, expectedHoldSeconds)) {
      fail(`${owner}: holdSeconds must equal holdFrames/raw fps (${expectedHoldSeconds})`);
    }
    if (acceptedFrameCount !== null && Number.isFinite(postProcess.holdSeconds)) {
      expectedFilter = `trim=end_frame=${acceptedFrameCount},tpad=stop_mode=clone:stop_duration=${postProcess.holdSeconds},format=yuv420p`;
    }
    if (Number.isInteger(acceptedFrameCount) && Number.isInteger(postProcess.holdFrames)) {
      expectedFinalFrames = acceptedFrameCount + postProcess.holdFrames;
    }
  } else if (postProcess.type === "safe-prefix-slow-forward") {
    const forwardRange = postProcess.forwardFrameRange;
    const validForward = validRange && acceptedEnd >= 1
      && sameArray(forwardRange, [0, acceptedEnd]);
    if (!validForward) {
      fail(`${owner}: forwardFrameRange must exactly match an acceptedFrameRange containing at least two frames`);
    }

    const scaleNumerator = postProcess.timeScaleNumerator;
    const scaleDenominator = postProcess.timeScaleDenominator;
    const validScale = Number.isSafeInteger(scaleNumerator) && scaleNumerator > 0
      && Number.isSafeInteger(scaleDenominator) && scaleDenominator > 0;
    if (!validScale) {
      fail(`${owner}: timeScaleNumerator and timeScaleDenominator must be positive safe integers`);
    } else if (scaleNumerator <= scaleDenominator) {
      fail(`${owner}: timeScaleNumerator must exceed timeScaleDenominator for forward-only slowing`);
    }
    const rawFps = rawOutput.stream?.fps;
    if (!Number.isSafeInteger(postProcess.outputFps) || postProcess.outputFps <= 0
      || postProcess.outputFps > rawFps) {
      fail(`${owner}: outputFps must be a positive integer no greater than the raw fps`);
    }
    if (!Number.isInteger(postProcess.trimEndFrameExclusive)
      || postProcess.trimEndFrameExclusive <= 0) {
      fail(`${owner}: trimEndFrameExclusive must be a positive integer`);
    }

    const prohibitedSequenceFields = Object.keys(postProcess).filter(
      (field) => /reverse|hold|return|join/i.test(field),
    );
    if (prohibitedSequenceFields.length) {
      fail(`${owner}: safe-prefix-slow-forward prohibits reverse, hold, return, and join fields (${prohibitedSequenceFields.join(", ")})`);
    }

    if (validForward && validScale) {
      const scaledIntervalNumerator = (acceptedFrameCount - 1)
        * scaleNumerator * postProcess.outputFps;
      const scaledIntervalDenominator = scaleDenominator * rawFps;
      const scaledFinalIntervalCount = scaledIntervalNumerator / scaledIntervalDenominator;
      if (!Number.isSafeInteger(scaledIntervalNumerator)
        || !Number.isFinite(scaledIntervalDenominator) || scaledIntervalDenominator <= 0) {
        fail(`${owner}: slowed frame-count calculation exceeds the safe integer range`);
      } else if (!Number.isSafeInteger(scaledFinalIntervalCount)) {
        fail(`${owner}: accepted frame intervals, time-scale ratio, and output fps must yield an integer frame count`);
      } else {
        expectedFinalFrames = scaledFinalIntervalCount + 1;
        if (postProcess.trimEndFrameExclusive !== expectedFinalFrames) {
          fail(`${owner}: trimEndFrameExclusive must equal the deterministic slowed result (${expectedFinalFrames})`);
        }
      }
      expectedFilter = `trim=start_frame=0:end_frame=${acceptedFrameCount},setpts=(${scaleNumerator}/${scaleDenominator})*PTS,fps=${postProcess.outputFps},trim=end_frame=${postProcess.trimEndFrameExclusive},setpts=PTS-STARTPTS,format=yuv420p`;
    }
  } else if (postProcess.type === "safe-prefix-reverse-return") {
    const forwardRange = postProcess.forwardFrameRange;
    const reverseRange = postProcess.reverseFrameRange;
    const validForward = validRange && sameArray(forwardRange, [0, acceptedEnd]);
    const validReverse = Array.isArray(reverseRange) && reverseRange.length === 2
      && reverseRange.every(Number.isInteger)
      && reverseRange[0] >= 0 && reverseRange[0] <= acceptedEnd
      && reverseRange[1] === acceptedEnd;
    if (!validForward) {
      fail(`${owner}: forwardFrameRange must exactly match acceptedFrameRange`);
    }
    if (!validReverse) {
      fail(`${owner}: reverseFrameRange must be [returnStart, acceptedEnd]`);
    }
    if (postProcess.joinFrame !== acceptedEnd) {
      fail(`${owner}: joinFrame must equal accepted endInclusive`);
    }
    if (validReverse && acceptedFrameCount !== null) {
      const returnStart = reverseRange[0];
      const hasTurnaroundHold = Object.hasOwn(postProcess, "turnaroundHoldFrames")
        || Object.hasOwn(postProcess, "turnaroundHoldSeconds");
      const turnaroundHoldFrames = hasTurnaroundHold ? postProcess.turnaroundHoldFrames : 0;
      if (!Number.isInteger(turnaroundHoldFrames) || turnaroundHoldFrames < 0) {
        fail(`${owner}: turnaroundHoldFrames must be a non-negative integer`);
      }
      const expectedTurnaroundHoldSeconds = turnaroundHoldFrames / rawOutput.stream?.fps;
      if (hasTurnaroundHold
        && !nearlyEqual(postProcess.turnaroundHoldSeconds, expectedTurnaroundHoldSeconds)) {
        fail(`${owner}: turnaroundHoldSeconds must equal turnaroundHoldFrames/raw fps (${expectedTurnaroundHoldSeconds})`);
      }
      const forwardTail = turnaroundHoldFrames > 0
        ? `,tpad=stop_mode=clone:stop_duration=${postProcess.turnaroundHoldSeconds}`
        : "";
      expectedFilter = `split=2[a][b];[a]trim=end_frame=${acceptedFrameCount},setpts=PTS-STARTPTS${forwardTail}[f];[b]trim=start_frame=${returnStart}:end_frame=${acceptedFrameCount},reverse,setpts=PTS-STARTPTS[r];[f][r]concat=n=2:v=1:a=0,format=yuv420p`;
      expectedFinalFrames = acceptedFrameCount + turnaroundHoldFrames
        + (acceptedEnd - returnStart + 1);
    }
  } else if (postProcess.type === "safe-prefix-slow-hold-reverse-return") {
    const forwardRange = postProcess.forwardFrameRange;
    const reverseRange = postProcess.reverseFrameRange;
    const validForward = validRange && sameArray(forwardRange, [0, acceptedEnd]);
    const validReverse = validRange && Array.isArray(reverseRange) && reverseRange.length === 2
      && reverseRange.every(Number.isInteger)
      && reverseRange[0] === 0 && reverseRange[1] === acceptedEnd - 1;
    if (!validForward) {
      fail(`${owner}: forwardFrameRange must exactly match acceptedFrameRange`);
    }
    if (!validReverse) {
      fail(`${owner}: reverseFrameRange must be [0, acceptedEnd - 1]`);
    }
    if (postProcess.holdSourceFrame !== acceptedEnd) {
      fail(`${owner}: holdSourceFrame must equal accepted endInclusive`);
    }
    if (!Number.isInteger(postProcess.extraHoldFrames) || postProcess.extraHoldFrames <= 0) {
      fail(`${owner}: extraHoldFrames must be a positive integer`);
    }
    const expectedExtraHoldSeconds = postProcess.extraHoldFrames / rawOutput.stream?.fps;
    if (!nearlyEqual(postProcess.extraHoldSeconds, expectedExtraHoldSeconds)) {
      fail(`${owner}: extraHoldSeconds must equal extraHoldFrames/raw fps (${expectedExtraHoldSeconds})`);
    }
    if (!Number.isInteger(postProcess.timeScale) || postProcess.timeScale < 2) {
      fail(`${owner}: timeScale must be an integer of at least two`);
    }
    if (postProcess.outputFps !== rawOutput.stream?.fps) {
      fail(`${owner}: outputFps must equal the raw fps`);
    }
    if (!Number.isInteger(postProcess.trimEndFrameExclusive)
      || postProcess.trimEndFrameExclusive <= 0) {
      fail(`${owner}: trimEndFrameExclusive must be a positive integer`);
    }
    if (validForward && validReverse && Number.isInteger(postProcess.extraHoldFrames)) {
      const holdEndExclusive = postProcess.holdSourceFrame + 1;
      const reverseEndExclusive = reverseRange[1] + 1;
      expectedFilter = `split=3[a][b][c];[a]trim=start_frame=0:end_frame=${acceptedFrameCount},setpts=PTS-STARTPTS[f];[b]trim=start_frame=${postProcess.holdSourceFrame}:end_frame=${holdEndExclusive},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=${postProcess.extraHoldSeconds}[h];[c]trim=start_frame=0:end_frame=${reverseEndExclusive},reverse,setpts=PTS-STARTPTS[r];[f][h][r]concat=n=3:v=1:a=0,setpts=${postProcess.timeScale}*PTS,fps=${postProcess.outputFps},trim=end_frame=${postProcess.trimEndFrameExclusive},setpts=PTS-STARTPTS,format=yuv420p`;
      const sourceTimelineFrames = acceptedFrameCount + 1 + postProcess.extraHoldFrames
        + (reverseRange[1] - reverseRange[0] + 1);
      expectedFinalFrames = (sourceTimelineFrames - 1) * postProcess.timeScale + 1;
      if (postProcess.trimEndFrameExclusive !== expectedFinalFrames) {
        fail(`${owner}: trimEndFrameExclusive must equal the deterministic slowed result (${expectedFinalFrames})`);
      }
    }
  } else if (postProcess.type === "safe-prefix-double-reverse-return") {
    const firstForward = postProcess.firstForwardFrameRange;
    const firstReverse = postProcess.firstReverseFrameRange;
    const secondForward = postProcess.secondForwardFrameRange;
    const secondReverse = postProcess.secondReverseFrameRange;
    const validFirstForward = validRange && sameArray(firstForward, [0, acceptedEnd]);
    const validFirstReverse = validRange && sameArray(firstReverse, [0, acceptedEnd - 1]);
    const validSecondForward = validRange && Array.isArray(secondForward)
      && secondForward.length === 2 && secondForward.every(Number.isInteger)
      && secondForward[0] === 0 && secondForward[1] > 0 && secondForward[1] < acceptedEnd;
    const validSecondReverse = validSecondForward
      && sameArray(secondReverse, [0, secondForward[1] - 1]);
    if (!validFirstForward) {
      fail(`${owner}: firstForwardFrameRange must exactly match acceptedFrameRange`);
    }
    if (!validFirstReverse) {
      fail(`${owner}: firstReverseFrameRange must be [0, acceptedEnd - 1]`);
    }
    if (!validSecondForward) {
      fail(`${owner}: secondForwardFrameRange must be a shorter [0, endInclusive] safe range`);
    }
    if (!validSecondReverse) {
      fail(`${owner}: secondReverseFrameRange must omit the second turnaround duplicate`);
    }
    if (!Number.isInteger(postProcess.trimEndFrameExclusive)
      || postProcess.trimEndFrameExclusive <= 0) {
      fail(`${owner}: trimEndFrameExclusive must be a positive integer`);
    }
    if (validFirstForward && validFirstReverse && validSecondForward && validSecondReverse) {
      const firstForwardEnd = firstForward[1] + 1;
      const firstReverseEnd = firstReverse[1] + 1;
      const secondForwardEnd = secondForward[1] + 1;
      const secondReverseEnd = secondReverse[1] + 1;
      expectedFilter = `split=4[a][b][c][d];[a]trim=start_frame=0:end_frame=${firstForwardEnd},setpts=PTS-STARTPTS[f1];[b]trim=start_frame=0:end_frame=${firstReverseEnd},reverse,setpts=PTS-STARTPTS[r1];[c]trim=start_frame=0:end_frame=${secondForwardEnd},setpts=PTS-STARTPTS[f2];[d]trim=start_frame=0:end_frame=${secondReverseEnd},reverse,setpts=PTS-STARTPTS[r2];[f1][r1][f2][r2]concat=n=4:v=1:a=0,trim=end_frame=${postProcess.trimEndFrameExclusive},setpts=PTS-STARTPTS,format=yuv420p`;
      const concatenatedFrames = firstForwardEnd + firstReverseEnd
        + secondForwardEnd + secondReverseEnd;
      expectedFinalFrames = Math.min(concatenatedFrames, postProcess.trimEndFrameExclusive);
      if (postProcess.trimEndFrameExclusive >= concatenatedFrames) {
        fail(`${owner}: trimEndFrameExclusive must remove at least one duplicate boundary frame`);
      }
    }
  } else if (postProcess.type === "full-range-deterministic-safe-overlay") {
    if (!validRange || acceptedEnd !== rawOutput.stream?.frameCount - 1) {
      fail(`${owner}: deterministic safe overlay must preserve the complete raw frame range`);
    }
    expectedFinalFrames = rawOutput.stream?.frameCount;
    expectedFilter = "[0:v][1:v]overlay=0:0:shortest=1:format=auto,format=yuv420p";

    if (!isNonEmptyString(postProcess.overlayScript)
      || !/\.ps1$/i.test(postProcess.overlayScript)
      || !isSha256(postProcess.overlayScriptSha256)
      || !Number.isInteger(postProcess.overlayScriptBytes)
      || postProcess.overlayScriptBytes <= 0) {
      fail(`${owner}: deterministic safe-overlay script record is incomplete`);
    } else {
      checkHashedFile(
        postProcess.overlayScript,
        postProcess.overlayScriptSha256,
        postProcess.overlayScriptBytes,
        `${owner}: deterministic safe-overlay script`,
      );
    }

    const effect = postProcess.effect;
    const activeFrames = effect?.activeFrameRange;
    const bounds = effect?.protectedEmptyAirBounds;
    const validActiveFrames = Array.isArray(activeFrames) && activeFrames.length === 2
      && activeFrames.every(Number.isInteger) && activeFrames[0] >= 0
      && activeFrames[0] < activeFrames[1] && activeFrames[1] < rawOutput.stream?.frameCount;
    const validBounds = Array.isArray(bounds) && bounds.length === 4
      && bounds.every(Number.isInteger) && bounds[0] >= 0 && bounds[1] >= 0
      && bounds[2] > bounds[0] && bounds[3] > bounds[1]
      && bounds[2] < rawOutput.stream?.width && bounds[3] < rawOutput.stream?.height;
    if (!effect || effect.subject !== "nostril-dust-exhale"
      || effect.count !== 1 || !validActiveFrames || !validBounds
      || effect.intersectsDinosaur !== false || effect.intersectsGround !== false
      || effect.reverseMotion !== false || effect.returnMotion !== false
      || effect.loop !== false || effect.autoplay !== false) {
      fail(`${owner}: deterministic safe-overlay effect boundary is incomplete or unsafe`);
    }
  }
  if (!isNonEmptyString(postProcess.ffmpegFilter) || postProcess.ffmpegFilter !== expectedFilter) {
    fail(`${owner}: ffmpegFilter must exactly encode the declared safe-prefix post-process`);
  }
  const command = normalizeWhitespace(postProcess.ffmpegCommand);
  if (postProcess.type === "safe-prefix-slow-forward"
    && /\b(?:reverse|tpad|loop)\b/i.test(command)) {
    fail(`${owner}: safe-prefix-slow-forward ffmpegCommand must not reverse, hold, or loop frames`);
  }
  if (postProcess.type === "full-range-deterministic-safe-overlay"
    && (!hasPortablePlaceholder(command, "overlayFrames")
      || /\b(?:reverse|tpad|loop|trim)\b/i.test(command))) {
    fail(`${owner}: deterministic safe-overlay ffmpegCommand must use overlayFrames and preserve the forward full range`);
  }
  if (!isNonEmptyString(command)
    || !hasPortablePlaceholder(command, "rawOutput")
    || !hasPortablePlaceholder(command, "projectAsset")
    || command.split("{rawOutput}").length !== 2
    || command.split("{projectAsset}").length !== 2
    || !command.includes(postProcess.ffmpegFilter || "\u0000")
    || !/(?:^|\s)-(?:vf|filter:v|filter_complex)\s/i.test(command)
    || !/(?:^|\s)-an(?:\s|$)/i.test(command)
    || !/(?:^|\s)-(?:c:v|vcodec)\s+libx264(?:\s|$)/i.test(command)
    || !/(?:^|\s)-movflags\s+\+faststart(?:\s|$)/i.test(command)
    || /[a-z]:[\\/]/i.test(command)) {
    fail(`${owner}: ffmpegCommand must be portable, use both placeholders, the exact filter, H.264, no audio, and faststart`);
  }

  const finalFile = sample.file;
  if (finalFile?.frameCount !== expectedFinalFrames) {
    fail(`${owner}: final frameCount must equal the declared post-process result (${expectedFinalFrames})`);
  }
  for (const field of ["width", "height"]) {
    if (finalFile?.[field] !== rawOutput.stream?.[field]) {
      fail(`${owner}: final ${field} must match the raw output stream`);
    }
  }
  const expectedFinalFps = postProcess.type === "safe-prefix-slow-forward"
    ? postProcess.outputFps
    : rawOutput.stream?.fps;
  if (finalFile?.fps !== expectedFinalFps) {
    fail(`${owner}: final fps must match the declared post-process output fps (${expectedFinalFps})`);
  }
  return rawOutput.stream;
}

function checkEnvironmentDerivative(derivative, metadata, samplesById, sample, owner) {
  const expectsDerivative = sample.sceneRole === "environment-event";
  if (!derivative) {
    if (expectsDerivative) fail(`${owner}: environment-event requires a pinned published-source derivative record`);
    return null;
  }
  if (!expectsDerivative || typeof derivative !== "object" || Array.isArray(derivative)) {
    fail(`${owner}: derivedFromPublishedSample is allowed only for a valid environment-event object`);
    return null;
  }
  if (derivative.type !== "deterministic-single-meteor-overlay") {
    fail(`${owner}: unsupported environment derivative type`);
  }

  const sourceSample = samplesById.get(derivative.sampleId);
  const sourceRecord = metadata.samples?.[derivative.sampleId];
  if (!sourceSample || !sourceRecord || derivative.sampleId === sample.id) {
    fail(`${owner}: environment derivative source sample is missing or recursive`);
    return null;
  }
  if (sourceSample.review?.publication?.status !== "published"
    || sourceSample.taxonId !== sample.taxonId
    || sourceSample.poster !== sample.poster
    || derivative.projectAsset !== sourceSample.src) {
    fail(`${owner}: environment derivative must reuse a published same-taxon source sample and poster`);
  }
  compareStreamRecords(derivative.file, sourceSample.file, `${owner}: derivative source file`);
  checkStreamRecord(derivative.file, `${owner}: derivative source file`);
  checkHashedFile(
    derivative.projectAsset,
    derivative.file?.sha256,
    derivative.file?.bytes,
    `${owner}: derivative source video`,
  );

  if (!isNonEmptyString(derivative.buildScript)
    || !/\.ps1$/i.test(derivative.buildScript)
    || !isSha256(derivative.buildScriptSha256)) {
    fail(`${owner}: deterministic overlay build script record is incomplete`);
  } else {
    checkHashedFile(
      derivative.buildScript,
      derivative.buildScriptSha256,
      undefined,
      `${owner}: deterministic overlay build script`,
    );
  }
  const command = normalizeWhitespace(derivative.command);
  if (!hasPortablePlaceholder(command, "buildScript")
    || !command.includes("-Sample tyrannosaurus")) {
    fail(`${owner}: deterministic overlay command must use {buildScript} and the tyrannosaurus target`);
  }

  const effect = derivative.effect;
  const activeSeconds = effect?.activeSeconds;
  const trajectory = effect?.trajectory;
  const validActiveRange = Array.isArray(activeSeconds) && activeSeconds.length === 2
    && activeSeconds.every(Number.isFinite)
    && activeSeconds[0] >= 0 && activeSeconds[0] < activeSeconds[1]
    && activeSeconds[1] <= sample.file?.durationSeconds;
  const validTrajectory = trajectory && Array.isArray(trajectory.start)
    && Array.isArray(trajectory.end) && trajectory.start.length === 2 && trajectory.end.length === 2
    && [...trajectory.start, ...trajectory.end].every(Number.isFinite)
    && trajectory.start[0] >= 0 && trajectory.end[0] < sample.file?.width
    && trajectory.start[1] >= 0 && trajectory.end[1] < sample.file?.height
    && trajectory.end[0] > trajectory.start[0] && trajectory.end[1] >= trajectory.start[1];
  if (!effect || effect.subject !== "distant-meteor" || effect.count !== 1
    || !validActiveRange || !validTrajectory
    || effect.paleRoundedCore !== true || effect.diffuseTrail !== true
    || effect.fadesBeforeCanopy !== true || effect.intersectsDinosaur !== false
    || effect.intersectsGround !== false || effect.reverseMotion !== false
    || effect.loop !== false || effect.autoplay !== false) {
    fail(`${owner}: deterministic meteor effect boundary is incomplete or unsafe`);
  }
  return { sourceSample, sourceRecord };
}

function parseLegacyManualRange(value) {
  const match = String(value || "").match(/frames?\s+(\d+)\s*-\s*(\d+)/i);
  return match ? [Number(match[1]), Number(match[2])] : null;
}

function checkPublishedQa(record, sample, owner) {
  const qa = record?.qa;
  if (!qa || typeof qa !== "object" || Array.isArray(qa)) {
    fail(`${owner}: published sample requires metadata qa`);
    return;
  }
  const legacyRange = parseLegacyManualRange(qa.manualFramesReviewed);
  const range = Array.isArray(qa.frameIndexRange) ? qa.frameIndexRange : legacyRange;
  const reviewedCount = Number.isInteger(qa.manualFrameCountReviewed)
    ? qa.manualFrameCountReviewed
    : legacyRange && legacyRange[0] === 0
      ? legacyRange[1] + 1
      : null;
  if (reviewedCount !== sample.file?.frameCount) {
    fail(`${owner}: qa.manualFrameCountReviewed must equal file.frameCount`);
  }
  if (!Array.isArray(range) || range.length !== 2 || range[0] !== 0
    || range[1] !== sample.file?.frameCount - 1) {
    fail(`${owner}: qa frameIndexRange must cover first through last frame`);
  }
  const checkpoints = qa.checkpointFrames;
  if (!Array.isArray(checkpoints) || checkpoints.length < 2
    || checkpoints.some((frame) => !Number.isInteger(frame)
      || frame < 0 || frame >= sample.file?.frameCount)
    || new Set(checkpoints).size !== checkpoints.length
    || !checkpoints.includes(0)
    || !checkpoints.includes(sample.file?.frameCount - 1)) {
    fail(`${owner}: qa.checkpointFrames must be unique, in range, and include first and last`);
  }
  const expectedVisualStatus = `pass-independent-${sample.file?.frameCount}-of-${sample.file?.frameCount}`;
  if (qa.visualStatus !== expectedVisualStatus) {
    fail(`${owner}: qa.visualStatus must be ${expectedVisualStatus}`);
  }
  if (qa.evidenceFiles !== undefined) {
    if (!Array.isArray(qa.evidenceFiles) || !qa.evidenceFiles.length) {
      fail(`${owner}: qa.evidenceFiles must be a non-empty array when present`);
    } else {
      for (const [index, evidence] of qa.evidenceFiles.entries()) {
        if (!isNonEmptyString(evidence?.purpose)) {
          fail(`${owner}: qa.evidenceFiles[${index}] requires a purpose`);
        }
        checkHashedFile(
          evidence?.path,
          evidence?.sha256,
          evidence?.bytes,
          `${owner}: qa evidence ${index}`,
        );
      }
    }
  }
}

function checkRunRecord(
  runRecord,
  metadataWorkflow,
  record,
  sample,
  models,
  probedStream,
  postProcess,
  owner,
) {
  if (!runRecord || !metadataWorkflow) return;
  if (![1, 2].includes(runRecord.schemaVersion)) {
    fail(`${owner}: run record schemaVersion must be 1 or 2`);
  }
  if (!isNonEmptyString(metadataWorkflow.promptId)
    || runRecord.promptId !== metadataWorkflow.promptId
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

  if (runRecord.schemaVersion === 2) {
    if (!isNonEmptyString(metadataWorkflow.candidateId)
      || runRecord.candidateId !== metadataWorkflow.candidateId) {
      fail(`${owner}: schema-2 candidateId differs from metadata workflow`);
    }
    if (runRecord.taxonId !== sample.taxonId || runRecord.taxonId !== record.taxonId) {
      fail(`${owner}: schema-2 taxonId differs from catalog or metadata`);
    }
    const runConfig = runRecord.runConfig;
    if (!runConfig || typeof runConfig !== "object" || Array.isArray(runConfig)) {
      fail(`${owner}: schema-2 runConfig is missing`);
    } else {
      for (const field of [
        "seed", "width", "height", "frames", "fps", "steps", "cfg",
        "sampler", "scheduler", "shift", "denoise",
      ]) {
        if (runConfig[field] !== metadataWorkflow[field]) {
          fail(`${owner}: schema-2 runConfig ${field} differs from metadata workflow`);
        }
      }
      if (runConfig.inputName !== record.comfyInput) {
        fail(`${owner}: schema-2 runConfig inputName differs from metadata comfyInput`);
      }
      if (normalizeWhitespace(runConfig.positivePrompt)
          !== normalizeWhitespace(metadataWorkflow.positivePrompt)
        || normalizeWhitespace(runConfig.negativePrompt)
          !== normalizeWhitespace(metadataWorkflow.negativePrompt)) {
        fail(`${owner}: schema-2 runConfig prompts differ from metadata workflow`);
      }
      if (!nearlyEqual(
        runConfig.effectiveDurationSeconds,
        metadataWorkflow.frames / metadataWorkflow.fps,
      )) {
        fail(`${owner}: schema-2 effectiveDurationSeconds differs from frames/fps`);
      }
    }

    const provenance = runRecord.provenance;
    const expectedGenerationRunnerHash = metadataWorkflow.generationRunnerSha256
      || metadataWorkflow.runnerSha256;
    if (!provenance || provenance.templateSha256 !== metadataWorkflow.templateSha256
      || provenance.runnerSha256 !== expectedGenerationRunnerHash
      || provenance.comfyInputSha256 !== record.sourcePosterSha256
      || provenance.sourcePoster !== record.sourcePoster
      || provenance.sourcePosterSha256 !== record.sourcePosterSha256
      || provenance.sourceLicense !== record.sourceLicense) {
      fail(`${owner}: schema-2 provenance differs from workflow or approved source metadata`);
    }
    if (metadataWorkflow.specGenerationSha256
      && provenance?.specSha256 !== metadataWorkflow.specGenerationSha256) {
      fail(`${owner}: schema-2 generation spec SHA-256 differs from metadata`);
    }
  }

  checkConfiguredWorkflow(runRecord.workflow, metadataWorkflow, record, models, `${owner}: run workflow`);
  const historyWorkflow = runRecord.history?.prompt?.[2];
  checkConfiguredWorkflow(historyWorkflow, metadataWorkflow, record, models, `${owner}: history workflow`);
  if (JSON.stringify(runRecord.workflow) !== JSON.stringify(historyWorkflow)) {
    fail(`${owner}: queued workflow and history workflow differ`);
  }
  const output = runRecord.history?.outputs?.["12"]?.images?.[0];
  if (!output || output.type !== "output" || !/\.mp4$/i.test(output.filename || "")) {
    fail(`${owner}: run record lacks the generated MP4 output record`);
  }

  if (postProcess && output) {
    const outputSubfolder = normalizeProjectSlashes(output.subfolder).replace(/^\/+|\/+$/g, "");
    const recordedRawPath = ["output", outputSubfolder, output.filename].filter(Boolean).join("/");
    if (recordedRawPath !== postProcess.rawOutput?.path) {
      fail(`${owner}: postProcess rawOutput.path differs from the run-record output`);
    }
  } else if (probedStream && !probedStream.unavailable && !probedStream.error) {
    if (!isNonEmptyString(probedStream.embeddedPrompt)) {
      fail(`${owner}: MP4 lacks the embedded ComfyUI prompt graph`);
    } else {
      try {
        const embeddedWorkflow = JSON.parse(probedStream.embeddedPrompt);
        checkConfiguredWorkflow(
          embeddedWorkflow,
          metadataWorkflow,
          record,
          models,
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

function checkEventCandidateBatch(batch, samplesById) {
  if (!batch || batch.schemaVersion !== 1
    || batch.status !== "review-complete-with-safe-replacements") {
    fail("event candidate batch must be a completed schema-1 review record");
    return;
  }
  const candidates = Array.isArray(batch.candidates) ? batch.candidates : [];
  const summary = batch.reviewSummary;
  if (!isSha256(batch.generationSpecSha256) || !isNonEmptyString(batch.generationSpecNote)) {
    fail("event candidate batch must preserve the exact pre-review generation manifest hash and its relationship to the reviewed manifest");
  }
  if (candidates.length !== 2 || summary?.nativeCandidatesAccepted !== 0
    || summary?.nativeCandidatesRejected !== candidates.length
    || summary?.safeReplacementsPublished !== candidates.length) {
    fail("event candidate batch counts must record two rejected native candidates and two safe replacements");
  }
  for (const candidate of candidates) {
    const owner = `event candidate ${candidate?.id || "(blank)"}`;
    if (!isSafeCatalogId(candidate?.id) || !isSafeCatalogId(candidate?.taxonId)
      || candidate?.sceneRole !== "environment-event"
      || !isNonEmptyString(candidate?.positivePrompt)
      || !isNonEmptyString(candidate?.negativePrompt)) {
      fail(`${owner}: identity, role, or prompt record is incomplete`);
    }
    checkHashedFile(
      candidate?.sourcePoster,
      candidate?.sourcePosterSha256,
      undefined,
      `${owner}: source poster`,
    );
    const runRecordFile = checkHashedFile(
      candidate?.record,
      candidate?.recordSha256,
      undefined,
      `${owner}: rejected native run record`,
    );
    if (runRecordFile) {
      try {
        const runRecord = JSON.parse(fs.readFileSync(runRecordFile.absolutePath, "utf8"));
        const expectedConfig = { ...batch.settings, ...(candidate.settings || {}) };
        if (runRecord.schemaVersion !== 2
          || runRecord.candidateId !== candidate.id
          || runRecord.taxonId !== candidate.taxonId
          || runRecord.status?.status_str !== "success"
          || runRecord.status?.completed !== true
          || !isNonEmptyString(runRecord.promptId)) {
          fail(`${owner}: run record identity or successful completion state differs from the reviewed candidate`);
        }
        for (const field of [
          "seed", "width", "height", "frames", "fps", "steps", "cfg",
          "sampler", "scheduler", "shift", "denoise",
        ]) {
          const expectedValue = field === "seed" ? candidate.seed : expectedConfig[field];
          if (runRecord.runConfig?.[field] !== expectedValue) {
            fail(`${owner}: run record ${field} differs from the generation manifest`);
          }
        }
        if (runRecord.runConfig?.inputName !== candidate.inputName
          || normalizeWhitespace(runRecord.runConfig?.positivePrompt)
            !== normalizeWhitespace(candidate.positivePrompt)
          || normalizeWhitespace(runRecord.runConfig?.negativePrompt)
            !== normalizeWhitespace(`${batch.commonNegativePrompt}, ${candidate.negativePrompt}`)) {
          fail(`${owner}: run record input or prompts differ from the generation manifest`);
        }
        if (runRecord.provenance?.specSha256 !== batch.generationSpecSha256
          || runRecord.provenance?.comfyInputSha256 !== candidate.sourcePosterSha256
          || runRecord.provenance?.sourcePoster !== candidate.sourcePoster
          || runRecord.provenance?.sourcePosterSha256 !== candidate.sourcePosterSha256
          || runRecord.provenance?.sourceLicense !== candidate.sourceLicense) {
          fail(`${owner}: run record provenance differs from the pinned generation snapshot or source`);
        }
      } catch (error) {
        fail(`${owner}: rejected native run record is invalid JSON: ${error.message}`);
      }
    }
    if (candidate?.reviewStatus !== "rejected"
      || candidate?.review?.allFrames !== "rejected"
      || candidate?.review?.usableSafePrefix !== "none"
      || !isNonEmptyString(candidate?.review?.firstClearDefect)
      || !isNonEmptyString(candidate?.review?.reason)) {
      fail(`${owner}: rejection review must prohibit every native output and safe prefix`);
    }
    const replacement = candidate?.safeReplacement;
    if (!isSafeCatalogId(replacement?.id)
      || !["M0", "M2"].includes(replacement?.tier)
      || !isNonEmptyString(replacement?.method)
      || !String(replacement?.reviewStatus || "").startsWith("published-after-independent-")) {
      fail(`${owner}: safe replacement identity or independent review is incomplete`);
      continue;
    }
    checkHashedFile(
      replacement.projectAsset,
      replacement.sha256,
      undefined,
      `${owner}: safe replacement`,
    );
    if (replacement.tier === "M2") {
      const publishedSample = samplesById.get(replacement.id);
      if (!publishedSample || publishedSample.src !== replacement.projectAsset
        || publishedSample.file?.sha256 !== replacement.sha256
        || publishedSample.review?.publication?.status !== "published") {
        fail(`${owner}: M2 safe replacement is not the matching published catalog sample`);
      }
    } else if (!/^assets\/motion\/[a-z0-9][a-z0-9.-]*-m0-v[0-9]+\.mp4$/i.test(
      replacement.projectAsset || "",
    )) {
      fail(`${owner}: M0 safe replacement path is not species-prefixed and versioned`);
    }
  }
}

if (!fs.existsSync(CATALOG_PATH)) throw new Error(`missing ${CATALOG_RELATIVE_PATH}`);
if (!fs.existsSync(METADATA_PATH)) throw new Error(`missing ${METADATA_RELATIVE_PATH}`);
if (!fs.existsSync(EVENT_CANDIDATES_PATH)) throw new Error(`missing ${EVENT_CANDIDATES_RELATIVE_PATH}`);

const catalogSource = fs.readFileSync(CATALOG_PATH, "utf8");
const metadataSource = fs.readFileSync(METADATA_PATH, "utf8");
const eventCandidatesSource = fs.readFileSync(EVENT_CANDIDATES_PATH, "utf8");
const sandbox = { window: {} };
new vm.Script(catalogSource, { filename: CATALOG_PATH }).runInNewContext(sandbox);
const catalog = sandbox.window.motionM2I2VSampleCatalog;
const metadata = JSON.parse(metadataSource);
const eventCandidates = JSON.parse(eventCandidatesSource);

if (!catalog || typeof catalog !== "object") {
  throw new Error("motionM2I2VSampleCatalog was not exported");
}
if (/\.codex[\\/]generated_images/i.test(catalogSource)
  || /\.codex[\\/]generated_images/i.test(metadataSource)
  || /\.codex[\\/]generated_images/i.test(eventCandidatesSource)) {
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
if (catalog.policy?.loop !== "prohibited") {
  fail("catalog policy must prohibit looping");
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
const samplesById = new Map(samples.map((sample) => [sample?.id, sample]));
checkEventCandidateBatch(eventCandidates, samplesById);
const catalogIds = samples.map((sample) => sample?.id);
const metadataIds = Object.keys(metadata.samples || {});
if (!samples.length) fail("catalog must contain at least one I2V sample");
if (catalogIds.some((id) => !isSafeCatalogId(id))) {
  fail("catalog contains a missing or unsafe sample id");
}
if (new Set(catalogIds).size !== catalogIds.length) {
  fail("catalog contains duplicate sample ids");
}
if (!sameStringSet(catalogIds, metadataIds)) {
  fail(`catalog-metadata one-to-one mismatch: catalog=${catalogIds.join(",")} metadata=${metadataIds.join(",")}`);
}

checkModelRecords(metadata.models);
if (!isNonEmptyString(metadata.software?.comfyUiCommit)
  || metadata.software?.comfyUiVersion !== "0.25.0"
  || !metadata.software?.launchFlags?.includes("--disable-all-custom-nodes")) {
  fail("metadata: ComfyUI version, commit, or core-only launch flag is incomplete");
}

let publishedVideos = 0;
const streams = {};
const publicationStatuses = [];
for (const sample of samples) {
  const owner = sample?.id || "sample:(blank)";
  const record = metadata.samples?.[sample.id];
  if (!record) {
    fail(`${owner}: missing metadata record`);
    continue;
  }

  const allowedSceneRoles = new Set(["solo", "foraging-behavior", "predator-prey-interaction", "environment-event"]);
  if (sample.tier !== "M2" || sample.motionClass !== "generative-i2v"
    || !allowedSceneRoles.has(sample.sceneRole) || !isNonEmptyString(sample.sceneRoleLabel)) {
    fail(`${owner}: must remain an M2 generative-I2V candidate with an approved scene role and label`);
  }
  if (sample.representativeEligible !== false || sample.galleryEligible !== false
    || sample.anatomyEligible !== false || record.review?.representativeEligible !== false
    || record.review?.galleryEligible !== false || record.review?.anatomyEligible !== false) {
    fail(`${owner}: representative, gallery, and anatomy eligibility must all be false`);
  }
  if (record.taxonId !== sample.taxonId || !isSafeCatalogId(sample.taxonId)) {
    fail(`${owner}: catalog and metadata taxonId must match and be safe`);
  }
  const expectedVideoPath = `assets/motion/m2/${sample.id}.mp4`;
  if (!/-m2-v[0-9]+$/i.test(sample.id)
    || sample.src !== expectedVideoPath || record.projectAsset !== expectedVideoPath) {
    fail(`${owner}: catalog and metadata must use assets/motion/m2/{id}.mp4 with a versioned M2 id`);
  }
  const expectedPosterPrefix = `assets/dinosaurs/${sample.taxonId}-`;
  if (!sample.poster?.startsWith(expectedPosterPrefix)
    || !/-v[0-9]+(?:-source-candidate)?\.png$/i.test(sample.poster)
    || !/^assets\/dinosaurs\/[a-z0-9][a-z0-9.-]*\.png$/i.test(sample.poster)
    || sample.poster !== record.sourcePoster) {
    fail(`${owner}: source poster must be the same species-prefixed, versioned project PNG in both records`);
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

  compareStreamRecords(sample.file, record.file, owner);
  checkStreamRecord(sample.file, `${owner}: catalog file record`);
  checkStreamRecord(record.file, `${owner}: metadata file record`);
  const videoFile = checkHashedFile(
    sample.src,
    sample.file?.sha256,
    sample.file?.bytes,
    `${owner}: video`,
  );
  let probedStream = null;
  if (videoFile) {
    probedStream = probeMedia(videoFile.absolutePath);
    checkProbe(probedStream, sample.file, `${owner}: video`);
    checkMp4FastStart(videoFile.absolutePath, `${owner}: video`, {
      required: Boolean(record.workflow),
    });
    if (!probedStream.unavailable && !probedStream.error) {
      streams[sample.id] = {
        width: probedStream.width,
        height: probedStream.height,
        fps: probedStream.fps,
        frameCount: probedStream.frameCount,
        codec: probedStream.codec,
        pixelFormat: probedStream.pixelFormat,
        audioStreams: probedStream.audioStreamCount,
      };
    }
  }

  const derivativeContext = checkEnvironmentDerivative(
    record.derivedFromPublishedSample,
    metadata,
    samplesById,
    sample,
    owner,
  );
  const lineageSample = derivativeContext?.sourceSample || sample;
  const lineageRecord = derivativeContext?.sourceRecord || record;
  const generationStream = checkPostProcess(
    lineageRecord.postProcess,
    lineageSample,
    `${owner}: generation lineage`,
  ) || lineageSample.file;
  const metadataWorkflow = resolveSampleWorkflow(metadata, lineageRecord, lineageSample, owner);
  const { runRecord } = loadWorkflowArtifacts(metadataWorkflow, owner);
  checkGenerationStreamConfig(metadataWorkflow, generationStream, owner);
  if (sample.provenance?.metadataRecord
      !== `${METADATA_RELATIVE_PATH}#/samples/${sample.id}`
    || sample.provenance?.runRecord !== metadataWorkflow?.runRecord) {
    fail(`${owner}: metadata or run-record provenance pointer is invalid`);
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
  publicationStatuses.push(publicationStatus);
  if (sample.reviewStatus !== publicationStatus
    || record.review?.publication?.status !== publicationStatus) {
    fail(`${owner}: catalog and metadata publication status must agree`);
  }
  const published = publicationStatus === "published" || publicationStatus === "public"
    || sample.public === true || record.public === true
    || sample.visibility === "public" || record.visibility === "public";
  if (published) {
    publishedVideos += 1;
    const subject = sample.subjectMotion;
    if (subject?.status !== "supported" || subject.evidenceGate !== "review.motionPlausibility"
      || !Array.isArray(subject.taxonIds) || !subject.taxonIds.includes(sample.taxonId)
      || !Array.isArray(subject.movingParts) || !subject.movingParts.length) {
      fail(`${owner}: published I2V sample lacks supported dinosaur subject motion`);
    }
    if (subject?.inheritedFrom) {
      const inherited = samplesById.get(subject.inheritedFrom);
      if (!inherited || inherited.review?.publication?.status !== "published"
        || inherited.subjectMotion?.status !== "supported"
        || !subject.taxonIds.some((id) => inherited.subjectMotion.taxonIds.includes(id))) {
        fail(`${owner}: inherited subject motion lacks a compatible published source sample`);
      }
    }
    if (publicationStatus !== "published" && publicationStatus !== "public") {
      fail(`${owner}: public visibility requires a public or published publication gate`);
    }
    for (const gate of REQUIRED_PUBLIC_GATES) {
      if (sample.review?.[gate]?.status !== "supported"
        || record.review?.[gate]?.status !== "supported") {
        fail(`${owner}: published without supported ${gate} gate`);
      }
    }
    checkPublishedQa(record, sample, owner);
  }

  checkRunRecord(
    runRecord,
    metadataWorkflow,
    lineageRecord,
    lineageSample,
    metadata.models,
    probedStream,
    lineageRecord.postProcess,
    owner,
  );
}

const uniquePublicationStatuses = new Set(publicationStatuses);
const expectedMetadataStatus = uniquePublicationStatuses.size === 1
  ? publicationStatuses[0]
  : "mixed";
if (metadata.status !== expectedMetadataStatus) {
  fail(`metadata status must aggregate sample publication states as ${expectedMetadataStatus}`);
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
  streams,
  warnings,
  errors,
};

console.log(JSON.stringify(report, null, 2));
if (errors.length) {
  throw new Error(`M2 I2V verification failed with ${errors.length} error(s):\n${errors.join("\n")}`);
}
