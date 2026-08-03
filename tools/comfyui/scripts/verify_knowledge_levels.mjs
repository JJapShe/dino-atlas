import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..", "..");
const APP_JS = path.join(ROOT, "app.js");
const INDEX_HTML = path.join(ROOT, "index.html");
const RUBRIC = path.join(ROOT, "docs", "knowledge-level-rubric.md");
const AUDIT = path.join(ROOT, "docs", "knowledge-level-audit-2026-08-03.md");

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

function fail(message) {
  errors.push(message);
}

const source = fs.readFileSync(APP_JS, "utf8");
const html = fs.readFileSync(INDEX_HTML, "utf8");
const rubric = fs.readFileSync(RUBRIC, "utf8");
const audit = fs.readFileSync(AUDIT, "utf8");
const dinosaurs = vm.runInNewContext(`(${extractLiteral(source, "dinosaurs")})`, Object.create(null), {
  timeout: 5000,
});
const errors = [];
const byId = new Map();
const distribution = { 1: 0, 2: 0, 3: 0, 4: 0 };

for (const dino of dinosaurs) {
  if (!dino?.id) fail("Taxon without id");
  if (byId.has(dino.id)) fail(`Duplicate id: ${dino.id}`);
  byId.set(dino.id, dino);
  if (!Number.isInteger(dino.knowledgeLevel) || !(dino.knowledgeLevel in distribution)) {
    fail(`Invalid level: ${dino.id}=${dino.knowledgeLevel}`);
  } else {
    distribution[dino.knowledgeLevel] += 1;
  }
}

if (dinosaurs.length !== 133) fail(`Expected 133 taxa, found ${dinosaurs.length}`);

const levelSnapshot = dinosaurs
  .map((dino) => `${dino.id}:${dino.knowledgeLevel}`)
  .sort()
  .join("\n");
const levelSnapshotSha256 = createHash("sha256").update(levelSnapshot).digest("hex");
const expectedLevelSnapshotSha256 = "bed270283f81b80c521d16aaff01002e506a984ba78b01317f322978555c5a17";
if (levelSnapshotSha256 !== expectedLevelSnapshotSha256) {
  fail(`Level snapshot hash mismatch: ${levelSnapshotSha256}`);
}

const expectedDistribution = { 1: 19, 2: 27, 3: 39, 4: 48 };
for (const [level, expected] of Object.entries(expectedDistribution)) {
  if (distribution[level] !== expected) {
    fail(`LV${level} expected ${expected}, found ${distribution[level]}`);
  }
}

const expectedLevels = {
  "camptosaurus-dispar": 3,
  "pentaceratops-sternbergii": 3,
  "rhamphorhynchus-muensteri": 3,
  "tapejara-wellnhoferi": 3,
  "stygimoloch-spinifer": 2,
  "saurolophus-angustirostris": 2,
  "monolophosaurus-jiangi": 2,
  "nasutoceratops-titusi": 2,
  "brachiosaurus-altithorax": 1,
  "tarbosaurus-bataar": 1,
  "almas-ukhaa": 4,
};

const previousBoundaryLevels = {
  "camptosaurus-dispar": 2,
  "pentaceratops-sternbergii": 2,
  "rhamphorhynchus-muensteri": 2,
  "tapejara-wellnhoferi": 2,
};
const changedFromPreviousBaseline = Object.entries(previousBoundaryLevels)
  .filter(([id, previous]) => byId.get(id)?.knowledgeLevel !== previous)
  .map(([id]) => id)
  .sort();
if (changedFromPreviousBaseline.length !== 4) {
  fail(`Expected four audited boundary changes, found ${changedFromPreviousBaseline.length}`);
}

for (const [id, expected] of Object.entries(expectedLevels)) {
  const actual = byId.get(id)?.knowledgeLevel;
  if (actual !== expected) fail(`${id} expected LV${expected}, found LV${actual}`);
}

const centrosaurus = byId.get("centrosaurus-apertus");
if (centrosaurus?.koreanName !== "센트로사우루스") {
  fail(`Centrosaurus Korean name mismatch: ${centrosaurus?.koreanName || "missing"}`);
}
if (!centrosaurus?.aliases?.includes("켄트로사우루스")) {
  fail("Centrosaurus legacy Korean search alias is missing");
}
if (!source.includes("...(dino.aliases || [])")) fail("Taxon aliases are not included in catalog search");
if (
  !html.includes('id="levelFilterNote"') ||
  !html.includes('id="levelFilterHelp"') ||
  !html.includes('aria-describedby="levelFilterNote levelFilterHelp"') ||
  !html.includes("읽기 난이도 아님")
) {
  fail("Visible level-filter explanation is missing");
}
const stylesCacheDate = html.match(/styles\.css\?v=(\d{8})-[^"']+/)?.[1] || "";
const appCacheDate = html.match(/app\.js\?v=(\d{8})-[^"']+/)?.[1] || "";
if (stylesCacheDate < "20260803" || appCacheDate < "20260803") {
  fail("Knowledge-level release cache keys are stale");
}
if (!rubric.includes("대상 생물: 133종") || !rubric.includes("LV2 27종 / LV3 39종")) {
  fail("Rubric baseline does not match the audited 133-taxon distribution");
}
if (!audit.includes("변경: 4종") || !audit.includes("최종 분포: LV1 19 / LV2 27 / LV3 39 / LV4 48")) {
  fail("Audit summary does not match the expected decision set");
}

for (const level of [1, 2, 3, 4]) {
  const snapshotMatch = audit.match(new RegExp(`^- LV${level} \\d+종: (.+)$`, "m"));
  if (!snapshotMatch) {
    fail(`Audit LV${level} snapshot line is missing`);
    continue;
  }
  const documentedNames = snapshotMatch[1]
    .replace(/\.$/, "")
    .split(",")
    .map((name) => name.trim())
    .filter(Boolean);
  const expectedNames = dinosaurs
    .filter((dino) => dino.knowledgeLevel === level)
    .map((dino) => dino.koreanName);
  const documentedSet = new Set(documentedNames);
  const expectedSet = new Set(expectedNames);
  const missingNames = expectedNames.filter((name) => !documentedSet.has(name));
  const unexpectedNames = documentedNames.filter((name) => !expectedSet.has(name));
  if (
    documentedNames.length !== expectedNames.length ||
    documentedSet.size !== documentedNames.length ||
    missingNames.length ||
    unexpectedNames.length
  ) {
    fail(
      `Audit LV${level} snapshot mismatch: expected ${expectedNames.length}, documented ${documentedNames.length}, ` +
        `missing [${missingNames.join(", ")}], unexpected [${unexpectedNames.join(", ")}]`,
    );
  }
}

const result = {
  taxa: dinosaurs.length,
  uniqueIds: byId.size,
  distribution,
  levelSnapshotSha256,
  changedFromPreviousBaseline,
  centrosaurusSearchAliases: centrosaurus?.aliases || [],
  errors,
};

console.log(JSON.stringify(result, null, 2));
if (errors.length) process.exitCode = 1;
