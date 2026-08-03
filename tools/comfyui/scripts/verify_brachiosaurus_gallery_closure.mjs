import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..", "..");
const APP_JS = path.join(ROOT, "app.js");
const ASSIGNMENTS_JS = path.join(ROOT, "gallery-slots.js");
const METADATA_JSON = path.join(ROOT, "tools", "comfyui", "brachiosaurus-gallery-closure-20260803.json");
const DECISIONS_JSON = path.join(ROOT, "tools", "comfyui", "gallery-slot-visual-decisions.json");
const REJECTIONS_JSON = path.join(ROOT, "tools", "comfyui", "gallery-slot-rejections.json");
const PLAN_JSON = path.join(ROOT, "tools", "comfyui", "outputs", "gallery-slot-generation-plan.json");
const SEED_MANIFEST_JSON = path.join(
  ROOT,
  "tools",
  "comfyui",
  "lora_training",
  "sauropod_brachiosaurus",
  "seed_manifest.json",
);
const TAXON_ID = "brachiosaurus-altithorax";
const OLD_FAILED_S2 = "assets/dinosaurs/brachiosaurus-altithorax-slate-moss-pattern-imagegen-v1.png";

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

function loadAssignments() {
  const context = { window: {} };
  vm.runInNewContext(fs.readFileSync(ASSIGNMENTS_JS, "utf8"), context, { filename: ASSIGNMENTS_JS });
  return context.window.gallerySlotAssignments;
}

function sha256(buffer) {
  return crypto.createHash("sha256").update(buffer).digest("hex");
}

function pngDimensions(buffer) {
  const signature = "89504e470d0a1a0a";
  if (buffer.length < 24 || buffer.subarray(0, 8).toString("hex") !== signature) {
    throw new Error("not a valid PNG");
  }
  return `${buffer.readUInt32BE(16)}x${buffer.readUInt32BE(20)}`;
}

const errors = [];
const fail = (message) => errors.push(message);
const appSource = fs.readFileSync(APP_JS, "utf8");
const samples = vm.runInNewContext(`(${extractLiteral(appSource, "generatedImageSamples")})`, Object.create(null));
const assignments = loadAssignments();
const metadata = JSON.parse(fs.readFileSync(METADATA_JSON, "utf8"));
const decisions = JSON.parse(fs.readFileSync(DECISIONS_JSON, "utf8"));
const rejections = JSON.parse(fs.readFileSync(REJECTIONS_JSON, "utf8"));
const plan = JSON.parse(fs.readFileSync(PLAN_JSON, "utf8"));
const seedManifest = JSON.parse(fs.readFileSync(SEED_MANIFEST_JSON, "utf8"));

const slots = Object.entries(metadata.slots || {}).sort(([a], [b]) => a.localeCompare(b, "en"));
if (metadata.auditId !== "2026-08-03-brachiosaurus-gallery-closure-2") {
  fail(`Unexpected auditId: ${metadata.auditId}`);
}
if (slots.length !== 6) fail(`Expected six metadata slots, found ${slots.length}`);
if (metadata.summary?.pass !== 6 || metadata.summary?.hold !== 0 || metadata.summary?.fail !== 0) {
  fail("Metadata summary must be PASS 6 / HOLD 0 / FAIL 0");
}

const compositionKeys = [];
const cameraFamilies = [];
const spatialSignatures = [];
const expectedSources = [];
const expectedRoles = [];
const historicalPromptGaps = new Set(["S1", "S4"]);

for (const [slotName, slot] of slots) {
  const slotNumber = Number(slotName.slice(1));
  if (slotNumber < 1 || slotNumber > 6) fail(`Invalid slot key: ${slotName}`);
  if (slot.result !== "PASS") fail(`${slotName} is not PASS: ${slot.result}`);
  if (!slot.source?.startsWith("assets/dinosaurs/brachiosaurus-altithorax-")) {
    fail(`${slotName} has an unsafe or non-species-prefixed source: ${slot.source}`);
  }
  if (slot.source?.includes(".codex/generated_images")) fail(`${slotName} references a generated staging path`);
  if (!slot.compositionKey || !slot.cameraFamily || !slot.spatialSignature) {
    fail(`${slotName} lacks composition metadata`);
  }
  compositionKeys.push(slot.compositionKey);
  cameraFamilies.push(slot.cameraFamily);
  spatialSignatures.push(slot.spatialSignature);
  expectedSources.push(slot.source);
  expectedRoles.push(slot.galleryRole);

  const assetPath = path.join(ROOT, slot.source);
  if (!fs.existsSync(assetPath)) {
    fail(`${slotName} asset is missing: ${slot.source}`);
  } else {
    const buffer = fs.readFileSync(assetPath);
    if (buffer.length !== slot.bytes) fail(`${slotName} byte mismatch: ${buffer.length} != ${slot.bytes}`);
    if (sha256(buffer) !== slot.sha256) fail(`${slotName} sha256 mismatch`);
    try {
      if (pngDimensions(buffer) !== slot.dimensions) fail(`${slotName} dimension mismatch`);
    } catch (error) {
      fail(`${slotName} PNG validation failed: ${error.message}`);
    }
  }

  const provenance = slot.provenance || {};
  for (const key of ["generator", "seedAvailability", "workflow", "sourceLicense"]) {
    if (typeof provenance[key] !== "string" || provenance[key].trim().length < 4) {
      fail(`${slotName} provenance is missing ${key}`);
    }
  }
  if (historicalPromptGaps.has(slotName)) {
    if (provenance.prompt !== null || provenance.callId !== null || provenance.seed !== null) {
      fail(`${slotName} must preserve unknown historical prompt/call/seed as null`);
    }
    if (!provenance.seedAvailability.includes("not recorded")) {
      fail(`${slotName} must explicitly state that the historical seed was not recorded`);
    }
  } else if (Array.isArray(provenance.steps)) {
    if (!provenance.steps.length || provenance.steps.some((step) => !step.callId || !step.prompt)) {
      fail(`${slotName} workflow steps must retain call IDs and prompts`);
    }
  } else if (!provenance.callId || !provenance.prompt) {
    fail(`${slotName} must retain a generator call ID and prompt`);
  }
}

for (const [label, values] of [
  ["compositionKey", compositionKeys],
  ["cameraFamily", cameraFamilies],
  ["spatialSignature", spatialSignatures],
]) {
  if (new Set(values).size !== 6) fail(`Expected six unique ${label} values, found ${new Set(values).size}`);
}

const taxonAssignments = assignments?.[TAXON_ID] || [];
if (taxonAssignments.length !== 6) fail(`Expected six gallery assignments, found ${taxonAssignments.length}`);
for (let index = 0; index < 6; index += 1) {
  const assignment = taxonAssignments[index];
  const slot = metadata.slots[`S${index + 1}`];
  if (!assignment) continue;
  if (assignment.gallerySlot !== index + 1) fail(`Assignment order mismatch at S${index + 1}`);
  if (assignment.source !== slot.source) fail(`Assignment source mismatch at S${index + 1}`);
  if (assignment.galleryRole !== slot.galleryRole) fail(`Assignment role mismatch at S${index + 1}`);
}

const taxonSamples = samples[TAXON_ID] || [];
const sampleBySource = new Map(taxonSamples.map((sample) => [sample.src || sample.source, sample]));
for (const [slotName, slot] of slots) {
  const sample = sampleBySource.get(slot.source);
  if (!sample) {
    fail(`${slotName} is missing from generatedImageSamples`);
    continue;
  }
  if (sample.compositionKey !== slot.compositionKey) fail(`${slotName} sample compositionKey mismatch`);
  if (sample.metadataRecord !== `tools/comfyui/brachiosaurus-gallery-closure-20260803.json#slots/${slotName}`) {
    fail(`${slotName} sample metadataRecord mismatch`);
  }
}

const countLevelPasses = taxonSamples.filter((sample) => sample.kind === "count-level pass");
if (countLevelPasses.length !== 1 || countLevelPasses[0]?.src !== metadata.slots.S1.source) {
  fail(`Expected S1 to be the sole count-level pass, found ${countLevelPasses.length}`);
}
const v16 = sampleBySource.get("assets/dinosaurs/brachiosaurus-altithorax-imagegen-v16-source-candidate.png");
if (v16?.kind !== "review hold") fail("Historical v16 must be review hold");
const staleV16PromotionPhrases = ["승격된 v16", "현재 v16", "v16을 긍정 시드"];
for (const phrase of staleV16PromotionPhrases) {
  if (taxonSamples.some((sample) => `${sample.title || ""} ${sample.body || ""}`.includes(phrase))) {
    fail(`Brachiosaurus sample copy still presents v16 as current: ${phrase}`);
  }
}

if (metadata.slots.S4.anatomyScope !== "head-only" || metadata.slots.S4.representativeEligible !== false) {
  fail("S4 must be a non-representative head-only pass");
}
if (!Array.isArray(metadata.slots.S4.notAssessed) || metadata.slots.S4.notAssessed.length < 4) {
  fail("S4 must list the unassessed full-body gates");
}
if (
  metadata.slots.S6.roleVariant !== "two-individual-spacing" ||
  metadata.slots.S6.gallerySubrole !== "two-individual-spacing" ||
  metadata.slots.S6.representativeEligible !== false
) {
  fail("S6 must be a non-representative two-individual-spacing variant");
}
const s6Sample = sampleBySource.get(metadata.slots.S6.source);
if (!s6Sample?.body?.includes("직접 증거로 설명하지 않습니다")) {
  fail("S6 sample must explicitly reject age, kinship, herd, and growth claims");
}
const s4Assignment = taxonAssignments.find((assignment) => assignment.gallerySlot === 4);
if (s4Assignment?.gallerySubrole !== "identity-head-detail" || !s4Assignment?.claimBoundary?.includes("Head-only")) {
  fail("S4 assignment must transmit the head-only subrole and claim boundary");
}
const s6Assignment = taxonAssignments.find((assignment) => assignment.gallerySlot === 6);
if (
  s6Assignment?.gallerySubrole !== "two-individual-spacing" ||
  !s6Assignment?.claimBoundary?.includes("no age") ||
  !s6Assignment?.claimBoundary?.includes("herd") ||
  !s6Assignment?.claimBoundary?.includes("defense")
) {
  fail("S6 assignment must transmit the two-individual-spacing subrole and no-age/social claim boundary");
}

const decisionSlots = decisions?.taxa?.[TAXON_ID] || {};
for (let slotNumber = 1; slotNumber <= 6; slotNumber += 1) {
  const decision = decisionSlots[String(slotNumber)];
  const slot = metadata.slots[`S${slotNumber}`];
  if (decision?.status !== "approved" || decision?.source !== slot.source) {
    fail(`Visual decision mismatch at S${slotNumber}`);
  }
}
if (!rejections?.rejectedSources?.[OLD_FAILED_S2]) fail("Former failed S2 is missing from the rejection manifest");

const brachPlan = plan.taxa?.find((taxon) => taxon.taxon === TAXON_ID);
if (!brachPlan || brachPlan.slots.some((slot) => slot.status !== "approved")) {
  fail("Generated Brachiosaurus slot plan is not fully approved");
}
if (plan.summary?.visualDecisionErrors !== 0 || plan.summary?.approvedSlots !== plan.summary?.targetSlots) {
  fail("Global slot plan contains visual-decision errors or unapproved target slots");
}

const v18Seed = seedManifest.items?.find((item) => item.source === metadata.slots.S1.source);
const v16Seed = seedManifest.items?.find(
  (item) => item.source === "assets/dinosaurs/brachiosaurus-altithorax-imagegen-v16-source-candidate.png",
);
if (v18Seed?.role !== "train_seed") fail("S1 v18 must be the positive train seed");
if (v16Seed?.role !== "review_hold") fail("Historical v16 must be demoted from train_seed");
const staleSeedText = JSON.stringify(seedManifest);
for (const phrase of ["promoted v16", "while v16 gives", "promoted v16 seed", "outrank v16"]) {
  if (staleSeedText.includes(phrase)) fail(`Seed manifest still presents v16 as current: ${phrase}`);
}

const result = {
  taxon: TAXON_ID,
  slots: slots.length,
  assigned: taxonAssignments.length,
  pass: metadata.summary?.pass,
  soleRepresentative: metadata.slots.S1.source,
  uniqueCompositionKeys: new Set(compositionKeys).size,
  uniqueCameraFamilies: new Set(cameraFamilies).size,
  uniqueSpatialSignatures: new Set(spatialSignatures).size,
  oldFailedS2Rejected: Boolean(rejections?.rejectedSources?.[OLD_FAILED_S2]),
  errors,
};

console.log(JSON.stringify(result, null, 2));
if (errors.length) process.exitCode = 1;
