#!/usr/bin/env python3
"""Export a mindtix brain.

    python3 export.py anki   <brain> <out.txt>   recall cards as an Anki import file
    python3 export.py json   <brain> <out.json>  every note as JSON (path, title, links, text) + cards
    python3 export.py bundle <brain> <out.zip>   a zip backup of the brain

All three leave out private/, logs/, raw/imports/, .git/ and the template examples, and the
input brain is never changed. Standard library only.
"""
import json
import os
import re
import sys
import zipfile
from datetime import date

SKIP_DIRS = {".git", "private", "logs", "exports", ".obsidian", ".claude"}
CARD = re.compile(r"^\s*-\s*(?:\[b([0-5])\s*·\s*due\s+(\d{4}-\d{2}-\d{2})\]\s*)?(.+?)\s*$")
LINK = re.compile(r"\[\[([^\]|#]+)")


def walk(brain):
    """Yield (relative path, absolute path) for every exportable file."""
    for root, dirs, files in os.walk(brain):
        rel_root = os.path.relpath(root, brain)
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS
                         and os.path.join(rel_root, d).replace("\\", "/") not in ("raw/imports", "./raw/imports"))
        for f in sorted(files):
            if f.startswith("_example") or f == ".DS_Store":
                continue
            rel = os.path.normpath(os.path.join(rel_root, f)).replace("\\", "/")
            if rel.startswith("learning/_example/"):
                continue
            yield rel, os.path.join(root, f)


def cards(brain):
    """Every recall card in knowledge/: dicts with topic, question, box, due."""
    out = []
    for rel, path in walk(brain):
        if not (rel.startswith("knowledge/") and rel.endswith(".md")):
            continue
        in_recall = False
        for line in open(path, encoding="utf-8", errors="ignore"):
            if line.startswith("## "):
                in_recall = line.strip().lower() == "## recall"
                continue
            m = CARD.match(line) if in_recall else None
            if m and m.group(3):
                out.append({"topic": rel[len("knowledge/"):-3], "question": m.group(3),
                            "box": int(m.group(1) or 0), "due": m.group(2) or date.today().isoformat()})
    return out


def summary(brain, topic):
    """The one-line summary under a knowledge page's title, if there is one."""
    try:
        lines = open(os.path.join(brain, "knowledge", topic + ".md"), encoding="utf-8").read().splitlines()
    except OSError:
        return ""
    for l in lines[1:6]:
        if l.strip() and not l.startswith(("#", "-", "`", ">")):
            return l.strip()
    return ""


def export_anki(brain, out):
    """Tab-separated file Anki imports directly (File > Import): Front, Back, Tags."""
    rows = ["#separator:tab", "#html:false", "#tags column:3"]
    for c in cards(brain):
        s = summary(brain, c["topic"])
        back = (s + " " if s else "") + f"(Full answer: knowledge/{c['topic']}.md in your mindtix brain)"
        tag = "mindtix " + re.sub(r"[^A-Za-z0-9_/-]", "_", c["topic"])
        rows.append("\t".join(x.replace("\t", " ") for x in (c["question"], back, tag)))
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(rows) + "\n")
    return len(rows) - 3


def export_json(brain, out):
    notes = []
    for rel, path in walk(brain):
        if not rel.endswith(".md") or rel.endswith("README.md"):
            continue
        text = open(path, encoding="utf-8", errors="ignore").read()
        title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), rel)
        notes.append({"path": rel, "title": title, "links": sorted(set(LINK.findall(text))), "text": text})
    data = {"exported": date.today().isoformat(), "notes": notes, "cards": cards(brain)}
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    return len(notes)


def export_bundle(brain, out):
    n = 0
    out_abs = os.path.abspath(out)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, path in walk(brain):
            if os.path.abspath(path) == out_abs:
                continue
            z.write(path, rel)
            n += 1
    return n


def main(argv):
    if len(argv) != 4 or argv[1] not in ("anki", "json", "bundle"):
        print(__doc__)
        return 1
    kind, brain, out = argv[1:]
    if not os.path.isfile(os.path.join(brain, "MIND.md")):
        print(f"{brain} is not a mindtix brain (no MIND.md)")
        return 1
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    n = {"anki": export_anki, "json": export_json, "bundle": export_bundle}[kind](brain, out)
    unit = {"anki": "cards", "json": "notes", "bundle": "files"}[kind]
    print(f"{n} {unit} → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
