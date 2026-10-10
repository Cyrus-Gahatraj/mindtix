// Read and write a mindtix brain: plain markdown notes on disk, read fresh on every request.
// Skips the same folders as export.py (private/, logs/, raw/imports/, ...).
// Standard library only, so `node --test` runs without an install.
import fs from "node:fs";
import path from "node:path";

// The site's settings live in mindtix.json in this project, read on every request so Settings
// takes effect at once: {"brain": "/path", "folders": "all", "engine": "claude", "model": "", "edits": true}.
// The brain comes from the environment, else mindtix.json, else two folders up (<brain>/exports/site/).
const CONF = process.env.MINDTIX_CONF || "mindtix.json";
const readConf = () => { try { return JSON.parse(fs.readFileSync(CONF, "utf8")) } catch { return {} } };
export const BRAIN = path.resolve(process.env.MINDTIX_BRAIN || readConf().brain || "../..");
export const settings = () => ({ folders: "all", engine: "", model: "", edits: true, ...readConf(),
  ...(process.env.MINDTIX_FOLDERS ? { folders: process.env.MINDTIX_FOLDERS } : {}) });
export function saveSettings(patch) {
  const next = { ...readConf(), ...patch };
  fs.writeFileSync(CONF, JSON.stringify(next, null, 2) + "\n");
  return next;
}
/** The brain folders the site shows: "all" or a list. */
export function folders() {
  const f = String(settings().folders || "all").trim();
  return f === "all" ? "all" : f.split(/[\s,]+/).map(x => x.replace(/^\/+|\/+$/g, "")).filter(Boolean);
}

const SKIP_DIRS = new Set([".git", "private", "logs", "exports", ".obsidian", ".claude", "node_modules"]);
const SKIP_PAGES = new Set(["README.md", "CLAUDE.md", "AGENTS.md", "GEMINI.md"]);
export const IMAGES = { ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml" };
const CARD = /^\s*-\s*(?:\[b([0-5])\s*·\s*due\s+(\d{4}-\d{2}-\d{2})\]\s*)?(.+?)\s*$/;
const OBS_LINK = /(!?)\[\[([^\]]+)\]\]/g;
const CALLOUT = /^(\s*>\s*)\[!(\w+)\][+-]?[ \t]*(.*)$/gm;
const MD_NOISE = /^\s*(#{1,6}\s+|>\s?|[-*+]\s+|\d+\.\s+|\|)|[*_`]|!?\[\[([^\]|#]+)[^\]]*\]\]|\[([^\]]*)\]\([^)]*\)|\[(stated|inferred)[^\]]*\]/gm;
export const INTERVALS = [1, 3, 7, 14, 30, 90]; // days until the next review, per Leitner box
const INDEX_SECTIONS = { self: "Who I am", knowledge: "Knowledge", learning: "Learning now", projects: "Projects", hobbies: "Hobbies" };

export const isBrain = () => fs.existsSync(path.join(BRAIN, "MIND.md"));
export const today = (plus = 0) => new Date(Date.now() + plus * 864e5).toLocaleDateString("en-CA"); // local YYYY-MM-DD
export const noteUrl = id => "/n/" + id.split("/").map(encodeURIComponent).join("/");
// Notes are parsed with \n line ends; a file written back keeps its own (\r\n on Windows checkouts)
const read = p => { try { return fs.readFileSync(p, "utf8").replace(/\r\n/g, "\n") } catch { return null } };
const eolOf = p => { try { return fs.readFileSync(p, "utf8").includes("\r\n") ? "\r\n" : "\n" } catch { return "\n" } };
const top = rel => rel.split("/")[0];
export const shown = (rel, F = folders()) => rel.includes("/") && (F === "all" || F.includes(top(rel)));
const pad = n => String(n).padStart(2, "0");

/** Top-level folders of the brain that a site could show (never private/, logs/, exports/, dot folders). */
export const brainFolders = () => fs.readdirSync(BRAIN, { withFileTypes: true })
  .filter(e => e.isDirectory() && !SKIP_DIRS.has(e.name) && !e.name.startsWith(".")).map(e => e.name).sort();

/** Every exportable file as [relative path, absolute path], like export.walk. */
export function walk(dir = BRAIN, rel = "") {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true }).sort((a, b) => a.name < b.name ? -1 : 1)) {
    const r = rel ? rel + "/" + e.name : e.name;
    if (e.isDirectory()) {
      if (!SKIP_DIRS.has(e.name) && r !== "raw/imports" && r !== "learning/_example") out.push(...walk(path.join(dir, e.name), r));
    } else if (!e.name.startsWith("_example") && e.name !== ".DS_Store") out.push([r, path.join(dir, e.name)]);
  }
  return out;
}

export function stripFrontmatter(s) {
  if (s.startsWith("---\n")) { const end = s.indexOf("\n---\n", 4); if (end !== -1) return s.slice(end + 5) }
  return s;
}

/** Markdown down to readable text, for excerpts and search. */
export const plain = s => s.replace(MD_NOISE, (_, _h, link, text) => link || text || " ").replaceAll("|", " ").replaceAll("---", " ").split(/\s+/).filter(Boolean).join(" ");

function describe(id, src) {
  const head = src.split("\n").find(l => l.startsWith("# "));
  const title = head ? plain(head.slice(2)) : id.split("/").pop();
  // The first real paragraph: not a heading, table, code, or a "Sources: … · Updated: …" line
  const para = src.split("\n\n").map(p => p.split("\n").filter(l => !/^#{1,6} /.test(l)).join("\n").trim()).find(p => p && !/^(\||```|(Sources|Source|Related|Updated|Captured|Tags|Status)\b[^\n]{0,20}:)/i.test(p));
  let excerpt = para ? plain(para) : "";
  if (excerpt.length > 150) excerpt = excerpt.slice(0, 150).trim() + "…";
  return { title, excerpt, text: plain(src) };
}

/** Recall cards in knowledge/: {topic, question, box, due}. */
export function cards() {
  const out = [];
  for (const [rel, abs] of walk()) {
    if (!rel.startsWith("knowledge/") || !rel.endsWith(".md")) continue;
    let inRecall = false;
    for (const line of read(abs).split("\n")) {
      if (line.startsWith("## ")) { inRecall = line.trim().toLowerCase() === "## recall"; continue }
      const m = inRecall && CARD.exec(line);
      if (m && m[3]) out.push({ topic: rel.slice(10, -3), question: m[3], box: +(m[1] || 0), due: m[2] || today() });
    }
  }
  return out;
}

/** The 0-5 levels from the | Topic | Level | table in insight/knowledge.md, highest first. */
export function knowledgeLevels() {
  const out = [];
  for (const line of (read(path.join(BRAIN, "insight", "knowledge.md")) || "").split("\n")) {
    const cells = line.trim().replace(/^\||\|$/g, "").split("|").map(c => c.trim());
    const digits = cells.length > 1 && cells[0] !== "Topic" ? cells[1].match(/\d/g) || [] : [];
    if (digits.length) {
      const value = digits.reduce((s, d) => s + +d, 0) / digits.length;
      out.push({ label: cells[0].replace(/[`*]/g, ""), value, max: 5, text: String(+value.toFixed(2)) });
    }
  }
  return out.sort((a, b) => b.value - a.value);
}

/** The "## About ..." section of MIND.md as {Key: value}, or its first paragraph as Intro (and Name). */
export function about() {
  const text = read(path.join(BRAIN, "MIND.md")) || "";
  const section = (/^## About[^\n]*\n([\s\S]*?)(?=^## |(?![\s\S]))/m.exec(text) || [])[1] || "";
  const out = {};
  for (const l of section.split("\n")) {
    if (!l.startsWith("- ") || !l.includes(":") || l.slice(0, 4).includes("`")) continue;
    const i = l.indexOf(":"), k = l.slice(2, i).trim(), v = l.slice(i + 1);
    if (v.trim() && !v.trim().startsWith("<!--")) out[k] = plain(v);
  }
  if (!Object.keys(out).length) {
    const para = section.split("\n\n").map(p => p.trim()).find(p => p && !/^(-|<!--|Labels:)/.test(p));
    if (para) {
      const intro = para.split(/\s+/).join(" ");
      out.Intro = intro.endsWith(":") && intro.includes(". ") ? intro.slice(0, intro.lastIndexOf(". ")) + "." : intro;
      const name = out.Intro.split(",")[0];
      if (name.split(" ").length <= 4 && name.split(" ").every(w => /^[A-Z][^A-Z]*$/.test(w))) out.Name = name;
    }
  }
  return out;
}

/** The whole brain as the site sees it: notes (with links resolved), backlinks, cards, insight. */
export function load() {
  const F = folders(), files = walk().filter(([rel]) => shown(rel, F));
  const pages = files.filter(([rel]) => rel.endsWith(".md") && !SKIP_PAGES.has(rel.split("/").pop()))
    .sort(([a], [b]) => top(a).localeCompare(top(b)) || a.split("/").length - b.split("/").length || (a < b ? -1 : 1));
  const ids = pages.map(([rel]) => rel.slice(0, -3)), idSet = new Set(ids), byBase = {};
  for (const id of ids) byBase[id.split("/").pop().toLowerCase()] ??= id;
  const images = {};
  for (const [rel] of files) if (IMAGES[path.extname(rel).toLowerCase()]) images[rel.split("/").pop().toLowerCase()] = rel;
  const resolve = t => {
    t = t.trim().replace(/\.md$/, "");
    return idSet.has(t) ? t : byBase[t.split("/").pop().toLowerCase()];
  };
  // Obsidian links, embeds and callouts as plain markdown; notes left out become plain text
  const toMd = (src, links, titles = false) => src.replace(OBS_LINK, (_, bang, inner) => {
    let [target, ...alias] = inner.split("|");
    target = target.split("#")[0].trim(); alias = alias.join("|").trim();
    if (bang && IMAGES[path.extname(target).toLowerCase()]) {
      const img = images[target.split("/").pop().toLowerCase()];
      return img ? `![${alias}](</file/${img}>)` : `*(missing image: ${target})*`;
    }
    const id = resolve(target);
    if (id) { links.add(id); return `[${alias || (titles && byTitle[id]) || target}](<${noteUrl(id)}>)` }
    return alias || target;
  }).replace(CALLOUT, (_, q, kind, rest) => `${q}**${kind[0].toUpperCase() + kind.slice(1).toLowerCase()}${rest.trim() ? ": " + rest.trim() : ""}**`);

  const notes = [], edges = [], byTitle = {};
  pages.forEach(([rel, abs], i) => {
    const id = ids[i], src = stripFrontmatter(read(abs) || ""), links = new Set();
    const { title, excerpt, text } = describe(id, src);
    notes.push({ id, folder: top(rel), title, excerpt, text: text.slice(0, 4000), words: text.split(" ").filter(Boolean).length,
      md: toMd(src, links), mod: Math.floor(fs.statSync(abs).mtimeMs / 1000) });
    byTitle[id] = title;
    for (const t of [...links].sort()) if (t !== id) edges.push([id, t]);
  });
  const me = about(), has = f => F === "all" || F.includes(f);
  const data = { name: me.Name || "", notes, links: edges, byId: Object.fromEntries(notes.map(n => [n.id, n])), resolve,
    linkify: s => toMd(s, new Set(), true), folders: [...new Set(notes.map(n => n.folder))], back: {} };
  for (const [a, b] of edges) (data.back[b] ||= []).includes(a) || data.back[b].push(a);
  if (has("knowledge")) data.cards = cards();
  if (has("self")) data.about = Object.fromEntries(Object.entries(me).filter(([k]) => k !== "Name"));
  // The profile picture shows whatever folders are chosen: it's the owner's, on their own machine
  data.photo = photo();
  data.photoV = data.photo ? Math.floor(fs.statSync(path.join(BRAIN, data.photo)).mtimeMs) : 0;
  if (has("insight")) {
    try { data.scores = JSON.parse(read(path.join(BRAIN, "insight", "scores.json"))) } catch { data.scores = {} }
    data.knowledge = knowledgeLevels();
  }
  return data;
}

// ---------- Writing ----------

const KEYS = /sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----/;
const ASSIGN = /\b(?:password|passwd|api[_-]?key|secret|token)\s*[:=]\s*['"]?([^\s'",;)]{8,})/gi;
const NOT_A_SECRET = /^(?:os\.|process\.env|getenv|environ|env\b|env\(|config\.|settings\.|self\.|req\.|request\.|\$|\{|<|%|your[_-]|my[_-]|example|placeholder|changeme|dummy|test|fake|x{4,}|\*{4,}|\.{3})/i;

/** The first thing that looks like a real secret (same rules as hooks/guard.py), or null. */
export function findSecret(text) {
  const k = KEYS.exec(text);
  if (k) return k[0];
  for (const m of text.matchAll(ASSIGN)) if (!NOT_A_SECRET.test(m[1])) return m[1];
  return null;
}

export class WriteError extends Error { constructor(msg, status = 400) { super(msg); this.status = status } }

/** Folders the site may write notes into: those shown, minus insight/ (only /mindtix:reflect writes it). */
export const writable = () => fs.readdirSync(BRAIN, { withFileTypes: true })
  .filter(e => e.isDirectory() && !SKIP_DIRS.has(e.name) && !e.name.startsWith(".") && e.name !== "insight" && shown(e.name + "/x"))
  .map(e => e.name).sort();

/** A note id ("folder/sub/name") checked and turned into its absolute .md path. */
export function notePath(id) {
  id = String(id || "").trim().replace(/\.md$/, "");
  const parts = id.split("/");
  if (parts.length < 2 || parts.some(p => !p || p.startsWith(".") || /[\\:*?"<>|\0]/.test(p)))
    throw new WriteError("A note needs a folder and a name, like knowledge/sql-joins.");
  if (!writable().includes(parts[0]) || id.startsWith("raw/imports/") || id.startsWith("learning/_example/"))
    throw new WriteError(`Notes can't be written to ${parts[0]}/ from the site.`, 403);
  const abs = path.resolve(BRAIN, id + ".md");
  if (!abs.startsWith(BRAIN + path.sep)) throw new WriteError("That path leaves the brain.", 403);
  return { id, abs };
}

/** A note's source and modified time (ms) for the editor. */
export function readNote(id) {
  const { abs } = notePath(id);
  const src = read(abs);
  return src === null ? null : { src, mod: fs.statSync(abs).mtimeMs };
}

/** Save a note. mod is the time the editor loaded it (null for a new note); a newer file on disk wins. */
export function saveNote(id, md, mod) {
  const note = notePath(id);
  const secret = findSecret(md);
  if (secret) throw new WriteError(`This looks like a secret (${secret.slice(0, 6)}…). Brains never store passwords, keys or tokens; take it out and save again.`, 422);
  const exists = fs.existsSync(note.abs);
  if (mod == null && exists) throw new WriteError(`${note.id} already exists. Open it and edit it instead.`, 409);
  if (mod != null && (!exists || Math.abs(fs.statSync(note.abs).mtimeMs - mod) > 1))
    throw new WriteError("This note changed on disk since you opened it (maybe Claude edited it). Copy your text, reload, and merge.", 409);
  fs.mkdirSync(path.dirname(note.abs), { recursive: true });
  const eol = exists ? eolOf(note.abs) : "\n";
  fs.writeFileSync(note.abs, (md.endsWith("\n") ? md : md + "\n").replace(/\r?\n/g, eol));
  if (!exists) addToIndex(note.id, md);
  return { id: note.id, mod: fs.statSync(note.abs).mtimeMs };
}

/** A new note gets its one line in INDEX.md, at the end of its folder's section. */
function addToIndex(id, md) {
  const file = path.join(BRAIN, "INDEX.md"), text = read(file), heading = INDEX_SECTIONS[top(id)];
  if (text === null || !heading || text.includes(`[[${id}]]`)) return;
  const lines = text.split("\n"), start = lines.findIndex(l => l.trim() === "## " + heading);
  if (start === -1) return;
  let end = start + 1;
  while (end < lines.length && !lines[end].startsWith("## ")) end++;
  while (end > start + 1 && !lines[end - 1].trim()) end--;
  const { title, excerpt } = describe(id, stripFrontmatter(md));
  const hook = (excerpt || title).replace(/…$/, "");
  lines.splice(end, 0, `- [[${id}]]: ${hook.length > 80 ? hook.slice(0, 80).trim() + "…" : hook}`);
  fs.writeFileSync(file, lines.join(eolOf(file)));
}

// ---------- Profile picture: self/photo.<png|jpg|webp> ----------

const PHOTO = /^photo\.(png|jpe?g|webp)$/i;
const MAGIC = { png: [0x89, 0x50, 0x4e, 0x47], jpg: [0xff, 0xd8, 0xff], webp: [0x52, 0x49, 0x46, 0x46] };
export const PHOTO_TYPES = { png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", webp: "image/webp" };

/** The profile picture's path in the brain ("self/photo.jpg"), or "". */
export function photo() {
  try { const f = fs.readdirSync(path.join(BRAIN, "self")).find(f => PHOTO.test(f)); return f ? "self/" + f : "" } catch { return "" }
}

/** Save a profile picture sent as a data: URL (the browser has already cropped it), replacing any old one. */
export function savePhoto(dataUrl) {
  const m = /^data:image\/(png|jpeg|webp);base64,([A-Za-z0-9+/=]+)$/.exec(String(dataUrl || ""));
  if (!m) throw new WriteError("Send a PNG, JPEG or WebP picture.");
  const ext = m[1] === "jpeg" ? "jpg" : m[1], buf = Buffer.from(m[2], "base64");
  if (buf.length > 4_000_000) throw new WriteError("That picture is over 4 MB. Pick a smaller one.", 413);
  if (!MAGIC[ext].every((b, i) => buf[i] === b)) throw new WriteError("That file isn't the picture it says it is.");
  fs.mkdirSync(path.join(BRAIN, "self"), { recursive: true });
  removePhoto();
  fs.writeFileSync(path.join(BRAIN, "self", "photo." + ext), buf);
  return { photo: "self/photo." + ext };
}

export function removePhoto() {
  const p = photo();
  if (p) fs.rmSync(path.join(BRAIN, p));
  return { photo: "" };
}

/** Quick capture: a line in today's raw/notes/YYYY-MM-DD.md (the user's own notes; /mindtix:capture files them). */
export function capture(text) {
  text = String(text || "").trim();
  if (!text) throw new WriteError("Write something first.");
  const secret = findSecret(text);
  if (secret) throw new WriteError(`This looks like a secret (${secret.slice(0, 6)}…). Brains never store passwords, keys or tokens.`, 422);
  const rel = `raw/notes/${today()}.md`, file = path.join(BRAIN, rel), now = new Date();
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const head = fs.existsSync(file) ? "" : `# Notes · ${today()}\n\n`;
  fs.appendFileSync(file, `${head}- ${pad(now.getHours())}:${pad(now.getMinutes())} ${text.replace(/\s*\n\s*/g, "\n  ")}\n`);
  return { file: rel };
}

/** Due cards for one round: lowest box, then oldest; weaker topics first; at most 3 per topic and 10 in all. */
export function dueCards(data) {
  const level = Object.fromEntries((data.knowledge || knowledgeLevels()).map(k => [k.label.toLowerCase(), k.value]));
  const lv = c => level[(data.byId["knowledge/" + c.topic]?.title || c.topic).toLowerCase()] ?? level[c.topic.toLowerCase()] ?? 5;
  const due = (data.cards || []).filter(c => c.due <= today()).sort((a, b) => a.box - b.box || (a.due < b.due ? -1 : a.due > b.due ? 1 : 0) || lv(a) - lv(b));
  const per = {}, out = [];
  for (const c of due) if (out.length < 10 && (per[c.topic] = (per[c.topic] || 0) + 1) <= 3) out.push(c);
  return out;
}

/** Grade one card in place: right moves it a box up, wrong sends it to b0 and into learning/mistakes.md. Logs the round. */
export function grade(topic, question, right) {
  const { abs } = notePath("knowledge/" + topic);
  const text = read(abs);
  if (text === null) throw new WriteError("No such topic.", 404);
  const lines = text.split("\n");
  let inRecall = false, at = -1, box = 0;
  lines.forEach((l, i) => {
    if (l.startsWith("## ")) inRecall = l.trim().toLowerCase() === "## recall";
    const m = inRecall && at === -1 && CARD.exec(l);
    if (m && m[3] === question) { at = i; box = +(m[1] || 0) }
  });
  if (at === -1) throw new WriteError("That card isn't in the note any more. Reload.", 409);
  box = right ? Math.min(box + 1, 5) : 0;
  lines[at] = `- [b${box} · due ${today(INTERVALS[right ? box : 0])}] ${question}`;
  log(lines, right, question);
  fs.writeFileSync(abs, lines.join(eolOf(abs)));
  if (!right) {
    const file = path.join(BRAIN, "learning", "mistakes.md");
    let m = read(file) ?? "# Mistakes\n\n| Date | Topic | Mistake | Guessed root cause |\n|---|---|---|---|\n";
    fs.mkdirSync(path.dirname(file), { recursive: true });
    const eol = eolOf(file);
    fs.writeFileSync(file, (m.replace(/\n*$/, "\n") + `| ${today()} | ${topic} | missed: ${question.replaceAll("|", "/")} | |\n`).replaceAll("\n", eol));
  }
  return { box, due: today(INTERVALS[right ? box : 0]) };
}

/** Today's "- YYYY-MM-DD recall: right/total, missed: ..." line in ## Log, updated as cards are graded. */
function log(lines, right, question) {
  let start = lines.findIndex(l => l.trim().toLowerCase() === "## log");
  if (start === -1) {
    let end = lines.length;
    while (end > 0 && (!lines[end - 1].trim() || lines[end - 1].startsWith("Sources:"))) end--;
    lines.splice(end, 0, "", "## Log", ...(lines[end]?.trim() ? [""] : []));
    start = end + 1;
  }
  let end = start + 1;
  while (end < lines.length && lines[end].startsWith("- ")) end++;
  const prev = /^- (\d{4}-\d{2}-\d{2}) recall: (\d+)\/(\d+)(?:, missed: (.*))?$/.exec(lines[end - 1] || "");
  const same = prev && prev[1] === today();
  const [ok, all] = same ? [+prev[2], +prev[3]] : [0, 0];
  const missed = [...(same && prev[4] ? prev[4].split("; ") : []), ...(right ? [] : [question])];
  const line = `- ${today()} recall: ${ok + right}/${all + 1}${missed.length ? ", missed: " + missed.join("; ") : ""}`;
  same ? (lines[end - 1] = line) : lines.splice(end, 0, line);
}
