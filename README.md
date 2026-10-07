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

## Status

Early. This repo holds the design and an empty brain in [`template/`](template/). The
Claude Code plugin (skills + `/mindtix init`) comes next.

## License

MIT
