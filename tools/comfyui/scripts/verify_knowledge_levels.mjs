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
const EVIDENCE_JSON = path.join(ROOT, "docs", "knowledge-level-evidence-2026-08-03.json");
const EVIDENCE_MARKDOWN = path.join(ROOT, "docs", "knowledge-level-evidence-2026-08-03.md");

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
const evidence = JSON.parse(fs.readFileSync(EVIDENCE_JSON, "utf8"));
const evidenceMarkdown = fs.readFileSync(EVIDENCE_MARKDOWN, "utf8");
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

if (dinosaurs.length !== 145) fail(`Expected 145 taxa, found ${dinosaurs.length}`);

const levelSnapshot = dinosaurs
  .map((dino) => `${dino.id}:${dino.knowledgeLevel}`)
  .sort()
  .join("\n");
const levelSnapshotSha256 = createHash("sha256").update(levelSnapshot).digest("hex");
const expectedLevelSnapshotSha256 = "15c201c6e0764a30314390bc7eef2f577cf1f8a2e304a623c27027b073b7a540";
if (levelSnapshotSha256 !== expectedLevelSnapshotSha256) {
  fail(`Level snapshot hash mismatch: ${levelSnapshotSha256}`);
}

const expectedDistribution = { 1: 25, 2: 33, 3: 39, 4: 48 };
for (const [level, expected] of Object.entries(expectedDistribution)) {
  if (distribution[level] !== expected) {
    fail(`LV${level} expected ${expected}, found ${distribution[level]}`);
  }
}

const expectedEvidenceSignals = {
  1: {
    familiarity: "iconic",
    bookExposure: "cross-channel-recurring",
    namingAccessibility: "immediate",
    catalogStatus: "major-icon",
  },
  2: {
    familiarity: "well-known",
    bookExposure: "recurring",
    namingAccessibility: "recognizable-with-cue",
    catalogStatus: "major-recurring",
  },
  3: {
    familiarity: "interest-led",
    bookExposure: "occasional",
    namingAccessibility: "needs-guidance",
    catalogStatus: "supporting",
  },
  4: {
    familiarity: "specialist",
    bookExposure: "limited",
    namingAccessibility: "specialist-name",
    catalogStatus: "minor-specialist",
  },
};

if (evidence?.schemaVersion !== 1) fail(`Evidence schemaVersion expected 1, found ${evidence?.schemaVersion}`);
if (evidence?.baselineDate !== "2026-08-03") {
  fail(`Evidence baselineDate expected 2026-08-03, found ${evidence?.baselineDate || "missing"}`);
}
if (!Array.isArray(evidence?.limitations) || evidence.limitations.length < 4) {
  fail("Evidence limitations must describe at least four rubric boundaries");
}
if (!Array.isArray(evidence?.taxa)) {
  fail("Evidence taxa must be an array");
} else {
  if (evidence.taxa.length !== dinosaurs.length) {
    fail(`Evidence expected ${dinosaurs.length} rows, found ${evidence.taxa.length}`);
  }

  const evidenceById = new Map();
  for (const row of evidence.taxa) {
    if (!row?.id) {
      fail("Evidence row without id");
      continue;
    }
    if (evidenceById.has(row.id)) fail(`Duplicate evidence id: ${row.id}`);
    evidenceById.set(row.id, row);

    const dino = byId.get(row.id);
    if (!dino) {
      fail(`Evidence id is not in app.js: ${row.id}`);
      continue;
    }
    if (row.knowledgeLevel !== dino.knowledgeLevel) {
      fail(`Evidence level mismatch: ${row.id}=LV${row.knowledgeLevel}, app.js=LV${dino.knowledgeLevel}`);
    }
    if (row.scientificName !== dino.name) {
      fail(`Evidence scientific name mismatch: ${row.id}`);
    }
    if (row.koreanName !== dino.koreanName) {
      fail(`Evidence Korean name mismatch: ${row.id}`);
    }
    if (!Number.isInteger(row.order) || row.order < 1 || row.order > dinosaurs.length) {
      fail(`Evidence order is invalid: ${row.id}=${row.order}`);
    }
    if (typeof row.editorialCue !== "string" || row.editorialCue.trim().length < 8) {
      fail(`Evidence editorial cue is missing or too short: ${row.id}`);
    }
    if (typeof row.rationale !== "string" || row.rationale.trim().length < 30) {
      fail(`Evidence rationale is missing or too short: ${row.id}`);
    }
    if (!row.rationale?.includes(row.koreanName) || !row.rationale?.includes(`LV${row.knowledgeLevel}`)) {
      fail(`Evidence rationale must identify the taxon and level: ${row.id}`);
    }

    const expectedSignals = expectedEvidenceSignals[dino.knowledgeLevel];
    if (!row.signals || typeof row.signals !== "object") {
      fail(`Evidence signals are missing: ${row.id}`);
    } else {
      for (const [signal, expected] of Object.entries(expectedSignals)) {
        if (typeof row.signals[signal] !== "string" || !row.signals[signal].trim()) {
          fail(`Evidence signal is empty: ${row.id}.${signal}`);
        } else if (row.signals[signal] !== expected) {
          fail(`Evidence signal mismatch: ${row.id}.${signal}=${row.signals[signal]}, expected ${expected}`);
        }
      }
    }
  }

  for (const dino of dinosaurs) {
    if (!evidenceById.has(dino.id)) fail(`Missing evidence id: ${dino.id}`);
  }

  const evidenceOrders = evidence.taxa.map((row) => row.order);
  if (new Set(evidenceOrders).size !== dinosaurs.length) fail("Evidence order values must be unique");
  if (new Set(evidence.taxa.map((row) => row.editorialCue)).size !== dinosaurs.length) {
    fail("Every evidence row must have a taxon-specific editorial cue");
  }
  if (new Set(evidence.taxa.map((row) => row.rationale)).size !== dinosaurs.length) {
    fail("Every evidence row must have a taxon-specific rationale");
  }
  const expectedOrderIds = dinosaurs.map((dino) => dino.id);
  const evidenceOrderIds = [...evidence.taxa]
    .sort((a, b) => a.order - b.order)
    .map((row) => row.id);
  if (evidenceOrderIds.some((id, index) => id !== expectedOrderIds[index])) {
    fail("Evidence rows do not preserve app.js taxon order");
  }

  const markdownIds = [...evidenceMarkdown.matchAll(/<code>([^<]+)<\/code>/g)].map((match) => match[1]);
  if (markdownIds.length !== dinosaurs.length || new Set(markdownIds).size !== dinosaurs.length) {
    fail(`Evidence Markdown expected ${dinosaurs.length} unique id rows, found ${markdownIds.length}`);
  }
  for (const dino of dinosaurs) {
    if (!markdownIds.includes(dino.id)) fail(`Evidence Markdown is missing id: ${dino.id}`);
  }
}

const expectedLevels = {
  "camptosaurus-dispar": 3,
  "maiasaura-peeblesorum": 2,
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
  "carnotaurus-sastrei": 1,
  "carcharodontosaurus-saharicus": 2,
  "giganotosaurus-carolinii": 1,
  "iguanodon-bernissartensis": 1,
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
if (!rubric.includes("대상 생물: 145종") || !rubric.includes("LV1 25종 / LV2 33종 / LV3 39종 / LV4 48종")) {
  fail("Rubric baseline does not match the audited 145-taxon distribution");
}
if (
  !rubric.includes("knowledge-level-evidence-2026-08-03.md") ||
  !rubric.includes("knowledge-level-evidence-2026-08-03.json")
) {
  fail("Rubric does not link to both per-taxon evidence artifacts");
}
if (
  !audit.includes("변경: 기존 4종 재분류를 보존하고, 138종 기준선 이후 친숙 고생물 7종 신규 수록") ||
  !audit.includes("최종 분포: LV1 25 / LV2 33 / LV3 39 / LV4 48")
) {
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
  evidenceRows: Array.isArray(evidence?.taxa) ? evidence.taxa.length : 0,
  evidenceUniqueCues: Array.isArray(evidence?.taxa)
    ? new Set(evidence.taxa.map((row) => row.editorialCue)).size
    : 0,
  centrosaurusSearchAliases: centrosaurus?.aliases || [],
  errors,
};

console.log(JSON.stringify(result, null, 2));
if (errors.length) process.exitCode = 1;
