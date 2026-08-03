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
const METADATA_JSON = path.join(
  ROOT,
  "tools",
  "comfyui",
  "maiasaura-peeblesorum-initial-gallery-batch-20260803.json",
);
const INDEX_HTML = path.join(ROOT, "index.html");

const EXPECTED = [
  {
    slot: 1,
    role: "representative",
    kind: "count-level pass",
    source: "assets/dinosaurs/maiasaura-peeblesorum-low-transverse-crest-representative-imagegen-v1.png",
    sha256: "9dfd43f42bd3f9368399f09103aa926ee199d7279a6abfabac2112c0c24208b7",
    bytes: 3309147,
    metadataKey: "representative",
    representativeEligible: true,
  },
  {
    slot: 2,
    role: "color-pattern",
    kind: "review hold",
    source: "assets/dinosaurs/maiasaura-peeblesorum-celadon-blackberry-diagonal-pattern-imagegen-v1.png",
    sha256: "187c2f87125614fc626461fd09598e83d6e3175a9c54fd6b6370123e6c7f886b",
    bytes: 3213976,
    metadataKey: "color-pattern",
    representativeEligible: false,
  },
  {
    slot: 3,
    role: "habitat-ecology",
    kind: "anatomy review",
    source: "assets/dinosaurs/maiasaura-peeblesorum-two-medicine-nesting-ground-egg-hypothesis-portrait-imagegen-v1.png",
    sha256: "3c4e211f17d2c9ce4399a76c8eaa11b0974bbde39e7634900ddf5d86a5c030fd",
    bytes: 2882242,
    metadataKey: "habitat-ecology",
    representativeEligible: false,
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
const samples = vm.runInNewContext(
  `(${extractLiteral(appSource, "generatedImageSamples")})`,
  Object.create(null),
);
const identities = vm.runInNewContext(
  `(${extractLiteral(appSource, "identityChecklists")})`,
  Object.create(null),
);
const profiles = vm.runInNewContext(
  `(${extractLiteral(appSource, "visualVariationProfiles")})`,
  Object.create(null),
);
const routes = vm.runInNewContext(
  `(${extractLiteral(appSource, "generationRouteGuides")})`,
  Object.create(null),
);
const assignmentSandbox = { window: {} };
vm.runInNewContext(fs.readFileSync(ASSIGNMENTS_JS, "utf8"), assignmentSandbox);
const assignments = assignmentSandbox.window.gallerySlotAssignments || {};
const decisions = JSON.parse(fs.readFileSync(DECISIONS_JSON, "utf8"));
const metadata = JSON.parse(fs.readFileSync(METADATA_JSON, "utf8"));
const html = fs.readFileSync(INDEX_HTML, "utf8");
const errors = [];
const taxonId = "maiasaura-peeblesorum";
const taxon = dinosaurs.find((item) => item.id === taxonId);

if (!taxon) errors.push("missing Maiasaura taxon");
else {
  if (taxon.knowledgeLevel !== 2) errors.push("Maiasaura must be LV2");
  if (taxon.imageSlots !== 3) errors.push("Maiasaura must expose three initial slots");
  if (taxon.family !== "Hadrosauridae") errors.push("Maiasaura family mismatch");
}
if (!Array.isArray(identities[taxonId]) || identities[taxonId].length < 8) {
  errors.push("Maiasaura identity checklist incomplete");
}
if (!profiles[taxonId]?.composition || !profiles[taxonId]?.avoid) {
  errors.push("Maiasaura visual variation profile incomplete");
}
if (!routes[taxonId]?.control?.includes(EXPECTED[0].source)) {
  errors.push("Maiasaura generation route does not lock S1 control");
}

for (const expected of EXPECTED) {
  const candidate = (samples[taxonId] || []).find(
    (item) => Number(item.gallerySlot) === expected.slot,
  );
  const assignment = (assignments[taxonId] || []).find(
    (item) => Number(item.gallerySlot) === expected.slot,
  );
  const decision = decisions.taxa?.[taxonId]?.[String(expected.slot)];
  const record = metadata.records?.[expected.metadataKey];
  const filePath = path.join(ROOT, expected.source);

  if (!candidate) errors.push(`S${expected.slot}: missing candidate`);
  else {
    if ((candidate.src || candidate.source) !== expected.source) errors.push(`S${expected.slot}: candidate source mismatch`);
    if (candidate.galleryRole !== expected.role) errors.push(`S${expected.slot}: candidate role mismatch`);
    if (candidate.kind !== expected.kind) errors.push(`S${expected.slot}: candidate kind mismatch`);
    if (expected.representativeEligible === false && candidate.representativeEligible !== false) {
      errors.push(`S${expected.slot}: representative prohibition missing`);
    }
    if (!candidate.sourceAttribution || !candidate.licenseRecord || !candidate.generationPromptRecord
      || !candidate.generationSeed || !candidate.generationWorkflow || !candidate.metadataRecord) {
      errors.push(`S${expected.slot}: app provenance incomplete`);
    }
  }

  if (!assignment) errors.push(`S${expected.slot}: missing assignment`);
  else {
    if (assignment.source !== expected.source) errors.push(`S${expected.slot}: assignment source mismatch`);
    if (assignment.galleryRole !== expected.role) errors.push(`S${expected.slot}: assignment role mismatch`);
    if (assignment.expectedKind !== expected.kind) errors.push(`S${expected.slot}: assignment kind mismatch`);
  }

  if (!decision || decision.status !== "approved") errors.push(`S${expected.slot}: decision not approved`);
  else if (decision.source !== expected.source || decision.role !== expected.role) {
    errors.push(`S${expected.slot}: decision mismatch`);
  }

  if (!record) errors.push(`S${expected.slot}: metadata record missing`);
  else {
    if (record.approvedProjectPath !== expected.source) errors.push(`S${expected.slot}: metadata path mismatch`);
    if (record.bytes !== expected.bytes || record.sha256.toLowerCase() !== expected.sha256) {
      errors.push(`S${expected.slot}: metadata byte/hash mismatch`);
    }
    if (!Array.isArray(record.prompt) || record.prompt.length < 6 || record.seed !== "not exposed by generator") {
      errors.push(`S${expected.slot}: prompt or seed record incomplete`);
    }
    if (record.representativeEligible !== expected.representativeEligible) {
      errors.push(`S${expected.slot}: metadata representative policy mismatch`);
    }
  }

  if (!fs.existsSync(filePath)) errors.push(`S${expected.slot}: asset missing`);
  else {
    if (fs.statSync(filePath).size !== expected.bytes) errors.push(`S${expected.slot}: asset bytes mismatch`);
    if (sha256(filePath) !== expected.sha256) errors.push(`S${expected.slot}: asset hash mismatch`);
  }
}

if (!metadata.copyrightSafety || metadata.copyrightSafety.externalArtworkUsed !== false) {
  errors.push("copyright safety record incomplete");
}
if (!metadata.evidenceBoundary?.hypothetical?.some((item) => item.includes("maternity"))) {
  errors.push("maternal-care reconstruction boundary missing");
}
if (!metadata.records?.["habitat-ecology"]?.promptOutputDivergence?.includes("nine")) {
  errors.push("egg-count prompt-output divergence missing");
}
if (/\.codex[\\/]generated_images/.test(appSource) || /\.codex[\\/]generated_images/.test(fs.readFileSync(ASSIGNMENTS_JS, "utf8"))) {
  errors.push("generator path leaked into app data");
}
if (!html.includes("20260803-maiasaura-nesting-v1")) errors.push("Maiasaura cache key missing");
if (decisions.targetSlots < 808) errors.push("decision target slots regressed below 808");

console.log(JSON.stringify({
  taxon: taxonId,
  slots: EXPECTED.length,
  targetSlots: decisions.targetSlots,
  rejectedAttempts: metadata.rejectedAttempts?.length || 0,
  errors,
}, null, 2));
if (errors.length) process.exitCode = 1;
