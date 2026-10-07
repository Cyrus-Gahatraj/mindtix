---
name: know-me
description: Short adaptive interview that keeps learning who the user is (background, personality, goals, habits, taste, people) and updates self/ in their mindtix brain. Use when the user says "know me", "interview me", "learn about me", or when the profile has gaps.
user-invocable: false
---

# Know me

Work from the brain root (the folder with `MIND.md`); if there is none, suggest `/mindtix:init`.

1. **Find the gaps.** Read `MIND.md`, `INDEX.md` and `self/`, plus `projects/` and
   `hobbies/`. Look for:
   - blanks in "About me" in `MIND.md`, and any `## Unknown` lists
   - `[inferred]` facts that need confirming
   - `[inferred]` guesses in `insight/` worth checking (read only; never edit `insight/`)
   - anything stale (a "currently doing" from months ago)
2. **Ask 3-5 short questions in one message**, each building on what they've already said,
   never repeating one. Mix the kinds:
   - facts: skills, tools, routine, goals, where they're from
   - personality: how they decide, what drains or energizes them, what they obsess over
   - confirmations: "I guessed X [inferred]. Is that right?"
3. **Wait for the answers.** If one opens something interesting, ask one follow-up.
4. **Update the right note** in `self/` (`profile.md`, `personality.md`, `people.md`,
   `timeline.md`), or `projects/`, `hobbies/`, and the "About me" lines in `MIND.md`:
   - what they said is `[stated]`; your deductions are `[inferred]`
   - edit lines in place; delete anything they say is wrong
   - never record passwords, keys or ID numbers
   - a new note only for a genuinely new subject; add it to `INDEX.md`
5. **Show a short summary** of what changed and offer another round. If they confirmed or
   overturned a guess from `insight/`, suggest `/mindtix:reflect`.

Keep each round to a few minutes. Several small rounds beat one long interrogation.
