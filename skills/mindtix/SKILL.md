---
name: mindtix
description: A second brain that gets to know you and helps you actually learn, kept as a folder of plain markdown. Sets up a brain, imports exports (Instagram, WhatsApp, ChatGPT, Claude, Takeout, Obsidian), files notes, teaches topics by making the user produce, runs spaced-repetition recall, writes an evidence-based read of the user, and exports a profile, Anki deck, backup or local web app. Use when the user says "mindtix", "set up mindtix", "my brain", "second brain", "save this", "import my export", "teach me X", "quiz me", "what's due", "today", "reflect on me", "weekly review", "tidy the brain", "export my brain", or "forget someone", or works in a folder that has MIND.md.
argument-hint: "[workflow] [arguments]"
---

# mindtix

Asked for: $ARGUMENTS

This skill holds thirteen workflows, each in `workflows/<name>.md` in this skill's folder.
If the first word asked for is a workflow name, run that workflow on the rest; otherwise pick
the one that fits. Read that file in full and follow it.

| Workflow | Use when the user wants to… |
|---|---|
| `init` | create a new brain ("set up mindtix"), with a first short interview |
| `import` | import an export or a folder/.zip, and file what it says about them |
| `capture` | save anything they say or paste; `notes` files new files in `raw/` |
| `learn` | learn a topic: start, teach, quiz, diagnose repeated mistakes, spar |
| `recall` | review the recall cards that are due |
| `today` | do the daily 5-10 minutes: due cards, one learning step, one old question |
| `know-me` | be interviewed so `self/` fills in |
| `reflect` | get the AI's read of them (`insight/`), or take a personality test |
| `connect-dots` | find how everything they know connects |
| `review` | do the weekly review |
| `tidy` | health-check the brain: links, index, secrets, overdue cards |
| `export` | export a profile, Anki deck, JSON, zip backup, or the local web app |
| `forget` | remove a person or topic from the whole brain |

No match but they're in a brain (a folder with `MIND.md`)? Answer from the notes, following
`MIND.md`. Not in a brain yet? Offer `init`.

## Reading a workflow

- `/mindtix <name> <args>` means the `<name>` workflow, run with those arguments.
- `$ARGUMENTS` means what the user asked for; in a workflow, minus the workflow name.
- `<this skill's dir>` means this skill's folder, which holds `to_text.py`, `export.py`,
  `template/` and `site/`.
- Without the Claude Code plugin, its hooks (secret guard, `raw/` guard, due-card count,
  auto-commit) aren't installed, so keep those rules yourself: never write secrets into
  notes, never edit files in `raw/`, and commit after changes when the brain is a git repo.
