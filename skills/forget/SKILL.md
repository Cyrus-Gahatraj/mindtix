---
name: forget
description: Remove a person or topic from a mindtix brain everywhere it appears (notes, cards, insight, logs, exports, and raw/ files on request), after showing the user every hit and getting one confirmation. Use when the user says "forget", "forget about <name>", "remove everything about", "delete <person> from my brain", "I don't want <topic> in here anymore", or asks to take someone out after an import.
argument-hint: "<person or topic>"
---

# Forget

Forget: $ARGUMENTS (if empty, ask who or what).

Work from the brain root (the folder with `MIND.md`). This deletes, so show everything
first and change nothing until they confirm. Never write the name into a new file, a log
line or a commit message.

1. **Collect the names to search for.** The name they gave, plus every alias: nicknames,
   handles, first name alone, and what `self/people.md` (or a note about them) lists. Ask
   once: "Any other names, handles or spellings?" For a topic: its name, page names and
   obvious synonyms.
2. **Search everywhere**, `.git/` excluded, whole words, case-insensitive:

   ```sh
   grep -rnIiw --exclude-dir=.git -e 'Name' -e 'nickname' -e '@handle' .
   ```

   Also look at file and folder names (`find . -iname '*name*' -not -path './.git/*'`).
   Read each hit and drop false positives (a "Sam" inside "Sam's Club", a topic word used in
   passing about something else).
3. **Show the plan, grouped**, with a count per group:
   - **Delete whole file:** notes that are about them (a page on the person, `learning/<topic>/`,
     `knowledge/<topic>.md`).
   - **Remove lines:** mentions inside other notes (`self/`, `knowledge/`, `projects/`,
     `insight/`, `logs/`, `INDEX.md`), recall cards and `learning/mistakes.md` rows about them,
     `[[links]]` to deleted pages. Where a sentence is mostly about the user, keep it and
     rewrite the other person as "someone"; otherwise drop the line.
   - **raw/ files (yours, never edited):** list them. Each can only be deleted whole or kept;
     say which ones are mostly about them (a chat export with them) and which only mention
     them once.
   - **exports/:** old exports that contain them. Offer to delete them; re-export later.
   - **Topic only:** its entry in `insight/knowledge.md` and `insight/scores.json`.

   Then ask once: "Go ahead? You can drop any item from the list." Apply only what they
   approve. `/mindtix:forget` is the one skill besides `/mindtix:reflect` allowed to change
   `insight/`, and only to delete.
4. **Apply it.** Edit lines in place; delete files with `rm` only for the approved files.
   Update `INDEX.md`. Don't add notes about what was forgotten.
5. **Check:** run the same search again. Report what's left (should be only what they chose
   to keep) in 1-2 lines.
6. **Git.** If the brain is a git repo, commit right away as "Forget a person" or "Forget a
   topic" (never the name). Then tell them plainly: it's gone from the files, but still in
   git history, and in any remote the brain was pushed to. If they want it out of history,
   give them the command to run themselves; don't run it:

   ```sh
   # needs git-filter-repo; rewrites history. First drop the deleted files, then the name in the rest
   git filter-repo --invert-paths --path self/people/name.md --path raw/imports/chat-with-name.md
   git filter-repo --force --replace-text <(printf '%s==>someone\n' 'Name' 'nickname')
   ```

   and that after rewriting, a pushed remote needs a force-push and other clones must be
   re-cloned.
