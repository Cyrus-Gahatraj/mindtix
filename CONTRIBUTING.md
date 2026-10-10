# Contributing

Mindtix is mostly markdown, so most changes are edits to a workflow in `skills/mindtix/workflows/`.

- **Layout:** one skill, `skills/mindtix/`: `SKILL.md` routes to `workflows/<name>.md`; the
  scripts, the empty brain (`template/`) and the web app (`site/`) sit next to them; hooks in `hooks/`, the reader agent in `agents/`.
- **Rules every workflow keeps:** `raw/` is read-only, facts about the user are labeled
  `[stated]` or `[inferred]`, no secrets anywhere, only `reflect` writes `insight/`, update
  instead of duplicating, keep `INDEX.md` in sync. See [docs/structure.md](docs/structure.md).
- **Scripts** (`hooks/*.py`, `skills/mindtix/to_text.py`, `skills/mindtix/export.py`) use
  only the Python standard library. Add a case to `tests/` for anything you change, and run
  `for t in tests/test_*.py; do python3 "$t"; done`.
- **Try a change** without installing: `claude --plugin-dir /path/to/mindtix` in a test folder.
- Keep workflows short and concrete. If a step can't be checked, it probably isn't needed.
