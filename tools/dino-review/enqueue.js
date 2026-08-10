const fs = require("fs");
const path = require("path");
const {
  PROMOTABLE_KINDS,
  assertPng,
  defaultConfig,
  isVersionedSpeciesPng,
  requireSafeCandidateId,
} = require("./backend");

function parseArguments(argv) {
  const values = {};
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith("--")) throw new Error(`unexpected argument: ${token}`);
    const key = token.slice(2);
    if (key === "representative") {
      values.representative = true;
      continue;
    }
    const value = argv[index + 1];
    if (value === undefined || value.startsWith("--")) throw new Error(`missing value for --${key}`);
    values[key] = value;
    index += 1;
  }
  return values;
}

function readPrompt(options) {
  if (options["prompt-file"]) return fs.readFileSync(path.resolve(options["prompt-file"]), "utf8").trim();
  return String(options.prompt || "").trim();
}

function assertSourcePng(sourceFile) {
  const stat = fs.lstatSync(sourceFile);
  if (!stat.isFile() || stat.isSymbolicLink() || path.extname(sourceFile).toLowerCase() !== ".png") {
    throw new Error("--image must be a regular non-symlink PNG");
  }
  try {
    assertPng(sourceFile);
  } catch (error) {
    throw new Error(`--image has invalid PNG structure: ${error.message}`);
  }
}

function enqueueCandidate(options, overrides = {}) {
  const config = defaultConfig(overrides);
  const candidateId = requireSafeCandidateId(options.candidateId || options["candidate-id"]);
  const sourceFile = path.resolve(String(options.image || ""));
  assertSourcePng(sourceFile);
  const filename = path.basename(sourceFile);
  const speciesId = String(options.speciesId || options["species-id"] || "");
  const kind = String(options.kind || "review hold");
  const targetFilename = String(options.targetFilename || options["target-filename"] || filename);
  if (!PROMOTABLE_KINDS.has(kind)) throw new Error(`unsupported --kind: ${kind}`);
  if (!isVersionedSpeciesPng(filename, speciesId)) {
    throw new Error("PNG filename must start with speciesId and end with -vN.png");
  }
  if (!isVersionedSpeciesPng(targetFilename, speciesId)) {
    throw new Error("target filename must start with speciesId and end with -vN.png");
  }
  if (targetFilename !== path.basename(targetFilename)) throw new Error("target filename must not contain a path");
  if (!fs.existsSync(config.pendingDir)) fs.mkdirSync(config.pendingDir, { recursive: true });
  const pendingStat = fs.lstatSync(config.pendingDir);
  if (!pendingStat.isDirectory() || pendingStat.isSymbolicLink()) throw new Error("unsafe pending directory");
  const candidateDir = path.resolve(config.pendingDir, candidateId);
  if (path.dirname(candidateDir) !== path.resolve(config.pendingDir)) throw new Error("unsafe candidate path");
  fs.mkdirSync(candidateDir);
  const destination = path.join(candidateDir, filename);
  const manifestFile = path.join(candidateDir, "candidate.json");
  const manifest = {
    schemaVersion: 1,
    candidateId,
    filename,
    speciesId,
    kind,
    targetFilename,
    provenance: {
      source: String(options.source || "").trim(),
      license: String(options.license || "").trim(),
      prompt: readPrompt(options),
      seed: String(options.seed || "").trim(),
      workflow: String(options.workflow || "").trim(),
    },
    anatomyReview: {
      status: String(options.anatomyStatus || options["anatomy-status"] || "pending"),
      representative: Boolean(options.representative),
      reviewer: String(options.reviewer || "").trim(),
      reviewedAt: String(options.reviewedAt || options["reviewed-at"] || "").trim(),
      notes: String(options.anatomyNotes || options["anatomy-notes"] || "").trim(),
    },
  };
  try {
    fs.copyFileSync(sourceFile, destination, fs.constants.COPYFILE_EXCL);
    fs.writeFileSync(manifestFile, `${JSON.stringify(manifest, null, 2)}\n`, { encoding: "utf8", flag: "wx" });
  } catch (error) {
    if (fs.existsSync(manifestFile)) fs.unlinkSync(manifestFile);
    if (fs.existsSync(destination)) fs.unlinkSync(destination);
    if (fs.existsSync(candidateDir)) fs.rmdirSync(candidateDir);
    throw error;
  }
  return { candidateId, candidateDir, image: destination, manifestFile, manifest };
}

function printHelp() {
  console.log(`Usage:
  node tools/dino-review/enqueue.js \\
    --candidate-id <id> --image <species-prefixed-vN.png> --species-id <id> \\
    --kind <kind> [--target-filename <name>] \\
    [--source <source>] [--license <license>] [--prompt <prompt>|--prompt-file <file>] \\
    [--seed <seed>] [--workflow <workflow>] \\
    [--anatomy-status <status>] [--representative] [--reviewer <name>] \\
    [--reviewed-at <ISO>] [--anatomy-notes <notes>]

Incomplete provenance/anatomy fields are allowed into pending review, but promotion stays blocked.`);
}

if (require.main === module) {
  try {
    if (process.argv.includes("--help") || process.argv.includes("-h")) {
      printHelp();
      process.exitCode = 0;
    } else {
      const options = parseArguments(process.argv.slice(2));
      const result = enqueueCandidate(options);
      console.log(JSON.stringify({
        ok: true,
        candidateId: result.candidateId,
        candidateDir: result.candidateDir,
        manifestFile: result.manifestFile,
      }, null, 2));
    }
  } catch (error) {
    console.error(error?.message || error);
    process.exitCode = 1;
  }
}

module.exports = { enqueueCandidate, parseArguments };
