# Learning

The learning design draws on Nick Saraev's video
[How I Learn Complex Skills & Difficult Subjects So Fast with AI](https://www.youtube.com/watch?v=FSXHk4hMrY8),
plus standard memory research. This is our summary, adapted to mindtix.

## The core idea: produce, don't consume

Reading, watching and having something explained all *feel* like learning, but memory forms
when you **produce**: recall from memory, predict, explain in your own words, or do the thing.
Re-reading looks good on a test five minutes later and falls apart a week later; testing
yourself holds up. So the AI's main job is to make you produce, not to explain more.

## Ten roles for the AI

| Role | When | What it does in mindtix |
|---|---|---|
| Interviewer | Starting out | Asks your goal, deadline, current level and how you'll be tested, until the goal is specific. |
| Mapmaker | The subject feels shapeless | Breaks it into modules, with prerequisites and the usual sticking points → `learning/<topic>/map.md` |
| Explainer | You're stuck | Explains only the part you're stuck on, at your level. Then you **redo the whole task without help**. |
| Socratic questioner | You think you understand | Asks why and what-if questions until you find the gap yourself. Never hands over the answer. |
| Examiner | You've covered a topic | One question at a time, each harder, until you miss. That's your level. |
| Checker | You made something | Grades your process, not just the answer, and points to a shorter path. Doesn't rewrite your work. |
| Listener | You can explain it | You explain it back (spoken, drawn, written); it grades you against the source and names what you missed. |
| Diagnostician | Mistakes repeat | Reads `learning/mistakes.md` and past sessions and names the one root misunderstanding behind them. |
| Sparring partner | It's a real-world skill | Timed role-play (interviews, sales calls, live coding) with adjustable difficulty. |
| Clerk | Notes are messy | Turns your notes into clean pages and cards. Adds nothing you didn't write. |

## Rules the workflows follow

1. **Redo without help.** After any explanation, go back to the start of the task and do it
   alone. It takes about 10-15% more time and is where the learning happens.
2. **Spaced repetition.** Cards come back just before you'd forget them. The scheduler is
   [FSRS](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm), the one Anki
   uses: each card keeps a stability (days until recall drops to 90%) and a difficulty, so easy
   cards drift out to months and hard ones stay close. You say whether you were sure before the
   grade; a confident wrong answer is the one most worth fixing, so it comes back the same round.
3. **Stay just above your level.** Difficulty follows the topic level in
   `insight/knowledge.md`: hard enough to struggle, not so hard you guess.
4. **Explain it at several levels.** If you can explain a topic to a child and to an expert,
   you know it.
5. **Use the best human explanations.** The AI finds the explanation that fits your exact
   level and links it, instead of writing a weaker one.
6. **Fix the root, not the symptom.** Repeated mistakes usually share one missing idea.

## How mindtix learns how you learn

"Learning styles" (visual, auditory, …) don't hold up in studies: teaching to a stated style
doesn't help. What does differ between people is which *methods* work for them on which
material, and that can be measured. So mindtix treats "how I like to learn" as a first guess
and then watches what actually happens:

- **Every session is labelled** with one of four formats: `worked` (faded worked examples),
  `build` (build first), `socratic` (questions only) and `explain` (short explanation, then
  practice). Each records the pretest, the hints you needed, whether you redid it alone, and a
  mastery check on questions you hadn't seen.
- **Every card remembers how it was made** (`srs.py add --via learn:worked`), and every review
  goes into `learning/reviews.csv` with your confidence. Whether a card survives its first
  review a few days later is the honest signal of which format worked.
- **Every mistake gets a type:** a slip, a misconception, or a missing prerequisite. Each
  needs a different fix.
- `/mindtix reflect` turns this into `insight/learning.md`: what works for you, with the
  numbers; how well your confidence matches your answers; your mix of mistakes; and a
  **Teaching plan**. `/mindtix learn` follows that plan, and still tries another format about
  one session in four, so it keeps checking and doesn't lock into an early guess.

Two defaults hold until there's evidence: beginners (level 0-1) get worked examples, because
solving from scratch overloads them, and people with some footing (2+) build first, because
worked examples start to get in the way. A module is ticked only after you redo it alone and
get 4 of 5 new questions right, and the next module is one whose prerequisites are all done.

## When not to lean on AI

Learning happens in the struggle. If the AI explains every hard part straight away, you get
the feeling of understanding without the memory. Like turn-by-turn GPS, it can weaken the
skill it replaces. So the workflows ask before they tell, and make you try first.
