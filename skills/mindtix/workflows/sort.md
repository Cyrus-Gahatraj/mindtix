# Sort

Moves loose files (dropped in the brain root or in the wrong folder) to where they belong.
Input: $ARGUMENTS, the files or folder to sort. Empty means every stray file in the brain.

Work from the brain root (the folder with `MIND.md`). Never touch `logs/`, `private/` or
`insight/`, and never move or rename anything already in `raw/`.

1. **Find strays.** Without arguments: `git status --porcelain --untracked-files=all`, plus any
   file in the brain root other than `MIND.md`, `INDEX.md`, the agent files (`CLAUDE.md`,
   `AGENTS.md`, `GEMINI.md`), `README.md` and dotfiles. A non-markdown file outside `raw/` (a
   photo in `self/`, audio in `projects/`) is a stray too, unless a note links to it.
2. **Look at each one** before deciding: its name, type (`file`), size, metadata (`ffprobe`,
   `exiftool` or `mdls`, whichever exists), and the text inside if it has any. Search the
   brain for its name (`grep -rl "<name>" --exclude-dir=.git .`); a note that mentions it
   tells you where it goes.
3. **Pick a home:**

   | File | Goes to |
   |---|---|
   | Their own notes | `raw/notes/` |
   | Their creative work (writing, music they made, art) | `raw/writing/`, or `raw/<kind>/` when there are two or more files of that kind (`raw/music/`, `raw/art/`) |
   | Something from outside (article, PDF, export, downloaded audio or video) | `raw/imports/` |
   | An asset for a project | next to that project's files, linked from `projects/<project>.md` |
   | Coursework | `raw/education/<place>/...`, next to that course |
   | A photo or file of them for a note (profile photo) | stays beside the note that links to it; add the link if it's missing |
   | Holds an ID, password or key | `private/`, and say so |
   | A markdown note | the right note folder; merge it if a note on that already exists |

   Still unsure what it is? Ask one short question for all the unclear files at once (what
   they are, where they came from), and don't guess.
4. **Show the plan** as `file → destination` lines, then move with `git mv` for tracked files
   and `mv` for the rest. Never overwrite; on a name clash, ask.
5. **File what they say.** A file that tells you something about them (a song they made, a
   project asset) gets a line in the right note (`hobbies/`, `projects/`, `self/`), labeled
   [stated] or [inferred], with a link to the file. Update `INDEX.md` for every note you create
   or move.
6. **Report** in a few lines what moved where, then offer to commit as "Sort YYYY-MM-DD".
