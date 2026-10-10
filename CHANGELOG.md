# Changelog

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
