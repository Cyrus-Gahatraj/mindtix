---
name: review
description: Weekly review of a mindtix brain. Finds patterns in what the user captured, learned and worked on, checks learning progress and due cards, and proposes what the brain should grow next. Use when the user says "review", "weekly review", "review my week", or "what should the brain grow".
---

# Review

1. **See what changed this week.** Git misses gitignored and uncommitted files, so check both:
   - `git log --since="7 days ago" --stat` and `git status`
   - `find raw logs -name '*.md' -mtime -7`
2. **Read what changed** (if more than ~30 files changed, give them to the `reader` agent). Themes they kept returning to (the questions in `logs/` show what
   they wonder about), topics in `learning/` that moved and ones that stalled, projects that
   went quiet, open questions, and files in `raw/` that `/mindtix:capture` hasn't processed.
3. **Learning check:** modules ticked this week in each `learning/<topic>/map.md`, scores in
   `sessions.md`, new rows in `learning/mistakes.md`, and how many recall cards are due.
4. **Run `/mindtix:tidy` in report-only mode** and keep the count of problems.
5. **Check before you claim.** Anything about git or ignore rules must be confirmed with a
   command (`git check-ignore -v`, `git status`, `git log`) first; leave out what you can't confirm.
6. **Report in under 20 lines:**
   - what they focused on, and what that says about them (`[inferred]`)
   - patterns: repeated topics, unfinished threads, contradictions
   - learning: progress per topic, the most repeated mistake (suggest
     `/mindtix:learn diagnose` if one repeats), due cards (offer a `/mindtix:recall` round)
   - housekeeping: unprocessed `raw/` files, tidy problems
7. **Propose growth:** at most 3 changes, each justified by real content (e.g. "8 notes
   about chess sit in `knowledge/`, so give chess its own `hobbies/chess/` folder"). If
   nothing is justified, say so.
8. **Apply only what they approve**, keep `INDEX.md` in sync, and offer to commit as
   "Review YYYY-MM-DD".
