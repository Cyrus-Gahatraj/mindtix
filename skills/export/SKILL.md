---
name: export
description: Export a mindtix brain. "profile" writes a short about-me for other AIs (ChatGPT custom instructions, Claude projects, Gemini), "anki" turns recall cards into an Anki deck file, "json" dumps every note and card, "bundle" zips the whole brain as a backup. Use when the user says "export", "back up my brain", "make my profile for ChatGPT", "send my cards to Anki", or "give me my data".
argument-hint: "[profile|anki|json|bundle|all]"
---

# Export

Format: $ARGUMENTS (if empty, ask which, listing the four in one line each).

Work from the brain root (the folder with `MIND.md`). Exports go to `exports/` in the brain
(gitignored; add `exports/` to `.gitignore` if it's missing) unless the user names another
path. Never export `private/`, `logs/` or `raw/imports/`, and never put secrets in an export.

## profile: about-me for other AIs
Write `exports/profile-YYYY-MM-DD.md`, at most ~400 words, in second person to the AI
("The user is…"), from `MIND.md`, `self/`, `projects/`, `hobbies/` and the levels in
`insight/knowledge.md`:
- who they are, what they do, what they're learning now and their level in it
- how they like to learn and to be answered (from `MIND.md` "How the AI should behave")
- current projects in one line each
Use **only `[stated]` facts** by default; ask before including `[inferred]` guesses, and
never include love life, health, mood, other people's details or anything from `private/`.
Show it in the reply so they can paste it straight into custom instructions.

## anki, json, bundle: run the script
Next to this SKILL.md is `export.py`:

```sh
python3 "<this skill's dir>/export.py" anki   . exports/mindtix-cards-YYYY-MM-DD.txt
python3 "<this skill's dir>/export.py" json   . exports/mindtix-YYYY-MM-DD.json
python3 "<this skill's dir>/export.py" bundle . exports/mindtix-YYYY-MM-DD.zip
```

- **anki:** one note per recall card (front = question, back = which page holds the
  answer, tags = `mindtix` + topic). In Anki: File → Import, pick the file. Mention that the
  cards keep living in the brain; Anki is a copy.
- **json:** every note with its path, title, links and text, plus every card with box and
  due date. Useful for other apps or scripts.
- **bundle:** a zip of the brain for backup or moving machines. It leaves out `.git`; tell
  them the git history is the fuller backup (`git push` to a private repo).
- **all:** profile plus the three files.

Report in a few lines: what was written where, and the counts the script printed.
