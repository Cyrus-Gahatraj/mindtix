# Tidy

Never touches `raw/` (the user's), `logs/`, `private/`, or `self/insight/` (only `/mindtix reflect`;
it reports problems there for reflect to fix).

1. **Run the checks** from the brain root:

   ```sh
   # Dangling [[links]]: resolve like Obsidian, by path or by bare filename anywhere
   grep -rhoE '\[\[[^]|#]+' --include='*.md' --exclude-dir=raw --exclude-dir=private --exclude-dir=logs --exclude-dir=.git . | sed 's/^\[\[//' | sort -u |
     while read -r l; do [ -e "$l.md" ] || [ -e "$l" ] ||
       [ -n "$(find . -name "$(basename "$l").md" -print -quit)" ] || echo "dangling: $l"; done
   # Orphans: notes nothing links to (INDEX.md doesn't count)
   find knowledge projects self learning -name '*.md' ! -name README.md ! -name '_example*' 2>/dev/null | while read -r f; do
     p=${f%.md}; n=$(basename "$p"); q=${p#*/}
     [ -n "$(grep -rlF -e "[[$n]" -e "[[$n|" -e "[[$n#" -e "[[$p]" -e "[[$p|" -e "[[$p#" -e "[[$q]" -e "[[$q|" -e "[[$q#" --include='*.md' --exclude=INDEX.md --exclude-dir=raw --exclude-dir=.git . | grep -vx "./$f")" ] || echo "orphan: $p"; done
   # Unlinked mentions: a knowledge page's title written in another note without a link to it
   find knowledge -name '*.md' ! -name README.md ! -name '_example*' | while read -r f; do
     t=$(sed -n 's/^# //p' "$f" | head -1); p=${f%.md}; n=$(basename "$p"); [ ${#t} -ge 4 ] || continue
     grep -rliF -- "$t" --include='*.md' self knowledge learning projects 2>/dev/null | grep -vx "$f" | while read -r g; do
       grep -qF -e "[[$n" -e "[[$p" -e "[[${p#*/}" "$g" || echo "unlinked: \"$t\" in $g"; done; done
   # Notes missing from INDEX.md (READMEs and examples excluded)
   find self knowledge learning projects -name '*.md' ! -name README.md ! -name '_example*' 2>/dev/null |
     sed 's|\.md$||' | while read -r n; do grep -qF "$n" INDEX.md || echo "not in INDEX: $n"; done
   # Empty folders
   find . -type d -empty -not -path './.git/*'
   # Yes/no cards (rewrite them so the answer has to be produced)
   grep -rnE '^\s*-\s*(\[b[0-5] · due [0-9-]+\]\s*)?(Is|Are|Does|Do|Did|Can|Could|Should|Will|Has|Have) ' knowledge --exclude='_example*'
   # Secrets and ID-like numbers
   grep -rnIE '(api[_-]?key|token|secret|password)\s*[:=]|sk-[A-Za-z0-9]{20,}|[0-9]{9,}' --exclude-dir=raw --exclude-dir=private --exclude-dir=logs --exclude-dir=.git --include='*.md' .
   # Overdue recall cards (due before today)
   grep -rnoE '\[b[0-5] · due [0-9-]+\]' knowledge --exclude='_example*' | awk -v t="$(date +%F)" '{d=$NF; sub(/\]$/,"",d); if (d<t) print}'
   ```

2. **Weed out false positives by reading each hit**, and confirm anything about git with a
   command (`git check-ignore -v <file>`, `git status`) before reporting it: a `[[link]]` inside backticks is an
   example; long numbers can be dates, ratings or ISBNs (flag only what looks like an ID or key).
   An unlinked title that's an ordinary word in that sentence isn't a miss. The fix for an
   orphan is a link from the page it belongs with; for an unlinked mention, link its first one.
3. **Also check by reading** (a sample on a big brain; hand big folders to the `reader` agent):
   - **contradictions:** two notes that claim opposite things; say which looks right and why
   - **stale claims:** time-sensitive facts ("currently", versions, prices, "the latest") whose
     `Updated:` or `Captured:` is over 6 months old
   - **missing concept pages:** a term used in 3+ notes with no page of its own
   - **leeches:** cards in the Leeches table of `python3 "<this skill's dir>/srs.py" stats .`,
     to rewrite or split
   - also: `INDEX.md` lines that point at missing files; `MINDTIX.md` (or `MIND.md`) over
   ~80 lines (move a section into its own note); `[inferred]` facts in `self/` older than a
   month, listed as questions for `/mindtix know-me`; `learning/<topic>/map.md` untouched for a
   month (stalled topic); a result in `self/insight/scores.json` with no `method` (`asked`, `self`
   or `inferred`), fixed by `/mindtix reflect`, not here.
4. **Report** one line per problem, grouped by check, with the fix you'd make. If all clean,
   say so in one line. When run from `/mindtix review`, stop here.
5. **Fix only what they approve.** A secret is removed at once, with a note that it's still in
   git history if it was committed. Offer to commit as "Tidy YYYY-MM-DD".
