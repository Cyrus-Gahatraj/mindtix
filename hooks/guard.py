"""PreToolUse guard for mindtix brains.

Blocks (exit 2, reason on stderr) when Claude tries to:
- edit or overwrite an existing file in raw/ (the user's own material; new files are fine)
- write something that looks like a secret into any note

Does nothing outside a mindtix brain (no MIND.md above the file).
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from brain import find_root  # noqa: E402

KEYS = re.compile(
    r"sk-[A-Za-z0-9_-]{20,}"                      # OpenAI/Anthropic-style keys
    r"|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}"
    r"|AKIA[0-9A-Z]{16}"                          # AWS access key
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
)
ASSIGN = re.compile(
    r"\b(?:password|passwd|api[_-]?key|secret|token)\s*[:=]\s*['\"]?([^\s'\",;)]{8,})", re.I
)
# Values that are code or placeholders, not real secrets
NOT_A_SECRET = re.compile(
    r"^(?:os\.|process\.env|getenv|environ|env\b|env\(|config\.|settings\.|self\.|req\.|request\."
    r"|\$|\{|<|%|your[_-]|my[_-]|example|placeholder|changeme|dummy|test|fake|x{4,}|\*{4,}|\.{3})",
    re.I,
)


def find_secret(text):
    """Return the first thing in text that looks like a real secret, or None."""
    m = KEYS.search(text)
    if m:
        return m.group(0)
    for m in ASSIGN.finditer(text):
        if not NOT_A_SECRET.match(m.group(1)):
            return m.group(1)
    return None


def new_text(tool, inp):
    if tool == "Write":
        return inp.get("content", "")
    if tool == "Edit":
        return inp.get("new_string", "")
    if tool == "MultiEdit":
        return "\n".join(e.get("new_string", "") for e in inp.get("edits", []))
    return ""


def check(event):
    """Return a reason to block, or None."""
    tool = event.get("tool_name", "")
    inp = event.get("tool_input", {}) or {}
    path = inp.get("file_path", "")
    if not path:
        return None
    root = find_root(path)
    if not root:
        return None
    rel = os.path.relpath(os.path.abspath(path), root)
    if rel.split(os.sep)[0] == "raw" and os.path.exists(path):
        return f"mindtix: {rel} is in raw/, which is the user's own material and read-only. Write the result to another folder instead."
    found = find_secret(new_text(tool, inp))
    if found:
        return f"mindtix: this looks like a secret ({found[:6]}…). Brains never store passwords, keys or tokens. Leave it out and tell the user."
    return None


if __name__ == "__main__":
    try:
        reason = check(json.load(sys.stdin))
    except Exception:
        sys.exit(0)  # never block on a hook bug
    if reason:
        print(reason, file=sys.stderr)
        sys.exit(2)
