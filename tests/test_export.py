"""Self-check for the export script: python3 tests/test_export.py"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "skills", "mindtix", "export.py")
TEMPLATE = os.path.join(HERE, "..", "skills", "mindtix", "template")


def run(*args):
    r = subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return r.stdout


with tempfile.TemporaryDirectory() as tmp:
    brain = os.path.join(tmp, "mind")
    shutil.copytree(TEMPLATE, brain)
    with open(os.path.join(brain, "knowledge", "sql-joins.md"), "w", encoding="utf-8") as f:
        f.write("# SQL joins\n\n## Recall\n- [b1 · due 2026-10-10] What does a left join keep?\n"
                "- Why use not exists?\n\n## Log\n- 2026-10-07 recall: 1/1\n\nSee [[self/profile]].\n")
    os.makedirs(os.path.join(brain, "private"))
    open(os.path.join(brain, "private", "id.md"), "w", encoding="utf-8").write("secret id")
    open(os.path.join(brain, "raw", "imports", "chat.txt"), "w", encoding="utf-8").write("someone else's message")

    mind = os.path.join(brain, "MIND.md")
    text = open(mind, encoding="utf-8").read().replace("- Name:", "- Name: Ada *Lovelace* [stated]", 1)
    open(mind, "w", encoding="utf-8").write(text)

    out = os.path.join(brain, "exports")
    assert "2 cards" in run("anki", brain, os.path.join(out, "c.txt"))
    deck = open(os.path.join(out, "c.txt"), encoding="utf-8").read()
    assert "What does a left join keep?\t" in deck and "Why use not exists?" in deck
    assert "_example" not in deck and "n-1" not in deck, "template example cards are not exported"

    run("json", brain, os.path.join(out, "b.json"))
    data = json.load(open(os.path.join(out, "b.json"), encoding="utf-8"))
    paths = {n["path"] for n in data["notes"]}
    assert "knowledge/sql-joins.md" in paths and "MIND.md" in paths
    assert not any(p.startswith(("private/", "raw/imports/", "logs/")) for p in paths)
    assert {"box": 1, "due": "2026-10-10"}.items() <= next(c for c in data["cards"] if c["box"] == 1).items()
    assert "self/profile" in next(n for n in data["notes"] if n["path"] == "knowledge/sql-joins.md")["links"]

    run("bundle", brain, os.path.join(out, "b.zip"))
    names = zipfile.ZipFile(os.path.join(out, "b.zip")).namelist()
    assert "MIND.md" in names and "knowledge/sql-joins.md" in names
    assert not any(n.startswith(("private/", "raw/imports/", "exports/", ".git/")) for n in names), names

    # site: sets up the Astro app in exports/site/ by default, remembers where, keeps the user's copy
    site = os.path.join(brain, "exports", "site")
    os.makedirs(site)
    open(os.path.join(site, "index.html"), "w").write("old one-file export")
    out_ = run("site", brain, "--no-install")
    assert "copied" in out_ and os.path.isfile(os.path.join(site, "package.json")) and not os.path.exists(os.path.join(site, "index.html")), out_
    assert not os.path.exists(os.path.join(site, "node_modules")) and not os.path.exists(os.path.join(site, "dist"))
    conf = json.load(open(os.path.join(site, "mindtix.json")))
    assert conf == {"brain": os.path.abspath(brain), "folders": "all"}, conf
    assert json.load(open(os.path.join(brain, "exports", "site.json")))["path"] == site
    open(os.path.join(site, "src", "mine.txt"), "w").write("my change")
    assert "kept your copy" in run("site", brain, "knowledge", "projects", "--no-install")
    assert os.path.isfile(os.path.join(site, "src", "mine.txt")), "a second run keeps their copy"
    assert json.load(open(os.path.join(site, "mindtix.json")))["folders"] == "knowledge projects"
    assert "replaced" in run("site", brain, "--replace", "--no-install")
    assert not os.path.exists(os.path.join(site, "src", "mine.txt")) and json.load(open(os.path.join(site, "mindtix.json")))["folders"] == "knowledge projects"
    other = os.path.join(tmp, "brain-site")
    assert "copied" in run("site", brain, other, "--no-install") and os.path.isfile(os.path.join(other, "package.json"))
    assert "brain-site" in run("site", brain, "--no-install"), "the folder is remembered"
    open(os.path.join(tmp, "afile"), "w").write("x")
    for bad in (os.path.join(brain, "knowledge", "site"), tmp, os.path.join(tmp, "afile")):
        r = subprocess.run([sys.executable, SCRIPT, "site", brain, bad, "--no-install"], capture_output=True, text=True)
        assert r.returncode == 1, (bad, r.stdout)

    r = subprocess.run([sys.executable, SCRIPT, "anki", tmp, os.path.join(tmp, "x.txt")], capture_output=True, text=True)
    assert r.returncode == 1 and "not a mindtix brain" in r.stdout

print("export ok")
