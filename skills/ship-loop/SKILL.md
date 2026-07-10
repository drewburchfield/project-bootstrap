---
name: ship-loop
description: >
  Use when the user wants to ship, land, or merge a branch or PR ("ship it", "land this",
  "merge when green"), babysit CI, remediate review findings, or greenlit-merge.
  Wraps quality-gate Review Suite with CI watch, optional external bots, merge gate, deploy verify.
version: 1.5.0
---

# Ship Loop

State machine around **quality-gate review**. Ship-loop owns **watch, merge gate, deploy, closeout**. Quality-gate owns **Review Suite + remediation policy**.

## Invocation

```bash
/ship-loop
/ship-loop --watch
/ship-loop --watch 123
/ship-loop --greenlit
/loop 5m /ship-loop --watch
/loop 2m /ship-loop --watch 123 --hot
```

## Modes

| Mode | Behavior |
|------|----------|
| default | current branch → preflight → PR → Review Suite → watch → merge gate (stop for approval unless greenlit) |
| `--watch` | existing PR; poll CI, comments, bots if configured; remediate when safe |
| `--greenlit` | user authorized merge if gates pass (this session / explicit) |
| `--hot` | shorter poll; same gates |

## Project profile

Read if present: `.claude/ship-loop.md`, `.claude/project-meta.json`, `CLAUDE.md`, `AGENTS.md`.

Optional review block in project-meta (same as quality-gate):

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

## Local state (gitignored)

```text
.claude/ship-loop/state.json
.claude/ship-loop/current-status.md
.claude/ship-loop/history/
.claude/ship-loop/review-cache/
```

## Workflow

### 1. Intake

Repo root, branch, base, PR, issue, author, mode, greenlit. Never ship from `main`/`master`.

### 2. Risk scan

Pause even with greenlit on secrets, auth, IAM, destructive migrations, deploy/billing, irreversible data, unclear product decisions.

### 3. Preflight

`git status`, branch ahead of base, PR exists or creatable, issue tracker if configured, local verify commands from profile.

### 4. Quality gate (review only)

Apply **project-bootstrap quality-gate** review steps:

1. Capability probe (host, agent suite, external bots, clawpatch).
2. Load `skills/quality-gate/references/review-suite/SPEC.md` and the host adapter.
3. Run Review Suite; require pass artifacts + tier_declaration for Pass/Blocked.
4. Remediate Critical/High per quality-gate rules (draft by default).

**Do not** invoke `/quality-gate` as a nested full merge workflow. **Do not** unconditional-wait for Devin.

Ship-loop owns merge: when quality-gate would merge, return here.

### 5. Watch

Poll:

- CI (required checks; pending ≠ green)
- mergeability
- human review decisions
- **external bots only if configured** (probe); state `n/a (not configured)` otherwise
- new comments
- branch freshness
- post-merge deploy workflows when shipping

Cadence: 5m default, 2m hot, longer if only slow bots. Re-run Review Suite when head SHA changes; reuse review-cache for same SHA.

### 6. Merge gate

All must hold:

- CI green
- PR mergeable
- blocking comments resolved
- external bots: findings handled **or** n/a not configured
- Review Suite gate Pass (or Incomplete only if user explicitly accepts incomplete)
- issue fit OK
- risk scan clear or approved

No greenlit → present summary, stop for approval.  
Greenlit + gates pass → merge (squash default unless project says otherwise), delete branch if configured.

### 7. Post-merge

Verify merge commit, issue tracker update if configured, deploy workflows if present, smoke from profile. Do not claim shipped until verified.

### 8. Blocked

Stop with concrete next action: unclear CI, judgment-needed bot finding, conflicts, missing secrets, ambiguous scope.

## Output

```text
Ship loop
Target: <branch or PR>
Mode: default | watch | greenlit | hot
Host: <host> · Review tier: T2|T3|T1|Incomplete

Status
- shipped | watching | remediating | waiting approval | blocked

Gates
- CI: <state>
- Review suite: Pass|Blocked|Incomplete (tier, adapter)
- External bots: n/a | waited | timeout | findings
- Mergeable: <state>
- Risk: <state>

Actions taken
- …

Next
- <one step>
```

## Hard rules

- No auto-merge without greenlit.
- No “CI pending” as success.
- External bots are optional; never hang forever or blind-sleep when none configured.
- Review Suite honesty: same as quality-gate (no false Pass).
- Do not rerun expensive review on unchanged SHA every tick.
- Do not mark issues Done before merge + verification.
