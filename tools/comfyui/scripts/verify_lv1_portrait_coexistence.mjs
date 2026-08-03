import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..", "..");
const APP_JS = path.join(ROOT, "app.js");
const ASSIGNMENTS_JS = path.join(ROOT, "gallery-slots.js");
const DECISIONS_JSON = path.join(ROOT, "tools", "comfyui", "gallery-slot-visual-decisions.json");
const METADATA_JSON = path.join(ROOT, "tools", "comfyui", "lv1-portrait-coexistence-batch-20260803.json");
const INDEX_HTML = path.join(ROOT, "index.html");

const EXPECTED = [
  {
    taxonId: "triceratops-horridus",
    companionTaxon: "edmontosaurus-annectens",
    source: "assets/dinosaurs/triceratops-horridus-edmontosaurus-lower-hellcreek-portrait-ecology-imagegen-v2.png",
    sha256: "dac6eb1a1c067631ce5ea8858e58a36ed2ab2c54bfde1cf250d6ed0f0085bfe8",
    bytes: 2900485,
    compositionKey: "portrait-channel-depth-diagonal",
  },
  {
    taxonId: "parasaurolophus-walkeri",
    companionTaxon: "centrosaurus-apertus",
    source: "assets/dinosaurs/parasaurolophus-walkeri-centrosaurus-forest-scurve-portrait-ecology-imagegen-v3.png",
    sha256: "cdd22717e91c448494cb80237e486ad3e1e2167b81e45782cb32d6725862e13d",
    bytes: 3256137,
    compositionKey: "portrait-low-forest-scurve-zdepth",
  },
];

function extractLiteral(source, name) {
  const marker = `const ${name} =`;
  const markerAt = source.indexOf(marker);
  if (markerAt < 0) throw new Error(`Missing declaration: ${name}`);

  let start = markerAt + marker.length;
  while (/\s/.test(source[start])) start += 1;
  while (source[start] !== "[" && source[start] !== "{") start += 1;

  const open = source[start];
  const close = open === "[" ? "]" : "}";
  let depth = 0;
  let quote = "";
  let escaped = false;

  for (let index = start; index < source.length; index += 1) {
    const char = source[index];
    if (quote) {
      if (escaped) escaped = false;
      else if (char === "\\") escaped = true;
      else if (char === quote) quote = "";
      continue;
    }
    if (char === '"' || char === "'" || char === "`") {
      quote = char;
      continue;
    }
    if (char === open) depth += 1;
    if (char === close && --depth === 0) return source.slice(start, index + 1);
  }

  throw new Error(`Unterminated declaration: ${name}`);
}

function sha256(filePath) {
  return crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");
}

const appSource = fs.readFileSync(APP_JS, "utf8");
const dinosaurs = vm.runInNewContext(`(${extractLiteral(appSource, "dinosaurs")})`, Object.create(null));
const samples = vm.runInNewContext(`(${extractLiteral(appSource, "generatedImageSamples")})`, Object.create(null));
const assignmentSandbox = { window: {} };
vm.runInNewContext(fs.readFileSync(ASSIGNMENTS_JS, "utf8"), assignmentSandbox);
const assignments = assignmentSandbox.window.gallerySlotAssignments || {};
const decisionsRoot = JSON.parse(fs.readFileSync(DECISIONS_JSON, "utf8"));
const metadata = JSON.parse(fs.readFileSync(METADATA_JSON, "utf8"));
const indexHtml = fs.readFileSync(INDEX_HTML, "utf8");
const errors = [];

for (const expected of EXPECTED) {
  const taxon = dinosaurs.find((item) => item.id === expected.taxonId);
  const candidate = (samples[expected.taxonId] || []).find(
    (item) => (item?.src || item?.source) === expected.source,
  );
  const assignment = (assignments[expected.taxonId] || []).find(
    (item) => Number(item.gallerySlot) === 7,
  );
  const decision = decisionsRoot.taxa?.[expected.taxonId]?.["7"];
  const record = metadata.records?.[expected.taxonId];
  const assetPath = path.join(ROOT, expected.source);

  if (!taxon) errors.push(`${expected.taxonId}: missing dinosaur record`);
  else {
    if (taxon.knowledgeLevel !== 1) errors.push(`${expected.taxonId}: expected LV1`);
    if (taxon.imageSlots !== 7) errors.push(`${expected.taxonId}: imageSlots must be 7`);
    if (!String(taxon.reviewStatus || "").startsWith("7장")) {
      errors.push(`${expected.taxonId}: reviewStatus does not expose seven slots`);
    }
  }

  if (!candidate) errors.push(`${expected.taxonId}: missing app S7 candidate`);
  else {
    if (candidate.gallerySlot !== 7) errors.push(`${expected.taxonId}: candidate slot mismatch`);
    if (candidate.galleryRole !== "alternate-habitat-behavior") {
      errors.push(`${expected.taxonId}: candidate role mismatch`);
    }
    if (candidate.kind !== "anatomy review") errors.push(`${expected.taxonId}: candidate kind mismatch`);
    if (candidate.compositionKey !== expected.compositionKey) {
      errors.push(`${expected.taxonId}: compositionKey mismatch`);
    }
    if (!candidate.reviewStatus?.includes("not representative")) {
      errors.push(`${expected.taxonId}: representative prohibition missing`);
    }
    if (!candidate.sourceAttribution || !candidate.licenseRecord || !candidate.generationPromptRecord
      || !candidate.generationSeed || !candidate.generationWorkflow || !candidate.metadataRecord) {
      errors.push(`${expected.taxonId}: incomplete app provenance`);
    }
    if (!Array.isArray(candidate.evidenceSources) || candidate.evidenceSources.length < 2) {
      errors.push(`${expected.taxonId}: evidence sources incomplete`);
    }
  }

  if (!assignment) errors.push(`${expected.taxonId}: missing S7 assignment`);
  else {
    if (assignment.source !== expected.source) errors.push(`${expected.taxonId}: assignment source mismatch`);
    if (assignment.galleryRole !== "alternate-habitat-behavior") {
      errors.push(`${expected.taxonId}: assignment role mismatch`);
    }
    if (assignment.expectedKind !== "anatomy review") {
      errors.push(`${expected.taxonId}: assignment kind mismatch`);
    }
  }

  if (!decision || decision.status !== "approved") {
    errors.push(`${expected.taxonId}: S7 decision is not approved`);
  } else {
    if (decision.source !== expected.source) errors.push(`${expected.taxonId}: decision source mismatch`);
    if (decision.role !== "alternate-habitat-behavior") {
      errors.push(`${expected.taxonId}: decision role mismatch`);
    }
  }

  if (!record) errors.push(`${expected.taxonId}: missing metadata record`);
  else {
    if (record.companionTaxon !== expected.companionTaxon) {
      errors.push(`${expected.taxonId}: metadata companion mismatch`);
    }
    if (record.projectAsset !== expected.source || record.approvedProjectCopy !== expected.source) {
      errors.push(`${expected.taxonId}: metadata project asset mismatch`);
    }
    if (record.sha256 !== expected.sha256 || record.bytes !== expected.bytes) {
      errors.push(`${expected.taxonId}: metadata hash or byte count mismatch`);
    }
    if (record.compositionKey !== expected.compositionKey) {
      errors.push(`${expected.taxonId}: metadata compositionKey mismatch`);
    }
    if (!record.prompt || !record.generatorCallId || !record.generatorOriginal
      || !record.review?.status?.includes("not representative")) {
      errors.push(`${expected.taxonId}: metadata provenance or review incomplete`);
    }
  }

  if (!fs.existsSync(assetPath)) errors.push(`${expected.taxonId}: approved asset missing`);
  else {
    if (fs.statSync(assetPath).size !== expected.bytes) errors.push(`${expected.taxonId}: asset byte mismatch`);
    if (sha256(assetPath) !== expected.sha256) errors.push(`${expected.taxonId}: asset hash mismatch`);
  }
}

const compositionKeys = EXPECTED.map((item) => item.compositionKey);
if (new Set(compositionKeys).size !== compositionKeys.length) {
  errors.push("compositionKey values are not unique");
}
if (decisionsRoot.targetSlots !== 805) errors.push("decision targetSlots must be 805");
if (metadata.galleryPolicy?.representativePromotion !== "prohibited until a separate stricter anatomy review passes") {
  errors.push("metadata representative policy mismatch");
}
if (!metadata.galleryPolicy?.compositionDiversityGate) errors.push("metadata composition gate missing");
if (/\.codex[\\/]generated_images/.test(appSource)) errors.push("generator path leaked into app.js");
if (!indexHtml.includes("20260803-lv1-portrait-composition-v1")) errors.push("cache key mismatch");

const report = {
  batchId: metadata.batchId || "",
  expectedSlots: EXPECTED.length,
  compositionKeys,
  targetSlots: decisionsRoot.targetSlots,
  errors,
};

console.log(JSON.stringify(report, null, 2));
if (errors.length) process.exitCode = 1;
