// Self-check for the site's brain and chat code: npm test  (fake LLMs and a fake `claude`; no network, no install)
import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const tmp = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), "mindtix-")));
const brain = path.join(tmp, "brain");
fs.cpSync(path.join(HERE, "../../../init/template"), brain, { recursive: true });
const w = (rel, s) => { fs.mkdirSync(path.dirname(path.join(brain, rel)), { recursive: true }); fs.writeFileSync(path.join(brain, rel), s) };
const r = rel => fs.readFileSync(path.join(brain, rel), "utf8");
const lf = rel => r(rel).replace(/\r\n/g, "\n"); // template files are CRLF on a Windows checkout
w("knowledge/sql-joins.md", "# SQL joins\n\nA left join keeps every row.\n\n## Recall\n- [b1 · due 2020-01-01] What does a left join keep?\n- Which join drops rows?\n\nSources: lecture\n");
w("private/id.md", "# ID\n\nsecret number 12345\n");
w("MIND.md", r("MIND.md").replace("- Name:", "- Name: Ada *Lovelace* [stated]"));
for (const k of ["MINDTIX_API_URL", "MINDTIX_API_KEY", "MINDTIX_MODEL", "ANTHROPIC_API_KEY", "ANTHROPIC_BASE_URL", "MINDTIX_FOLDERS"]) delete process.env[k];
Object.assign(process.env, {
  MINDTIX_BRAIN: brain, MINDTIX_CONF: path.join(tmp, "mindtix.json"), FAKE_CLAUDE_LOG: path.join(tmp, "claude.log"),
  MINDTIX_CLAUDE: JSON.stringify([process.execPath, path.join(HERE, "fake-claude.mjs")]), CLAUDECODE: "1",
});
const B = await import("../src/lib/brain.js");
const A = await import("../src/lib/ask.js");
const calls = () => fs.readFileSync(process.env.FAKE_CLAUDE_LOG, "utf8").trim().split("\n").map(l => JSON.parse(l));
const arg = (c, flag) => c.args[c.args.indexOf(flag) + 1];

// Fake LLMs that stream: an OpenAI-compatible endpoint and the Anthropic Messages API
const SEEN = [];
const llm = http.createServer((req, res) => {
  let data = "";
  req.on("data", c => data += c).on("end", () => {
    const body = JSON.parse(data);
    SEEN.push({ path: req.url, headers: req.headers, body });
    res.writeHead(200, { "Content-Type": "text/event-stream" });
    const ev = o => res.write(`data: ${JSON.stringify(o)}\n\n`);
    if (req.url === "/v1/chat/completions") {
      ev({ choices: [{ delta: { content: `${body.messages.length} messages.` } }] });
      ev({ choices: [{ delta: { content: " See [[sql-joins]]." } }] });
      res.end("data: [DONE]\n\n");
    } else {
      const refuse = body.messages.at(-1).content.includes("refuse");
      if (!refuse) { ev({ type: "content_block_delta", delta: { type: "text_delta", text: "From " } }); ev({ type: "content_block_delta", delta: { type: "text_delta", text: "Claude." } }) }
      ev({ type: "message_delta", delta: { stop_reason: refuse ? "refusal" : "end_turn" } });
      res.end();
    }
  });
});
await new Promise(ok => llm.listen(0, "127.0.0.1", ok));
const base = `http://127.0.0.1:${llm.address().port}`;
test.after(() => { llm.close(); fs.rmSync(tmp, { recursive: true, force: true }) });

test("load reads the notes, never private/, and resolves links", () => {
  const D = B.load();
  assert.ok(D.byId["knowledge/sql-joins"]);
  assert.ok(!JSON.stringify(D.notes).includes("12345"));
  assert.equal(D.linkify("see [[sql-joins]] and [[sql-joins|joins]]"), "see [SQL joins](</n/knowledge/sql-joins>) and [joins](</n/knowledge/sql-joins>)", "chat links show the title, or the alias");
  assert.equal(D.cards.length, 2);
  assert.equal(D.name, "Ada Lovelace", "labels and markdown are stripped from About me");
});

test("settings: folders apply at once; unknown values never reach the file", () => {
  B.saveSettings({ folders: "knowledge" });
  assert.deepEqual(B.load().folders, ["knowledge"]);
  B.saveSettings({ folders: "all" });
  assert.ok(B.load().folders.length > 1);
  assert.ok(B.brainFolders().includes("knowledge") && !B.brainFolders().includes("private") && !B.brainFolders().includes("logs"));
});

test("chat engine: Claude Code when it's installed, unless Settings says API", () => {
  assert.equal(A.engine().kind, "claude");
  B.saveSettings({ engine: "api" });
  assert.deepEqual(A.engine(), { kind: "api", ready: false, label: "No AI set up", commands: false });
  assert.equal(A.expandCommand("/today"), "/mindtix:today");
  assert.equal(A.expandCommand("/learn rust"), "/mindtix:learn rust");
  assert.equal(A.expandCommand("/mindtix:recall sql"), "/mindtix:recall sql");
  assert.equal(A.expandCommand("/unknown x"), "/unknown x");
});

test("api engine: no AI is a clear error, and commands need Claude Code", async () => {
  await assert.rejects(A.ask(null, "hi"), /Settings/);
  w(".env", `MINDTIX_API_URL=${base}/v1\n`);
  await assert.rejects(A.ask(null, "/today"), /Claude Code/);
  assert.deepEqual(A.sessions(), [], "a failed question is not logged");
});

test("api engine: OpenAI-compatible streaming, chat memory, logs", async () => {
  w(".env", `# llm\nMINDTIX_API_URL=${base}/v1\nMINDTIX_API_KEY='k1'\n`);
  const got = [];
  const first = await A.ask(null, "What does a left join keep?", e => got.push(e));
  assert.equal(first.answer, "2 messages. See [[sql-joins]].");
  assert.deepEqual(got.map(e => e.t), ["session", "text", "text"], "the answer streams");
  assert.equal(SEEN.at(-1).body.stream, true);
  assert.equal(SEEN.at(-1).headers.authorization, "Bearer k1");
  assert.ok(SEEN.at(-1).body.messages[0].content.includes("A left join keeps every row."), "related notes go to the LLM");
  assert.ok(!JSON.stringify(SEEN.at(-1).body).includes("12345"), "private/ never reaches the LLM");
  const second = await A.ask(first.session, "And a right join?");
  assert.match(second.answer, /^4 messages/, "the second turn carries the first");
  const log = r(`logs/${first.session}.md`);
  assert.ok(log.startsWith("# What does a left join keep?") && log.split("## You · ").length === 3 && log.split("## Brain · ").length === 3);
  assert.deepEqual(A.readLog(first.session).map(t => t.role), ["user", "assistant", "user", "assistant"]);
  await A.ask(null, "New topic");
  assert.ok(SEEN.at(-1).body.messages[0].content.includes("What does a left join keep?"), "new chats remember earlier questions");
  assert.ok(!A.hasSession("../MIND") && !A.SESSION.test("../MIND"));
  assert.ok(A.deleteSession(first.session) && !A.hasSession(first.session) && !A.deleteSession("../MIND"));
});

test("api engine: Claude headers, model, fallbacks, caching, refusals", async () => {
  w(".env", `ANTHROPIC_API_KEY=sk-test\nANTHROPIC_BASE_URL=${base}\n`);
  assert.equal((await A.ask(null, "Hello")).answer, "From Claude.");
  const { path: p, headers, body } = SEEN.at(-1);
  assert.equal(p, "/v1/messages");
  assert.equal(headers["x-api-key"], "sk-test");
  assert.equal(headers["anthropic-version"], "2023-06-01");
  assert.equal(headers["anthropic-beta"], "server-side-fallback-2026-07-01");
  assert.equal(body.model, "claude-opus-5-5");
  assert.equal(body.fallbacks, "default");
  assert.equal(body.stream, true);
  assert.deepEqual(body.system[0].cache_control, { type: "ephemeral" });
  assert.ok(body.system[0].text.includes("MIND.md"));
  assert.match((await A.ask(null, "please refuse")).answer, /declined/);
});

test("claude engine: runs /mindtix commands in the brain, streams steps, keeps one session per chat", async () => {
  B.saveSettings({ engine: "claude", model: "", edits: true });
  const got = [];
  const first = await A.ask(null, "/today", e => got.push(e));
  assert.equal(first.answer, "Let me look.\n\nA left join keeps every row. [[sql-joins]]");
  assert.deepEqual(got.filter(e => e.t === "step").map(e => e.v), ["Reading knowledge/sql-joins.md"], "tool use shows as steps; TodoWrite stays quiet");
  let c = calls().at(-1);
  assert.equal(c.input, "/mindtix:today", "the command goes in on stdin, expanded");
  assert.equal(c.cwd, brain, "Claude Code runs in the brain");
  assert.equal(c.claudecode, null, "the parent Claude Code session's variables are dropped");
  assert.equal(arg(c, "--permission-mode"), "acceptEdits");
  assert.equal(arg(c, "--output-format"), "stream-json");
  assert.ok(c.args.includes("--include-partial-messages") && !c.args.includes("--model"));
  const uuid = arg(c, "--session-id");
  assert.match(r(`logs/${first.session}.md`), new RegExp(`^# /today\n\n<!-- claude-session: ${uuid} -->\n\n## You · `));

  B.saveSettings({ model: "haiku", edits: false });
  await A.ask(first.session, "and then?");
  c = calls().at(-1);
  assert.equal(arg(c, "--resume"), uuid, "the next turn resumes the same Claude Code session");
  assert.ok(!c.args.includes("--session-id"));
  assert.equal(arg(c, "--model"), "haiku");
  assert.equal(arg(c, "--permission-mode"), "default", "edits off: Claude Code can only read");
  assert.equal(A.readLog(first.session).length, 4);

  const before = A.sessions().length;
  await assert.rejects(A.ask(null, "please fail"), /Something broke/);
  assert.equal(A.sessions().length, before, "a failed turn is not logged");
  B.saveSettings({ model: "", edits: true });
});

test("write: new notes go in INDEX.md; guards hold", () => {
  const saved = B.saveNote("knowledge/rust", "# Rust\n\nOwnership moves values.", null);
  assert.match(lf("INDEX.md"), /## Knowledge\n- \[\[knowledge\/rust\]\]: Ownership moves values\./);
  B.saveNote("knowledge/rust", "# Rust\n\nEdited.", saved.mod);
  assert.equal(r("knowledge/rust.md"), "# Rust\n\nEdited.\n");
  const fails = [["knowledge/rust", null, 409], ["knowledge/rust", 1, 409], ["insight/mind", null, 403], ["private/x", null, 403],
    ["logs/x", null, 403], ["knowledge/../../x", null, 400], ["MIND", null, 400], ["raw/imports/x", null, 403]];
  for (const [id, mod, status] of fails) assert.throws(() => B.saveNote(id, "# x", mod), e => e.status === status, id);
  assert.throws(() => B.saveNote("knowledge/k", "token: ghp_abcdefghijklmnopqrstuvwxyz0123456789", null), e => e.status === 422);
  assert.equal(B.findSecret("api_key = process.env.KEY"), null);
});

test("capture: a timed line in today's raw note; secrets refused", () => {
  assert.deepEqual(B.capture("first idea"), { file: `raw/notes/${B.today()}.md` });
  B.capture("second\nline two");
  assert.match(r(`raw/notes/${B.today()}.md`), new RegExp(`^# Notes · ${B.today()}\n\n- \\d\\d:\\d\\d first idea\n- \\d\\d:\\d\\d second\n  line two\n$`));
  assert.throws(() => B.capture("  "), e => e.status === 400);
  assert.throws(() => B.capture("password: hunter2hunter2"), e => e.status === 422);
});

test("recall: boxes move, misses go to mistakes.md, the round is logged", () => {
  assert.deepEqual(B.dueCards(B.load()).map(c => c.box), [0, 1]);
  assert.deepEqual(B.grade("sql-joins", "What does a left join keep?", true), { box: 2, due: B.today(7) });
  assert.deepEqual(B.grade("sql-joins", "Which join drops rows?", false), { box: 0, due: B.today(1) });
  const note = r("knowledge/sql-joins.md");
  assert.ok(note.includes(`- [b2 · due ${B.today(7)}] What does a left join keep?`));
  assert.ok(note.includes(`## Log\n- ${B.today()} recall: 1/2, missed: Which join drops rows?\n\nSources: lecture`), note);
  assert.ok(lf("learning/mistakes.md").endsWith(`| ${B.today()} | sql-joins | missed: Which join drops rows? | |\n`));
  assert.throws(() => B.grade("sql-joins", "not a card", true), e => e.status === 409);
});

test("api setup: Settings saves the AI to .env, keeps other lines, and git ignores it", () => {
  w(".env", "OMNIROUTE_URL=x\nMINDTIX_API_KEY=old\n");
  w(".gitignore", "logs/*\n");
  assert.deepEqual(A.saveLLM({ kind: "openai", url: "http://localhost:20128/v1", key: "", model: "" }),
    { kind: "openai", url: "http://localhost:20128/v1", model: "auto" });
  assert.equal(r(".env"), "OMNIROUTE_URL=x\nMINDTIX_API_KEY=old\nMINDTIX_API_URL=http://localhost:20128/v1\n", "an empty key keeps the old one");
  assert.match(r(".gitignore"), /^\.env$/m);
  assert.equal(A.saveLLM({ kind: "claude", key: "sk-ant-1", model: "" }).kind, "claude");
  assert.ok(!r(".env").includes("MINDTIX_API_URL"), "switching to Claude drops the endpoint, which would win");
  assert.throws(() => A.saveLLM({ kind: "openai", url: "nope" }), /URL/);
  assert.throws(() => A.saveLLM({ kind: "claude", key: "a\nb" }), /one line/);
});

test("profile picture: saved in self/, replaces the old one, checked and removable", () => {
  const url = (type, bytes) => `data:image/${type};base64,` + Buffer.from(bytes).toString("base64");
  assert.equal(B.photo(), "");
  assert.deepEqual(B.savePhoto(url("png", [0x89, 0x50, 0x4e, 0x47, 1, 2])), { photo: "self/photo.png" });
  assert.deepEqual(B.savePhoto(url("jpeg", [0xff, 0xd8, 0xff, 0xe0, 1])), { photo: "self/photo.jpg" });
  assert.ok(!fs.existsSync(path.join(brain, "self/photo.png")), "the old picture goes");
  assert.equal(B.load().photo, "self/photo.jpg");
  assert.throws(() => B.savePhoto(url("jpeg", [0x3c, 0x73, 0x76, 0x67])), e => e.status === 400, "bytes must match the type");
  assert.throws(() => B.savePhoto("data:image/svg+xml;base64,PHN2Zz4="), e => e.status === 400, "no SVG");
  assert.throws(() => B.savePhoto("../../x"), e => e.status === 400);
  B.removePhoto();
  assert.equal(B.photo(), "");
});

test("windows line ends (CRLF): parsed like LF, and kept when the site writes", () => {
  const crlf = s => s.replace(/\r?\n/g, "\r\n");
  w("INDEX.md", crlf(r("INDEX.md")));
  w("knowledge/crlf.md", crlf("---\ntags: x\n---\n# CRLF note\nA summary line.\n\n## Recall\n- [b0 · due 2020-01-01] Does it parse?\n\n## Log\n- 2020-01-01 recall: 1/1\n"));
  const n = B.load().byId["knowledge/crlf"];
  assert.equal(n.title, "CRLF note");
  assert.equal(n.excerpt, "A summary line.", "frontmatter and the heading are skipped");
  B.grade("crlf", "Does it parse?", true);
  B.saveNote("knowledge/crlf-two", "# Two\n\nNew.", null);
  for (const f of ["knowledge/crlf.md", "INDEX.md"]) assert.ok(!/(^|[^\r])\n/.test(r(f)), f + " keeps CRLF everywhere");
  assert.match(r("knowledge/crlf.md"), new RegExp(`\\[b1 · due ${B.today(3)}\\] Does it parse\\?\\r\\n`));
  assert.match(r("knowledge/crlf.md"), new RegExp(`- ${B.today()} recall: 1/1\\r\\n`));
  const saved = B.readNote("knowledge/crlf");
  B.saveNote("knowledge/crlf", saved.src + "\nMore.", saved.mod);
  assert.ok(!/(^|[^\r])\n/.test(r("knowledge/crlf.md")), "an edit keeps the note's CRLF");
});
