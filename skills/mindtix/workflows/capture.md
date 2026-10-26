# Capture

Input: $ARGUMENTS. Empty or "notes" means job B; anything else is job A.

Find the brain root:
1. Current folder or any parent holding `MIND.md` (local brain).
2. `MINDTIX_BRAIN` environment variable.
3. User config `~/.config/mindtix/brain`.
4. Default `~/mind` (if it holds `MIND.md`).
If none found, suggest `/mindtix init` to create one.

When capturing from an external project repository (cwd outside the brain):
- Detect the active project name from the current folder (or git repo root).
- Automatically link the captured note to `[[projects/<project-name>]]`.
- If `projects/<project-name>.md` does not exist in the brain yet, create it with a one-line summary linking to the project path.

Pick the job:
- **They said or pasted something** → job A
- **They asked to process notes or imports, or `raw/` has new files** → job B

Rules for both:
- **Strip secrets first.** Passwords, keys, tokens, card or ID numbers: leave them out and say so.
- **Find before you create.** Read `INDEX.md`, then search (`grep -ril "<terms>"
  --exclude-dir=raw --exclude-dir=private .`). Merge into an existing note when one fits.
- **`raw/` is read-only.** Never edit or delete anything in it, except saving new input in
  job A as described below.
- **`notes/` belongs to `/mindtix reflect`**, which tidies it in place. Job B may file what a
  note teaches into other folders (citing it under `Sources:`), but leaves the note where it is.
- **Never write `insight/`** (only `/mindtix reflect`). If something shows how they think or
  what they know, say so and suggest it.
- Label every fact about the user `[stated]` (they said it) or `[inferred]` (your guess).
- **Link every new note** to at least one existing note, and turn plain mentions of existing
  page titles into `[[links]]`. A note nothing links to gets lost.
- **Touch every page the input touches.** After the main note, add a line and a link to each
  existing page (from `INDEX.md`) that the input adds to, corrects or contradicts. One source
  usually updates several pages; say which.
- **Tighten the summary.** Each time a page is touched, rewrite its one-line summary to be
  shorter and truer to the whole page.
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
   | A long source (article, book, talk, transcript) | `raw/imports/`, then run job B on it |
   | A quote or highlight from something they read | The source note in `knowledge/sources/` (shape in job B) |
   | A data export or a whole folder of notes | Use `/mindtix import <path>` instead |

2. **Write the note** at `kebab-case-title.md`: a `# Title`, a one-line summary, the content
   in their words with the mess removed (code in fenced blocks), `Related: [[...]]` (only
   notes that exist) and `Captured: YYYY-MM-DD`.
3. Reply in one line: the path, and whether it was new or merged.

## B. Process raw/ into the brain

1. **Find what's pending:** files in `raw/` and `notes/` not yet listed under `Sources:` in any note, or
   changed since the note that cites them. Skip the READMEs.
2. **Sort each file:**

   | File | Do |
   |---|---|
   | A note about a topic | Elaborate into `knowledge/` (step 3) |
   | An article, book, talk or video transcript | A source note (step 4), then what it teaches into `knowledge/` pages (step 3) |
   | Creative writing | Leave it; mention it to `/mindtix reflect` for writing style |
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
   - [b0 · due YYYY-MM-DD] A question to answer from memory (due tomorrow) :: short answer
   (added with `srs.py add … --via capture`, see "Writing cards" in recall.md)

   ## Log
   - YYYY-MM-DD capture: from raw/notes/...

   Sources: raw/notes/... · Updated: YYYY-MM-DD
   ```

   Keep their ideas and examples, fill gaps, and **correct mistakes** marked
   "(corrected: you wrote X)". Anything well beyond their notes goes under `## Going further`.
   Write the page, then add its cards with `python3 "<this skill's dir>/srs.py" add . <topic>
   "<question>" --answer "<answer>" --via capture`, following "Writing cards" in `recall.md` (one
   idea each, no yes/no, at most 10 per pass).
   `## Log` and `## Recall` are shared with `/mindtix learn` and `/mindtix recall`; append,
   never rewrite.
4. **Source note** for an article, book, talk or transcript (`knowledge/sources/<slug>.md`),
   so what they read keeps its exact words next to what they made of it:

   ```markdown
   # Title of the source
   Source: author · url or where it lives · read YYYY-MM-DD

   ## Highlights
   - "the exact words, verbatim" (p. 12 / 14:05 / section)

   ## My take
   What they think of it, in their words. [[links]] to the pages it fed.

   ## Log
   - YYYY-MM-DD capture
   ```

   Pages that take a fact from it cite `[[sources/<slug>#Highlights]]`. Highlights are never
   reworded; "My take" is only theirs (ask if they haven't said).
5. **Report** in a few lines: what was created or updated, corrections made, anything
   skipped. Offer to commit as "Capture YYYY-MM-DD".
