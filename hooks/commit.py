"""Stop: in a mindtix brain that is its own git repo, commit what changed this turn.

Does nothing when: not in a brain, the brain isn't the top folder of a git repo, a merge or
rebase is in progress, nothing changed, or MINDTIX_AUTOCOMMIT=0. If a changed file looks
like it holds a secret, it doesn't commit and warns the user instead.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from brain import find_root  # noqa: E402
from guard import find_secret  # noqa: E402


def git(root, *args):
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def same(a, b):
    return os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))


def autocommit(root):
    """Commit every change in the brain. Return a warning for the user, or None."""
    top = git(root, "rev-parse", "--show-toplevel")
    if top.returncode or not same(top.stdout.strip(), root):
        return None
    gitdir = git(root, "rev-parse", "--absolute-git-dir").stdout.strip()
    if any(os.path.exists(os.path.join(gitdir, f))
           for f in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "rebase-merge", "rebase-apply")):
        return None

    # Changed and new files (not deleted), in the worktree or already staged
    out = git(root, "ls-files", "-m", "-o", "--exclude-standard", "-z").stdout
    out += git(root, "diff", "--cached", "--name-only", "--diff-filter=d", "-z").stdout
    for rel in sorted(set(filter(None, out.split("\0")))):
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8", errors="ignore") as f:
            found = find_secret(f.read())
        if found:
            return (f"mindtix: didn't auto-commit; {rel} looks like it holds a secret ({found[:6]}…). "
                    "Remove it, or set MINDTIX_AUTOCOMMIT=0 if it's a false alarm.")

    git(root, "add", "-A")
    kept = list(filter(None, git(root, "diff", "--cached", "--name-only", "--diff-filter=d", "-z").stdout.split("\0")))
    gone = list(filter(None, git(root, "diff", "--cached", "--name-only", "--diff-filter=D", "-z").stdout.split("\0")))
    if not kept and not gone:
        return None
    # Deleted files are only counted, never named: /mindtix forget may have removed a page named after someone
    msg = "mindtix: " + ", ".join(kept[:3]) + (f" (+{len(kept) - 3} more)" if len(kept) > 3 else "")
    if gone:
        msg += f"{', ' if kept else ''}deleted {len(gone)} file{'s' if len(gone) != 1 else ''}"
    git(root, "commit", "-q", "-m", msg)
    return None


if __name__ == "__main__":
    try:
        event = json.load(sys.stdin)
    except Exception:
        event = {}
    root = find_root(event.get("cwd") or os.getcwd())
    if root and os.environ.get("MINDTIX_AUTOCOMMIT") != "0":
        try:
            warning = autocommit(root)
        except Exception:
            warning = None  # never break a session on a hook bug (or no git installed)
        if warning:
            print(json.dumps({"systemMessage": warning}))
