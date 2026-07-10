# Review Suite Spec

Portable methodology for quality-gate, ship-loop, and supervision-loop reviews.

**Source of truth for lenses.** Host adapters only define *how* to run passes, not *what* to check.
Content borrowed from pr-review-toolkit agent descriptions and quality-gate-codex pass lists.

This file is host-agnostic. No Claude slash commands, no Devin sleeps, no Linear templates.

---

## Goal

Produce evidence-backed findings across independent review lenses, synthesize severity, and emit an honest **gate status** with a **tier claim** that matches what actually ran.

---

## Mandatory passes

| id | File | Skip when |
|----|------|-----------|
| `code-correctness` | `passes/code-correctness.md` | never (for code diffs) |
| `silent-failures` | `passes/silent-failures.md` | never (for code diffs) |
| `tests` | `passes/tests.md` | never (for code diffs) |
| `types` | `passes/types.md` | untyped / non-code-only diffs |
| `comments` | `passes/comments.md` | never (for code diffs) |
| `simplify` | `passes/simplify.md` | after correctness passes; still required for suite Pass |

Non-code docs-only diffs: run at least `comments` + `code-correctness` (as content accuracy) or mark suite **Incomplete** with reason.

---

## Severity

| Level | Meaning | Gate impact |
|-------|---------|-------------|
| Critical | data loss, security, broken primary path, silent failure with material impact, untested risky core | Blocks Pass until fixed or explicitly deferred with operator approval |
| High | likely bug, important missing test, clear regression risk | Blocks Pass until fixed or explicitly deferred with reason |
| Medium | real maintainability/correctness risk, not immediately blocking | Pass only if fixed or deferred with reason |
| Low | cleanup / clarity | Does not block |

**Gate Pass** requires: no unresolved Critical or High, and every Medium fixed or deferred with a reason.

---

## Tiers (honesty)

| Tier | Name | Requirements | May claim suite Pass? |
|------|------|--------------|------------------------|
| **T3** | Parallel multi-lens (isolated) | Multiple independent contexts/agents, one primary lens each; all mandatory pass artifacts present | Yes |
| **T2** | Sequential multi-lens | All mandatory pass artifacts present; sequential or map-reduce execution | Yes |
| **T1** | Single general review | One undifferentiated review | **No** → status **Incomplete** |
| **T0** | Diff skim | No structured review | **No** → forbidden for quality-gate |

**T2 is not T3.** T2 is methodologically complete sequential coverage. T3 adds isolation / anti-anchoring. Never market T2 as "equivalent to Claude parallel toolkit."

**Minimum for quality-gate Pass:** T2 or T3 **and** all mandatory pass artifacts.

---

## Pass artifact contract (enforcement)

Each mandatory pass **must** emit a block:

```yaml
pass_id: code-correctness   # one of the ids above
checked:
  - "logic / edge cases"
  - "security patterns in diff"
  # short list of checklist items actually examined
line_ranges_or_files:
  - "src/foo.ts:10-40"
  - "src/bar.ts (full in diff)"
findings:
  - severity: High
    file: src/foo.ts
    line: 22
    title: short title
    evidence: what is wrong
    fix: recommended fix
  # empty list only if none_found is true
none_found: false
# if none_found true:
# findings: []
# none_found: true
```

Rules:

1. `none_found: true` requires non-empty `checked` (what was examined). Rubber-stamp empty passes are invalid.
2. Every finding needs `severity`, `file`, and evidence. Prefer `line` when available.
3. Gate Pass is **invalid** if any mandatory pass artifact is missing or invalid.
4. Hosts should prefer re-injecting only the current pass checklist between passes (isolation). Continuous single-context six-section output is allowed for T2 only if each section still satisfies this contract.

---

## Tier declaration contract (every run)

Emit once per quality-gate / ship-loop review / supervision PR review:

```yaml
tier_declaration:
  host: claude-code | codex | grok | opencode | agy | other
  adapter: claude-pr-review-toolkit | codex-sequential | grok-sequential | ...
  tier: T3 | T2 | T1 | T0
  execution_mode: parallel | sequential | single | skim
  passes_completed: [code-correctness, silent-failures, tests, types, comments, simplify]
  passes_skipped: [{ id: types, reason: "untyped diff" }]
  capabilities:
    agent_suite: true | false
    external_bots: [] | [devin, coderabbit]
    clawpatch: true | false
    issue_tracker: linear | github | none
  gate_status: Pass | Blocked | Incomplete
```

If `tier` is T1 or T0, `gate_status` must not be Pass for suite purposes.

---

## Capability probe (shared primitive)

Before review execution, probe cheaply:

| Capability | Detect | If absent |
|------------|--------|-----------|
| git / gh | binaries + auth | fail PR modes; local may continue |
| agent_suite / parallel | host can spawn isolated reviewers | T2 sequential or T1 |
| external_bots | project-meta `review.externalBots` or profile list | **no wait**; do not sleep |
| clawpatch | `command -v clawpatch` | skip; note unavailable |
| issue_tracker | project-meta | standalone |

**Forbidden:** unconditional `sleep 60` for Devin/CodeRabbit when bots are not configured.

---

## Synthesis

After all pass artifacts exist, run `synthesis.md` rules: dedupe, severity normalize, set `gate_status`, list deferrals.

---

## Host adapters

| Host | Doc | Default tier path |
|------|-----|-------------------|
| Claude Code | `host-adapters/claude-code.md` | T3 via pr-review-toolkit |
| Codex | `host-adapters/codex.md` | T2 via sequential + optional Clawpatch |
| Grok | `host-adapters/grok.md` | T2 sequential (T3 deferred until isolation verified) |
| OpenCode | `host-adapters/opencode.md` | T2 sequential |
| agy | `host-adapters/agy.md` | T2 sequential |

Thin host skills load this SPEC and the adapter. They must not embed other hosts' tool IDs as required steps.

---

## Integration points

- **quality-gate:** full gate orchestration + this suite for review
- **ship-loop:** uses same suite for review phase; owns merge
- **supervision-loop:** uses same suite for teammate PR review; draft-only posts

---

## Version

- Spec version: `1.0.0-draft` (Phase 1a extraction)
- Align skill rewrites to this before claiming multi-harness Pass
