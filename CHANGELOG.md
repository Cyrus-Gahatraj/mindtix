# Changelog

## Unreleased

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
