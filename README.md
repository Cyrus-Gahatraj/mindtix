# mindtix

[![test](https://github.com/Cyrus-Gahatraj/mindtix/actions/workflows/test.yml/badge.svg)](https://github.com/Cyrus-Gahatraj/mindtix/actions/workflows/test.yml)

A second brain that gets to know you, and helps you actually learn. Mind + *The Matrix*.

Mindtix is a folder of plain markdown that an AI agent (Claude Code, for now) keeps for you.
You drop in your notes, writing and data exports. The AI builds pages about who you are and
what you know, tracks what you're learning, and quizzes you until it sticks. Everything is
local, readable in Obsidian, and yours.

## The layout

```
my-mind/
├── MIND.md        rules for the AI + short "who you are"
├── INDEX.md       one line per note; the AI reads this first
├── raw/           everything YOU put in. The AI reads it, never edits it
│   ├── notes/       your own notes
│   ├── imports/     data exports, transcripts, articles, PDFs
│   └── writing/     drafts and creative writing, verbatim
├── self/          who you are: profile, personality, people, timeline
├── knowledge/     one page per topic you understand, with recall cards
├── learning/      what you're learning now: maps, sessions, mistakes
├── projects/      one note per thing you make
├── hobbies/       one subfolder per hobby
├── extra/         anything else: school, work, health, ...
├── insight/       the AI's evidence-based read of you
├── logs/          chats with your brain (not committed)
└── private/       anything sensitive (not committed)
```

Details: [docs/structure.md](docs/structure.md).

## How learning works

You don't learn by reading. You learn by producing: recalling, explaining, predicting, doing.
Mindtix puts the AI in ten roles around that idea (interviewer, mapmaker, explainer, Socratic
questioner, examiner, checker, listener, diagnostician, sparring partner, clerk) and schedules
reviews with spaced repetition. See [docs/learning.md](docs/learning.md).

```
interview → map → try → explain only the stuck part → redo without help
        → quiz at your level → log mistakes → cards → review when due → diagnose patterns
```

## Install (Claude Code)

```
/plugin marketplace add Cyrus-Gahatraj/mindtix
/plugin install mindtix@mindtix
```

Then, in an empty folder (e.g. `~/mind`), run `/mindtix:init`. It copies the empty brain
from [`skills/init/template/`](skills/init/template/) and asks you a few questions.

**Codex, opencode, Gemini CLI, Cursor and other agents:**

```sh
git clone https://github.com/Cyrus-Gahatraj/mindtix && python3 mindtix/install.py
```

Then open your agent in an empty folder and say "set up mindtix". See
[docs/other-agents.md](docs/other-agents.md).

## Skills

| Skill | What it does |
|---|---|
| `/mindtix:init [folder]` | Creates a new brain and runs a first short interview |
| `/mindtix:import <path>` | Imports an export (Instagram, WhatsApp, ChatGPT, Claude, Takeout, Obsidian, any folder or .zip) and files what it says about you |
| `/mindtix:capture [text \| notes]` | Files anything you say or paste; `notes` processes new files in `raw/` |
| `/mindtix:learn <topic>` | Interview + map a new topic, then build-first teaching with redo-without-help |
| `/mindtix:learn quiz <topic> [socratic\|exam\|explain\|check]` | Makes you produce: questions, explain-back, or a check of your work |
| `/mindtix:learn diagnose [topic]` | Finds the one root misunderstanding behind repeated mistakes |
| `/mindtix:learn spar <scenario>` | Timed practice: interviews, live coding, pitches, exams |
| `/mindtix:recall [topic]` | Spaced-repetition review of the cards that are due |
| `/mindtix:today` | The daily 5-10 minutes: a few due cards, one learning step, one old question |
| `/mindtix:know-me` | A short interview round that fills in `self/` |
| `/mindtix:reflect [test]` | Rewrites `insight/`, or runs a personality test |
| `/mindtix:connect-dots` | Finds how everything you know connects |
| `/mindtix:export [profile\|anki\|json\|bundle]` | An about-me for other AIs, an Anki deck of your cards, a JSON dump, or a zip backup |
| `/mindtix:forget <person \| topic>` | Removes someone or something from the whole brain, after showing you every hit |
| `/mindtix:tidy` | Health check: broken links, index drift, secrets, overdue cards |
| `/mindtix:review` | Weekly review: focus, learning progress, what to grow |

Each skill is one folder in [`skills/`](skills/). One helper agent,
[`agents/reader.md`](agents/reader.md), reads big imports and large brains in parallel and
reports back facts only, so your chat stays light. It can't edit anything.

You can also just talk ("teach me SQL", "save this", "quiz me") and Claude picks the right skill.

**Hooks** ([`hooks/`](hooks/)) enforce the rules that matter most, only inside a folder
that has `MIND.md`:
- **Secret guard:** blocks writing API keys, tokens, passwords or private keys into notes
- **raw/ guard:** blocks editing your own material in `raw/` (adding new files is fine)
- **Due cards:** at session start, tells Claude how many recall cards are due
- **Auto-commit:** after each reply, commits what changed if the brain is its own git repo,
  so every change can be undone. Skips (and warns) if a file looks like it holds a secret.
  Turn it off with `MINDTIX_AUTOCOMMIT=0`

## A first week

```
/mindtix:init ~/mind                      # 5 questions, your brain exists
/mindtix:import ~/Downloads/instagram.zip # who you are, people, timeline, interests
/mindtix:capture notes                    # your notes in raw/notes/ become topic pages + cards
/mindtix:learn sql                        # interview → map → build first → redo without help
/mindtix:today                            # 5-10 minutes a day: due cards + one learning step
/mindtix:reflect                          # the AI's read of you, with evidence
/mindtix:review                           # once a week
```

Open the folder in [Obsidian](https://obsidian.md) to browse it as a linked graph.

## Privacy

- Everything stays in a local folder you own. Mindtix has no server.
- Imports are converted locally. Keys, passwords, phone and card numbers are masked first,
  and `raw/imports/`, `logs/`, `exports/` and `private/` are gitignored.
- What Claude reads is sent to Anthropic like any Claude Code session. Keep anything you
  never want sent in `private/` and don't ask the AI to open it.
- Changed your mind about someone you imported? `/mindtix:forget <name>` removes them from
  every note, card and export, and tells you how to clear git history too.
- If you push your brain to GitHub, make the repo **private**.

## Requirements

- [Claude Code](https://claude.com/claude-code), or any agent with Agent Skills (Codex, opencode, Gemini CLI, Cursor)
- Python 3 (standard library only), for the hooks, importer and exporter
- Git (recommended: every change is a commit you can undo)

## Update or remove

```
/plugin marketplace update mindtix
/plugin uninstall mindtix@mindtix
```

Uninstalling never touches your brain folder; it's just markdown.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CHANGELOG.md](CHANGELOG.md).

## License

MIT
