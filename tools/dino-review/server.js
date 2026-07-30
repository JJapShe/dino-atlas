const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = Number(process.env.DINO_REVIEW_PORT || 8792);
const HOST = "127.0.0.1";
const ACCESS_KEY = process.env.DINO_REVIEW_KEY || "";
const ROOT = path.resolve(__dirname, "..", "..");
const ASSET_DIR = path.join(ROOT, "assets", "dinosaurs");
const DATA_DIR = path.join(__dirname, "data");
const REVIEW_FILE = path.join(DATA_DIR, "reviews.json");
const REJECTION_FILE = path.join(ROOT, "tools", "comfyui", "gallery-slot-rejections.json");

const IMAGE_TYPES = new Set([".png", ".jpg", ".jpeg", ".webp"]);
const EXCLUDED_KINDS = new Set([
  "audit",
  "contact-sheet",
  "comparison",
  "crops",
  "dashboard",
  "guide",
  "mask",
  "rejected",
  "reference",
  "review-options",
  "review-sheet",
  "split-panel-test",
]);

// The workbench is for reviewing actual dinosaur candidates.  Atlas guide,
// comparison, and failure records stay in the asset archive but must never
// reappear here just because their filename happens to look like an image.
const REVIEWABLE_CANDIDATE_KINDS = new Set([
  "count-level pass",
  "review hold",
  "anatomy review",
]);

const SPECIES_ALIASES = {
  allosaurus: "allosaurus-fragilis",
  ankylosaurus: "ankylosaurus-magniventris",
  herrerasaurus: "herrerasaurus-ischigualastensis",
  plateosaurus: "plateosaurus-engelhardti",
  stegosaurus: "stegosaurus-stenops",
  triceratops: "triceratops-horridus",
  tyrannosaurus: "tyrannosaurus-rex",
  velociraptor: "velociraptor-mongoliensis",
};

const KOREAN_NAMES = {
  "adasaurus-mongoliensis": "아다사우루스",
  "agujaceratops-mariscalensis": "아구하케라톱스",
  "allosaurus-fragilis": "알로사우루스",
  allosaurus: "알로사우루스",
  "almas-ukhaa": "알마스",
  "anchiornis-huxleyi": "안키오르니스",
  "ankylosaurus-magniventris": "안킬로사우루스",
  "apatosaurus-ajax": "아파토사우루스",
  "avimimus-portentosus": "아비미무스",
  "brachiosaurus-altithorax": "브라키오사우루스",
  "byronosaurus-jaffei": "비로노사우루스",
  "camarasaurus-lentus": "카마라사우루스",
  "caudipteryx-zoui": "카우딥테릭스",
  "ceratosaurus-nasicornis": "케라토사우루스",
  "citipati-osmolskae": "키티파티",
  "coelophysis-bauri": "코엘로피시스",
  "conchoraptor-gracilis": "콘코랍토르",
  "deinocheirus-mirificus": "데이노케이루스",
  "diplodocus-carnegiei": "디플로도쿠스",
  "edmontosaurus-annectens": "에드몬토사우루스",
  "elmisaurus-rarus": "엘미사우루스",
  "gallimimus-bullatus": "갈리미무스",
  "gobivenator-mongoliensis": "고비베나토르",
  "herrerasaurus-ischigualastensis": "헤레라사우루스",
  herrerasaurus: "헤레라사우루스",
  "khaan-mckennai": "칸",
  "microraptor-gui": "미크로랍토르",
  "mononykus-olecranus": "모노니쿠스",
  "nomingia-gobiensis": "노밍기아",
  "oviraptor-philoceratops": "오비랍토르",
  "pachycephalosaurus-wyomingensis": "파키케팔로사우루스",
  "parasaurolophus-walkeri": "파라사우롤로푸스",
  "plateosaurus-engelhardti": "플라테오사우루스",
  plateosaurus: "플라테오사우루스",
  "psittacosaurus-mongoliensis": "프시타코사우루스",
  "saurornithoides-mongoliensis": "사우로르니토이데스",
  "saurolophus-angustirostris": "사우롤로푸스",
  "sinornithosaurus-millenii": "시노르니토사우루스",
  "sinovenator-changii": "시노베나토르",
  "spinosaurus-aegyptiacus": "스피노사우루스",
  "stegosaurus-stenops": "스테고사우루스",
  stegosaurus: "스테고사우루스",
  "tarbosaurus-bataar": "타르보사우루스",
  "therizinosaurus-cheloniformis": "테리지노사우루스",
  "thescelosaurus-neglectus": "테스켈로사우루스",
  "triceratops-horridus": "트리케라톱스",
  triceratops: "트리케라톱스",
  "tyrannosaurus-rex": "티라노사우루스",
  tyrannosaurus: "티라노사우루스",
  "utahceratops-gettyi": "유타케라톱스",
  "velociraptor-mongoliensis": "벨로키랍토르",
  velociraptor: "벨로키랍토르",
  "zanabazar-junior": "자나바자르",
};

function loadAtlasKoreanNames() {
  const appFile = path.join(ROOT, "app.js");
  try {
    const source = fs.readFileSync(appFile, "utf8");
    const names = {};
    const matcher = /id:\s*"([^"]+)"[\s\S]{0,900}?koreanName:\s*"([^"]+)"/g;
    for (const match of source.matchAll(matcher)) {
      names[match[1]] = match[2];
    }
    return names;
  } catch {
    return {};
  }
}

const ATLAS_KOREAN_NAMES = loadAtlasKoreanNames();

function parseAppStringSet(source, name) {
  const match = source.match(new RegExp(`const ${name} = new Set\\(\\[([\\s\\S]*?)\\]\\);`));
  if (!match) return new Set();
  return new Set([...match[1].matchAll(/"([^"]+)"/g)].map((item) => item[1]));
}

function loadRejectedSources() {
  try {
    const data = JSON.parse(fs.readFileSync(REJECTION_FILE, "utf8"));
    return new Set(Object.keys(data.rejectedSources || {}));
  } catch {
    return new Set();
  }
}

function loadAtlasCandidateManifest() {
  const appFile = path.join(ROOT, "app.js");
  try {
    const source = fs.readFileSync(appFile, "utf8");
    const start = source.indexOf("const generatedImageSamples = {");
    const approvedSetStart = source.indexOf(
      "const approvedVelociraptorCandidateSources",
      start,
    );
    const end = source.lastIndexOf("\n};", approvedSetStart);
    if (start < 0 || approvedSetStart < 0 || end <= start) {
      throw new Error("candidate manifest not found");
    }

    const candidateKinds = new Map();
    const rawCandidates = source.slice(start, end);
    const entryMatcher = /^\s{4}\{\r?\n([\s\S]*?)^\s{4}\},/gm;
    for (const entry of rawCandidates.matchAll(entryMatcher)) {
      const kind = entry[1].match(/^\s*kind:\s*"([^"]+)",/m)?.[1];
      const asset = entry[1].match(/^\s*source:\s*"(assets\/dinosaurs\/[^"]+)",/m)?.[1];
      if (kind && asset) candidateKinds.set(asset, kind);
    }

    const rejectedSources = parseAppStringSet(source, "verifiedRejectedCandidateSources");
    for (const rejectedSource of loadRejectedSources()) {
      rejectedSources.add(rejectedSource);
    }

    return {
      candidateKinds,
      approvedVelociraptorSources: parseAppStringSet(source, "approvedVelociraptorCandidateSources"),
      rejectedSources,
    };
  } catch {
    return {
      candidateKinds: new Map(),
      approvedVelociraptorSources: new Set(),
      rejectedSources: new Set(),
    };
  }
}

function isAtlasVisibleCandidate(name, manifest = loadAtlasCandidateManifest()) {
  const source = `assets/dinosaurs/${name}`;
  const kind = manifest.candidateKinds.get(source);
  if (!kind) return false;
  if (!REVIEWABLE_CANDIDATE_KINDS.has(kind)) return false;
  if (manifest.rejectedSources.has(source)) return false;
  if (inferDinoGroup(name) === "velociraptor-mongoliensis" && !manifest.approvedVelociraptorSources.has(source)) {
    return false;
  }
  return true;
}

function authorized(url) {
  return !ACCESS_KEY || url.searchParams.get("key") === ACCESS_KEY;
}

function sendJson(res, status, value) {
  const body = JSON.stringify(value);
  res.writeHead(status, {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
  });
  res.end(body);
}

function sendText(res, status, value) {
  res.writeHead(status, { "content-type": "text/plain; charset=utf-8" });
  res.end(value);
}

function ensureDataDir() {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

function readReviews() {
  try {
    return JSON.parse(fs.readFileSync(REVIEW_FILE, "utf8"));
  } catch {
    return {};
  }
}

function writeReviews(value) {
  ensureDataDir();
  fs.writeFileSync(REVIEW_FILE, JSON.stringify(value, null, 2), "utf8");
}

function listImages() {
  const reviews = readReviews();
  const manifest = loadAtlasCandidateManifest();
  return fs.readdirSync(ASSET_DIR, { withFileTypes: true })
    .filter((entry) => entry.isFile() && IMAGE_TYPES.has(path.extname(entry.name).toLowerCase()))
    .filter((entry) => !EXCLUDED_KINDS.has(classify(entry.name)))
    .filter((entry) => isAtlasVisibleCandidate(entry.name, manifest))
    .map((entry) => {
      const full = path.join(ASSET_DIR, entry.name);
      const stat = fs.statSync(full);
      const id = entry.name;
      const kind = classify(entry.name);
      const species = inferDinoGroup(entry.name);
      return {
        id,
        name: entry.name,
        species,
        speciesLabel: dinoLabel(species),
        kind,
        url: `/image/${encodeURIComponent(entry.name)}`,
        sizeBytes: stat.size,
        updatedAt: stat.mtime.toISOString(),
        review: reviews[id] || null,
      };
    })
    .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
}

function classify(name) {
  const lower = name.toLowerCase();
  if (
    lower.includes("three-panel") ||
    lower.includes("triptych") ||
    lower.includes("center-panel") ||
    lower.includes("charcoal-opal")
  ) return "split-panel-test";
  if (lower.includes("anatomy-audit") || lower.includes("-audit")) return "audit";
  if (lower.includes("review-options")) return "review-options";
  if (lower.includes("review-sheet")) return "review-sheet";
  if (lower.includes("contact-sheet")) return "contact-sheet";
  if (lower.includes("dashboard")) return "dashboard";
  if (lower.includes("crops")) return "crops";
  if (lower.includes("mask")) return "mask";
  if (lower.includes("guide")) return "guide";
  if (lower.includes("reference")) return "reference";
  if (lower.includes("comparison")) return "comparison";
  if (lower.includes("rejected") || lower.includes("rejection")) return "rejected";
  if (lower.includes("candidate")) return "candidate";
  if (lower.includes("ecology")) return "ecology";
  if (lower.includes("pattern")) return "pattern";
  if (lower.includes("imagegen")) return "imagegen";
  if (lower.includes("lora")) return "lora";
  if (lower.includes("controlnet")) return "controlnet";
  if (lower.includes("i2i")) return "i2i";
  if (lower.includes("inpaint")) return "inpaint";
  return "gallery";
}

function isExcludedImageName(name) {
  return EXCLUDED_KINDS.has(classify(name)) || !isAtlasVisibleCandidate(name);
}

function inferDinoGroup(name) {
  const base = path.basename(name, path.extname(name)).toLowerCase();
  const stopWords = new Set([
    "imagegen", "source", "candidate", "review", "sheet", "contact", "crops", "mask",
    "comparison", "ecology", "pattern", "guide", "bodylock", "controlnet", "lora",
    "i2i", "inpaint", "clean", "rejected", "options", "current", "samples", "gallery",
    "compacthands", "digit", "micro", "closedjaw", "closedmouth", "handcue", "lowbrow",
    "lowhorn", "mediumarm", "natural", "strict", "smoothbrow", "subtlebrow", "threefinger",
  ]);
  const parts = base.split("-").filter(Boolean);
  const cut = [];
  for (const part of parts) {
    if (/^v\d+$/.test(part) || /^p\d+$/.test(part) || /^\d+$/.test(part) || stopWords.has(part)) break;
    cut.push(part);
    if (cut.length >= 2) break;
  }
  const group = cut.length ? cut.join("-") : "misc";
  return SPECIES_ALIASES[group] || group;
}

function dinoLabel(group) {
  const scientific = group
    .split("-")
    .map((part, index) => index === 0 ? capitalize(part) : part)
    .join(" ");
  const korean = KOREAN_NAMES[group] || ATLAS_KOREAN_NAMES[group];
  return korean ? `${korean} (${scientific})` : scientific;
}

function capitalize(value) {
  return value ? `${value[0].toUpperCase()}${value.slice(1)}` : value;
}

function mimeFor(file) {
  const ext = path.extname(file).toLowerCase();
  if (ext === ".jpg" || ext === ".jpeg") return "image/jpeg";
  if (ext === ".webp") return "image/webp";
  return "image/png";
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let size = 0;
    req.on("data", (chunk) => {
      size += chunk.length;
      if (size > 128 * 1024) {
        reject(new Error("body too large"));
        req.destroy();
        return;
      }
      chunks.push(chunk);
    });
    req.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
    req.on("error", reject);
  });
}

async function saveReview(req, res, url) {
  if (!authorized(url)) {
    sendText(res, 403, "forbidden");
    return;
  }
  let body;
  try {
    body = JSON.parse(await readBody(req));
  } catch {
    sendText(res, 400, "bad json");
    return;
  }

  const id = String(body.id || "");
  const status = String(body.status || "unreviewed");
  if (!id || !["unreviewed", "pass", "hold", "reject"].includes(status)) {
    sendText(res, 400, "bad review");
    return;
  }

  const target = path.join(ASSET_DIR, id);
  if (!target.startsWith(ASSET_DIR) || !fs.existsSync(target)) {
    sendText(res, 404, "image not found");
    return;
  }

  const reviews = readReviews();
  if (status === "unreviewed" && !body.note) {
    delete reviews[id];
  } else {
    reviews[id] = {
      status,
      note: String(body.note || "").slice(0, 2000),
      updatedAt: new Date().toISOString(),
    };
  }
  writeReviews(reviews);
  sendJson(res, 200, { ok: true, review: reviews[id] || null });
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${HOST}:${PORT}`);

  if (url.pathname === "/" || url.pathname === "/index.html") {
    if (!authorized(url)) {
      sendText(res, 403, "forbidden");
      return;
    }
    const html = fs.readFileSync(path.join(__dirname, "index.html"));
    res.writeHead(200, {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "no-store",
    });
    res.end(html);
    return;
  }

  if (url.pathname === "/api/images") {
    if (!authorized(url)) {
      sendText(res, 403, "forbidden");
      return;
    }
    const images = listImages();
    const species = [...new Map(images.map((image) => [
      image.species,
      {
        id: image.species,
        label: image.speciesLabel,
        count: images.filter((item) => item.species === image.species).length,
      },
    ])).values()].sort((a, b) => a.label.localeCompare(b.label, "ko"));
    const kinds = [...new Set(images.map((image) => image.kind))].sort();
    sendJson(res, 200, { generatedAt: new Date().toISOString(), images, species, kinds });
    return;
  }

  if (url.pathname === "/api/review" && req.method === "POST") {
    await saveReview(req, res, url);
    return;
  }

  if (url.pathname.startsWith("/image/")) {
    if (!authorized(url)) {
      sendText(res, 403, "forbidden");
      return;
    }
    const name = decodeURIComponent(url.pathname.slice("/image/".length));
    if (isExcludedImageName(name)) {
      sendText(res, 410, "excluded review image");
      return;
    }
    const full = path.resolve(ASSET_DIR, name);
    if (!full.startsWith(ASSET_DIR) || !fs.existsSync(full)) {
      sendText(res, 404, "not found");
      return;
    }
    res.writeHead(200, {
      "content-type": mimeFor(full),
      "cache-control": "no-store",
    });
    fs.createReadStream(full).pipe(res);
    return;
  }

  sendText(res, 404, "not found");
});

server.listen(PORT, HOST, () => {
  console.log(`Dino review listening on http://${HOST}:${PORT}`);
});
