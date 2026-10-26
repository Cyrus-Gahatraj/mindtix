# Reflect

If an argument names a personality test, run that test: $ARGUMENTS

`self/insight/` is written **only** by this workflow and `connect-dots`. Each run rereads everything
and rewrites `self/insight/` from that evidence, so it reflects all of it, not just the latest bit.
Besides `self/insight/`, the only thing it edits is `raw/notes/` (step 0).

0. **Tidy `raw/notes/` in place** (their quick captures). Their words stay theirs: fix
   form, never content or voice.
   - Give each note a `# Title` and a one-line summary if it lacks them; turn plain mentions of
     existing page titles into `[[links]]`; fix links that point nowhere.
   - Merge notes that say the same thing into one (keep every line, drop exact repeats), and
     split a note that holds unrelated ideas. A dated quick-capture file
     (`raw/notes/YYYY-MM-DD.md`) stays as it is, apart from links.
   - Once 3+ notes share a theme, group them into `raw/notes/<theme>/`. No folder before that.
   - Strip any secret or ID number and say so. Keep `INDEX.md` in sync (section `## Notes`)
     for every note made, merged, moved or split.
   - Don't move notes out of `raw/notes/` or file them into other folders: that's
     `/mindtix capture`. List what was tidied in the report.

1. **Gather everything.** Start from `MINDTIX.md` (or `MIND.md`) and `INDEX.md`, then read every folder except
   `private/`: `self/` (including `self/insight/`), `knowledge/`, `learning/` (maps, sessions, `mistakes.md`), `projects/`,
   `raw/` (their own notes and writing are the most direct evidence
   of how they think), `logs/` (the questions they ask: what they wonder and worry about). Read `git log --stat` for rhythm and hours. Read anything outside the brain
   only with permission.
   On a large brain (more than ~100 notes or a lot of `raw/`), hand big folders to the
   `reader` agent (in parallel when there are several) and work from its reports; without
   sub-agents, read folder by folder and keep short notes as you go.
2. **Rewrite each file:**
   - `self/insight/knowledge.md`: a table `| Topic | Level | Evidence | Updated |` with levels
     0 never touched · 1 heard of it · 2 can follow along · 3 can build with it · 4 can teach
     it · 5 expert. Every level needs evidence (a project, a quiz score from `learning/`, a
     note). `/mindtix learn` uses these levels to pitch difficulty.
   - `self/insight/learning.md`: **how they learn**, from what actually happened, never from
     what they say they prefer. Run `python3 "<this skill's dir>/srs.py" stats .` and read every
     `learning/*/sessions.md` (the format, pretest, hints, redo and mastery fields),
     the types in `learning/mistakes.md` and the `## In my words` lines. Sections:
     - **What works for you:** which formats (`worked`, `build`, `socratic`, `explain`) lead
       to passing the mastery check and to cards remembered at their first review, each claim
       with its numbers (n) and a confidence. Under 5 cards and 2 sessions for a format, say
       "too early" instead of guessing.
     - **Calibration:** right when sure vs not sure. Name overconfidence plainly ("you're
       sure and wrong about a third of the time on SQL").
     - **Mistake mix:** slips vs misconceptions vs missing prerequisites, and what that means
       (slips → slow down; misconceptions → contrast cases; prereqs → go back a module).
     - **Rhythm:** session length and time of day where results hold up, if `reviews.csv`
       and git show it; leeches to rewrite.
     - **Teaching plan:** the lines `/mindtix learn` follows, e.g. `Default: level 0-1 →
       worked; 2+ → build. Try next: socratic. Always pretest. Hints: stop at rung 2.`
     Say that "How I like to learn" in `MINDTIX.md` is a starting guess and these numbers win;
     there is no evidence for fixed learning styles (visual, auditory…), so don't use them.
   - `self/insight/mind.md`: how they think and how mature they are, each point with evidence and
     a confidence level (low, medium, high). Any IQ range only at medium confidence or above,
     always called a guess, never a test result.
   - `self/insight/habits.md`: good and bad habits, each with evidence.
   - `self/insight/writing-style.md`: only if `raw/writing/` or long notes exist. Voice, themes,
     images, strengths and weaknesses, with short quotes as proof.
   - `self/insight/scores.json`: keep `iq` in sync with `mind.md`, bump `updated`, and check it
     parses (`python3 -m json.tool self/insight/scores.json`). Change test results only when a
     test is (re)taken, or when the user states a result. Every result carries a `method`:
     - `asked`: you asked the test items here; the raw `answers` are stored
     - `self`: the user wrote or stated it (an outside test, "I'm an INFJ" in a note or chat)
     - `inferred`: you estimated it from the brain's evidence (`iq` always is)
     When it's mixed, label the headline result (the type, the code) and say the rest in `source`. Give any result
     without a `method` one, judging by its `source` and `answers`; if it can't be told, ask.
3. **Connect the dots:** run `/mindtix connect-dots` on the same evidence.
4. **Write about the user in the second person** ("you"), never as "I". **Be honest, not flattering.** Name bad habits plainly, without moralizing. Everything is
   `[inferred]` unless they stated it. Remove claims the evidence no longer supports.
5. **Report** in under 15 lines: what was tidied in `raw/notes/`, what changed in `self/insight/`, the most surprising pattern, and the one
   question that would raise confidence most. Ask it. Offer to commit as
   "Reflect YYYY-MM-DD: <what changed>".

**Personality tests** (on request): Big Five (Mini-IPIP, 20 items), MBTI-style axes, Grit
(8 items), Holland RIASEC. Ask one item at a time on a 1-5 scale, store the raw answers and
scores in `scores.json` with `"method": "asked"`. A result the user brings from elsewhere
goes in with `"method": "self"` and where it came from in `source`.

Never store secrets or ID numbers. Add a new insight file (e.g. `values.md`) only when there
is real evidence for it.
