# Forget

Forget: $ARGUMENTS (if empty, ask who or what).

Work from the brain root (the folder with `MINDTIX.md` or `MIND.md`). This deletes, so show everything
first and change nothing until they confirm. Never write the name into a new file, a log
line or a commit message.

1. **Collect the names to search for.** The name they gave, plus every alias: nicknames,
   handles, first name alone, and what `self/people.md` (or a note about them) lists. Ask
   once: "Any other names, handles or spellings?" For a topic: its name, page names and
   obvious synonyms.
   - **Every spelling of each name:** as written, and as a slug with `-`, `_` and no space
     (`Night Train` → `night-train`, `night_train`, `nighttrain`). `[[links]]`,
     `INDEX.md` and file names use the slug, so the plain name alone misses them.
   - **The real file and folder names:** find the notes and `raw/` folders about them and add
     their names as they are, typos included (a `raw/writing/nigth_train/` folder).
   - **Topic only, its own words:** read its main note and add what only it uses: character
     and place names, chapter or part titles, a quoted line. A story's drafts often never say
     its title. Show this list in the alias question so they can strike common words.
2. **Search everywhere**, `.git/` and `node_modules/` excluded, whole words, case-insensitive:

   ```sh
   grep -rnIiw --exclude-dir=.git --exclude-dir=node_modules -e 'Name' -e 'name-slug' -e '@handle' .
   ```

   Also look at file and folder names, once per spelling
   (`find . -iname '*name*' -not -path './.git/*' -not -path '*/node_modules/*'`).
   `grep -I` skips binary files, so list the PDFs, `.docx` and images in the brain and read
   any whose name doesn't already settle it. Dot folders count too (`.obsidian/workspace.json`
   keeps recently opened file names).
   For a topic with its own `raw/` files, also check every quoted phrase in the notes
   (`"…"`, `*…*`) against those files: insight lines often quote the work without naming it.
   Words it shares with real life (an object from the story that really happened) are false
   positives when the line is about life, not the work.
   Read each hit and drop false positives (a "Sam" inside "Sam's Club", a topic word used in
   passing about something else).
3. **Show the plan, grouped**, with a count per group:
   - **Delete whole file:** notes that are about them (a page on the person, `learning/<topic>/`,
     `knowledge/<topic>.md`).
   - **Remove lines:** mentions inside other notes (`self/`, `knowledge/`, `projects/`,
     `self/insight/`, `logs/`, `INDEX.md`), recall cards and `learning/mistakes.md` rows about them,
     `[[links]]` to deleted pages. Where a sentence is mostly about the user, keep it and
     rewrite the other person as "someone"; otherwise drop the line. For a topic, cut the
     example or quote that names it and keep the rest of the sentence when it still says
     something.
   - **raw/ files (yours, never edited):** list them. Each can only be deleted whole or kept;
     say which ones are mostly about them (a chat export with them) and which only mention
     them once.
   - **exports/:** old exports that contain them. Offer to delete them; re-export later.
   - **Topic only:** its entry in `self/insight/knowledge.md` and `self/insight/scores.json`.
   - **This chat:** a chat on the site is saved as `logs/<id>.md`, so this request itself
     names them. Offer to delete that log once the rest is done.
   - **Outside the brain (only tell them, don't touch):** the agent's own session history
     (for Claude Code, `~/.claude/projects/<brain path>/`) and any memory it keeps outside
     the brain, plus the original files they copied in (Downloads, a notes app).

   Then ask once: "Go ahead? You can drop any item from the list." Apply only what they
   approve. `/mindtix forget` is the one workflow besides `/mindtix reflect` allowed to change
   `self/insight/`, and only to delete.
4. **Apply it.** Edit lines in place; delete files with `rm` only for the approved files.
   Update `INDEX.md`. Don't add notes about what was forgotten.
5. **Check:** run the same search again, every spelling and term from step 1, plus `find`.
   Report what's left (should be only what they chose to keep) in 1-2 lines.
6. **Git.** If the brain is a git repo, commit right away as "Forget a person" or "Forget a
   topic" (never the name). Then tell them plainly: it's gone from the files, but still in
   git history, and in any remote the brain was pushed to. Earlier auto-commit messages
   list changed file names, so check those too (`git log --oneline -i --grep='name-slug'`).
   If they want it out of history, give them the command to run themselves; don't run it:

   ```sh
   # needs git-filter-repo; rewrites history. First drop the deleted files, then the name in
   # the rest of the files and in commit messages
   git filter-repo --invert-paths --path self/people/name.md --path raw/imports/chat-with-name.md
   printf '%s==>someone\n' 'Name' 'nickname' 'name-slug' > /tmp/forget.txt
   git filter-repo --force --replace-text /tmp/forget.txt --replace-message /tmp/forget.txt
   rm /tmp/forget.txt
   ```

   and that after rewriting, a pushed remote needs a force-push and other clones must be
   re-cloned.
