"""Shared helpers for mindtix hooks: find the brain root and parse recall cards."""
import os
import re
from datetime import date

CARD = re.compile(r"^\s*-\s*\[b([0-5])\s*·\s*due\s+(\d{4}-\d{2}-\d{2})\]", re.M)


def find_root(path):
    """Return the nearest folder at or above path that holds MIND.md, else None."""
    p = os.path.abspath(path)
    if not os.path.isdir(p):
        p = os.path.dirname(p)
    while True:
        if os.path.isfile(os.path.join(p, "MIND.md")):
            return p
        parent = os.path.dirname(p)
        if parent == p:
            return None
        p = parent


def due_cards(root, today=None):
    """Count cards in knowledge/**/*.md that are due today or earlier."""
    today = (today or date.today()).isoformat()
    n = 0
    for d, _, files in os.walk(os.path.join(root, "knowledge")):
        for f in files:
            if f.endswith(".md") and not f.startswith("_example"):
                with open(os.path.join(d, f), encoding="utf-8", errors="ignore") as fh:
                    n += sum(1 for _, due in CARD.findall(fh.read()) if due <= today)
    return n
