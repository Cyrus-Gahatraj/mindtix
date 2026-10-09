---
name: export
description: Export a mindtix brain. "profile" writes a short about-me for other AIs (ChatGPT custom instructions, Claude projects, Gemini), "anki" turns recall cards into an Anki deck file, "json" dumps every note and card, "bundle" zips the whole brain as a backup, "site" makes a website of the brain: static (one file to open or host), live (a local server adding an Ask chatbot that answers from the notes and remembers chats) or custom (built to the user's description). Use when the user says "export", "back up my brain", "make my profile for ChatGPT", "send my cards to Anki", "make a website of my brain", "publish my notes", "chat with my brain", or "give me my data".
argument-hint: "[profile|anki|json|bundle|site|all]"
---

# Export

Format: $ARGUMENTS (if empty, ask which, listing the five in one line each).

Work from the brain root (the folder with `MIND.md`). Exports go to `exports/` in the brain
(gitignored; add `exports/` to `.gitignore` if it's missing) unless the user names another
path. Never export `private/`, `logs/` or `raw/imports/`, and never put secrets in an export.

## profile: about-me for other AIs
Write `exports/profile-YYYY-MM-DD.md`, at most ~400 words, in second person to the AI
("The user is…"), from `MIND.md`, `self/`, `projects/`, `hobbies/` and the levels in
`insight/knowledge.md`:
- who they are, what they do, what they're learning now and their level in it
- how they like to learn and to be answered (from `MIND.md` "How the AI should behave")
- current projects in one line each
Use **only `[stated]` facts** by default; ask before including `[inferred]` guesses, and
never include love life, health, mood, other people's details or anything from `private/`.
Show it in the reply so they can paste it straight into custom instructions.

## anki, json, bundle, site: run the scripts
Next to this SKILL.md are `export.py` and `serve.py` (standard library only). `PY` below means
`uv run --no-project python` when `command -v uv` finds uv, otherwise `python3`.

```sh
PY "<this skill's dir>/export.py" anki   . exports/mindtix-cards-YYYY-MM-DD.txt
PY "<this skill's dir>/export.py" json   . exports/mindtix-YYYY-MM-DD.json
PY "<this skill's dir>/export.py" bundle . exports/mindtix-YYYY-MM-DD.zip
PY "<this skill's dir>/export.py" site   . exports/site/index.html [folder ...|all]
PY "<this skill's dir>/serve.py"  . [port] [folder ...|all]
```

- **anki:** one note per recall card (front = question, back = which page holds the
  answer, tags = `mindtix` + topic). In Anki: File → Import, pick the file. Mention that the
  cards keep living in the brain; Anki is a copy.
- **json:** every note with its path, title, links and text, plus every card with box and
  due date. Useful for other apps or scripts.
- **bundle:** a zip of the brain for backup or moving machines. It leaves out `.git`; tell
  them the git history is the fuller backup (`git push` to a private repo).
- **site:** first ask, in one message, which kind (unless they already said):
  1. **static**: one `index.html` that opens in any browser, no server: home, every note with
     its backlinks, folder pages, an index, the link graph, ⌘K search, and the insight charts
     from `insight/scores.json` and `insight/knowledge.md`. Light and dark. Good to host.
  2. **live**: the same site served on `http://127.0.0.1:4321`, rebuilt from the notes on
     every page load, plus an **Ask** page: a chatbot that answers from the brain (the notes
     most related to the question, `MIND.md` and `INDEX.md`), cites notes as links, and
     remembers. Each chat is kept in `logs/<date>-chat.md`, sent back in full on every turn,
     and new chats see recent questions from earlier ones. Only for themselves, never hosted.
  3. **custom**: whatever they describe (pages, look, interactions, a framework).

  Then ask **which folders**:
  - **static** defaults to `knowledge` and `projects`, which is safe to publish.
  - `self`, `insight`, `hobbies`, `extra`, `learning` and `raw` hold personal material:
    add them only when they name them.
  - `all` (every folder) is only for a copy they keep to themselves, and is the default for live.
  - `private/`, `logs/` and `raw/imports/` never go into any site. In a static site, links to
    notes that aren't exported become plain text.

  - **static:** run `export.py site`. It needs the internet once, for fonts and the markdown
    renderer. Putting it online (GitHub Pages, Netlify, any static host) is their step; never
    upload it yourself.
  - **live:** it needs an LLM. Check the brain's `.env` for `ANTHROPIC_API_KEY` (Claude, model
    `claude-opus-5-5`), or `MINDTIX_API_URL` plus `MINDTIX_API_KEY` for any OpenAI-compatible
    endpoint (OmniRoute, Ollama, OpenRouter, ...). `MINDTIX_MODEL` picks the model.
    - If neither is set, ask them to add one to `.env` themselves. Never ask them to paste a
      key into the chat. Make sure `.env` is in `.gitignore`.
    - Start `serve.py` in the background and give them the URL. It listens on 127.0.0.1 only;
      Ctrl+C or stopping the task ends it.
    - Mention that `/mindtix:reflect` reads `logs/`, so what they ask shapes `insight/`.
  - **custom:** build it in `exports/site-custom/` from `export.py json` output only. Never
    read `private/`, `logs/` or `raw/imports/` for it.
    - Default to a copy of `site.html` edited to their spec: plain HTML/JS, no build step.
    - Use a framework (Astro, Next, ...) only when they ask for one. Then it's their project:
      tell them the install and build commands.
    - A chatbot needs a server: offer the live kind for that, not a second server.
- **all:** profile plus the anki, json and bundle files.

Report in a few lines: what was written where, and the counts the script printed.
