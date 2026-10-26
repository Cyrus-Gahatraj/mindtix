# Learn

Arguments: $ARGUMENTS. If the first word is a mode name, use that mode on the rest. For quiz, an optional style (socratic, exam, explain, check) may follow the topic.

Memory forms when you **produce**: recall, predict, explain, build. Explanations only feel
like learning. So ask before telling, make the user try first, and explain only the part
they're stuck on. Method: `docs/learning.md` in the mindtix repo.

Work from the brain root (the folder with `MIND.md`); if there is none, suggest
`/mindtix init`. **Before any mode**, read: the **Teaching plan** in `insight/learning.md`,
their level in `insight/knowledge.md`, `learning/<topic>/` if it exists, `knowledge/<topic>.md`,
and `raw/notes/` on the topic. Pitch everything just above their level: hard enough to
struggle, not so hard they guess. "How I like to learn" in `MIND.md` is only a first guess;
what `insight/learning.md` measured wins.

Pick the mode from the arguments or what they say. If unclear: no `learning/<topic>/` yet → **start**;
otherwise **teach** the next module.

## start: interview + map
1. **Interview**, 3-5 short questions at once: what it's for, by when, what they already
   know, how they'll be tested or use it. Push vague answers until the goal is specific
   ("pass a live coding round in 3 weeks", not "learn coding").
2. **Map** it into 4-8 modules in order, with prerequisites, the usual sticking points, and
   2-3 of the best existing explanations at their level (links, one line on why each fits).
   Skip what they already know.
3. Write `learning/<topic>/map.md`: goal, deadline, level at start, how they'll be tested,
   a `- [ ]` checklist of modules with `(needs: …)`, stuck points, best explanations. Add
   it to `INDEX.md` under "Learning now".
4. Go straight into **teach** for the first module.

## teach: one module

**Which module:** a module marked `(review)` comes first, opening with 2 questions on it
(both right → untick the mark; a miss → teach it again). Otherwise the first unchecked module
whose `(needs: …)` are all ticked.

**Which format**, from one closed list so the brain can count what works:

| Format | What it is |
|---|---|
| `worked` | A fully worked example, then the same kind of problem with the last step blank, then the last two, until they do it all (faded examples) |
| `build` | The smallest runnable thing that shows the idea, plus a small change for them to make |
| `socratic` | Questions only, until they find the idea themselves |
| `explain` | A short explanation at their level, then practice straight away |

- Use the Teaching plan's default for their level. No plan yet: worked examples for levels
  0-1 and build-first for 2 and up (beginners learn more from worked examples; past that
  they get in the way).
- **Try something else** when there is no plan and a format has fewer than 2 sessions (rotate
  through them), or when the plan names a "Try next" format and the last 3 sessions all used
  the default. Say it in one line: "trying worked examples today to see what sticks".

**The session:**
1. **Pretest:** 2-3 quick questions on the module before teaching anything. Trying first
   helps even when they get it wrong. 3/3 right → tick it and move on.
2. **Teach in the chosen format.** Use examples from their own projects and interests
   (`projects/`, `hobbies/`). Run code yourself first.
3. **Let them try.** When stuck, climb the hint ladder one rung at a time, and count the rungs:
   a question that nudges → point at the exact spot → one worked step. Never the whole answer.
4. **Redo without help.** Once it works, they go back to the start and do the whole task
   alone. This is where the learning happens; don't skip it.
5. **Explain-back:** in 3-5 plain sentences with one example of their own. Grade it against
   the source, name what's missing, and save it (see below).
6. **Mastery check:** 5 questions they haven't seen, mixed in with a neighbouring module.
   **Tick the module only after an unaided redo and 4/5.** Otherwise it stays open; a module
   can take several sessions.

## quiz: make them produce
- **Socratic:** why and what-if questions until they find the gap themselves. Never hand
  over the answer.
- **Examiner:** one question at a time, each harder, until they miss twice. That's their
  level. Prefer "what does this do?" and "find the bug" over definitions.
- **Explain-back:** they explain it in their own words (typed, spoken or drawn); grade it
  against the source and name what's missing or wrong.
- **Checker:** they show their work; check the steps, not just the answer, and point to a
  shorter path. Don't rewrite it.

Ask "sure or guessing?" before you grade. Correct in 1-2 lines with a tiny example.

## diagnose: find the root
When mistakes repeat, read `learning/mistakes.md`, every `sessions.md`, and the `missed:`
lines in `knowledge/` logs. Name the **one** misunderstanding behind them ("you keep
assuming X because you don't yet have Z"), write it in the root-cause column, then teach Z.

## spar: timed real-world practice
Scenario-based testing that pushes beyond memorization. Present realistic real-world dilemmas,
broken code to troubleshoot, system architecture trade-offs, or tough counterarguments:
- Play an active counterpart (interviewer, skeptical client, senior architect, or examiner).
- Give concrete scenarios with constraints and competing priorities, not trivia questions.
- Ask one targeted question or dilemma at a time with a realistic response expectation.
- Push back forcefully on vague, surface-level, or generic answers. Demand specific mechanics.
- At the end of the round, give a score (1-5), identify the root reasoning gap, and provide 2-3 actionable fixes. Raise difficulty in the next round.

## Save every session
- Append to `learning/<topic>/sessions.md`, always with the format (for quiz, spar and
  diagnose, the mode is enough):
  ```markdown
  ## YYYY-MM-DD · teach · worked
  - Module: spread · Pretest: 1/3 · Hints: 2 · Redid without help: yes · Mastery: 4/5
  - Produced: … · Missed: …
  ```
- Each miss: one row in `learning/mistakes.md`. Start the root-cause cell with its type:
  `slip:` (knew it, careless), `misconception:` (believed something wrong) or
  `prereq <module>:` (a missing earlier idea). A `prereq` miss marks that module `(review)`
  in `map.md` and unticks it.
- Cards for what they learned, following "Writing cards" in `recall.md`, each through the
  script so the brain knows which format made it (write `knowledge/<topic>.md` first if it's new):
  ```sh
  python3 "<this skill's dir>/srs.py" add . <topic> "<question>" --answer "<short answer>" --via learn:<format>
  ```
- Their explain-back goes under `## In my words` in `knowledge/<topic>.md`:
  `- YYYY-MM-DD: "<what they said>" (missed: …)`. Later sessions ask for it again from scratch.
- What they now understand goes into `knowledge/<topic>.md` (shape in `/mindtix capture`):
  the code they built, why it works, connections. Add a `## Log` line:
  `- YYYY-MM-DD learn <mode>: score 3/5, missed: …`.
- Don't edit `insight/`. If their level clearly moved, suggest `/mindtix reflect`.

Keep the pace quick. If they're bored, move faster. Don't do the struggle for them.
