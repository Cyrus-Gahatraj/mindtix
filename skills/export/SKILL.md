---
name: export
description: Export a mindtix brain. "profile" writes a short about-me for other AIs (ChatGPT custom instructions, Claude projects, Gemini), "anki" turns recall cards into an Anki deck file, "json" dumps every note and card, "bundle" zips the whole brain as a backup, "site" runs the brain as a local Astro web app: Today with quick capture, Notes, a graph, ⌘K search, Insight, Write (add and edit notes), Recall (due cards), Settings, and Ask, a chat that runs the /mindtix commands through Claude Code or answers from the notes over an API. Use when the user says "export", "back up my brain", "make my profile for ChatGPT", "send my cards to Anki", "make a website of my brain", "chat with my brain", "edit my notes in a browser", or "give me my data".
argument-hint: "[profile|anki|json|bundle|site [folder path]|all]"
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

## anki, json, bundle: run the script
Next to this SKILL.md is `export.py` (standard library only). `PY` below means
`uv run --no-project python` when `command -v uv` finds uv, otherwise `python3`.

```sh
PY "<this skill's dir>/export.py" anki   . exports/mindtix-cards-YYYY-MM-DD.txt
PY "<this skill's dir>/export.py" json   . exports/mindtix-YYYY-MM-DD.json
PY "<this skill's dir>/export.py" bundle . exports/mindtix-YYYY-MM-DD.zip
```

- **anki:** one note per recall card (front = question, back = which page holds the
  answer, tags = `mindtix` + topic). In Anki: File → Import, pick the file. Mention that the
  cards keep living in the brain; Anki is a copy.
- **json:** every note with its path, title, links and text, plus every card with box and
  due date. Useful for other apps or scripts.
- **bundle:** a zip of the brain for backup or moving machines. It leaves out `.git`; tell
  them the git history is the fuller backup (`git push` to a private repo).
- **all:** profile plus the anki, json and bundle files.

## site: the brain as a local website
The Astro project is `site/` next to this SKILL.md. `export site` copies it into
`exports/site/` in the brain (or a folder they name), where it's theirs to see and change. It
runs on `http://127.0.0.1:4321`, only for them, and reads the notes on every request.
- **Today:** a greeting, quick capture, due cards, the last chat, what they're learning, and
  recent notes.
- **Notes:** every note, with a filter, folder chips and sort. Each note shows its backlinks and
  outgoing links.
- **Ask:** chat that streams. With Claude Code it runs the `/mindtix` commands (type `/`).
- **Write:** new notes and edits, with `[[` autocomplete, preview and drafts that survive a
  closed tab.
- **Recall:** today's due cards, driven by the keyboard.
- **Insight:** the scores, the knowledge levels and the brain's stats.
- **Graph:** its own page.
- **Profile:** their picture (saved as `self/photo.jpg`), About me and their notes in `self/`.
- **Settings:** the chat engine, folders and theme.
- **⌘K:** search and actions everywhere. Light and dark, and a bottom tab bar on phones.

It's never hosted. For a public copy of some notes, `export json` is the starting point.

**Set it up and start it, without asking anything:**

```sh
PY "<this skill's dir>/export.py" site . [folder path] [brain folder ...]
```

- **Where:** by default the project goes in `exports/site/` in the brain, which is gitignored.
  A path in the arguments (anything with `/`, `~` or `.`, like `site ~/projects/brain-site`)
  puts it there instead. The folder is remembered in `exports/site.json`, so the next
  `export site` reuses it.
- **What the script does:** copies `site/` there (never links it, because edits through a link
  would change the plugin and be lost on the next update). It writes `mindtix.json` (the brain's
  path and folders) and runs `npm install`.
- **A copy that's already there** is theirs and is kept. Ask before running it again with
  `--replace` to update it to this version; their `mindtix.json` stays.
- **Inside the brain,** it refuses any folder outside `exports/`. It also refuses a folder that
  has other files in it.
- **Folders:** every folder by default. Bare words in the arguments (`site knowledge projects`)
  pick folders. `private/`, `logs/` and `raw/imports/` never go in.
- **Then** start `npm run dev` in that folder in the background and give them
  `http://127.0.0.1:4321` and the folder. It needs Node 22.12 or newer; the script says so if
  it's missing. The site listens on 127.0.0.1 only, and `npx astro dev stop` in the folder
  ends it.

**What the pages do:**
- **Write** adds new notes to `INDEX.md`. It refuses `insight/`, `private/`, `logs/` and
  `raw/imports/`, anything that looks like a secret, and a note that changed on disk since it
  was opened.
- **Recall** moves a right card up a box. A miss sends the card to b0 and into
  `learning/mistakes.md`. Each round is logged in the topic's `## Log`.
- **Ask** keeps each chat in `logs/<date>-chat.md`. It has two engines, picked in Settings:
  - **Claude Code** is the default when `claude` is installed. It runs `claude -p` in the brain
    with their own login, one Claude Code session per chat. It reads and edits notes itself and
    runs the `/mindtix` commands (`/today` works as short for `/mindtix:today`), under the same
    hooks as the terminal (secret guard, auto-commit). Settings picks the model and can make it
    read-only.
  - **API** answers questions from the notes most related to them, without commands. It uses
    `ANTHROPIC_API_KEY` (Claude, model `claude-opus-5-5`), or `MINDTIX_API_URL` plus
    `MINDTIX_API_KEY` for any OpenAI-compatible endpoint (OmniRoute, Ollama, OpenRouter, ...).
    `MINDTIX_MODEL` picks the model. These come from the environment or the brain's `.env`.
    Check which names are set, never their values. Settings saves one to `.env` and keeps `.env`
    in `.gitignore`. Never ask them to paste a key into the chat.
- **Quick capture** on Today adds a timed line to `raw/notes/<date>.md`, the user's own notes.
  `/mindtix:capture` files it into the brain later.
- Mention that `/mindtix:reflect` reads `logs/`, so what they ask shapes `insight/`. What they
  write and grade on the site lands in the brain right away.

For other changes (pages, look), they or Claude edit their copy in that folder. It's plain Astro
(`src/pages/` for pages, `src/styles/site.css` for the look), and the dev server reloads on save.
`npm test` there runs the self-check.

Report in a few lines: what was written where, and the counts the script or build printed.
When Claude Code isn't installed and no API AI is set up, make the **last line** of the report:
"Ask needs an AI: pick one in the site's Settings (saved to your brain's `.env`), or add
`ANTHROPIC_API_KEY=...` or `MINDTIX_API_URL=...` to `.env` yourself."
