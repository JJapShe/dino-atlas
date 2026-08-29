import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..", "..");
const REAL_ROOT = fs.realpathSync.native(ROOT);
const AUDIT_SCRIPT = path.join(ROOT, "tools", "comfyui", "scripts", "audit_gallery_composition_similarity.cjs");
const SLUG = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const SPECIES_ID = /^[a-z0-9]+(?:-[a-z0-9]+)+$/;
const SHA256 = /^[a-f0-9]{64}$/;
const SOURCE_CALL_ID = /^exec-[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/;
const PNG_SIGNATURE = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);

function loadSharp() {
  const attempts = [];
  const candidates = ["sharp"];
  if (process.env.DINO_ATLAS_NODE_MODULES) {
    candidates.push(path.join(process.env.DINO_ATLAS_NODE_MODULES, "sharp"));
  }
  candidates.push(path.join(path.dirname(process.execPath), "node_modules", "sharp"));

  const codexRuntimeRoot = process.env.LOCALAPPDATA
    ? path.join(process.env.LOCALAPPDATA, "OpenAI", "Codex", "runtimes", "cua_node")
    : null;
  if (codexRuntimeRoot && fs.existsSync(codexRuntimeRoot)) {
    const runtimeCandidates = fs.readdirSync(codexRuntimeRoot, { withFileTypes: true })
      .filter((entry) => entry.isDirectory())
      .map((entry) => path.join(codexRuntimeRoot, entry.name, "bin", "node_modules", "sharp"))
      .filter((candidate) => fs.existsSync(candidate))
      .sort((left, right) => fs.statSync(right).mtimeMs - fs.statSync(left).mtimeMs);
    candidates.push(...runtimeCandidates);
  }

  for (const candidate of [...new Set(candidates)]) {
    try {
      return require(candidate);
    } catch (error) {
      attempts.push(`${candidate}: ${error.code || error.message}`);
    }
  }
  throw new Error(
    "Unable to load sharp. Install it for the active Node runtime or set " +
    "DINO_ATLAS_NODE_MODULES to a node_modules directory containing sharp.\n" + attempts.join("\n"),
  );
}

const sharp = loadSharp();
const readJson = (file) => JSON.parse(fs.readFileSync(file, "utf8"));
const hash = (buffer) => crypto.createHash("sha256").update(buffer).digest("hex");
const hashFile = (file) => hash(fs.readFileSync(file));
const escapeRegex = (value) => value.replace(/[.*+?^$()|[\]\\]/g, "\\$&");

function isInside(root, target) {
  const relative = path.relative(root, target);
  return relative === "" || (!relative.startsWith(`..${path.sep}`) && relative !== ".." && !path.isAbsolute(relative));
}

function resolveRepoPath(rawPath, label, {
  extension = null,
  canonical = false,
  kind = "file",
  mustExist = true,
} = {}) {
  assert.equal(typeof rawPath, "string", `${label} must be a repository-relative path`);
  assert.ok(rawPath.length > 0 && !rawPath.includes("\0"), `${label} must be a non-empty repository-relative path`);
  assert.equal(path.isAbsolute(rawPath), false, `${label} must be repository-relative`);
  if (canonical) {
    assert.equal(rawPath.includes("\\"), false, `${label} must use forward slashes`);
    assert.equal(path.posix.normalize(rawPath), rawPath, `${label} must be a canonical repository path`);
    assert.ok(!rawPath.startsWith("./"), `${label} must not start with ./`);
  }
  const resolved = path.resolve(ROOT, rawPath);
  assert.ok(isInside(ROOT, resolved), `${label} must stay inside the repository`);
  if (extension) assert.equal(path.extname(resolved).toLowerCase(), extension, `${label} must use ${extension}`);
  if (mustExist) assert.ok(fs.existsSync(resolved), `Missing ${label}: ${rawPath}`);
  if (fs.existsSync(resolved)) {
    const real = fs.realpathSync.native(resolved);
    assert.ok(isInside(REAL_ROOT, real), `${label} resolves outside the repository`);
    const stat = fs.statSync(real);
    assert.equal(kind === "directory" ? stat.isDirectory() : stat.isFile(), true, `${label} has the wrong file type`);
    return real;
  }
  let ancestor = path.dirname(resolved);
  while (!fs.existsSync(ancestor)) ancestor = path.dirname(ancestor);
  assert.ok(isInside(REAL_ROOT, fs.realpathSync.native(ancestor)), `${label} resolves through a path outside the repository`);
  return resolved;
}

function canonicalRelative(file) {
  return path.relative(ROOT, file).split(path.sep).join("/");
}

function nonEmptyString(value, label) {
  assert.equal(typeof value, "string", `${label} must be a string`);
  assert.ok(value.trim(), `${label} must not be empty`);
  return value;
}

function runAudit(arguments_) {
  const stdout = execFileSync(process.execPath, [AUDIT_SCRIPT, ...arguments_], {
    cwd: ROOT,
    encoding: "utf8",
    env: process.env,
    maxBuffer: 64 * 1024 * 1024,
    windowsHide: true,
  });
  return JSON.parse(stdout);
}

async function decodePng(buffer, label) {
  assert.ok(buffer.length >= 24, `${label} is too short to be a PNG`);
  assert.deepEqual(buffer.subarray(0, 8), PNG_SIGNATURE, `${label} has an invalid PNG signature`);
  const metadata = await sharp(buffer, { failOn: "error" }).metadata();
  assert.equal(metadata.format, "png", `${label} is not a decoded PNG`);
  assert.equal(metadata.pages ?? 1, 1, `${label} must contain exactly one image`);
  assert.ok(Number.isInteger(metadata.width) && metadata.width > 0, `${label} has no decoded width`);
  assert.ok(Number.isInteger(metadata.height) && metadata.height > 0, `${label} has no decoded height`);
  const decoded = await sharp(buffer, { failOn: "error" }).raw().toBuffer({ resolveWithObject: true });
  assert.ok(decoded.data.length > 0, `${label} produced no decoded pixels`);
  assert.equal(decoded.info.width, metadata.width, `${label} decoded width changed`);
  assert.equal(decoded.info.height, metadata.height, `${label} decoded height changed`);
  return { width: metadata.width, height: metadata.height };
}

function displayNameForSpecies(speciesId) {
  const words = speciesId.split("-");
  return words[0][0].toUpperCase() + words[0].slice(1) + " " + words.slice(1).join(" ");
}

function promptBlockForSpecies(markdown, speciesId) {
  const displayName = displayNameForSpecies(speciesId);
  const headingPattern = new RegExp(`^## ${escapeRegex(displayName)}\\r?$`, "gm");
  const headings = [...markdown.matchAll(headingPattern)];
  assert.equal(headings.length, 1, `Prompt heading must be exact and unique for ${speciesId}`);
  const blockPattern = new RegExp(
    "^## " + escapeRegex(displayName) + "\\r?\\n\\r?\\n```text\\r?\\n([\\s\\S]*?)\\r?\\n```(?:\\r?\\n|$)",
    "gm",
  );
  const blocks = [...markdown.matchAll(blockPattern)];
  assert.equal(blocks.length, 1, `Prompt fenced block must be exact and unique for ${speciesId}`);
  return blocks[0][1].trim();
}

function collectPngFiles(root) {
  if (!fs.existsSync(root)) return [];
  const rootStat = fs.lstatSync(root);
  if (rootStat.isSymbolicLink()) throw new Error(`Symlink scan root is not allowed: ${root}`);
  if (!rootStat.isDirectory()) throw new Error(`PNG scan root must be a directory: ${root}`);
  const realRoot = fs.realpathSync.native(root);
  if (!isInside(REAL_ROOT, realRoot)) throw new Error(`PNG scan root resolves outside the repository: ${root}`);
  const files = [];
  const visit = (directory) => {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const file = path.join(directory, entry.name);
      if (entry.isSymbolicLink()) throw new Error(`Symlink is not allowed in rejected-pixel scan: ${file}`);
      if (entry.isDirectory()) visit(file);
      else if (entry.isFile() && path.extname(entry.name).toLowerCase() === ".png") files.push(file);
    }
  };
  visit(realRoot);
  return files;
}

const batchArgument = process.argv.find((argument) => argument.startsWith("--batch="));
const batchArg = batchArgument
  ? batchArgument.slice("--batch=".length)
  : "tools/comfyui/gallery-composition-diversity-batch-20260810.json";
assert.ok(batchArg, "--batch requires a repository-relative JSON path");
const batchPath = resolveRepoPath(batchArg, "--batch", { extension: ".json" });
const batch = readJson(batchPath);
assert.ok([1, 2].includes(batch.schemaVersion), "Unsupported batch schemaVersion");
const strictProvenance = batch.schemaVersion >= 2;
const warnings = [];
const warnLegacy = (code, message, context = null) => warnings.push({ code, message, context });

assert.match(batch.batchId, SLUG, "batchId must be a lowercase slug");
assert.equal(batch.status, "review-hold");
nonEmptyString(batch.sourceAttribution, "sourceAttribution");
nonEmptyString(batch.licenseRecord, "licenseRecord");
assert.equal(batch.policy.automaticPromotion, false);
assert.equal(batch.policy.representativePromotion, false);
assert.equal(batch.policy.automaticDeletionFromPending, false);
assert.ok(Number.isFinite(batch.policy.candidateMaxSimilarityGate));
assert.ok(batch.policy.candidateMaxSimilarityGate >= 0 && batch.policy.candidateMaxSimilarityGate <= 1);
const policyCandidateKinds = Array.isArray(batch.policy.candidateKinds)
  ? batch.policy.candidateKinds
  : [batch.policy.candidateKind];
assert.ok(policyCandidateKinds.length >= 1, "policy must allow at least one candidate kind");
for (const candidateKind of policyCandidateKinds) nonEmptyString(candidateKind, "policy candidate kind");
assert.equal(new Set(policyCandidateKinds).size, policyCandidateKinds.length, "policy candidate kinds must be unique");
if (policyCandidateKinds.length > 1) {
  assert.equal(strictProvenance, true, "Mixed candidate kinds require schemaVersion 2");
  assert.ok(Array.isArray(batch.policy.candidateKinds), "Mixed candidate kinds require policy.candidateKinds");
}
assert.ok(Array.isArray(batch.records) && batch.records.length >= 1);
const rejectedAttempts = Array.isArray(batch.rejectedAttempts) ? batch.rejectedAttempts : [];
assert.equal(batch.records.length, batch.policy.retainedCandidateCount, "Retained candidate count mismatch");
assert.equal(
  batch.records.length + rejectedAttempts.length,
  batch.policy.attemptedImageCount,
  "Attempted image count mismatch",
);
assert.equal(
  batch.records.length + rejectedAttempts.filter((attempt) => attempt.candidateId).length,
  batch.policy.enqueuedCandidateCount,
  "Enqueued candidate count mismatch",
);
assert.equal(batch.policy.batchSize, batch.policy.enqueuedCandidateCount, "Batch size must mean enqueued candidate count");

const trackedRecord = fs.readFileSync(batchPath, "utf8");
const promptRecordPath = batchPath.replace(/\.json$/i, ".md");
assert.notEqual(promptRecordPath, batchPath, "Batch record must use a .json extension");
const promptRecordPathSafe = resolveRepoPath(canonicalRelative(promptRecordPath), "batch prompt record", {
  extension: ".md",
  canonical: true,
});
const promptRecord = fs.readFileSync(promptRecordPathSafe, "utf8");
assert.doesNotMatch(trackedRecord, /\.codex[\\/]generated_images/i);
assert.doesNotMatch(promptRecord, /\.codex[\\/]generated_images/i);

const storedAuditJsonPath = resolveRepoPath(batch.audit.json, "batch.audit.json", {
  extension: ".json",
  canonical: true,
});
resolveRepoPath(batch.audit.markdown, "batch.audit.markdown", { extension: ".md", canonical: true });
const storedAudit = readJson(storedAuditJsonPath);
const liveAudit = runAudit([
  "--threshold=0.45",
  "--top=1",
  "--markdown-top=1",
  "--queue-size=1",
  "--include-image-hashes",
]);
const expectedAuditSummary = {
  taxa: batch.audit.taxa,
  auditedUniqueImages: batch.audit.approvedImages,
  comparedPairs: batch.audit.withinTaxonPairs,
  pairsAtOrAbove045: batch.audit.pairsAtOrAbove045,
  pairsAtOrAbove055: batch.audit.pairsAtOrAbove055,
  pairsAtOrAbove065: batch.audit.pairsAtOrAbove065,
  pairsAtOrAbove075: batch.audit.pairsAtOrAbove075,
};
for (const [label, audit] of [["stored", storedAudit], ["live", liveAudit]]) {
  assert.equal(audit.taxa, expectedAuditSummary.taxa, `${label} audit taxa mismatch`);
  assert.equal(audit.auditedUniqueImages, expectedAuditSummary.auditedUniqueImages, `${label} approved image count mismatch`);
  assert.equal(audit.comparedPairs, expectedAuditSummary.comparedPairs, `${label} within-taxon pair count mismatch`);
  assert.equal(audit.thresholdCounts["0.45"], expectedAuditSummary.pairsAtOrAbove045, `${label} >=0.45 count mismatch`);
  assert.equal(audit.thresholdCounts["0.55"], expectedAuditSummary.pairsAtOrAbove055, `${label} >=0.55 count mismatch`);
  assert.equal(audit.thresholdCounts["0.65"], expectedAuditSummary.pairsAtOrAbove065, `${label} >=0.65 count mismatch`);
  assert.equal(audit.thresholdCounts["0.75"], expectedAuditSummary.pairsAtOrAbove075, `${label} >=0.75 count mismatch`);
}
assert.ok(Array.isArray(liveAudit.approvedImageHashes), "Live audit did not return approved image hashes");
assert.equal(liveAudit.approvedImageHashes.length, liveAudit.auditedUniqueImages);
const liveApprovedHashes = new Set();
for (const imageRecord of liveAudit.approvedImageHashes) {
  assert.equal(typeof imageRecord.source, "string");
  assert.match(imageRecord.sha256, SHA256);
  liveApprovedHashes.add(imageRecord.sha256);
}

const dateMatch = batch.batchId.match(/(?:^|-)(\d{8})(?:-|$)/);
assert.ok(dateMatch, "Batch id must contain a delimited YYYYMMDD date");
const stagingDir = path.join(ROOT, "tools", "comfyui", "outputs", "overnight", dateMatch[1]);
assert.ok(isInside(ROOT, stagingDir), "Derived staging directory escaped the repository");
const promptRecordRelative = canonicalRelative(promptRecordPathSafe);
const seenIds = new Set();
const seenTargets = new Set();
const seenSpeciesIds = new Set();
const seenSpeciesSlots = new Set();
const seenSourceCallIds = new Set();
const seenImageHashes = new Set();
const deletedInputReferenceHashes = new Set();
const linkedRejectedInputCallIds = new Set();
const verified = [];

for (const record of batch.records) {
  assert.match(record.candidateId, SLUG);
  assert.match(record.speciesId, SPECIES_ID);
  assert.ok(!seenSpeciesIds.has(record.speciesId), `A batch may retain only one candidate per species: ${record.speciesId}`);
  seenSpeciesIds.add(record.speciesId);
  assert.ok(record.candidateId.startsWith(`${record.speciesId}-`), "Candidate id must start with species id");
  assert.match(record.sourceCallId, SOURCE_CALL_ID);
  assert.ok(!seenSourceCallIds.has(record.sourceCallId), `Duplicate source call id: ${record.sourceCallId}`);
  seenSourceCallIds.add(record.sourceCallId);
  assert.ok(!seenIds.has(record.candidateId), `Duplicate candidate id: ${record.candidateId}`);
  seenIds.add(record.candidateId);
  assert.equal(path.basename(record.targetFilename), record.targetFilename, "Target filename must not contain directories");
  assert.match(record.targetFilename, new RegExp(`^${escapeRegex(record.speciesId)}-[a-z0-9]+(?:-[a-z0-9]+)*-imagegen-v\\d+\\.png$`));
  assert.ok(!seenTargets.has(record.targetFilename), `Duplicate target filename: ${record.targetFilename}`);
  seenTargets.add(record.targetFilename);
  assert.ok(Number.isInteger(record.intendedSlot) && record.intendedSlot > 0, "intendedSlot must be a positive integer");
  const speciesSlot = `${record.speciesId}:${record.intendedSlot}`;
  assert.ok(!seenSpeciesSlots.has(speciesSlot), `Duplicate species/slot: ${speciesSlot}`);
  seenSpeciesSlots.add(speciesSlot);
  assert.match(record.compositionKey, SLUG);
  const candidateKind = record.kind ?? batch.policy.candidateKind;
  nonEmptyString(candidateKind, `candidate kind for ${record.candidateId}`);
  assert.ok(policyCandidateKinds.includes(candidateKind), `Candidate kind is not allowed by policy: ${candidateKind}`);
  if (policyCandidateKinds.length > 1) {
    assert.equal(record.kind, candidateKind, `Mixed-kind record must declare kind: ${record.candidateId}`);
  }
  assert.equal(record.review.status, "review-hold");
  assert.equal(record.review.representative, false);
  nonEmptyString(record.review.reviewer, "review.reviewer");
  nonEmptyString(record.review.notes, "review.notes");
  assert.ok(Number.isFinite(Date.parse(record.review.reviewedAt)), "review.reviewedAt must be an ISO timestamp");

  const candidateDirRelative = `tools/dino-review/pending/${record.candidateId}`;
  const candidateDir = resolveRepoPath(candidateDirRelative, `candidate directory ${record.candidateId}`, {
    canonical: true,
    kind: "directory",
  });
  const manifestPath = resolveRepoPath(`${candidateDirRelative}/candidate.json`, `manifest ${record.candidateId}`, {
    extension: ".json",
    canonical: true,
  });
  const manifest = readJson(manifestPath);
  const imageRelative = `${candidateDirRelative}/${record.targetFilename}`;
  const imagePath = resolveRepoPath(imageRelative, `candidate image ${record.candidateId}`, {
    extension: ".png",
    canonical: true,
  });
  assert.ok(isInside(candidateDir, imagePath), "Candidate image escaped its candidate directory");
  const image = fs.readFileSync(imagePath);
  const size = await decodePng(image, `candidate image ${record.candidateId}`);
  const imageSha256 = hash(image);
  assert.equal(imageSha256, record.image.sha256);
  assert.match(record.image.sha256, SHA256);
  assert.ok(!seenImageHashes.has(record.image.sha256), `Duplicate image hash: ${record.image.sha256}`);
  seenImageHashes.add(record.image.sha256);
  assert.equal(image.length, record.image.bytes);
  assert.deepEqual(size, { width: record.image.width, height: record.image.height });
  assert.equal(record.image.format, "png");

  assert.equal(manifest.candidateId, record.candidateId);
  assert.equal(manifest.filename, record.targetFilename);
  assert.equal(manifest.targetFilename, record.targetFilename);
  assert.equal(manifest.speciesId, record.speciesId);
  assert.equal(manifest.kind, candidateKind);
  assert.equal(manifest.anatomyReview.status, "review-hold");
  assert.equal(manifest.anatomyReview.representative, false);
  assert.equal(manifest.anatomyReview.reviewer, record.review.reviewer);
  assert.equal(manifest.anatomyReview.reviewedAt, record.review.reviewedAt);
  assert.equal(manifest.anatomyReview.notes, record.review.notes);
  assert.equal(manifest.provenance.source, batch.sourceAttribution);
  assert.equal(manifest.provenance.license, batch.licenseRecord);
  nonEmptyString(manifest.provenance.seed, "manifest provenance seed");
  nonEmptyString(manifest.provenance.workflow, "manifest provenance workflow");
  assert.equal(manifest.provenance.seed, record.provenance.seed);
  assert.equal(manifest.provenance.workflow, record.provenance.workflow);

  const promptFileRelative = strictProvenance
    ? record.provenance.promptPath
    : `tools/comfyui/outputs/overnight/${dateMatch[1]}/${record.targetFilename.replace(/\.png$/i, ".txt")}`;
  if (strictProvenance) nonEmptyString(record.provenance.promptPath, "record.provenance.promptPath");
  const promptFile = resolveRepoPath(promptFileRelative, `prompt file ${record.candidateId}`, {
    extension: ".txt",
    canonical: true,
  });
  assert.ok(
    canonicalRelative(promptFile).startsWith(`tools/comfyui/outputs/overnight/${dateMatch[1]}/`),
    "Candidate prompt must stay under the batch-date overnight staging root",
  );
  const promptBuffer = fs.readFileSync(promptFile);
  assert.match(record.provenance.promptSha256, SHA256);
  assert.equal(hash(promptBuffer), record.provenance.promptSha256);
  assert.equal(manifest.provenance.prompt, promptBuffer.toString("utf8").trim());
  assert.equal(
    record.provenance.promptRecord,
    `${promptRecordRelative}#${record.speciesId}`,
    `Prompt record path or anchor mismatch for ${record.speciesId}`,
  );
  assert.equal(promptBlockForSpecies(promptRecord, record.speciesId), promptBuffer.toString("utf8").trim());

  const referenceNumbers = [...manifest.provenance.prompt.matchAll(/\bImage\s+(\d+)\b/gi)]
    .map((match) => Number(match[1]));
  const requiredReferenceCount = referenceNumbers.length ? Math.max(...referenceNumbers) : 0;
  if (record.inputReferences == null) {
    if (strictProvenance) assert.fail(`schemaVersion 2 requires an inputReferences array for ${record.candidateId}`);
    if (requiredReferenceCount > 0) {
      warnLegacy(
        "missing-input-references",
        "Prompt names project-owned input images, but schemaVersion 1 does not record their paths and hashes.",
        record.candidateId,
      );
    }
  } else {
    assert.ok(Array.isArray(record.inputReferences), "inputReferences must be an array or null");
    assert.ok(record.inputReferences.length >= requiredReferenceCount, "inputReferences does not cover every numbered input image");
    const seenReferencePaths = new Set();
    for (const [index, reference] of record.inputReferences.entries()) {
      const referencePathValue = strictProvenance ? reference.path : (reference.path ?? reference.source);
      nonEmptyString(referencePathValue, `inputReferences[${index}].path`);
      assert.match(reference.sha256, SHA256);
      nonEmptyString(reference.role, `inputReferences[${index}].role`);
      const status = reference.status ?? (strictProvenance ? null : "approved-retained");
      if (strictProvenance) {
        assert.ok(["approved-retained", "rejected-input-deleted"].includes(status), `Invalid input reference status: ${status}`);
        assert.equal(reference.pixelsRetained, status === "approved-retained");
      }
      const referencePath = resolveRepoPath(referencePathValue, `inputReferences[${index}] path`, {
        canonical: true,
        extension: ".png",
        mustExist: status === "approved-retained",
      });
      const relativeReference = canonicalRelative(referencePath);
      assert.ok(!seenReferencePaths.has(relativeReference), `Duplicate input reference path: ${relativeReference}`);
      seenReferencePaths.add(relativeReference);
      if (status === "approved-retained") {
        assert.ok(relativeReference.startsWith("assets/dinosaurs/"), "Retained input references must be approved project assets");
        assert.equal(hashFile(referencePath), reference.sha256, `Input reference hash mismatch: ${relativeReference}`);
      } else {
        assert.ok(
          relativeReference.startsWith(`tools/comfyui/outputs/overnight/${dateMatch[1]}/`),
          "Deleted input references must name their former batch-date staging path",
        );
        assert.equal(fs.existsSync(referencePath), false, `Deleted input reference pixels still exist: ${relativeReference}`);
        assert.equal(liveApprovedHashes.has(reference.sha256), false, "Deleted input reference is still assigned in the live gallery");
        const linkedRejectedAttempts = rejectedAttempts.filter((attempt) => (
          attempt.speciesId === record.speciesId && attempt.sha256 === reference.sha256
        ));
        assert.equal(linkedRejectedAttempts.length, 1, "Deleted input reference must link to exactly one rejected attempt by species and SHA-256");
        const linkedRejected = linkedRejectedAttempts[0];
        assert.ok(!linkedRejectedInputCallIds.has(linkedRejected.sourceCallId), "A rejected attempt may back only one deleted input reference");
        linkedRejectedInputCallIds.add(linkedRejected.sourceCallId);
        if (reference.sourceCallId !== undefined) assert.equal(reference.sourceCallId, linkedRejected.sourceCallId);
        const linkedPromptPath = linkedRejected.provenance?.promptPath;
        nonEmptyString(linkedPromptPath, "Linked rejected attempt provenance.promptPath");
        assert.equal(
          relativeReference,
          linkedPromptPath.replace(/\.txt$/i, ".png"),
          "Deleted input reference path must match the linked rejected attempt prompt basename",
        );
        deletedInputReferenceHashes.add(reference.sha256);
      }
    }
  }

  const freshCandidateReport = runAudit([
    `--taxon=${record.speciesId}`,
    `--candidate=${imageRelative}`,
    "--threshold=1",
    "--top=1",
    "--markdown-top=1",
    "--queue-size=1",
  ]);
  const freshCandidateAudit = freshCandidateReport.candidateAudit;
  assert.ok(freshCandidateAudit, `Missing fresh candidate audit for ${record.candidateId}`);
  assert.ok(freshCandidateAudit.comparisonCount > 0, `Fresh candidate audit had zero comparisons for ${record.candidateId}`);
  const nearest = freshCandidateAudit.comparisons[0];
  const passedGate = freshCandidateAudit.maxStructuralSimilarity < batch.policy.candidateMaxSimilarityGate;
  assert.equal(record.candidateCompositionAudit.maxStructuralSimilarity, freshCandidateAudit.maxStructuralSimilarity);
  assert.equal(record.candidateCompositionAudit.nearestSlot, nearest.slot);
  assert.equal(record.candidateCompositionAudit.nearestRole, nearest.role);
  assert.equal(record.candidateCompositionAudit.matchMode, nearest.matchMode);
  assert.equal(record.candidateCompositionAudit.passedGate, passedGate);
  assert.equal(passedGate, true, `Candidate no longer passes the live similarity gate: ${record.candidateId}`);
  assert.ok(
    freshCandidateAudit.comparisons.some((comparison) => comparison.slot === record.intendedSlot),
    `intendedSlot is not present in the current gallery assignment: ${record.candidateId}`,
  );

  const assetTarget = path.join(ROOT, "assets", "dinosaurs", record.targetFilename);
  assert.equal(fs.existsSync(assetTarget), false, `Review-hold candidate already exists in public assets: ${record.targetFilename}`);
  verified.push({
    candidateId: record.candidateId,
    speciesId: record.speciesId,
    width: size.width,
    height: size.height,
    sha256: record.image.sha256,
    currentMaxStructuralSimilarity: freshCandidateAudit.maxStructuralSimilarity,
    targetPublicAssetAbsent: true,
    pngFullyDecoded: true,
  });
}

const verifiedRejected = [];
for (const attempt of rejectedAttempts) {
  assert.match(attempt.speciesId, SPECIES_ID);
  assert.match(attempt.sourceCallId, SOURCE_CALL_ID);
  assert.ok(!seenSourceCallIds.has(attempt.sourceCallId), `Duplicate source call id: ${attempt.sourceCallId}`);
  seenSourceCallIds.add(attempt.sourceCallId);
  assert.match(attempt.sha256, SHA256);
  assert.ok(!seenImageHashes.has(attempt.sha256), `Duplicate image hash: ${attempt.sha256}`);
  seenImageHashes.add(attempt.sha256);
  assert.ok(Number.isInteger(attempt.width) && attempt.width > 0);
  assert.ok(Number.isInteger(attempt.height) && attempt.height > 0);
  if (strictProvenance) assert.ok(Number.isInteger(attempt.bytes) && attempt.bytes > 0, "schemaVersion 2 rejects require bytes");
  if (attempt.bytes !== undefined) assert.ok(Number.isInteger(attempt.bytes) && attempt.bytes > 0);
  assert.ok(["rejected-before-enqueue", "deleted-rejected"].includes(attempt.status));
  nonEmptyString(attempt.reason, "Rejected attempt reason");
  assert.equal(attempt.pixelsRetained, false);

  const rejectProvenance = attempt.provenance ?? attempt;
  const requiredRejectFields = ["promptSha256", "seed", "workflow", "sourceAttribution", "licenseRecord"];
  for (const field of requiredRejectFields) {
    if (strictProvenance) nonEmptyString(rejectProvenance[field], `Rejected attempt provenance ${field}`);
    else if (!String(rejectProvenance[field] ?? "").trim()) {
      warnLegacy(
        `missing-reject-${field}`,
        `schemaVersion 1 rejected attempt does not retain verifiable ${field}.`,
        attempt.sourceCallId,
      );
    }
  }
  if (rejectProvenance.promptSha256) {
    assert.match(rejectProvenance.promptSha256, SHA256);
  }
  if (strictProvenance) {
    assert.equal(rejectProvenance.sourceAttribution, batch.sourceAttribution);
    assert.equal(rejectProvenance.licenseRecord, batch.licenseRecord);
    const rejectedPromptPath = resolveRepoPath(
      rejectProvenance.promptPath,
      `Rejected prompt path ${attempt.sourceCallId}`,
      { extension: ".txt", canonical: true },
    );
    assert.ok(
      canonicalRelative(rejectedPromptPath).startsWith(`tools/comfyui/outputs/overnight/${dateMatch[1]}/`),
      "Rejected prompt must stay under the batch-date overnight staging root",
    );
    assert.equal(hashFile(rejectedPromptPath), rejectProvenance.promptSha256);
  }

  if (attempt.candidateId) {
    assert.equal(attempt.status, "deleted-rejected");
    assert.match(attempt.candidateId, SLUG);
    assert.ok(attempt.candidateId.startsWith(`${attempt.speciesId}-`));
    assert.equal(path.basename(attempt.targetFilename), attempt.targetFilename);
    assert.match(attempt.targetFilename, new RegExp(`^${escapeRegex(attempt.speciesId)}-[a-z0-9]+(?:-[a-z0-9]+)*-imagegen-v\\d+\\.png$`));
    assert.ok(!seenIds.has(attempt.candidateId), `Candidate id appears as retained and rejected: ${attempt.candidateId}`);
    seenIds.add(attempt.candidateId);
    assert.ok(!seenTargets.has(attempt.targetFilename), `Target appears as retained and rejected: ${attempt.targetFilename}`);
    seenTargets.add(attempt.targetFilename);
    assert.equal(fs.existsSync(path.join(ROOT, "tools", "dino-review", "pending", attempt.candidateId)), false);
    assert.equal(fs.existsSync(path.join(ROOT, "assets", "dinosaurs", attempt.targetFilename)), false);
    if (strictProvenance) {
      const rejectedImageRelative = rejectProvenance.promptPath.replace(/\.txt$/i, ".png");
      assert.equal(
        path.posix.basename(rejectedImageRelative),
        attempt.targetFilename,
        "Deleted candidate target filename must match its schemaVersion 2 prompt basename",
      );
      const rejectedImagePath = resolveRepoPath(
        rejectedImageRelative,
        `deleted candidate image ${attempt.candidateId}`,
        { extension: ".png", canonical: true, mustExist: false },
      );
      assert.ok(
        canonicalRelative(rejectedImagePath).startsWith(`tools/comfyui/outputs/overnight/${dateMatch[1]}/`),
        "Deleted candidate image must stay under the batch-date overnight staging root",
      );
      assert.equal(fs.existsSync(rejectedImagePath), false, "Deleted schemaVersion 2 candidate pixels still exist in staging");
    } else {
      assert.equal(fs.existsSync(path.join(stagingDir, attempt.targetFilename)), false);
      const rejectedPromptRelative = `tools/comfyui/outputs/overnight/${dateMatch[1]}/${attempt.targetFilename.replace(/\.png$/i, ".txt")}`;
      const rejectedPrompt = resolveRepoPath(rejectedPromptRelative, `rejected prompt ${attempt.candidateId}`, {
        extension: ".txt",
        canonical: true,
      });
      assert.match(attempt.promptSha256, SHA256);
      assert.equal(hashFile(rejectedPrompt), attempt.promptSha256);
    }
    nonEmptyString(rejectProvenance.seed, "deleted reject seed");
    nonEmptyString(rejectProvenance.workflow, "deleted reject workflow");
  } else {
    assert.equal(attempt.status, "rejected-before-enqueue");
  }
  verifiedRejected.push({
    speciesId: attempt.speciesId,
    status: attempt.status,
    sha256: attempt.sha256,
    checkedSurfacePixelCopiesAbsent: true,
  });
}

const rejectedByHash = new Map(rejectedAttempts.map((attempt) => [attempt.sha256, attempt]));
const checkedAbsentHashes = new Set([...rejectedByHash.keys(), ...deletedInputReferenceHashes]);
const pixelScanRoots = [
  path.join(ROOT, "tools", "dino-review", "pending"),
  stagingDir,
];
for (const absentHash of checkedAbsentHashes) {
  assert.equal(liveApprovedHashes.has(absentHash), false, "Rejected or deleted-input pixels are still assigned in the current gallery");
}
const pixelFiles = pixelScanRoots.flatMap(collectPngFiles);
if (checkedAbsentHashes.size) {
  for (const file of pixelFiles) {
    if (checkedAbsentHashes.has(hashFile(file))) {
      assert.fail(`Rejected or deleted-input pixels still exist in a checked retention root: ${canonicalRelative(file)}`);
    }
  }
}

if (!strictProvenance && rejectedAttempts.length) {
  warnLegacy(
    "external-cache-absence-unverifiable",
    "Current assigned-gallery hashes plus pending and staging roots were checked, but schemaVersion 1 does not carry external generated-cache deletion evidence.",
    null,
  );
}

console.log(JSON.stringify({
  batchId: batch.batchId,
  schemaVersion: batch.schemaVersion,
  status: batch.status,
  liveAuditMatchesBatchDeclaration: true,
  verifiedCandidates: verified.length,
  candidates: verified,
  verifiedRejectedAttempts: verifiedRejected.length,
  rejectedAttempts: verifiedRejected,
  liveApprovedGalleryHashesChecked: liveAudit.approvedImageHashes.length,
  deletedInputReferenceHashesChecked: deletedInputReferenceHashes.size,
  rejectedPixelScanRoots: pixelScanRoots.map(canonicalRelative),
  rejectedPixelsAbsentFromCheckedSurfaces: true,
  retainedCandidateTargetPathsAbsent: true,
  automaticPromotionAllowed: false,
  verifierPerformedPublicAssetMutation: false,
  provenanceVerification: warnings.length ? "legacy-partial" : "complete",
  verificationWarnings: warnings,
}, null, 2));
