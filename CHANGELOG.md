# Changelog

## Unreleased

- **`today` skill:** one daily 5-10 minute session: up to 5 due cards, one step on the
  topic being learned now, and one question from an older topic.
- **`forget` skill:** removes a person or topic from every note, card, insight line, log
  and export after one confirmation; `raw/` files are only deleted whole, on request.
  Commits without the name and explains how to clear git history.

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
