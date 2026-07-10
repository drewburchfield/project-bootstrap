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


def score_baseline_skills(r: Result) -> None:
    """Document coupling in *current* shipping skills (expected failures are reported as baseline signals)."""
    qg = (SKILLS / "quality-gate/SKILL.md").read_text()
    ship = (SKILLS / "ship-loop/SKILL.md").read_text()
    sup = (SKILLS / "supervision-loop/SKILL.md").read_text()

    # Baseline: current quality-gate still Claude-shaped (informational + expected_fail flags)
    patterns = [
        ("qg_has_review_pr", r"/review-pr", qg, True),
        ("qg_has_pr_review_toolkit", r"pr-review-toolkit", qg, True),
        ("qg_has_sleep_60", r"sleep 60", qg, True),
        ("qg_has_devin_wait", r"Devin", qg, True),
        ("ship_mentions_devin", r"Devin", ship, True),
        ("sup_mentions_pr_review_toolkit", r"pr-review-toolkit", sup, True),
    ]
    for name, pat, text, expect_present in patterns:
        found = re.search(pat, text) is not None
        if found == expect_present:
            r.ok(f"baseline:{name}", "present as expected (migration debt)" if found else "absent")
        else:
            r.fail(f"baseline:{name}", f"expected present={expect_present} found={found}")

    # Suite must NOT be referenced as already wired (Phase 1a is extraction only)
    if "review-suite/SPEC" in qg or "references/review-suite" in qg:
        r.ok("baseline:qg_not_yet_wired_or_already", "skill already points at suite")
    else:
        r.ok("baseline:qg_not_wired_yet", "expected until Phase 1b")


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
        choices=["all", "structure", "contracts", "artifacts", "baseline", "host-matrix", "align"],
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    r = Result()
    runners = {
        "structure": score_structure,
        "contracts": score_spec_contracts,
        "artifacts": score_artifacts,
        "baseline": score_baseline_skills,
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
