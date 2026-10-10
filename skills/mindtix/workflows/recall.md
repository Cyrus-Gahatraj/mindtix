# Recall

Limit to this topic if given: $ARGUMENTS

Cards live in the `## Recall` section of each `knowledge/*.md` page, one per line:

```markdown
- [b1 · due 2026-10-13] Why does BFS find the shortest path in an unweighted graph? :: it expands in distance order · s3.2 d5.3
```

`:: answer` is a short reference answer; `s` (stability, days) and `d` (difficulty, 1-10) are
the card's memory state, kept by `<this skill's dir>/srs.py` (FSRS). The box `b0`-`b5` follows
from `s`. Never edit the state or due date by hand; grade through the script.

1. **Collect due cards:** every card whose due date is today or earlier. Skip the template
   examples (`knowledge/_example*.md`). If `knowledge/` has
   no cards, suggest `/mindtix capture` (from their notes) or `/mindtix learn`, then stop.
   Cards written without a box (plain `- question`) count as new and due now.
2. **Pick up to 10**, lowest box first, then oldest due date, at most 3 per topic, and weaker
   topics (lower level in `insight/knowledge.md`) first. If they named a topic, use only it.
   **Interleave:** never two in a row from the same topic, and put easily confused topics
   next to each other.
3. **Ask one at a time.** They answer from memory, no peeking, then say **sure or guessing**
   before you grade. Prefer "what does this do?", predictions and short explanations over
   definitions.
4. **Grade in 1-2 lines**, against the `:: answer` and the page, with a tiny example when
   they're wrong. No lectures; for more, that's `/mindtix learn`. Pick the rating:
   - `again`: wrong or blank
   - `hard`: right, but with a hint or a guess
   - `good`: right
   - `easy`: instant, sure, and trivially so
5. **Record it** (from the brain root):
   ```sh
   python3 "<this skill's dir>/srs.py" grade . <topic> "<question, or its unique start>" <rating> --sure|--unsure [--note "<what they got wrong>"]
   ```
   It rewrites the card, appends to `learning/reviews.csv`, and on `again` adds a row to
   `learning/mistakes.md` (with `--note` as the mistake). If it says 0 or 2+ cards match,
   pass more of the question.
6. **Hypercorrection:** a card they got wrong while **sure** is the one most worth fixing.
   Ask it once more at the end of the round (don't grade it twice), and say in one line why
   their answer felt right.
7. **Log** one line per topic in its `## Log`: `- YYYY-MM-DD recall: 3/4, missed: <question>`.
8. **Report** in 2-3 lines: the score, the weakest topic, how many cards are due tomorrow.
   If the same kind of mistake shows up 3+ times in `mistakes.md`, suggest
   `/mindtix learn diagnose`. Don't edit `insight/`.

## Writing cards

Every workflow that makes cards follows these rules (from Andy Matuschak's and Piotr
Wozniak's guides):

- **Understand first.** Only card what they've already worked through.
- **One idea per card**, with one answer that's the same every time.
- **No yes/no questions**, and no cues in the question that give the answer away.
- **3-5 angles per concept:** cause, contrast with a neighbour, an example, an application,
  what breaks without it.
- **At most 10 new cards per pass.** Card what would take more than a few minutes to look up
  again; skip trivia.
- **Always a short answer** (12 words or fewer) after ` :: `.
- A new card is `- [b0 · due <tomorrow>] <question> :: <answer>`; the script adds the state on
  its first grade.
