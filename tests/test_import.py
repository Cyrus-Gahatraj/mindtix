"""Self-check for the import converter: python3 tests/test_import.py"""
import json
import os
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "mindtix"))
from to_text import convert  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    src, out = os.path.join(tmp, "export"), os.path.join(tmp, "out")
    os.makedirs(os.path.join(src, "inbox/sam_1"))
    with open(os.path.join(src, "inbox/sam_1/message_1.html"), "w", encoding="utf-8") as f:
        f.write("<html><head><style>x{}</style></head><body><div>Sam</div><div>Sam Generated</div>"
                "<div>Contains data</div><div>Participants: Sam and Me</div>"
                "<div>Me</div><div>second</div><div>Jan 02, 2026 9:00 am</div>"
                "<div>Sam</div><div>first</div><div>Jan 01, 2026 8:00 am</div>"
                "<div>Sam</div><div>Sam liked a message</div><div>Jan 01, 2026 8:01 am</div>"
                "<script>alert(1)</script></body></html>")
    with open(os.path.join(src, "conversations.json"), "w", encoding="utf-8") as f:
        json.dump([{"title": "SQL help", "mapping": {
            "a": {"message": {"author": {"role": "user"}, "create_time": 1, "content": {"parts": ["what is a join?"]}}},
            "b": {"message": {"author": {"role": "assistant"}, "create_time": 2, "content": {"parts": ["It combines rows."]}}}}}], f)
    os.makedirs(os.path.join(src, "claude"))
    with open(os.path.join(src, "claude/conversations.json"), "w", encoding="utf-8") as f:
        json.dump([{"name": "Poem", "chat_messages": [{"sender": "human", "text": "read my poem"}]}], f)
    with open(os.path.join(src, "inbox/sam_1/message_2.json"), "w", encoding="utf-8") as f:
        json.dump({"title": "Sam", "participants": [{"name": "Sam"}],
                   "messages": [{"sender_name": "Sam", "timestamp_ms": 1700000000000, "content": "cafÃ©"}]}, f)
    open(os.path.join(src, "photo.jpg"), "wb").close()
    with open(os.path.join(src, "notes.md"), "w", encoding="utf-8") as f:
        f.write("# my note\nmy wifi password is hunter2hunter2, call +91 98450 12345 or 9845012345,\n"
                "card 4111 1111 1111 1111, key sk-abcdefghijklmnopqrstuvwxyz1234\nmet on 2026-10-07 09:00, pin is 4421\nlink https://x.com/p/?id=3740404041617868413_1234567890 ok")

    manifest = convert(src, out)
    thread = open(os.path.join(out, "inbox/sam_1/message_1.txt"), encoding="utf-8").read()
    assert "alert" not in thread and "x{}" not in thread, "scripts and styles removed"
    assert thread.index("first") < thread.index("second"), "thread is oldest first"
    assert "liked a message" not in thread, "reactions dropped"
    chat = open(os.path.join(out, "conversations/sql-help.md"), encoding="utf-8").read()
    assert "what is a join?" in chat and "It combines rows." in chat
    assert "read my poem" in open(os.path.join(out, "claude/conversations/poem.md"), encoding="utf-8").read()
    assert "café" in open(os.path.join(out, "inbox/sam_1/message_2.txt"), encoding="utf-8").read(), "Meta mojibake fixed"
    note = open(os.path.join(out, "notes.md"), encoding="utf-8").read()
    for leak in ("hunter2", "98450", "9845012345", "4111", "sk-abc", "4421"):
        assert leak not in note, f"{leak} should be masked"
    assert "2026-10-07 09:00" in note, "dates are not phone numbers"
    assert "_1234567890" in note, "IDs inside links are not phone numbers"
    assert "masked" not in manifest.lower() or "Masked: 6" in manifest, manifest
    assert not os.path.exists(os.path.join(out, "photo.jpg")) and "1 media" in manifest

    z = os.path.join(tmp, "e.zip")
    with zipfile.ZipFile(z, "w") as zf:
        zf.write(os.path.join(src, "notes.md"), "notes.md")
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "..", "skills", "mindtix", "to_text.py"), z, os.path.join(tmp, "zout")], capture_output=True, text=True)
    assert r.returncode == 0 and os.path.exists(os.path.join(tmp, "zout/notes.md")), r.stderr

print("import ok")
