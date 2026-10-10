# Sort

Moves files into the brain from anywhere (`/mindtix sort ~/Downloads/song.mp3`), and loose
files inside it (dropped in the root or in the wrong folder) to where they belong. Each one
leaves a line of text in a note, because `/mindtix reflect` reads text, not audio or images.
Input: $ARGUMENTS, the files or folder to sort. Empty means every stray file in the brain.

Work from the brain root (the folder with `MIND.md`). Never touch `logs/`, `private/` or
`insight/`, and never move or rename anything already in `raw/`.

1. **Find strays.** Without arguments: `git status --porcelain --untracked-files=all`, plus any
   file in the brain root other than `MIND.md`, `INDEX.md`, the agent files (`CLAUDE.md`,
   `AGENTS.md`, `GEMINI.md`), `README.md` and dotfiles. A non-markdown file outside `raw/` (a
   photo in `self/`, audio in `projects/`) is a stray too, unless a note links to it.
   A path outside the brain is moved in (step 4). A data export or a big folder of notes goes
   to `/mindtix import` instead.
2. **Look at each one** before deciding: its name, type (`file`), size, metadata (`ffprobe`,
   `exiftool` or `mdls`, whichever exists), and the text inside if it has any. Search the
   brain for its name (`grep -rl "<name>" --exclude-dir=.git .`); a note that mentions it
   tells you where it goes. Then read what's in it, so the brain gets the content:

   | Kind | Read it with |
   |---|---|
   | Audio | `librosa` (try `uv run --with librosa python`): length, tempo, key and mode from chroma plus the bass notes, the chords used, loudness over time, stereo width. Measured, not heard: say so, and give close candidates (relative modes share notes) |
   | Image | look at it: what it shows, any text in it |
   | PDF or document | its text (`pdftotext`, or your file reader) |
   | Video | `ffprobe` for length; frames (`ffmpeg -vf fps=1/10`) and its audio as above |

   No tool for it? Note only what you know (type, length, name) and move on.
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
   and `mv` for the rest, including files from outside the brain. Never overwrite; on a name
   clash, ask.
5. **File what they say.** A file that tells you something about them (a song they made, a
   project asset) gets a line in the right note (`hobbies/`, `projects/`, `self/`), labeled
   [stated] or [inferred], with a link to the file and a short summary of what step 2 found
   (marked [inferred], "measured, not heard" for audio). Ask one question that the content
   raises and only they can answer (which key they meant, who's in the photo), and file the
   answer as [stated]. Update `INDEX.md` for every note you create or move.
6. **Report** in a few lines what moved where, then offer to commit as "Sort YYYY-MM-DD".
