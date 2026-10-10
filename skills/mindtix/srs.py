#!/usr/bin/env python3
"""Spaced repetition for a mindtix brain: FSRS-5 with its default weights, standard library only.

    python3 srs.py grade <brain> <topic> "<question or a unique start of it>" again|hard|good|easy
                         [--sure | --unsure] [--note "what they said"] [--via recall|today|learn]
                         [--cause "slip: … | misconception: … | prereq <module>: …"]
    python3 srs.py add   <brain> <topic> "<question>" [--answer "<short answer>"] [--via capture|learn:<format>]
    python3 srs.py stats <brain> [--days N]

A card is one line in the `## Recall` section of knowledge/<topic>.md:

    - [b1 · due 2026-10-13] Why does BFS find shortest paths? :: expands in distance order · s3.2 d5.3

`s` is stability (days until recall drops to 90%), `d` difficulty (1-10). The box is derived from
s so older readers keep working. Cards without s/d are migrated on their next grade. Each grade
rewrites the line in place, appends a row to learning/reviews.csv, and a miss adds a row to
learning/mistakes.md. Prints the new `b1 · due 2026-10-13`; exits 1 if the card isn't found once.

`add` puts a new card at the end of `## Recall` (made if missing) and logs how it was made, so
`stats` can tell which way of learning sticks for this user. It refuses yes/no questions, ones
over 160 characters and duplicates (exit 1). `stats` prints markdown tables from reviews.csv:
pass rate vs predicted recall, calibration (right when sure vs not), first-review retention by
how the card was made, topics, and leeches. `/mindtix reflect` turns them into insight/learning.md.

Writes go through Bash, so the editor's secret guard never sees them; the auto-commit hook's
secret scan still does. Card text is the user's own question, so this is low-risk.
"""
import csv
import math
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from export import CARD  # noqa: E402  (one card regex for every Python script)

W = (0.40255, 1.18385, 3.173, 15.69105, 7.1949, 0.5345, 1.4604, 0.0046, 1.54575, 0.1192,
     1.01925, 1.9395, 0.11, 0.29605, 2.2698, 0.2315, 2.9898, 0.51655, 0.6621)
INTERVALS = (1, 3, 7, 14, 30, 90)  # the old Leitner boxes, kept as labels
RATINGS = ("again", "hard", "good", "easy")
HEADER = ["when", "topic", "question", "rating", "sure", "r", "s", "d", "via"]
YES_NO = re.compile(r"(is|are|was|were|does|do|did|can|could|should|will|would|has|have)\b", re.I)
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


def grade(brain, topic, question, rating, sure=None, note="", via="recall", cause="", today=None):
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
    _append_csv(os.path.join(brain, "learning", "reviews.csv"), HEADER, row)
    if g == 1:
        cause = (cause or ("misconception: was sure" if sure else "")).replace("|", "/")
        _append_mistake(brain, today, topic, (note or "missed: " + q).replace("|", "/"), cause)
    return box(s), today + timedelta(days=interval(s))


def add(brain, topic, question, answer="", via="capture", today=None):
    """Append a new card to knowledge/<topic>.md's ## Recall, due tomorrow, and log its creation."""
    today = today or date.today()
    question, answer = " ".join(question.split()), " ".join(answer.split())
    if YES_NO.match(question):
        raise ValueError("yes/no question: ask for the answer itself (why, what, how, which)")
    if len(question) > 160:
        raise ValueError("over 160 characters: split it into focused cards")
    path = os.path.join(brain, "knowledge", topic + ".md")
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(eol)
    start = next((i for i, l in enumerate(lines) if l.strip().lower() == "## recall"), None)
    if start is not None:
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith(("## ", "Sources:"))), len(lines))
        if any((m := CARD.match(l)) and m.group(3) == question for l in lines[start + 1:end]):
            raise ValueError("already a card on this page")
        while end > start + 1 and not lines[end - 1].strip():
            end -= 1
        new = [None]
    else:  # a new section before ## Log, else before the Sources: line, else at the end
        end = next((i for i, l in enumerate(lines) if l.strip().lower() == "## log"), None)
        if end is None:
            end = next((i for i, l in enumerate(lines) if l.startswith("Sources:")), len(lines))
            while end > 0 and not lines[end - 1].strip():
                end -= 1
        new = ["## Recall", None] + ([""] if end < len(lines) and lines[end].strip() else [])
        if end and lines[end - 1].strip():
            new.insert(0, "")
    card = f"- [b0 · due {(today + timedelta(days=1)).isoformat()}] {question}" + (f" :: {answer}" if answer else "")
    lines[end:end] = [card if x is None else x for x in new]
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(eol.join(lines))
    _append_csv(os.path.join(brain, "learning", "reviews.csv"), HEADER,
                [datetime.now().strftime("%Y-%m-%dT%H:%M"), topic, question, "", "", "", "", "", via])
    return card


def stats(brain, days=None, today=None):
    """Markdown tables from learning/reviews.csv; `days` limits the graded rows to the last N days."""
    today = today or date.today()
    path = os.path.join(brain, "learning", "reviews.csv")
    rows = list(csv.DictReader(open(path, encoding="utf-8", newline=""))) if os.path.exists(path) else []
    made = {}
    for r in rows:
        if not r["rating"]:
            made.setdefault((r["topic"], r["question"]), r["via"])
    since = (today - timedelta(days=days)).isoformat() if days else ""
    graded = [r for r in rows if r["rating"] and r["when"][:10] >= since]
    ok = lambda rs: sum(r["rating"] != "again" for r in rs)  # noqa: E731
    pct = lambda a, n: f"{100 * a / n:.0f}%" if n else "-"  # noqa: E731
    if not graded:
        return "No reviews yet" + (f" in the last {days} days." if days else ".")

    rs = [float(r["r"]) for r in graded if r["r"]]
    out = [f"## Reviews{f' (last {days} days)' if days else ''}", "",
           "| Reviews | Right | Predicted |", "|---|---|---|",
           f"| {len(graded)} | {pct(ok(graded), len(graded))} | {pct(sum(rs), len(rs))} |", "",
           "## Calibration", "", "| | Reviews | Right |", "|---|---|---|"]
    for label, flag in (("Sure", "1"), ("Not sure", "0")):
        g = [r for r in graded if r["sure"] == flag]
        out.append(f"| {label} | {len(g)} | {pct(ok(g), len(g))} |")

    first = {}
    for r in graded:
        first.setdefault((r["topic"], r["question"]), r)
    by_via = defaultdict(list)
    for key, via in made.items():
        if key in first:
            by_via[via].append(first[key])
    if by_via:
        out += ["", "## First review by how the card was made", "", "| Made by | Cards | Right |", "|---|---|---|"]
        out += [f"| {v} | {len(g)} | {pct(ok(g), len(g))} |" for v, g in sorted(by_via.items())]

    by_topic = defaultdict(list)
    for r in graded:
        by_topic[r["topic"]].append(r)
    out += ["", "## Topics", "", "| Topic | Reviews | Right | Lapses |", "|---|---|---|---|"]
    out += [f"| {t} | {len(g)} | {pct(ok(g), len(g))} | {len(g) - ok(g)} |" for t, g in sorted(by_topic.items())]

    misses = Counter((r["topic"], r["question"]) for r in rows if r["rating"] == "again")
    leeches = [f"- {t}: {q} ({n} misses)" for (t, q), n in misses.most_common() if n >= 4]
    if leeches:
        out += ["", "## Leeches (rewrite or split these)", ""] + leeches
    return "\n".join(out)


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
    cmd, args = (argv[1], argv[2:]) if len(argv) > 1 else ("", [])
    pos = [a for i, a in enumerate(args) if not a.startswith("--") and not (i and args[i - 1] in ("--note", "--via", "--cause", "--answer", "--days"))]
    opt = lambda k: args[args.index(k) + 1] if k in args[:-1] else None  # noqa: E731
    try:
        if cmd == "grade" and len(pos) == 4 and pos[3] in RATINGS:
            sure = True if "--sure" in args else False if "--unsure" in args else None
            b, due = grade(*pos, sure=sure, note=opt("--note") or "", via=opt("--via") or "recall",
                           cause=opt("--cause") or "")
            print(f"b{b} · due {due.isoformat()}")
        elif cmd == "add" and len(pos) == 3:
            print(add(*pos, answer=opt("--answer") or "", via=opt("--via") or "capture"))
        elif cmd == "stats" and len(pos) == 1:
            print(stats(pos[0], int(opt("--days") or 0) or None))
        else:
            print(__doc__)
            return 2
    except (LookupError, ValueError, OSError) as e:
        print(e)
        return 1
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv))
