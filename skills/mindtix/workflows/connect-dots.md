# Connect dots

Rewrites `insight/connections.md` from scratch each run. Touches no other file.

1. **Gather** (reuse what `/mindtix reflect` just read): `INDEX.md`, `knowledge/`,
   `learning/`, the levels in `insight/knowledge.md`, `projects/`, `hobbies/`, `extra/`, `self/`,
   `raw/notes/` and `raw/writing/`.
2. **Find the lines between the dots:**
   - **Bridges:** one idea in two areas under different names (the chain rule in calculus is
     backpropagation in a neural net; meter in poetry is a syntax rule in a language).
   - **Clusters:** topics that are really one deeper skill.
   - **Leverage:** a strong area that could pull up a weak one.
   - **Missing links:** one prerequisite gap that blocks several goals at once (check
     `learning/mistakes.md` for evidence).
   - **Combinations:** concrete project ideas that use 2+ of their strengths and fit how they
     like to learn.
3. **Write to the user in the second person** ("you already explain recursion well"), never
   "I". **Every connection needs evidence.** Link both ends with `[[wikilinks]]` to notes that
   prove them, give one line on why they connect, and label anything speculative
   `[inferred]`. Prefer 5 strong connections to 20 weak ones; drop the trivial.
4. **Write `insight/connections.md`:**

   ```markdown
   # Connections
   How everything you know fits together. Rewritten by /mindtix connect-dots · Updated: YYYY-MM-DD

   ## Bridges
   - **A ↔ B:** why they're the same idea. [[a]] · [[b]]
   ## Clusters
   ## Leverage
   ## Missing links
   ## Combinations (project ideas)
   ```
   Leave out empty sections.
5. **Report** in 3-5 lines: the most useful connection and the missing link worth fixing
   next. Run alone, offer to commit as "Connect dots YYYY-MM-DD".
