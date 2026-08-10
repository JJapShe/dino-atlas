const crypto = require("crypto");
const fs = require("fs");
const http = require("http");
const path = require("path");
const vm = require("vm");

const REVIEW_STATUSES = new Set(["unreviewed", "pass", "hold", "reject"]);
const PROMOTABLE_KINDS = new Set([
  "count-level pass",
  "review hold",
  "anatomy review",
  "structure reference",
  "ecosystem scene review",
]);
const NON_REPRESENTATIVE_ANATOMY_STATUSES = new Set([
  "passed",
  "review-hold",
  "reference-only",
  "not-applicable",
]);
const REVIEWABLE_CANDIDATE_KINDS = new Set([
  "count-level pass",
  "review hold",
  "anatomy review",
  "ecosystem scene review",
]);
const IMAGE_TYPES = new Set([".png", ".jpg", ".jpeg", ".webp"]);
const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const CANDIDATE_ID_PATTERN = /^[a-z0-9][a-z0-9-]{0,79}$/;
const SPECIES_ID_PATTERN = /^[a-z0-9][a-z0-9-]{1,99}$/;
const LOOPBACK_HOSTS = new Set(["127.0.0.1", "::1"]);
const MAX_JSON_BODY_BYTES = 128 * 1024;
const INVALID_PLACEHOLDER_URL = "/placeholder/invalid.svg";
const INVENTORY_SYNC_STATES = new WeakMap();

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

class HttpError extends Error {
  constructor(status, message, code = "request_error") {
    super(message);
    this.status = status;
    this.code = code;
  }
}

function defaultConfig(overrides = {}) {
  const reviewDir = __dirname;
  const root = overrides.root ?? path.resolve(reviewDir, "..", "..");
  const dataDir = path.join(reviewDir, "data");
  return {
    host: overrides.host ?? process.env.DINO_REVIEW_HOST ?? "127.0.0.1",
    port: Number(overrides.port ?? process.env.DINO_REVIEW_PORT ?? 8792),
    accessKey: overrides.accessKey ?? process.env.DINO_REVIEW_KEY ?? "",
    root: overrides.root ?? root,
    assetDir: overrides.assetDir ?? process.env.DINO_REVIEW_ASSET_DIR ?? path.join(root, "assets", "dinosaurs"),
    pendingDir: overrides.pendingDir ?? process.env.DINO_REVIEW_PENDING_DIR ?? path.join(reviewDir, "pending"),
    dbPath: overrides.dbPath ?? process.env.DINO_REVIEW_DB ?? process.env.DINO_REVIEW_DB_PATH ?? path.join(dataDir, "review.sqlite"),
    legacyReviewFile: overrides.legacyReviewFile ?? path.join(dataDir, "reviews.json"),
    promotionDir: overrides.promotionDir ?? process.env.DINO_REVIEW_PROMOTION_DIR ?? path.join(reviewDir, "promotions"),
    indexFile: overrides.indexFile ?? path.join(reviewDir, "index.html"),
    rejectionFile: overrides.rejectionFile ?? path.join(root, "tools", "comfyui", "gallery-slot-rejections.json"),
    appFile: overrides.appFile ?? path.join(root, "app.js"),
    faultInjector: overrides.faultInjector ?? null,
    quiet: Boolean(overrides.quiet),
  };
}

function ensurePlainDirectory(directory) {
  if (!fs.existsSync(directory)) fs.mkdirSync(directory, { recursive: true });
  const stat = fs.lstatSync(directory);
  if (!stat.isDirectory() || stat.isSymbolicLink()) {
    throw new Error(`unsafe directory: ${directory}`);
  }
  return directory;
}

function directChild(parent, name) {
  const root = path.resolve(parent);
  const target = path.resolve(root, name);
  if (path.dirname(target) !== root) throw new HttpError(400, "invalid path component", "invalid_path");
  return target;
}

function requireSafeCandidateId(value) {
  const id = String(value || "");
  if (!CANDIDATE_ID_PATTERN.test(id)) {
    throw new HttpError(400, "invalid candidateId", "invalid_candidate_id");
  }
  return id;
}

function requireSafeFilename(value) {
  const filename = String(value || "");
  if (!filename || filename !== path.basename(filename) || /[\\/\0]/.test(filename)) {
    throw new HttpError(400, "invalid filename", "invalid_filename");
  }
  return filename;
}

function isVersionedSpeciesPng(filename, speciesId) {
  if (!SPECIES_ID_PATTERN.test(speciesId)) return false;
  if (!filename.startsWith(`${speciesId}-`)) return false;
  return /^[a-z0-9][a-z0-9-]*-v[1-9]\d*\.png$/.test(filename);
}

function isRegularNonLink(file) {
  try {
    const stat = fs.lstatSync(file);
    return stat.isFile() && !stat.isSymbolicLink();
  } catch {
    return false;
  }
}

function assertPng(file) {
  const fd = fs.openSync(file, "r");
  try {
    const fileSize = fs.fstatSync(fd).size;
    const signature = Buffer.alloc(PNG_SIGNATURE.length);
    const read = fs.readSync(fd, signature, 0, signature.length, 0);
    if (read !== PNG_SIGNATURE.length || !signature.equals(PNG_SIGNATURE)) {
      throw new HttpError(400, "file is not a PNG", "invalid_png");
    }
    let offset = PNG_SIGNATURE.length;
    let chunkIndex = 0;
    let sawIdat = false;
    let sawIend = false;
    while (offset + 12 <= fileSize) {
      const header = Buffer.allocUnsafe(8);
      if (fs.readSync(fd, header, 0, 8, offset) !== 8) {
        throw new HttpError(400, "PNG chunk header is truncated", "invalid_png");
      }
      const length = header.readUInt32BE(0);
      const type = header.toString("ascii", 4, 8);
      if (!/^[A-Za-z]{4}$/.test(type)) {
        throw new HttpError(400, "PNG chunk type is invalid", "invalid_png");
      }
      const chunkEnd = offset + 12 + length;
      if (!Number.isSafeInteger(chunkEnd) || chunkEnd > fileSize) {
        throw new HttpError(400, "PNG chunk exceeds file bounds", "invalid_png");
      }
      if (chunkIndex === 0) {
        if (type !== "IHDR" || length !== 13) {
          throw new HttpError(400, "PNG must begin with a 13-byte IHDR", "invalid_png");
        }
        const ihdr = Buffer.allocUnsafe(13);
        fs.readSync(fd, ihdr, 0, 13, offset + 8);
        if (ihdr.readUInt32BE(0) === 0 || ihdr.readUInt32BE(4) === 0) {
          throw new HttpError(400, "PNG dimensions must be positive", "invalid_png");
        }
      } else if (type === "IHDR") {
        throw new HttpError(400, "PNG contains more than one IHDR", "invalid_png");
      }
      if (type === "IDAT") sawIdat = true;
      if (type === "IEND") {
        if (length !== 0 || !sawIdat) {
          throw new HttpError(400, "PNG IEND structure is invalid", "invalid_png");
        }
        sawIend = true;
        break;
      }
      offset = chunkEnd;
      chunkIndex += 1;
    }
    if (!sawIend) throw new HttpError(400, "PNG is missing IEND", "invalid_png");
  } finally {
    fs.closeSync(fd);
  }
}

function sha256File(file) {
  const hash = crypto.createHash("sha256");
  const fd = fs.openSync(file, "r");
  const buffer = Buffer.allocUnsafe(1024 * 1024);
  try {
    let offset = 0;
    for (;;) {
      const read = fs.readSync(fd, buffer, 0, buffer.length, offset);
      if (!read) break;
      hash.update(buffer.subarray(0, read));
      offset += read;
    }
  } finally {
    fs.closeSync(fd);
  }
  return hash.digest("hex");
}

function injectFault(config, operation, targetPath) {
  config.faultInjector?.({ operation, path: targetPath });
}

function unlinkWithFault(config, file, operation) {
  injectFault(config, operation, file);
  fs.unlinkSync(file);
}

function canonicalJson(value) {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map((item) => canonicalJson(item)).join(",")}]`;
  return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(",")}}`;
}

function manifestDigest(manifest) {
  return crypto.createHash("sha256").update(canonicalJson(manifest), "utf8").digest("hex");
}

function openReviewDatabase(config) {
  const { DatabaseSync } = require("node:sqlite");
  ensurePlainDirectory(path.dirname(config.dbPath));
  const db = new DatabaseSync(config.dbPath);
  db.exec(`
    PRAGMA busy_timeout = 5000;
    PRAGMA journal_mode = WAL;
    PRAGMA foreign_keys = ON;
    CREATE TABLE IF NOT EXISTS metadata (
      key TEXT PRIMARY KEY,
      value TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS reviews (
      scope TEXT NOT NULL CHECK (scope IN ('atlas', 'pending')),
      asset_id TEXT NOT NULL,
      status TEXT NOT NULL CHECK (status IN ('unreviewed', 'pass', 'hold', 'reject')),
      note TEXT NOT NULL DEFAULT '',
      updated_at TEXT NOT NULL,
      PRIMARY KEY (scope, asset_id)
    );
    CREATE TABLE IF NOT EXISTS candidates (
      candidate_id TEXT PRIMARY KEY,
      filename TEXT NOT NULL,
      species_id TEXT NOT NULL,
      kind TEXT NOT NULL,
      state TEXT NOT NULL,
      target_path TEXT,
      manifest_json TEXT NOT NULL,
      sha256 TEXT,
      deletion_reason TEXT,
      discovered_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS candidate_events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      candidate_id TEXT NOT NULL,
      event_type TEXT NOT NULL,
      detail_json TEXT NOT NULL,
      created_at TEXT NOT NULL,
      FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id)
    );
    CREATE TABLE IF NOT EXISTS review_events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      scope TEXT NOT NULL CHECK (scope IN ('atlas', 'pending')),
      asset_id TEXT NOT NULL,
      status TEXT NOT NULL CHECK (status IN ('unreviewed', 'pass', 'hold', 'reject')),
      note TEXT NOT NULL DEFAULT '',
      image_sha256 TEXT,
      manifest_sha256 TEXT,
      created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS inventory_sync_runs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      started_at TEXT NOT NULL,
      completed_at TEXT,
      status TEXT NOT NULL CHECK (status IN ('running', 'complete', 'error')),
      item_count INTEGER NOT NULL DEFAULT 0,
      app_registration_count INTEGER NOT NULL DEFAULT 0,
      error TEXT
    );
    CREATE TABLE IF NOT EXISTS asset_inventory (
      asset_key TEXT PRIMARY KEY,
      scope TEXT NOT NULL,
      candidate_id TEXT,
      relative_path TEXT NOT NULL,
      species_id TEXT NOT NULL,
      kind TEXT NOT NULL,
      state TEXT NOT NULL,
      file_present INTEGER NOT NULL CHECK (file_present IN (0, 1)),
      size_bytes INTEGER,
      mtime_ms REAL,
      sha256 TEXT,
      source_record TEXT,
      metadata_json TEXT NOT NULL DEFAULT '{}',
      provenance_json TEXT NOT NULL DEFAULT '{}',
      issues_json TEXT NOT NULL DEFAULT '[]',
      last_seen TEXT NOT NULL,
      sync_run_id INTEGER NOT NULL
    );
    CREATE INDEX IF NOT EXISTS asset_inventory_scope_state
      ON asset_inventory(scope, state);
    CREATE INDEX IF NOT EXISTS asset_inventory_relative_path
      ON asset_inventory(relative_path);
    CREATE TABLE IF NOT EXISTS asset_app_registrations (
      registration_key TEXT PRIMARY KEY,
      asset_key TEXT NOT NULL,
      source_path TEXT NOT NULL,
      species_id TEXT NOT NULL,
      kind TEXT NOT NULL,
      entry_index INTEGER NOT NULL,
      source_record TEXT NOT NULL,
      app_metadata_json TEXT NOT NULL,
      last_seen TEXT NOT NULL,
      sync_run_id INTEGER NOT NULL
    );
    CREATE INDEX IF NOT EXISTS asset_app_registrations_asset
      ON asset_app_registrations(asset_key);
  `);
  const reviewColumns = new Set(db.prepare("PRAGMA table_info(reviews)").all().map((column) => column.name));
  if (!reviewColumns.has("image_sha256")) db.exec("ALTER TABLE reviews ADD COLUMN image_sha256 TEXT");
  if (!reviewColumns.has("manifest_sha256")) db.exec("ALTER TABLE reviews ADD COLUMN manifest_sha256 TEXT");
  importLegacyReviews(db, config.legacyReviewFile);
  return db;
}

function importLegacyReviews(db, legacyFile) {
  const key = "legacy_reviews_json_imported_v1";
  if (db.prepare("SELECT value FROM metadata WHERE key = ?").get(key)) return;
  let legacy = {};
  if (fs.existsSync(legacyFile)) {
    legacy = JSON.parse(fs.readFileSync(legacyFile, "utf8"));
  }
  const insert = db.prepare(`
    INSERT OR IGNORE INTO reviews (scope, asset_id, status, note, updated_at)
    VALUES ('atlas', ?, ?, ?, ?)
  `);
  db.exec("BEGIN IMMEDIATE");
  try {
    for (const [assetId, review] of Object.entries(legacy)) {
      if (!REVIEW_STATUSES.has(review?.status)) continue;
      insert.run(
        String(assetId),
        review.status,
        String(review.note || "").slice(0, 2000),
        validIsoDate(review.updatedAt) ? review.updatedAt : new Date().toISOString(),
      );
    }
    db.prepare("INSERT INTO metadata (key, value) VALUES (?, ?)").run(key, new Date().toISOString());
    db.exec("COMMIT");
  } catch (error) {
    db.exec("ROLLBACK");
    throw error;
  }
}

function validIsoDate(value) {
  return typeof value === "string" && value.length >= 20 && Number.isFinite(Date.parse(value));
}

function getReview(db, scope, assetId) {
  const row = db.prepare(`
    SELECT status, note, updated_at AS updatedAt,
      image_sha256 AS imageSha256, manifest_sha256 AS manifestSha256
    FROM reviews WHERE scope = ? AND asset_id = ?
  `).get(scope, assetId);
  return row || null;
}

function saveReviewRow(db, scope, assetId, status, note, binding = {}) {
  const updatedAt = new Date().toISOString();
  const imageSha256 = binding.imageSha256 || null;
  const manifestSha256 = binding.manifestSha256 || null;
  db.exec("BEGIN IMMEDIATE");
  try {
    if (status === "unreviewed" && !note) {
      db.prepare("DELETE FROM reviews WHERE scope = ? AND asset_id = ?").run(scope, assetId);
    } else {
      db.prepare(`
        INSERT INTO reviews (scope, asset_id, status, note, updated_at, image_sha256, manifest_sha256)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(scope, asset_id) DO UPDATE SET
          status = excluded.status,
          note = excluded.note,
          updated_at = excluded.updated_at,
          image_sha256 = excluded.image_sha256,
          manifest_sha256 = excluded.manifest_sha256
      `).run(scope, assetId, status, note, updatedAt, imageSha256, manifestSha256);
    }
    db.prepare(`
      INSERT INTO review_events
        (scope, asset_id, status, note, image_sha256, manifest_sha256, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `).run(scope, assetId, status, note, imageSha256, manifestSha256, updatedAt);
    db.exec("COMMIT");
  } catch (error) {
    db.exec("ROLLBACK");
    throw error;
  }
  if (status === "unreviewed" && !note) return null;
  return { status, note, updatedAt, imageSha256, manifestSha256 };
}

function reviewMatchesCandidate(review, candidate) {
  return Boolean(
    review
    && review.imageSha256
    && review.manifestSha256
    && review.imageSha256 === candidate.imageSha256
    && review.manifestSha256 === candidate.manifestSha256
  );
}

function upsertPendingCandidate(db, candidate) {
  const now = new Date().toISOString();
  const manifestJson = JSON.stringify(candidate.manifest);
  const existing = db.prepare(`
    SELECT filename, species_id AS speciesId, kind, state, target_path AS targetPath,
      manifest_json AS manifestJson
    FROM candidates WHERE candidate_id=?
  `).get(candidate.candidateId);
  if (!existing) {
    db.prepare(`
      INSERT INTO candidates
        (candidate_id, filename, species_id, kind, state, target_path, manifest_json, discovered_at, updated_at)
      VALUES (?, ?, ?, ?, 'pending', ?, ?, ?, ?)
    `).run(
      candidate.candidateId,
      candidate.filename,
      candidate.speciesId,
      candidate.kind,
      candidate.targetPath,
      manifestJson,
      now,
      now,
    );
    return "pending";
  }
  if (
    existing.state === "pending"
    && (
      existing.filename !== candidate.filename
      || existing.speciesId !== candidate.speciesId
      || existing.kind !== candidate.kind
      || existing.targetPath !== candidate.targetPath
      || existing.manifestJson !== manifestJson
    )
  ) {
    db.prepare(`
      UPDATE candidates SET filename = ?, species_id = ?, kind = ?, target_path = ?,
        manifest_json = ?, updated_at = ?
      WHERE candidate_id = ? AND state = 'pending'
    `).run(
      candidate.filename,
      candidate.speciesId,
      candidate.kind,
      candidate.targetPath,
      manifestJson,
      now,
      candidate.candidateId,
    );
  }
  return existing.state;
}

function addCandidateEvent(db, candidateId, eventType, detail) {
  db.prepare(`
    INSERT INTO candidate_events (candidate_id, event_type, detail_json, created_at)
    VALUES (?, ?, ?, ?)
  `).run(candidateId, eventType, JSON.stringify(detail || {}), new Date().toISOString());
}

function candidateMetadataIssues(manifest, actual) {
  const issues = [];
  if (manifest.schemaVersion !== 1) issues.push("schemaVersion은 1이어야 함");
  if (manifest.candidateId !== actual.candidateId) issues.push("candidateId가 폴더명과 일치하지 않음");
  if (manifest.filename !== actual.filename) issues.push("filename이 실제 PNG 파일명과 일치하지 않음");
  if (!SPECIES_ID_PATTERN.test(String(manifest.speciesId || ""))) issues.push("speciesId 형식 오류");
  if (!PROMOTABLE_KINDS.has(manifest.kind)) issues.push("허용되지 않은 kind");
  if (!isVersionedSpeciesPng(actual.filename, String(manifest.speciesId || ""))) {
    issues.push("파일명은 speciesId 접두사와 -vN.png 끝맺음이 필요함");
  }
  if (!isVersionedSpeciesPng(String(manifest.targetFilename || ""), String(manifest.speciesId || ""))) {
    issues.push("targetFilename은 speciesId 접두사와 -vN.png 끝맺음이 필요함");
  }
  for (const key of ["source", "license", "prompt", "seed", "workflow"]) {
    if (typeof manifest.provenance?.[key] !== "string" || !manifest.provenance[key].trim()) {
      issues.push(`provenance.${key} 누락`);
    }
  }
  const anatomy = manifest.anatomyReview || {};
  if (typeof anatomy.reviewer !== "string" || !anatomy.reviewer.trim()) {
    issues.push("anatomyReview.reviewer 누락");
  }
  if (!validIsoDate(anatomy.reviewedAt)) issues.push("anatomyReview.reviewedAt ISO 시각 누락");
  if (typeof anatomy.notes !== "string" || !anatomy.notes.trim()) issues.push("anatomyReview.notes 누락");
  if (manifest.kind === "count-level pass") {
    if (anatomy.status !== "passed") issues.push("대표 후보 anatomyReview.status는 passed여야 함");
    if (anatomy.representative !== true) issues.push("대표 후보 anatomyReview.representative는 true여야 함");
  } else {
    if (!NON_REPRESENTATIVE_ANATOMY_STATUSES.has(anatomy.status)) {
      issues.push("비대표 anatomyReview.status가 승인 가능한 값이 아님");
    }
    if (anatomy.representative !== false) issues.push("비대표 후보 anatomyReview.representative는 false여야 함");
  }
  return issues;
}

function inspectPendingCandidate(config, db, candidateId, options = {}) {
  const id = requireSafeCandidateId(candidateId);
  ensurePlainDirectory(config.pendingDir);
  const candidateDir = directChild(config.pendingDir, id);
  if (!fs.existsSync(candidateDir)) throw new HttpError(404, "candidate not found", "candidate_not_found");
  const dirStat = fs.lstatSync(candidateDir);
  if (!dirStat.isDirectory() || dirStat.isSymbolicLink()) {
    throw new HttpError(400, "unsafe candidate directory", "unsafe_candidate_directory");
  }
  const entries = fs.readdirSync(candidateDir, { withFileTypes: true });
  if (entries.some((entry) => entry.isSymbolicLink())) {
    throw new HttpError(400, "candidate contains a symlink", "candidate_symlink");
  }
  const extra = entries.filter((entry) => {
    if (!entry.isFile()) return true;
    return entry.name !== "candidate.json" && path.extname(entry.name).toLowerCase() !== ".png";
  });
  if (extra.length) throw new HttpError(400, "candidate directory contains unexpected files", "candidate_extra_files");
  const pngs = entries.filter((entry) => entry.isFile() && path.extname(entry.name).toLowerCase() === ".png");
  if (pngs.length !== 1) throw new HttpError(400, "candidate directory must contain exactly one PNG", "candidate_png_count");
  const manifestFile = directChild(candidateDir, "candidate.json");
  if (!isRegularNonLink(manifestFile)) throw new HttpError(400, "candidate.json missing or unsafe", "candidate_manifest_missing");
  let manifest;
  try {
    manifest = JSON.parse(fs.readFileSync(manifestFile, "utf8"));
  } catch {
    throw new HttpError(400, "candidate.json is not valid JSON", "candidate_manifest_invalid");
  }
  const filename = requireSafeFilename(pngs[0].name);
  const imageFile = directChild(candidateDir, filename);
  if (!isRegularNonLink(imageFile)) throw new HttpError(400, "unsafe candidate PNG", "candidate_png_unsafe");
  assertPng(imageFile);
  const speciesId = String(manifest.speciesId || inferDinoGroup(filename));
  const kind = String(manifest.kind || "candidate");
  const targetFilename = requireSafeFilename(manifest.targetFilename || filename);
  const targetPath = `assets/dinosaurs/${targetFilename}`;
  const metadataIssues = candidateMetadataIssues(manifest, { candidateId: id, filename });
  const candidate = {
    candidateId: id,
    filename,
    speciesId,
    kind,
    targetFilename,
    targetPath,
    candidateDir,
    manifestFile,
    imageFile,
    manifest,
    metadataIssues,
    imageSha256: sha256File(imageFile),
    manifestSha256: manifestDigest(manifest),
  };
  const state = upsertPendingCandidate(db, candidate);
  candidate.state = state || "pending";
  if (state !== "pending") {
    if (options.requirePendingState) {
      throw new HttpError(409, `candidateId has terminal history: ${state}`, "candidate_id_reused");
    }
    metadataIssues.push(`candidateId 종료 이력 존재: ${state}`);
  }
  return candidate;
}

function invalidCandidateIdForEntry(name) {
  if (CANDIDATE_ID_PATTERN.test(name)) return name;
  return `invalid-${crypto.createHash("sha256").update(name, "utf8").digest("hex").slice(0, 16)}`;
}

function inspectInvalidCandidateFiles(config, entryName) {
  const candidateDir = directChild(config.pendingDir, entryName);
  const snapshot = {
    candidateDir,
    entryName,
    manifest: null,
    imageFile: null,
    filename: null,
    stat: fs.lstatSync(candidateDir),
  };
  if (!snapshot.stat.isDirectory() || snapshot.stat.isSymbolicLink()) return snapshot;
  let entries;
  try {
    entries = fs.readdirSync(candidateDir, { withFileTypes: true });
  } catch {
    return snapshot;
  }
  const manifestFile = directChild(candidateDir, "candidate.json");
  if (isRegularNonLink(manifestFile)) {
    try {
      snapshot.manifest = JSON.parse(fs.readFileSync(manifestFile, "utf8"));
    } catch {
      snapshot.manifest = null;
    }
  }
  const pngs = entries.filter((entry) => {
    if (!entry.isFile() || entry.isSymbolicLink() || path.extname(entry.name).toLowerCase() !== ".png") return false;
    return isRegularNonLink(directChild(candidateDir, entry.name));
  });
  if (pngs.length !== 1) return snapshot;
  const imageFile = directChild(candidateDir, pngs[0].name);
  try {
    assertPng(imageFile);
  } catch {
    return snapshot;
  }
  snapshot.imageFile = imageFile;
  snapshot.filename = pngs[0].name;
  snapshot.stat = fs.statSync(imageFile);
  return snapshot;
}

function invalidPendingItem(config, db, entryName, error) {
  const snapshot = inspectInvalidCandidateFiles(config, entryName);
  const candidateId = invalidCandidateIdForEntry(entryName);
  const filename = snapshot.filename || entryName;
  const manifest = snapshot.manifest && typeof snapshot.manifest === "object" ? snapshot.manifest : {};
  const species = SPECIES_ID_PATTERN.test(String(manifest.speciesId || ""))
    ? String(manifest.speciesId)
    : inferDinoGroup(filename);
  const issueCode = error instanceof HttpError ? error.code : "candidate_load_error";
  const issueMessage = error?.message || "candidate could not be loaded";
  const sourceRecord = `tools/dino-review/pending/${entryName}/candidate.json`;
  const item = {
    id: `pending:${candidateId}`,
    candidateId,
    name: filename,
    species,
    speciesLabel: dinoLabel(config, species),
    kind: String(manifest.kind || "invalid candidate"),
    state: "invalid",
    scope: "pending",
    mediaType: "image/png",
    url: snapshot.imageFile
      ? `/quarantine-media/${encodeURIComponent(candidateId)}/${encodeURIComponent(filename)}`
      : INVALID_PLACEHOLDER_URL,
    sizeBytes: snapshot.imageFile ? snapshot.stat.size : 0,
    updatedAt: snapshot.stat.mtime.toISOString(),
    review: getReview(db, "pending", `pending:${candidateId}`),
    canPromote: false,
    loadError: true,
    metadataIssues: [`${issueCode}: ${issueMessage}`],
    targetPath: typeof manifest.targetFilename === "string"
      ? `assets/dinosaurs/${path.basename(manifest.targetFilename)}`
      : null,
    provenance: manifest.provenance && typeof manifest.provenance === "object" ? manifest.provenance : {},
    anatomyReview: manifest.anatomyReview && typeof manifest.anatomyReview === "object" ? manifest.anatomyReview : {},
  };
  Object.defineProperty(item, "_inventory", {
    enumerable: false,
    value: {
      absolutePath: snapshot.imageFile,
      pendingFolder: entryName,
      quarantineFilename: snapshot.filename,
      sourceRecord,
      sha256: null,
      manifest,
    },
  });
  return item;
}

function listPendingCandidates(config, db) {
  ensurePlainDirectory(config.pendingDir);
  const result = [];
  const koreanNames = loadAtlasKoreanNames(config);
  for (const entry of fs.readdirSync(config.pendingDir, { withFileTypes: true })) {
    if (!(entry.isDirectory() || entry.isSymbolicLink())) continue;
    try {
      const candidate = inspectPendingCandidate(config, db, entry.name);
      const stat = fs.statSync(candidate.imageFile);
      const assetId = `pending:${candidate.candidateId}`;
      const review = getReview(db, "pending", assetId);
      const bindingCurrent = !review || reviewMatchesCandidate(review, candidate);
      const metadataIssues = [...candidate.metadataIssues];
      if (!bindingCurrent) metadataIssues.push("검수 후 후보 이미지 또는 manifest가 변경되어 재검수 필요");
      const loadError = candidate.state !== "pending";
      const item = {
        id: assetId,
        candidateId: candidate.candidateId,
        name: candidate.filename,
        species: candidate.speciesId,
        speciesLabel: dinoLabel(config, candidate.speciesId, koreanNames),
        kind: candidate.kind,
        state: loadError ? candidate.state : "pending",
        scope: "pending",
        mediaType: "image/png",
        url: `/pending-media/${encodeURIComponent(candidate.candidateId)}/${encodeURIComponent(candidate.filename)}`,
        sizeBytes: stat.size,
        updatedAt: stat.mtime.toISOString(),
        review,
        canPromote: !loadError && review?.status === "pass" && bindingCurrent && metadataIssues.length === 0,
        loadError,
        metadataIssues,
        targetPath: candidate.targetPath,
        provenance: candidate.manifest.provenance || {},
        anatomyReview: candidate.manifest.anatomyReview || {},
      };
      Object.defineProperty(item, "_inventory", {
        enumerable: false,
        value: {
          absolutePath: candidate.imageFile,
          pendingFolder: candidate.candidateId,
          sourceRecord: `tools/dino-review/pending/${candidate.candidateId}/candidate.json`,
          sha256: candidate.imageSha256,
          manifest: candidate.manifest,
        },
      });
      result.push(item);
    } catch (error) {
      if (!(error instanceof HttpError)) throw error;
      result.push(invalidPendingItem(config, db, entry.name, error));
    }
  }
  return result;
}

function parseAppStringSet(source, name) {
  const match = source.match(new RegExp(`const ${name} = new Set\\(\\[([\\s\\S]*?)\\]\\);`));
  if (!match) return new Set();
  return new Set([...match[1].matchAll(/"([^"]+)"/g)].map((item) => item[1]));
}

function extractAssignedLiteral(source, name) {
  const assignment = new RegExp(`\\bconst\\s+${name}\\s*=\\s*`).exec(source);
  if (!assignment) throw new Error(`${name} assignment not found`);
  const start = assignment.index + assignment[0].length;
  const opener = source[start];
  if (opener !== "{" && opener !== "[") throw new Error(`${name} must be an object or array literal`);
  const closer = opener === "{" ? "}" : "]";
  let depth = 0;
  let quote = null;
  let escaped = false;
  let lineComment = false;
  let blockComment = false;
  for (let index = start; index < source.length; index += 1) {
    const character = source[index];
    const next = source[index + 1];
    if (lineComment) {
      if (character === "\n") lineComment = false;
      continue;
    }
    if (blockComment) {
      if (character === "*" && next === "/") {
        blockComment = false;
        index += 1;
      }
      continue;
    }
    if (quote) {
      if (escaped) escaped = false;
      else if (character === "\\") escaped = true;
      else if (character === quote) quote = null;
      continue;
    }
    if (character === "/" && next === "/") {
      lineComment = true;
      index += 1;
      continue;
    }
    if (character === "/" && next === "*") {
      blockComment = true;
      index += 1;
      continue;
    }
    if (character === "\"" || character === "'" || character === "`") {
      quote = character;
      continue;
    }
    if (character === opener) depth += 1;
    else if (character === closer) {
      depth -= 1;
      if (depth === 0) return source.slice(start, index + 1);
    }
  }
  throw new Error(`${name} literal is unterminated`);
}

function parseIsolatedLiteral(literal, name) {
  const context = vm.createContext(Object.create(null), {
    codeGeneration: { strings: false, wasm: false },
  });
  try {
    return new vm.Script(`"use strict";(${literal})`, {
      filename: `${name}.literal.js`,
      displayErrors: true,
    }).runInContext(context, { timeout: 2000, displayErrors: true });
  } catch (error) {
    throw new Error(`unable to parse ${name}: ${error.message}`, { cause: error });
  }
}

function loadRejectedSources(config) {
  try {
    const data = JSON.parse(fs.readFileSync(config.rejectionFile, "utf8"));
    return new Set(Object.keys(data.rejectedSources || {}));
  } catch {
    return new Set();
  }
}

function loadAtlasCandidateManifest(config) {
  const source = fs.readFileSync(config.appFile, "utf8");
  const samples = parseIsolatedLiteral(
    extractAssignedLiteral(source, "generatedImageSamples"),
    "generatedImageSamples",
  );
  if (!samples || typeof samples !== "object" || Array.isArray(samples)) {
    throw new Error("generatedImageSamples did not evaluate to an object");
  }
  const candidateEntries = new Map();
  const registrations = [];
  let entryIndex = 0;
  for (const [speciesId, entries] of Object.entries(samples)) {
    if (!Array.isArray(entries)) throw new Error(`generatedImageSamples.${speciesId} must be an array`);
    for (const entry of entries) {
      if (!entry || typeof entry !== "object" || Array.isArray(entry)) {
        throw new Error(`generatedImageSamples.${speciesId}[${entryIndex}] must be an object`);
      }
      const metadata = JSON.parse(JSON.stringify(entry));
      const sourcePath = String(metadata.source || metadata.src || "");
      const kind = String(metadata.kind || "");
      const registration = { speciesId, kind, metadata, sourcePath, entryIndex };
      registrations.push(registration);
      if (sourcePath.startsWith("assets/dinosaurs/")) {
        const existing = candidateEntries.get(sourcePath) || [];
        existing.push(registration);
        candidateEntries.set(sourcePath, existing);
      }
      entryIndex += 1;
    }
  }
  const rejectedSources = parseAppStringSet(source, "verifiedRejectedCandidateSources");
  for (const rejected of loadRejectedSources(config)) rejectedSources.add(rejected);
  return {
    candidateEntries,
    registrations,
    appEntryCount: registrations.length,
    approvedVelociraptorSources: parseAppStringSet(source, "approvedVelociraptorCandidateSources"),
    rejectedSources,
  };
}

function atlasRegistration(name, manifest) {
  const source = `assets/dinosaurs/${name}`;
  if (manifest.rejectedSources.has(source)) return null;
  if (inferDinoGroup(name) === "velociraptor-mongoliensis" && !manifest.approvedVelociraptorSources.has(source)) return null;
  return (manifest.candidateEntries.get(source) || []).find((entry) => REVIEWABLE_CANDIDATE_KINDS.has(entry.kind)) || null;
}

function isAtlasVisibleCandidate(name, manifest) {
  return Boolean(atlasRegistration(name, manifest));
}

function loadAtlasKoreanNames(config) {
  try {
    const source = fs.readFileSync(config.appFile, "utf8");
    const names = {};
    for (const match of source.matchAll(/id:\s*"([^"]+)"[\s\S]{0,900}?koreanName:\s*"([^"]+)"/g)) {
      names[match[1]] = match[2];
    }
    return names;
  } catch {
    return {};
  }
}

function listAtlasImages(config, db, manifest = loadAtlasCandidateManifest(config)) {
  ensurePlainDirectory(config.assetDir);
  const koreanNames = loadAtlasKoreanNames(config);
  return fs.readdirSync(config.assetDir, { withFileTypes: true })
    .filter((entry) => entry.isFile() && !entry.isSymbolicLink() && IMAGE_TYPES.has(path.extname(entry.name).toLowerCase()))
    .filter((entry) => isAtlasVisibleCandidate(entry.name, manifest))
    .map((entry) => {
      const full = directChild(config.assetDir, entry.name);
      const stat = fs.statSync(full);
      const registration = atlasRegistration(entry.name, manifest);
      const species = registration.speciesId;
      const item = {
        id: entry.name,
        name: entry.name,
        species,
        speciesLabel: dinoLabel(config, species, koreanNames),
        kind: registration.kind,
        state: "app-registered",
        scope: "atlas",
        mediaType: mimeFor(full),
        url: `/image/${encodeURIComponent(entry.name)}`,
        sizeBytes: stat.size,
        updatedAt: stat.mtime.toISOString(),
        review: getReview(db, "atlas", entry.name),
      };
      Object.defineProperty(item, "_inventory", {
        enumerable: false,
        value: { absolutePath: full, appRegistration: registration },
      });
      return item;
    });
}

function markIntegratedCandidates(db, manifest) {
  const rows = db.prepare(`
    SELECT candidate_id AS candidateId, target_path AS targetPath
    FROM candidates WHERE state = 'promoted-awaiting-app-integration'
    ORDER BY candidate_id
  `).all();
  const registeredRows = rows.filter((row) => manifest.candidateEntries.has(String(row.targetPath || "")));
  if (registeredRows.length === 0) return [];
  const integrated = [];
  db.exec("BEGIN IMMEDIATE");
  try {
    for (const row of registeredRows) {
      const integratedAt = new Date().toISOString();
      const update = db.prepare(`
        UPDATE candidates SET state='integrated', updated_at=?
        WHERE candidate_id=? AND state='promoted-awaiting-app-integration'
      `).run(integratedAt, row.candidateId);
      if (Number(update.changes) !== 1) continue;
      addCandidateEvent(db, row.candidateId, "integrated", {
        targetPath: row.targetPath,
        integratedAt,
      });
      integrated.push(row.candidateId);
    }
    db.exec("COMMIT");
  } catch (error) {
    db.exec("ROLLBACK");
    throw error;
  }
  return integrated;
}

function listIntegrationCandidates(config, db) {
  const koreanNames = loadAtlasKoreanNames(config);
  return db.prepare(`
    SELECT candidate_id AS candidateId, filename, species_id AS speciesId, kind,
      state, target_path AS targetPath, manifest_json AS manifestJson,
      sha256, updated_at AS updatedAt
    FROM candidates WHERE state='promoted-awaiting-app-integration'
    ORDER BY updated_at DESC, candidate_id
  `).all().map((row) => {
    let manifest = {};
    try {
      manifest = JSON.parse(row.manifestJson || "{}");
    } catch {
      manifest = {};
    }
    const metadataIssues = [];
    const targetFilename = path.basename(String(row.targetPath || ""));
    let targetFile = null;
    let stat = null;
    if (!targetFilename || row.targetPath !== `assets/dinosaurs/${targetFilename}`) {
      metadataIssues.push("승격 대상 경로 형식 오류");
    } else {
      targetFile = directChild(config.assetDir, targetFilename);
      if (!isRegularNonLink(targetFile)) {
        metadataIssues.push("승격된 프로젝트 자산이 없거나 안전하지 않음");
      } else {
        stat = fs.statSync(targetFile);
        if (!row.sha256 || sha256File(targetFile) !== row.sha256) {
          metadataIssues.push("승격된 프로젝트 자산 해시 불일치");
        }
      }
    }
    const promotionRecord = `tools/dino-review/promotions/${row.candidateId}.json`;
    const item = {
      id: `integration:${row.candidateId}`,
      candidateId: row.candidateId,
      name: targetFilename || row.filename,
      species: row.speciesId,
      speciesLabel: dinoLabel(config, row.speciesId, koreanNames),
      kind: row.kind,
      state: row.state,
      scope: "integration",
      mediaType: "image/png",
      url: stat && metadataIssues.length === 0
        ? `/promoted-media/${encodeURIComponent(row.candidateId)}/${encodeURIComponent(targetFilename)}`
        : INVALID_PLACEHOLDER_URL,
      sizeBytes: stat?.size || 0,
      updatedAt: stat?.mtime.toISOString() || row.updatedAt,
      size: stat?.size || 0,
      updated: stat?.mtime.toISOString() || row.updatedAt,
      targetPath: row.targetPath,
      promotionRecord,
      provenance: manifest.provenance || {},
      anatomyReview: manifest.anatomyReview || {},
      review: getReview(db, "pending", `pending:${row.candidateId}`),
      metadataIssues,
      canPromote: false,
      loadError: metadataIssues.length > 0,
    };
    Object.defineProperty(item, "_inventory", {
      enumerable: false,
      value: {
        absolutePath: targetFile,
        sourceRecord: promotionRecord,
        sha256: row.sha256,
        manifest,
      },
    });
    return item;
  });
}

function appEntryProvenance(metadata) {
  return {
    source: metadata.sourceAttribution || "",
    license: metadata.licenseRecord || "",
    prompt: metadata.generationPromptRecord || "",
    seed: metadata.generationSeed || "",
    workflow: metadata.generationWorkflow || "",
  };
}

function statSafeRegular(file) {
  if (!file || !isRegularNonLink(file)) return null;
  return fs.statSync(file);
}

function appInventoryRecords(config, db, manifest) {
  const grouped = new Map();
  for (const registration of manifest.registrations) {
    const sourcePath = registration.sourcePath || `app.js#generatedImageSamples/${registration.speciesId}/${registration.entryIndex}`;
    const existing = grouped.get(sourcePath) || [];
    existing.push(registration);
    grouped.set(sourcePath, existing);
  }
  const inventory = [];
  const appRegistrations = [];
  const previousStatement = db.prepare(`
    SELECT size_bytes AS sizeBytes, mtime_ms AS mtimeMs, sha256
    FROM asset_inventory WHERE asset_key=?
  `);
  for (const [sourcePath, registrations] of grouped) {
    const first = registrations[0];
    const assetKey = `app:${sourcePath}`;
    const issues = [];
    let file = null;
    let stat = null;
    if (!sourcePath.startsWith("assets/dinosaurs/") || path.basename(sourcePath) !== sourcePath.slice("assets/dinosaurs/".length)) {
      issues.push("app 등록 경로가 assets/dinosaurs의 단일 파일이 아님");
    } else {
      file = directChild(config.assetDir, path.basename(sourcePath));
      stat = statSafeRegular(file);
      if (!stat) issues.push("app 등록 자산 파일 누락");
    }
    if (registrations.length > 1) issues.push(`app 중복 등록 ${registrations.length}건`);
    const visible = sourcePath.startsWith("assets/dinosaurs/")
      ? atlasRegistration(path.basename(sourcePath), manifest)
      : null;
    const state = manifest.rejectedSources.has(sourcePath)
      ? "app-rejected"
      : (visible ? "app-registered" : "app-hidden");
    const previous = previousStatement.get(assetKey);
    const lazyHash = stat && previous
      && Number(previous.sizeBytes) === stat.size
      && Number(previous.mtimeMs) === stat.mtimeMs
      ? previous.sha256
      : null;
    inventory.push({
      assetKey,
      scope: "atlas",
      candidateId: null,
      relativePath: sourcePath,
      speciesId: visible?.speciesId || first.speciesId,
      kind: visible?.kind || first.kind || "unclassified",
      state,
      filePresent: Boolean(stat),
      sizeBytes: stat?.size ?? null,
      mtimeMs: stat?.mtimeMs ?? null,
      sha256: lazyHash || null,
      sourceRecord: `app.js#generatedImageSamples/${first.speciesId}/${first.entryIndex}`,
      metadata: { registrationCount: registrations.length, primary: first.metadata },
      provenance: appEntryProvenance(first.metadata),
      issues,
    });
    for (const registration of registrations) {
      appRegistrations.push({
        registrationKey: crypto.createHash("sha256").update(
          `${registration.entryIndex}\0${registration.speciesId}\0${sourcePath}`,
          "utf8",
        ).digest("hex"),
        assetKey,
        sourcePath,
        speciesId: registration.speciesId,
        kind: registration.kind || "unclassified",
        entryIndex: registration.entryIndex,
        sourceRecord: `app.js#generatedImageSamples/${registration.speciesId}/${registration.entryIndex}`,
        metadata: registration.metadata,
      });
    }
  }
  return { inventory, appRegistrations };
}

function itemInventoryRecord(config, item) {
  const detail = item._inventory || {};
  const stat = statSafeRegular(detail.absolutePath);
  const relativePath = item.scope === "integration"
    ? String(item.targetPath || "")
    : `tools/dino-review/pending/${detail.pendingFolder || item.candidateId}/${item.name}`;
  return {
    assetKey: item.id,
    scope: item.scope,
    candidateId: item.candidateId || null,
    relativePath,
    speciesId: item.species || "unknown",
    kind: item.kind || "unclassified",
    state: item.state || item.scope,
    filePresent: Boolean(stat),
    sizeBytes: stat?.size ?? null,
    mtimeMs: stat?.mtimeMs ?? null,
    sha256: detail.sha256 || null,
    sourceRecord: detail.sourceRecord || null,
    metadata: {
      manifest: detail.manifest || {},
      pendingFolder: detail.pendingFolder || null,
      quarantineFilename: detail.quarantineFilename || null,
    },
    provenance: item.provenance || {},
    issues: item.metadataIssues || [],
  };
}

function beginInventorySync(db) {
  const startedAt = new Date().toISOString();
  const result = db.prepare(`
    INSERT INTO inventory_sync_runs(started_at, status) VALUES (?, 'running')
  `).run(startedAt);
  return Number(result.lastInsertRowid);
}

function failInventorySync(db, runId, error) {
  db.prepare(`
    UPDATE inventory_sync_runs SET completed_at=?, status='error', error=? WHERE id=?
  `).run(new Date().toISOString(), String(error?.message || error).slice(0, 4000), runId);
}

function inventorySignature(records, appRegistrations) {
  const normalizedRecords = records.map((record) => ({
    assetKey: record.assetKey,
    scope: record.scope,
    candidateId: record.candidateId,
    relativePath: record.relativePath,
    speciesId: record.speciesId,
    kind: record.kind,
    state: record.state,
    filePresent: record.filePresent,
    sizeBytes: record.sizeBytes,
    mtimeMs: record.mtimeMs,
    sha256: record.sha256,
    sourceRecord: record.sourceRecord,
    metadata: record.metadata || {},
    provenance: record.provenance || {},
    issues: record.issues || [],
  })).sort((left, right) => left.assetKey.localeCompare(right.assetKey));
  const normalizedRegistrations = appRegistrations.map((registration) => ({
    registrationKey: registration.registrationKey,
    assetKey: registration.assetKey,
    sourcePath: registration.sourcePath,
    speciesId: registration.speciesId,
    kind: registration.kind,
    entryIndex: registration.entryIndex,
    sourceRecord: registration.sourceRecord,
    metadata: registration.metadata || {},
  })).sort((left, right) => left.registrationKey.localeCompare(right.registrationKey));
  return crypto.createHash("sha256").update(
    canonicalJson({ records: normalizedRecords, registrations: normalizedRegistrations }),
    "utf8",
  ).digest("hex");
}

function syncInventory(db, runId, records, appRegistrations, signature) {
  const seenAt = new Date().toISOString();
  const upsertAsset = db.prepare(`
    INSERT INTO asset_inventory(
      asset_key, scope, candidate_id, relative_path, species_id, kind, state,
      file_present, size_bytes, mtime_ms, sha256, source_record, metadata_json,
      provenance_json, issues_json, last_seen, sync_run_id
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(asset_key) DO UPDATE SET
      scope=excluded.scope, candidate_id=excluded.candidate_id,
      relative_path=excluded.relative_path, species_id=excluded.species_id,
      kind=excluded.kind, state=excluded.state, file_present=excluded.file_present,
      size_bytes=excluded.size_bytes, mtime_ms=excluded.mtime_ms,
      sha256=excluded.sha256, source_record=excluded.source_record,
      metadata_json=excluded.metadata_json, provenance_json=excluded.provenance_json,
      issues_json=excluded.issues_json, last_seen=excluded.last_seen,
      sync_run_id=excluded.sync_run_id
  `);
  const upsertRegistration = db.prepare(`
    INSERT INTO asset_app_registrations(
      registration_key, asset_key, source_path, species_id, kind, entry_index,
      source_record, app_metadata_json, last_seen, sync_run_id
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(registration_key) DO UPDATE SET
      asset_key=excluded.asset_key, source_path=excluded.source_path,
      species_id=excluded.species_id, kind=excluded.kind,
      entry_index=excluded.entry_index, source_record=excluded.source_record,
      app_metadata_json=excluded.app_metadata_json, last_seen=excluded.last_seen,
      sync_run_id=excluded.sync_run_id
  `);
  db.exec("BEGIN IMMEDIATE");
  try {
    for (const record of records) {
      upsertAsset.run(
        record.assetKey,
        record.scope,
        record.candidateId,
        record.relativePath,
        record.speciesId,
        record.kind,
        record.state,
        record.filePresent ? 1 : 0,
        record.sizeBytes,
        record.mtimeMs,
        record.sha256,
        record.sourceRecord,
        JSON.stringify(record.metadata || {}),
        JSON.stringify(record.provenance || {}),
        JSON.stringify(record.issues || []),
        seenAt,
        runId,
      );
    }
    for (const registration of appRegistrations) {
      upsertRegistration.run(
        registration.registrationKey,
        registration.assetKey,
        registration.sourcePath,
        registration.speciesId,
        registration.kind,
        registration.entryIndex,
        registration.sourceRecord,
        JSON.stringify(registration.metadata || {}),
        seenAt,
        runId,
      );
    }
    db.prepare("DELETE FROM asset_inventory WHERE sync_run_id <> ?").run(runId);
    db.prepare("DELETE FROM asset_app_registrations WHERE sync_run_id <> ?").run(runId);
    db.prepare(`
      INSERT INTO metadata(key, value) VALUES ('inventory_success_signature_v1', ?)
      ON CONFLICT(key) DO UPDATE SET value=excluded.value
    `).run(signature);
    db.prepare(`
      UPDATE inventory_sync_runs SET completed_at=?, status='complete',
        item_count=?, app_registration_count=?, error=NULL WHERE id=?
    `).run(seenAt, records.length, appRegistrations.length, runId);
    db.exec("COMMIT");
  } catch (error) {
    db.exec("ROLLBACK");
    throw error;
  }
}

function listImages(config, db, suppliedSyncState = null) {
  let syncState = suppliedSyncState;
  if (!syncState) {
    syncState = INVENTORY_SYNC_STATES.get(db);
    if (!syncState) {
      syncState = { lastSignature: null };
      INVENTORY_SYNC_STATES.set(db, syncState);
    }
  }
  let runId = null;
  try {
    const manifest = loadAtlasCandidateManifest(config);
    markIntegratedCandidates(db, manifest);
    const pending = listPendingCandidates(config, db);
    const integration = listIntegrationCandidates(config, db);
    const atlas = listAtlasImages(config, db, manifest);
    const appRecords = appInventoryRecords(config, db, manifest);
    const activeRecords = [
      ...appRecords.inventory,
      ...pending.map((item) => itemInventoryRecord(config, item)),
      ...integration.map((item) => itemInventoryRecord(config, item)),
    ];
    const signature = inventorySignature(activeRecords, appRecords.appRegistrations);
    const images = [...pending, ...integration, ...atlas]
      .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
    if (syncState.lastSignature === signature) return images;
    runId = beginInventorySync(db);
    syncInventory(db, runId, activeRecords, appRecords.appRegistrations, signature);
    syncState.lastSignature = signature;
    return images;
  } catch (error) {
    try {
      if (runId === null) runId = beginInventorySync(db);
      failInventorySync(db, runId, error);
    } catch (recordError) {
      if (!config.quiet) console.error(`Unable to record inventory sync error: ${recordError.message}`);
    }
    throw error;
  }
}

function inferDinoGroup(name) {
  const base = path.basename(name, path.extname(name)).toLowerCase();
  const stopWords = new Set([
    "imagegen", "source", "candidate", "review", "sheet", "contact", "crops", "mask",
    "comparison", "ecology", "pattern", "guide", "bodylock", "controlnet", "lora", "i2i",
    "inpaint", "clean", "rejected", "options", "current", "samples", "gallery",
  ]);
  const cut = [];
  for (const part of base.split("-").filter(Boolean)) {
    if (/^v\d+$/.test(part) || /^p\d+$/.test(part) || /^\d+$/.test(part) || stopWords.has(part)) break;
    cut.push(part);
    if (cut.length >= 2) break;
  }
  const group = cut.length ? cut.join("-") : "misc";
  return SPECIES_ALIASES[group] || group;
}

function dinoLabel(config, group, koreanNames = loadAtlasKoreanNames(config)) {
  const scientific = group.split("-").map((part, index) => index === 0 ? `${part[0]?.toUpperCase() || ""}${part.slice(1)}` : part).join(" ");
  const korean = koreanNames[group];
  return korean ? `${korean} (${scientific})` : scientific;
}

function mimeFor(file) {
  const ext = path.extname(file).toLowerCase();
  if (ext === ".jpg" || ext === ".jpeg") return "image/jpeg";
  if (ext === ".webp") return "image/webp";
  return "image/png";
}

function accessKeyMatches(provided, expected) {
  if (!expected) return true;
  if (typeof provided !== "string") return false;
  const left = Buffer.from(provided);
  const right = Buffer.from(expected);
  return left.length === right.length && crypto.timingSafeEqual(left, right);
}

function assertAuthorized(req, url, config, mutation = false) {
  if (!config.accessKey) return;
  const header = req.headers["x-dino-review-key"];
  const query = url.searchParams.get("key");
  const provided = mutation ? header : (header || query);
  if (!accessKeyMatches(provided, config.accessKey)) throw new HttpError(403, "forbidden", "forbidden");
}

function assertLocalHostAndOrigin(req) {
  let host;
  try {
    host = new URL(`http://${req.headers.host || ""}`);
  } catch {
    throw new HttpError(403, "invalid host", "invalid_host");
  }
  if (!new Set(["127.0.0.1", "localhost", "[::1]"]).has(host.hostname)) {
    throw new HttpError(403, "non-local host rejected", "invalid_host");
  }
  const originHeader = req.headers.origin;
  if (!originHeader) return;
  let origin;
  try {
    origin = new URL(originHeader);
  } catch {
    throw new HttpError(403, "invalid origin", "invalid_origin");
  }
  if (origin.protocol !== "http:" || origin.host !== host.host || !new Set(["127.0.0.1", "localhost", "[::1]"]).has(origin.hostname)) {
    throw new HttpError(403, "origin rejected", "invalid_origin");
  }
}

function assertJsonRequest(req) {
  const type = String(req.headers["content-type"] || "").split(";", 1)[0].trim().toLowerCase();
  if (type !== "application/json") throw new HttpError(415, "application/json required", "unsupported_media_type");
}

function readJsonBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let size = 0;
    let tooLarge = false;
    req.on("data", (chunk) => {
      size += chunk.length;
      if (size > MAX_JSON_BODY_BYTES) tooLarge = true;
      else if (!tooLarge) chunks.push(chunk);
    });
    req.on("end", () => {
      if (tooLarge) {
        reject(new HttpError(413, "body too large", "body_too_large"));
        return;
      }
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString("utf8")));
      } catch {
        reject(new HttpError(400, "bad json", "bad_json"));
      }
    });
    req.on("error", reject);
  });
}

function sendJson(res, status, value) {
  res.writeHead(status, { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", "x-content-type-options": "nosniff" });
  res.end(JSON.stringify(value));
}

function sendText(res, status, value) {
  res.writeHead(status, { "content-type": "text/plain; charset=utf-8", "cache-control": "no-store", "x-content-type-options": "nosniff" });
  res.end(value);
}

function pendingIdFromBody(body) {
  const idCandidate = String(body.id || "").startsWith("pending:") ? String(body.id).slice(8) : "";
  if (body.candidateId && idCandidate && String(body.candidateId) !== idCandidate) {
    throw new HttpError(400, "id and candidateId do not match", "candidate_id_mismatch");
  }
  const explicit = body.candidateId || idCandidate;
  return requireSafeCandidateId(explicit);
}

function assertAtlasAsset(config, name) {
  const filename = requireSafeFilename(name);
  const file = directChild(config.assetDir, filename);
  const manifest = loadAtlasCandidateManifest(config);
  if (!isRegularNonLink(file) || !isAtlasVisibleCandidate(filename, manifest)) {
    throw new HttpError(404, "image not found", "image_not_found");
  }
  return file;
}

function inspectMutablePendingCandidate(config, db, candidateId) {
  const inventory = db.prepare(`
    SELECT state FROM asset_inventory WHERE asset_key=?
  `).get(`pending:${candidateId}`);
  if (inventory?.state === "invalid") {
    throw new HttpError(409, "invalid candidates are read-only", "invalid_candidate");
  }
  try {
    return inspectPendingCandidate(config, db, candidateId, { requirePendingState: true });
  } catch (error) {
    if (error instanceof HttpError && error.status === 400) {
      throw new HttpError(409, "invalid candidates are read-only", "invalid_candidate");
    }
    throw error;
  }
}

async function handleSaveReview(req, res, url, config, db) {
  assertAuthorized(req, url, config, true);
  assertLocalHostAndOrigin(req);
  assertJsonRequest(req);
  const body = await readJsonBody(req);
  const status = String(body.status || "unreviewed");
  const note = String(body.note || "").slice(0, 2000);
  if (!REVIEW_STATUSES.has(status)) throw new HttpError(400, "bad review status", "invalid_review");
  const scope = body.scope === "pending"
    || Boolean(body.candidateId)
    || String(body.id || "").startsWith("pending:")
    ? "pending"
    : "atlas";
  let assetId;
  let candidate;
  let binding;
  if (scope === "pending") {
    const candidateId = pendingIdFromBody(body);
    candidate = inspectMutablePendingCandidate(config, db, candidateId);
    assetId = `pending:${candidateId}`;
    binding = { imageSha256: candidate.imageSha256, manifestSha256: candidate.manifestSha256 };
  } else {
    assetId = requireSafeFilename(body.id);
    const atlasFile = assertAtlasAsset(config, assetId);
    binding = { imageSha256: sha256File(atlasFile), manifestSha256: null };
  }
  const review = saveReviewRow(db, scope, assetId, status, note, binding);
  if (scope === "atlas" && binding.imageSha256) {
    db.prepare(`
      UPDATE asset_inventory SET sha256=? WHERE asset_key=?
    `).run(binding.imageSha256, `app:assets/dinosaurs/${assetId}`);
  }
  if (candidate) addCandidateEvent(db, candidate.candidateId, "review-updated", { status, note });
  sendJson(res, 200, {
    ok: true,
    review,
    ...(candidate ? { canPromote: review?.status === "pass" && candidate.metadataIssues.length === 0 } : {}),
  });
}

function writePromotionRecordAtomically(config, candidateId, record) {
  ensurePlainDirectory(config.promotionDir);
  const finalRecord = directChild(config.promotionDir, `${candidateId}.json`);
  if (fs.existsSync(finalRecord)) throw new HttpError(409, "promotion record already exists", "promotion_record_exists");
  const tempName = `.${candidateId}.${process.pid}.${crypto.randomBytes(6).toString("hex")}.tmp`;
  const tempRecord = directChild(config.promotionDir, tempName);
  try {
    const fd = fs.openSync(tempRecord, "wx");
    try {
      fs.writeFileSync(fd, `${JSON.stringify(record, null, 2)}\n`, "utf8");
      fs.fsyncSync(fd);
    } finally {
      fs.closeSync(fd);
    }
    fs.linkSync(tempRecord, finalRecord);
    fs.unlinkSync(tempRecord);
  } catch (error) {
    if (fs.existsSync(tempRecord)) fs.unlinkSync(tempRecord);
    throw error;
  }
  return finalRecord;
}

function cleanupPendingFiles(config, paths, operationPrefix) {
  const warnings = [];
  if (paths.imageFile && fs.existsSync(paths.imageFile)) {
    try {
      unlinkWithFault(config, paths.imageFile, `${operationPrefix}-image`);
    } catch (error) {
      warnings.push({ step: "image", code: error.code || "ERROR", message: error.message });
      return warnings;
    }
  }
  if (paths.manifestFile && fs.existsSync(paths.manifestFile)) {
    try {
      unlinkWithFault(config, paths.manifestFile, `${operationPrefix}-manifest`);
    } catch (error) {
      warnings.push({ step: "manifest", code: error.code || "ERROR", message: error.message });
      return warnings;
    }
  }
  if (paths.candidateDir && fs.existsSync(paths.candidateDir)) {
    try {
      injectFault(config, `${operationPrefix}-directory`, paths.candidateDir);
      fs.rmdirSync(paths.candidateDir);
    } catch (error) {
      warnings.push({ step: "directory", code: error.code || "ERROR", message: error.message });
    }
  }
  return warnings;
}

function appendCleanupWarning(db, candidateId, phase, warnings) {
  if (!warnings.length) return;
  try {
    addCandidateEvent(db, candidateId, "cleanup-warning", { phase, warnings });
  } catch (error) {
    console.error(`Unable to record cleanup warning for ${candidateId}:`, error?.message || error);
  }
}

function beginPromotionIntent(db, candidate, hash, startedAt, record) {
  db.exec("BEGIN IMMEDIATE");
  try {
    const update = db.prepare(`
      UPDATE candidates SET state = 'promotion-in-progress', target_path = ?, sha256 = ?,
        manifest_json = ?, updated_at = ? WHERE candidate_id = ? AND state = 'pending'
    `).run(candidate.targetPath, hash, JSON.stringify(candidate.manifest), startedAt, candidate.candidateId);
    if (Number(update.changes) !== 1) {
      throw new HttpError(409, "candidate state changed", "candidate_state_conflict");
    }
    addCandidateEvent(db, candidate.candidateId, "promotion-in-progress", record);
    db.exec("COMMIT");
  } catch (error) {
    db.exec("ROLLBACK");
    throw error;
  }
}

function restorePromotionPending(db, candidateId, detail) {
  db.exec("BEGIN IMMEDIATE");
  try {
    const update = db.prepare(`
      UPDATE candidates SET state = 'pending', updated_at = ?
      WHERE candidate_id = ? AND state = 'promotion-in-progress'
    `).run(new Date().toISOString(), candidateId);
    if (Number(update.changes) !== 1) {
      throw new HttpError(409, "candidate state changed during promotion recovery", "candidate_state_conflict");
    }
    db.exec("COMMIT");
  } catch (error) {
    db.exec("ROLLBACK");
    throw error;
  }
  try {
    addCandidateEvent(db, candidateId, "promotion-failed", detail);
  } catch (error) {
    console.error(`Unable to record promotion failure for ${candidateId}:`, error?.message || error);
  }
}

function removeCreatedPromotionArtifacts(destination, recordFile) {
  const errors = [];
  for (const [role, file] of [["record", recordFile], ["destination", destination]]) {
    if (!file || !fs.existsSync(file)) continue;
    try {
      fs.unlinkSync(file);
    } catch (error) {
      errors.push({ role, code: error.code || "ERROR", message: error.message });
    }
  }
  return errors;
}

async function handlePromote(req, res, url, config, db) {
  assertAuthorized(req, url, config, true);
  assertLocalHostAndOrigin(req);
  assertJsonRequest(req);
  const body = await readJsonBody(req);
  const candidateId = pendingIdFromBody(body);
  const candidate = inspectMutablePendingCandidate(config, db, candidateId);
  const assetId = `pending:${candidateId}`;
  const review = getReview(db, "pending", assetId);
  if (review?.status !== "pass") throw new HttpError(409, "candidate review must be pass", "review_not_passed");
  if (!reviewMatchesCandidate(review, candidate)) {
    throw new HttpError(409, "candidate changed after review", "candidate_changed_after_review");
  }
  if (candidate.metadataIssues.length) {
    throw new HttpError(409, "candidate metadata is incomplete", "metadata_incomplete");
  }
  ensurePlainDirectory(config.assetDir);
  const destination = directChild(config.assetDir, candidate.targetFilename);
  if (fs.existsSync(destination)) throw new HttpError(409, "target asset already exists", "target_exists");
  const stat = fs.statSync(candidate.imageFile);
  const hash = sha256File(candidate.imageFile);
  const promotedAt = new Date().toISOString();
  const promotionRecord = {
    schemaVersion: 1,
    candidateId,
    disposition: "promoted-awaiting-app-integration",
    promotedAt,
    sourcePath: `tools/dino-review/pending/${candidateId}/${candidate.filename}`,
    targetPath: candidate.targetPath,
    filename: candidate.targetFilename,
    sha256: hash,
    sizeBytes: stat.size,
    review,
    candidate: candidate.manifest,
  };
  let recordFile;
  let destinationCreated = false;
  beginPromotionIntent(db, candidate, hash, promotedAt, promotionRecord);
  try {
    fs.copyFileSync(candidate.imageFile, destination, fs.constants.COPYFILE_EXCL);
    destinationCreated = true;
    if (sha256File(destination) !== hash) throw new Error("promoted copy hash mismatch");
    recordFile = writePromotionRecordAtomically(config, candidateId, promotionRecord);
    db.exec("BEGIN IMMEDIATE");
    try {
      const update = db.prepare(`
        UPDATE candidates SET state = 'promoted-awaiting-app-integration', target_path = ?,
          sha256 = ?, manifest_json = ?, updated_at = ? WHERE candidate_id = ? AND state = 'promotion-in-progress'
      `).run(candidate.targetPath, hash, JSON.stringify(candidate.manifest), promotedAt, candidateId);
      if (Number(update.changes) !== 1) {
        throw new HttpError(409, "candidate state changed", "candidate_state_conflict");
      }
      addCandidateEvent(db, candidateId, "promoted-awaiting-app-integration", promotionRecord);
      db.exec("COMMIT");
    } catch (error) {
      db.exec("ROLLBACK");
      throw error;
    }
  } catch (error) {
    const destinationForRollback = destinationCreated || error.code !== "EEXIST" ? destination : null;
    const rollbackErrors = removeCreatedPromotionArtifacts(
      destinationForRollback,
      recordFile || directChild(config.promotionDir, `${candidateId}.json`),
    );
    try {
      restorePromotionPending(db, candidateId, {
        error: error.message,
        rollbackErrors,
        sourcePreserved: fs.existsSync(candidate.imageFile),
      });
    } catch (restoreError) {
      console.error(`Unable to restore promotion intent for ${candidateId}:`, restoreError?.stack || restoreError);
    }
    throw error;
  }
  const cleanupWarnings = cleanupPendingFiles(config, candidate, "promotion-cleanup");
  appendCleanupWarning(db, candidateId, "promotion", cleanupWarnings);
  const relativeRecord = path.relative(config.root, recordFile).split(path.sep).join("/");
  sendJson(res, 200, {
    ok: true,
    candidateId,
    state: "promoted-awaiting-app-integration",
    targetPath: candidate.targetPath,
    projectAsset: candidate.targetPath,
    promotionRecord: relativeRecord,
    cleanupWarning: cleanupWarnings.length ? cleanupWarnings : null,
  });
}

function beginDeleteIntent(db, candidate, reason, hash, startedAt) {
  db.exec("BEGIN IMMEDIATE");
  try {
    const update = db.prepare(`
      UPDATE candidates SET state = 'delete-in-progress', sha256 = ?, deletion_reason = ?,
        manifest_json = ?, updated_at = ? WHERE candidate_id = ? AND state = 'pending'
    `).run(hash, reason, JSON.stringify(candidate.manifest), startedAt, candidate.candidateId);
    if (Number(update.changes) !== 1) {
      throw new HttpError(409, "candidate state changed", "candidate_state_conflict");
    }
    addCandidateEvent(db, candidate.candidateId, "delete-requested", {
      reason,
      filename: candidate.filename,
      sha256: hash,
    });
    db.exec("COMMIT");
  } catch (error) {
    db.exec("ROLLBACK");
    throw error;
  }
}

function restoreDeletePending(db, candidateId, detail) {
  db.exec("BEGIN IMMEDIATE");
  try {
    const update = db.prepare(`
      UPDATE candidates SET state = 'pending', updated_at = ?
      WHERE candidate_id = ? AND state = 'delete-in-progress'
    `).run(new Date().toISOString(), candidateId);
    if (Number(update.changes) !== 1) {
      throw new HttpError(409, "candidate state changed during delete recovery", "candidate_state_conflict");
    }
    addCandidateEvent(db, candidateId, "delete-failed", detail);
    db.exec("COMMIT");
  } catch (error) {
    db.exec("ROLLBACK");
    throw error;
  }
}

function finalizeDelete(db, candidateId, deletedAt, detail, cleanupWarnings = []) {
  db.exec("BEGIN IMMEDIATE");
  try {
    const update = db.prepare(`
      UPDATE candidates SET state = 'deleted-rejected', updated_at = ?
      WHERE candidate_id = ? AND state = 'delete-in-progress'
    `).run(deletedAt, candidateId);
    if (Number(update.changes) !== 1) {
      throw new HttpError(409, "candidate state changed", "candidate_state_conflict");
    }
    addCandidateEvent(db, candidateId, "deleted-rejected", detail);
    if (cleanupWarnings.length) {
      addCandidateEvent(db, candidateId, "cleanup-warning", { phase: "delete", warnings: cleanupWarnings });
    }
    db.exec("COMMIT");
  } catch (error) {
    db.exec("ROLLBACK");
    throw error;
  }
}

async function handleDelete(req, res, url, config, db) {
  assertAuthorized(req, url, config, true);
  assertLocalHostAndOrigin(req);
  assertJsonRequest(req);
  const body = await readJsonBody(req);
  const candidateId = pendingIdFromBody(body);
  const candidate = inspectMutablePendingCandidate(config, db, candidateId);
  const review = getReview(db, "pending", `pending:${candidateId}`);
  const reason = String(body.reason || "").trim().slice(0, 2000);
  if (review?.status !== "reject") throw new HttpError(409, "candidate review must be reject", "review_not_rejected");
  if (!reviewMatchesCandidate(review, candidate)) {
    throw new HttpError(409, "candidate changed after review", "candidate_changed_after_review");
  }
  if (!review.note.trim() || !reason) throw new HttpError(400, "rejection reason required", "reason_required");
  if (String(body.confirmName || "") !== candidate.filename) {
    throw new HttpError(400, "filename confirmation does not match", "confirmation_mismatch");
  }
  const deletedAt = new Date().toISOString();
  const hash = sha256File(candidate.imageFile);
  beginDeleteIntent(db, candidate, reason, hash, deletedAt);
  try {
    unlinkWithFault(config, candidate.imageFile, "delete-image");
  } catch (error) {
    restoreDeletePending(db, candidateId, {
      reason,
      filename: candidate.filename,
      sha256: hash,
      error: error.message,
    });
    throw new HttpError(500, "candidate image deletion failed", "delete_failed");
  }
  const cleanupWarnings = cleanupPendingFiles(config, {
    imageFile: null,
    manifestFile: candidate.manifestFile,
    candidateDir: candidate.candidateDir,
  }, "delete-cleanup");
  finalizeDelete(db, candidateId, deletedAt, {
    reason,
    filename: candidate.filename,
    sha256: hash,
  }, cleanupWarnings);
  sendJson(res, 200, {
    ok: true,
    candidateId,
    state: "deleted-rejected",
    cleanupWarning: cleanupWarnings.length ? cleanupWarnings : null,
  });
}

function recoveryPaths(config, row) {
  const candidateId = requireSafeCandidateId(row.candidateId);
  const filename = requireSafeFilename(row.filename);
  const candidateDir = directChild(config.pendingDir, candidateId);
  const targetFilename = requireSafeFilename(path.basename(String(row.targetPath || "")));
  return {
    candidateId,
    candidateDir,
    imageFile: directChild(candidateDir, filename),
    manifestFile: directChild(candidateDir, "candidate.json"),
    destination: directChild(config.assetDir, targetFilename),
    recordFile: directChild(config.promotionDir, `${candidateId}.json`),
  };
}

function fileMatchesHash(file, expectedHash) {
  return Boolean(expectedHash && isRegularNonLink(file) && sha256File(file) === expectedHash);
}

function promotionRecordMatches(file, candidateId, expectedHash) {
  if (!isRegularNonLink(file)) return false;
  try {
    const record = JSON.parse(fs.readFileSync(file, "utf8"));
    return record.candidateId === candidateId && record.sha256 === expectedHash;
  } catch {
    return false;
  }
}

function addRecoveryWarning(db, candidateId, phase, warnings) {
  try {
    addCandidateEvent(db, candidateId, "recovery-warning", { phase, warnings });
  } catch (error) {
    console.error(`Unable to record recovery warning for ${candidateId}:`, error?.message || error);
  }
}

function reconcilePromotionIntent(config, db, row) {
  const paths = recoveryPaths(config, row);
  const warnings = [];
  if (!fileMatchesHash(paths.imageFile, row.sha256)) {
    warnings.push({ step: "source", message: "pending source missing, unsafe, or hash-mismatched" });
    addRecoveryWarning(db, row.candidateId, "promotion-in-progress", warnings);
    return;
  }
  if (fs.existsSync(paths.destination)) {
    if (!fileMatchesHash(paths.destination, row.sha256)) {
      warnings.push({ step: "destination", message: "orphan destination hash mismatch; not removed" });
    } else {
      try {
        fs.unlinkSync(paths.destination);
      } catch (error) {
        warnings.push({ step: "destination", code: error.code || "ERROR", message: error.message });
      }
    }
  }
  if (fs.existsSync(paths.recordFile)) {
    if (!promotionRecordMatches(paths.recordFile, row.candidateId, row.sha256)) {
      warnings.push({ step: "record", message: "orphan promotion record mismatch; not removed" });
    } else {
      try {
        fs.unlinkSync(paths.recordFile);
      } catch (error) {
        warnings.push({ step: "record", code: error.code || "ERROR", message: error.message });
      }
    }
  }
  if (warnings.length) {
    addRecoveryWarning(db, row.candidateId, "promotion-in-progress", warnings);
    return;
  }
  restorePromotionPending(db, row.candidateId, { recoveredAtStartup: true, sourcePreserved: true });
}

function reconcilePromotedCleanup(config, db, row) {
  const paths = recoveryPaths(config, row);
  if (!fs.existsSync(paths.candidateDir)) return;
  const warnings = [];
  if (!fileMatchesHash(paths.destination, row.sha256)) {
    warnings.push({ step: "destination", message: "promoted destination missing, unsafe, or hash-mismatched" });
    addRecoveryWarning(db, row.candidateId, "promoted-cleanup", warnings);
    return;
  }
  if (fs.existsSync(paths.imageFile) && !fileMatchesHash(paths.imageFile, row.sha256)) {
    warnings.push({ step: "source", message: "leftover pending source is hash-mismatched" });
    addRecoveryWarning(db, row.candidateId, "promoted-cleanup", warnings);
    return;
  }
  const cleanupWarnings = cleanupPendingFiles(config, paths, "startup-promotion-cleanup");
  appendCleanupWarning(db, row.candidateId, "startup-promotion", cleanupWarnings);
}

function reconcileDeleteIntent(config, db, row) {
  const paths = recoveryPaths(config, row);
  const detail = {
    reason: row.deletionReason || "recovered delete intent",
    filename: row.filename,
    sha256: row.sha256,
    recoveredAtStartup: true,
  };
  if (fs.existsSync(paths.imageFile)) {
    if (!fileMatchesHash(paths.imageFile, row.sha256)) {
      restoreDeletePending(db, row.candidateId, { ...detail, error: "pending source hash mismatch during recovery" });
      return;
    }
    try {
      unlinkWithFault(config, paths.imageFile, "startup-delete-image");
    } catch (error) {
      restoreDeletePending(db, row.candidateId, { ...detail, error: error.message });
      return;
    }
  }
  const cleanupWarnings = cleanupPendingFiles(config, {
    imageFile: null,
    manifestFile: paths.manifestFile,
    candidateDir: paths.candidateDir,
  }, "startup-delete-cleanup");
  finalizeDelete(db, row.candidateId, new Date().toISOString(), detail, cleanupWarnings);
}

function reconcileCandidateStates(config, db) {
  const rows = db.prepare(`
    SELECT candidate_id AS candidateId, filename, state, target_path AS targetPath,
      sha256, deletion_reason AS deletionReason
    FROM candidates
    WHERE state IN ('promotion-in-progress', 'promoted-awaiting-app-integration', 'delete-in-progress')
    ORDER BY candidate_id
  `).all();
  for (const row of rows) {
    try {
      if (row.state === "promotion-in-progress") reconcilePromotionIntent(config, db, row);
      else if (row.state === "promoted-awaiting-app-integration") reconcilePromotedCleanup(config, db, row);
      else reconcileDeleteIntent(config, db, row);
    } catch (error) {
      addRecoveryWarning(db, row.candidateId, row.state, [{ code: error.code || "ERROR", message: error.message }]);
    }
  }
}

function htmlSecurityHeaders() {
  return {
    "content-security-policy": "default-src 'self'; img-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
    "referrer-policy": "no-referrer",
    "x-frame-options": "DENY",
    "x-content-type-options": "nosniff",
  };
}

function parseInventoryMetadata(row) {
  try {
    return JSON.parse(row?.metadataJson || "{}");
  } catch {
    return {};
  }
}

function quarantineMediaFile(config, db, candidateId, filename) {
  const row = db.prepare(`
    SELECT state, metadata_json AS metadataJson
    FROM asset_inventory WHERE asset_key=?
  `).get(`pending:${candidateId}`);
  if (!row || row.state !== "invalid") throw new HttpError(404, "quarantine image not found", "image_not_found");
  const metadata = parseInventoryMetadata(row);
  const folder = String(metadata.pendingFolder || "");
  const expectedFilename = String(metadata.quarantineFilename || "");
  if (!folder || folder !== path.basename(folder) || expectedFilename !== filename) {
    throw new HttpError(404, "quarantine image not found", "image_not_found");
  }
  const candidateDir = directChild(config.pendingDir, folder);
  const dirStat = fs.lstatSync(candidateDir);
  if (!dirStat.isDirectory() || dirStat.isSymbolicLink()) {
    throw new HttpError(404, "quarantine image not found", "image_not_found");
  }
  const file = directChild(candidateDir, filename);
  if (!isRegularNonLink(file)) throw new HttpError(404, "quarantine image not found", "image_not_found");
  assertPng(file);
  return file;
}

function promotedMediaFile(config, db, candidateId, filename) {
  const row = db.prepare(`
    SELECT state, target_path AS targetPath, sha256
    FROM candidates WHERE candidate_id=?
  `).get(candidateId);
  if (!row || row.state !== "promoted-awaiting-app-integration") {
    throw new HttpError(404, "promoted image not found", "image_not_found");
  }
  if (row.targetPath !== `assets/dinosaurs/${filename}`) {
    throw new HttpError(404, "promoted image not found", "image_not_found");
  }
  const file = directChild(config.assetDir, filename);
  if (!fileMatchesHash(file, row.sha256)) {
    throw new HttpError(409, "promoted image hash mismatch", "promoted_asset_changed");
  }
  return file;
}

function urlHost(host) {
  return String(host).includes(":") ? `[${host}]` : host;
}

function createReviewApp(overrides = {}) {
  const config = defaultConfig(overrides);
  ensurePlainDirectory(config.pendingDir);
  ensurePlainDirectory(config.assetDir);
  ensurePlainDirectory(config.promotionDir);
  const db = openReviewDatabase(config);
  reconcileCandidateStates(config, db);
  let closed = false;
  const handler = async (req, res) => {
    try {
      const url = new URL(req.url, `http://${urlHost(config.host)}:${config.port}`);
      if (url.pathname === "/" || url.pathname === "/index.html") {
        assertAuthorized(req, url, config, false);
        assertLocalHostAndOrigin(req);
        const html = fs.readFileSync(config.indexFile);
        res.writeHead(200, {
          "content-type": "text/html; charset=utf-8",
          "cache-control": "no-store",
          ...htmlSecurityHeaders(),
        });
        res.end(html);
        return;
      }
      if (url.pathname === "/api/images" && req.method === "GET") {
        assertAuthorized(req, url, config, false);
        assertLocalHostAndOrigin(req);
        const images = listImages(config, db);
        const speciesCounts = new Map();
        for (const image of images) {
          const current = speciesCounts.get(image.species) || { id: image.species, label: image.speciesLabel, count: 0 };
          current.count += 1;
          speciesCounts.set(image.species, current);
        }
        sendJson(res, 200, {
          generatedAt: new Date().toISOString(),
          images,
          species: [...speciesCounts.values()].sort((a, b) => a.label.localeCompare(b.label, "ko")),
          kinds: [...new Set(images.map((image) => image.kind))].sort(),
        });
        return;
      }
      if (url.pathname === "/api/health" && req.method === "GET") {
        assertAuthorized(req, url, config, false);
        assertLocalHostAndOrigin(req);
        sendJson(res, 200, { ok: true, service: "dino-review", schemaVersion: 1, database: "sqlite" });
        return;
      }
      if (url.pathname === "/api/review" && req.method === "POST") {
        await handleSaveReview(req, res, url, config, db);
        return;
      }
      if (url.pathname === "/api/pending/promote" && req.method === "POST") {
        await handlePromote(req, res, url, config, db);
        return;
      }
      if (url.pathname === "/api/pending/delete" && req.method === "POST") {
        await handleDelete(req, res, url, config, db);
        return;
      }
      if (url.pathname.startsWith("/pending-media/") && req.method === "GET") {
        assertAuthorized(req, url, config, false);
        assertLocalHostAndOrigin(req);
        const raw = url.pathname.slice("/pending-media/".length).split("/");
        if (raw.length !== 2) throw new HttpError(400, "invalid pending media path", "invalid_path");
        let candidateId;
        let filename;
        try {
          candidateId = requireSafeCandidateId(decodeURIComponent(raw[0]));
          filename = requireSafeFilename(decodeURIComponent(raw[1]));
        } catch (error) {
          if (error instanceof URIError) throw new HttpError(400, "invalid path encoding", "invalid_path");
          throw error;
        }
        const candidate = inspectPendingCandidate(config, db, candidateId);
        if (filename !== candidate.filename) throw new HttpError(404, "pending image not found", "image_not_found");
        res.writeHead(200, { "content-type": "image/png", "cache-control": "no-store", "x-content-type-options": "nosniff" });
        fs.createReadStream(candidate.imageFile).pipe(res);
        return;
      }
      if (url.pathname.startsWith("/quarantine-media/") && req.method === "GET") {
        assertAuthorized(req, url, config, false);
        assertLocalHostAndOrigin(req);
        const raw = url.pathname.slice("/quarantine-media/".length).split("/");
        if (raw.length !== 2) throw new HttpError(400, "invalid quarantine media path", "invalid_path");
        let candidateId;
        let filename;
        try {
          candidateId = requireSafeCandidateId(decodeURIComponent(raw[0]));
          filename = requireSafeFilename(decodeURIComponent(raw[1]));
        } catch (error) {
          if (error instanceof URIError) throw new HttpError(400, "invalid path encoding", "invalid_path");
          throw error;
        }
        const file = quarantineMediaFile(config, db, candidateId, filename);
        res.writeHead(200, { "content-type": "image/png", "cache-control": "no-store", "x-content-type-options": "nosniff" });
        fs.createReadStream(file).pipe(res);
        return;
      }
      if (url.pathname.startsWith("/promoted-media/") && req.method === "GET") {
        assertAuthorized(req, url, config, false);
        assertLocalHostAndOrigin(req);
        const raw = url.pathname.slice("/promoted-media/".length).split("/");
        if (raw.length !== 2) throw new HttpError(400, "invalid promoted media path", "invalid_path");
        let candidateId;
        let filename;
        try {
          candidateId = requireSafeCandidateId(decodeURIComponent(raw[0]));
          filename = requireSafeFilename(decodeURIComponent(raw[1]));
        } catch (error) {
          if (error instanceof URIError) throw new HttpError(400, "invalid path encoding", "invalid_path");
          throw error;
        }
        const file = promotedMediaFile(config, db, candidateId, filename);
        res.writeHead(200, { "content-type": "image/png", "cache-control": "no-store", "x-content-type-options": "nosniff" });
        fs.createReadStream(file).pipe(res);
        return;
      }
      if (url.pathname === INVALID_PLACEHOLDER_URL && req.method === "GET") {
        assertAuthorized(req, url, config, false);
        assertLocalHostAndOrigin(req);
        const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="640" height="400" viewBox="0 0 640 400"><rect width="640" height="400" fill="#151b26"/><path d="M210 120h220v160H210z" fill="none" stroke="#d9776b" stroke-width="10"/><path d="m235 250 70-70 48 48 35-35 28 57" fill="none" stroke="#d9776b" stroke-width="10"/><circle cx="375" cy="160" r="14" fill="#d9776b"/><text x="320" y="330" text-anchor="middle" fill="#f3c7c2" font-family="sans-serif" font-size="24">invalid candidate</text></svg>`;
        res.writeHead(200, { "content-type": "image/svg+xml; charset=utf-8", "cache-control": "no-store", "x-content-type-options": "nosniff" });
        res.end(svg);
        return;
      }
      if (url.pathname.startsWith("/image/") && req.method === "GET") {
        assertAuthorized(req, url, config, false);
        assertLocalHostAndOrigin(req);
        let name;
        try {
          name = requireSafeFilename(decodeURIComponent(url.pathname.slice("/image/".length)));
        } catch (error) {
          if (error instanceof URIError) throw new HttpError(400, "invalid path encoding", "invalid_path");
          throw error;
        }
        const full = assertAtlasAsset(config, name);
        res.writeHead(200, { "content-type": mimeFor(full), "cache-control": "no-store", "x-content-type-options": "nosniff" });
        fs.createReadStream(full).pipe(res);
        return;
      }
      throw new HttpError(404, "not found", "not_found");
    } catch (error) {
      if (res.headersSent) {
        res.destroy(error);
        return;
      }
      const status = error instanceof HttpError ? error.status : 500;
      const message = error instanceof HttpError ? error.message : "internal server error";
      const code = error instanceof HttpError ? error.code : "internal_error";
      if (urlLooksLikeApi(req.url)) sendJson(res, status, { error: message, code });
      else sendText(res, status, message);
      if (!(error instanceof HttpError) && !config.quiet) console.error(error?.stack || error);
    }
  };
  return {
    config,
    db,
    handler,
    close() {
      if (!closed) {
        closed = true;
        db.close();
      }
    },
  };
}

function urlLooksLikeApi(value) {
  return String(value || "").startsWith("/api/");
}

function startReviewServer(overrides = {}) {
  const startupConfig = defaultConfig(overrides);
  if (!startupConfig.accessKey) {
    throw new Error("DINO_REVIEW_KEY is required to start the review server");
  }
  if (!LOOPBACK_HOSTS.has(String(startupConfig.host).toLowerCase())) {
    throw new Error("DINO_REVIEW_HOST must be a loopback host");
  }
  let app;
  try {
    app = createReviewApp({ ...overrides, accessKey: startupConfig.accessKey });
  } catch (error) {
    app?.close();
    throw error;
  }
  const server = http.createServer(app.handler);
  server.once("close", app.close);
  server.once("error", (error) => {
    app.close();
    process.exitCode = 1;
    if (!app.config.quiet) {
      console.error(error?.stack || error);
    }
  });
  try {
    server.listen(app.config.port, app.config.host, () => {
      if (!app.config.quiet) {
        const address = server.address();
        console.log(`Dino review listening on http://${app.config.host}:${address.port}`);
      }
    });
  } catch (error) {
    app.close();
    throw error;
  }
  return { server, app };
}

module.exports = {
  HttpError,
  PROMOTABLE_KINDS,
  assertPng,
  createReviewApp,
  defaultConfig,
  inspectPendingCandidate,
  isVersionedSpeciesPng,
  loadAtlasCandidateManifest,
  listAtlasImages,
  listImages,
  openReviewDatabase,
  reconcileCandidateStates,
  requireSafeCandidateId,
  startReviewServer,
};
