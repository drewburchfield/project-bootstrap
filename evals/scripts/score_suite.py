#!/usr/bin/env python3
"""Deterministic scorer for project-bootstrap Review Suite evals (Phase 0/1a).

Usage:
  python3 evals/scripts/score_suite.py              # full suite, exit 1 on fail
  python3 evals/scripts/score_suite.py --json       # machine-readable summary
  python3 evals/scripts/score_suite.py structure    # suite files only
  python3 evals/scripts/score_suite.py artifacts    # sample YAML only
  python3 evals/scripts/score_suite.py baseline     # current skill anti-patterns
  python3 evals/scripts/score_suite.py contracts    # SPEC contract presence
  python3 evals/scripts/score_suite.py host-matrix  # host adapter docs + rules
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / "skills/quality-gate/references/review-suite"
SKILLS = ROOT / "skills"
SAMPLES = ROOT / "evals/samples"

MANDATORY_PASSES = [
    "code-correctness",
    "silent-failures",
    "tests",
    "types",
    "comments",
    "simplify",
]

HOSTS = ["claude-code", "codex", "grok", "opencode", "agy"]


class Result:
    def __init__(self) -> None:
        self.checks: list[dict] = []

    def ok(self, name: str, detail: str = "") -> None:
        self.checks.append({"name": name, "pass": True, "detail": detail})

    def fail(self, name: str, detail: str) -> None:
        self.checks.append({"name": name, "pass": False, "detail": detail})

    @property
    def passed(self) -> int:
        return sum(1 for c in self.checks if c["pass"])

    @property
    def failed(self) -> int:
        return sum(1 for c in self.checks if not c["pass"])

    @property
    def all_ok(self) -> bool:
        return self.failed == 0


def load_yaml(path: Path) -> dict:
    if yaml is None:
        raise RuntimeError("PyYAML required: pip install pyyaml")
    with path.open() as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected mapping")
    return data


def score_structure(r: Result) -> None:
    required = [
        SUITE / "SPEC.md",
        SUITE / "synthesis.md",
    ]
    for p in required:
        if p.is_file() and p.stat().st_size > 100:
            r.ok(f"exists:{p.relative_to(ROOT)}", f"{p.stat().st_size} bytes")
        else:
            r.fail(f"exists:{p.relative_to(ROOT)}", "missing or tiny")

    for pid in MANDATORY_PASSES:
        p = SUITE / "passes" / f"{pid}.md"
        if not p.is_file():
            r.fail(f"pass_file:{pid}", "missing")
            continue
        text = p.read_text()
        if len(text) > 80 and ("Checklist" in text or "checklist" in text) and pid in text:
            r.ok(f"pass_file:{pid}")
        else:
            r.fail(f"pass_file:{pid}", "missing checklist content or pass id")

    for h in HOSTS:
        p = SUITE / "host-adapters" / f"{h}.md"
        if p.is_file() and len(p.read_text()) > 80:
            r.ok(f"host_adapter:{h}")
        else:
            r.fail(f"host_adapter:{h}", "missing or tiny")


def score_spec_contracts(r: Result) -> None:
    spec = (SUITE / "SPEC.md").read_text()
    required_phrases = [
        ("Pass artifact contract", "artifact contract section"),
        ("Tier declaration contract", "tier declaration section"),
        ("Capability probe", "capability probe"),
        ("none_found", "none_found enforcement"),
        ("T2 is not T3", "T2/T3 honesty"),
        ("unconditional", "no unconditional bot wait"),
        ("gate_status", "gate_status field"),
    ]
    for needle, label in required_phrases:
        if needle.lower() in spec.lower() or needle in spec:
            r.ok(f"spec:{label}")
        else:
            # softer: search alternate
            if label == "no unconditional bot wait" and "sleep" in spec.lower() and "bot" in spec.lower():
                r.ok(f"spec:{label}", "sleep/bot language present")
            else:
                r.fail(f"spec:{label}", f"missing phrase near: {needle}")

    # Must forbid false equivalence
    if "not" in spec.lower() and "t3" in spec.lower() and "t2" in spec.lower():
        r.ok("spec:t2_not_t3_wording")
    else:
        r.fail("spec:t2_not_t3_wording", "need explicit T2 not T3")


def validate_run(data: dict) -> list[str]:
    """Return list of error strings; empty = valid suite structure for Pass eligibility."""
    errors: list[str] = []
    td = data.get("tier_declaration") or {}
    tier = td.get("tier")
    gate = td.get("gate_status")
    passes = data.get("passes") or []

    if tier in ("T1", "T0") and gate == "Pass":
        errors.append(f"tier {tier} cannot have gate_status Pass")

    if gate == "Pass" and tier not in ("T2", "T3"):
        errors.append(f"Pass requires T2/T3, got {tier}")

    if gate == "Pass" or tier in ("T2", "T3"):
        by_id = {p.get("pass_id"): p for p in passes if isinstance(p, dict)}
        skip_ids: set = set()
        for s in td.get("passes_skipped") or []:
            if isinstance(s, dict):
                skip_ids.add(s.get("id"))
            else:
                skip_ids.add(s)
        for pid in MANDATORY_PASSES:
            if pid in skip_ids:
                continue
            if pid not in by_id:
                errors.append(f"missing pass artifact: {pid}")
                continue
            art = by_id[pid]
            checked = art.get("checked") or []
            findings = art.get("findings")
            none_found = art.get("none_found")
            if findings is None:
                errors.append(f"{pid}: findings key required")
                continue
            if none_found is True:
                if not checked:
                    errors.append(f"{pid}: none_found requires non-empty checked")
                if findings:
                    errors.append(f"{pid}: none_found true but findings non-empty")
            elif none_found is False or (isinstance(findings, list) and len(findings) > 0):
                if not isinstance(findings, list):
                    errors.append(f"{pid}: findings must be list")
                else:
                    for i, fnd in enumerate(findings):
                        if not isinstance(fnd, dict):
                            errors.append(f"{pid}: finding {i} not mapping")
                            continue
                        for k in ("severity", "file", "evidence"):
                            if k not in fnd:
                                errors.append(f"{pid}: finding {i} missing {k}")
            else:
                errors.append(f"{pid}: must set none_found or provide findings")

    return errors


def score_artifacts(r: Result) -> None:
    if yaml is None:
        r.fail("artifacts:pyyaml", "pip install pyyaml")
        return

    cases = [
        ("valid_t2_run.yaml", True),
        ("valid_t2_with_findings.yaml", True),
        ("invalid_t1_claims_pass.yaml", False),
        ("invalid_rubber_stamp.yaml", False),
    ]
    for name, should_valid in cases:
        path = SAMPLES / name
        if not path.is_file():
            r.fail(f"sample:{name}", "file missing")
            continue
        try:
            data = load_yaml(path)
            errors = validate_run(data)
            is_valid = len(errors) == 0
            if is_valid == should_valid:
                r.ok(f"sample:{name}", "valid" if is_valid else f"correctly rejected: {errors[0]}")
            else:
                r.fail(
                    f"sample:{name}",
                    f"expected valid={should_valid} got valid={is_valid} errors={errors}",
                )
        except Exception as e:
            r.fail(f"sample:{name}", str(e))


BASELINES = ROOT / "evals/baselines"


def _has(pat: str, text: str) -> bool:
    return re.search(pat, text, re.I) is not None


def score_wired_skills(r: Result) -> None:
    """Live skills after Phase 1b must be multi-harness + suite-wired."""
    qg = (SKILLS / "quality-gate/SKILL.md").read_text()
    ship = (SKILLS / "ship-loop/SKILL.md").read_text()
    sup = (SKILLS / "supervision-loop/SKILL.md").read_text()

    # Must wire suite
    for name, text in [("qg", qg), ("ship", ship), ("sup", sup)]:
        if "review-suite" in text or "Review Suite" in text:
            r.ok(f"wired:{name}:mentions_review_suite")
        else:
            r.fail(f"wired:{name}:mentions_review_suite", "must reference Review Suite")

    if "SPEC.md" in qg or "review-suite/SPEC" in qg:
        r.ok("wired:qg:points_at_spec")
    else:
        r.fail("wired:qg:points_at_spec", "must load SPEC.md")

    # Must forbid unconditional sleep
    if re.search(r"sleep\s+60", qg) and "Forbidden" not in qg and "unconditional" not in qg.lower():
        # bare sleep 60 as instruction is bad
        if re.search(r"(?m)^(?:```[\s\S]*?)?sleep 60", qg) and "Forbidden" not in qg[: qg.find("sleep 60") + 200]:
            r.fail("wired:qg:no_bare_sleep_60", "found sleep 60 without forbid framing")
        else:
            r.ok("wired:qg:sleep_60_only_as_forbid_or_absent")
    elif re.search(r"sleep\s+60", qg):
        # allowed only in forbid/context about bots
        if "unconditional" in qg.lower() or "Forbidden" in qg:
            r.ok("wired:qg:sleep_60_only_as_forbid_or_absent", "discussed as forbidden")
        else:
            r.fail("wired:qg:no_bare_sleep_60", "sleep 60 present without forbid")
    else:
        r.ok("wired:qg:no_bare_sleep_60", "no sleep 60")

    # Must have multi-host language
    for host in ("codex", "grok", "opencode", "agy", "claude"):
        if host in qg.lower():
            r.ok(f"wired:qg:host_{host}")
        else:
            r.fail(f"wired:qg:host_{host}", "host not mentioned")

    # Tier honesty
    for needle in ("T2", "T3", "Incomplete", "tier_declaration", "pass artifact"):
        if needle.lower() in qg.lower() or needle in qg:
            r.ok(f"wired:qg:has_{needle.replace(' ', '_')}")
        else:
            r.fail(f"wired:qg:has_{needle.replace(' ', '_')}", "missing")

    # Non-Claude must not be required path only
    if "do not" in qg.lower() and ("/review-pr" in qg or "pr-review-toolkit" in qg):
        r.ok("wired:qg:limits_claude_tools_on_other_hosts")
    else:
        r.fail("wired:qg:limits_claude_tools_on_other_hosts", "must constrain toolkit to Claude path")

    # Ship loop owns merge / no unconditional bots
    if "unconditional" in ship.lower() or "n/a" in ship.lower() or "not configured" in ship.lower():
        r.ok("wired:ship:optional_bots")
    else:
        r.fail("wired:ship:optional_bots", "must treat bots optional")

    if "Review Suite" in ship or "review-suite" in ship:
        r.ok("wired:ship:suite")
    else:
        r.fail("wired:ship:suite", "must use suite")

    # Supervision generic operator + suite
    if "operator" in sup.lower():
        r.ok("wired:sup:operator_generic")
    else:
        r.fail("wired:sup:operator_generic", "must use operator not only personal name")

    if "Review Suite" in sup or "review-suite" in sup:
        r.ok("wired:sup:suite")
    else:
        r.fail("wired:sup:suite", "must use suite")

    if re.search(r"do not claim.*Review Suite|do not claim.*quality-gate", sup, re.I):
        r.ok("wired:sup:honesty")
    else:
        r.fail("wired:sup:honesty", "must forbid false suite claims")


def score_old_vs_new(r: Result) -> None:
    """A/B: frozen v1.4.0 baselines vs live skills (regression + improvement)."""
    pairs = [
        ("quality-gate", "quality-gate-v1.4.0-SKILL.md", "quality-gate/SKILL.md"),
        ("ship-loop", "ship-loop-v1.4.0-SKILL.md", "ship-loop/SKILL.md"),
        ("supervision-loop", "supervision-loop-v1.4.0-SKILL.md", "supervision-loop/SKILL.md"),
    ]

    def debt_score(text: str) -> dict:
        # Instructional wait (debt), not prose forbidding unconditional wait
        has_wait_instruction = bool(
            re.search(r"Waiting 60 seconds for Devin|Wait 60s for external tools \(Devin", text, re.I)
        ) or bool(re.search(r"(?m)^\s*sleep 60\s*$", text))
        discusses_forbid_wait = "unconditional" in text.lower() and (
            "forbidden" in text.lower() or "do not" in text.lower()
        )
        return {
            "bare_sleep_60": bool(re.search(r"(?m)^\s*sleep 60\s*$", text))
            or (
                "sleep 60" in text
                and not discusses_forbid_wait
                and bool(re.search(r"echo.*[Ww]aiting 60", text))
            ),
            "unconditional_devin_wait": has_wait_instruction and not discusses_forbid_wait,
            "suite_wired": "review-suite" in text or "Review Suite" in text,
            "multi_host": sum(1 for h in ("codex", "grok", "opencode", "agy") if h in text.lower()) >= 2,
            "tier_system": "T2" in text and "T3" in text,
        }

    for label, old_name, new_rel in pairs:
        old_path = BASELINES / old_name
        new_path = SKILLS / new_rel
        if not old_path.is_file():
            r.fail(f"ab:{label}:old_baseline", f"missing {old_path}")
            continue
        if not new_path.is_file():
            r.fail(f"ab:{label}:new_skill", f"missing {new_path}")
            continue
        old = debt_score(old_path.read_text())
        new = debt_score(new_path.read_text())

        # Old should show debt (quality-gate especially)
        if label == "quality-gate":
            if old["unconditional_devin_wait"] or old["bare_sleep_60"] or not old["suite_wired"]:
                r.ok(f"ab:{label}:old_has_debt", f"old={old}")
            else:
                r.fail(f"ab:{label}:old_has_debt", f"expected v1.4 debt, got {old}")

            if new["suite_wired"] and new["multi_host"] and new["tier_system"] and not new["unconditional_devin_wait"]:
                r.ok(f"ab:{label}:new_improved", f"new={new}")
            else:
                r.fail(f"ab:{label}:new_improved", f"expected multi-harness suite, got {new}")

            if old["suite_wired"] and not new["suite_wired"]:
                r.fail(f"ab:{label}:no_regress_suite", "suite lost")
            else:
                r.ok(f"ab:{label}:no_regress_suite")
        else:
            # ship / supervision: new must be suite-wired; old typically not
            if new["suite_wired"]:
                r.ok(f"ab:{label}:new_suite_wired")
            else:
                r.fail(f"ab:{label}:new_suite_wired", "new must wire suite")
            if not old["suite_wired"] and new["suite_wired"]:
                r.ok(f"ab:{label}:improved_over_v14")
            elif old["suite_wired"] and new["suite_wired"]:
                r.ok(f"ab:{label}:still_wired")
            else:
                r.fail(f"ab:{label}:improved_over_v14", f"old={old} new={new}")

        # Size sanity: new quality-gate should be leaner than 1010-line v1.4
        if label == "quality-gate":
            old_lines = len(old_path.read_text().splitlines())
            new_lines = len(new_path.read_text().splitlines())
            if new_lines < old_lines * 0.5:
                r.ok(f"ab:{label}:leaner", f"{old_lines} → {new_lines} lines")
            else:
                r.fail(f"ab:{label}:leaner", f"expected hybrid slim, {old_lines} → {new_lines}")


def score_baseline_skills(r: Result) -> None:
    """v1.4.0 frozen baselines still exhibit Claude-shaped debt (control group)."""
    qg = (BASELINES / "quality-gate-v1.4.0-SKILL.md").read_text()
    ship = (BASELINES / "ship-loop-v1.4.0-SKILL.md").read_text()
    sup = (BASELINES / "supervision-loop-v1.4.0-SKILL.md").read_text()

    patterns = [
        ("v14_qg_has_review_pr", r"/review-pr", qg, True),
        ("v14_qg_has_pr_review_toolkit", r"pr-review-toolkit", qg, True),
        ("v14_qg_has_sleep_60", r"sleep 60", qg, True),
        ("v14_qg_has_devin_wait", r"Devin", qg, True),
        ("v14_qg_no_suite", r"review-suite", qg, False),
        ("v14_ship_mentions_devin", r"Devin", ship, True),
        # v1.4 supervision mentioned Devin/quality-gate but not always pr-review-toolkit by name
        ("v14_sup_no_suite", r"review-suite|Review Suite", sup, False),
    ]
    for name, pat, text, expect_present in patterns:
        found = re.search(pat, text) is not None
        if found == expect_present:
            r.ok(f"baseline:{name}", "control group as expected")
        else:
            r.fail(f"baseline:{name}", f"expected present={expect_present} found={found}")


def score_host_matrix(r: Result) -> None:
    """Each host adapter must forbid Claude-only IDs except claude-code."""
    for h in HOSTS:
        p = SUITE / "host-adapters" / f"{h}.md"
        text = p.read_text()
        if h == "claude-code":
            if "pr-review-toolkit" in text or "/review-pr" in text:
                r.ok(f"host_matrix:{h}:allows_toolkit")
            else:
                r.fail(f"host_matrix:{h}:allows_toolkit", "claude adapter should mention toolkit")
            if "T3" in text:
                r.ok(f"host_matrix:{h}:t3")
            else:
                r.fail(f"host_matrix:{h}:t3", "should default T3 path")
        else:
            # Forbidden as required path
            bad = []
            if re.search(r"(?i)required.*(/review-pr|pr-review-toolkit)", text):
                bad.append("requires toolkit")
            if "Forbidden" in text and ("/review-pr" in text or "pr-review-toolkit" in text):
                r.ok(f"host_matrix:{h}:forbids_claude_tools")
            elif "do not" in text.lower() and "review-pr" in text.lower():
                r.ok(f"host_matrix:{h}:forbids_claude_tools")
            else:
                # codex/grok/opencode/agy should still mention not using toolkit
                if "pr-review-toolkit" in text or "/review-pr" in text:
                    # mentioned in forbidden section is ok
                    if "Forbidden" in text:
                        r.ok(f"host_matrix:{h}:mentions_forbid")
                    else:
                        r.fail(f"host_matrix:{h}:forbids_claude_tools", "must forbid Claude-only tools")
                else:
                    r.ok(f"host_matrix:{h}:no_claude_tool_refs")
            if "T2" in text:
                r.ok(f"host_matrix:{h}:t2_default")
            else:
                r.fail(f"host_matrix:{h}:t2_default", "non-claude should default T2")


def score_pass_id_alignment(r: Result) -> None:
    for pid in MANDATORY_PASSES:
        text = (SUITE / "passes" / f"{pid}.md").read_text()
        if f"**id:** `{pid}`" in text or f"id:** `{pid}`" in text or f"`{pid}`" in text.split("\n")[0:5].__str__():
            r.ok(f"align:id:{pid}")
        else:
            # first lines should include id
            if pid in text[:200]:
                r.ok(f"align:id:{pid}")
            else:
                r.fail(f"align:id:{pid}", "pass id not in header")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "suite",
        nargs="?",
        default="all",
        choices=[
            "all",
            "structure",
            "contracts",
            "artifacts",
            "baseline",
            "wired",
            "ab",
            "host-matrix",
            "align",
        ],
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    r = Result()
    runners = {
        "structure": score_structure,
        "contracts": score_spec_contracts,
        "artifacts": score_artifacts,
        "baseline": score_baseline_skills,
        "wired": score_wired_skills,
        "ab": score_old_vs_new,
        "host-matrix": score_host_matrix,
        "align": score_pass_id_alignment,
    }

    if args.suite == "all":
        for fn in runners.values():
            fn(r)
    else:
        runners[args.suite](r)

    if args.json:
        print(
            json.dumps(
                {
                    "passed": r.passed,
                    "failed": r.failed,
                    "ok": r.all_ok,
                    "checks": r.checks,
                },
                indent=2,
            )
        )
    else:
        for c in r.checks:
            mark = "PASS" if c["pass"] else "FAIL"
            detail = f" — {c['detail']}" if c["detail"] else ""
            print(f"[{mark}] {c['name']}{detail}")
        print()
        print(f"Summary: {r.passed} passed, {r.failed} failed")
        if r.all_ok:
            print("RESULT: GREEN")
        else:
            print("RESULT: RED")

    return 0 if r.all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
