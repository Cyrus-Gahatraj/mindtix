#!/usr/bin/env python3
"""Export a mindtix brain.

    python3 export.py anki   <brain> <out.txt>   recall cards as an Anki import file
    python3 export.py json   <brain> <out.json>  every note as JSON (path, title, links, text) + cards
    python3 export.py bundle <brain> <out.zip>   a zip backup of the brain
    python3 export.py site   <brain> <out.html> [folder ...|all]
                                                 a one-file website of the notes; default
                                                 knowledge and projects, "all" for every folder
                                                 (serve.py runs the same site live, with Ask)

All leave out private/, logs/, raw/imports/, .git/ and the template examples, and the
input brain is never changed. Standard library only.
"""
import base64
import json
import os
import posixpath
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


SITE_DEFAULT = ("knowledge", "projects")
SITE_HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site.html")
OBS_LINK = re.compile(r"(!?)\[\[([^\]]+)\]\]")
CALLOUT = re.compile(r"(?m)^(\s*>\s*)\[!(\w+)\][+-]?[ \t]*(.*)$")
IMAGES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif",
          ".webp": "image/webp", ".svg": "image/svg+xml"}
MD_NOISE = re.compile(r"(?m)^\s*(#{1,6}\s+|>\s?|[-*+]\s+|\d+\.\s+|\|)|[*_`]|!?\[\[([^\]|#]+)[^\]]*\]\]"
                      r"|\[([^\]]*)\]\([^)]*\)|\[(stated|inferred)[^\]]*\]")


def strip_frontmatter(s):
    if s.startswith("---\n"):
        end = s.find("\n---\n", 4)
        if end != -1:
            return s[end + 5:]
    return s


def plain(s):
    """Markdown down to readable text, for excerpts and search."""
    s = MD_NOISE.sub(lambda m: m.group(2) or m.group(3) or " ", s)
    return " ".join(s.replace("|", " ").replace("---", " ").split())


def describe(note_id, src):
    """A note's title (first "# " heading), a one-line excerpt and its plain text."""
    title = next((plain(l[2:]) for l in src.splitlines() if l.startswith("# ")), posixpath.basename(note_id))
    excerpt = ""
    for para in src.split("\n\n"):
        p = para.strip()
        if p and not p.startswith(("#", "|", "```")):
            excerpt = plain(p)
            break
    if len(excerpt) > 150:
        excerpt = excerpt[:150].strip() + "…"
    return title, excerpt, plain(src)


def data_uri(path):
    with open(path, "rb") as f:
        return f"data:{IMAGES[os.path.splitext(path)[1].lower()]};base64,{base64.b64encode(f.read()).decode()}"


def knowledge_levels(brain):
    """The 0-5 levels from the | Topic | Level | table in insight/knowledge.md, highest first."""
    try:
        lines = open(os.path.join(brain, "insight", "knowledge.md"), encoding="utf-8", errors="ignore").read().splitlines()
    except OSError:
        return []
    out = []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        digits = re.findall(r"\d", cells[1]) if len(cells) > 1 and cells[0] != "Topic" else []
        if digits:
            lvl = sum(map(int, digits)) / len(digits)
            out.append({"label": cells[0].replace("`", "").replace("*", ""), "value": lvl, "max": 5, "text": f"{lvl:g}"})
    return sorted(out, key=lambda b: -b["value"])


def about(brain):
    """The "## About ..." section of MIND.md: its "- Key: value" lines, or else its first paragraph
    as "Intro" (and a short name before the first comma as "Name")."""
    try:
        text = open(os.path.join(brain, "MIND.md"), encoding="utf-8", errors="ignore").read()
    except OSError:
        return {}
    m = re.search(r"(?m)^## About[^\n]*\n(.*?)(?=^## |\Z)", text, re.S)
    section = m.group(1) if m else ""
    pairs = (l[2:].split(":", 1) for l in section.splitlines() if l.startswith("- ") and ":" in l and "`" not in l[:4])
    out = {k.strip(): plain(v) for k, v in pairs if v.strip() and not v.strip().startswith("<!--")}
    if not out:
        paras = [p.strip() for p in section.split("\n\n") if p.strip() and not p.lstrip().startswith(("-", "<!--", "Labels:"))]
        if paras:
            intro = " ".join(paras[0].split())
            out["Intro"] = intro.rsplit(". ", 1)[0] + "." if intro.endswith(":") and ". " in intro else intro
            name = out["Intro"].split(",")[0]
            if len(name.split()) <= 4 and name.istitle():
                out["Name"] = name
    return out


def build_site(brain, folders=SITE_DEFAULT, live=False):
    """The site as one HTML string, and its note count. live=True turns on the Ask page (serve.py)."""
    every = folders == "all"
    shown = lambda rel: "/" in rel and (every or rel.split("/")[0] in folders)
    files = [(rel, path) for rel, path in walk(brain) if shown(rel)]
    pages = sorted(((rel, path) for rel, path in files if rel.endswith(".md")
                    and posixpath.basename(rel) not in ("README.md", "CLAUDE.md", "AGENTS.md", "GEMINI.md")),
                   key=lambda f: (f[0].split("/")[0], f[0].count("/"), f[0]))  # an overview before its details
    ids = [rel[:-3] for rel, _ in pages]
    by_base = {}
    for i in ids:
        by_base.setdefault(posixpath.basename(i).lower(), i)
    images = {posixpath.basename(rel).lower(): path for rel, path in files if os.path.splitext(rel)[1].lower() in IMAGES}

    def resolve(target):
        t = target.strip()
        t = t[:-3] if t.endswith(".md") else t
        return t if t in ids else by_base.get(posixpath.basename(t).lower())

    def to_md(src, links):
        """Obsidian links, embeds and callouts as plain markdown; notes left out become plain text."""
        def link(m):
            target, _, alias = m.group(2).partition("|")
            target, alias = target.split("#")[0].strip(), alias.strip()
            if m.group(1) and os.path.splitext(target)[1].lower() in IMAGES:
                img = images.get(posixpath.basename(target).lower())
                return f"![{alias}]({data_uri(img)})" if img else f"*(missing image: {target})*"
            note = resolve(target)
            if note:
                links.add(note)
                return f"[{alias or target}](<#/n/{note}>)"
            return alias or target
        src = OBS_LINK.sub(link, src)
        return CALLOUT.sub(lambda m: f"{m.group(1)}**{m.group(2).capitalize()}{': ' + m.group(3).strip() if m.group(3).strip() else ''}**", src)

    notes, edges = [], []
    for (rel, path), note_id in zip(pages, ids):
        src = strip_frontmatter(open(path, encoding="utf-8", errors="ignore").read())
        title, excerpt, text = describe(note_id, src)
        links = set()
        notes.append({"id": note_id, "folder": rel.split("/")[0], "title": title, "excerpt": excerpt,
                      "text": text[:4000], "words": len(text.split()), "md": to_md(src, links),
                      "mod": int(os.path.getmtime(path))})
        edges += [[note_id, t] for t in sorted(links) if t != note_id]

    me = about(brain)
    data = {"name": me.get("Name", ""), "notes": notes, "links": edges, "exported": date.today().isoformat(), "live": live}
    if every or "self" in folders:
        data["about"] = {k: v for k, v in me.items() if k != "Name"}
        photo = next((os.path.join(brain, "self", f) for f in ("photo.png", "photo.jpg")
                      if os.path.isfile(os.path.join(brain, "self", f))), None)
        data["photo"] = data_uri(photo) if photo else ""
    if every or "insight" in folders:
        try:
            data["scores"] = json.load(open(os.path.join(brain, "insight", "scores.json"), encoding="utf-8"))
        except (OSError, ValueError):
            data["scores"] = {}
        data["knowledge"] = knowledge_levels(brain)
    # Inside <script>, "</script" or "<!--" in a note would break the page; \u003c is still "<" to JSON
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    return open(SITE_HTML, encoding="utf-8").read().replace("__MINDTIX_DATA__", payload), len(notes)


def export_site(brain, out, folders=SITE_DEFAULT):
    """One self-contained HTML file: home, notes with backlinks, folders, index, graph, search, insight."""
    html, n = build_site(brain, folders)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return n


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to cp1252
    if len(argv) < 4 or argv[1] not in ("anki", "json", "bundle", "site") or (len(argv) > 4 and argv[1] != "site"):
        print(__doc__)
        return 1
    kind, brain, out = argv[1:4]
    if not os.path.isfile(os.path.join(brain, "MIND.md")):
        print(f"{brain} is not a mindtix brain (no MIND.md)")
        return 1
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    if kind == "site":
        folders = "all" if argv[4:] == ["all"] else tuple(f.strip("/") for f in argv[4:]) or SITE_DEFAULT
        n = export_site(brain, out, folders)
    else:
        n = {"anki": export_anki, "json": export_json, "bundle": export_bundle}[kind](brain, out)
    unit = {"anki": "cards", "json": "notes", "bundle": "files", "site": "notes"}[kind]
    print(f"{n} {unit} -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
