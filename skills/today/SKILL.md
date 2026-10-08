---
name: today
description: The daily 5-10 minute session for a mindtix brain. Runs a short round of due recall cards, one small step on the topic being learned now, and one question from an older topic, so the user only has to remember one command a day. Use when the user says "today", "daily", "my daily session", "what should I do today", "5 minutes", or starts a session with no clear task and cards are due.
---

# Today

One short session, three steps. Keep it moving: if they want to stop after any step, stop
and still save. Work from the brain root (the folder with `MIND.md`); if there is none,
suggest `/mindtix:init`.

1. **Recall (about 3 minutes).** Run `/mindtix:recall`, but ask at most **5** due cards. If
   none are due, say so in one line and move on.
2. **One learning step (about 5 minutes).** Find the topic being learned now: the
   `learning/<topic>/map.md` (skip `_example`) with unchecked modules and the nearest
   deadline; if none has a deadline, the one with the newest entry in `sessions.md`. Run one
   short `/mindtix:learn teach` step on its next unchecked module: one small task, a hint only
   if they're stuck, then redo without help. A module can take several days; don't rush the
   tick. If nothing is being learned, offer `/mindtix:learn` and skip this step.
3. **One old question.** Pick one card or idea from a `knowledge/` topic that wasn't touched
   in steps 1-2 and wasn't reviewed in the last week, and ask it as a "what would happen
   if…" or "how does this connect to…" question. Grade in 1-2 lines; update the card as
   recall does if it was a card.
4. **Report in 2 lines:** what they did today, and what's waiting tomorrow (cards due
   tomorrow, the next module).

Recall and learn save their own logs, cards and mistakes. Add nothing else.
