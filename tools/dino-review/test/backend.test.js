const assert = require("node:assert/strict");
const crypto = require("crypto");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { once } = require("events");
const test = require("node:test");
const {
  assertPng,
  defaultConfig,
  listAtlasImages,
  listImages,
  loadAtlasCandidateManifest,
  openReviewDatabase,
  reconcileCandidateStates,
  startReviewServer,
} = require("../backend");
const { enqueueCandidate } = require("../enqueue");

const PNG = Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9Z0xkAAAAASUVORK5CYII=", "base64");

test("refuses to start a listening server without an access key", () => {
  assert.throws(
    () => startReviewServer({ accessKey: "", quiet: true }),
    /DINO_REVIEW_KEY is required/,
  );
});

test("refuses non-loopback listeners", () => {
  assert.throws(
    () => startReviewServer({ host: "0.0.0.0", accessKey: "test-secret", quiet: true }),
    /loopback host/,
  );
});

test("migrates an existing reviews table with immutable binding columns", () => {
  const { DatabaseSync } = require("node:sqlite");
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "dino-review-migration-"));
  const dbPath = path.join(temp, "old.sqlite");
  const old = new DatabaseSync(dbPath);
  old.exec(`
    CREATE TABLE reviews (
      scope TEXT NOT NULL,
      asset_id TEXT NOT NULL,
      status TEXT NOT NULL,
      note TEXT NOT NULL DEFAULT '',
      updated_at TEXT NOT NULL,
      PRIMARY KEY (scope, asset_id)
    );
  `);
  old.close();
  const config = defaultConfig({ dbPath, legacyReviewFile: path.join(temp, "missing.json") });
  const migrated = openReviewDatabase(config);
  const columns = migrated.prepare("PRAGMA table_info(reviews)").all().map((column) => column.name);
  assert.ok(columns.includes("image_sha256"));
  assert.ok(columns.includes("manifest_sha256"));
  assert.ok(migrated.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='review_events'").get());
  for (const table of ["asset_inventory", "inventory_sync_runs", "asset_app_registrations"]) {
    assert.ok(migrated.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name=?").get(table));
  }
  assert.equal(Number(migrated.prepare("PRAGMA busy_timeout").get().timeout), 5000);
  migrated.close();
  fs.rmSync(temp, { recursive: true, force: true });
});

function writeFixtureApp(file, assetName) {
  fs.writeFileSync(file, `
const dinosaurs = [
  { id: "testosaurus-examplei", koreanName: "테스토사우루스" },
];
const generatedImageSamples = {
  "testosaurus-examplei": [
    {
      kind: "count-level pass",
      source: "assets/dinosaurs/${assetName}",
    },
  ],
};
const approvedVelociraptorCandidateSources = new Set([]);
const verifiedRejectedCandidateSources = new Set([]);
`, "utf8");
}

async function fixture(t, { legacy = {}, faultInjector = null } = {}) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "dino-review-test-"));
  const root = path.join(temp, "repo");
  const assetDir = path.join(root, "assets", "dinosaurs");
  const reviewDir = path.join(root, "tools", "dino-review");
  const dataDir = path.join(reviewDir, "data");
  const pendingDir = path.join(reviewDir, "pending");
  const promotionDir = path.join(reviewDir, "promotions");
  fs.mkdirSync(assetDir, { recursive: true });
  fs.mkdirSync(dataDir, { recursive: true });
  fs.mkdirSync(pendingDir, { recursive: true });
  const atlasName = "testosaurus-examplei-profile-imagegen-v1.png";
  fs.writeFileSync(path.join(assetDir, atlasName), PNG);
  const appFile = path.join(root, "app.js");
  writeFixtureApp(appFile, atlasName);
  const legacyReviewFile = path.join(dataDir, "reviews.json");
  fs.writeFileSync(legacyReviewFile, JSON.stringify(legacy), "utf8");
  const indexFile = path.join(reviewDir, "index.html");
  fs.writeFileSync(indexFile, "<!doctype html><title>review</title>", "utf8");
  const dbPath = path.join(dataDir, "review.sqlite");
  const accessKey = "test-secret";
  const started = startReviewServer({
    host: "127.0.0.1",
    port: 0,
    accessKey,
    root,
    assetDir,
    pendingDir,
    dbPath,
    legacyReviewFile,
    promotionDir,
    indexFile,
    appFile,
    rejectionFile: path.join(root, "missing-rejections.json"),
    faultInjector,
    quiet: true,
  });
  await once(started.server, "listening");
  const address = started.server.address();
  const base = `http://127.0.0.1:${address.port}`;
  t.after(async () => {
    started.server.close();
    started.server.closeAllConnections();
    await once(started.server, "close");
    fs.rmSync(temp, { recursive: true, force: true });
  });
  return {
    ...started,
    db: started.app.db,
    temp,
    root,
    assetDir,
    pendingDir,
    promotionDir,
    dbPath,
    appFile,
    legacyReviewFile,
    atlasName,
    accessKey,
    base,
  };
}

function writeSource(directory, filename) {
  fs.mkdirSync(directory, { recursive: true });
  const file = path.join(directory, filename);
  fs.writeFileSync(file, PNG);
  return file;
}

function completeOptions(sourceFile, candidateId, overrides = {}) {
  return {
    candidateId,
    image: sourceFile,
    speciesId: "testosaurus-examplei",
    kind: "count-level pass",
    source: "project-owned image generation",
    license: "original project-generated bitmap",
    prompt: "scientific educational test reconstruction",
    seed: "service-assigned-not-exposed",
    workflow: "test image generation workflow",
    anatomyStatus: "passed",
    representative: true,
    reviewer: "test-reviewer",
    reviewedAt: "2026-08-10T00:00:00.000Z",
    anatomyNotes: "appendages and silhouette passed",
    ...overrides,
  };
}

async function apiJson(ctx, pathname, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body !== undefined && !headers["content-type"]) headers["content-type"] = "application/json";
  if (options.mutation !== false) headers["x-dino-review-key"] = ctx.accessKey;
  const response = await fetch(`${ctx.base}${pathname}`, {
    method: options.method || (options.body === undefined ? "GET" : "POST"),
    headers,
    body: options.body === undefined ? undefined : (typeof options.body === "string" ? options.body : JSON.stringify(options.body)),
  });
  const data = await response.json().catch(() => null);
  return { response, data };
}

test("imports legacy reviews once and lists compatible atlas plus pending records", async (t) => {
  const ctx = await fixture(t, {
    legacy: {
      "testosaurus-examplei-profile-imagegen-v1.png": {
        status: "hold",
        note: "legacy note",
        updatedAt: "2026-08-01T00:00:00.000Z",
      },
    },
  });
  const source = writeSource(path.join(ctx.temp, "incoming"), "testosaurus-examplei-forest-imagegen-v2.png");
  enqueueCandidate(completeOptions(source, "testosaurus-forest-v2"), { pendingDir: ctx.pendingDir });

  const health = await apiJson(ctx, `/api/health?key=${ctx.accessKey}`, { mutation: false });
  assert.equal(health.response.status, 200);
  assert.deepEqual(health.data, { ok: true, service: "dino-review", schemaVersion: 1, database: "sqlite" });

  const listed = await apiJson(ctx, `/api/images?key=${ctx.accessKey}`, { mutation: false });
  assert.equal(listed.response.status, 200);
  assert.equal(listed.data.images.length, 2);
  const atlas = listed.data.images.find((item) => item.scope === "atlas");
  const pending = listed.data.images.find((item) => item.scope === "pending");
  assert.equal(atlas.id, ctx.atlasName);
  assert.equal(atlas.review.status, "hold");
  assert.equal(pending.id, "pending:testosaurus-forest-v2");
  assert.equal(pending.mediaType, "image/png");
  assert.equal(pending.state, "pending");
  assert.equal(pending.loadError, false);
  assert.equal(pending.canPromote, false);
  assert.deepEqual(pending.metadataIssues, []);
  assert.equal(pending.targetPath, "assets/dinosaurs/testosaurus-examplei-forest-imagegen-v2.png");
  assert.equal(pending.provenance.source, "project-owned image generation");
  assert.equal(pending.anatomyReview.status, "passed");

  const pendingMedia = await fetch(`${ctx.base}${pending.url}?key=${ctx.accessKey}`);
  assert.equal(pendingMedia.status, 200);
  assert.equal(pendingMedia.headers.get("content-type"), "image/png");
  assert.deepEqual(Buffer.from(await pendingMedia.arrayBuffer()), PNG);
  const atlasMedia = await fetch(`${ctx.base}${atlas.url}?key=${ctx.accessKey}`);
  assert.equal(atlasMedia.status, 200);
  assert.equal(atlasMedia.headers.get("content-type"), "image/png");

  const atlasReview = await apiJson(ctx, "/api/review", {
    body: { id: ctx.atlasName, scope: "atlas", status: "hold", note: "atlas event snapshot" },
  });
  assert.equal(atlasReview.response.status, 200);
  const atlasEvent = ctx.db.prepare(`
    SELECT status, note, image_sha256 AS imageSha256, manifest_sha256 AS manifestSha256
    FROM review_events WHERE scope='atlas' AND asset_id=? ORDER BY id DESC LIMIT 1
  `).get(ctx.atlasName);
  assert.equal(atlasEvent.status, "hold");
  assert.equal(atlasEvent.note, "atlas event snapshot");
  assert.match(atlasEvent.imageSha256, /^[a-f0-9]{64}$/);
  assert.equal(atlasEvent.manifestSha256, null);

  fs.writeFileSync(ctx.legacyReviewFile, JSON.stringify({ [ctx.atlasName]: { status: "reject", note: "changed" } }), "utf8");
  const marker = ctx.db.prepare("SELECT value FROM metadata WHERE key = ?").get("legacy_reviews_json_imported_v1");
  assert.ok(marker);
  assert.equal(ctx.db.prepare("SELECT status FROM reviews WHERE scope='atlas' AND asset_id=?").get(ctx.atlasName).status, "hold");
  const reviewColumns = ctx.db.prepare("PRAGMA table_info(reviews)").all().map((column) => column.name);
  assert.ok(reviewColumns.includes("image_sha256"));
  assert.ok(reviewColumns.includes("manifest_sha256"));
});

test("requires key header for mutations and rejects foreign origins and wrong content type", async (t) => {
  const ctx = await fixture(t);
  const noKey = await fetch(`${ctx.base}/api/health`);
  assert.equal(noKey.status, 403);

  const queryOnly = await fetch(`${ctx.base}/api/review?key=${ctx.accessKey}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ id: ctx.atlasName, status: "hold", note: "x" }),
  });
  assert.equal(queryOnly.status, 403);

  const wrongType = await fetch(`${ctx.base}/api/review`, {
    method: "POST",
    headers: { "x-dino-review-key": ctx.accessKey, "content-type": "text/plain" },
    body: "{}",
  });
  assert.equal(wrongType.status, 415);

  const foreignOrigin = await fetch(`${ctx.base}/api/review`, {
    method: "POST",
    headers: {
      "x-dino-review-key": ctx.accessKey,
      "content-type": "application/json",
      origin: "https://evil.example",
    },
    body: JSON.stringify({ id: ctx.atlasName, status: "hold", note: "x" }),
  });
  assert.equal(foreignOrigin.status, 403);
});

test("reviews and atomically promotes a complete representative without overwrite", async (t) => {
  const ctx = await fixture(t);
  const source = writeSource(path.join(ctx.temp, "incoming"), "testosaurus-examplei-river-imagegen-v3.png");
  enqueueCandidate(completeOptions(source, "testosaurus-river-v3"), { pendingDir: ctx.pendingDir });

  const saved = await apiJson(ctx, "/api/review", {
    body: { id: "pending:testosaurus-river-v3", candidateId: "testosaurus-river-v3", scope: "pending", status: "pass", note: "anatomy passed" },
  });
  assert.equal(saved.response.status, 200);
  assert.equal(saved.data.canPromote, true);
  const reviewEvent = ctx.db.prepare(`
    SELECT image_sha256 AS imageSha256, manifest_sha256 AS manifestSha256
    FROM review_events WHERE scope='pending' AND asset_id=? ORDER BY id DESC LIMIT 1
  `).get("pending:testosaurus-river-v3");
  assert.match(reviewEvent.imageSha256, /^[a-f0-9]{64}$/);
  assert.match(reviewEvent.manifestSha256, /^[a-f0-9]{64}$/);

  const promoted = await apiJson(ctx, "/api/pending/promote", {
    body: { id: "pending:testosaurus-river-v3", candidateId: "testosaurus-river-v3" },
  });
  assert.equal(promoted.response.status, 200);
  assert.equal(promoted.data.state, "promoted-awaiting-app-integration");
  assert.equal(promoted.data.targetPath, "assets/dinosaurs/testosaurus-examplei-river-imagegen-v3.png");
  assert.equal(fs.existsSync(path.join(ctx.assetDir, "testosaurus-examplei-river-imagegen-v3.png")), true);
  assert.equal(fs.existsSync(path.join(ctx.pendingDir, "testosaurus-river-v3")), false);
  assert.equal(fs.existsSync(path.join(ctx.promotionDir, "testosaurus-river-v3.json")), true);
  assert.equal(ctx.db.prepare("SELECT state FROM candidates WHERE candidate_id=?").get("testosaurus-river-v3").state, "promoted-awaiting-app-integration");

  const duplicateSource = writeSource(path.join(ctx.temp, "incoming2"), "testosaurus-examplei-river-imagegen-v4.png");
  enqueueCandidate(completeOptions(duplicateSource, "testosaurus-river-v4", {
    targetFilename: "testosaurus-examplei-river-imagegen-v3.png",
  }), { pendingDir: ctx.pendingDir });
  await apiJson(ctx, "/api/review", {
    body: { id: "pending:testosaurus-river-v4", candidateId: "testosaurus-river-v4", scope: "pending", status: "pass", note: "pass" },
  });
  const collision = await apiJson(ctx, "/api/pending/promote", {
    body: { id: "pending:testosaurus-river-v4", candidateId: "testosaurus-river-v4" },
  });
  assert.equal(collision.response.status, 409);
  assert.equal(collision.data.code, "target_exists");
  assert.equal(fs.existsSync(path.join(ctx.pendingDir, "testosaurus-river-v4", "testosaurus-examplei-river-imagegen-v4.png")), true);
});

test("allows approved non-representative kinds but blocks incomplete metadata", async (t) => {
  const ctx = await fixture(t);
  const source = writeSource(path.join(ctx.temp, "incoming"), "testosaurus-examplei-detail-reference-v5.png");
  enqueueCandidate(completeOptions(source, "testosaurus-reference-v5", {
    kind: "structure reference",
    anatomyStatus: "reference-only",
    representative: false,
  }), { pendingDir: ctx.pendingDir });
  const saved = await apiJson(ctx, "/api/review", {
    body: { candidateId: "testosaurus-reference-v5", scope: "pending", status: "pass", note: "reference approved" },
  });
  assert.equal(saved.data.canPromote, true);
  const promoted = await apiJson(ctx, "/api/pending/promote", { body: { candidateId: "testosaurus-reference-v5" } });
  assert.equal(promoted.response.status, 200);

  const incomplete = writeSource(path.join(ctx.temp, "incoming"), "testosaurus-examplei-missing-imagegen-v6.png");
  enqueueCandidate({
    candidateId: "testosaurus-missing-v6",
    image: incomplete,
    speciesId: "testosaurus-examplei",
    kind: "review hold",
  }, { pendingDir: ctx.pendingDir });
  await apiJson(ctx, "/api/review", {
    body: { candidateId: "testosaurus-missing-v6", scope: "pending", status: "pass", note: "visual pass only" },
  });
  const listed = await apiJson(ctx, `/api/images?key=${ctx.accessKey}`, { mutation: false });
  const item = listed.data.images.find((image) => image.candidateId === "testosaurus-missing-v6");
  assert.equal(item.canPromote, false);
  assert.ok(item.metadataIssues.some((issue) => issue.includes("provenance.source")));
  const blocked = await apiJson(ctx, "/api/pending/promote", { body: { candidateId: "testosaurus-missing-v6" } });
  assert.equal(blocked.response.status, 409);
  assert.equal(blocked.data.code, "metadata_incomplete");
});

test("deletes only an exactly confirmed rejected candidate and preserves DB history", async (t) => {
  const ctx = await fixture(t);
  const filename = "testosaurus-examplei-bad-anatomy-v7.png";
  const source = writeSource(path.join(ctx.temp, "incoming"), filename);
  enqueueCandidate(completeOptions(source, "testosaurus-bad-v7"), { pendingDir: ctx.pendingDir });
  await apiJson(ctx, "/api/review", {
    body: { candidateId: "testosaurus-bad-v7", scope: "pending", status: "reject", note: "extra limb" },
  });

  const mismatch = await apiJson(ctx, "/api/pending/delete", {
    body: { candidateId: "testosaurus-bad-v7", confirmName: "wrong.png", reason: "extra limb" },
  });
  assert.equal(mismatch.response.status, 400);
  assert.equal(fs.existsSync(path.join(ctx.pendingDir, "testosaurus-bad-v7")), true);

  const deleted = await apiJson(ctx, "/api/pending/delete", {
    body: { candidateId: "testosaurus-bad-v7", confirmName: filename, reason: "extra limb" },
  });
  assert.equal(deleted.response.status, 200);
  assert.equal(deleted.data.state, "deleted-rejected");
  assert.equal(fs.existsSync(path.join(ctx.pendingDir, "testosaurus-bad-v7")), false);
  const row = ctx.db.prepare("SELECT state, deletion_reason AS reason, sha256 FROM candidates WHERE candidate_id=?").get("testosaurus-bad-v7");
  assert.equal(row.state, "deleted-rejected");
  assert.equal(row.reason, "extra limb");
  assert.match(row.sha256, /^[a-f0-9]{64}$/);
  const events = ctx.db.prepare("SELECT event_type FROM candidate_events WHERE candidate_id=? ORDER BY id").all("testosaurus-bad-v7");
  assert.deepEqual(events.map((event) => event.event_type), ["review-updated", "delete-requested", "deleted-rejected"]);
});

test("does not follow pending symlinks or accept traversal identifiers", async (t) => {
  const ctx = await fixture(t);
  const traversal = await fetch(`${ctx.base}/pending-media/%2e%2e/candidate.json?key=${ctx.accessKey}`);
  assert.ok([400, 404].includes(traversal.status));

  const outside = path.join(ctx.temp, "outside");
  fs.mkdirSync(outside);
  let linked = false;
  try {
    fs.symlinkSync(outside, path.join(ctx.pendingDir, "linked-candidate"), "junction");
    linked = true;
  } catch (error) {
    if (!["EPERM", "EACCES", "ENOTSUP"].includes(error.code)) throw error;
  }
  if (linked) {
    const listed = await apiJson(ctx, `/api/images?key=${ctx.accessKey}`, { mutation: false });
    const quarantined = listed.data.images.find((image) => image.candidateId === "linked-candidate");
    assert.equal(quarantined.state, "invalid");
    assert.equal(quarantined.loadError, true);
    assert.equal(quarantined.canPromote, false);
    assert.equal(quarantined.url, "/placeholder/invalid.svg");
  }
});

test("blocks promotion when pixels change after a pass review", async (t) => {
  const ctx = await fixture(t);
  const filename = "testosaurus-examplei-tamper-imagegen-v8.png";
  const source = writeSource(path.join(ctx.temp, "incoming"), filename);
  enqueueCandidate(completeOptions(source, "testosaurus-tamper-v8"), { pendingDir: ctx.pendingDir });
  await apiJson(ctx, "/api/review", {
    body: { candidateId: "testosaurus-tamper-v8", scope: "pending", status: "pass", note: "passed original pixels" },
  });
  fs.appendFileSync(path.join(ctx.pendingDir, "testosaurus-tamper-v8", filename), Buffer.from([0x00]));

  const listed = await apiJson(ctx, `/api/images?key=${ctx.accessKey}`, { mutation: false });
  const item = listed.data.images.find((image) => image.candidateId === "testosaurus-tamper-v8");
  assert.equal(item.canPromote, false);
  assert.ok(item.metadataIssues.some((issue) => issue.includes("재검수")));
  const promoted = await apiJson(ctx, "/api/pending/promote", { body: { candidateId: "testosaurus-tamper-v8" } });
  assert.equal(promoted.response.status, 409);
  assert.equal(promoted.data.code, "candidate_changed_after_review");
  assert.equal(fs.existsSync(path.join(ctx.pendingDir, "testosaurus-tamper-v8", filename)), true);
  assert.equal(fs.existsSync(path.join(ctx.assetDir, filename)), false);
});

test("uses a canonical manifest digest and blocks semantic manifest changes", async (t) => {
  const ctx = await fixture(t);
  const filename = "testosaurus-examplei-manifest-imagegen-v12.png";
  const source = writeSource(path.join(ctx.temp, "incoming"), filename);
  enqueueCandidate(completeOptions(source, "testosaurus-manifest-v12"), { pendingDir: ctx.pendingDir });
  await apiJson(ctx, "/api/review", {
    body: { candidateId: "testosaurus-manifest-v12", scope: "pending", status: "pass", note: "manifest reviewed" },
  });
  const manifestFile = path.join(ctx.pendingDir, "testosaurus-manifest-v12", "candidate.json");
  const manifest = JSON.parse(fs.readFileSync(manifestFile, "utf8"));
  const reordered = Object.fromEntries(Object.entries(manifest).reverse());
  fs.writeFileSync(manifestFile, JSON.stringify(reordered), "utf8");
  let listed = await apiJson(ctx, `/api/images?key=${ctx.accessKey}`, { mutation: false });
  assert.equal(listed.data.images.find((image) => image.candidateId === "testosaurus-manifest-v12").canPromote, true);

  reordered.provenance.workflow = "different workflow revision";
  fs.writeFileSync(manifestFile, JSON.stringify(reordered, null, 4), "utf8");
  listed = await apiJson(ctx, `/api/images?key=${ctx.accessKey}`, { mutation: false });
  assert.equal(listed.data.images.find((image) => image.candidateId === "testosaurus-manifest-v12").canPromote, false);
  const blocked = await apiJson(ctx, "/api/pending/promote", { body: { candidateId: "testosaurus-manifest-v12" } });
  assert.equal(blocked.response.status, 409);
  assert.equal(blocked.data.code, "candidate_changed_after_review");
});

test("blocks deletion when pixels change after a reject review", async (t) => {
  const ctx = await fixture(t);
  const filename = "testosaurus-examplei-reject-tamper-v9.png";
  const source = writeSource(path.join(ctx.temp, "incoming"), filename);
  enqueueCandidate(completeOptions(source, "testosaurus-reject-v9"), { pendingDir: ctx.pendingDir });
  await apiJson(ctx, "/api/review", {
    body: { candidateId: "testosaurus-reject-v9", scope: "pending", status: "reject", note: "bad original anatomy" },
  });
  fs.appendFileSync(path.join(ctx.pendingDir, "testosaurus-reject-v9", filename), Buffer.from([0x01]));

  const deleted = await apiJson(ctx, "/api/pending/delete", {
    body: { candidateId: "testosaurus-reject-v9", confirmName: filename, reason: "bad original anatomy" },
  });
  assert.equal(deleted.response.status, 409);
  assert.equal(deleted.data.code, "candidate_changed_after_review");
  assert.equal(fs.existsSync(path.join(ctx.pendingDir, "testosaurus-reject-v9", filename)), true);
});

test("blocks a terminal candidateId from reusing an old reject review", async (t) => {
  const ctx = await fixture(t);
  const candidateId = "testosaurus-reused-v10";
  const firstName = "testosaurus-examplei-first-reject-v10.png";
  const first = writeSource(path.join(ctx.temp, "incoming-first"), firstName);
  enqueueCandidate(completeOptions(first, candidateId), { pendingDir: ctx.pendingDir });
  await apiJson(ctx, "/api/review", {
    body: { candidateId, scope: "pending", status: "reject", note: "first candidate rejected" },
  });
  const firstDelete = await apiJson(ctx, "/api/pending/delete", {
    body: { candidateId, confirmName: firstName, reason: "first candidate rejected" },
  });
  assert.equal(firstDelete.response.status, 200);

  const secondName = "testosaurus-examplei-new-file-v11.png";
  const second = writeSource(path.join(ctx.temp, "incoming-second"), secondName);
  enqueueCandidate(completeOptions(second, candidateId), { pendingDir: ctx.pendingDir });
  const reusedDelete = await apiJson(ctx, "/api/pending/delete", {
    body: { candidateId, confirmName: secondName, reason: "must not reuse old review" },
  });
  assert.equal(reusedDelete.response.status, 409);
  assert.equal(reusedDelete.data.code, "candidate_id_reused");
  assert.equal(fs.existsSync(path.join(ctx.pendingDir, candidateId, secondName)), true);
  const reusedReview = await apiJson(ctx, "/api/review", {
    body: { candidateId, scope: "pending", status: "reject", note: "attempted reused id" },
  });
  assert.equal(reusedReview.response.status, 409);
  assert.equal(reusedReview.data.code, "candidate_id_reused");
});

test("rolls back promotion copies and records when DB finalization fails", async (t) => {
  const ctx = await fixture(t);
  const candidateId = "testosaurus-db-fault-v13";
  const filename = "testosaurus-examplei-db-fault-imagegen-v13.png";
  const source = writeSource(path.join(ctx.temp, "incoming"), filename);
  enqueueCandidate(completeOptions(source, candidateId), { pendingDir: ctx.pendingDir });
  await apiJson(ctx, "/api/review", {
    body: { candidateId, scope: "pending", status: "pass", note: "ready before DB fault" },
  });
  ctx.db.exec(`
    CREATE TRIGGER fail_promotion_finalize
    BEFORE INSERT ON candidate_events
    WHEN NEW.event_type = 'promoted-awaiting-app-integration'
    BEGIN
      SELECT RAISE(ABORT, 'injected promotion finalize failure');
    END;
  `);

  const promoted = await apiJson(ctx, "/api/pending/promote", { body: { candidateId } });
  assert.equal(promoted.response.status, 500);
  assert.equal(ctx.db.prepare("SELECT state FROM candidates WHERE candidate_id=?").get(candidateId).state, "pending");
  assert.equal(fs.existsSync(path.join(ctx.pendingDir, candidateId, filename)), true);
  assert.equal(fs.existsSync(path.join(ctx.pendingDir, candidateId, "candidate.json")), true);
  assert.equal(fs.existsSync(path.join(ctx.assetDir, filename)), false);
  assert.equal(fs.existsSync(path.join(ctx.promotionDir, `${candidateId}.json`)), false);
  const events = ctx.db.prepare("SELECT event_type FROM candidate_events WHERE candidate_id=? ORDER BY id").all(candidateId).map((row) => row.event_type);
  assert.ok(events.includes("promotion-in-progress"));
  assert.ok(events.includes("promotion-failed"));
});

test("finalizes deletion with cleanup warning when manifest cleanup fails", async (t) => {
  const fault = { operation: null };
  const ctx = await fixture(t, {
    faultInjector({ operation }) {
      if (fault.operation === operation) {
        fault.operation = null;
        const error = new Error("injected manifest cleanup failure");
        error.code = "EACCES";
        throw error;
      }
    },
  });
  const candidateId = "testosaurus-delete-cleanup-v14";
  const filename = "testosaurus-examplei-delete-cleanup-v14.png";
  const source = writeSource(path.join(ctx.temp, "incoming"), filename);
  enqueueCandidate(completeOptions(source, candidateId), { pendingDir: ctx.pendingDir });
  await apiJson(ctx, "/api/review", {
    body: { candidateId, scope: "pending", status: "reject", note: "cleanup failure test" },
  });
  fault.operation = "delete-cleanup-manifest";
  const deleted = await apiJson(ctx, "/api/pending/delete", {
    body: { candidateId, confirmName: filename, reason: "cleanup failure test" },
  });
  assert.equal(deleted.response.status, 200);
  assert.ok(Array.isArray(deleted.data.cleanupWarning));
  assert.equal(ctx.db.prepare("SELECT state FROM candidates WHERE candidate_id=?").get(candidateId).state, "deleted-rejected");
  assert.equal(fs.existsSync(path.join(ctx.pendingDir, candidateId, filename)), false);
  assert.equal(fs.existsSync(path.join(ctx.pendingDir, candidateId, "candidate.json")), true);
  const warnings = ctx.db.prepare("SELECT COUNT(*) AS count FROM candidate_events WHERE candidate_id=? AND event_type='cleanup-warning'").get(candidateId);
  assert.equal(Number(warnings.count), 1);
});

test("restores pending state and records delete-failed when image unlink fails", async (t) => {
  const fault = { operation: null };
  const ctx = await fixture(t, {
    faultInjector({ operation }) {
      if (fault.operation === operation) {
        fault.operation = null;
        const error = new Error("injected image unlink failure");
        error.code = "EACCES";
        throw error;
      }
    },
  });
  const candidateId = "testosaurus-delete-image-v15";
  const filename = "testosaurus-examplei-delete-image-v15.png";
  const source = writeSource(path.join(ctx.temp, "incoming"), filename);
  enqueueCandidate(completeOptions(source, candidateId), { pendingDir: ctx.pendingDir });
  await apiJson(ctx, "/api/review", {
    body: { candidateId, scope: "pending", status: "reject", note: "image unlink failure test" },
  });
  fault.operation = "delete-image";
  const deleted = await apiJson(ctx, "/api/pending/delete", {
    body: { candidateId, confirmName: filename, reason: "image unlink failure test" },
  });
  assert.equal(deleted.response.status, 500);
  assert.equal(deleted.data.code, "delete_failed");
  assert.equal(ctx.db.prepare("SELECT state FROM candidates WHERE candidate_id=?").get(candidateId).state, "pending");
  assert.equal(fs.existsSync(path.join(ctx.pendingDir, candidateId, filename)), true);
  assert.equal(fs.existsSync(path.join(ctx.pendingDir, candidateId, "candidate.json")), true);
  assert.equal(ctx.db.prepare("SELECT COUNT(*) AS count FROM candidate_events WHERE candidate_id=? AND event_type='delete-failed'").get(candidateId).count, 1);
});

test("returns promotion success with cleanup warning and startup reconciliation removes the leftover source", async (t) => {
  const fault = { operation: null };
  const ctx = await fixture(t, {
    faultInjector({ operation }) {
      if (fault.operation === operation) {
        fault.operation = null;
        const error = new Error("injected promotion source cleanup failure");
        error.code = "EACCES";
        throw error;
      }
    },
  });
  const candidateId = "testosaurus-promote-cleanup-v16";
  const filename = "testosaurus-examplei-promote-cleanup-v16.png";
  const source = writeSource(path.join(ctx.temp, "incoming"), filename);
  enqueueCandidate(completeOptions(source, candidateId), { pendingDir: ctx.pendingDir });
  await apiJson(ctx, "/api/review", {
    body: { candidateId, scope: "pending", status: "pass", note: "promotion cleanup test" },
  });
  fault.operation = "promotion-cleanup-image";
  const promoted = await apiJson(ctx, "/api/pending/promote", { body: { candidateId } });
  assert.equal(promoted.response.status, 200);
  assert.ok(Array.isArray(promoted.data.cleanupWarning));
  assert.equal(ctx.db.prepare("SELECT state FROM candidates WHERE candidate_id=?").get(candidateId).state, "promoted-awaiting-app-integration");
  assert.equal(fs.existsSync(path.join(ctx.pendingDir, candidateId, filename)), true);
  assert.equal(fs.existsSync(path.join(ctx.assetDir, filename)), true);

  reconcileCandidateStates(ctx.app.config, ctx.db);
  assert.equal(fs.existsSync(path.join(ctx.pendingDir, candidateId)), false);
  assert.equal(fs.existsSync(path.join(ctx.assetDir, filename)), true);
});

test("startup reconciliation rolls an interrupted promotion intent back to pending", async (t) => {
  const ctx = await fixture(t);
  const candidateId = "testosaurus-crash-recovery-v17";
  const filename = "testosaurus-examplei-crash-recovery-v17.png";
  const source = writeSource(path.join(ctx.temp, "incoming"), filename);
  enqueueCandidate(completeOptions(source, candidateId), { pendingDir: ctx.pendingDir });
  await apiJson(ctx, `/api/images?key=${ctx.accessKey}`, { mutation: false });
  const pendingFile = path.join(ctx.pendingDir, candidateId, filename);
  const hash = crypto.createHash("sha256").update(fs.readFileSync(pendingFile)).digest("hex");
  const targetPath = `assets/dinosaurs/${filename}`;
  const update = ctx.db.prepare(`
    UPDATE candidates SET state='promotion-in-progress', target_path=?, sha256=?, updated_at=?
    WHERE candidate_id=? AND state='pending'
  `).run(targetPath, hash, new Date().toISOString(), candidateId);
  assert.equal(Number(update.changes), 1);
  fs.copyFileSync(pendingFile, path.join(ctx.assetDir, filename), fs.constants.COPYFILE_EXCL);
  fs.writeFileSync(path.join(ctx.promotionDir, `${candidateId}.json`), JSON.stringify({ candidateId, sha256: hash }), "utf8");

  reconcileCandidateStates(ctx.app.config, ctx.db);
  assert.equal(ctx.db.prepare("SELECT state FROM candidates WHERE candidate_id=?").get(candidateId).state, "pending");
  assert.equal(fs.existsSync(pendingFile), true);
  assert.equal(fs.existsSync(path.join(ctx.assetDir, filename)), false);
  assert.equal(fs.existsSync(path.join(ctx.promotionDir, `${candidateId}.json`)), false);
});

test("returns JSON 413 without resetting the request socket and serves hardened HTML", async (t) => {
  const ctx = await fixture(t);
  const html = await fetch(`${ctx.base}/?key=${ctx.accessKey}`);
  assert.equal(html.status, 200);
  assert.match(html.headers.get("content-security-policy"), /frame-ancestors 'none'/);
  assert.equal(html.headers.get("referrer-policy"), "no-referrer");
  assert.equal(html.headers.get("x-frame-options"), "DENY");
  const oversized = JSON.stringify({
    id: ctx.atlasName,
    status: "hold",
    note: "x".repeat(129 * 1024),
  });
  const response = await fetch(`${ctx.base}/api/review`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-dino-review-key": ctx.accessKey,
    },
    body: oversized,
  });
  assert.equal(response.status, 413);
  assert.deepEqual(await response.json(), { error: "body too large", code: "body_too_large" });
});

test("shares structural PNG validation between server inspection and enqueue", () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "dino-review-png-"));
  try {
    const valid = path.join(temp, "testosaurus-examplei-valid-imagegen-v1.png");
    fs.writeFileSync(valid, PNG);
    assert.doesNotThrow(() => assertPng(valid));

    const noIend = path.join(temp, "testosaurus-examplei-no-iend-imagegen-v2.png");
    fs.writeFileSync(noIend, PNG.subarray(0, PNG.length - 12));
    assert.throws(() => assertPng(noIend), /IEND|bounds/);
    assert.throws(
      () => enqueueCandidate({
        candidateId: "testosaurus-no-iend-v2",
        image: noIend,
        speciesId: "testosaurus-examplei",
        kind: "review hold",
      }, { pendingDir: path.join(temp, "pending") }),
      /invalid PNG structure/,
    );

    const zeroWidth = Buffer.from(PNG);
    zeroWidth.writeUInt32BE(0, 16);
    const zeroWidthFile = path.join(temp, "testosaurus-examplei-zero-width-v3.png");
    fs.writeFileSync(zeroWidthFile, zeroWidth);
    assert.throws(() => assertPng(zeroWidthFile), /dimensions/);

    const badBounds = Buffer.from(PNG);
    badBounds.writeUInt32BE(0xffffffff, 8);
    const badBoundsFile = path.join(temp, "testosaurus-examplei-bounds-v4.png");
    fs.writeFileSync(badBoundsFile, badBounds);
    assert.throws(() => assertPng(badBoundsFile), /bounds/);
  } finally {
    fs.rmSync(temp, { recursive: true, force: true });
  }
});

test("exposes malformed, extra-file, and invalid-PNG candidates as read-only inventory", async (t) => {
  const ctx = await fixture(t);
  const malformedId = "testosaurus-malformed-v18";
  const malformedDir = path.join(ctx.pendingDir, malformedId);
  const malformedName = "testosaurus-examplei-malformed-imagegen-v18.png";
  fs.mkdirSync(malformedDir);
  fs.writeFileSync(path.join(malformedDir, malformedName), PNG);
  fs.writeFileSync(path.join(malformedDir, "candidate.json"), "{not-json", "utf8");

  const extraSource = writeSource(path.join(ctx.temp, "incoming-extra"), "testosaurus-examplei-extra-imagegen-v19.png");
  enqueueCandidate(completeOptions(extraSource, "testosaurus-extra-v19"), { pendingDir: ctx.pendingDir });
  fs.writeFileSync(path.join(ctx.pendingDir, "testosaurus-extra-v19", "unexpected.txt"), "extra", "utf8");

  const invalidPngId = "testosaurus-invalid-png-v20";
  const invalidPngDir = path.join(ctx.pendingDir, invalidPngId);
  fs.mkdirSync(invalidPngDir);
  fs.writeFileSync(path.join(invalidPngDir, "testosaurus-examplei-invalid-imagegen-v20.png"), PNG.subarray(0, 20));
  fs.writeFileSync(path.join(invalidPngDir, "candidate.json"), JSON.stringify({
    schemaVersion: 1,
    candidateId: invalidPngId,
    filename: "testosaurus-examplei-invalid-imagegen-v20.png",
    speciesId: "testosaurus-examplei",
    kind: "review hold",
  }), "utf8");

  const listed = await apiJson(ctx, `/api/images?key=${ctx.accessKey}`, { mutation: false });
  for (const candidateId of [malformedId, "testosaurus-extra-v19", invalidPngId]) {
    const item = listed.data.images.find((image) => image.candidateId === candidateId);
    assert.equal(item.scope, "pending");
    assert.equal(item.state, "invalid");
    assert.equal(item.loadError, true);
    assert.equal(item.canPromote, false);
    assert.ok(item.metadataIssues.length > 0);
  }
  const malformed = listed.data.images.find((image) => image.candidateId === malformedId);
  const extra = listed.data.images.find((image) => image.candidateId === "testosaurus-extra-v19");
  const invalidPng = listed.data.images.find((image) => image.candidateId === invalidPngId);
  assert.match(malformed.url, /^\/quarantine-media\//);
  assert.match(extra.url, /^\/quarantine-media\//);
  assert.equal(invalidPng.url, "/placeholder/invalid.svg");
  const quarantine = await fetch(`${ctx.base}${malformed.url}?key=${ctx.accessKey}`);
  assert.equal(quarantine.status, 200);
  assert.deepEqual(Buffer.from(await quarantine.arrayBuffer()), PNG);
  const placeholder = await fetch(`${ctx.base}${invalidPng.url}?key=${ctx.accessKey}`);
  assert.equal(placeholder.status, 200);
  assert.equal(placeholder.headers.get("content-type"), "image/svg+xml; charset=utf-8");

  for (const endpoint of ["/api/review", "/api/pending/promote", "/api/pending/delete"]) {
    const rejected = await apiJson(ctx, endpoint, {
      body: {
        candidateId: malformedId,
        scope: "pending",
        status: "pass",
        note: "must remain read only",
        confirmName: malformedName,
        reason: "invalid",
      },
    });
    assert.equal(rejected.response.status, 409);
    assert.equal(rejected.data.code, "invalid_candidate");
  }
  const invalidRows = ctx.db.prepare("SELECT COUNT(*) AS count FROM asset_inventory WHERE state='invalid'").get();
  assert.equal(Number(invalidRows.count), 3);
});

test("parses inline app entries, preserves duplicate registrations, and records exact app kind", async (t) => {
  const ctx = await fixture(t);
  fs.writeFileSync(ctx.appFile, `
const dinosaurs = [
  { id: "testosaurus-examplei", koreanName: "테스토사우루스" },
  { id: "otherosaurus-examplei", koreanName: "아더로사우루스" },
];
const generatedImageSamples = {
  "testosaurus-examplei": [{ kind: "anatomy review", title: "inline one", source: "assets/dinosaurs/${ctx.atlasName}", src: "assets/dinosaurs/${ctx.atlasName}" }],
  "otherosaurus-examplei": [{ kind: "review hold", title: "duplicate registration", source: "assets/dinosaurs/${ctx.atlasName}" }],
};
const approvedVelociraptorCandidateSources = new Set([]);
const verifiedRejectedCandidateSources = new Set([]);
`, "utf8");
  const listed = await apiJson(ctx, `/api/images?key=${ctx.accessKey}`, { mutation: false });
  const atlas = listed.data.images.find((image) => image.scope === "atlas");
  assert.equal(atlas.kind, "anatomy review");
  assert.equal(atlas.species, "testosaurus-examplei");
  assert.equal(ctx.db.prepare("SELECT COUNT(*) AS count FROM asset_app_registrations").get().count, 2);
  const inventory = ctx.db.prepare(`
    SELECT state, metadata_json AS metadataJson, issues_json AS issuesJson
    FROM asset_inventory WHERE asset_key=?
  `).get(`app:assets/dinosaurs/${ctx.atlasName}`);
  assert.equal(inventory.state, "app-registered");
  assert.equal(JSON.parse(inventory.metadataJson).registrationCount, 2);
  assert.ok(JSON.parse(inventory.issuesJson).some((issue) => issue.includes("중복")));
});

test("keeps the last good inventory when app literal parsing fails", async (t) => {
  const ctx = await fixture(t);
  const good = await apiJson(ctx, `/api/images?key=${ctx.accessKey}`, { mutation: false });
  assert.equal(good.response.status, 200);
  const before = Number(ctx.db.prepare("SELECT COUNT(*) AS count FROM asset_inventory").get().count);
  assert.ok(before > 0);
  fs.writeFileSync(ctx.appFile, "const generatedImageSamples = { broken: [;", "utf8");
  const broken = await apiJson(ctx, `/api/images?key=${ctx.accessKey}`, { mutation: false });
  assert.equal(broken.response.status, 500);
  assert.equal(Number(ctx.db.prepare("SELECT COUNT(*) AS count FROM asset_inventory").get().count), before);
  const lastRun = ctx.db.prepare("SELECT status, error FROM inventory_sync_runs ORDER BY id DESC LIMIT 1").get();
  assert.equal(lastRun.status, "error");
  assert.match(lastRun.error, /generatedImageSamples/);
});

test("skips all inventory writes for unchanged polling but syncs changes and a fresh server state", async (t) => {
  const ctx = await fixture(t);
  const pendingSource = writeSource(path.join(ctx.temp, "incoming-poll"), "testosaurus-examplei-poll-imagegen-v22.png");
  enqueueCandidate(completeOptions(pendingSource, "testosaurus-poll-v22"), { pendingDir: ctx.pendingDir });
  const first = await apiJson(ctx, `/api/images?key=${ctx.accessKey}`, { mutation: false });
  assert.equal(first.response.status, 200);
  const runsAfterFirst = Number(ctx.db.prepare("SELECT COUNT(*) AS count FROM inventory_sync_runs").get().count);
  const changesAfterFirst = Number(ctx.db.prepare("SELECT total_changes() AS count").get().count);
  assert.equal(runsAfterFirst, 1);

  const second = await apiJson(ctx, `/api/images?key=${ctx.accessKey}`, { mutation: false });
  assert.equal(second.response.status, 200);
  assert.equal(Number(ctx.db.prepare("SELECT COUNT(*) AS count FROM inventory_sync_runs").get().count), runsAfterFirst);
  assert.equal(Number(ctx.db.prepare("SELECT total_changes() AS count").get().count), changesAfterFirst);

  const future = new Date(Date.now() + 5000);
  fs.utimesSync(path.join(ctx.assetDir, ctx.atlasName), future, future);
  const changed = await apiJson(ctx, `/api/images?key=${ctx.accessKey}`, { mutation: false });
  assert.equal(changed.response.status, 200);
  const runsAfterChange = Number(ctx.db.prepare("SELECT COUNT(*) AS count FROM inventory_sync_runs").get().count);
  assert.equal(runsAfterChange, runsAfterFirst + 1);

  listImages(ctx.app.config, ctx.db, { lastSignature: null });
  assert.equal(Number(ctx.db.prepare("SELECT COUNT(*) AS count FROM inventory_sync_runs").get().count), runsAfterChange + 1);
});

test("lists promoted assets for integration and marks them integrated exactly once after app registration", async (t) => {
  const ctx = await fixture(t);
  const candidateId = "testosaurus-integration-v21";
  const filename = "testosaurus-examplei-integration-imagegen-v21.png";
  const source = writeSource(path.join(ctx.temp, "incoming-integration"), filename);
  enqueueCandidate(completeOptions(source, candidateId), { pendingDir: ctx.pendingDir });
  await apiJson(ctx, "/api/review", {
    body: { candidateId, scope: "pending", status: "pass", note: "ready for integration" },
  });
  const promotion = await apiJson(ctx, "/api/pending/promote", { body: { candidateId } });
  assert.equal(promotion.response.status, 200);

  let listed = await apiJson(ctx, `/api/images?key=${ctx.accessKey}`, { mutation: false });
  const integration = listed.data.images.find((image) => image.id === `integration:${candidateId}`);
  assert.equal(integration.scope, "integration");
  assert.equal(integration.state, "promoted-awaiting-app-integration");
  assert.equal(integration.targetPath, `assets/dinosaurs/${filename}`);
  assert.match(integration.promotionRecord, new RegExp(`${candidateId}\\.json$`));
  assert.deepEqual(integration.metadataIssues, []);
  const promotedMedia = await fetch(`${ctx.base}${integration.url}?key=${ctx.accessKey}`);
  assert.equal(promotedMedia.status, 200);
  assert.deepEqual(Buffer.from(await promotedMedia.arrayBuffer()), PNG);
  assert.equal(ctx.db.prepare("SELECT state FROM asset_inventory WHERE asset_key=?").get(`integration:${candidateId}`).state, "promoted-awaiting-app-integration");

  writeFixtureApp(ctx.appFile, filename);
  listed = await apiJson(ctx, `/api/images?key=${ctx.accessKey}`, { mutation: false });
  assert.equal(listed.data.images.some((image) => image.id === `integration:${candidateId}`), false);
  const atlas = listed.data.images.find((image) => image.id === filename);
  assert.equal(atlas.scope, "atlas");
  assert.equal(atlas.kind, "count-level pass");
  assert.equal(ctx.db.prepare("SELECT state FROM candidates WHERE candidate_id=?").get(candidateId).state, "integrated");
  assert.equal(ctx.db.prepare("SELECT COUNT(*) AS count FROM candidate_events WHERE candidate_id=? AND event_type='integrated'").get(candidateId).count, 1);
  await apiJson(ctx, `/api/images?key=${ctx.accessKey}`, { mutation: false });
  assert.equal(ctx.db.prepare("SELECT COUNT(*) AS count FROM candidate_events WHERE candidate_id=? AND event_type='integrated'").get(candidateId).count, 1);
});

test("parses all current checkout app entries including the three inline Sphaerotholus records", (t) => {
  const root = path.resolve(__dirname, "..", "..", "..");
  const reviewHtml = fs.readFileSync(path.join(root, "tools", "dino-review", "index.html"), "utf8");
  assert.match(reviewHtml, /id="previousPreview"/);
  assert.match(reviewHtml, /preferredSelectedId/);
  assert.match(reviewHtml, /nextReviewIdAfterRemoval/);
  assert.doesNotMatch(reviewHtml, /\$\("scope"\)\.value\s*=\s*"integration"/);
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "dino-review-checkout-index-"));
  const config = defaultConfig({
    root,
    appFile: path.join(root, "app.js"),
    assetDir: path.join(root, "assets", "dinosaurs"),
    dbPath: path.join(temp, "review.sqlite"),
    legacyReviewFile: path.join(temp, "missing-reviews.json"),
    rejectionFile: path.join(root, "tools", "comfyui", "gallery-slot-rejections.json"),
  });
  const db = openReviewDatabase(config);
  try {
    const manifest = loadAtlasCandidateManifest(config);
    assert.equal(manifest.appEntryCount, 1862, "intentional checkout baseline; update with app data changes");
    const inlineSources = [
      "assets/dinosaurs/sphaerotholus-goodwini-charcoal-russet-dome-fullbody-imagegen-v4.png",
      "assets/dinosaurs/sphaerotholus-goodwini-arroyo-fern-browse-ecology-imagegen-v4.png",
      "assets/dinosaurs/sphaerotholus-goodwini-cobalt-violet-ochre-variant-imagegen-v4.png",
    ];
    const expectedKinds = ["anatomy review", "anatomy review", "review hold"];
    for (let index = 0; index < inlineSources.length; index += 1) {
      const registrations = manifest.candidateEntries.get(inlineSources[index]);
      assert.ok(registrations?.some((entry) => entry.speciesId === "sphaerotholus-goodwini" && entry.kind === expectedKinds[index]));
    }
    const visible = listAtlasImages(config, db, manifest);
    for (let index = 0; index < inlineSources.length; index += 1) {
      const item = visible.find((image) => image.name === path.basename(inlineSources[index]));
      assert.equal(item.kind, expectedKinds[index]);
      assert.equal(item.species, "sphaerotholus-goodwini");
    }
    const scanned = listImages(config, db);
    assert.equal(scanned.filter((item) => item.scope === "atlas").length, visible.length);
    const inventoryCount = Number(db.prepare("SELECT COUNT(*) AS count FROM asset_inventory").get().count);
    const registrationCount = Number(db.prepare("SELECT COUNT(*) AS count FROM asset_app_registrations").get().count);
    const states = db.prepare("SELECT state, COUNT(*) AS count FROM asset_inventory GROUP BY state ORDER BY state").all();
    assert.equal(registrationCount, manifest.appEntryCount);
    t.diagnostic(`checkout app entries=${manifest.appEntryCount}, visible atlas=${visible.length}, inventory=${inventoryCount}, states=${JSON.stringify(states)}`);
  } finally {
    db.close();
    fs.rmSync(temp, { recursive: true, force: true });
  }
});
