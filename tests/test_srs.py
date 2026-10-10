"""Self-check for the scheduler: python3 tests/test_srs.py
The vectors at the top are shared with the site's test (site/test/site.test.mjs), so the
Python and JS schedulers can't drift apart."""
import csv
import os
import subprocess
import sys
import tempfile
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "skills", "mindtix", "srs.py")
sys.path.insert(0, os.path.dirname(SCRIPT))
from srs import grade, review  # noqa: E402

# (s, d, rating, days since last review) -> (s, d) after
assert review(None, None, 3, 0)[:2] == (3.2, 5.3), review(None, None, 3, 0)
assert review(None, None, 1, 0)[:2] == (0.4, 7.2)
assert review(7.0, 5.0, 3, 7)[:2] == (23.8, 5.0), review(7.0, 5.0, 3, 7)
assert review(7.0, 5.0, 1, 7)[:2] == (1.7, 6.6), review(7.0, 5.0, 1, 7)
for s in (0.4, 3.2, 30.0, 400.0):
    for t in (0, 1, 30, 900):
        assert review(s, 5.0, 1, t)[0] <= s, "again never raises stability"

TODAY = date(2026, 10, 10)
with tempfile.TemporaryDirectory() as brain:
    os.makedirs(os.path.join(brain, "knowledge"))
    note = os.path.join(brain, "knowledge", "graphs.md")
    with open(note, "w", encoding="utf-8", newline="") as f:
        f.write("# Graphs\r\n\r\n## Recall\r\n- Why does BFS find shortest paths?\r\n"
                "- [b2 · due 2026-10-10] What breaks without a visited set? :: it loops forever\r\n"
                "- [b0 · due 2026-10-01] Why, in a DAG, does topo order exist?\r\n"
                "- [b0 · due 2026-10-01] Why, in a DAG, can you do DP?\r\n\r\n## Log\r\n")

    assert grade(brain, "graphs", "Why does BFS", "good", sure=True, today=TODAY) == (1, date(2026, 10, 13))
    assert grade(brain, "graphs", "What breaks without a visited set?", "good", today=TODAY)[0] >= 3
    assert grade(brain, "graphs", "Why, in a DAG, does topo order exist?", "again", sure=True,
                 note="said DFS order", today=TODAY) == (0, date(2026, 10, 11))
    try:
        grade(brain, "graphs", "Why, in a DAG", "good", today=TODAY)
        raise AssertionError("an ambiguous prefix must fail")
    except LookupError:
        pass

    text = open(note, encoding="utf-8", newline="").read()
    assert "\r\n" in text and "\n" not in text.replace("\r\n", ""), "CRLF kept"
    assert "- [b1 · due 2026-10-13] Why does BFS find shortest paths? · s3.2 d5.3\r\n" in text, text
    assert "] What breaks without a visited set? :: it loops forever · s23.8 d5\r\n" in text, text

    rows = list(csv.reader(open(os.path.join(brain, "learning", "reviews.csv"), encoding="utf-8")))
    assert rows[0] == ["when", "topic", "question", "rating", "sure", "r", "s", "d", "via"]
    assert rows[1][2] == "Why does BFS find shortest paths?" and rows[1][3:] == ["good", "1", "", "3.2", "5.3", "recall"]
    assert rows[3][2] == "Why, in a DAG, does topo order exist?", "a comma in a question is quoted, not split"
    assert open(os.path.join(brain, "learning", "mistakes.md"), encoding="utf-8").read().endswith(
        "| 2026-10-10 | graphs | said DFS order | misconception: was sure |\n")

    r = subprocess.run([sys.executable, SCRIPT, "grade", brain, "graphs", "no such card", "good"],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "0 cards" in r.stdout, r.stdout
    r = subprocess.run([sys.executable, SCRIPT, "grade", brain, "graphs", "Why does BFS", "easy", "--unsure"],
                       capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout.startswith("b"), r.stdout + r.stderr

print("srs ok")
