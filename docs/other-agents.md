# Using mindtix outside Claude Code

The skill follows the open [Agent Skills](https://agentskills.io) format (`SKILL.md`), so it
runs in any agent that supports it. The brain itself is plain markdown, so any agent can read it.

## Install

```sh
git clone https://github.com/Cyrus-Gahatraj/mindtix
python3 mindtix/install.py                    # global: ~/.agents/skills (+ ~/.gemini/skills)
python3 mindtix/install.py --project ~/mind   # only inside one brain: ~/mind/.agents/skills
```

| Agent | Reads skills from | Use |
|---|---|---|
| Claude Code | the plugin | `/plugin install mindtix@mindtix` (not this script) |
| Codex CLI | `~/.agents/skills`, `<repo>/.agents/skills` | `install.py` or `--project` |
| opencode | `~/.agents/skills`, `~/.config/opencode/skills`, `<project>/.agents/skills` | `install.py` or `--project` |
| Gemini CLI | `~/.gemini/skills`, `<project>/.agents/skills` | `install.py` (adds `~/.gemini/skills` if it exists) |
| Cursor | `<project>/.agents/skills`, `.cursor/skills` | `install.py --project <brain>` |
| Anything else with Agent Skills | its skills folder | `install.py --to <folder>` |

It installs one skill, `mindtix`, that holds every workflow (and removes the `mindtix-<name>`
skills older versions installed). Update by pulling the repo and running the script again; remove
with `--uninstall` (same target options). Only mindtix folders are touched.

## Use

Open your agent in an empty folder and say "set up mindtix". After that, just talk:
"import ~/Downloads/instagram.zip", "save this", "teach me SQL", "quiz me on SQL",
"what's due?", "reflect on me", "weekly review", "export my profile".

Every brain has `AGENTS.md` and `GEMINI.md` that point the agent to `MIND.md`, so the rules
load in Codex, opencode, Cursor and Gemini CLI the way `CLAUDE.md` does in Claude Code.

## What's different from Claude Code

| | Claude Code | Other agents |
|---|---|---|
| Starting a workflow | `/mindtix learn quiz sql` | say it, or call the `mindtix` skill |
| Big imports | parallel `reader` agents | read batch by batch, writing facts to a scratch file in between |
| Secret guard and `raw/` guard | enforced by hooks | the skill's rules; imports are still masked by the converter |
| Due-cards reminder | at session start | ask "what's due?" |

Requires Python 3 for `init`, `import` and `export`.
