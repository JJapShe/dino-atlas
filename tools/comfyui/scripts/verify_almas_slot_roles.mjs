import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..", "..");
const APP_JS = path.join(ROOT, "app.js");
const ASSIGNMENTS_JS = path.join(ROOT, "gallery-slots.js");
const DECISIONS_JSON = path.join(ROOT, "tools", "comfyui", "gallery-slot-visual-decisions.json");
const METADATA_JSON = path.join(ROOT, "tools", "comfyui", "almas-ukhaa-slot-role-repair-batch-20260803.json");

const TAXON_ID = "almas-ukhaa";
const DEASSIGNED_SOURCE = "assets/dinosaurs/almas-ukhaa-ash-apricot-unbanded-pattern-imagegen-v2.png";
const EXPECTED = {
  5: {
    source: "assets/dinosaurs/almas-ukhaa-channel-separated-ceratopsian-context-imagegen-v2.png",
    role: "interaction",
    kind: "anatomy review",
    phenotype: "canonical-a",
  },
  6: {
    source: "assets/dinosaurs/almas-ukhaa-short-deep-skull-postrain-dune-slump-avoidance-imagegen-v3.png",
    role: "social-growth-defense",
    kind: "anatomy review",
    phenotype: "canonical-a",
  },
};

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

const appSource = fs.readFileSync(APP_JS, "utf8");
const samples = vm.runInNewContext(`(${extractLiteral(appSource, "generatedImageSamples")})`, Object.create(null));
const assignmentSandbox = { window: {} };
vm.runInNewContext(fs.readFileSync(ASSIGNMENTS_JS, "utf8"), assignmentSandbox);
const assignments = assignmentSandbox.window.gallerySlotAssignments?.[TAXON_ID] || [];
const decisions = JSON.parse(fs.readFileSync(DECISIONS_JSON, "utf8")).taxa?.[TAXON_ID] || {};
const metadata = JSON.parse(fs.readFileSync(METADATA_JSON, "utf8"));
const candidates = samples[TAXON_ID] || [];
const errors = [];

function candidateFor(source) {
  return candidates.find((item) => (item?.src || item?.source) === source);
}

for (const [slotText, expected] of Object.entries(EXPECTED)) {
  const slot = Number(slotText);
  const assignment = assignments.find((item) => Number(item.gallerySlot) === slot);
  const candidate = candidateFor(expected.source);
  const decision = decisions[slotText];

  if (!assignment) errors.push(`S${slot}: missing assignment`);
  else {
    if (assignment.source !== expected.source) errors.push(`S${slot}: assignment source mismatch`);
    if (assignment.galleryRole !== expected.role) errors.push(`S${slot}: assignment role mismatch`);
    if (assignment.expectedKind !== expected.kind) errors.push(`S${slot}: assignment kind mismatch`);
    if (assignment.phenotype !== expected.phenotype) errors.push(`S${slot}: assignment phenotype mismatch`);
  }

  if (!candidate) errors.push(`S${slot}: missing app candidate`);
  else {
    if (candidate.kind !== expected.kind) errors.push(`S${slot}: candidate kind mismatch`);
    if (!candidate.metadataRecord?.includes("almas-ukhaa-slot-role-repair-batch-20260803.json")) {
      errors.push(`S${slot}: missing metadata record`);
    }
    if (!candidate.sourceAttribution || !candidate.licenseRecord || !candidate.generationPromptRecord
      || !candidate.generationSeed || !candidate.generationWorkflow || !candidate.reviewStatus) {
      errors.push(`S${slot}: incomplete provenance or review fields`);
    }
  }

  if (!decision || decision.status !== "approved") errors.push(`S${slot}: decision is not approved`);
  else {
    if (decision.source !== expected.source) errors.push(`S${slot}: decision source mismatch`);
    if (decision.role !== expected.role) errors.push(`S${slot}: decision role mismatch`);
  }

  if (expected.source.includes(".codex/generated_images")) errors.push(`S${slot}: generator path leaked into assignment`);
  if (!fs.existsSync(path.join(ROOT, expected.source))) errors.push(`S${slot}: approved asset missing`);
}

const deassignedCandidate = candidateFor(DEASSIGNED_SOURCE);
if (!deassignedCandidate) errors.push("former S5 palette candidate missing from diagnostic history");
else {
  if (deassignedCandidate.kind !== "diagnostic only") errors.push("former S5 palette candidate is not diagnostic only");
  if (deassignedCandidate.gallerySlot || deassignedCandidate.galleryRole) {
    errors.push("former S5 palette candidate still declares a fixed slot or role");
  }
}
if (assignments.some((item) => item.source === DEASSIGNED_SOURCE)) {
  errors.push("former S5 palette candidate is still assigned");
}

if (metadata.batchId !== "2026-08-03-almas-slot-role-repair-1") errors.push("metadata batch id mismatch");
if (metadata.records?.["interaction-relocated"]?.gallerySlot !== 5) errors.push("metadata S5 record mismatch");
if (metadata.records?.["social-growth-defense"]?.gallerySlot !== 6) errors.push("metadata S6 record mismatch");
if (metadata.records?.["social-growth-defense"]?.callId !== "exec-1d0bb336-4496-4829-944f-62401289d161") {
  errors.push("metadata S6 generator output id mismatch");
}

const report = {
  taxon: TAXON_ID,
  assignedSlots: assignments.length,
  fixedSlotSources: Object.fromEntries(
    assignments
      .filter((item) => Number(item.gallerySlot) === 5 || Number(item.gallerySlot) === 6)
      .map((item) => [`S${item.gallerySlot}`, item.source]),
  ),
  deassignedPaletteHidden: deassignedCandidate?.kind === "diagnostic only",
  metadataBatchId: metadata.batchId || "",
  errors,
};

console.log(JSON.stringify(report, null, 2));
if (errors.length) process.exitCode = 1;
