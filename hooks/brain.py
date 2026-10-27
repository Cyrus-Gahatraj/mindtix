"""Shared helpers for mindtix hooks: find the brain root and parse recall cards."""
import os
import re
from datetime import date

CARD = re.compile(r"^\s*-\s*\[b([0-5])\s*·\s*due\s+(\d{4}-\d{2}-\d{2})\]", re.M)
DEFAULT_BRAIN = os.path.expanduser("~/.config/mindtix/brain")
CONFIG_FILE = os.path.expanduser("~/.config/mindtix/brain_path")


def is_brain_dir(d):
    """Return True if folder contains MINDTIX.md or legacy MIND.md."""
    return os.path.isfile(os.path.join(d, "MINDTIX.md")) or os.path.isfile(os.path.join(d, "MIND.md"))


def mind_file(d):
    """Return the absolute path to MINDTIX.md or fallback MIND.md."""
    tix = os.path.join(d, "MINDTIX.md")
    return tix if os.path.isfile(tix) else os.path.join(d, "MIND.md")


def save_brain(path):
    """Save the path to the primary brain in user config for global discovery."""
    path = os.path.abspath(os.path.expanduser(path))
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(path + "\n")


def find_root(path, allow_global=False):
    """Return the nearest folder at or above path holding MINDTIX.md/MIND.md, or the global brain."""
    p = os.path.abspath(path)
    if not os.path.isdir(p):
        p = os.path.dirname(p)
    curr = p
    while True:
        if is_brain_dir(curr):
            return curr
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent

    if not allow_global:
        return None

    # Global brain discovery fallbacks
    env_brain = os.environ.get("MINDTIX_BRAIN")
    if env_brain:
        env_brain = os.path.abspath(os.path.expanduser(env_brain))
        if is_brain_dir(env_brain):
            return env_brain

    # Dedicated ~/.config/mindtix/brain folder
    if os.path.isdir(DEFAULT_BRAIN) and is_brain_dir(DEFAULT_BRAIN):
        return DEFAULT_BRAIN

    # Explicit pointer file
    for cfile in [CONFIG_FILE, DEFAULT_BRAIN]:
        if os.path.isfile(cfile):
            try:
                with open(cfile, encoding="utf-8") as f:
                    saved = f.read().strip()
                if saved and is_brain_dir(saved):
                    return os.path.abspath(os.path.expanduser(saved))
            except OSError:
                pass

    # Standard home paths
    for candidate in [os.path.expanduser("~/.mindtix"), os.path.expanduser("~/brain"), os.path.expanduser("~/mind")]:
        if os.path.isdir(candidate) and is_brain_dir(candidate):
            return candidate

    return None


def find_brain(cwd=None):
    """Find the active brain root: local ancestor of cwd, or global configuration."""
    return find_root(cwd or os.getcwd(), allow_global=True)


def detect_project_context(cwd, brain_root):
    """If cwd is outside brain_root, return the project name to link against."""
    if not brain_root:
        return None
    cwd = os.path.abspath(cwd)
    brain_root = os.path.abspath(brain_root)
    try:
        common = os.path.commonpath([cwd, brain_root])
        if common == brain_root:
            return None  # Inside the brain
    except ValueError:
        pass  # Different drive letters on Windows

    # Outside the brain: find git root or fallback to folder basename
    curr = cwd
    while True:
        if os.path.isdir(os.path.join(curr, ".git")):
            return os.path.basename(curr)
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent
    return os.path.basename(cwd)


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
