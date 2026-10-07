#!/usr/bin/env python3
"""Convert a data export into plain text that an AI can read.

    python3 to_text.py <export folder, file or .zip> <output folder>

Handles, with only the standard library:
- HTML pages (Instagram, Facebook, Google Takeout)  -> .txt, scripts and styles removed
- Instagram/Facebook message threads (message_1.html / message_1.json)
                                                    -> one compact, chronological .txt per thread
- ChatGPT export (conversations.json)               -> one .md per conversation
- Claude export (conversations.json)                -> one .md per conversation
- WhatsApp chat exports (.txt), notes (.md/.txt)    -> copied as is
- any other JSON                                    -> flattened "key: value" text
- media (images, video, audio)                      -> skipped, only counted

Keys, passwords ("my wifi password is …"), phone and card numbers are masked in the
output, so they never land in the brain.

Writes `_manifest.md` in the output folder: what was converted, sizes, and what was skipped.
Never edits the input.
"""
import html
import json
import os
import re
import sys
import tempfile
import zipfile
from html.parser import HTMLParser

MEDIA = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".mp4", ".mov", ".m4a",
         ".mp3", ".aac", ".opus", ".ogg", ".wav", ".webm", ".pdf", ".zip"}
BLOCK = {"div", "p", "br", "li", "tr", "td", "h1", "h2", "h3", "h4", "section", "article"}
REDACT = [
    (re.compile(r"sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}"
                r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"), "[redacted key]"),
    (re.compile(r"(?i)\b((?:wi-?fi |email |gmail |account )?(?:password|passwd|pwd|passcode|otp|pin|cvv)"
                r"(?: is|:|=| -)\s*)[^\s,.;!?]{3,}"), r"\1[redacted secret]"),
    (re.compile(r"(?<![\w/=?&.])(?:\+\d{1,3}[\s-]?\d[\d\s-]{6,12}\d|\d{10})(?![\w/&])"), "[redacted phone]"),
    (re.compile(r"(?<!\d)\d{4}[ -]\d{4}[ -]\d{4}[ -]\d{4}(?!\d)"), "[redacted card]"),
]


def redact(text):
    """Mask keys, passwords, phone and card numbers. Returns (text, how many were masked)."""
    n = 0
    for pattern, repl in REDACT:
        text, k = pattern.subn(repl, text)
        n += k
    return text, n


DATE_LINE = re.compile(r"^[A-Z][a-z]{2} \d{1,2}, \d{4},? \d{1,2}:\d{2}(?::\d{2})? ?[APap][Mm]$")


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        elif tag in BLOCK:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.out.append(data.strip() + " ")


def html_to_text(raw):
    p = _Text()
    p.feed(raw)
    lines = [l.strip() for l in "".join(p.out).split("\n")]
    return "\n".join(l for l in lines if l)


def compact_thread(text):
    """Instagram/Facebook HTML thread: blocks of 'sender / message / date' -> 'date sender: message', oldest first."""
    lines = text.split("\n")
    head, body = lines[:4], lines[4:]
    msgs, cur = [], []
    for l in body:
        if DATE_LINE.match(l):
            if cur:
                sender, rest = cur[0], " / ".join(cur[1:])
                if rest and not re.search(r"(liked a message|reacted .+ to your message)$", rest):
                    msgs.append(f"{l} | {sender}: {rest}")
            cur = []
        else:
            cur.append(l)
    if not msgs:
        return text
    return "\n".join(head + list(reversed(msgs)))


def _fix(s):
    # Meta JSON exports store UTF-8 bytes as latin-1 escapes
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def meta_json_thread(d):
    from datetime import datetime
    title = _fix(d.get("title", "thread"))
    who = ", ".join(_fix(p.get("name", "")) for p in d.get("participants", []))
    rows = []
    for m in sorted(d.get("messages", []), key=lambda m: m.get("timestamp_ms", 0)):
        ts = datetime.fromtimestamp(m.get("timestamp_ms", 0) / 1000).strftime("%Y-%m-%d %H:%M")
        content = _fix(m.get("content", "")) or ("[attachment]" if any(k in m for k in ("photos", "videos", "audio_files", "share")) else "")
        if content:
            rows.append(f"{ts} | {_fix(m.get('sender_name', '?'))}: {content}")
    return f"# {title}\nParticipants: {who}\n" + "\n".join(rows)


def chatgpt(convs):
    out = {}
    for c in convs:
        msgs = []
        for node in (c.get("mapping") or {}).values():
            m = node.get("message") or {}
            parts = (m.get("content") or {}).get("parts") or []
            txt = "\n".join(p for p in parts if isinstance(p, str)).strip()
            role = (m.get("author") or {}).get("role")
            if txt and role in ("user", "assistant"):
                msgs.append((m.get("create_time") or 0, role, txt))
        msgs.sort()
        out[c.get("title") or "untitled"] = "\n\n".join(f"**{r}:** {t}" for _, r, t in msgs)
    return out


def claude(convs):
    out = {}
    for c in convs:
        msgs = [(m.get("sender"), m.get("text", "")) for m in c.get("chat_messages", [])]
        out[c.get("name") or "untitled"] = "\n\n".join(f"**{s}:** {t}" for s, t in msgs if t)
    return out


def flatten(d, prefix=""):
    lines = []
    if isinstance(d, dict):
        for k, v in d.items():
            lines += flatten(v, f"{prefix}{k}.")
    elif isinstance(d, list):
        for i, v in enumerate(d):
            lines += flatten(v, f"{prefix}{i}.")
    elif d not in (None, "", [], {}):
        lines.append(f"{prefix.rstrip('.')}: {_fix(d) if isinstance(d, str) else d}")
    return lines


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "untitled"


def convert(src, dst):
    """Convert everything under src into text files under dst. Returns the manifest text."""
    os.makedirs(dst, exist_ok=True)
    stats = {"converted": 0, "copied": 0, "skipped_media": 0, "skipped_other": 0, "bytes": 0, "redacted": 0}
    written = []

    def write(rel, text, clean=True):
        if clean:
            text, n = redact(text)
            stats["redacted"] += n
        path = os.path.join(dst, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text.rstrip() + "\n")
        stats["bytes"] += len(text.encode())
        written.append((rel, len(text.encode())))

    for root, _, files in os.walk(src):
        for name in sorted(files):
            path = os.path.join(root, name)
            rel = os.path.relpath(path, src)
            ext = os.path.splitext(name)[1].lower()
            if ext in MEDIA:
                stats["skipped_media"] += 1
                continue
            try:
                with open(path, encoding="utf-8", errors="ignore") as f:
                    raw = f.read()
            except OSError:
                stats["skipped_other"] += 1
                continue
            base = os.path.splitext(rel)[0]
            if ext in (".html", ".htm"):
                text = html_to_text(raw)
                if re.match(r"message_\d+$", os.path.splitext(name)[0]):
                    text = compact_thread(text)
                write(base + ".txt", text)
                stats["converted"] += 1
            elif ext == ".json":
                try:
                    d = json.loads(raw)
                except json.JSONDecodeError:
                    stats["skipped_other"] += 1
                    continue
                if isinstance(d, dict) and "messages" in d and "participants" in d:
                    write(base + ".txt", meta_json_thread(d))
                elif isinstance(d, list) and d and isinstance(d[0], dict) and "mapping" in d[0]:
                    for title, text in chatgpt(d).items():
                        write(os.path.join(base, slug(title) + ".md"), f"# {title}\n\n{text}")
                elif isinstance(d, list) and d and isinstance(d[0], dict) and "chat_messages" in d[0]:
                    for title, text in claude(d).items():
                        write(os.path.join(base, slug(title) + ".md"), f"# {title}\n\n{text}")
                else:
                    write(base + ".txt", "\n".join(flatten(d)))
                stats["converted"] += 1
            elif ext in (".txt", ".md", ".csv"):
                write(rel, raw)
                stats["copied"] += 1
            else:
                stats["skipped_other"] += 1

    written.sort(key=lambda x: -x[1])
    manifest = [
        "# Import manifest",
        "",
        f"Source: `{src}`",
        f"Text files: {len(written)} ({stats['converted']} converted, {stats['copied']} copied), "
        f"{stats['bytes'] / 1024:.0f} KB of text",
        f"Skipped: {stats['skipped_media']} media files, {stats['skipped_other']} other files",
        f"Masked: {stats['redacted']} secrets, phone or card numbers (shown as [redacted ...])",
        "",
        "## Largest files (read these with the most care)",
    ] + [f"- {r} ({b / 1024:.0f} KB)" for r, b in written[:40]]
    write("_manifest.md", "\n".join(manifest), clean=False)
    return "\n".join(manifest)


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 1
    src, dst = argv[1], argv[2]
    if src.lower().endswith(".zip"):
        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(src) as z:
                z.extractall(tmp)
            print(convert(tmp, dst))
    else:
        print(convert(src, dst))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
