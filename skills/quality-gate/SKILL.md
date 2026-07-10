---
name: quality-gate
description: >
  Use when the user asks to "quality gate", "run quality gate", "review and merge",
  "PR review cycle", or wants a structured pre-merge review with remediation.
  Multi-harness Review Suite (shared lenses + host adapters). Optional external bots
  (Devin, CodeRabbit). Prefer ship-loop for greenlit merge/CI babysit.
version: 1.5.0
---

# Quality Gate

Structured review and remediation before merge. **Review methodology is host-agnostic** (Review Suite). **Execution** uses the current host’s adapter.

Deep docs (load on demand):

- `references/review-suite/SPEC.md` — tiers, pass artifacts, capability probe
- `references/review-suite/passes/*.md` — six lenses
- `references/review-suite/host-adapters/{claude-code,codex,grok,opencode,agy}.md`
- `references/review-suite/synthesis.md`
- `references/linear-integration.md`, `references/github-cli.md` (issue/PR ops)

## Modes

| Mode | Flag | PR | Push | External bots | Merge |
|------|------|----|------|---------------|-------|
| Auto / full | (default) | yes | yes | if configured | user confirm |
| Explicit issue | `NAS-577` / pattern | yes | yes | if configured | user confirm |
| Standalone | `--no-issue` | yes | yes | if configured | user confirm |
| Local | `--local` | no | no | n/a | no (stop) |

Prefer **ship-loop** when the user wants CI watch + greenlit merge ownership.

## 0. Capability probe (every run)

Probe before review. Never invent tools.

```text
host:          claude-code | codex | grok | opencode | agy | other
git/gh:        available?
issue_tracker: from .claude/project-meta.json (linear|jira|github|standalone|none)
agent_suite:   host can run isolated multi-lens review (Claude: pr-review-toolkit; else subagents)
external_bots: from project-meta.review.externalBots or profile; default empty
clawpatch:     command -v clawpatch (Codex path)
require_suite: project-meta.review.requireAgentSuite (default false)
```

**project-meta optional review block:**

```json
{
  "review": {
    "externalBots": ["devin", "coderabbit"],
    "botWaitSeconds": 60,
    "requireExternalBots": false,
    "requireAgentSuite": false
  }
}
```

**Forbidden:** unconditional `sleep 60` (or any fixed wait) for Devin/CodeRabbit when `external_bots` is empty or bots are not configured.

If bots are configured: after push, wait up to `botWaitSeconds` (default 60), then fetch PR comments; if none arrive, proceed and note `bots: timeout/none`.

## 1. Prerequisites and issue detection

- Not on `main`/`master` for full PR modes (local may run on any branch with a diff).
- Read `project-meta.json` issueTracker when present; else standalone.
- Detect issue from branch / commits / tracker CLI when configured; `--no-issue` skips.
- Uncommitted work: do not silently mix into shipping; ask or commit if clearly part of the work.

Details: `references/linear-integration.md`, `references/github-cli.md`.

## 2. Review Suite (core)

**Always load and follow** `references/review-suite/SPEC.md`.

### Host adapter selection

| Detected host | Adapter file | Default tier path |
|---------------|--------------|-------------------|
| Claude Code | `host-adapters/claude-code.md` | T3 via pr-review-toolkit / `/review-pr` when available |
| Codex | `host-adapters/codex.md` | T2 sequential + optional Clawpatch |
| Grok | `host-adapters/grok.md` | T2 sequential (T3 multi-subagent only if isolation verified) |
| OpenCode | `host-adapters/opencode.md` | T2 sequential |
| agy / other | matching adapter or sequential default | T2 sequential |

On Claude: prefer parallel toolkit agents mapped to suite pass ids (see claude-code adapter). If toolkit missing, fall back to T2 sequential using `passes/*.md`.

On non-Claude hosts: **do not** require `/review-pr` or `pr-review-toolkit:*` agent IDs. Run pass files sequentially (or host subagents) and emit artifacts.

### Pass artifacts (required for Pass)

For each mandatory pass (`code-correctness`, `silent-failures`, `tests`, `types` if typed, `comments`, `simplify`), emit the artifact shape from SPEC (checked list, findings or `none_found: true` with non-empty checked).

### Tier declaration (required every run)

Emit `tier_declaration` from SPEC: host, adapter, tier (T3|T2|T1|T0), execution_mode, passes_completed, passes_skipped, capabilities, gate_status (Pass|Blocked|Incomplete).

| Rule | |
|------|--|
| T2/T3 + valid artifacts + no unresolved Critical/High | may **Pass** |
| T1 single general review | **Incomplete**, never Pass |
| T0 skim | forbidden; do not claim gate |
| Missing artifacts | **Incomplete** / not Pass |
| T2 is not T3 | never claim “equivalent to Claude parallel toolkit” for sequential |

Synthesize with `references/review-suite/synthesis.md`.

### Honesty

- Do not claim Review Suite / quality-gate ran unless T2/T3 with artifacts (or toolkit-mapped equivalent).
- Manual diff read alone = label as manual/T1, not suite Pass.
- If `requireAgentSuite: true` and suite cannot run → **Blocked** with config hint.

## 3. Workflow by mode

### Local (`--local`)

1. Probe + collect local or unpushed diff.
2. Run Review Suite (adapter).
3. Remediate Critical/High (local commits only if user wants fixes).
4. Re-run suite on updated diff if needed.
5. **Stop.** No PR, no push, no merge.

### Full PR (default / issue / `--no-issue`)

1. **Preflight Review Suite** on branch diff (before or as first pass).
2. Create or reuse PR (`gh`); see github-cli reference.
3. Run Review Suite on PR diff (adapter).
4. Remediate Critical/High; push intentional commits.
5. **External bots only if configured** (probe); then re-fetch comments and fold findings.
6. Re-run suite or targeted re-check on changed risk.
7. Verification: project-meta quality commands or inferred tests/lint/typecheck.
8. Present merge options; **do not merge without user confirmation** (unless ship-loop owns merge with greenlit).
9. On merge approve: squash default, update issue tracker if configured.

When **ship-loop** is driving: run this skill’s review + remediation steps only; hand merge/watch/deploy back to ship-loop.

## 4. Remediation

- Critical/High first; Medium deferred only with reason.
- Scoped fixes; clear commit messages.
- Draft-only for risky changes unless user approved auto-remediation.
- Deterministic formatter/linter fixes may apply when safe.

## 5. Output format

```text
Quality gate
Mode: local | full | standalone
Host: <host> · Adapter: <adapter> · Tier: T2|T3|T1|T0

Capabilities
- agent_suite: yes|no
- external_bots: none | [devin,…] (waited|skipped|timeout)
- issue_tracker: linear|none|…

Gate: Pass | Blocked | Incomplete

Findings
- [High] title (path:line): evidence → fix

Passes
- code-correctness: N findings | none found (checked: …)
- …

Verification
- command: result

Next
- <one concrete step>
```

Include machine-readable `tier_declaration` + pass artifacts when writing to a file or when the host benefits from structure (YAML/JSON block is fine).

## 6. Hard rules

1. Follow Review Suite SPEC for Pass/Blocked/Incomplete.
2. No unconditional external-bot sleep.
3. No Claude-only tool IDs as **required** steps on non-Claude hosts.
4. No auto-merge without explicit user approval in this skill (ship-loop may greenlit separately).
5. No false “all agents ran” without actual suite execution.
6. Prefer ship-loop for babysit-until-shipped.

## 7. Drew / maximal pipeline (optional)

For full personal pipeline, set in project-meta:

```json
{
  "review": {
    "externalBots": ["devin", "coderabbit"],
    "botWaitSeconds": 60,
    "requireAgentSuite": true
  }
}
```

Plugin defaults stay permissive so other harnesses complete T2 without bots.
