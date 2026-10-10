# Tidy

Never touches `raw/` (the user's), `logs/`, `private/` or `insight/` (only `/mindtix reflect`).

1. **Run the checks** from the brain root:

   ```sh
   # Dangling [[links]]: resolve like Obsidian, by path or by bare filename anywhere
   grep -rhoE '\[\[[^]|#]+' --include='*.md' --exclude-dir=raw --exclude-dir=private --exclude-dir=logs --exclude-dir=.git . | sed 's/^\[\[//' | sort -u |
     while read -r l; do [ -e "$l.md" ] || [ -e "$l" ] ||
       [ -n "$(find . -name "$(basename "$l").md" -print -quit)" ] || echo "dangling: $l"; done
   # Notes missing from INDEX.md (READMEs and examples excluded)
   find self knowledge learning projects hobbies extra -name '*.md' ! -name README.md ! -name '_example*' 2>/dev/null |
     sed 's|\.md$||' | while read -r n; do grep -qF "$n" INDEX.md || echo "not in INDEX: $n"; done
   # Empty folders
   find . -type d -empty -not -path './.git/*'
   # Secrets and ID-like numbers
   grep -rnIE '(api[_-]?key|token|secret|password)\s*[:=]|sk-[A-Za-z0-9]{20,}|[0-9]{9,}' --exclude-dir=raw --exclude-dir=private --exclude-dir=logs --exclude-dir=.git --include='*.md' .
   # Overdue recall cards (due before today)
   grep -rnoE '\[b[0-5] · due [0-9-]+\]' knowledge --exclude='_example*' | awk -v t="$(date +%F)" '{d=$NF; sub(/\]$/,"",d); if (d<t) print}'
   ```

2. **Weed out false positives by reading each hit**, and confirm anything about git with a
   command (`git check-ignore -v <file>`, `git status`) before reporting it: a `[[link]]` inside backticks is an
   example; long numbers can be dates, ratings or ISBNs (flag only what looks like an ID or key).
3. **Also check by reading:** `INDEX.md` lines that point at missing files; `MIND.md` over
   ~80 lines (move a section into its own note); `[inferred]` facts in `self/` older than a
   month, listed as questions for `/mindtix know-me`; `learning/<topic>/map.md` untouched for a
   month (stalled topic); a result in `insight/scores.json` with no `method` (`asked`, `self`
   or `inferred`), fixed by `/mindtix reflect`, not here.
4. **Report** one line per problem, grouped by check, with the fix you'd make. If all clean,
   say so in one line. When run from `/mindtix review`, stop here.
5. **Fix only what they approve.** A secret is removed at once, with a note that it's still in
   git history if it was committed. Offer to commit as "Tidy YYYY-MM-DD".
