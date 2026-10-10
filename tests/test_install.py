"""Self-check for install.py: python3 tests/test_install.py"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import install  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    dest = os.path.join(tmp, "skills")
    os.makedirs(os.path.join(dest, "mindtix-learn"))  # left by a version before 1.4
    install.install(dest)
    assert sorted(os.listdir(dest)) == ["mindtix"], "one skill; the old per-workflow ones are gone"
    skill = os.path.join(dest, "mindtix")
    text = open(os.path.join(skill, "SKILL.md"), encoding="utf-8").read()
    assert "\nname: mindtix\n" in text and "argument-hint" not in text
    workflows = sorted(os.listdir(os.path.join(install.SKILL, "workflows")))
    assert sorted(os.listdir(os.path.join(skill, "workflows"))) == workflows
    for n in workflows:
        assert n[:-3] in text, f"SKILL.md lists the {n[:-3]} workflow"
    assert os.path.isfile(os.path.join(skill, "to_text.py")) and os.path.isfile(os.path.join(skill, "export.py"))
    assert os.path.isfile(os.path.join(skill, "template", "AGENTS.md"))
    imp = open(os.path.join(skill, "workflows", "import.md"), encoding="utf-8").read()
    assert "<this skill's dir>" not in imp and os.path.abspath(skill).replace(os.sep, "/") + "/to_text.py" in imp

    open(os.path.join(dest, "other-skill.md"), "w").close()
    install.install(dest, uninstall=True)
    assert os.listdir(dest) == ["other-skill.md"], "uninstall removes only mindtix"

    install.main(["--project", os.path.join(tmp, "mind")])
    assert os.path.isdir(os.path.join(tmp, "mind", ".agents", "skills", "mindtix", "workflows"))

# Only one SKILL.md, so neither Claude Code nor skills.sh sees a skill per workflow.
repo = os.path.dirname(os.path.abspath(install.__file__))
found = [os.path.relpath(os.path.join(r, f), repo) for r, ds, fs in os.walk(repo)
         if "node_modules" not in r and ".git" not in r.split(os.sep) for f in fs if f == "SKILL.md"]
assert found == [os.path.join("skills", "mindtix", "SKILL.md")], found

# Frontmatter must be strict YAML: `npx skills` (skills.sh) silently skips a skill whose
# unquoted value has ": " or " #", while Claude Code accepts it.
head = open(os.path.join(install.SKILL, "SKILL.md"), encoding="utf-8").read().split("---")[1]
for line in head.strip().splitlines():
    key, _, value = line.partition(": ")
    assert value.startswith('"') or (": " not in value and " #" not in value), f"quote or reword {key}"

print("install ok")
