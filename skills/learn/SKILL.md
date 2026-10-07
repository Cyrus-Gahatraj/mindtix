---
name: learn
description: Teach the user a topic and make it stick, by making them produce (recall, predict, explain, build) instead of only reading. Modes; start (interview and map a new topic), teach (build first, explain only the stuck part, then redo without help), quiz (Socratic, examiner, explain-back, check their work), diagnose (root of repeated mistakes) and spar (timed role-play for real-world skills). Use when the user says "learn", "teach me", "explain X", "quiz me on X", "check my work", "why do I keep getting this wrong", "spar", "mock interview", or wants to understand a concept, language, tool or paper.
user-invocable: false
---

# Learn

Memory forms when you **produce**: recall, predict, explain, build. Explanations only feel
like learning. So ask before telling, make the user try first, and explain only the part
they're stuck on. Method: `docs/learning.md` in the mindtix repo.

Work from the brain root (the folder with `MIND.md`); if there is none, suggest
`/mindtix:init`. **Before any mode**, read: how they like to learn in `MIND.md`, their level
in `insight/knowledge.md`, `learning/<topic>/` if it exists, `knowledge/<topic>.md`, and
`raw/notes/` on the topic. Pitch everything just above their level: hard enough to
struggle, not so hard they guess.

Pick the mode from what they say. If unclear: no `learning/<topic>/` yet → **start**;
otherwise **teach** the next unchecked module.

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
4. Go straight into **teach** for module 1.

## teach: build first
1. **Build first.** The smallest runnable thing (or concrete exercise) that shows the idea,
   plus a tiny task to change it. Run code yourself first. Use examples from their own
   projects and interests (`projects/`, `hobbies/`).
2. **Let them try.** When stuck, explain **only that part**, at their level, a hint before
   the answer. Offer it at two levels (beginner, expert) if it helps.
3. **Redo without help.** Once it works, they go back to the start and do the whole task
   alone. This is where the learning happens; don't skip it.
4. **Theory last**, in short chunks tied to what they built, each ending with 1-2 questions
   answered from memory.
5. Tick the module in `map.md` once they can redo it unaided.

## quiz: make them produce
- **Socratic:** why and what-if questions until they find the gap themselves. Never hand
  over the answer.
- **Examiner:** one question at a time, each harder, until they miss twice. That's their
  level. Prefer "what does this do?" and "find the bug" over definitions.
- **Explain-back:** they explain it in their own words (typed, spoken or drawn); grade it
  against the source and name what's missing or wrong.
- **Checker:** they show their work; check the steps, not just the answer, and point to a
  shorter path. Don't rewrite it.

Correct in 1-2 lines with a tiny example.

## diagnose: find the root
When mistakes repeat, read `learning/mistakes.md`, every `sessions.md`, and the `missed:`
lines in `knowledge/` logs. Name the **one** misunderstanding behind them ("you keep
assuming X because you don't yet have Z"), write it in the root-cause column, then teach Z.

## spar: timed real-world practice
Interviews, live coding, presentations, sales calls, exams. Play a tough counterpart, one
question at a time, with a time limit (30-60 s per answer, or what the real thing allows).
Push back on vague answers. Score at the end, name 2-3 fixes, raise the difficulty next round.

## Save every session
- Append to `learning/<topic>/sessions.md`:
  ```markdown
  ## YYYY-MM-DD · <mode>
  - Task: … · Produced: … · Score: 3/5 · Redid without help: yes
  - Missed: …
  ```
- Each miss: one row in `learning/mistakes.md` (date, topic, mistake, guessed root cause), and
  a card in `knowledge/<topic>.md` `## Recall`: `- [b0 · due <tomorrow>] <question>`.
- What they now understand goes into `knowledge/<topic>.md` (shape in `/mindtix:capture`):
  the code they built, why it works, connections. Add a `## Log` line:
  `- YYYY-MM-DD learn <mode>: score 3/5, missed: …`.
- Don't edit `insight/`. If their level clearly moved, suggest `/mindtix:reflect`.

Keep the pace quick. If they're bored, move faster. Don't do the struggle for them.
