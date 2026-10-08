"""SessionStart: in a mindtix brain, tell Claude how many recall cards are due."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from brain import due_cards, find_root  # noqa: E402

try:
    cwd = json.load(sys.stdin).get("cwd") or os.getcwd()
except Exception:
    cwd = os.getcwd()
root = find_root(cwd)
if root:
    n = due_cards(root)
    if n:
        print(f"mindtix: {n} recall card{'s' if n != 1 else ''} due. Mention it once and offer /mindtix:today (or /mindtix:recall for cards only).")
