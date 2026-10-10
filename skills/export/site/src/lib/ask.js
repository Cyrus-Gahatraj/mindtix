// Ask: the chat. Each chat is kept in logs/<id>.md, which is also its memory.
//
// Two engines (Settings → Chat):
//   claude   Claude Code (`claude -p`) runs in the brain with the user's own login, one Claude Code
//            session per chat. It reads and edits notes itself and runs the /mindtix commands, with
//            mindtix's hooks (secret guard, auto-commit) as in the terminal.
//   api      An LLM over HTTP answers from the notes most related to the question. Questions only.
//            From the environment or the brain's .env:
//              MINDTIX_API_URL (+ MINDTIX_API_KEY)   any OpenAI-compatible endpoint (OmniRoute, Ollama, ...)
//              ANTHROPIC_API_KEY                     otherwise, Claude through the Messages API
//              MINDTIX_MODEL                         model name (Claude default: claude-opus-5-5)
// Both stream: ask() calls emit({t: "text"|"step"|"session", v}) as the answer comes in.
import fs from "node:fs";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { spawn, spawnSync } from "node:child_process";
import { BRAIN, folders, settings, shown, stripFrontmatter, walk } from "./brain.js";

export const SESSION = /^\d{4}-\d{2}-\d{2}-\d{4,6}-chat$/;
const TURN = /^## (You|Brain) · ([^\n]*)\n/gm;
const CLAUDE_SESSION = /^<!-- claude-session: ([0-9a-f-]{36}) -->$/m;
const CLAUDE_MODEL = "claude-opus-5-5";
export const MODELS = ["opus", "sonnet", "haiku"]; // Claude Code model aliases; "" is the user's default
const NOTES_BUDGET = 60000; // characters of notes sent with each question (api engine)
const WIN = process.platform === "win32";
// Tests point this at a fake: MINDTIX_CLAUDE='["node", "fake-claude.mjs"]'
const CLAUDE = (() => { try { return JSON.parse(process.env.MINDTIX_CLAUDE) } catch { return ["claude"] } })();

/** The mindtix commands the chat offers: [name, argument hint, what it does]. "/today" is short for "/mindtix:today". */
export const COMMANDS = [
  ["today", "", "Your daily 5–10 minutes: due cards, one step, one old question"],
  ["recall", "[topic]", "Review the cards that are due"],
  ["learn", "<topic>", "Learn something by doing: start, teach, quiz, diagnose, spar"],
  ["capture", "<text>", "Save a thought, or file your raw notes into the brain"],
  ["know-me", "", "A short interview so the brain knows you better"],
  ["review", "", "Weekly review: patterns, progress, what to grow"],
  ["reflect", "", "Reread everything and rewrite insight/"],
  ["connect-dots", "", "How everything you know fits together"],
  ["tidy", "", "Health check: links, index, secrets, old guesses"],
  ["forget", "<name or topic>", "Remove someone or something everywhere"],
];
export function expandCommand(q) {
  const m = /^\/(?:mindtix:)?([a-z-]+)(?=\s|$)/.exec(q);
  return m && COMMANDS.some(c => c[0] === m[1]) ? "/mindtix:" + m[1] + q.slice(m[0].length) : q;
}

const SYSTEM = `You are the AI of a mindtix second brain: plain markdown notes about one person, \
what they know, make and learn. Answer their question from the notes below. Talk to them as "you".
- Cite the notes you used as [[folder/note]] wikilinks; the site turns them into links.
- If the notes don't hold the answer, say so plainly, then answer from general knowledge and mark it as such.
- Facts labelled [inferred] are guesses; say so when you rely on one.
- Be short and practical unless they ask for more.`;
// No double quotes: on Windows the args go through a shell
const APPEND = "You are talking to the user in the Ask page of their mindtix web app, not a terminal. " +
  "Your text is shown as markdown. Cite notes as [[folder/note]] wikilinks, which become links. " +
  "Where a skill says to ask with a question tool, ask in plain text instead and wait for their next message. " +
  "Keep replies short and practical unless they ask for more.";
const LOGS = () => path.join(BRAIN, "logs");
const pad = n => String(n).padStart(2, "0");
const stamp = d => `${d.toLocaleDateString("en-CA")} ${pad(d.getHours())}:${pad(d.getMinutes())}`;

/** Environment first, then the brain's .env (KEY=value lines). */
function config() {
  const env = {};
  try {
    for (const line of fs.readFileSync(path.join(BRAIN, ".env"), "utf8").split("\n")) {
      const t = line.trim(), i = t.indexOf("=");
      if (i > 0 && !t.startsWith("#")) env[t.slice(0, i).trim().replace(/^export\s+/, "")] = t.slice(i + 1).trim().replace(/^['"]|['"]$/g, "");
    }
  } catch {}
  return (k, d = "") => process.env[k] || env[k] || d;
}

// ---------- Which engine ----------

/** The environment for `claude`, without the variables of a Claude Code session this server may run inside. */
function cleanEnv() {
  const env = { ...process.env };
  for (const k of Object.keys(env))
    if (/^(CLAUDECODE|CLAUDE_PID|CLAUDE_EFFORT|CLAUDE_CODE_(ENTRYPOINT|EXECPATH|SSE_PORT|CHILD_SESSION|SESSION_\w+|MESSAGING_\w+))$/.test(k)) delete env[k];
  return env;
}
const quote = a => WIN && /[\s"&|<>^]/.test(a) ? `"${a}"` : a;
let found;
/** Whether Claude Code is installed (checked once per server). */
export const hasClaude = () => found ??= (() => {
  try { return spawnSync(CLAUDE[0], [...CLAUDE.slice(1), "--version"], { timeout: 15000, env: cleanEnv(), shell: WIN }).status === 0 } catch { return false }
})();

/** The API engine's AI, or null when none is set up. Never includes a key. */
export function llm() {
  const get = config();
  if (get("MINDTIX_API_URL")) return { kind: "openai", url: get("MINDTIX_API_URL"), model: get("MINDTIX_MODEL", "auto") };
  if (get("ANTHROPIC_API_KEY")) return { kind: "claude", model: get("MINDTIX_MODEL", CLAUDE_MODEL) };
  return null;
}

/** The chat engine in use: Settings decides; unset means Claude Code when it's installed. */
export function engine() {
  const s = settings(), kind = s.engine === "api" || s.engine === "claude" ? s.engine : hasClaude() ? "claude" : "api";
  if (kind === "claude") return { kind, ready: hasClaude(), label: "Claude Code" + (s.model ? " · " + s.model : ""), commands: true };
  const ai = llm(), host = ai?.kind === "openai" ? (URL.canParse(ai.url) ? new URL(ai.url).host : ai.url) : "Claude API";
  return { kind, ready: !!ai, label: ai ? `${host} · ${ai.model}` : "No AI set up", commands: false };
}

/** Save the API engine's AI into the brain's .env (and make sure git ignores it).
 *  Per name: a string sets it, "" removes it, undefined keeps what's there (an empty key field keeps the old key). */
export function saveLLM({ kind, url, key, model }) {
  [url, key, model] = [url, key, model].map(v => String(v ?? "").trim());
  if (/[\r\n]/.test(url + key + model)) throw new Error("Each field is one line.");
  let set;
  if (kind === "claude") set = { ANTHROPIC_API_KEY: key || undefined, MINDTIX_MODEL: model, MINDTIX_API_URL: "" };
  else if (kind === "openai") {
    if (!/^https?:\/\/\S+$/.test(url)) throw new Error("The endpoint is a URL, like http://localhost:20128/v1.");
    set = { MINDTIX_API_URL: url, MINDTIX_API_KEY: key || undefined, MINDTIX_MODEL: model };
  } else throw new Error("Pick Claude or an OpenAI-compatible endpoint.");
  const file = path.join(BRAIN, ".env"), out = [], done = new Set();
  let lines = [];
  try { lines = fs.readFileSync(file, "utf8").split("\n") } catch {}
  for (const line of lines) {
    const name = line.trim().startsWith("#") ? "" : line.split("=")[0].trim().replace(/^export\s+/, "");
    if (!(name in set) || set[name] === undefined) { out.push(line); continue }
    if (set[name] && !done.has(name)) out.push(`${name}=${set[name]}`);
    done.add(name);
  }
  while (out.length && !out.at(-1).trim()) out.pop();
  for (const [name, v] of Object.entries(set)) if (v && !done.has(name)) out.push(`${name}=${v}`);
  fs.writeFileSync(file, out.join("\n") + "\n");
  const ignore = path.join(BRAIN, ".gitignore");
  let gi = "";
  try { gi = fs.readFileSync(ignore, "utf8") } catch {}
  if (!/^\/?\.env$/m.test(gi)) fs.writeFileSync(ignore, gi + (gi && !gi.endsWith("\n") ? "\n" : "") + ".env\n");
  if (!llm()) throw new Error("Claude needs an API key.");
  return llm();
}

// ---------- Claude Code engine ----------

/** One line for the chat about what Claude Code is doing, or null to say nothing. */
function step(b) {
  const i = b.input || {}, rel = p => p ? path.relative(BRAIN, p).replaceAll("\\", "/") || p : "";
  switch (b.name) {
    case "Read": return `Reading ${rel(i.file_path)}`;
    case "Edit": case "Write": case "MultiEdit": case "NotebookEdit": return `Editing ${rel(i.file_path || i.notebook_path)}`;
    case "Grep": return `Searching for “${i.pattern}”`;
    case "Glob": return `Looking for ${i.pattern}`;
    case "Skill": return `Running /${i.skill || i.command || "a skill"}`;
    case "Bash": return i.description ? i.description[0].toUpperCase() + i.description.slice(1) : "Running a command";
    case "Agent": case "Task": return `Asking a helper${i.description ? ": " + i.description : ""}`;
    case "WebSearch": return `Searching the web for “${i.query}”`;
    case "WebFetch": return `Reading ${i.url}`;
    case "TodoWrite": case "ToolSearch": return null;
    default: return b.name.replace(/^mcp__[^_]+(?:_[^_]+)*__/, "");
  }
}

/** Run one turn through `claude -p`, streaming its text and steps. Resolves to the full text. */
function runClaude(prompt, uuid, resume, emit, signal) {
  const s = settings();
  const args = ["-p", "--output-format", "stream-json", "--verbose", "--include-partial-messages",
    "--permission-mode", s.edits === false ? "default" : "acceptEdits", "--append-system-prompt", APPEND,
    ...(resume ? ["--resume", uuid] : ["--session-id", uuid]), ...(MODELS.includes(s.model) ? ["--model", s.model] : [])];
  return new Promise((resolve, reject) => {
    const child = spawn(CLAUDE[0], [...CLAUDE.slice(1), ...args].map(quote), { cwd: BRAIN, env: cleanEnv(), shell: WIN });
    const kill = () => child.kill();
    signal?.addEventListener("abort", kill);
    let buf = "", err = "", result = null;
    const parts = [""];
    const handle = line => {
      let d;
      try { d = JSON.parse(line) } catch { return }
      if (d.type === "stream_event" && d.event?.type === "content_block_delta" && d.event.delta?.type === "text_delta") {
        parts[parts.length - 1] += d.event.delta.text;
        emit({ t: "text", v: d.event.delta.text });
      } else if (d.type === "assistant") {
        for (const b of d.message?.content || []) {
          const said = b.type === "tool_use" && step(b);
          if (said) { emit({ t: "step", v: said }); parts.push("") }
        }
      } else if (d.type === "result") result = d;
    };
    child.stdout.on("data", chunk => {
      buf += chunk;
      for (let i; (i = buf.indexOf("\n")) >= 0; buf = buf.slice(i + 1)) handle(buf.slice(0, i));
    });
    child.stderr.on("data", chunk => { err += chunk });
    child.on("error", e => reject(new Error(e.code === "ENOENT"
      ? "Claude Code isn't installed here (no `claude` command). Install it, or pick the API engine in Settings."
      : `Couldn't start Claude Code: ${e.message}`)));
    child.on("close", code => {
      signal?.removeEventListener("abort", kill);
      handle(buf);
      const text = parts.map(p => p.trim()).filter(Boolean).join("\n\n");
      if (signal?.aborted) return resolve(text);
      if (result?.is_error || (code !== 0 && !text))
        return reject(new Error(String(result?.result || err.trim().split("\n").pop() || `Claude Code stopped (exit ${code}).`).slice(0, 400)));
      resolve(text || String(result?.result || ""));
    });
    child.stdin.end(prompt);
  });
}

// ---------- API engine ----------

async function post(url, body, headers, signal) {
  let r;
  try {
    r = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json", ...headers }, body: JSON.stringify(body),
      signal: AbortSignal.any([AbortSignal.timeout(600_000), ...(signal ? [signal] : [])]) });
  } catch (e) {
    if (signal?.aborted) throw e;
    throw new Error(`Couldn't reach the AI at ${url}: ${e.cause?.code || e.message}`);
  }
  if (!r.ok) throw new Error(`The AI returned HTTP ${r.status}: ${(await r.text()).slice(0, 300)}`);
  return r;
}

/** Server-sent events as parsed JSON objects (a plain JSON reply comes through as one object). */
async function* events(r) {
  if ((r.headers.get("content-type") || "").includes("application/json")) { yield await r.json(); return }
  const dec = new TextDecoder();
  let buf = "";
  for await (const chunk of r.body) {
    buf += dec.decode(chunk, { stream: true });
    for (let i; (i = buf.indexOf("\n")) >= 0; buf = buf.slice(i + 1)) {
      const line = buf.slice(0, i).trim();
      if (!line.startsWith("data:")) continue;
      const data = line.slice(5).trim();
      if (data === "[DONE]") return;
      try { yield JSON.parse(data) } catch {}
    }
  }
}

/** system = [stable text, per-question text]; messages = [{role, content}]. Streams; resolves to the answer. */
async function callLLM(system, messages, emit, signal) {
  const get = config();
  let text = "";
  const say = v => { if (v) { text += v; emit({ t: "text", v }) } };
  try {
    if (get("MINDTIX_API_URL")) {
      const r = await post(get("MINDTIX_API_URL").replace(/\/+$/, "") + "/chat/completions",
        { model: get("MINDTIX_MODEL", "auto"), stream: true, messages: [{ role: "system", content: system.join("\n\n") }, ...messages] },
        get("MINDTIX_API_KEY") ? { Authorization: "Bearer " + get("MINDTIX_API_KEY") } : {}, signal);
      for await (const d of events(r)) say(d.choices?.[0]?.delta?.content ?? d.choices?.[0]?.message?.content);
      return text;
    }
    if (get("ANTHROPIC_API_KEY")) {
      const body = { model: get("MINDTIX_MODEL", CLAUDE_MODEL), max_tokens: 16000, stream: true,
        system: [{ type: "text", text: system[0], cache_control: { type: "ephemeral" } }, { type: "text", text: system[1] }], messages };
      const headers = { "x-api-key": get("ANTHROPIC_API_KEY"), "anthropic-version": "2023-06-01" };
      if (body.model === CLAUDE_MODEL) { // on a safety decline, the API retries on its recommended model
        body.fallbacks = "default";
        headers["anthropic-beta"] = "server-side-fallback-2026-07-01";
      }
      const r = await post(get("ANTHROPIC_BASE_URL", "https://api.anthropic.com").replace(/\/+$/, "") + "/v1/messages", body, headers, signal);
      let stop = null;
      for await (const d of events(r)) {
        if (d.type === "content_block_delta" && d.delta?.type === "text_delta") say(d.delta.text);
        else if (d.type === "message_delta") stop = d.delta?.stop_reason;
        else if (d.type === "error") throw new Error(d.error?.message || "The AI's stream failed.");
        else if (d.type === "message") { stop = d.stop_reason; for (const b of d.content || []) if (b.type === "text") say(b.text) }
      }
      if (stop === "refusal") say((text ? "\n\n" : "") + "*The model declined to answer this one. Try rephrasing it.*");
      if (stop === "max_tokens") say("\n\n*(cut off: the answer hit the length limit)*");
      return text;
    }
  } catch (e) {
    if (signal?.aborted) return text;
    throw e;
  }
  throw new Error("No AI set up yet. Pick one in Settings (or put ANTHROPIC_API_KEY=... or MINDTIX_API_URL=... in the brain's .env).");
}

/** The notes most related to this question (and the chat so far), plus earlier questions as memory. */
function context(question, history) {
  const F = folders();
  const notes = walk().filter(([rel]) => rel.endsWith(".md") && shown(rel, F) && !rel.endsWith("README.md"))
    .map(([rel, abs]) => [rel, stripFrontmatter(fs.readFileSync(abs, "utf8").replace(/\r\n/g, "\n"))]);
  const asked = question + " " + history.slice(-4).filter(t => t.role === "user").map(t => t.content).join(" ");
  const words = [...new Set(asked.toLowerCase().match(/[\p{L}\p{N}_]{3,}/gu) || [])];
  const count = (s, w) => s.split(w).length - 1;
  const score = ([rel, text]) => words.reduce((s, w) => s + Math.min(count(text.toLowerCase(), w), 5) + 5 * rel.toLowerCase().includes(w), 0);
  const picked = [];
  let size = 0;
  for (const [rel, text] of notes.map(n => [n, score(n)]).sort((a, b) => b[1] - a[1]).slice(0, 12).map(([n]) => n)) {
    if (size + text.length > NOTES_BUDGET) continue;
    picked.push(`=== ${rel} ===\n${text}`);
    size += text.length;
  }
  const earlier = sessions().slice(0, 15).flatMap(s => readLog(s.id).filter(t => t.role === "user").map(t => `- ${t.at}: ${t.content.slice(0, 200)}`));
  let stable = SYSTEM;
  for (const name of ["MIND.md", "INDEX.md"]) {
    try { stable += `\n\n=== ${name} ===\n` + fs.readFileSync(path.join(BRAIN, name), "utf8") } catch {}
  }
  let dynamic = "Notes related to this question:\n\n" + (picked.join("\n\n") || "(none matched)");
  if (earlier.length) dynamic += "\n\nQuestions they asked in earlier chats (your memory of them):\n" + earlier.slice(0, 40).join("\n");
  return [stable, dynamic];
}

// ---------- Chats ----------

/** A chat log as [{role, content, at}]. */
export function readLog(id) {
  const text = fs.readFileSync(path.join(LOGS(), id + ".md"), "utf8");
  const heads = [...text.matchAll(TURN)];
  return heads.map((h, i) => ({ role: h[1] === "You" ? "user" : "assistant", at: h[2],
    content: text.slice(h.index + h[0].length, heads[i + 1]?.index ?? text.length).trim() }));
}

export const hasSession = id => SESSION.test(id) && fs.existsSync(path.join(LOGS(), id + ".md"));

export function sessions() {
  let files = [];
  try { files = fs.readdirSync(LOGS()) } catch {}
  return files.filter(f => f.endsWith(".md") && SESSION.test(f.slice(0, -3))).sort().reverse().map(f => {
    const first = fs.readFileSync(path.join(LOGS(), f), "utf8").split("\n")[0];
    return { id: f.slice(0, -3), title: first.replace(/^#\s*/, "").trim() || f.slice(0, -3) };
  });
}

export function deleteSession(id) {
  if (!hasSession(id)) return false;
  fs.unlinkSync(path.join(LOGS(), id + ".md"));
  return true;
}

/** Answer a question in a chat (new when session is empty), streaming through emit, and log both turns. */
export async function ask(session, question, emit = () => {}, signal) {
  fs.mkdirSync(LOGS(), { recursive: true });
  const now = new Date(), title = `# ${question.trim().split("\n")[0].slice(0, 80)}\n\n`;
  let fresh = false;
  // A new chat claims its log at once (exclusive create), a second later if two start together
  for (let t = now.getTime(); !session; t += 1000) {
    const d = new Date(t), id = `${d.toLocaleDateString("en-CA")}-${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}-chat`;
    try { fs.writeFileSync(path.join(LOGS(), id + ".md"), title, { flag: "wx" }); session = id; fresh = true } catch (e) { if (e.code !== "EEXIST") throw e }
  }
  const file = path.join(LOGS(), session + ".md");
  const log = fs.existsSync(file) ? fs.readFileSync(file, "utf8") : "";
  const history = log ? readLog(session) : [];
  try { return await turn(session, file, log, history, question, now, emit, signal) }
  catch (e) { if (fresh) fs.rmSync(file, { force: true }); throw e }
}

async function turn(session, file, log, history, question, now, emit, signal) {
  const prompt = expandCommand(question.trim()), how = engine();
  let uuid = null, answer;
  if (how.kind === "claude") {
    const known = CLAUDE_SESSION.exec(log)?.[1];
    uuid = known || randomUUID();
    emit({ t: "session", v: session });
    answer = await runClaude(prompt, uuid, !!known, emit, signal);
  } else {
    if (prompt.startsWith("/")) throw new Error("Commands like /mindtix:today run through Claude Code. Switch the chat engine in Settings.");
    emit({ t: "session", v: session });
    const messages = [...history.map(t => ({ role: t.role, content: t.content })), { role: "user", content: question }];
    answer = await callLLM(context(question, history), messages, emit, signal);
  }
  if (signal?.aborted) answer = (answer.trim() + "\n\n*(stopped)*").trim();
  let text = log;
  if (uuid && !CLAUDE_SESSION.test(text)) text = text.replace(/^(# [^\n]*\n)\n?/, `$1\n<!-- claude-session: ${uuid} -->\n\n`);
  fs.writeFileSync(file, text + `## You · ${stamp(now)}\n\n${question.trim()}\n\n## Brain · ${stamp(new Date())}\n\n${answer.trim()}\n\n`);
  return { session, answer };
}
