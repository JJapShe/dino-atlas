const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const sharp = require("sharp");

const ROOT = path.resolve(__dirname, "..", "..", "..");
const APP_JS = path.join(ROOT, "app.js");
const ASSIGNMENTS_JS = path.join(ROOT, "gallery-slots.js");
const SIZE = 64;

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

function correlation(left, right) {
  let leftMean = 0;
  let rightMean = 0;
  for (let i = 0; i < left.length; i += 1) {
    leftMean += left[i];
    rightMean += right[i];
  }
  leftMean /= left.length;
  rightMean /= right.length;
  let numerator = 0;
  let leftVariance = 0;
  let rightVariance = 0;
  for (let i = 0; i < left.length; i += 1) {
    const a = left[i] - leftMean;
    const b = right[i] - rightMean;
    numerator += a * b;
    leftVariance += a * a;
    rightVariance += b * b;
  }
  const denominator = Math.sqrt(leftVariance * rightVariance);
  return denominator > 0 ? numerator / denominator : 0;
}

function meanAbsoluteSimilarity(left, right) {
  let difference = 0;
  for (let i = 0; i < left.length; i += 1) difference += Math.abs(left[i] - right[i]);
  return 1 - difference / left.length / 255;
}

function horizontalFlip(values) {
  const flipped = new Float32Array(values.length);
  for (let y = 0; y < SIZE; y += 1) {
    for (let x = 0; x < SIZE; x += 1) flipped[y * SIZE + x] = values[y * SIZE + (SIZE - 1 - x)];
  }
  return flipped;
}

function sobel(values) {
  const edges = new Float32Array(values.length);
  for (let y = 1; y < SIZE - 1; y += 1) {
    for (let x = 1; x < SIZE - 1; x += 1) {
      const at = (dx, dy) => values[(y + dy) * SIZE + (x + dx)];
      const gx = -at(-1, -1) + at(1, -1) - 2 * at(-1, 0) + 2 * at(1, 0) - at(-1, 1) + at(1, 1);
      const gy = -at(-1, -1) - 2 * at(0, -1) - at(1, -1) + at(-1, 1) + 2 * at(0, 1) + at(1, 1);
      edges[y * SIZE + x] = Math.min(255, Math.sqrt(gx * gx + gy * gy));
    }
  }
  return edges;
}

async function imageFeatures(source) {
  const filePath = path.join(ROOT, source);
  const { data, info } = await sharp(filePath)
    .rotate()
    .resize(SIZE, SIZE, { fit: "fill" })
    .removeAlpha()
    .raw()
    .toBuffer({ resolveWithObject: true });
  const gray = new Float32Array(SIZE * SIZE);
  const meanRgb = [0, 0, 0];
  for (let pixel = 0; pixel < SIZE * SIZE; pixel += 1) {
    const offset = pixel * info.channels;
    const red = data[offset];
    const green = data[offset + 1];
    const blue = data[offset + 2];
    gray[pixel] = red * 0.299 + green * 0.587 + blue * 0.114;
    meanRgb[0] += red;
    meanRgb[1] += green;
    meanRgb[2] += blue;
  }
  for (let channel = 0; channel < 3; channel += 1) meanRgb[channel] /= SIZE * SIZE;
  return { gray, edge: sobel(gray), meanRgb };
}

function round(value) {
  return Math.round(value * 1000) / 1000;
}

function structuralScores(left, right) {
  const directGray = correlation(left.gray, right.gray);
  const directEdge = correlation(left.edge, right.edge);
  const directMae = meanAbsoluteSimilarity(left.gray, right.gray);
  const flippedGray = horizontalFlip(right.gray);
  const flippedEdge = horizontalFlip(right.edge);
  const mirrorGray = correlation(left.gray, flippedGray);
  const mirrorEdge = correlation(left.edge, flippedEdge);
  const mirrorMae = meanAbsoluteSimilarity(left.gray, flippedGray);
  const direct = directGray * 0.35 + directEdge * 0.45 + directMae * 0.2;
  const mirrored = mirrorGray * 0.35 + mirrorEdge * 0.45 + mirrorMae * 0.2;
  const colorMeanDistance = Math.sqrt(
    left.meanRgb.reduce((sum, value, index) => sum + (value - right.meanRgb[index]) ** 2, 0),
  );
  return {
    direct: round(direct),
    mirrored: round(mirrored),
    structuralSimilarity: round(Math.max(direct, mirrored)),
    matchMode: mirrored > direct ? "mirrored" : "direct",
    grayCorrelation: round(directGray),
    edgeCorrelation: round(directEdge),
    graySimilarity: round(directMae),
    colorMeanDistance: round(colorMeanDistance),
  };
}

async function main() {
  if (process.argv.includes("--help")) {
    console.log([
      "Usage: node audit_gallery_composition_similarity.cjs [options]",
      "  --representative-pattern-only  compare only slot 1 versus slot 2",
      "  --taxon=<id>                   limit the audit to one taxon",
      "  --threshold=<0..1>             minimum reported structural score (default 0.45)",
      "  --fail-above=<0..1>            exit 1 when any in-scope pair reaches this score",
      "  --top=<count>                   maximum ranked results (default 40)",
      "",
      "structuralSimilarity is the larger of direct and horizontally mirrored grayscale/edge scores.",
    ].join("\n"));
    return;
  }
  const threshold = Number(process.argv.find((arg) => arg.startsWith("--threshold="))?.split("=")[1] || 0.45);
  const top = Number(process.argv.find((arg) => arg.startsWith("--top="))?.split("=")[1] || 40);
  const failAboveArg = process.argv.find((arg) => arg.startsWith("--fail-above="));
  const failAbove = failAboveArg ? Number(failAboveArg.split("=")[1]) : null;
  const taxonFilter = process.argv.find((arg) => arg.startsWith("--taxon="))?.split("=")[1] || "";
  const representativePatternOnly = process.argv.includes("--representative-pattern-only");
  if (
    !Number.isFinite(threshold) || threshold < 0 || threshold > 1 ||
    !Number.isInteger(top) || top < 1 ||
    (failAbove !== null && (!Number.isFinite(failAbove) || failAbove < 0 || failAbove > 1))
  ) {
    throw new Error("threshold and fail-above must be between 0 and 1; top must be a positive integer");
  }
  const appSource = fs.readFileSync(APP_JS, "utf8");
  const dinosaurs = vm.runInNewContext(`(${extractLiteral(appSource, "dinosaurs")})`, Object.create(null));
  const samples = vm.runInNewContext(`(${extractLiteral(appSource, "generatedImageSamples")})`, Object.create(null));
  const assignmentSandbox = { window: {} };
  vm.runInNewContext(fs.readFileSync(ASSIGNMENTS_JS, "utf8"), assignmentSandbox);
  const assignments = assignmentSandbox.window.gallerySlotAssignments || {};
  const dinoById = new Map(dinosaurs.map((dino) => [dino.id, dino]));
  const sampleBySource = new Map();
  for (const [taxonId, entries] of Object.entries(samples)) {
    for (const entry of entries) sampleBySource.set(entry.src || entry.source, { ...entry, taxonId });
  }

  const featureCache = new Map();
  const load = async (source) => {
    if (!featureCache.has(source)) featureCache.set(source, imageFeatures(source));
    return featureCache.get(source);
  };
  const pairs = [];
  for (const [taxonId, entries] of Object.entries(assignments)) {
    if (taxonFilter && taxonId !== taxonFilter) continue;
    const dino = dinoById.get(taxonId) || {};
    for (let leftIndex = 0; leftIndex < entries.length; leftIndex += 1) {
      for (let rightIndex = leftIndex + 1; rightIndex < entries.length; rightIndex += 1) {
        const left = entries[leftIndex];
        const right = entries[rightIndex];
        const isRepresentativePatternPair =
          new Set([left.galleryRole, right.galleryRole]).has("representative") &&
          new Set([left.galleryRole, right.galleryRole]).has("color-pattern");
        if (representativePatternOnly && !isRepresentativePatternPair) continue;
        if (!fs.existsSync(path.join(ROOT, left.source)) || !fs.existsSync(path.join(ROOT, right.source))) continue;
        const scores = structuralScores(await load(left.source), await load(right.source));
        const leftSample = sampleBySource.get(left.source) || {};
        const rightSample = sampleBySource.get(right.source) || {};
        const sameHabitat = Boolean(left.habitatKey && left.habitatKey === right.habitatKey);
        const sameComposition = Boolean(
          leftSample.compositionKey && leftSample.compositionKey === rightSample.compositionKey,
        );
        const knowledgeBoost = dino.knowledgeLevel === 1 ? 0.08 : dino.knowledgeLevel === 2 ? 0.04 : 0;
        const priorityScore =
          scores.structuralSimilarity +
          (isRepresentativePatternPair ? 0.08 : 0) +
          (sameComposition ? 0.08 : 0) +
          (sameHabitat ? 0.015 : 0) +
          knowledgeBoost;
        pairs.push({
          taxonId,
          taxonName: dino.name || taxonId,
          koreanName: dino.koreanName || "",
          knowledgeLevel: dino.knowledgeLevel || null,
          left: {
            slot: left.gallerySlot,
            role: left.galleryRole,
            source: left.source,
            compositionKey: leftSample.compositionKey || null,
            habitatKey: left.habitatKey || leftSample.habitatKey || null,
          },
          right: {
            slot: right.gallerySlot,
            role: right.galleryRole,
            source: right.source,
            compositionKey: rightSample.compositionKey || null,
            habitatKey: right.habitatKey || rightSample.habitatKey || null,
          },
          isRepresentativePatternPair,
          sameHabitat,
          sameComposition,
          ...scores,
          priorityScore: round(priorityScore),
        });
      }
    }
  }

  const ranked = pairs
    .filter((pair) => pair.structuralSimilarity >= threshold)
    .filter((pair) => !representativePatternOnly || pair.isRepresentativePatternPair)
    .sort((a, b) => b.priorityScore - a.priorityScore || b.structuralSimilarity - a.structuralSimilarity)
    .slice(0, top);
  const failures = failAbove === null
    ? []
    : pairs
        .filter((pair) => pair.structuralSimilarity >= failAbove)
        .filter((pair) => !representativePatternOnly || pair.isRepresentativePatternPair)
        .sort((a, b) => b.structuralSimilarity - a.structuralSimilarity);
  console.log(
    JSON.stringify(
      {
        taxa: dinosaurs.length,
        auditedUniqueImages: featureCache.size,
        comparedPairs: pairs.length,
        threshold,
        taxonFilter: taxonFilter || null,
        failAbove,
        failureCount: failures.length,
        failures: failures.map((pair) => ({
          taxonId: pair.taxonId,
          left: pair.left,
          right: pair.right,
          structuralSimilarity: pair.structuralSimilarity,
          matchMode: pair.matchMode,
        })),
        representativePatternOnly,
        resultCount: ranked.length,
        results: ranked,
      },
      null,
      2,
    ),
  );
  if (failures.length) process.exitCode = 1;
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
