---
name: capture
description: Put things into a mindtix brain. Two jobs. (1) Turn anything the user says or pastes (an idea, a link, code, a lecture, a poem line, a fact about themselves) into a clean, linked note in the right folder. (2) Process their raw notes and imports in raw/ into topic pages in knowledge/ and facts in self/, projects/ and hobbies/. Use when the user says "capture", "save this", "note this", "remember this", "process my notes", "elaborate", "import this", pastes something to keep, or after files are added to raw/.
argument-hint: "[text to save | notes]"
---

# Capture

Input: $ARGUMENTS. Empty or "notes" means job B; anything else is job A.

Work from the brain root (the folder with `MIND.md`). If there is none, suggest
`/mindtix:init` and stop.

Pick the job:
- **They said or pasted something** → job A
- **They asked to process notes or imports, or `raw/` has new files** → job B

Rules for both:
- **Strip secrets first.** Passwords, keys, tokens, card or ID numbers: leave them out and say so.
- **Find before you create.** Read `INDEX.md`, then search (`grep -ril "<terms>"
  --exclude-dir=raw --exclude-dir=private .`). Merge into an existing note when one fits.
- **`raw/` is read-only.** Never edit or delete anything in it, except saving new input in
  job A as described below.
- **Never write `insight/`** (only `/mindtix:reflect`). If something shows how they think or
  what they know, say so and suggest it.
- Label every fact about the user `[stated]` (they said it) or `[inferred]` (your guess).
- New folder only when it will hold more than one note. No empty folders.
- Update `INDEX.md` for every note you create, move or delete.

## A. Something they said or pasted

1. **Pick a home:**

   | Input | Goes to |
   |---|---|
   | Something they're learning (concept, command, lecture) | `knowledge/<topic>.md`, page shape below |
   | Their creative writing (poem, story, draft) | `raw/writing/`, **verbatim**, never polished |
   | A fact about them (background, taste, goal, people, feelings) | `self/` (`profile.md`, `personality.md`, `people.md`, `timeline.md`) |
   | News about something they make | `projects/<project>.md` |
   | A hobby | `hobbies/<hobby>/` |
   | Anything else (school, work, health, travel) | `extra/<area>/` |
   | A long source (article, transcript) | `raw/imports/`, then run job B on it |
   | A data export or a whole folder of notes | Use `/mindtix:import <path>` instead |

2. **Write the note** at `kebab-case-title.md`: a `# Title`, a one-line summary, the content
   in their words with the mess removed (code in fenced blocks), `Related: [[...]]` (only
   notes that exist) and `Captured: YYYY-MM-DD`.
3. Reply in one line: the path, and whether it was new or merged.

## B. Process raw/ into the brain

1. **Find what's pending:** files in `raw/` not yet listed under `Sources:` in any note, or
   changed since the note that cites them. Skip the READMEs.
2. **Sort each file:**

   | File | Do |
   |---|---|
   | A note about a topic | Elaborate into `knowledge/` (step 3) |
   | Creative writing | Leave it; mention it to `/mindtix:reflect` for writing style |
   | About them (diary, bio, habits) | Facts into `self/`, labeled |
   | About a project or hobby | Into `projects/` or `hobbies/` |
   | A data export (chats, social media, Takeout) | Read it fully; extract who they are, people, timeline, interests and projects into `self/`, `projects/`, `hobbies/`. Leave out other people's private matters and every secret |

   List what you'll create or update, then go ahead.

   **Big imports** (more than ~50 files or ~200 KB of text): don't read them into this
   conversation. Split them into batches of similar size and launch the `reader` agent on
   each batch **in parallel** (one message, several agents), telling it who the user is.
   Then write the notes from their reports. Without sub-agents, read batch by batch and
   write notes after each batch. Read the most important threads yourself only
   if the user asks.
3. **Knowledge page shape**, grouped by topic not by file (`knowledge/binary-search.md`):

   ```markdown
   # Topic
   One-line summary.

   ## Try it
   The smallest runnable code or concrete example. Run it first.

   ## Why it works
   The theory in short chunks, tied to the example.

   ## Connections
   [[links]] to related topics, projects and learning maps.

   ## Recall
   - [b0 · due YYYY-MM-DD] A question to answer from memory (due tomorrow)

   ## Log
   - YYYY-MM-DD capture: from raw/notes/...

   Sources: raw/notes/... · Updated: YYYY-MM-DD
   ```

   Keep their ideas and examples, fill gaps, and **correct mistakes** marked
   "(corrected: you wrote X)". Anything well beyond their notes goes under `## Going further`.
   `## Log` and `## Recall` are shared with `/mindtix:learn` and `/mindtix:recall`; append,
   never rewrite.
4. **Report** in a few lines: what was created or updated, corrections made, anything
   skipped. Offer to commit as "Capture YYYY-MM-DD".
