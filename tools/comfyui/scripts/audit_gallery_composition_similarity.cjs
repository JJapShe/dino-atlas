const fs = require("node:fs");
const crypto = require("node:crypto");
const path = require("node:path");
const vm = require("node:vm");

const ROOT = path.resolve(__dirname, "..", "..", "..");
const APP_JS = path.join(ROOT, "app.js");
const ASSIGNMENTS_JS = path.join(ROOT, "gallery-slots.js");
const SIZE = 64;

function loadSharp() {
  const attempts = [];
  const candidates = ["sharp"];
  const explicitNodeModules = process.env.DINO_ATLAS_NODE_MODULES;
  if (explicitNodeModules) candidates.push(path.join(explicitNodeModules, "sharp"));
  candidates.push(path.join(path.dirname(process.execPath), "node_modules", "sharp"));

  const codexRuntimeRoot = process.env.LOCALAPPDATA
    ? path.join(process.env.LOCALAPPDATA, "OpenAI", "Codex", "runtimes", "cua_node")
    : null;
  if (codexRuntimeRoot && fs.existsSync(codexRuntimeRoot)) {
    const runtimeCandidates = fs.readdirSync(codexRuntimeRoot, { withFileTypes: true })
      .filter((entry) => entry.isDirectory())
      .map((entry) => path.join(codexRuntimeRoot, entry.name, "bin", "node_modules", "sharp"))
      .filter((candidate) => fs.existsSync(candidate))
      .sort((left, right) => fs.statSync(right).mtimeMs - fs.statSync(left).mtimeMs);
    candidates.push(...runtimeCandidates);
  }

  for (const candidate of [...new Set(candidates)]) {
    try {
      return require(candidate);
    } catch (error) {
      attempts.push(`${candidate}: ${error.code || error.message}`);
    }
  }
  throw new Error(
    "Unable to load sharp. Install it for the active Node runtime or set " +
    "DINO_ATLAS_NODE_MODULES to a node_modules directory containing sharp.\n" + attempts.join("\n"),
  );
}

const sharp = loadSharp();

function isInsideRoot(root, target) {
  const relative = path.relative(root, target);
  return relative === "" || (!relative.startsWith(`..${path.sep}`) && relative !== ".." && !path.isAbsolute(relative));
}

function resolveRepoInput(rawPath, label) {
  if (typeof rawPath !== "string" || !rawPath.trim() || rawPath.includes("\0")) {
    throw new Error(`${label} must be a non-empty repository path`);
  }
  const resolved = path.resolve(ROOT, rawPath);
  if (!isInsideRoot(ROOT, resolved)) throw new Error(`${label} must stay inside the repository`);
  if (!fs.existsSync(resolved)) throw new Error(`Missing ${label}: ${rawPath}`);
  const real = fs.realpathSync.native(resolved);
  if (!isInsideRoot(fs.realpathSync.native(ROOT), real)) {
    throw new Error(`${label} resolves outside the repository`);
  }
  if (!fs.statSync(real).isFile()) throw new Error(`${label} must be a regular file: ${rawPath}`);
  return real;
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

async function imageFeatures(filePath) {
  const fileBuffer = fs.readFileSync(filePath);
  const { data, info } = await sharp(fileBuffer)
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
  return {
    gray,
    edge: sobel(gray),
    meanRgb,
    sha256: crypto.createHash("sha256").update(fileBuffer).digest("hex"),
  };
}

function round(value) {
  return Math.round(value * 1000) / 1000;
}

function optionValue(name) {
  const argument = process.argv.find((arg) => arg.startsWith(`${name}=`));
  return argument === undefined ? undefined : argument.slice(name.length + 1);
}

function resolveRepoOutput(rawPath, optionName) {
  if (rawPath === undefined) return null;
  if (!rawPath || rawPath.includes("\0")) throw new Error(`${optionName} requires a repository path`);
  const resolved = path.resolve(ROOT, rawPath);
  if (!isInsideRoot(ROOT, resolved)) {
    throw new Error(`${optionName} must stay inside the repository`);
  }
  let existingAncestor = fs.existsSync(resolved) ? resolved : path.dirname(resolved);
  while (!fs.existsSync(existingAncestor)) {
    const parent = path.dirname(existingAncestor);
    if (parent === existingAncestor) break;
    existingAncestor = parent;
  }
  const realAncestor = fs.realpathSync.native(existingAncestor);
  if (!isInsideRoot(fs.realpathSync.native(ROOT), realAncestor)) {
    throw new Error(`${optionName} resolves through a path outside the repository`);
  }
  return resolved;
}

function riskLevel(pair) {
  if (pair.structuralSimilarity >= 0.78 || (pair.sameComposition && pair.structuralSimilarity >= 0.68)) {
    return "critical";
  }
  if (pair.structuralSimilarity >= 0.68 || (pair.isRepresentativePatternPair && pair.structuralSimilarity >= 0.62)) {
    return "high";
  }
  if (pair.structuralSimilarity >= 0.58) return "medium";
  return "watch";
}

function diversificationRoute(pair) {
  if (pair.sameComposition) return "change-action-camera-and-spatial-layout";
  if (pair.isRepresentativePatternPair) return "replace-pattern-slot-with-opposite-action-or-scale";
  if (pair.matchMode === "mirrored") return "avoid-mirror-variant-change-camera-height-and-pose";
  return "change-camera-distance-direction-subject-count-or-habitat";
}

function markdownCell(value) {
  return String(value ?? "").replace(/\|/g, "\\|").replace(/\r?\n/g, " ");
}

function shortSource(source) {
  return path.basename(source || "");
}

function buildMarkdownReport(report, markdownResults) {
  const lines = [
    "# Dino Atlas gallery composition similarity audit",
    "",
    "> This report ranks visual-composition risk. It is not an anatomy pass and never authorizes representative promotion.",
    "",
    "## Baseline",
    "",
    `- Taxa in audit scope: ${report.taxa}`,
    `- Taxa with assigned gallery slots in scope: ${report.assignedTaxa}`,
    `- Total taxa in app data: ${report.totalTaxaInApp}`,
    `- Total taxa with assigned gallery slots: ${report.totalAssignedTaxa}`,
    `- Audited unique approved images: ${report.auditedUniqueImages}`,
    `- Compared within-taxon pairs: ${report.comparedPairs}`,
    `- Reporting threshold: ${report.threshold}`,
    `- Pairs at or above threshold: ${report.totalResultCount}`,
    "",
    "Fixed-threshold distribution:",
    "",
    ...Object.entries(report.thresholdCounts).map(([score, count]) => `- >= ${score}: ${count}`),
    "",
    "## Priority taxa",
    "",
    "| Rank | Taxon | LV | Flagged pairs | Max structural | Max priority | Critical | High | Mirrored | Recolor risk | Suggested route |",
    "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
  ];
  report.priorityTaxa.forEach((taxon, index) => {
    lines.push(`| ${index + 1} | ${markdownCell(taxon.taxonId)} | ${markdownCell(taxon.knowledgeLevel)} | ${taxon.flaggedPairs} | ${taxon.maxStructuralSimilarity} | ${taxon.maxPriorityScore} | ${taxon.criticalPairs} | ${taxon.highPairs} | ${taxon.mirroredPairs} | ${taxon.recolorRiskPairs} | ${markdownCell(taxon.suggestedRoute)} |`);
  });
  lines.push(
    "",
    "## Ranked pairs",
    "",
    "| Rank | Taxon | LV | Risk | Structural | Mode | Slots | Roles | Same composition | Recolor risk | Sources |",
    "| ---: | --- | ---: | --- | ---: | --- | --- | --- | --- | --- | --- |",
  );
  markdownResults.forEach((pair, index) => {
    lines.push(`| ${index + 1} | ${markdownCell(pair.taxonId)} | ${markdownCell(pair.knowledgeLevel)} | ${pair.riskLevel} | ${pair.structuralSimilarity} | ${pair.matchMode} | ${pair.left.slot}/${pair.right.slot} | ${pair.left.role}/${pair.right.role} | ${pair.sameComposition ? "yes" : "no"} | ${pair.recolorRisk ? "yes" : "no"} | ${markdownCell(shortSource(pair.left.source))}<br>${markdownCell(shortSource(pair.right.source))} |`);
  });
  lines.push(
    "",
    "## Gate",
    "",
    "- Treat high similarity as a review signal, not proof of duplication; inspect original-size images before acting.",
    "- A new candidate must materially change pose/action, camera family, spatial layout, subject count, or habitat; palette-only and mirror-only changes do not count.",
    "- Keep candidates in the ignored local review queue until provenance and anatomy review are complete.",
    "- Do not promote a representative from this report alone.",
    "",
  );
  return lines.join("\n");
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
      "  --candidate=<repo path>         compare one staged candidate to --taxon slots",
      "  --candidate-fail-above=<0..1>   exit 1 when a candidate comparison reaches this score",
      "  --threshold=<0..1>             minimum reported structural score (default 0.45)",
      "  --fail-above=<0..1>            exit 1 when any in-scope pair reaches this score",
      "  --top=<count>                   maximum ranked results (default 40)",
      "  --markdown-top=<count>          maximum ranked pairs in Markdown (default 100)",
      "  --queue-size=<count>            maximum priority taxa in the queue (default 30)",
      "  --json-output=<repo path>       write the audit JSON inside the repository",
      "  --markdown-output=<repo path>   write a human-readable report inside the repository",
      "  --include-image-hashes          include current approved source SHA-256 records",
      "",
      "structuralSimilarity is the larger of direct and horizontally mirrored grayscale/edge scores.",
    ].join("\n"));
    return;
  }
  const thresholdArg = optionValue("--threshold");
  const topArg = optionValue("--top");
  const markdownTopArg = optionValue("--markdown-top");
  const queueSizeArg = optionValue("--queue-size");
  const threshold = thresholdArg === undefined ? 0.45 : Number(thresholdArg);
  const top = topArg === undefined ? 40 : Number(topArg);
  const markdownTop = markdownTopArg === undefined ? 100 : Number(markdownTopArg);
  const queueSize = queueSizeArg === undefined ? 30 : Number(queueSizeArg);
  const jsonOutput = resolveRepoOutput(optionValue("--json-output"), "--json-output");
  const markdownOutput = resolveRepoOutput(optionValue("--markdown-output"), "--markdown-output");
  const candidatePath = resolveRepoOutput(optionValue("--candidate"), "--candidate");
  const candidateFailAboveArg = optionValue("--candidate-fail-above");
  const candidateFailAbove = candidateFailAboveArg === undefined ? null : Number(candidateFailAboveArg);
  const failAboveArg = optionValue("--fail-above");
  const failAbove = failAboveArg === undefined ? null : Number(failAboveArg);
  const taxonArg = optionValue("--taxon");
  if (taxonArg === "") throw new Error("--taxon requires a lowercase hyphenated species id");
  const taxonFilter = taxonArg ?? "";
  const representativePatternOnly = process.argv.includes("--representative-pattern-only");
  const includeImageHashes = process.argv.includes("--include-image-hashes");
  if (candidatePath && !taxonFilter) throw new Error("--candidate requires --taxon=<id>");
  if (taxonFilter && !/^[a-z0-9]+(?:-[a-z0-9]+)+$/.test(taxonFilter)) {
    throw new Error("--taxon must be a lowercase hyphenated species id");
  }
  if (
    !Number.isFinite(threshold) || threshold < 0 || threshold > 1 ||
    !Number.isInteger(top) || top < 1 ||
    !Number.isInteger(markdownTop) || markdownTop < 1 ||
    !Number.isInteger(queueSize) || queueSize < 1 ||
    (candidateFailAbove !== null && (!Number.isFinite(candidateFailAbove) || candidateFailAbove < 0 || candidateFailAbove > 1)) ||
    (failAbove !== null && (!Number.isFinite(failAbove) || failAbove < 0 || failAbove > 1))
  ) {
    throw new Error("threshold, fail-above and candidate-fail-above must be between 0 and 1; top, markdown-top and queue-size must be positive integers");
  }
  const appSource = fs.readFileSync(APP_JS, "utf8");
  const dinosaurs = vm.runInNewContext(`(${extractLiteral(appSource, "dinosaurs")})`, Object.create(null));
  const samples = vm.runInNewContext(`(${extractLiteral(appSource, "generatedImageSamples")})`, Object.create(null));
  const assignmentSandbox = { window: {} };
  vm.runInNewContext(fs.readFileSync(ASSIGNMENTS_JS, "utf8"), assignmentSandbox);
  const assignments = assignmentSandbox.window.gallerySlotAssignments || {};
  if (taxonFilter && !Object.prototype.hasOwnProperty.call(assignments, taxonFilter)) {
    throw new Error(`Unknown assigned taxon: ${taxonFilter}`);
  }
  const scopedAssignments = taxonFilter
    ? { [taxonFilter]: assignments[taxonFilter] }
    : assignments;
  const dinoById = new Map(dinosaurs.map((dino) => [dino.id, dino]));
  const sampleBySource = new Map();
  for (const [taxonId, entries] of Object.entries(samples)) {
    for (const entry of entries) sampleBySource.set(entry.src || entry.source, { ...entry, taxonId });
  }

  const featureCache = new Map();
  const approvedSources = new Set();
  const auditedApprovedSources = new Set();
  const load = async (source) => {
    if (!featureCache.has(source)) {
      const filePath = resolveRepoInput(source, `gallery source ${source}`);
      featureCache.set(source, imageFeatures(filePath));
    }
    if (approvedSources.has(source)) auditedApprovedSources.add(source);
    return featureCache.get(source);
  };
  const pairs = [];
  for (const [taxonId, entries] of Object.entries(scopedAssignments)) {
    if (!Array.isArray(entries) || entries.length === 0) {
      throw new Error(`Assigned taxon has no gallery slots: ${taxonId}`);
    }
    const dino = dinoById.get(taxonId) || {};
    for (const entry of entries) {
      if (!Number.isInteger(entry.gallerySlot) || entry.gallerySlot < 1) {
        throw new Error(`Invalid gallery slot for ${taxonId}: ${entry.gallerySlot}`);
      }
      resolveRepoInput(entry.source, `gallery source for ${taxonId} slot ${entry.gallerySlot}`);
      approvedSources.add(entry.source);
    }
    for (let leftIndex = 0; leftIndex < entries.length; leftIndex += 1) {
      for (let rightIndex = leftIndex + 1; rightIndex < entries.length; rightIndex += 1) {
        const left = entries[leftIndex];
        const right = entries[rightIndex];
        const isRepresentativePatternPair =
          new Set([left.galleryRole, right.galleryRole]).has("representative") &&
          new Set([left.galleryRole, right.galleryRole]).has("color-pattern");
        if (representativePatternOnly && !isRepresentativePatternPair) continue;
        const scores = structuralScores(await load(left.source), await load(right.source));
        const leftSample = sampleBySource.get(left.source) || {};
        const rightSample = sampleBySource.get(right.source) || {};
        const leftHabitat = left.habitatKey || leftSample.habitatKey || null;
        const rightHabitat = right.habitatKey || rightSample.habitatKey || null;
        const sameHabitat = Boolean(leftHabitat && leftHabitat === rightHabitat);
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
            kind: leftSample.kind || left.expectedKind || null,
            title: leftSample.title || null,
            phenotype: left.phenotype || leftSample.phenotype || null,
            compositionKey: leftSample.compositionKey || null,
            cameraDirection: leftSample.cameraDirection || leftSample.cameraFamily || null,
            habitatKey: leftHabitat,
          },
          right: {
            slot: right.gallerySlot,
            role: right.galleryRole,
            source: right.source,
            kind: rightSample.kind || right.expectedKind || null,
            title: rightSample.title || null,
            phenotype: right.phenotype || rightSample.phenotype || null,
            compositionKey: rightSample.compositionKey || null,
            cameraDirection: rightSample.cameraDirection || rightSample.cameraFamily || null,
            habitatKey: rightHabitat,
          },
          isRepresentativePatternPair,
          sameHabitat,
          sameComposition,
          ...scores,
          recolorRisk: scores.structuralSimilarity >= 0.58 && scores.colorMeanDistance >= 18,
          priorityScore: round(priorityScore),
        });
      }
    }
  }

  let candidateAudit = null;
  if (candidatePath) {
    const candidateSource = path.relative(ROOT, candidatePath).split(path.sep).join("/");
    resolveRepoInput(candidateSource, "candidate");
    const entries = scopedAssignments[taxonFilter];
    const comparisons = [];
    for (const entry of entries) {
      const scores = structuralScores(await load(candidateSource), await load(entry.source));
      comparisons.push({
        slot: entry.gallerySlot,
        role: entry.galleryRole,
        source: entry.source,
        ...scores,
      });
    }
    if (comparisons.length === 0) {
      throw new Error(`Candidate audit produced zero gallery comparisons for ${taxonFilter}`);
    }
    comparisons.sort((a, b) => b.structuralSimilarity - a.structuralSimilarity);
    const candidateFailures = candidateFailAbove === null
      ? []
      : comparisons.filter((comparison) => comparison.structuralSimilarity >= candidateFailAbove);
    candidateAudit = {
      source: candidateSource,
      taxonId: taxonFilter,
      comparisonCount: comparisons.length,
      maxStructuralSimilarity: comparisons[0]?.structuralSimilarity || 0,
      candidateFailAbove,
      failureCount: candidateFailures.length,
      failures: candidateFailures,
      comparisons,
    };
  }

  const inScopePairs = pairs.filter((pair) => !representativePatternOnly || pair.isRepresentativePatternPair);
  if (!candidatePath && inScopePairs.length === 0) {
    const mode = representativePatternOnly ? "representative/color-pattern" : "within-taxon";
    throw new Error(`Audit produced zero ${mode} comparisons${taxonFilter ? ` for ${taxonFilter}` : ""}`);
  }
  const rankedAll = inScopePairs
    .filter((pair) => pair.structuralSimilarity >= threshold)
    .map((pair) => ({ ...pair, riskLevel: riskLevel(pair), suggestedRoute: diversificationRoute(pair) }))
    .sort((a, b) => b.priorityScore - a.priorityScore || b.structuralSimilarity - a.structuralSimilarity);
  const ranked = rankedAll.slice(0, top);
  const thresholdCounts = Object.fromEntries(
    [0.45, 0.55, 0.65, 0.75].map((score) => [score.toFixed(2), inScopePairs.filter((pair) => pair.structuralSimilarity >= score).length]),
  );
  const taxonStats = new Map();
  for (const [taxonId] of Object.entries(scopedAssignments)) {
    const dino = dinoById.get(taxonId);
    if (!dino) throw new Error(`Assigned taxon is missing from app data: ${taxonId}`);
    taxonStats.set(taxonId, {
      taxonId,
      taxonName: dino.name || taxonId,
      koreanName: dino.koreanName || "",
      knowledgeLevel: dino.knowledgeLevel || null,
      comparedPairs: 0,
      flaggedPairs: 0,
      maxStructuralSimilarity: 0,
      maxPriorityScore: 0,
      criticalPairs: 0,
      highPairs: 0,
      mediumPairs: 0,
      watchPairs: 0,
      mirroredPairs: 0,
      representativePatternPairs: 0,
      sameCompositionPairs: 0,
      recolorRiskPairs: 0,
      suggestedRoute: null,
      topPair: null,
    });
  }
  for (const pair of inScopePairs) {
    const stats = taxonStats.get(pair.taxonId);
    if (stats) stats.comparedPairs += 1;
  }
  for (const pair of rankedAll) {
    const stats = taxonStats.get(pair.taxonId);
    if (!stats) continue;
    stats.flaggedPairs += 1;
    stats.maxStructuralSimilarity = Math.max(stats.maxStructuralSimilarity, pair.structuralSimilarity);
    stats.maxPriorityScore = Math.max(stats.maxPriorityScore, pair.priorityScore);
    stats[`${pair.riskLevel}Pairs`] += 1;
    if (pair.matchMode === "mirrored") stats.mirroredPairs += 1;
    if (pair.isRepresentativePatternPair) stats.representativePatternPairs += 1;
    if (pair.sameComposition) stats.sameCompositionPairs += 1;
    if (pair.recolorRisk) stats.recolorRiskPairs += 1;
    if (!stats.topPair) {
      stats.topPair = pair;
      stats.suggestedRoute = pair.suggestedRoute;
    }
  }
  const allTaxa = [...taxonStats.values()]
    .map((stats) => ({
      ...stats,
      maxStructuralSimilarity: round(stats.maxStructuralSimilarity),
      maxPriorityScore: round(stats.maxPriorityScore),
    }))
    .sort((a, b) => b.maxPriorityScore - a.maxPriorityScore || b.flaggedPairs - a.flaggedPairs || a.taxonId.localeCompare(b.taxonId));
  const priorityTaxa = allTaxa.filter((stats) => stats.flaggedPairs > 0).slice(0, queueSize);
  const failures = failAbove === null
    ? []
    : inScopePairs
        .filter((pair) => pair.structuralSimilarity >= failAbove)
        .sort((a, b) => b.structuralSimilarity - a.structuralSimilarity);
  const markdownResults = rankedAll.slice(0, markdownTop);
  if (includeImageHashes) {
    await Promise.all([...approvedSources].map((source) => load(source)));
  }
  const approvedImageHashes = includeImageHashes
    ? await Promise.all([...auditedApprovedSources].sort().map(async (source) => ({
        source,
        sha256: (await featureCache.get(source)).sha256,
      })))
    : undefined;
  const scopeTaxa = taxonFilter ? 1 : dinosaurs.length;
  const report = {
    auditVersion: 2,
    taxa: scopeTaxa,
    assignedTaxa: Object.keys(scopedAssignments).length,
    totalTaxaInApp: dinosaurs.length,
    totalAssignedTaxa: Object.keys(assignments).length,
    assignedUniqueApprovedImages: approvedSources.size,
    auditedUniqueImages: auditedApprovedSources.size,
    auditedApprovedImages: auditedApprovedSources.size,
    ...(approvedImageHashes ? { approvedImageHashes } : {}),
    candidateImagesAudited: candidateAudit ? 1 : 0,
    comparedPairs: inScopePairs.length,
    threshold,
    thresholdCounts,
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
    candidateAudit,
    totalResultCount: rankedAll.length,
    resultCount: ranked.length,
    markdownResultLimit: markdownResults.length,
    priorityTaxa,
    taxaSummary: allTaxa,
    results: ranked,
  };
  const json = `${JSON.stringify(report, null, 2)}\n`;
  if (jsonOutput) {
    fs.mkdirSync(path.dirname(jsonOutput), { recursive: true });
    fs.writeFileSync(jsonOutput, json, "utf8");
  }
  if (markdownOutput) {
    fs.mkdirSync(path.dirname(markdownOutput), { recursive: true });
    fs.writeFileSync(markdownOutput, buildMarkdownReport(report, markdownResults), "utf8");
  }
  console.log(json.trimEnd());
  if (failures.length || candidateAudit?.failureCount) process.exitCode = 1;
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
