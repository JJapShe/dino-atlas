import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..", "..");
const CATALOG_JS = path.join(ROOT, "ecosystem-scenes.js");
const DECISIONS_JSON = path.join(ROOT, "tools", "comfyui", "ecosystem-scene-decisions.json");
const APP_JS = path.join(ROOT, "app.js");
const REQUIRED_TIME_BINS = [
  "late-triassic",
  "early-jurassic",
  "middle-jurassic",
  "late-jurassic",
  "early-cretaceous",
  "late-cretaceous",
];
const SCENE_TYPES = new Set([
  "coexistence",
  "predation-tension",
  "herd-growth",
  "environment-event",
  "trace-evidence",
]);
const SUPPORT_STATUSES = new Set(["supported", "pending", "blocked"]);
const errors = [];
const jsonCache = new Map();

function fail(message) {
  errors.push(message);
}

function isNonEmptyString(value) {
  return typeof value === "string" && value.trim().length > 0;
}

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
    if (char === "\"" || char === "'" || char === "`") {
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

function readPngDimensions(filePath) {
  const header = Buffer.alloc(24);
  const handle = fs.openSync(filePath, "r");
  try {
    const bytesRead = fs.readSync(handle, header, 0, header.length, 0);
    if (bytesRead !== header.length || header.toString("hex", 0, 8) !== "89504e470d0a1a0a") {
      throw new Error("not a PNG file");
    }
    return { width: header.readUInt32BE(16), height: header.readUInt32BE(20) };
  } finally {
    fs.closeSync(handle);
  }
}

function loadJson(filePath) {
  if (!jsonCache.has(filePath)) {
    jsonCache.set(filePath, JSON.parse(fs.readFileSync(filePath, "utf8")));
  }
  return jsonCache.get(filePath);
}

function resolveJsonReference(reference, owner) {
  if (!isNonEmptyString(reference) || !reference.includes("#")) {
    fail(`${owner}: invalid JSON record reference`);
    return null;
  }
  if (/\.codex[\\/]/i.test(reference)) {
    fail(`${owner}: generator-area path is prohibited`);
    return null;
  }

  const [relativePath, fragment = ""] = reference.split("#", 2);
  const absolutePath = path.resolve(ROOT, relativePath);
  const relativeCheck = path.relative(ROOT, absolutePath);
  if (relativeCheck.startsWith("..") || path.isAbsolute(relativeCheck)) {
    fail(`${owner}: metadata reference escapes project root`);
    return null;
  }
  if (!fs.existsSync(absolutePath)) {
    fail(`${owner}: missing metadata file ${relativePath}`);
    return null;
  }

  let root;
  try {
    root = loadJson(absolutePath);
  } catch (error) {
    fail(`${owner}: invalid metadata JSON ${relativePath}: ${error.message}`);
    return null;
  }

  let value = root;
  const segments = fragment.split("/").filter(Boolean).map(decodeURIComponent);
  for (const segment of segments) {
    if (value === null || typeof value !== "object" || !(segment in value)) {
      fail(`${owner}: unresolved metadata fragment #${fragment}`);
      return null;
    }
    value = value[segment];
  }
  return { root, value, absolutePath, relativePath, fragment };
}

const catalogSource = fs.readFileSync(CATALOG_JS, "utf8");
const decisionsSource = fs.readFileSync(DECISIONS_JSON, "utf8");
const sandbox = { window: {} };
new vm.Script(catalogSource, { filename: CATALOG_JS }).runInNewContext(sandbox);
const catalog = sandbox.window.ecosystemSceneCatalog;
const decisions = JSON.parse(decisionsSource);

if (!catalog || typeof catalog !== "object") throw new Error("ecosystemSceneCatalog was not exported");
if (/\.codex[\\/]generated_images/i.test(catalogSource)) fail("catalog: generator-area path leak");
if (/\.codex[\\/]generated_images/i.test(decisionsSource)) fail("decisions: generator-area path leak");

const appSource = fs.readFileSync(APP_JS, "utf8");
const dinosaurs = vm.runInNewContext(`(${extractLiteral(appSource, "dinosaurs")})`, Object.create(null));
const taxonNames = new Map(dinosaurs.map((item) => [item.id, item.name]));

if (catalog.schemaVersion !== 1) fail("catalog: schemaVersion must be 1");
if (decisions.schemaVersion !== 1) fail("decisions: schemaVersion must be 1");
if (!Array.isArray(catalog.timeBins)) fail("catalog: timeBins must be an array");
if (!Array.isArray(catalog.scenes)) fail("catalog: scenes must be an array");
const catalogSceneTypeIds = Array.isArray(catalog.sceneTypes)
  ? catalog.sceneTypes.map((item) => item?.id)
  : [];
if (JSON.stringify(catalogSceneTypeIds) !== JSON.stringify([...SCENE_TYPES])) {
  fail("catalog: sceneTypes must match the verifier scene-type order");
}

const timeBins = Array.isArray(catalog.timeBins) ? catalog.timeBins : [];
const scenes = Array.isArray(catalog.scenes) ? catalog.scenes : [];
const timeBinIds = timeBins.map((item) => item.id);
if (JSON.stringify(timeBinIds) !== JSON.stringify(REQUIRED_TIME_BINS)) {
  fail(`catalog: timeBins must be ordered as ${REQUIRED_TIME_BINS.join(", ")}`);
}

const timeBinById = new Map();
for (const timeBin of timeBins) {
  if (!isNonEmptyString(timeBin.id) || timeBinById.has(timeBin.id)) {
    fail(`timeBin: missing or duplicate id ${timeBin.id || "(blank)"}`);
    continue;
  }
  timeBinById.set(timeBin.id, timeBin);
  if (!isNonEmptyString(timeBin.label) || !isNonEmptyString(timeBin.era)) {
    fail(`${timeBin.id}: incomplete label or era`);
  }
  if (!Number.isFinite(timeBin.ageRangeMa?.older)
    || !Number.isFinite(timeBin.ageRangeMa?.younger)
    || timeBin.ageRangeMa.older <= timeBin.ageRangeMa.younger) {
    fail(`${timeBin.id}: invalid ageRangeMa`);
  }
  if (!Array.isArray(timeBin.sceneIds)) fail(`${timeBin.id}: sceneIds must be an array`);
}

const sceneById = new Map();
const compositionKeys = new Set();
const compositionFamilies = new Set();
const compositionSignatures = new Set();
const publicationEligibility = [];
let verifiedAssets = 0;
let verifiedMetadataRecords = 0;

for (const scene of scenes) {
  const owner = scene?.id || "scene:(blank)";
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(scene?.id || "")) {
    fail(`${owner}: invalid id`);
    continue;
  }
  if (sceneById.has(scene.id)) fail(`${owner}: duplicate id`);
  sceneById.set(scene.id, scene);

  if (!SCENE_TYPES.has(scene.sceneType)) fail(`${owner}: invalid sceneType ${scene.sceneType}`);
  if (!isNonEmptyString(scene.title) || !isNonEmptyString(scene.summary)) {
    fail(`${owner}: title and summary are required`);
  }

  const timeBin = timeBinById.get(scene.timeBinId);
  if (!timeBin) {
    fail(`${owner}: unknown timeBinId ${scene.timeBinId}`);
  }

  const asset = scene.asset || {};
  if (!/^assets\/dinosaurs\/[a-z0-9][a-z0-9.-]*\.png$/i.test(asset.src || "")) {
    fail(`${owner}: asset must be a project PNG under assets/dinosaurs`);
  } else {
    const assetPath = path.join(ROOT, asset.src);
    if (!fs.existsSync(assetPath)) {
      fail(`${owner}: missing asset ${asset.src}`);
    } else {
      const stat = fs.statSync(assetPath);
      const dimensions = readPngDimensions(assetPath);
      if (stat.size !== asset.bytes) fail(`${owner}: asset byte count mismatch`);
      if (sha256(assetPath) !== String(asset.sha256 || "").toLowerCase()) fail(`${owner}: asset sha256 mismatch`);
      if (dimensions.width !== asset.width || dimensions.height !== asset.height) {
        fail(`${owner}: asset dimensions mismatch`);
      }
      const actualOrientation = dimensions.width > dimensions.height ? "landscape" : dimensions.width < dimensions.height ? "portrait" : "square";
      if (asset.orientation !== actualOrientation) fail(`${owner}: asset orientation mismatch`);
      verifiedAssets += 1;
    }
  }

  const formation = scene.formation || {};
  if (!isNonEmptyString(formation.name) || !isNonEmptyString(formation.context)
    || !isNonEmptyString(formation.resolution)) {
    fail(`${owner}: formation name, context, and resolution are required`);
  }
  const older = formation.ageRangeMa?.older;
  const younger = formation.ageRangeMa?.younger;
  if (!Number.isFinite(older) || !Number.isFinite(younger) || older <= younger) {
    fail(`${owner}: invalid formation age range`);
  } else if (timeBin && (older > timeBin.ageRangeMa.older || younger < timeBin.ageRangeMa.younger)) {
    fail(`${owner}: formation age range falls outside ${timeBin.id}`);
  }

  if (!Array.isArray(scene.participants) || scene.participants.length < 1) {
    fail(`${owner}: at least one participant is required`);
  } else {
    const participantIds = new Set();
    for (const participant of scene.participants) {
      if (participantIds.has(participant.taxonId)) fail(`${owner}: duplicate participant ${participant.taxonId}`);
      participantIds.add(participant.taxonId);
      const currentName = taxonNames.get(participant.taxonId);
      if (!currentName) fail(`${owner}: unknown taxon id ${participant.taxonId}`);
      else if (currentName !== participant.scientificName) {
        fail(`${owner}: scientific name mismatch for ${participant.taxonId}`);
      }
      if (!isNonEmptyString(participant.role) || !isNonEmptyString(participant.certainty)) {
        fail(`${owner}: participant role and certainty are required`);
      }
    }
  }

  const composition = scene.composition || {};
  if (!isNonEmptyString(scene.compositionKey) || !isNonEmptyString(scene.compositionLabel)
    || scene.compositionKey !== composition.key || scene.compositionLabel !== composition.label) {
    fail(`${owner}: composition aliases and nested composition must match`);
  }
  if (compositionKeys.has(composition.key)) fail(`${owner}: duplicate composition key ${composition.key}`);
  compositionKeys.add(composition.key);
  if (!isNonEmptyString(composition.family)) fail(`${owner}: composition family is required`);
  if (compositionFamilies.has(composition.family)) fail(`${owner}: duplicate composition family ${composition.family}`);
  compositionFamilies.add(composition.family);
  if (composition.orientation !== asset.orientation || !isNonEmptyString(composition.camera)
    || !isNonEmptyString(composition.spatialLayout)) {
    fail(`${owner}: incomplete composition geometry`);
  }
  if (!Array.isArray(composition.diversityTags) || composition.diversityTags.length < 3) {
    fail(`${owner}: at least three composition diversity tags are required`);
  }
  const compositionSignature = [composition.orientation, composition.camera, composition.spatialLayout].join("|");
  if (compositionSignatures.has(compositionSignature)) fail(`${owner}: duplicate camera/spatial composition signature`);
  compositionSignatures.add(compositionSignature);

  if (!Array.isArray(scene.epistemic?.known) || scene.epistemic.known.length < 1
    || !Array.isArray(scene.epistemic?.reconstructed) || scene.epistemic.reconstructed.length < 1
    || !isNonEmptyString(scene.epistemic?.boundary)) {
    fail(`${owner}: known/reconstructed/boundary metadata is incomplete`);
  }
  if (scene.sceneType === "trace-evidence") {
    const traceEvidence = scene.traceEvidence || {};
    for (const field of ["bodiesShown", "exactTaxonClaim", "simultaneousCrossingClaim", "interactionClaim"]) {
      if (traceEvidence[field] !== false) fail(`${owner}: traceEvidence.${field} must be false`);
    }
  }
  if (!Array.isArray(scene.evidence) || scene.evidence.length < 1) {
    fail(`${owner}: evidence is required`);
  } else {
    for (const evidence of scene.evidence) {
      if (!/^https:\/\//.test(evidence.url || "") || !isNonEmptyString(evidence.use)) {
        fail(`${owner}: invalid evidence entry`);
      }
    }
  }

  const provenance = scene.provenance || {};
  for (const field of ["sourceAttribution", "license", "metadataRecord", "promptRecord", "prompt", "seed", "workflow", "generator"]) {
    if (!isNonEmptyString(provenance[field])) fail(`${owner}: missing provenance.${field}`);
  }
  if (provenance.prompt !== provenance.promptRecord) {
    fail(`${owner}: provenance.prompt must point to the exact prompt record`);
  }

  const metadataResult = resolveJsonReference(provenance.metadataRecord, `${owner}: metadataRecord`);
  const promptResult = resolveJsonReference(provenance.promptRecord, `${owner}: promptRecord`);
  if (provenance.correctionPromptRecord) {
    const correctionResult = resolveJsonReference(provenance.correctionPromptRecord, `${owner}: correctionPromptRecord`);
    if (correctionResult && !(isNonEmptyString(correctionResult.value) || (Array.isArray(correctionResult.value) && correctionResult.value.length))) {
      fail(`${owner}: correction prompt record is empty`);
    }
  }
  if (promptResult && !(isNonEmptyString(promptResult.value) || (Array.isArray(promptResult.value) && promptResult.value.length))) {
    fail(`${owner}: prompt record is empty`);
  }
  if (metadataResult) {
    const record = metadataResult.value;
    const metadataAsset = record?.projectAsset || record?.approvedProjectCopy || record?.approvedProjectPath;
    if (metadataAsset !== asset.src) fail(`${owner}: metadata asset path mismatch`);
    const metadataSeed = record?.seed || metadataResult.root?.workflow?.seed;
    const metadataGenerator = record?.generator || metadataResult.root?.workflow?.generator;
    if (metadataSeed !== provenance.seed) fail(`${owner}: seed provenance mismatch`);
    if (metadataGenerator !== provenance.generator) fail(`${owner}: generator provenance mismatch`);
    if (!metadataResult.root?.copyrightSafety) fail(`${owner}: source copyright-safety record missing`);
    const reviewText = JSON.stringify(record?.review || "").toLowerCase();
    if (!/(approved|passed)/.test(reviewText)) fail(`${owner}: source anatomy review is not supported`);
    const metadataText = JSON.stringify(metadataResult.root);
    for (const evidence of scene.evidence || []) {
      if (!metadataText.includes(evidence.url)) fail(`${owner}: evidence URL is absent from source metadata: ${evidence.url}`);
    }
    verifiedMetadataRecords += 1;
  }

  if (scene.representativeEligible !== false) fail(`${owner}: representativeEligible must be false`);
  for (const gateName of ["anatomy", "ecology", "responsive"]) {
    if (!SUPPORT_STATUSES.has(scene.gates?.[gateName]?.status)) fail(`${owner}: invalid ${gateName} gate status`);
    if (!isNonEmptyString(scene.gates?.[gateName]?.note)) fail(`${owner}: ${gateName} gate note is required`);
  }
  if (!new Set(["draft", "published", "blocked"]).has(scene.gates?.publication?.status)
    || !isNonEmptyString(scene.gates?.publication?.note)) {
    fail(`${owner}: invalid publication gate`);
  }
  const eligible = ["anatomy", "ecology", "responsive"].every(
    (gateName) => scene.gates?.[gateName]?.status === "supported",
  );
  const unmetGates = ["anatomy", "ecology", "responsive"].filter(
    (gateName) => scene.gates?.[gateName]?.status !== "supported",
  );
  if (scene.publication?.eligible !== eligible) fail(`${owner}: publication eligibility is stale`);
  if (scene.publication?.status !== scene.gates?.publication?.status) fail(`${owner}: publication status mismatch`);
  if (scene.publication?.status === "published" && !eligible) fail(`${owner}: published without all required gates`);
  publicationEligibility.push({ id: scene.id, eligible, status: scene.publication?.status, unmetGates });

  const decision = decisions.scenes?.[scene.id];
  if (!decision) {
    fail(`${owner}: missing ecosystem decision`);
  } else {
    if (decision.asset !== asset.src) fail(`${owner}: decision asset mismatch`);
    if (decision.compositionKey !== composition.key) fail(`${owner}: decision composition mismatch`);
    if (decision.representativeEligible !== false) fail(`${owner}: decision representative gate mismatch`);
    for (const gateName of ["anatomy", "ecology", "responsive", "publication"]) {
      if (decision.gates?.[gateName]?.status !== scene.gates?.[gateName]?.status) {
        fail(`${owner}: decision ${gateName} gate mismatch`);
      }
      const evidenceRef = decision.gates?.[gateName]?.evidence;
      if ((gateName === "anatomy" || gateName === "ecology") && !resolveJsonReference(evidenceRef, `${owner}: decision ${gateName}`)) {
        // resolveJsonReference records the specific failure.
      }
    }
    if (decision.publication?.status !== scene.publication?.status
      || decision.publication?.eligible !== scene.publication?.eligible) {
      fail(`${owner}: decision publication mismatch`);
    }
  }
}

const mappedScenes = new Map();
for (const timeBin of timeBins) {
  for (const sceneId of timeBin.sceneIds || []) {
    mappedScenes.set(sceneId, (mappedScenes.get(sceneId) || 0) + 1);
    const scene = sceneById.get(sceneId);
    if (!scene) fail(`${timeBin.id}: unknown scene id ${sceneId}`);
    else if (scene.timeBinId !== timeBin.id) fail(`${sceneId}: timeBin mapping mismatch`);
  }
}
for (const scene of scenes) {
  if (mappedScenes.get(scene.id) !== 1) fail(`${scene.id}: must appear in exactly one timeBin sceneIds list`);
}

const decisionIds = Object.keys(decisions.scenes || {});
for (const decisionId of decisionIds) {
  if (!sceneById.has(decisionId)) fail(`decisions: orphan scene ${decisionId}`);
}
if (decisionIds.length !== scenes.length) fail("decisions: scene count mismatch");
if (decisions.policy?.catalogDraftAllowedWhenResponsivePending !== true) {
  fail("decisions: catalog draft must be allowed while responsive QA is pending");
}
if (JSON.stringify(decisions.policy?.publishedRequires) !== JSON.stringify(["anatomy", "ecology", "responsive"])) {
  fail("decisions: publishedRequires must be anatomy, ecology, responsive");
}
if (decisions.policy?.representativePromotion !== "prohibited") {
  fail("decisions: representative promotion must be prohibited");
}
if (decisions.policy?.compositionDiversity?.uniqueCompositionKeyRequired !== true
  || decisions.policy?.compositionDiversity?.uniqueCompositionFamilyRequired !== true
  || decisions.policy?.compositionDiversity?.uniqueCameraSpatialSignatureRequired !== true) {
  fail("decisions: composition diversity gates are incomplete");
}

const sceneTypeCounts = Object.fromEntries([...SCENE_TYPES].map((type) => [
  type,
  scenes.filter((scene) => scene.sceneType === type).length,
]));
const report = {
  schemaVersion: catalog.schemaVersion,
  timeBins: timeBins.map((timeBin) => ({ id: timeBin.id, scenes: timeBin.sceneIds?.length || 0 })),
  sceneCount: scenes.length,
  sceneTypeCounts,
  verifiedAssets,
  verifiedMetadataRecords,
  composition: {
    uniqueKeys: compositionKeys.size,
    uniqueFamilies: compositionFamilies.size,
    uniqueCameraSpatialSignatures: compositionSignatures.size,
    keys: [...compositionKeys],
    families: [...compositionFamilies],
  },
  publication: {
    draftAllowedWithResponsivePending: decisions.policy?.catalogDraftAllowedWhenResponsivePending === true,
    eligibleCount: publicationEligibility.filter((item) => item.eligible).length,
    draftCount: publicationEligibility.filter((item) => item.status === "draft").length,
    eligibility: publicationEligibility,
  },
  errors,
};

console.log(JSON.stringify(report, null, 2));
if (errors.length) process.exitCode = 1;
