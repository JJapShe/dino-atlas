import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..", "..");
const MANIFEST_PATH = path.join(ROOT, "motion-public-assets.json");
const CATALOG_FILES = [
  ["M0-legacy", "motion-samples.js", "motionSampleCatalog"],
  ["M1", "motion-m1-samples.js", "motionM1SampleCatalog"],
  ["M2", "motion-m2-samples.js", "motionM2SampleCatalog"],
  ["M2-I2V", "motion-m2-i2v-samples.js", "motionM2I2VSampleCatalog"],
];
const FROZEN_M0 = new Map([
  ["yutyrannus-huali-cold-breath-ambient-m0-v1", ["assets/motion/yutyrannus-huali-white-feather-cold-breath-ambient-m0-v1.mp4", "501c7fedc826ce49f97c687ff98250d63c0d66551024fbf651e215c38dbcdc3e", 278194]],
  ["tyrannosaurus-rex-ground-mist-ambient-m0-v1", ["assets/motion/tyrannosaurus-rex-hell-creek-ground-mist-ambient-m0-v1.mp4", "d117470c403e29c2f2d394277e1e3ccf155cea23557ae2340004cf0bfd5309c7", 220780]],
  ["brachiosaurus-altithorax-skylight-ambient-m0-v1", ["assets/motion/brachiosaurus-altithorax-high-shoulder-skylight-ambient-m0-v1.mp4", "1fc75a90a54d9c497afdc9892f27041dbad246d7d0fc2dc7acb8efc11c3f3362", 307698]],
  ["psittacosaurus-mongoliensis-water-shimmer-solo-m0-v1", ["assets/motion/psittacosaurus-mongoliensis-tail-bristle-water-shimmer-solo-m0-v1.mp4", "a6a9be69e7323ff3357267daf576aacb109d0adf68978bc40904948a9680e21c", 260005]],
  ["maiasaura-peeblesorum-nesting-ground-pollen-ecology-m0-v1", ["assets/motion/maiasaura-peeblesorum-nesting-ground-pollen-ecology-m0-v1.mp4", "13886af1a329ead6497f40a0e2a947bbfdc3b3ab0ab3aa367683af8dfc30f972", 176226]],
  ["velociraptor-protoceratops-dustfront-interaction-m0-v1", ["assets/motion/velociraptor-mongoliensis-protoceratops-dustfront-interaction-m0-v1.mp4", "ae04113adc19e592cc9b808054b2607bc9a3e9e15aa9beb9b3a8f6d85b3acff2", 280640]],
  ["yutyrannus-huali-volcanic-plume-ecology-m0-v1", ["assets/motion/yutyrannus-huali-volcanic-plume-ecology-m0-v1.mp4", "9d862616bdb8293f7028263b9d5d5560dd89cfa891dfffe853c30daaa991ca6a", 364730]],
  ["mononykus-olecranus-distant-rainsquall-environment-m0-v1", ["assets/motion/mononykus-olecranus-distant-rainsquall-environment-m0-v1.mp4", "d002ad6ae3a0b053f0d4349aa1b059e9fb16e6048f296b53dbbba84698e54ec4", 290324]],
  ["therizinosaurus-cheloniformis-tarbosaurus-watergap-ripples-interaction-m0-v1", ["assets/motion/therizinosaurus-cheloniformis-tarbosaurus-watergap-ripples-interaction-m0-v1.mp4", "b1f924126f63f2dcb7ab893a413e6f684f40fefef48575a81bf4369ffb1d09f3", 287158]],
  ["buriolestes-schultzi-candelaria-charcoal-ground-haze-environment-m0-v1", ["assets/motion/buriolestes-schultzi-candelaria-charcoal-ground-haze-environment-m0-v1.mp4", "8fe0f3e96eecfd02722bed8927dd4919147567902ce8ffc8924e373a694e06dc", 781513]],
  ["ceratosaurus-nasicornis-horsetail-dawn-water-ring-solo-m0-v1", ["assets/motion/ceratosaurus-nasicornis-horsetail-dawn-water-ring-solo-m0-v1.mp4", "3959a90f42414f77994741e2fda1da36c03b48d69a0e7080ba6f706efed26805", 319388]],
]);

const errors = [];
const fail = (message) => errors.push(message);
const hashFile = (filePath) => crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");
const isPublished = (sample) => sample?.review?.publication?.status === "published"
  && (sample.reviewStatus === undefined || sample.reviewStatus === "published");

const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, "utf8"));
if (manifest.schemaVersion !== 1 || manifest.policyVersion !== "2026-08-07-subject-motion-v1") {
  fail("public motion manifest schema or policy version is invalid");
}
const playback = manifest.policy?.playback;
if (manifest.policy?.newEnvironmentOnlyM0 !== "prohibited"
  || manifest.policy?.newPublicMotion !== "dinosaur subject motion required"
  || manifest.policy?.representativePromotion !== "prohibited"
  || manifest.policy?.galleryPromotion !== "prohibited"
  || manifest.policy?.rejectedRetiredAndRawAssets !== "excluded"
  || playback?.start !== "click-only" || playback?.muted !== true
  || playback?.autoplay !== false || playback?.loop !== false) {
  fail("public motion manifest policy is incomplete");
}

const sandbox = { window: {} };
vm.createContext(sandbox);
const catalogs = new Map();
for (const [kind, relativePath, exportName] of CATALOG_FILES) {
  const source = fs.readFileSync(path.join(ROOT, relativePath), "utf8");
  new vm.Script(source, { filename: relativePath }).runInContext(sandbox);
  const catalog = sandbox.window[exportName];
  if (!catalog || !Array.isArray(catalog.samples)) fail(`${relativePath}: catalog export is missing`);
  catalogs.set(kind, catalog || { policy: {}, samples: [] });
}

const m0Catalog = catalogs.get("M0-legacy");
if (m0Catalog.policy?.lifecycle !== "legacy-preserved"
  || m0Catalog.policy?.newEnvironmentOnlyM0 !== "prohibited") {
  fail("M0 catalog is not frozen as legacy-preserved");
}
const m0Ids = m0Catalog.samples.map((sample) => sample.id);
if (JSON.stringify(m0Ids) !== JSON.stringify([...FROZEN_M0.keys()])) {
  fail("M0 catalog differs from the frozen 11-sample legacy order");
}
for (const sample of m0Catalog.samples) {
  const frozen = FROZEN_M0.get(sample.id);
  if (!frozen || sample.motionClass !== "environment-only" || !isPublished(sample)
    || sample.src !== frozen[0] || sample.file?.sha256 !== frozen[1] || sample.file?.bytes !== frozen[2]) {
    fail(`${sample.id}: legacy M0 identity, publication state, path, or file identity changed`);
  }
}

for (const [kind, catalog] of catalogs) {
  const policy = catalog.policy || {};
  if (policy.autoplay !== "prohibited" || policy.loop !== "prohibited"
    || policy.clickToPlay !== "required" || policy.audio !== "prohibited") {
    fail(`${kind}: click-only, muted/no-audio, autoplay, or loop policy is incomplete`);
  }
  if (policy.representativePromotion !== "prohibited" || policy.galleryPromotion !== "prohibited") {
    fail(`${kind}: representative/gallery promotion must remain prohibited`);
  }
}

const publicSamples = [];
for (const [kind, catalog] of catalogs) {
  for (const sample of catalog.samples.filter(isPublished)) {
    publicSamples.push({ kind, sample });
  }
}
const publicById = new Map(publicSamples.map(({ kind, sample }) => [sample.id, { kind, sample }]));

for (const { kind, sample } of publicSamples) {
  if (sample.representativeEligible !== false || sample.galleryEligible !== false) {
    fail(`${sample.id}: public motion cannot be representative/gallery eligible`);
  }
  if (kind.startsWith("M2") && sample.anatomyEligible !== false) {
    fail(`${sample.id}: public M2 motion cannot be anatomy eligible`);
  }
  if (kind !== "M0-legacy") {
    const subject = sample.subjectMotion;
    if (sample.motionClass === "environment-only" || subject?.status !== "supported"
      || !Array.isArray(subject.taxonIds) || !subject.taxonIds.length
      || subject.taxonIds.some((id) => !/^[a-z0-9][a-z0-9-]*$/.test(id))
      || !Array.isArray(subject.movingParts) || !subject.movingParts.length
      || subject.movingParts.some((part) => typeof part !== "string" || !part.trim())
      || subject.evidenceGate !== "review.motionPlausibility"
      || sample.review?.motionPlausibility?.status !== "supported") {
      fail(`${sample.id}: public non-M0 motion lacks supported dinosaur subject motion`);
    }
    if (subject?.inheritedFrom) {
      const parent = publicById.get(subject.inheritedFrom)?.sample;
      if (!parent || parent.subjectMotion?.status !== "supported"
        || !subject.taxonIds.some((id) => parent.subjectMotion.taxonIds.includes(id))) {
        fail(`${sample.id}: inherited subject motion does not point to a compatible published sample`);
      }
    }
  }
}

const manifestAssets = Array.isArray(manifest.assets) ? manifest.assets : [];
const manifestById = new Map();
const manifestPaths = new Set();
for (const asset of manifestAssets) {
  if (!asset || manifestById.has(asset.id)) fail(`manifest duplicate or blank id: ${asset?.id || "(blank)"}`);
  if (manifestPaths.has(asset?.src)) fail(`manifest duplicate path: ${asset?.src}`);
  manifestById.set(asset?.id, asset);
  manifestPaths.add(asset?.src);
  const publicEntry = publicById.get(asset?.id);
  if (!publicEntry || publicEntry.kind !== asset.catalog) {
    fail(`${asset?.id}: manifest entry is not a published catalog sample`);
    continue;
  }
  const sample = publicEntry.sample;
  if (!/^assets\/motion\/[a-z0-9][a-z0-9./-]*\.mp4$/i.test(asset.src || "")
    || /(?:raw|candidate|rejected|retired)/i.test(asset.src)
    || sample.src !== asset.src || sample.file?.sha256 !== asset.sha256
    || sample.file?.bytes !== asset.bytes) {
    fail(`${asset.id}: manifest path or file identity differs from the published catalog`);
    continue;
  }
  const absolutePath = path.resolve(ROOT, asset.src);
  const relativeCheck = path.relative(ROOT, absolutePath);
  if (relativeCheck.startsWith("..") || path.isAbsolute(relativeCheck) || !fs.existsSync(absolutePath)) {
    fail(`${asset.id}: public asset is missing or escapes the repository`);
    continue;
  }
  const stat = fs.statSync(absolutePath);
  if (!stat.isFile() || stat.size !== asset.bytes || hashFile(absolutePath) !== asset.sha256) {
    fail(`${asset.id}: public asset bytes or SHA-256 mismatch`);
  }
}

const publicIds = [...publicById.keys()];
if (manifestAssets.length !== publicIds.length
  || publicIds.some((id) => !manifestById.has(id))
  || manifestAssets.some((asset) => !publicById.has(asset.id))) {
  fail("manifest must match the complete published catalog set exactly");
}

const appSource = fs.readFileSync(path.join(ROOT, "app.js"), "utf8");
const motionVideoTags = [...appSource.matchAll(/<video\b[^>]*data-motion-video[^>]*>/g)].map((match) => match[0]);
if (motionVideoTags.length !== 3) fail(`expected 3 motion video render tags, found ${motionVideoTags.length}`);
for (const [index, tag] of motionVideoTags.entries()) {
  if (!/\bmuted\b/.test(tag) || !/\bplaysinline\b/.test(tag)
    || /\bautoplay\b/.test(tag) || /\bloop\b/.test(tag)) {
    fail(`app motion video tag ${index + 1} must be muted/playsinline without autoplay or loop`);
  }
}

const retiredIds = [];
for (const catalog of catalogs.values()) {
  for (const sample of catalog.samples) {
    if (["retired", "rejected", "review-hold"].includes(sample.review?.publication?.status)) {
      retiredIds.push(sample.id);
      if (manifestById.has(sample.id) || manifestPaths.has(sample.src)) {
        fail(`${sample.id}: retired/rejected/review-hold sample leaked into the public manifest`);
      }
    }
  }
}

const report = {
  schemaVersion: manifest.schemaVersion,
  policyVersion: manifest.policyVersion,
  frozenLegacyM0: FROZEN_M0.size,
  publicAssets: manifestAssets.length,
  publicByCatalog: Object.fromEntries(
    [...catalogs.keys()].map((kind) => [kind, publicSamples.filter((entry) => entry.kind === kind).length]),
  ),
  excludedRetiredRejectedReviewHold: retiredIds.length,
  motionVideoRenderTags: motionVideoTags.length,
  errors,
};
console.log(JSON.stringify(report, null, 2));
if (errors.length) throw new Error(`public motion asset verification failed with ${errors.length} error(s)`);
