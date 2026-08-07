import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptPath = fileURLToPath(import.meta.url);
const repoRoot = path.resolve(path.dirname(scriptPath), "..", "..", "..");
const specPath = path.resolve(
  repoRoot,
  process.argv[2] || "tools/comfyui/motion-subject-required-candidates-20260807.json",
);
const reviewRoot = path.resolve(
  repoRoot,
  process.argv[3] || "tools/comfyui/review-evidence/motion-subject-required-20260807",
);
const manifestPath = path.resolve(
  repoRoot,
  process.argv[4] || "tools/comfyui/outputs/motion-subject-required-review-inputs-20260807.json",
);
const ffmpeg = process.env.FFMPEG_PATH || "ffmpeg";
const ffprobe = process.env.FFPROBE_PATH || "ffprobe";

function sha256(filePath) {
  const hash = createHash("sha256");
  hash.update(readFileSync(filePath));
  return hash.digest("hex");
}

function readJson(filePath) {
  return JSON.parse(readFileSync(filePath, "utf8"));
}

function repoRelative(filePath) {
  return path.relative(repoRoot, filePath).replaceAll("\\", "/");
}

function run(executable, args) {
  execFileSync(executable, args, { stdio: "inherit", windowsHide: true });
}

function probeVideo(filePath) {
  const output = execFileSync(
    ffprobe,
    [
      "-v",
      "error",
      "-count_frames",
      "-select_streams",
      "v:0",
      "-show_entries",
      "stream=width,height,codec_name,pix_fmt,r_frame_rate,avg_frame_rate,nb_frames,nb_read_frames,duration:format=duration",
      "-of",
      "json",
      filePath,
    ],
    { encoding: "utf8", windowsHide: true },
  );
  return JSON.parse(output);
}

function findRawOutput(record) {
  const outputNodes = Object.values(record.history?.outputs || {});
  const files = outputNodes.flatMap((node) => node.images || []);
  if (files.length !== 1) {
    throw new Error(`${record.candidateId}: expected one raw output, found ${files.length}`);
  }
  return files[0];
}

function cropFilter(region) {
  return `crop=${region.width}:${region.height}:${region.x}:${region.y},tile=9x9:padding=2:margin=2:color=black`;
}

const spec = readJson(specPath);
const comfyRoot = path.resolve(spec.comfyUiRoot);
const checkpointFrames = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80];
const records = [];

mkdirSync(reviewRoot, { recursive: true });

for (const candidate of spec.candidates) {
  const recordPath = path.resolve(repoRoot, candidate.record);
  if (!existsSync(recordPath)) throw new Error(`${candidate.id}: missing run record ${recordPath}`);
  const record = readJson(recordPath);
  if (record.candidateId !== candidate.id || record.status?.status_str !== "success") {
    throw new Error(`${candidate.id}: run record is not a matching successful generation`);
  }
  const output = findRawOutput(record);
  const rawPath = path.join(comfyRoot, "output", output.subfolder || "", output.filename);
  if (!existsSync(rawPath)) throw new Error(`${candidate.id}: missing raw video ${rawPath}`);

  const candidateRoot = path.join(reviewRoot, candidate.id);
  const checkpointsRoot = path.join(candidateRoot, "checkpoints");
  rmSync(candidateRoot, { recursive: true, force: true });
  mkdirSync(checkpointsRoot, { recursive: true });

  const allFramesSheet = path.join(candidateRoot, "all-81-frames-9x9.png");
  run(ffmpeg, [
    "-hide_banner",
    "-loglevel",
    "error",
    "-y",
    "-i",
    rawPath,
    "-vf",
    "tile=9x9:padding=2:margin=2:color=black",
    "-frames:v",
    "1",
    allFramesSheet,
  ]);

  const checkpointExpression = checkpointFrames.map((frame) => `eq(n\\,${frame})`).join("+");
  run(ffmpeg, [
    "-hide_banner",
    "-loglevel",
    "error",
    "-y",
    "-i",
    rawPath,
    "-vf",
    `select='${checkpointExpression}'`,
    "-vsync",
    "0",
    path.join(checkpointsRoot, "checkpoint-%02d.png"),
  ]);

  const regionSheets = {};
  for (const [name, region] of Object.entries(candidate.reviewRegions || {})) {
    const regionPath = path.join(candidateRoot, `${name}-all-81-frames-9x9.png`);
    run(ffmpeg, [
      "-hide_banner",
      "-loglevel",
      "error",
      "-y",
      "-i",
      rawPath,
      "-vf",
      cropFilter(region),
      "-frames:v",
      "1",
      regionPath,
    ]);
    regionSheets[name] = repoRelative(regionPath);
  }

  const rawStat = statSync(rawPath);
  const stream = probeVideo(rawPath);
  records.push({
    candidateId: candidate.id,
    taxonId: candidate.taxonId,
    runRecord: repoRelative(recordPath),
    runRecordSha256: sha256(recordPath),
    rawOutput: path.relative(path.join(comfyRoot, "output"), rawPath).replaceAll("\\", "/"),
    rawSha256: sha256(rawPath),
    rawBytes: rawStat.size,
    stream,
    requiredVisibleMotion: candidate.requiredVisibleMotion,
    reviewGate: spec.reviewGate,
    evidence: {
      allFramesSheet: repoRelative(allFramesSheet),
      checkpointFrames,
      checkpointsDirectory: repoRelative(checkpointsRoot),
      regionSheets,
      policy: "Contact sheets are navigation aids. Decisions require every full-resolution decoded frame plus temporal playback review.",
    },
  });
}

const manifest = {
  schemaVersion: 1,
  generatedAt: new Date().toISOString(),
  status: "review-pending",
  spec: repoRelative(specPath),
  specSha256: sha256(specPath),
  ffmpeg,
  ffprobe,
  records,
};

mkdirSync(path.dirname(manifestPath), { recursive: true });
writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ manifest: repoRelative(manifestPath), candidates: records.length }, null, 2));
