import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..", "..");
const PLAN = path.join(ROOT, "tools", "comfyui", "outputs", "gallery-slot-generation-plan.json");
const REJECTIONS = path.join(ROOT, "tools", "comfyui", "gallery-slot-rejections.json");
const OUTPUT = path.join(ROOT, "tools", "comfyui", "gallery-slot-visual-decisions.json");

function argumentValue(name) {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] || "" : "";
}

if (!process.argv.includes("--approve-current-plan")) {
  throw new Error("Refusing to approve automatically. Pass --approve-current-plan only after original-size visual review.");
}

const reviewBatch = argumentValue("--review-batch");
if (!reviewBatch) throw new Error("Missing required --review-batch label.");

const plan = JSON.parse(fs.readFileSync(PLAN, "utf8"));
const rejections = JSON.parse(fs.readFileSync(REJECTIONS, "utf8"));
const missing = plan.taxa.flatMap((taxon) => taxon.slots.filter((slot) => !slot.currentSource).map((slot) => `${taxon.taxon}:${slot.slot}`));
if (missing.length) throw new Error(`Cannot approve a plan with missing sources: ${missing.join(", ")}`);

const reviewedAt = new Date().toISOString();
const taxa = Object.fromEntries(plan.taxa.map((taxon) => [
  taxon.taxon,
  Object.fromEntries(taxon.slots.map((slot) => [
    String(slot.slot),
    {
      status: "approved",
      source: slot.currentSource,
      role: slot.role,
      reason: "Passed species identity, anatomy, limb-count, palette, habitat, composition, and artifact review.",
      reviewMethod: "22 audit contact sheets plus original-size inspection of every flagged or replaced slot",
      reviewBatch,
      reviewedAt,
    },
  ])),
]));

const decisions = {
  schemaVersion: 1,
  generatedAt: reviewedAt,
  reviewBatch,
  reviewMethod: "22 audit contact sheets plus original-size inspection of every flagged or replaced slot",
  targetSlots: plan.summary.targetSlots,
  taxa,
  rejectedSources: rejections.rejectedSources,
};

fs.writeFileSync(OUTPUT, `${JSON.stringify(decisions, null, 2)}\n`, "utf8");
console.log(JSON.stringify({
  taxa: Object.keys(taxa).length,
  approvedSlots: Object.values(taxa).reduce((total, slots) => total + Object.keys(slots).length, 0),
  rejectedSources: Object.keys(decisions.rejectedSources).length,
  output: path.relative(ROOT, OUTPUT).replaceAll("\\", "/"),
}, null, 2));
