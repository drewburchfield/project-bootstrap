---
name: ship-loop
description: Use when the user wants to ship, land, or merge a branch or PR ("ship it", "land this", "merge when green"), babysit CI or review feedback, watch a PR, run a PR watch loop, remediate review findings, continue until green, merge when explicitly greenlit, verify deploys, and close out issue tracking. End-to-end ship workflow that wraps quality-gate with CI watching, remediation, merge, and deploy verification.
version: 1.0.0
---

# Ship Loop

Ship loop is the state machine around `quality-gate`. It carries work from current branch or existing PR through checks, review, remediation, merge gate, deploy verification, and closeout.

Use `quality-gate` to decide whether the work is clean. Use `ship-loop` to keep moving the work until it is shipped, blocked, or waiting on real human judgment.

## Invocation

Current branch:

```bash
/ship-loop
```

Watch an existing PR:

```bash
/ship-loop --watch
/ship-loop --watch 123
```

Active babysitting loop:

```bash
/loop 5m /ship-loop --watch
```

Explicit greenlit shipping:

```bash
/ship-loop --greenlit
/ship-loop --watch 123 --greenlit
```

Hot mode:

```bash
/loop 2m /ship-loop --watch 123 --hot
```

## Modes

### Default

Use the current branch. Run preflight, create or find the PR, run review, watch checks, remediate, then stop at the merge gate unless the user explicitly passed `--greenlit` or gave equivalent instruction in the current session.

### `--watch`

Use an existing PR or auto-detect the PR for the current branch. Poll CI, Devin or other automated reviewers, GitHub comments, mergeability, and review state. Remediate clear findings when safe. Stop when shipped, blocked, or waiting on approval.

### `--greenlit`

The user has explicitly authorized autonomous merge if all gates pass.

Do not infer greenlit from prior sessions unless a project memory, repo instruction, or current user instruction clearly grants it for this repo and risk level.

### `--hot`

Use shorter polling and shorter summaries during active review. Still obey all merge and write gates.

## Project Profile

If present, read repo-local shipping guidance:

```text
.claude/ship-loop.md
.claude/project-meta.json
CLAUDE.md
AGENTS.md
```

Use project-specific verification commands from those files. If none exist, infer conservative defaults from the repo:
- package manager test command
- Python test command
- `make verify`
- `make test`
- GitHub CI

When uncertain, run read-only inspection and ask before expensive or risky commands.

## Local State

Use gitignored local state only when a loop needs memory:

```text
.claude/ship-loop/
  state.json
  current-status.md
  history/
  review-cache/
```

If the folder is not ignored, either add it to `.gitignore` with user approval or avoid persistent state and rely on live checks.

## Workflow

Run these phases in order.

### 1. Intake

Identify:
- repo root
- current branch
- target base branch
- PR number if any
- issue id if any
- author
- changed paths
- requested mode
- greenlit status

Never ship directly from `main` or `master`.

### 2. Risk Scan

Risk scanning is best-effort heuristic, not a substitute for human oversight on critical changes. When in doubt, stop even with `--greenlit`.

Pause before autonomous merge when the diff touches:
- secrets
- auth or permission policy
- IAM
- destructive migrations
- deploy infrastructure
- alert policies
- billing or payments
- irreversible data changes
- unclear product or architecture decisions

If `--greenlit` is present but the work is risky, stop and ask unless the current instruction explicitly greenlit that risk class.

### 3. Preflight

Check:
- `git status`
- branch up to date with remote
- branch has commits ahead of base
- PR exists or can be created
- issue tracking state if configured
- local verification commands from the project profile

If there are uncommitted changes, do not silently mix them into shipping. Ask or commit only if they are clearly part of the current work.

### 4. Quality Gate

Apply `project-bootstrap:quality-gate`'s review and remediation steps as the review pass for this loop. Do not run the `/quality-gate` slash command as a separate invocation.

Ship-loop owns the merge. When quality-gate would reach its own merge step, hand control back to ship-loop's phase 5 (Watch) and phase 6 (Merge Gate). Ship-loop's `--greenlit` gating, risk scan, and deploy verification supersede quality-gate's merge step.

Minimum review surface:
- local diff or PR diff
- tests and type checks
- GitHub comments
- CI status
- Devin or equivalent automated review when configured
- issue fit
- missing tests
- silent failure risks

Default to drafting remediation, not applying it. Only commit and push remediation automatically when (a) the change is a deterministic linter or formatter fix, or (b) the user has explicitly approved auto-remediation in the current session. Surface anything beyond that as a draft for the user to confirm.

### 5. Watch

Poll live status:
- CI checks
- mergeability
- review decisions
- Devin or other automated review
- new GitHub comments
- branch freshness
- deploy workflows after merge

Default loop cadence:
- 5 minutes for PR watch
- 2 minutes for hot mode
- 10 minutes for slow external reviewers

Avoid redoing expensive review for the same head SHA. Re-run review when the PR head SHA changes or new review feedback appears.

### 6. Merge Gate

A PR can merge only when all required gates pass:
- CI green
- PR mergeable
- blocking review comments resolved
- automated reviewer success or findings handled
- quality-gate has no unresolved medium, high, or critical findings
- issue fit is acceptable
- no risky diff class needs explicit approval

If `--greenlit` is absent, present the merge summary and stop for user approval.

If `--greenlit` is present and gates pass, merge using the repo's configured strategy. If no strategy is configured, default to squash merge and delete branch.

### 7. Post-Merge

After merge:
- verify merge commit
- confirm branch deletion if requested
- update issue tracker if configured
- pull or refresh local main only if useful
- check deploy workflows triggered by the merge
- run post-merge smoke checks from project profile
- report final state

Do not claim shipped until merge and required post-merge checks are verified.

### 8. Blocked State

Stop and report clearly when:
- CI fails and cause is unclear
- automated reviewer flags a real issue that needs judgment
- merge conflicts require careful resolution
- project secrets or credentials are missing
- deploy verification requires manual browser or account access
- issue scope is ambiguous
- reviewer comments conflict

Blocked output must include the next concrete action, not a vague status.

## Output Format

Keep output concise.

```text
Ship loop
Target: <branch or PR>
Mode: default | watch | greenlit | hot

Status
- <shipped / watching / remediating / waiting approval / blocked>

Gates
- CI: <state>
- Review: <state>
- Devin: <state>
- Mergeable: <state>
- Risk: <state>

Actions taken
- <commits, pushes, comments drafted, checks run>

Next
- <one concrete next step>
```

For a successful greenlit merge, do not ask a checkpoint question. Report what merged and what verification passed.

## Hard Rules

- Do not auto-merge without explicit greenlit authorization.
- Do not auto-merge someone else's PR unless the current user explicitly authorized that exact class of PR.
- Do not treat "CI pending" as success.
- Do not ignore stale Devin or automated review state.
- Do not claim deploy success from workflow start alone.
- Do not rerun expensive review on the same unchanged SHA every loop tick.
- Do not hide remediation commits.
- Do not update issue trackers with false Done state before merge and verification.
- Do not make the user babysit routine polling.
