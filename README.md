# mindtix

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

## Commands

| Command | What it does |
|---|---|
| `/mindtix:init [folder]` | Creates a new brain and runs a first short interview |
| `/mindtix:capture [text \| notes]` | Files anything you say or paste; `notes` processes new files in `raw/` |
| `/mindtix:learn <topic>` | Interview + map a new topic, then build-first teaching with redo-without-help |
| `/mindtix:quiz <topic> [socratic\|exam\|explain\|check]` | Makes you produce: questions, explain-back, or a check of your work |
| `/mindtix:diagnose [topic]` | Finds the one root misunderstanding behind repeated mistakes |
| `/mindtix:spar <scenario>` | Timed practice: interviews, live coding, pitches, exams |
| `/mindtix:recall [topic]` | Spaced-repetition review of the cards that are due |
| `/mindtix:know-me` | A short interview round that fills in `self/` |
| `/mindtix:reflect [test]` | Rewrites `insight/`, or runs a personality test |
| `/mindtix:connect-dots` | Finds how everything you know connects |
| `/mindtix:tidy` | Health check: broken links, index drift, secrets, overdue cards |
| `/mindtix:review` | Weekly review: focus, learning progress, what to grow |

Commands live in [`commands/`](commands/) and are thin entry points; the full instructions
are the skills in [`skills/`](skills/). You can also just talk ("teach me SQL", "save
this", "quiz me") and Claude picks the right skill.

## Status

Early (v0.2). A local web view and CLI may come later.

## License

MIT
