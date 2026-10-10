#!/usr/bin/env python3
"""Install the mindtix skill for AI agents other than Claude Code.

Claude Code users install the plugin instead (/plugin install mindtix@mindtix).

    python3 install.py                     # ~/.agents/skills (Codex, opencode, Gemini CLI)
    python3 install.py --project ~/mind    # <brain>/.agents/skills (also Cursor and Copilot)
    python3 install.py --to ~/.config/opencode/skills   # any other skills folder
    python3 install.py --uninstall [same target options]

It installs one skill, `mindtix`, which holds every workflow, and removes the `mindtix-<name>`
skills that versions before 1.4 installed.
Standard library only; run it from a clone of the repo:

    git clone https://github.com/Cyrus-Gahatraj/mindtix && python3 mindtix/install.py
"""
import argparse
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.join(HERE, "skills", "mindtix")
# The one-skill-per-workflow names installed before 1.4; removed on install and uninstall
OLD = ("capture", "connect-dots", "export", "forget", "import", "init", "know-me", "learn",
       "recall", "reflect", "review", "tidy", "today")
# Frontmatter keys only Claude Code understands; other agents ignore or reject them
CLAUDE_ONLY_KEYS = ("argument-hint", "user-invocable", "disable-model-invocation", "allowed-tools", "model")


def portable(text, skill_dir=None):
    """Rewrite a Claude Code skill file for other agents."""
    head, sep, body = text.partition("\n---\n")
    if text.startswith("---\n") and sep:
        head = "\n".join(l for l in head.splitlines() if l.split(":")[0].strip() not in CLAUDE_ONLY_KEYS)
        text = head + sep + body
    if skill_dir:  # other agents may not know where the skill lives
        text = text.replace("<this skill's dir>", skill_dir.replace(os.sep, "/"))
    return text


def install(dest, uninstall=False):
    os.makedirs(dest, exist_ok=True)
    for name in ("mindtix",) + tuple("mindtix-" + n for n in OLD):
        target = os.path.join(dest, name)
        if os.path.islink(target) or os.path.isfile(target):
            os.remove(target)
        elif os.path.isdir(target):
            shutil.rmtree(target)
    if uninstall:
        return
    target = os.path.join(dest, "mindtix")
    shutil.copytree(SKILL, target, ignore=shutil.ignore_patterns(
        "__pycache__", "*.pyc", "node_modules", "dist", ".astro", "mindtix.json"))
    for root, _, files in os.walk(target):  # SKILL.md, the workflows and the template
        for f in files:
            if f.endswith(".md"):
                path = os.path.join(root, f)
                with open(path, encoding="utf-8") as fh:
                    text = fh.read()
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(portable(text, os.path.abspath(target)))


def main(argv=None):
    p = argparse.ArgumentParser(description="Install the mindtix skill for Codex, opencode, Gemini CLI, Cursor and other agents.")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--project", metavar="BRAIN", help="install into <BRAIN>/.agents/skills (works for every agent opened in that folder)")
    g.add_argument("--to", metavar="DIR", help="install into this skills folder")
    p.add_argument("--uninstall", action="store_true", help="remove the mindtix skill from the target")
    a = p.parse_args(argv)

    if a.project:
        dests = [os.path.join(os.path.expanduser(a.project), ".agents", "skills")]
    elif a.to:
        dests = [os.path.expanduser(a.to)]
    else:
        home = os.path.expanduser("~")
        dests = [os.path.join(home, ".agents", "skills")]
        if os.path.isdir(os.path.join(home, ".gemini")):
            dests.append(os.path.join(home, ".gemini", "skills"))
    for d in dests:
        install(d, a.uninstall)
        print(f"{'Removed the mindtix skill from' if a.uninstall else 'Installed the mindtix skill in'} {d}")
    if not a.uninstall:
        print("\nNext: open your agent in an empty folder and say \"set up mindtix\" "
              "(the mindtix skill's init workflow). Requires python3 for import, export and init.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
