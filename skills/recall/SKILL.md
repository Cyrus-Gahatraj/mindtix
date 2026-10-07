---
name: recall
description: Spaced-repetition review for a mindtix brain. Asks the recall cards that are due across knowledge/ pages, one at a time, moves each card between Leitner boxes and logs the score. Use when the user says "recall", "quiz me" (with no topic), "review my cards", "test me", "what's due", or when /mindtix:review offers a round.
argument-hint: "[topic]"
---

# Recall

Limit to this topic if given: $ARGUMENTS

Cards live in the `## Recall` section of each `knowledge/*.md` page, one per line:

```markdown
- [b2 · due 2026-10-14] Why does BFS find the shortest path in an unweighted graph?
```

Boxes and the days until the next review: **b0** 1 · **b1** 3 · **b2** 7 · **b3** 14 ·
**b4** 30 · **b5** 90.

1. **Collect due cards:** every card whose due date is today or earlier. If `knowledge/` has
   no cards, suggest `/mindtix:capture` (from their notes) or `/mindtix:learn`, then stop.
   Cards written without a box (plain `- question`) count as b0 and due now.
2. **Pick up to 10**, lowest box first, then oldest due date, at most 3 per topic, and weaker
   topics (lower level in `insight/knowledge.md`) first. If they named a topic, use only it.
3. **Ask one at a time.** They answer from memory, no peeking. Prefer "what does this do?",
   predictions and short explanations over definitions.
4. **Grade in 1-2 lines**, with a tiny example when they're wrong. No lectures; for more,
   that's `/mindtix:learn`.
5. **Update the card in place:**
   - right → one box up (max b5), due = today + that box's interval
   - wrong → b0, due tomorrow, and a row in `learning/mistakes.md`
     (`| date | topic | the mistake | |`)
6. **Log** one line per topic in its `## Log`: `- YYYY-MM-DD recall: 3/4, missed: <question>`.
7. **Report** in 2-3 lines: the score, the weakest topic, how many cards are due tomorrow.
   If the same kind of mistake shows up 3+ times in `mistakes.md`, suggest
   `/mindtix:learn diagnose`. Don't edit `insight/`.
