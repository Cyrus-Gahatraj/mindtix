"""Self-check for the live site server: python3 tests/test_serve.py (fake LLMs, no network)"""
import json
import os
import shutil
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "skills", "export"))
import serve  # noqa: E402

TEMPLATE = os.path.join(HERE, "..", "skills", "init", "template")
SEEN = []  # (path, headers, body) of every request the fake LLMs got


class FakeLLM(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        SEEN.append((self.path, {k.lower(): v for k, v in self.headers.items()}, body))
        if self.path == "/v1/chat/completions":  # OpenAI-compatible
            n = len(body["messages"])
            out = {"choices": [{"message": {"content": f"{n} messages. See [[sql-joins]]."}}]}
        else:  # Anthropic Messages API
            refuse = "refuse" in body["messages"][-1]["content"]
            out = {"stop_reason": "refusal" if refuse else "end_turn",
                   "content": [] if refuse else [{"type": "text", "text": "From Claude."}]}
        data = json.dumps(out).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


def start(server):
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{server.server_port}"


def call(base, path, body=None):
    req = urllib.request.Request(base + path, json.dumps(body).encode() if body is not None else None,
                                 {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            data = r.read().decode()
            return r.status, json.loads(data) if r.headers["Content-Type"].startswith("application/json") else data
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


for k in ("MINDTIX_API_URL", "MINDTIX_API_KEY", "MINDTIX_MODEL", "ANTHROPIC_API_KEY", "ANTHROPIC_BASE_URL"):
    os.environ.pop(k, None)

with tempfile.TemporaryDirectory() as tmp:
    brain = os.path.join(tmp, "mind")
    shutil.copytree(TEMPLATE, brain)
    open(os.path.join(brain, "knowledge", "sql-joins.md"), "w", encoding="utf-8").write("# SQL joins\n\nA left join keeps every row.\n")
    os.makedirs(os.path.join(brain, "private"))
    open(os.path.join(brain, "private", "id.md"), "w", encoding="utf-8").write("# ID\n\nsecret number 12345\n")
    llm = start(ThreadingHTTPServer(("127.0.0.1", 0), FakeLLM))
    site = start(serve.make_server(brain, 0))

    # The page is the export site with the Ask page on, rebuilt per request, never private/
    code, page = call(site, "/")
    assert code == 200 and '"live": true' in page and "SQL joins" in page and "12345" not in page

    # No LLM set up: a clear error, nothing logged
    code, r = call(site, "/api/ask", {"question": "hi"})
    assert code == 502 and ".env" in r["error"], r
    assert serve.sessions(brain) == [], "a failed question is not logged"

    # OpenAI-compatible endpoint from the brain's .env; a chat keeps its history (memory)
    open(os.path.join(brain, ".env"), "w", encoding="utf-8").write(f"# llm\nMINDTIX_API_URL={llm}/v1\nMINDTIX_API_KEY='k1'\n")
    code, r = call(site, "/api/ask", {"question": "What does a left join keep?"})
    assert code == 200 and r["answer"] == "2 messages. See [[sql-joins]].", r  # system + question
    sid = r["session"]
    path, headers, body = SEEN[-1]
    assert headers["authorization"] == "Bearer k1"
    assert "A left join keeps every row." in body["messages"][0]["content"], "related notes go to the LLM"
    assert "12345" not in json.dumps(body), "private/ never reaches the LLM"
    code, r = call(site, "/api/ask", {"session": sid, "question": "And a right join?"})
    assert r["answer"].startswith("4 messages"), "the second turn carries the first question and answer"
    log = open(os.path.join(brain, "logs", sid + ".md"), encoding="utf-8").read()
    assert log.startswith("# What does a left join keep?") and log.count("## You · ") == 2 and log.count("## Brain · ") == 2
    code, turns = call(site, "/api/sessions/" + sid)
    assert [t["role"] for t in turns] == ["user", "assistant", "user", "assistant"] and turns[2]["content"] == "And a right join?"
    code, listed = call(site, "/api/sessions")
    assert listed == [{"id": sid, "title": "What does a left join keep?"}]

    # A new chat remembers questions from earlier chats
    call(site, "/api/ask", {"question": "New topic"})
    assert "What does a left join keep?" in SEEN[-1][2]["messages"][0]["content"]

    # Session ids can't reach outside logs/
    assert call(site, "/api/sessions/..%2FMIND")[0] == 404
    assert call(site, "/api/ask", {"session": "../MIND", "question": "x"})[0] == 400

    # Claude through the Messages API: headers, model, fallbacks, prompt caching, refusals
    open(os.path.join(brain, ".env"), "w", encoding="utf-8").write(f"ANTHROPIC_API_KEY=sk-test\nANTHROPIC_BASE_URL={llm}\n")
    code, r = call(site, "/api/ask", {"question": "Hello"})
    path, headers, body = SEEN[-1]
    assert code == 200 and r["answer"] == "From Claude." and path == "/v1/messages"
    assert headers["x-api-key"] == "sk-test" and headers["anthropic-version"] == "2023-06-01"
    assert body["model"] == "claude-opus-5-5" and body["fallbacks"] == "default"
    assert headers["anthropic-beta"] == "server-side-fallback-2026-07-01"
    assert body["system"][0]["cache_control"] == {"type": "ephemeral"} and "MIND.md" in body["system"][0]["text"]
    code, r = call(site, "/api/ask", {"question": "please refuse"})
    assert code == 200 and "declined" in r["answer"]

print("serve ok")
