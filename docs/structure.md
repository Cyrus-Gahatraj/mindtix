# Structure

A mindtix brain is a flat set of folders. Each has one job. A folder exists in the template
with only a README; the AI fills it once there is real content.

| Folder | Holds | Who writes it |
|---|---|---|
| `MIND.md` | Rules for the AI, and a short summary of who you are | You + AI |
| `INDEX.md` | One line per note. The AI reads it before searching | AI |
| `raw/notes/` | Your own notes, in any shape | You |
| `raw/imports/` | Exports (Instagram, chats, Google), transcripts, PDFs, articles | You |
| `raw/writing/` | Poems, stories, drafts, kept exactly as written | You |
| `self/` | Profile, personality, people in your life, a timeline of your life | AI, from what you say and import |
| `knowledge/` | One page per topic you understand, with recall cards | AI, from `raw/` and `learning/` |
| `learning/` | One folder per thing you're learning now, plus a mistakes ledger | AI, during sessions |
| `projects/` | One note per thing you build or make | AI + you |
| `hobbies/` | One subfolder per hobby (chess, music, ...) | AI + you |
| `extra/` | One subfolder per area that fits nowhere else (education, work, health, ...) | AI + you |
| `insight/` | The AI's guesses about you: knowledge levels, mind, habits, style | Only `/mindtix:reflect` |
| `logs/` | Conversations with your brain's AI | The app; not committed |
| `private/` | Files with ID numbers or anything you want hidden | You; not committed |

## Rules

1. **`raw/` is read-only for the AI.** It's the source of truth. Everything else can be
   rebuilt from it.
2. **Label facts about you.** `[stated]` means you said it. `[inferred]` means the AI guessed
   it. Guesses get confirmed or deleted over time.
3. **No secrets.** No passwords, keys, tokens or ID numbers in any note. If one shows up in
   an import, it stays out of the wiki.
4. **Update, don't duplicate.** Search `INDEX.md` first and merge into the existing note.
5. **Grow only when there's content.** No empty folders or placeholder notes.
6. **Only `/mindtix:reflect` writes `insight/`.** Other skills suggest running it.
7. **Link notes** with `[[wikilinks]]` so the brain works as a graph in Obsidian.

## Pages

**Knowledge page** (`knowledge/<topic>.md`):

```markdown
# Topic
## Try it        smallest runnable example or exercise
## Why it works  the theory, short
## Connections   [[links]] to related topics and projects
## Recall        cards (see below)
## Log           - YYYY-MM-DD learn|quiz|recall: score, missed: ...
Sources: [[raw/notes/...]] · Updated: YYYY-MM-DD
```

**Cards** live in `## Recall`, one per line, with a Leitner box and a due date:

```markdown
- [b0 · due 2026-10-08] What breaks if a graph search doesn't track visited nodes?
- [b2 · due 2026-10-14] Why does BFS find the shortest path in an unweighted graph?
```

A right answer moves a card up one box; a wrong one sends it to `b0` and adds a line to
`learning/mistakes.md`. Box intervals in days: b0 1, b1 3, b2 7, b3 14, b4 30, b5 90.

**Learning folder** (`learning/<topic>/`):
- `map.md`: the specific goal, your level when you started, a checklist of modules with
  prerequisites, where people usually get stuck, the best explanations found
- `sessions.md`: one entry per session: date, role, task, what you produced, score, mistakes,
  and whether you redid it without help

When a topic in `learning/` is understood, its lasting content becomes a page in
`knowledge/`. `learning/` is the process; `knowledge/` is the result.
