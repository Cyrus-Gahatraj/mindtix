"""Self-check for install.py: python3 tests/test_install.py"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import install  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    dest = os.path.join(tmp, "skills")
    names = install.install(dest)
    assert {"init", "import", "capture", "learn", "recall", "export"} <= set(names)
    for n in names:
        text = open(os.path.join(dest, "mindtix-" + n, "SKILL.md"), encoding="utf-8").read()
        assert f"\nname: mindtix-{n}\n" in text, n
        assert "$ARGUMENTS" not in text and "argument-hint" not in text and "/mindtix:" not in text, n
    for root, _, files in os.walk(dest):
        for f in files:
            if f.endswith(".md"):
                assert "/mindtix:" not in open(os.path.join(root, f), encoding="utf-8").read(), os.path.join(root, f)
    assert os.path.isfile(os.path.join(dest, "mindtix-import", "to_text.py")), "scripts are copied"
    imp = open(os.path.join(dest, "mindtix-import", "SKILL.md"), encoding="utf-8").read()
    assert "<this skill's dir>" not in imp and os.path.abspath(dest).replace(os.sep, "/") + "/mindtix-import/to_text.py" in imp
    assert os.path.isfile(os.path.join(dest, "mindtix-init", "template", "AGENTS.md"))
    assert "the `mindtix-learn` skill (diagnose)" in install.portable("run `/mindtix:learn diagnose` now")

    open(os.path.join(dest, "other-skill.md"), "w").close()
    install.install(dest, uninstall=True)
    assert os.listdir(dest) == ["other-skill.md"], "uninstall removes only mindtix skills"

    install.main(["--project", os.path.join(tmp, "mind")])
    assert os.path.isdir(os.path.join(tmp, "mind", ".agents", "skills", "mindtix-learn"))

print("install ok")
