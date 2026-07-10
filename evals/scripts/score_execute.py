#!/usr/bin/env python3
"""Score live execute dogfood against sandbox ground truth."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

GT = [
    {
        "id": "GT1",
        "patterns": [
            r"sql\s*injection",
            r"string\s*concat",
            r"user_id",
            r"SELECT.*users",
            r"inject",
            r"parameteriz",
        ],
        "file": r"user_service",
    },
    {
        "id": "GT2",
        "patterns": [
            r"empty\s*catch",
            r"bare\s*except",
            r"except\s+Exception\s*:\s*pass",
            r"swallow",
            r"silent",
            r"pass\b",
        ],
        "file": r"user_service",
    },
    {
        "id": "GT3",
        "patterns": [
            r"null",
            r"\bNone\b",
            r"format_display_name",
            r"without\s+(a\s+)?(null\s+)?guard",
            r"AttributeError",
            r"user\[.name.\]",
        ],
        "file": r"user_service",
    },
    {
        "id": "GT4",
        "patterns": [
            r"compute_score",
            r"no\s+test",
            r"missing\s+test",
            r"uncovered",
            r"test\s+gap",
            r"not\s+tested",
            r"0 tests",
        ],
        "file": r"user_service|test_user",
    },
]


def hit_gt(text: str, gt: dict) -> bool:
    t = text
    if not re.search(gt["file"], t, re.I):
        # still allow if patterns strong
        pass
    return any(re.search(p, t, re.I) for p in gt["patterns"])


def score_text(text: str) -> dict:
    if not text.strip() or text.startswith("SKIPPED") or text.startswith("GROK_FAILED"):
        return {
            "score": 0,
            "max": 9,
            "gt_hits": [],
            "gt_miss": [g["id"] for g in GT],
            "artifact": 0,
            "tier_honesty": 0,
            "bot_hygiene": 0,
            "empty": True,
        }

    gt_hits = [g["id"] for g in GT if hit_gt(text, g)]
    gt_miss = [g["id"] for g in GT if g["id"] not in gt_hits]
    finding_pts = len(gt_hits)  # max 4

    # Artifact shape: mention multiple pass_ids
    passes = [
        "code-correctness",
        "silent-failures",
        "tests",
        "comments",
        "simplify",
    ]
    pass_count = sum(1 for p in passes if re.search(rf"\b{re.escape(p)}\b", text))
    artifact = 2 if pass_count >= 3 else (1 if pass_count >= 1 else 0)

    # Tier honesty: Blocked + T2/T3
    tier_honesty = 0
    if re.search(r"gate_status:\s*Blocked|\bBlocked\b", text, re.I):
        tier_honesty += 1
    if re.search(r"\bT2\b|\bT3\b", text) and not re.search(
        r"gate_status:\s*Pass", text, re.I
    ):
        tier_honesty += 1
    # if wrongly Pass with findings still present, zero honesty
    if re.search(r"gate_status:\s*Pass", text, re.I) and finding_pts >= 2:
        tier_honesty = 0

    # Bot hygiene: no unconditional wait for this local fixture
    bot_hygiene = 1
    if re.search(r"sleep\s*60|wait(ing)?\s*60\s*seconds\s*for\s*Devin", text, re.I):
        if not re.search(r"not|no|skip|n/a|forbidden|local", text, re.I):
            bot_hygiene = 0

    score = finding_pts + artifact + tier_honesty + bot_hygiene
    return {
        "score": score,
        "max": 9,
        "gt_hits": gt_hits,
        "gt_miss": gt_miss,
        "finding_pts": finding_pts,
        "artifact": artifact,
        "tier_honesty": tier_honesty,
        "bot_hygiene": bot_hygiene,
        "pass_count": pass_count,
        "empty": False,
        "bytes": len(text),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("result_file")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    text = Path(args.result_file).read_text(errors="replace")
    out = score_text(text)
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(
            f"{out['score']}/{out['max']}|hits={','.join(out['gt_hits']) or '-'}|"
            f"miss={','.join(out['gt_miss']) or '-'}|art={out['artifact']}|"
            f"tier={out['tier_honesty']}|bot={out['bot_hygiene']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
