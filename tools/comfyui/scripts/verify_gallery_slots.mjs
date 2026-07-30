import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..", "..");
const APP_JS = path.join(ROOT, "app.js");
const ASSIGNMENTS_JS = path.join(ROOT, "gallery-slots.js");
const ASSET_ROOT = path.join(ROOT, "assets", "dinosaurs");
const OUTPUT = path.join(ROOT, "tools", "comfyui", "outputs", "gallery-slot-validation.json");
const DECISIONS_JSON = path.join(ROOT, "tools", "comfyui", "gallery-slot-visual-decisions.json");
const REJECTIONS_JSON = path.join(ROOT, "tools", "comfyui", "gallery-slot-rejections.json");

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

function loadLiteral(source, name) {
  return vm.runInNewContext(`(${extractLiteral(source, name)})`, Object.create(null), { timeout: 5000 });
}

function loadAssignments() {
  const sandbox = { window: {} };
  vm.runInNewContext(fs.readFileSync(ASSIGNMENTS_JS, "utf8"), sandbox, { timeout: 5000 });
  return sandbox.window.gallerySlotAssignments || {};
}

function itemSource(item) {
  return String(item?.src || item?.source || "").replaceAll("\\", "/");
}

const app = fs.readFileSync(APP_JS, "utf8");
const dinosaurs = loadLiteral(app, "dinosaurs");
const samples = loadLiteral(app, "generatedImageSamples");
const assignments = loadAssignments();
const decisions = fs.existsSync(DECISIONS_JSON)
  ? JSON.parse(fs.readFileSync(DECISIONS_JSON, "utf8"))
  : { taxa: {}, rejectedSources: {} };
const rejectionManifest = fs.existsSync(REJECTIONS_JSON)
  ? JSON.parse(fs.readFileSync(REJECTIONS_JSON, "utf8"))
  : { rejectedSources: {} };
const rejectedSources = new Set([
  ...Object.keys(decisions.rejectedSources || {}),
  ...Object.keys(rejectionManifest.rejectedSources || {}),
].map((source) => String(source).replaceAll("\\", "/")));
const missingSlots = [];
const duplicateSlots = [];
const outOfRangeSlots = [];
const missingCandidates = [];
const missingAssets = [];
const wrongRepresentativeKinds = [];
const pendingVisualReview = [];
const visualDecisionMismatches = [];
const rejectedSelections = [];
const orphanAssignments = Object.keys(assignments).filter((id) => !dinosaurs.some((dino) => dino.id === id));
const orphanDecisionTaxa = Object.keys(decisions.taxa || {}).filter((id) => !dinosaurs.some((dino) => dino.id === id));

for (const dino of dinosaurs) {
  const taxonAssignments = assignments[dino.id] || [];
  const candidateSources = new Map((samples[dino.id] || []).filter((item) => item && typeof item === "object").map((item) => [itemSource(item), item]));
  const slots = new Map();

  for (const assignment of taxonAssignments) {
    const slot = Number(assignment.gallerySlot);
    if (!Number.isInteger(slot) || slot < 1 || slot > dino.imageSlots) {
      outOfRangeSlots.push({ taxon: dino.id, slot: assignment.gallerySlot, source: assignment.source || "" });
      continue;
    }
    if (slots.has(slot)) {
      duplicateSlots.push({ taxon: dino.id, slot, sources: [slots.get(slot).source, assignment.source] });
      continue;
    }
    slots.set(slot, assignment);

    const normalizedAssignmentSource = String(assignment.source || "").replaceAll("\\", "/");
    if (rejectedSources.has(normalizedAssignmentSource)) {
      rejectedSelections.push({ taxon: dino.id, slot, source: normalizedAssignmentSource });
    }

    const candidate = candidateSources.get(String(assignment.source || ""));
    if (!candidate) {
      missingCandidates.push({ taxon: dino.id, slot, source: assignment.source || "" });
      continue;
    }
    const asset = path.join(ROOT, String(assignment.source || ""));
    if (!String(assignment.source || "").startsWith("assets/dinosaurs/") || !fs.existsSync(asset)) {
      missingAssets.push({ taxon: dino.id, slot, source: assignment.source || "" });
    }
    if (slot === 1 && candidate.kind !== "count-level pass") {
      wrongRepresentativeKinds.push({ taxon: dino.id, source: assignment.source || "", kind: candidate.kind || "" });
    }
  }

  for (let slot = 1; slot <= dino.imageSlots; slot += 1) {
    if (!slots.has(slot)) missingSlots.push({ taxon: dino.id, slot });
    const decision = decisions.taxa?.[dino.id]?.[String(slot)];
    if (decision?.status !== "approved") {
      pendingVisualReview.push({ taxon: dino.id, slot, status: decision?.status || "missing" });
      continue;
    }
    const assignedSource = String(slots.get(slot)?.source || "").replaceAll("\\", "/");
    const approvedSource = String(decision.source || "").replaceAll("\\", "/");
    if (!approvedSource || assignedSource !== approvedSource) {
      visualDecisionMismatches.push({ taxon: dino.id, slot, assignedSource, approvedSource });
    }
  }
}

const report = {
  generatedAt: new Date().toISOString(),
  summary: {
    taxa: dinosaurs.length,
    targetSlots: dinosaurs.reduce((total, dino) => total + dino.imageSlots, 0),
    assignedSlots: dinosaurs.reduce((total, dino) => total + (assignments[dino.id] || []).length, 0),
    approvedSlots: dinosaurs.reduce((total, dino) => total + Object.values(decisions.taxa?.[dino.id] || {}).filter((decision) => decision.status === "approved").length, 0),
    missingSlots: missingSlots.length,
    duplicateSlots: duplicateSlots.length,
    outOfRangeSlots: outOfRangeSlots.length,
    missingCandidates: missingCandidates.length,
    missingAssets: missingAssets.length,
    wrongRepresentativeKinds: wrongRepresentativeKinds.length,
    pendingVisualReview: pendingVisualReview.length,
    visualDecisionMismatches: visualDecisionMismatches.length,
    rejectedSelections: rejectedSelections.length,
    orphanAssignments: orphanAssignments.length,
    orphanDecisionTaxa: orphanDecisionTaxa.length,
  },
  missingSlots,
  duplicateSlots,
  outOfRangeSlots,
  missingCandidates,
  missingAssets,
  wrongRepresentativeKinds,
  pendingVisualReview,
  visualDecisionMismatches,
  rejectedSelections,
  orphanAssignments,
  orphanDecisionTaxa,
};

fs.mkdirSync(path.dirname(OUTPUT), { recursive: true });
fs.writeFileSync(OUTPUT, `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify(report.summary, null, 2));

if (process.argv.includes("--strict")) {
  const expected = report.summary.targetSlots;
  const failures = report.summary.assignedSlots !== expected
    || report.summary.approvedSlots !== expected
    || [
      "missingSlots",
      "duplicateSlots",
      "outOfRangeSlots",
      "missingCandidates",
      "missingAssets",
      "wrongRepresentativeKinds",
      "pendingVisualReview",
      "visualDecisionMismatches",
      "rejectedSelections",
      "orphanAssignments",
      "orphanDecisionTaxa",
    ].some((key) => report.summary[key] > 0);
  if (failures) process.exitCode = 1;
}
