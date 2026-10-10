# Init

Target folder: $ARGUMENTS (empty = current directory).

Sets up an empty brain from the `template/` folder in the skill folder.

1. **Pick the folder.** Use the path the user gave, otherwise the current directory. If it
   already has a `MIND.md`, stop: it's already a brain. If it has other files, list them
   and ask before mixing the brain into it; suggest a fresh folder such as `~/mind`.
2. **Copy the template** with its hidden files:
   `cp -R "<this skill's dir>/template/." "<target>/"`. If copying from the plugin folder
   is blocked, read each template file (including `.gitignore`) and write it to the same
   path in the target.
   Then delete the two example items, `knowledge/_example.md` and `learning/_example/`, only
   if the user says they don't want them. They show the formats and are safe to keep until
   real content arrives.
3. **Make it a git repo** if it isn't one (`git init`), so every change can be undone.
   `.gitignore` already keeps `logs/` and `private/` out.
4. **First interview.** Ask 4-5 short questions in one message:
   - what to call them, and where they are from or live
   - what they do (study, work, build, make)
   - what they want to learn next, and by when
   - how they like to learn (build first, read first, watch, talk it through)
   - one thing they want this brain to remember about them
5. **Write the answers** into `MIND.md` under "About me" and into `self/profile.md`, each
   fact labeled `[stated]`. Add `self/profile.md` to `INDEX.md`.
6. **Show the next steps** in a few lines:
   - drop notes into `raw/notes/`, exports into `raw/imports/`, writing into `raw/writing/`
   - `/mindtix capture` to file anything or process those notes
   - `/mindtix learn <topic>` to start learning what they named in step 4
   - `/mindtix know-me` for more interview rounds, `/mindtix reflect` once there is content
   Offer to commit as "Init mindtix".
