---
name: reflect
description: Reread everything in a mindtix brain and rewrite insight/, the AI's evidence-based read of the user; knowledge levels per topic (which pitch the difficulty of /mindtix:learn), mind, habits, writing style, and connections (via /mindtix:connect-dots). Also runs personality tests on request. Use when the user says "reflect", "insight", "analyze me", "what do you think of me", "rate my knowledge", "run a personality test", or after a lot of new content.
argument-hint: "[test name]"
---

# Reflect

If an argument names a personality test, run that test: $ARGUMENTS

`insight/` is written **only** by this skill and `connect-dots`. Each run rereads everything
and rewrites `insight/` from that evidence, so it reflects all of it, not just the latest bit.

1. **Gather everything.** Start from `MIND.md` and `INDEX.md`, then read every folder except
   `private/`: `self/`, `knowledge/`, `learning/` (maps, sessions, `mistakes.md`), `projects/`,
   `hobbies/`, `raw/` (their own notes and writing are the most direct evidence of how they
   think), `logs/` (the questions they ask: what they wonder and worry about), and the current
   `insight/`. Read `git log --stat` for rhythm and hours. Read anything outside the brain
   only with permission.
2. **Rewrite each file:**
   - `insight/knowledge.md`: a table `| Topic | Level | Evidence | Updated |` with levels
     0 never touched · 1 heard of it · 2 can follow along · 3 can build with it · 4 can teach
     it · 5 expert. Every level needs evidence (a project, a quiz score from `learning/`, a
     note). `/mindtix:learn` uses these levels to pitch difficulty.
   - `insight/mind.md`: how they think and how mature they are, each point with evidence and
     a confidence level (low, medium, high). Any IQ range only at medium confidence or above,
     always called a guess, never a test result.
   - `insight/habits.md`: good and bad habits, each with evidence.
   - `insight/writing-style.md`: only if `raw/writing/` or long notes exist. Voice, themes,
     images, strengths and weaknesses, with short quotes as proof.
   - `insight/scores.json`: keep `iq` in sync with `mind.md`, bump `updated`, and check it
     parses (`python3 -m json.tool insight/scores.json`). Change test results only when a
     test is (re)taken.
3. **Connect the dots:** run `/mindtix:connect-dots` on the same evidence.
4. **Be honest, not flattering.** Name bad habits plainly, without moralizing. Everything is
   `[inferred]` unless they stated it. Remove claims the evidence no longer supports.
5. **Report** in under 15 lines: what changed, the most surprising pattern, and the one
   question that would raise confidence most. Ask it. Offer to commit as
   "Reflect YYYY-MM-DD: <what changed>".

**Personality tests** (on request): Big Five (Mini-IPIP, 20 items), MBTI-style axes, Grit
(8 items), Holland RIASEC. Ask one item at a time on a 1-5 scale, store the raw answers and
scores in `scores.json`, and label the results self-report.

Never store secrets or ID numbers. Add a new insight file (e.g. `values.md`) only when there
is real evidence for it.
