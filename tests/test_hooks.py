"""Self-check for the mindtix hooks: python3 tests/test_hooks.py"""
import os
import sys
import tempfile
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hooks"))
from brain import due_cards, find_root  # noqa: E402
from guard import check  # noqa: E402

with tempfile.TemporaryDirectory() as root:
    open(os.path.join(root, "MIND.md"), "w").close()
    os.makedirs(os.path.join(root, "raw/notes"))
    os.makedirs(os.path.join(root, "knowledge"))
    note = os.path.join(root, "raw/notes/a.md")
    open(note, "w").close()

    def ev(tool, path, **inp):
        return {"tool_name": tool, "tool_input": {"file_path": path, **inp}}

    assert find_root(note) == root
    assert check(ev("Edit", note, new_string="x")), "editing raw/ must be blocked"
    assert not check(ev("Write", os.path.join(root, "raw/notes/new.md"), content="hi")), "new raw file is fine"
    assert check(ev("Write", os.path.join(root, "self/p.md"), content="api_key = abcd1234efgh")), "secret must be blocked"
    assert check(ev("Write", os.path.join(root, "self/p.md"), content="sk-" + "a" * 30))
    assert not check(ev("Write", os.path.join(root, "self/p.md"), content="I like tokens of appreciation")), "plain words pass"
    code = 'api_key = os.environ["KEY"]\ntoken = getenv("TOKEN")\npassword: <your-password>\nsecret = "your-secret-here"\nconst token = process.env.TOKEN\napi_key: ${API_KEY}'
    assert not check(ev("Write", os.path.join(root, "knowledge/jwt.md"), content=code)), "code and placeholders pass"
    assert check(ev("Write", os.path.join(root, "knowledge/jwt.md"), content='password = "Tr0ub4dor&3xyz"')), "a real-looking password is blocked"
    assert not check(ev("Edit", "/tmp/not-a-brain.md", new_string="password: hunter2hunter2")), "outside a brain: no-op"

    with open(os.path.join(root, "knowledge/t.md"), "w") as f:
        f.write("## Recall\n- [b0 · due 2000-01-01] old\n- [b2 · due 2999-01-01] future\n")
    assert due_cards(root, date(2026, 1, 1)) == 1

print("hooks ok")
