const http = require("http");
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const PORT = Number(process.env.CODEX_DASHBOARD_PORT || 8791);
const HOST = "127.0.0.1";
const CODEX_HOME = process.env.CODEX_HOME || path.join(process.env.USERPROFILE || process.env.HOME, ".codex");
const ROOT = __dirname;
const ACCESS_KEY = process.env.CODEX_DASHBOARD_KEY || "";

function json(res, value) {
  const body = JSON.stringify(value);
  res.writeHead(200, {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
  });
  res.end(body);
}

function text(res, status, value) {
  res.writeHead(status, { "content-type": "text/plain; charset=utf-8" });
  res.end(value);
}

function readJsonLines(file) {
  try {
    return parseJsonLines(fs.readFileSync(file, "utf8"));
  } catch {
    return [];
  }
}

function parseJsonLines(text) {
  return text
    .split(/\r?\n/)
    .filter(Boolean)
    .map((line) => {
      try {
        return JSON.parse(line);
      } catch {
        return null;
      }
    })
    .filter(Boolean);
}

function readSlice(file, offset, length) {
  const fd = fs.openSync(file, "r");
  try {
    const buffer = Buffer.alloc(length);
    const bytes = fs.readSync(fd, buffer, 0, length, offset);
    return buffer.subarray(0, bytes).toString("utf8");
  } finally {
    fs.closeSync(fd);
  }
}

function readStart(file, stat, maxBytes) {
  return readSlice(file, 0, Math.min(stat.size, maxBytes));
}

function readTail(file, stat, maxBytes) {
  const length = Math.min(stat.size, maxBytes);
  return readSlice(file, Math.max(0, stat.size - length), length);
}

function walkFiles(dir, acc = []) {
  let entries = [];
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return acc;
  }

  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walkFiles(full, acc);
    } else if (entry.isFile() && entry.name.endsWith(".jsonl")) {
      acc.push(full);
    }
  }
  return acc;
}

function readSessionIndex() {
  const index = new Map();
  for (const row of readJsonLines(path.join(CODEX_HOME, "session_index.jsonl"))) {
    if (!row.id) continue;
    index.set(row.id, {
      id: row.id,
      title: row.thread_name || row.id,
      updatedAt: row.updated_at || null,
    });
  }
  return index;
}

function extractSessionId(file) {
  const match = path.basename(file).match(/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.jsonl$/i);
  return match ? match[1] : path.basename(file, ".jsonl");
}

function parseSessionFile(file, indexed) {
  const stat = fs.statSync(file);
  const head = readStart(file, stat, 256 * 1024);
  const tail = readTail(file, stat, 768 * 1024);
  const rows = parseJsonLines(`${head}\n${tail}`);
  const id = extractSessionId(file);
  let meta = null;
  let token = null;
  let eventCount = (tail.match(/"type":"event_msg"/g) || []).length;
  let toolCount = (tail.match(/"type":"function_call"/g) || []).length;
  let lastEventAt = null;

  for (const row of rows) {
    if (row.timestamp) lastEventAt = row.timestamp;
    if (row.type === "session_meta") meta = row.payload || null;
    if (row.type === "event_msg" && row.payload && row.payload.type === "token_count") token = row.payload;
  }

  const indexedRow = indexed.get(id);
  const updatedAt = lastEventAt || stat.mtime.toISOString();
  const ageMs = Date.now() - new Date(updatedAt).getTime();

  return {
    id,
    title: indexedRow?.title || id,
    updatedAt,
    hot: ageMs >= 0 && ageMs < 15 * 60 * 1000,
    staleHours: Math.max(0, ageMs / 36e5),
    file,
    sizeBytes: stat.size,
    cwd: meta?.cwd || null,
    originator: meta?.originator || null,
    cliVersion: meta?.cli_version || null,
    modelProvider: meta?.model_provider || null,
    events: eventCount,
    toolCalls: toolCount,
    token,
  };
}

function readSessions() {
  const indexed = readSessionIndex();
  const dir = path.join(CODEX_HOME, "sessions");
  return walkFiles(dir)
    .map((file) => {
      try {
        return parseSessionFile(file, indexed);
      } catch {
        return null;
      }
    })
    .filter(Boolean)
    .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))
    .slice(0, 40);
}

function readProcesses() {
  return new Promise((resolve) => {
    const script = [
      "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8;",
      "$ErrorActionPreference='SilentlyContinue';",
      "$filter = \"Name='codex.exe' OR Name='Codex.exe' OR Name='wmux.exe' OR Name='node.exe' OR Name='node_repl.exe' OR Name LIKE 'codex-command-runner%'\";",
      "Get-CimInstance Win32_Process -Filter $filter |",
      "Select-Object ProcessId,Name,CreationDate,CommandLine |",
      "ConvertTo-Json -Depth 4 -Compress",
    ].join(" ");

    const child = spawn("powershell.exe", ["-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], {
      windowsHide: true,
    });
    const chunks = [];
    const timer = setTimeout(() => {
      child.kill();
      resolve([]);
    }, 8000);
    child.stdout.on("data", (chunk) => { chunks.push(chunk); });
    child.on("close", () => {
      clearTimeout(timer);
      try {
        const raw = Buffer.concat(chunks);
        const parsed = parseJsonBuffer(raw);
        const rows = Array.isArray(parsed) ? parsed : [parsed];
        resolve(rows.filter(Boolean).map(classifyProcess));
      } catch {
        resolve([]);
      }
    });
    child.on("error", () => {
      clearTimeout(timer);
      resolve([]);
    });
  });
}

function parseJsonBuffer(raw) {
  const utf8 = raw.toString("utf8").replace(/^\uFEFF/, "").trim();
  try {
    return JSON.parse(utf8 || "[]");
  } catch {
    const utf16 = raw.toString("utf16le").replace(/^\uFEFF/, "").trim();
    return JSON.parse(utf16 || "[]");
  }
}

function classifyProcess(row) {
  const command = row.CommandLine || "";
  const name = row.Name || "";
  let kind = "other";
  if (/wmux/i.test(name)) kind = "wmux";
  if (/Codex\.exe/i.test(name)) kind = "app";
  if (/codex\.exe/i.test(name) && /resume|app-server|exec/i.test(command)) kind = "cli";
  if (/node\.exe/i.test(name) && /kernel\.js/i.test(command)) kind = "kernel";
  if (/node_repl\.exe/i.test(name)) kind = "node-repl";
  if (/codex-command-runner/i.test(name)) kind = "runner";

  return {
    pid: row.ProcessId,
    name,
    kind,
    createdAt: row.CreationDate || null,
    cwd: command.match(/--working-dir\s+("?)([^"]+?)\1(?:\s|$)/i)?.[2] || null,
    command: command.replace(/\s+/g, " ").trim(),
  };
}

function latestTokenSnapshot(sessions) {
  const withToken = sessions.find((session) => session.token);
  if (!withToken) return null;
  return {
    sessionId: withToken.id,
    title: withToken.title,
    updatedAt: withToken.updatedAt,
    info: withToken.token.info || null,
    rateLimits: withToken.token.rate_limits || null,
  };
}

async function snapshot() {
  const sessions = readSessions();
  const processes = await readProcesses();
  const live = processes.filter((p) => ["cli", "app", "wmux", "kernel", "runner"].includes(p.kind));
  return {
    generatedAt: new Date().toISOString(),
    codexHome: CODEX_HOME,
    summary: {
      sessions: sessions.length,
      hotSessions: sessions.filter((s) => s.hot).length,
      liveProcesses: live.length,
      cliProcesses: processes.filter((p) => p.kind === "cli").length,
      wmuxProcesses: processes.filter((p) => p.kind === "wmux").length,
      kernels: processes.filter((p) => p.kind === "kernel").length,
    },
    token: latestTokenSnapshot(sessions),
    sessions,
    processes: live,
  };
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${HOST}:${PORT}`);
  if (url.pathname === "/api/snapshot") {
    if (!authorized(url)) {
      text(res, 403, "forbidden");
      return;
    }
    json(res, await snapshot());
    return;
  }
  if (url.pathname === "/" || url.pathname === "/index.html") {
    if (!authorized(url)) {
      text(res, 403, "forbidden");
      return;
    }
    const body = fs.readFileSync(path.join(ROOT, "index.html"));
    res.writeHead(200, {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "no-store",
    });
    res.end(body);
    return;
  }
  text(res, 404, "not found");
});

function authorized(url) {
  return !ACCESS_KEY || url.searchParams.get("key") === ACCESS_KEY;
}

server.listen(PORT, HOST, () => {
  console.log(`Codex dashboard listening on http://${HOST}:${PORT}`);
});
