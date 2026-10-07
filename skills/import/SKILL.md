---
name: import
description: Bring outside data into a mindtix brain. Converts an export (Instagram, Facebook, WhatsApp, Google Takeout, ChatGPT or Claude conversations, an Obsidian vault, any folder or .zip) into text in raw/imports/, reads all of it (with parallel reader agents when it's big) and files what it says about the user into self/, projects/, hobbies/ and knowledge/. Use when the user says "import", "import my Instagram/WhatsApp/ChatGPT data", "here is my export", or gives a path to an export or vault.
argument-hint: "<path to export folder, file or .zip> [what to focus on]"
---

# Import

Arguments: $ARGUMENTS (a path, then optionally what to focus on).

Work from the brain root (the folder with `MIND.md`); if there is none, suggest
`/mindtix:init` and stop.

## 1. Convert (never edit the original)
1. Check the path exists. Name the source from it (`instagram`, `whatsapp`, `chatgpt`,
   `claude`, `takeout`, `obsidian`, or the folder name) and the date:
   `raw/imports/<source>-YYYY-MM-DD/`.
2. Run the converter that sits next to this SKILL.md:
   `python3 "<this skill's dir>/to_text.py" "<path>" "raw/imports/<source>-YYYY-MM-DD"`
   It writes text only (HTML and JSON become text, message threads become one
   chronological file each, media is skipped), masks keys, passwords, phone and card
   numbers as `[redacted …]`, and writes a `_manifest.md` with sizes and the masked count.
   For an **Obsidian vault or notes folder**, copy the `.md` files into `raw/notes/` instead
   (keep the folder structure) and finish with `/mindtix:capture notes`.
3. Tell the user what was found: number of files, KB of text, the biggest parts, media
   skipped. `raw/imports/` is gitignored by default because exports hold other people's
   messages and personal data; the original export stays where it was.

## 2. Read all of it
- **Under ~200 KB of text:** read it yourself.
- **Bigger:** split the files into batches of roughly equal size (about 300-400 KB each,
  keeping each thread whole), and launch the `reader` agent on every batch **in parallel**
  in one message. Tell each reader who the user is (name and handles from `self/profile.md`
  and the export) and what to focus on. Put profile and personal-information files in their
  own batch first.
- Files that are mostly noise (ads, "posts viewed", likes): don't read line by line; count
  them (top accounts, hashtags, topics) with a short script and treat the counts as
  evidence of interests.
- If anything could not be read fully, say so in the final report. Never claim you read
  something you didn't.

## 3. File it
From the reports, update (merge, never duplicate; search `INDEX.md` first):
- `self/profile.md` (background, places, education, work), `self/timeline.md` (dated
  events), `self/people.md` (who each person is to the user, one line each),
  `self/personality.md` (taste, opinions, mood), with every fact `[stated]` or `[inferred]`
- `projects/`, `hobbies/`, and `knowledge/` for anything they were learning
- their own creative lines (poems, lyrics they wrote) into `raw/writing/` verbatim

Rules:
- **No secrets.** Passwords, keys, tokens, verification codes, card or bank numbers, ID
  numbers, phone numbers and emails never go into a note. If the export contains secrets
  the user pasted somewhere, tell them which kind and suggest rotating them.
- **Other people:** keep only how they relate to the user. Sensitive details about the
  user (love life, health, mood) are their call: ask once whether to keep them in normal
  notes or in `private/`.
- Don't write `insight/` (only `/mindtix:reflect`); suggest running it afterwards.

## 4. Report
Under 15 lines: what was imported, the notes created or updated, anything left out on
purpose (secrets, sensitive), contradictions worth asking about, and what wasn't read
fully. Offer to commit as "Import <source> YYYY-MM-DD".
