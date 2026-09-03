import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (relativePath) => fs.readFileSync(path.join(root, relativePath), "utf8");

function extractArrayLiteral(source, declaration) {
  const marker = `const ${declaration} = [`;
  const start = source.indexOf(marker);
  assert.notEqual(start, -1, `${declaration} declaration is missing`);

  let depth = 0;
  let quote = null;
  let escaped = false;
  for (let index = source.indexOf("[", start); index < source.length; index += 1) {
    const char = source[index];
    if (quote) {
      if (escaped) escaped = false;
      else if (char === "\\") escaped = true;
      else if (char === quote) quote = null;
      continue;
    }
    if (char === '"' || char === "'" || char === "`") {
      quote = char;
      continue;
    }
    if (char === "[") depth += 1;
    if (char === "]") {
      depth -= 1;
      if (depth === 0) return source.slice(source.indexOf("[", start), index + 1);
    }
  }
  throw new Error(`${declaration} array is not closed`);
}

const appSource = read("app.js");
const policySource = read("access-policy.js");
const publicHtml = read("index.html");
const adminHtml = read("admin.html");
const styles = read("styles.css");
const workflow = read(".github/workflows/deploy-pages.yml");

const dinosaurs = vm.runInNewContext(`(${extractArrayLiteral(appSource, "dinosaurs")})`, Object.create(null));
const policyContext = { globalThis: {} };
vm.runInNewContext(policySource, policyContext, { filename: "access-policy.js" });
const policy = policyContext.globalThis.dinoAtlasAccessPolicy;

assert.ok(policy, "access policy was not exported");
assert.equal(policy.schemaVersion, "dino-atlas-access-v1");
assert.equal(policy.defaultTier, "subscriber", "public atlas must open with the full catalog enabled");
assert.equal(policy.freeTaxonIds.length, 30, "free catalog must remain an intentional 30-taxon set");
assert.equal(new Set(policy.freeTaxonIds).size, policy.freeTaxonIds.length, "free IDs must be unique");

const knownIds = new Set(dinosaurs.map((dino) => dino.id));
const missingFreeIds = policy.freeTaxonIds.filter((id) => !knownIds.has(id));
assert.equal(missingFreeIds.length, 0, `free IDs missing from dinosaurs: ${missingFreeIds.join(", ")}`);

assert.match(publicHtml, /data-app-mode="public"/);
assert.match(publicHtml, /data-access-tier="subscriber"/);
assert.match(publicHtml, /data-access-scope="all"/);
assert.doesNotMatch(publicHtml, /id="reviewView"|id="assetReviewView"|data-view="review"|data-view="assetReview"/);
assert.match(
  styles,
  /body\[data-access-tier="subscriber"\]\s+\[data-access-scope-controls\]\s*\{[\s\S]*?display:\s*none;/,
  "free/full scope switch must remain hidden while the full catalog is the default",
);
assert.match(adminHtml, /data-app-mode="admin"/);
assert.match(adminHtml, /id="reviewView"/);
assert.match(adminHtml, /id="assetReviewView"/);

assert.match(workflow, /^\s*access-policy\.js\s*$/m, "Pages must deploy the public access policy");
assert.doesNotMatch(
  workflow,
  /\b(?:cp|install|rsync)\b[^\r\n]*\badmin\.html\b/i,
  "Pages must not copy the local admin surface into its artifact",
);
assert.match(appSource, /globalThis\.DINO_ATLAS_ENTITLEMENT/);
assert.match(appSource, /const hasLocalSubscriberPreview/);
assert.match(
  appSource,
  /hasLocalSubscriberPreview\s*=\s*[\s\S]*?isLocalAppHost[\s\S]*?previewCatalogEntitlement/,
  "subscriber query preview must remain restricted to localhost or 127.0.0.1",
);
assert.doesNotMatch(
  appSource,
  /isAdminPreviewMode/,
  "local subscriber preview must not require the unrelated admin=1 query",
);
assert.match(appSource, /isFreeTaxon/);
assert.match(appSource, /openSubscriptionDialog/);
assert.match(
  appSource,
  /isAdminMode \? sample\.description : getPublicMotionSummary\(sample\)/,
  "M1 descriptions must use public copy outside admin mode",
);
assert.doesNotMatch(
  appSource,
  /<p>\$\{escapeHtml\(sample\.description\)\}<\/p>/,
  "motion descriptions must never render raw on the public surface",
);
assert.match(
  appSource,
  /isAdminMode \? sample\.summary : getPublicMotionSummary\(sample\)/,
  "M2 summaries must use public copy outside admin mode",
);
const motionPatternStart = appSource.indexOf("const internalMotionTextPattern");
const motionPatternEnd = appSource.indexOf("function getPublicMotionSummary", motionPatternStart);
const motionPatternSource = appSource.slice(motionPatternStart, motionPatternEnd);
for (const productionPhrase of ["안전 구간", "같은 프레임", "생성형", "직접 증거"]) {
  assert.ok(
    motionPatternSource.includes(productionPhrase),
    `motion copy filter must cover: ${productionPhrase}`,
  );
}
assert.match(appSource, /"separate-site sequence-fauna context": "다른 유적에서 알려진 동물"/);
assert.doesNotMatch(
  appSource,
  /ecosystemParticipantRoleLabels\[participant\.role\] \|\| participant\.role/,
  "unknown ecosystem roles must not leak raw internal labels",
);

console.log(
  JSON.stringify(
    {
      taxa: dinosaurs.length,
      freeTaxa: policy.freeTaxonIds.length,
      subscriberTaxa: dinosaurs.length,
      publicReviewDom: false,
      adminDeployedToPages: false,
      errors: 0,
    },
    null,
    2,
  ),
);
