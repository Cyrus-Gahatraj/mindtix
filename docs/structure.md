# Structure

A Mindtix brain is organized into 5 clear content pillars (+ 2 gitignored operational folders). Each folder has one job with zero overlap. Folders in the template exist with only a README; the AI fills them as real content arrives.

| File / Folder | Holds | Who writes it |
|---|---|---|
| `MINDTIX.md` | Rules for the AI, and a short summary of who you are | You + AI |
| `INDEX.md` | One line per note. The AI reads it before searching | AI |
| `raw/notes/` | Your own quick notes, voice dumps, and thoughts | You |
| `raw/imports/` | Exports (chats, Takeout), transcripts, PDFs, articles | You |
| `raw/writing/` | Poems, stories, essays, kept verbatim | You |
| `knowledge/` | One page per topic you understand, with recall cards; `sources/` holds literature notes | AI, from `raw/` and `learning/` |
| `learning/` | One folder per active topic (`map.md`, `sessions.md`), mistakes ledger, and review logs | AI, during sessions |
| `projects/` | One note per thing you build, make, or manage (auto-linked from project repos) | AI + you |
| `self/` | Profile, personality, people, timeline; `insight/` holds AI cognitive profile | AI, from what you say and import; `self/insight/` only by `/mindtix reflect` |
| `logs/` | Chat session records with your brain's AI | The app; not committed |
| `private/` | Files with ID numbers, passwords, or secrets | You; not committed |

## Rules

1. **`raw/` is read-only for the AI.** It is the single source of truth. Everything else can be rebuilt from it.
2. **Label facts about you.** `[stated]` means you said it. `[inferred]` means the AI guessed it. Guesses get confirmed or deleted over time.
3. **No secrets.** No passwords, keys, tokens or ID numbers in any note. If one shows up in an import, it stays out of the vault.
4. **Update, don't duplicate.** Search `INDEX.md` first and merge into the existing note.
5. **Grow only when there's content.** No empty folders or placeholder notes.
6. **Only `/mindtix reflect` writes `self/insight/`.** Other skills suggest running it.
7. **Link notes** with `[[wikilinks]]` so the brain works as a graph in Obsidian. Every new note links to at least one existing note.
8. **Answers cite their notes** (`[[note#Heading]]`). Good answers combining notes can be filed back as pages, so the brain compounds.
9. **Structure is earned.** A hub page that ties a theme together appears only once 8+ notes share it.

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

**Cards** live in `## Recall`, one per line: a box and due date, the question, a short answer after ` :: `, and the FSRS state (`s` stability in days, `d` difficulty 1-10):

```markdown
- [b0 · due 2026-10-08] What breaks if a graph search doesn't track visited nodes? :: it loops forever
- [b2 · due 2026-10-14] Why does BFS find the shortest path in an unweighted graph? :: it expands in distance order · s7.4 d5.1
```

`skills/mindtix/srs.py` grades cards (again, hard, good, easy): the next review is `s` days away, a miss adds a line to `learning/mistakes.md`, and every grade is a row in `learning/reviews.csv`.

**Learning folder** (`learning/<topic>/`):
- `map.md`: the specific goal, your level when you started, a checklist of modules with prerequisites, where people usually get stuck, and explanations found
- `sessions.md`: one entry per challenge session: date, role, task, what you produced, score, mistakes, and whether you redid it without help

**Source note** (`knowledge/sources/<slug>.md`): a `Source:` line (author, where, when read), `## Highlights` with the exact words and where they are, and `## My take` in your words. Pages that take a fact from it cite `[[sources/<slug>#Highlights]]`.

When a topic in `learning/` is understood, its lasting content becomes a page in `knowledge/`. `learning/` is the process; `knowledge/` is the result.
