#!/usr/bin/env python3
"""Spaced repetition for a mindtix brain: FSRS-5 with its default weights, standard library only.

    python3 srs.py grade <brain> <topic> "<question or a unique start of it>" again|hard|good|easy
                         [--sure | --unsure] [--note "what they said"] [--via recall|today|learn]

A card is one line in the `## Recall` section of knowledge/<topic>.md:

    - [b1 · due 2026-10-13] Why does BFS find shortest paths? :: expands in distance order · s3.2 d5.3

`s` is stability (days until recall drops to 90%), `d` difficulty (1-10). The box is derived from
s so older readers keep working. Cards without s/d are migrated on their next grade. Each grade
rewrites the line in place, appends a row to learning/reviews.csv, and a miss adds a row to
learning/mistakes.md. Prints the new `b1 · due 2026-10-13`; exits 1 if the card isn't found once.

Writes go through Bash, so the editor's secret guard never sees them; the auto-commit hook's
secret scan still does. Card text is the user's own question, so this is low-risk.
"""
import csv
import math
import os
import sys
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from export import CARD  # noqa: E402  (one card regex for every Python script)

W = (0.40255, 1.18385, 3.173, 15.69105, 7.1949, 0.5345, 1.4604, 0.0046, 1.54575, 0.1192,
     1.01925, 1.9395, 0.11, 0.29605, 2.2698, 0.2315, 2.9898, 0.51655, 0.6621)
INTERVALS = (1, 3, 7, 14, 30, 90)  # the old Leitner boxes, kept as labels
RATINGS = ("again", "hard", "good", "easy")
MAX_S = 36500


def retrievability(t, s):
    return (1 + 19 / 81 * t / s) ** -0.5


def interval(s):
    """Days to the next review at 90% target retention, which is just s."""
    return max(1, math.floor(s + 0.5))


def box(s):
    return max([i for i, n in enumerate(INTERVALS) if n <= s] or [0])


def _d0(g):
    return min(10, max(1, W[4] - math.exp(W[5] * (g - 1)) + 1))


def review(s, d, g, t):
    """FSRS-5 step. s, d: state before (None = new card); g: 1-4; t: days since the last review.
    Returns (s, d, r) after, r being the recall chance at review time (None for a new card)."""
    if s is None:
        return round(W[g - 1], 1), round(_d0(g), 1), None
    r = retrievability(max(0, t), s)
    if g == 1:
        s2 = min(s, W[11] * d ** -W[12] * ((s + 1) ** W[13] - 1) * math.exp(W[14] * (1 - r)))
    else:
        s2 = s * (1 + math.exp(W[8]) * (11 - d) * s ** -W[9] * (math.exp(W[10] * (1 - r)) - 1)
                  * (W[15] if g == 2 else 1) * (W[16] if g == 4 else 1))
    d2 = d - W[6] * (g - 3) * (10 - d) / 9
    d2 = min(10, max(1, W[7] * _d0(4) + (1 - W[7]) * d2))
    return round(min(max(s2, 0.1), MAX_S), 1), round(d2, 1), r


def state(m):
    """(s, d, last review date or None) from a CARD match. Old cards: b0 is new, bN keeps its interval."""
    b, due = int(m.group(1) or 0), m.group(2)
    if m.group(5):
        s, d = float(m.group(5)), float(m.group(6))
    elif b:
        s, d = float(INTERVALS[b]), 5.0
    else:
        return None, None, None
    return s, d, date.fromisoformat(due) - timedelta(days=interval(s))


def line(q, a, s, d, today):
    due = today + timedelta(days=interval(s))
    return f"- [b{box(s)} · due {due.isoformat()}] {q}" + (f" :: {a}" if a else "") + f" · s{s:g} d{d:g}"


def grade(brain, topic, question, rating, sure=None, note="", via="recall", today=None):
    today = today or date.today()
    path = os.path.join(brain, "knowledge", topic + ".md")
    with open(path, encoding="utf-8", newline="") as f:
        lines = f.read().split("\n")
    hits, in_recall = [], False
    for i, l in enumerate(lines):
        if l.startswith("## "):
            in_recall = l.strip().lower() == "## recall"
            continue
        m = CARD.match(l.rstrip("\r")) if in_recall else None
        if m and (m.group(3) == question or m.group(3).startswith(question)):
            hits.append((m.group(3) != question, i, m))
    exact = [h for h in hits if not h[0]]
    hits = exact or hits
    if len(hits) != 1:
        raise LookupError(f"{len(hits)} cards match {question!r} in knowledge/{topic}.md")
    _, i, m = hits[0]
    q, a = m.group(3), m.group(4)
    s, d, last = state(m)
    g = RATINGS.index(rating) + 1
    s, d, r = review(s, d, g, (today - last).days if last else 0)
    cr = "\r" if lines[i].endswith("\r") else ""
    lines[i] = line(q, a, s, d, today) + cr
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lines))

    flag = "" if sure is None else str(int(sure))
    row = [datetime.now().strftime("%Y-%m-%dT%H:%M"), topic, q, rating, flag,
           "" if r is None else f"{r:.2f}", f"{s:g}", f"{d:g}", via]
    _append_csv(os.path.join(brain, "learning", "reviews.csv"),
                ["when", "topic", "question", "rating", "sure", "r", "s", "d", "via"], row)
    if g == 1:
        cause = "misconception: was sure" if sure else ""
        _append_mistake(brain, today, topic, (note or "missed: " + q).replace("|", "/"), cause)
    return box(s), today + timedelta(days=interval(s))


def _append_csv(path, header, row):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        if new:
            w.writerow(header)
        w.writerow(row)


def _append_mistake(brain, today, topic, mistake, cause):
    path = os.path.join(brain, "learning", "mistakes.md")
    text = open(path, encoding="utf-8", newline="").read() if os.path.exists(path) else \
        "# Mistakes\n\n| Date | Topic | Mistake | Guessed root cause |\n|---|---|---|---|\n"
    eol = "\r\n" if "\r\n" in text else "\n"
    row = f"| {today.isoformat()} | {topic} | {mistake} | {cause} |"
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text.rstrip("\r\n") + eol + row + eol)


def main(argv):
    if len(argv) < 6 or argv[1] != "grade" or argv[5] not in RATINGS:
        print(__doc__)
        return 2
    _, _, brain, topic, question, rating, *rest = argv
    opts = {"sure": None, "note": "", "via": "recall"}
    while rest:
        k = rest.pop(0)
        if k in ("--sure", "--unsure"):
            opts["sure"] = k == "--sure"
        elif k in ("--note", "--via") and rest:
            opts[k[2:]] = rest.pop(0)
    try:
        b, due = grade(brain, topic, question, rating, **opts)
    except (LookupError, OSError) as e:
        print(e)
        return 1
    print(f"b{b} · due {due.isoformat()}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv))
