#!/usr/bin/env python3
"""Run a mindtix brain as a live local site: the export site plus an Ask page.

    python3 serve.py <brain> [port] [folder ...|all]     default port 4321, default folders all

Every page load rebuilds the site from the notes, so edits show on refresh. Ask answers from
the brain with an LLM and keeps each conversation in logs/<date>-chat.md (its memory: the
current chat in full, and recent questions from earlier chats).

LLM, read from the environment or the brain's .env:
    MINDTIX_API_URL (+ MINDTIX_API_KEY)   any OpenAI-compatible endpoint (OmniRoute, Ollama, OpenRouter, ...)
    ANTHROPIC_API_KEY                     otherwise, Claude through the Messages API
    MINDTIX_MODEL                         model name (Claude default: claude-opus-5-5)

Listens on 127.0.0.1 only. Standard library only.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import export  # noqa: E402

SESSION = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{4,6}-chat$")
TURN = re.compile(r"(?m)^## (You|Brain) · ([^\n]*)\n")
CLAUDE_MODEL = "claude-opus-5-5"
NOTES_BUDGET = 60000  # characters of notes sent with each question
SYSTEM = """You are the AI of a mindtix second brain: plain markdown notes about one person, \
what they know, make and learn. Answer their question from the notes below. Talk to them as "you".
- Cite the notes you used as [[folder/note]] wikilinks; the site turns them into links.
- If the notes don't hold the answer, say so plainly, then answer from general knowledge and mark it as such.
- Facts labelled [inferred] are guesses; say so when you rely on one.
- Be short and practical unless they ask for more."""


def config(brain):
    """Environment first, then the brain's .env (KEY=value lines)."""
    env = {}
    try:
        for line in open(os.path.join(brain, ".env"), encoding="utf-8"):
            k, sep, v = line.strip().partition("=")
            if sep and not k.startswith("#"):
                env[k.strip().removeprefix("export ").strip()] = v.strip().strip("'\"")
    except OSError:
        pass
    return lambda k, d="": os.environ.get(k) or env.get(k) or d


def call_llm(brain, system, messages):
    """system = [stable text, per-question text]; messages = [{role, content}]. Returns the answer text."""
    get = config(brain)
    if get("MINDTIX_API_URL"):
        url = get("MINDTIX_API_URL").rstrip("/") + "/chat/completions"
        body = {"model": get("MINDTIX_MODEL", "auto"),
                "messages": [{"role": "system", "content": "\n\n".join(system)}] + messages}
        headers = {"Authorization": "Bearer " + get("MINDTIX_API_KEY")} if get("MINDTIX_API_KEY") else {}
        reply = post(url, body, headers)
        return reply["choices"][0]["message"]["content"]
    if get("ANTHROPIC_API_KEY"):
        url = get("ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/") + "/v1/messages"
        body = {"model": get("MINDTIX_MODEL", CLAUDE_MODEL), "max_tokens": 16000,
                "system": [{"type": "text", "text": system[0], "cache_control": {"type": "ephemeral"}},
                           {"type": "text", "text": system[1]}],
                "messages": messages}
        headers = {"x-api-key": get("ANTHROPIC_API_KEY"), "anthropic-version": "2023-06-01"}
        if body["model"] == CLAUDE_MODEL:  # on a safety decline, the API retries on its recommended model
            body["fallbacks"] = "default"
            headers["anthropic-beta"] = "server-side-fallback-2026-07-01"
        reply = post(url, body, headers)
        if reply.get("stop_reason") == "refusal":
            return "*The model declined to answer this one. Try rephrasing it.*"
        text = "".join(b.get("text", "") for b in reply.get("content", []) if b.get("type") == "text")
        return text + ("\n\n*(cut off: the answer hit the length limit)*" if reply.get("stop_reason") == "max_tokens" else "")
    raise RuntimeError("No LLM set up. Put ANTHROPIC_API_KEY=... (or MINDTIX_API_URL=..., MINDTIX_API_KEY=... "
                       "for an OpenAI-compatible endpoint) in the brain's .env, then ask again.")


def post(url, body, headers):
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json", **headers})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:300]
        raise RuntimeError(f"The LLM returned HTTP {e.code}: {detail}") from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"Couldn't reach the LLM at {url}: {e.reason}") from None


def read_log(path):
    """A chat log as [{role, content, at}]."""
    text = open(path, encoding="utf-8").read()
    heads = list(TURN.finditer(text))
    ends = [h.start() for h in heads[1:]] + [len(text)]
    return [{"role": "user" if h.group(1) == "You" else "assistant", "content": text[h.end():end].strip(), "at": h.group(2)}
            for h, end in zip(heads, ends)]


def sessions(brain):
    logs = os.path.join(brain, "logs")
    out = []
    for f in sorted(os.listdir(logs) if os.path.isdir(logs) else [], reverse=True):
        if f.endswith(".md") and SESSION.match(f[:-3]):
            first = open(os.path.join(logs, f), encoding="utf-8").readline()
            out.append({"id": f[:-3], "title": first.lstrip("# ").strip() or f[:-3]})
    return out


def context(brain, folders, question, history):
    """The notes most related to this question (and the chat so far), plus earlier questions as memory."""
    every = folders == "all"
    notes = []
    for rel, path in export.walk(brain):
        top = rel.split("/")[0]
        if rel.endswith(".md") and "/" in rel and (every or top in folders) and not rel.endswith("README.md"):
            notes.append((rel, export.strip_frontmatter(open(path, encoding="utf-8", errors="ignore").read())))
    words = {w for w in re.findall(r"\w{3,}", (question + " " + " ".join(t["content"] for t in history[-4:] if t["role"] == "user")).lower())}
    scored = sorted(notes, key=lambda n: -sum(min(n[1].lower().count(w), 5) + 5 * (w in n[0].lower()) for w in words))
    picked, size = [], 0
    for rel, text in scored[:12]:
        if size + len(text) > NOTES_BUDGET:
            continue
        picked.append(f"=== {rel} ===\n{text}")
        size += len(text)
    earlier = []
    for s in sessions(brain)[:15]:
        for t in read_log(os.path.join(brain, "logs", s["id"] + ".md")):
            if t["role"] == "user":
                earlier.append(f"- {t['at']}: {t['content'][:200]}")
    stable = SYSTEM
    for name in ("MIND.md", "INDEX.md"):
        try:
            stable += f"\n\n=== {name} ===\n" + open(os.path.join(brain, name), encoding="utf-8").read()
        except OSError:
            pass
    dynamic = "Notes related to this question:\n\n" + ("\n\n".join(picked) or "(none matched)")
    if earlier:
        dynamic += "\n\nQuestions they asked in earlier chats (your memory of them):\n" + "\n".join(earlier[:40])
    return [stable, dynamic]


def ask(brain, folders, session, question):
    """Answer a question in a session (new when session is None) and append both turns to its log."""
    logs = os.path.join(brain, "logs")
    os.makedirs(logs, exist_ok=True)
    now = datetime.now()
    if not session:
        session = now.strftime("%Y-%m-%d-%H%M%S") + "-chat"
    path = os.path.join(logs, session + ".md")
    history = read_log(path) if os.path.isfile(path) else []
    messages = [{"role": t["role"], "content": t["content"]} for t in history] + [{"role": "user", "content": question}]
    answer = call_llm(brain, context(brain, folders, question, history), messages)
    stamp = now.strftime("%Y-%m-%d %H:%M")
    with open(path, "a", encoding="utf-8") as f:
        if not history:
            f.write(f"# {question.splitlines()[0][:80]}\n\n")
        f.write(f"## You · {stamp}\n\n{question.strip()}\n\n## Brain · {datetime.now():%Y-%m-%d %H:%M}\n\n{answer.strip()}\n\n")
    return session, answer


def make_server(brain, port=4321, folders="all"):
    class Handler(BaseHTTPRequestHandler):
        def reply(self, code, body, kind="application/json"):
            data = body.encode() if isinstance(body, str) else json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", kind + "; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            path = self.path.split("?")[0]
            if path in ("/", "/index.html"):
                return self.reply(200, export.build_site(brain, folders, live=True)[0], "text/html")
            if path == "/favicon.ico":
                return self.reply(204, "", "image/x-icon")
            if path == "/api/sessions":
                return self.reply(200, sessions(brain))
            m = re.fullmatch(r"/api/sessions/([^/]+)", path)
            if m and SESSION.match(m.group(1)) and os.path.isfile(os.path.join(brain, "logs", m.group(1) + ".md")):
                return self.reply(200, read_log(os.path.join(brain, "logs", m.group(1) + ".md")))
            self.reply(404, {"error": "not found"})

        def do_POST(self):
            if self.path != "/api/ask":
                return self.reply(404, {"error": "not found"})
            try:
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            except ValueError:
                return self.reply(400, {"error": "bad JSON"})
            question, session = str(body.get("question", "")).strip(), body.get("session") or None
            if not question or (session and not SESSION.match(str(session))):
                return self.reply(400, {"error": "need a question (and a valid session id, if any)"})
            try:
                session, answer = ask(brain, folders, session, question)
            except RuntimeError as e:
                return self.reply(502, {"error": str(e)})
            self.reply(200, {"session": session, "answer": answer})

        def log_message(self, *args):
            pass

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(argv) < 2 or not os.path.isfile(os.path.join(argv[1], "MIND.md")):
        print(__doc__ if len(argv) < 2 else f"{argv[1]} is not a mindtix brain (no MIND.md)")
        return 1
    rest = argv[2:]
    port = int(rest.pop(0)) if rest and rest[0].isdigit() else 4321
    folders = "all" if not rest or rest == ["all"] else tuple(f.strip("/") for f in rest)
    server = make_server(os.path.abspath(argv[1]), port, folders)
    print(f"mindtix live at http://127.0.0.1:{server.server_port}  (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
