#!/usr/bin/env python3
"""Heuristic auto-score for live peer dogfood results (braintrust-style)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def score_contract(text: str) -> tuple[int, list[str]]:
    score = 0
    hits: list[str] = []
    t = text or ""
    if not t.strip() or t.startswith("SKIPPED"):
        return 0, ["empty"]

    if re.search(r"\bT2\b", t) and re.search(r"\bT3\b", t):
        score += 1
        hits.append("Q1")
    elif re.search(r"T2 or T3|minimum.*T2|T2/T3", t, re.I):
        score += 1
        hits.append("Q1")

    if re.search(r"no|never|not|do not", t, re.I) and re.search(
        r"sleep|wait|60|unconditional|bots? (not |un)configured|empty", t, re.I
    ):
        score += 1
        hits.append("Q2")

    if re.search(r"no|not|never|do not", t, re.I) and re.search(
        r"review-pr|pr-review-toolkit", t, re.I
    ):
        if re.search(r"sequential|pass file|T2|clawpatch|quality-gate-codex|adapter", t, re.I):
            score += 1
            hits.append("Q3")

    if re.search(r"T3|parallel|pr-review-toolkit|/review-pr", t, re.I):
        score += 1
        hits.append("Q4")

    if re.search(r"checked|checklist|none_found", t, re.I):
        score += 1
        hits.append("Q5")

    if re.search(r"\bno\b", t, re.I) and re.search(r"T1|Incomplete", t, re.I):
        score += 1
        hits.append("Q6")

    if re.search(r"ship-loop", t, re.I):
        score += 1
        hits.append("Q7")

    ids = [
        "code-correctness",
        "silent-failures",
        "tests",
        "types",
        "comments",
        "simplify",
    ]
    if sum(1 for i in ids if i in t) >= 4 or re.search(r"six|6 pass|passes/\*", t, re.I):
        score += 1
        hits.append("Q8")

    caps = 0
    for c in ("host", "bot", "agent", "clawpatch", "issue", "suite", "probe"):
        if re.search(c, t, re.I):
            caps += 1
    if caps >= 3:
        score += 1
        hits.append("Q9")

    if re.search(r"\bNOT GROUNDED\b", t):
        pass
    elif re.search(r"\bGROUNDED\b", t):
        score += 1
        hits.append("Q10")

    return score, hits


def score_mode_plan(text: str) -> tuple[int, list[str], dict]:
    """Score mode-plan fixture. Max 12 (2 pts x 6 scenarios)."""
    score = 0
    hits: list[str] = []
    detail: dict = {}
    t = text or ""
    if not t.strip() or t.startswith("SKIPPED"):
        return 0, ["empty"], {}

    # Split by scenario headers loosely
    sections = re.split(r"(?i)###\s*([A-F])\b", t)
    # sections[0] preamble, then A, body, B, body...
    by_sc: dict[str, str] = {}
    i = 1
    while i + 1 < len(sections):
        by_sc[sections[i].upper()] = sections[i + 1]
        i += 2
    if not by_sc:
        # fallback: whole text for each
        by_sc = {k: t for k in "ABCDEF"}

    def sec(letter: str) -> str:
        return by_sc.get(letter, t)

    # A: Claude local, no bots -> T3 or T2, bot_wait no, passes present
    a = sec("A")
    ok_a = 0
    if re.search(r"\bT3\b|\bT2\b", a) and not re.search(r"\bT1\b.*Pass|Pass.*\bT1\b", a, re.I):
        ok_a += 1
    if re.search(r"bot_wait:\s*no|wait.*no|no wait|bots?.*(empty|none|not configured)", a, re.I):
        ok_a += 1
    if re.search(r"pass|toolkit|review-pr|suite", a, re.I):
        ok_a += 1
    # max 2 for A
    pts_a = min(2, ok_a)
    score += pts_a
    if pts_a:
        hits.append(f"A:{pts_a}")
    detail["A"] = pts_a

    # B: Codex -> no review-pr required; T2; sequential/clawpatch; bot no
    b = sec("B")
    pts_b = 0
    if re.search(r"\bT2\b", b) and not re.search(r"require.*review-pr|must.*pr-review-toolkit", b, re.I):
        pts_b += 1
    if re.search(r"sequential|clawpatch|pass file|codex", b, re.I) and not re.search(
        r"will run /review-pr|invoke /review-pr", b, re.I
    ):
        pts_b += 1
    if re.search(r"bot_wait:\s*no|no wait|bots?.*(empty|none)", b, re.I):
        pts_b = min(2, pts_b + 0)  # already
    # penalize if plans review-pr on codex
    if re.search(r"/review-pr|pr-review-toolkit", b, re.I) and not re.search(
        r"not|no|never|do not|avoid|forbidden", b, re.I
    ):
        pts_b = max(0, pts_b - 1)
    pts_b = min(2, max(pts_b, 0))
    # bot wait
    if re.search(r"bot_wait:\s*no|no .*wait|skip.*bot", b, re.I):
        if pts_b < 2:
            pts_b = min(2, pts_b + 1)
    score += pts_b
    if pts_b:
        hits.append(f"B:{pts_b}")
    detail["B"] = pts_b

    # C: Grok single review -> Incomplete or T1 not Pass; not T3 falsely
    c = sec("C")
    pts_c = 0
    if re.search(r"Incomplete|\bT1\b|\bT2\b", c) and not re.search(
        r"gate_if_clean:\s*Pass.*T1|T1.*gate_if_clean:\s*Pass", c, re.I
    ):
        pts_c += 1
    if re.search(r"Incomplete|not.*Pass|cannot claim Pass|T1", c, re.I):
        pts_c += 1
    if re.search(r"tier:\s*T3", c, re.I) and re.search(r"single|/review", c, re.I):
        pts_c = max(0, pts_c - 1)  # overclaim
    pts_c = min(2, pts_c)
    score += pts_c
    if pts_c:
        hits.append(f"C:{pts_c}")
    detail["C"] = pts_c

    # D: OpenCode TS PR -> T2 sequential, types pass, bot no
    d = sec("D")
    pts_d = 0
    if re.search(r"\bT2\b|sequential", d, re.I):
        pts_d += 1
    if re.search(r"types|code-correctness|passes", d, re.I):
        pts_d += 1
    if re.search(r"/review-pr", d, re.I) and not re.search(r"not|no|never|do not", d, re.I):
        pts_d = max(0, pts_d - 1)
    pts_d = min(2, pts_d)
    score += pts_d
    if pts_d:
        hits.append(f"D:{pts_d}")
    detail["D"] = pts_d

    # E: Claude + devin configured -> bot wait yes
    e = sec("E")
    pts_e = 0
    if re.search(r"bot_wait:\s*yes|wait.*60|wait for (devin|bot)", e, re.I):
        pts_e += 1
    if re.search(r"devin|external.?bot|comment", e, re.I):
        pts_e += 1
    pts_e = min(2, pts_e)
    score += pts_e
    if pts_e:
        hits.append(f"E:{pts_e}")
    detail["E"] = pts_e

    # F: agy -> T2 sequential, no toolkit
    f = sec("F")
    pts_f = 0
    if re.search(r"\bT2\b|sequential", f, re.I):
        pts_f += 1
    if re.search(r"agy|sequential|pass", f, re.I) and (
        not re.search(r"/review-pr", f, re.I)
        or re.search(r"not|no|never|do not", f, re.I)
    ):
        pts_f += 1
    pts_f = min(2, pts_f)
    score += pts_f
    if pts_f:
        hits.append(f"F:{pts_f}")
    detail["F"] = pts_f

    if re.search(r"\bGROUNDED\b", t) and not re.search(r"\bNOT GROUNDED\b", t):
        # bonus not in max 12; track only
        detail["grounded"] = True
    else:
        detail["grounded"] = False

    return score, hits, detail


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("fixture", choices=["qg-live-contract", "qg-live-mode-plan", "auto"])
    ap.add_argument("result_file")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    text = Path(args.result_file).read_text(errors="replace")
    fix = args.fixture
    if fix == "auto":
        fix = "qg-live-mode-plan" if "Scenario A" in text or "### A" in text else "qg-live-contract"

    if fix == "qg-live-contract":
        score, hits = score_contract(text)
        max_s = 10
        detail = {}
    else:
        score, hits, detail = score_mode_plan(text)
        max_s = 12

    out = {
        "score": score,
        "max": max_s,
        "hits": hits,
        "detail": detail,
        "bytes": len(text),
        "empty": not text.strip() or text.startswith("SKIPPED"),
    }
    if args.json:
        print(json.dumps(out))
    else:
        print(f"{score}/{max_s}|{','.join(hits)}|bytes={len(text)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
