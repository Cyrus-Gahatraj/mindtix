# Changelog

## 1.7.0

- **`notes/`: what you write on the site lands here.** Write and quick capture save to
  `notes/` (listed under `## Notes` in `INDEX.md`). `/mindtix reflect` tidies it in place
  first (titles, `[[links]]`, merges, theme folders, always your words) and then reads it for
  `insight/`. `raw/` stays read-only.
- **Write several notes at once.** The Write page opens notes in tabs (`+` adds one); ⌘S saves
  every changed tab, and unsaved new tabs survive a closed browser tab.

- **Answers from your notes cite them.** Asking your brain a question reads `INDEX.md` first,
  cites every claim as `[[note#Heading]]`, says "not in your brain" before falling back on
  general knowledge, and offers to file a good answer that combines notes as a new page.
- **Capture links everything:** every new note links to at least one existing note, plain
  mentions of page titles become links, one input updates every page it touches, and each
  page's one-line summary gets tighter every time it's touched.
- **Source notes** (`knowledge/sources/<slug>.md`) for articles, books, talks and videos: the
  exact highlights with where they are, and your take. Facts taken from them cite them.
- **`today` resurfaces highlights.** Its last step alternates between an old idea and a
  highlight you haven't seen in 30 days, and adds what you think now to `## My take`.
- **`tidy` lints:** orphan notes, unlinked mentions of page titles, contradictions, stale
  time-sensitive claims, terms used in 3+ notes with no page, and leech cards.
- **`review` proposes hub pages** once 8+ notes share a theme, never before.

## 1.6.0

- **Mindtix learns how you learn.** `/mindtix reflect` writes `insight/learning.md` from what
  actually happened, not from what you say you prefer: which teaching formats lead to mastery
  and to cards you still remember days later (with the numbers, and "too early" until there are
  enough), how well your confidence matches your answers, your mix of mistakes, and a
  **Teaching plan** that `/mindtix learn` follows.
- **`learn` teaches by evidence:**
  - Every session uses one of four formats (`worked`, `build`, `socratic`, `explain`), chosen
    from the Teaching plan, with another tried about one session in four.
  - A pretest comes before each module, and hints come up a three-rung ladder.
  - Novices get faded worked examples.
  - Explain-backs are saved under `## In my words`.
  - A module is ticked only after an unaided redo and 4/5 on unseen questions, and the next
    module is one whose prerequisites are done.
  - A miss caused by a missing prerequisite reopens that module.
- **Mistakes have a type:** `slip:`, `misconception:` or `prereq <module>:` (`srs.py grade
  --cause`).
- **`srs.py add`** writes new cards (refusing yes/no questions, ones over 160 characters and
  duplicates) and records how each was made. **`srs.py stats [--days N]`** prints recall rate
  vs predicted, calibration, first-review retention by format, topics and leeches. `review`
  shows the week's.

## 1.5.0

- **FSRS scheduling.** Recall cards are scheduled with FSRS-5 (the algorithm Anki uses) instead of
  fixed Leitner boxes: each card keeps a stability and a difficulty, so easy cards drift out to
  months and hard ones stay close, for fewer reviews at the same recall. A card line can now hold
  a short answer and its memory state:
  `- [b1 · due 2026-10-13] question :: short answer · s3.2 d5.3`. The `[bN · due …]` prefix is
  unchanged (the box is now a label for stability), so old cards, the due-card hook, `tidy` and
  older site copies keep working, and old cards migrate on their next grade.
- **`srs.py`** (next to `export.py`, standard library only) grades a card: again, hard, good or
  easy, with `--sure`/`--unsure`. `recall` and `today` use it instead of editing cards by hand.
- **Confidence before the answer.** `recall` asks "sure or guessing?" before grading; a card
  missed while sure is asked again at the end of the round and logged as a misconception. Rounds
  interleave topics.
- **`learning/reviews.csv`:** every grade, with time, rating, confidence and predicted recall.
  It's the evidence the next release uses to learn how you learn.
- **Writing cards:** one idea each, no yes/no questions, 3-5 angles per concept, at most 10 new
  per pass, always a short answer (`recall.md`). `tidy` flags yes/no cards.
- **Export:** the Anki back is the card's answer when it has one; JSON cards carry `answer`,
  `s` and `d`.
- **Site:** Recall asks "I know it" or "not sure" before showing the answer, shows the card's
  answer, and schedules with the same FSRS. Run `/mindtix export site --replace` to get it; an
  older copy still grades new cards without breaking them.
- **`sort` workflow:** moves loose files (dropped in the brain root or the wrong folder) to
  where they belong, asking when it can't tell what a file is. It also brings files in from
  outside the brain (`/mindtix sort ~/Downloads/song.mp3`) and reads each one (audio key and
  tempo, image contents, PDF text) into a note, so `/mindtix reflect` can use it.

## 1.4.0

- **One skill.** Mindtix is now a single `mindtix` skill instead of thirteen: `/mindtix today`,
  `/mindtix learn sql`, or just talk. The workflows are files in `skills/mindtix/workflows/`,
  next to the scripts, the template and the site, so neither Claude Code nor skills.sh lists
  them as separate commands (and `init` and `review` no longer clash with built-ins).
- `install.py` installs that one skill and removes the old `mindtix-<name>` ones.
- The site sends `/mindtix <workflow>` to Claude Code.

## 1.3.0

- **The site, redesigned in "source mode":** it looks like a markdown file being written.
  - **Colors:** oat paper with warm ink, or night ink in dark mode; one vermilion accent,
    ink-blue links, highlighter selections, and a colour per folder (`#tags`, graph, charts).
  - **Type:** iA Writer Quattro and Mono, bundled so it works offline.
  - **Markdown markers:** hanging `#` on headings, `[[ ]]` on links between notes, `- ` bullets,
    fenced code, `> [!callout]` tiles, `<!-- notes -->`, a `---` frontmatter header on Today,
    and Claude Code's steps as a `- [x]` task list.
  - **Profile:** the avatar (top right) opens it: your picture, added there and cropped to a
    square in the browser, saved as `self/photo.jpg`; About me from MIND.md; your `self/` notes.
    The top bar says mindtix.
  - **Navigation:** a top bar (`today notes ask recall insight`, the current one in `[ ]`) that
    becomes a bottom tab bar on phones, and ⌘K for search and actions everywhere.
  - **Today:** greeting, quick capture into `raw/notes/<date>.md`, due cards, the last chat,
    learning now, recent notes and projects.
  - **Notes:** a library with filter, folder chips and sort. Note pages have Edit (E), "Ask
    about it", backlinks and outgoing links.
  - **Ask:** streams, and the Claude Code engine (default when installed) runs the `/mindtix`
    commands with a `/` menu, shows each step (Reading…, Editing…), has a Stop button that keeps
    the partial answer, and keeps one Claude Code session per chat. Chats can be deleted.
  - **Write:** `[[` autocomplete, drafts that survive a closed tab, and a warning before leaving
    unsaved work.
  - **Recall:** keyboard (Space, 1, 2), progress, and an end-of-round summary.
  - **Graph:** only on its own page, with highlight, folder filters, zoom and pan.
  - **Settings:** chat engine (Claude Code model and edits, or an API AI), folders, theme and
    keyboard shortcuts.
  - Stats moved into Insight. The old `/all`, `/stats` and `/f/<folder>` addresses redirect.
- **`export site` is one local Astro app you own, set up without questions:**
  `export.py site` copies `skills/export/site/` (never linked) into `exports/site/` in the brain,
  or a folder you name, which is remembered in `exports/site.json`. It writes `mindtix.json`
  (the brain's path and folders, so it runs from anywhere) and runs `npm install`. A copy that's
  already there is kept; `--replace` updates it. Start it with `npm run dev` on `127.0.0.1:4321`. It reads the notes on every request and has notes,
  backlinks, folders, index, graph, ⌘K search, stats and insight, plus:
  - **Ask:** the chatbot that remembers.
  - **Write:** new notes and edits; new notes get a line in `INDEX.md`; it refuses insight/,
    private/, logs/, secrets and stale edits.
  - **Recall:** due cards, Leitner boxes, `mistakes.md` and `## Log`, like `/mindtix:recall`.
  - It answers only to 127.0.0.1, and writes must be JSON.
  - **No AI set up?** The Ask page asks for one (Claude, or an OpenAI-compatible endpoint with an
    optional key and model), saves it to the brain's `.env` and keeps `.env` gitignored. Keys
    never go back to the page. Ask shows which AI it uses, with a link to change it. The export
    report says so in its last line.
  - **Removed:** the static one-file site (`site.html`, `export.py site`) and `serve.py` (live).
  - **CI:** runs the self-check (`npm test`) and an Astro build.
- **`export site` charts:** a Stats page (donut of notes by folder, words by folder, weekly
  activity, most connected and longest notes, recall cards by box, knowledge levels); home gets
  the folder donut and activity; each folder page gets its activity and longest notes. Every
  exported folder, `insight` included, is listed under Library.
- **Score methods:** every result in `insight/scores.json` says how it was got: `asked` (the
  test was taken here), `self` (the user wrote or stated it) or `inferred` (the AI's estimate).
  `reflect` sets it and labels old results; `tidy` reports any without one; the site shows it
  as a tag on each Insight chart.

## 1.2.0

- **`export site` asks which kind:** static (the one-file site), **live** (`serve.py`: the same
  site served locally and rebuilt on every load, plus an Ask page that answers from the notes,
  cites them as links and remembers: each chat is kept in `logs/`, and new chats see earlier
  questions), or custom (built to the user's description from the JSON export). Claude via the
  Messages API (`ANTHROPIC_API_KEY`) or any OpenAI-compatible endpoint (`MINDTIX_API_URL`), set
  in the brain's `.env`. Scripts run with `uv` when it's installed.
- **Template:** `.env` is gitignored.

- **`today` skill:** one daily 5-10 minute session: up to 5 due cards, one step on the
  topic being learned now, and one question from an older topic.
- **`forget` skill:** removes a person or topic from every note, card, insight line, log
  and export after one confirmation; `raw/` files are only deleted whole, on request.
  Commits without the name and explains how to clear git history.
- **Auto-commit hook:** after each reply, commits the brain's changes (when the brain is the
  top of its own git repo). Deleted files are counted, never named, in the message. Skips
  and warns if a changed file looks like it holds a secret. `MINDTIX_AUTOCOMMIT=0` turns it off.
- **`export site`:** one self-contained `index.html` of the brain: home, notes with backlinks,
  folders, index, link graph, ⌘K search and insight charts, light and dark. Only `knowledge/`
  and `projects/` by default; name more folders or pass `all`. Never `private/`, `logs/` or
  `raw/imports/`.

## 1.1.0

- **Other agents:** `install.py` installs the skills as `mindtix-<name>` for Codex, opencode,
  Gemini CLI, Cursor or any Agent Skills folder (global or per brain), rewriting Claude-only
  parts. Brains get `AGENTS.md` and `GEMINI.md` pointing to `MIND.md`.
- Skills fall back to batch-by-batch reading when the agent has no sub-agents.

## 1.0.0 (2026-10-07)

First stable release.

- **Skills:** `init`, `import`, `capture`, `learn` (start, teach, quiz, diagnose, spar),
  `recall`, `know-me`, `reflect`, `connect-dots`, `export`, `tidy`, `review`
- **Import:** Instagram/Facebook (HTML and JSON), WhatsApp, ChatGPT and Claude exports,
  Google Takeout, Obsidian vaults, any folder or `.zip`. Keys, passwords, phone and card
  numbers are masked before anything reaches the brain; `raw/imports/` is gitignored.
- **Export:** an about-me profile for other AIs, an Anki deck of your recall cards, a JSON
  dump, and a zip backup.
- **Learning:** spaced repetition with Leitner boxes (1, 3, 7, 14, 30, 90 days), a
  mistakes ledger, learning maps, and "redo without help".
- **Reader agent:** reads big imports and large brains in parallel, read-only.
- **Hooks:** secret guard, read-only `raw/`, due-cards reminder at session start. They do
  nothing outside a folder with `MIND.md`.
- Every skill smoke-tested end to end against a sample brain; unit tests for the hooks,
  importer and exporter run in CI on Linux, macOS and Windows.
- Works on Windows: hooks fall back to `python`, scripts read non-UTF-8 files and print UTF-8.

## 0.1.0 – 0.9.0 (2026-10-07)

Design, folder structure, first skills, commands (later folded back into skills), the
reader agent, hooks, import and export, and fixes from smoke tests.
