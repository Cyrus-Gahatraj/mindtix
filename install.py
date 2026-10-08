#!/usr/bin/env python3
"""Install the mindtix skills for AI agents other than Claude Code.

Claude Code users install the plugin instead (/plugin install mindtix@mindtix).

    python3 install.py                     # ~/.agents/skills (Codex, opencode, Gemini CLI)
    python3 install.py --project ~/mind    # <brain>/.agents/skills (also Cursor and Copilot)
    python3 install.py --to ~/.config/opencode/skills   # any other skills folder
    python3 install.py --uninstall [same target options]

Each skill is installed as `mindtix-<name>` (e.g. mindtix-learn) so it never clashes with
other skills, and references like `/mindtix:capture` become "the `mindtix-capture` skill".
Standard library only; run it from a clone of the repo:

    git clone https://github.com/Cyrus-Gahatraj/mindtix && python3 mindtix/install.py
"""
import argparse
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.join(HERE, "skills")
PREFIX = "mindtix-"
# Frontmatter keys only Claude Code understands; other agents ignore or reject them
CLAUDE_ONLY_KEYS = ("argument-hint", "user-invocable", "disable-model-invocation", "allowed-tools", "model")


def portable(text, skill_dir=None):
    """Rewrite a Claude Code SKILL.md for other agents."""
    head, sep, body = text.partition("\n---\n")
    if text.startswith("---\n") and sep:
        lines = [l for l in head.splitlines() if not l.split(":")[0].strip() in CLAUDE_ONLY_KEYS]
        lines = [re.sub(r"^name:\s*(\S+)", lambda m: f"name: {PREFIX}{m.group(1)}", l) for l in lines]
        head = "\n".join(lines)
        text = head + sep + body
    # /mindtix:learn quiz -> the `mindtix-learn` skill (quiz)
    text = re.sub(r"`/mindtix:([a-z-]+) ([^`]+)`", r"the `mindtix-\1` skill (\2)", text)
    text = re.sub(r"`?/mindtix:([a-z-]+)`?", r"the `mindtix-\1` skill", text)
    text = text.replace("$ARGUMENTS", "what the user asked for")
    if skill_dir:  # other agents may not know where the skill lives
        text = text.replace("<this skill's dir>", skill_dir.replace(os.sep, "/"))
    return text


def install(dest, uninstall=False):
    os.makedirs(dest, exist_ok=True)
    names = sorted(n for n in os.listdir(SKILLS) if os.path.isfile(os.path.join(SKILLS, n, "SKILL.md")))
    for name in names:
        target = os.path.join(dest, PREFIX + name)
        if os.path.islink(target) or os.path.isfile(target):
            os.remove(target)
        elif os.path.isdir(target):
            shutil.rmtree(target)
        if uninstall:
            continue
        shutil.copytree(os.path.join(SKILLS, name), target,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for root, _, files in os.walk(target):  # SKILL.md and the template it ships
            for f in files:
                if f.endswith(".md"):
                    path = os.path.join(root, f)
                    with open(path, encoding="utf-8") as fh:
                        text = fh.read()
                    with open(path, "w", encoding="utf-8") as fh:
                        fh.write(portable(text, os.path.abspath(target)))
    return names


def main(argv=None):
    p = argparse.ArgumentParser(description="Install mindtix skills for Codex, opencode, Gemini CLI, Cursor and other agents.")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--project", metavar="BRAIN", help="install into <BRAIN>/.agents/skills (works for every agent opened in that folder)")
    g.add_argument("--to", metavar="DIR", help="install into this skills folder")
    p.add_argument("--uninstall", action="store_true", help="remove the mindtix skills from the target")
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
        names = install(d, a.uninstall)
        verb = "Removed" if a.uninstall else "Installed"
        print(f"{verb} {len(names)} skills {'from' if a.uninstall else 'in'} {d}: "
              + ", ".join(PREFIX + n for n in names))
    if not a.uninstall:
        print("\nNext: open your agent in an empty folder and say \"set up mindtix\" "
              "(the mindtix-init skill). Requires python3 for import, export and init.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
