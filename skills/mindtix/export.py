#!/usr/bin/env python3
"""Export a mindtix brain.

    python3 export.py anki   <brain> <out.txt>   recall cards as an Anki import file
    python3 export.py json   <brain> <out.json>  every note as JSON (path, title, links, text) + cards
    python3 export.py bundle <brain> <out.zip>   a zip backup of the brain
    python3 export.py site   <brain> [folder path] [brain folder ...] [--replace] [--no-install]
                                                 set up the brain's website (the Astro app next to
                                                 this script) in <brain>/exports/site/, or the
                                                 folder given, and npm install it

The exports leave out private/, logs/, raw/imports/, .git/ and the template examples, and the
input brain is never changed (site writes only exports/ and its own folder). Standard library only.
"""
import json
import os
import shutil
import subprocess
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
        lines = open(os.path.join(brain, "knowledge", topic + ".md"), encoding="utf-8", errors="replace").read().splitlines()
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


SITE_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")
SITE_SKIP = ("node_modules", "dist", ".astro", "mindtix.json")


def node_ok():
    """Node 22.12 or newer, which Astro needs."""
    try:
        v = subprocess.run(["node", "--version"], capture_output=True, text=True, shell=os.name == "nt").stdout.strip().lstrip("v")
        return tuple(int(x) for x in v.split(".")[:2]) >= (22, 12)
    except (OSError, ValueError):
        return False


def setup_site(brain, dest=None, folders=None, replace=False, install=True):
    """Copy the site into dest (default: the folder remembered in exports/site.json, else
    <brain>/exports/site/), point it at the brain and npm install it. Returns (dest, what happened).
    A copy that's already there is theirs and is kept, unless replace=True (their mindtix.json stays)."""
    brain = os.path.abspath(brain)
    remembered = os.path.join(brain, "exports", "site.json")
    if not dest:
        try:
            dest = json.load(open(remembered, encoding="utf-8"))["path"]
        except (OSError, ValueError, KeyError):
            dest = ""
        if not os.path.isfile(os.path.join(dest, "package.json")):
            dest = os.path.join(brain, "exports", "site")
    dest = os.path.abspath(os.path.expanduser(dest))
    inside = os.path.commonpath([brain, dest]) == brain
    if inside and os.path.commonpath([os.path.join(brain, "exports"), dest]) != os.path.join(brain, "exports"):
        raise ValueError("Inside the brain, the site goes in exports/ only (the auto-commit hook would commit it anywhere else).")
    if os.path.exists(dest) and not os.path.isdir(dest):
        raise ValueError(f"{dest} is a file. Pick a folder.")
    ours = os.path.isfile(os.path.join(dest, "package.json"))
    if os.path.isdir(dest) and os.listdir(dest) and not ours:
        if dest != os.path.join(brain, "exports", "site"):
            raise ValueError(f"{dest} has other files in it. Pick an empty or new folder.")
        shutil.rmtree(dest)  # an old one-file export
    if ours and replace:
        for name in os.listdir(dest):
            if name not in ("node_modules", "mindtix.json"):
                p = os.path.join(dest, name)
                shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    what = "kept your copy" if ours and not replace else "replaced with this version" if ours else "copied"
    if what != "kept your copy":
        shutil.copytree(SITE_SRC, dest, ignore=shutil.ignore_patterns(*SITE_SKIP), dirs_exist_ok=True)
    conf_path = os.path.join(dest, "mindtix.json")
    try:
        conf = json.load(open(conf_path, encoding="utf-8"))
    except (OSError, ValueError):
        conf = {}
    conf["brain"] = brain
    if folders:
        conf["folders"] = " ".join(folders)
    conf.setdefault("folders", "all")
    with open(conf_path, "w", encoding="utf-8") as f:
        json.dump(conf, f, indent=2)
        f.write("\n")
    os.makedirs(os.path.dirname(remembered), exist_ok=True)
    with open(remembered, "w", encoding="utf-8") as f:
        json.dump({"path": dest}, f, indent=2)
    if install and (what != "kept your copy" or not os.path.isdir(os.path.join(dest, "node_modules"))):
        if not node_ok():
            return dest, what + "; needs Node 22.12 or newer for npm install (https://nodejs.org)"
        r = subprocess.run(["npm", "install", "--no-audit", "--no-fund"], cwd=dest, capture_output=True, text=True, shell=os.name == "nt")
        if r.returncode:
            return dest, what + "; npm install failed: " + (r.stderr.strip().splitlines() or ["?"])[-1]
        what += ", installed"
    return dest, what


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to cp1252
    if len(argv) >= 3 and argv[1] == "site":
        if not os.path.isfile(os.path.join(argv[2], "MIND.md")):
            print(f"{argv[2]} is not a mindtix brain (no MIND.md)")
            return 1
        rest = [a for a in argv[3:] if not a.startswith("--")]
        paths = [a for a in rest if "/" in a or "\\" in a or a.startswith((".", "~"))]
        try:
            dest, what = setup_site(argv[2], paths[0] if paths else None, [a for a in rest if a not in paths],
                                    "--replace" in argv, "--no-install" not in argv)
        except ValueError as e:
            print(e)
            return 1
        print(f"site -> {dest} ({what})\nstart it: cd \"{dest}\" && npm run dev   (http://127.0.0.1:4321)")
        return 0
    if len(argv) != 4 or argv[1] not in ("anki", "json", "bundle"):
        print(__doc__)
        return 1
    kind, brain, out = argv[1:4]
    if not os.path.isfile(os.path.join(brain, "MIND.md")):
        print(f"{brain} is not a mindtix brain (no MIND.md)")
        return 1
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    n = {"anki": export_anki, "json": export_json, "bundle": export_bundle}[kind](brain, out)
    unit = {"anki": "cards", "json": "notes", "bundle": "files"}[kind]
    print(f"{n} {unit} -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
