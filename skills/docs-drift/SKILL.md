---
name: docs-drift
description: Use when checking, auditing, scanning, or reviewing for stale, outdated, or drifting documentation ("are my docs stale", "scan for docs drift", "docs out of date", "reconcile docs", "audit CLAUDE.md and runbooks against recent PRs"). Compares recent merged PRs, commits, and changed files against README, CLAUDE.md, AGENTS.md, runbooks, setup docs, skills, and prompts. Drafts surgical patches by default; can open a docs-only PR when explicitly greenlit. Safe for weekly cloud routines from a fresh clone.
version: 1.0.0
---

# Docs Drift

Docs drift compares recent repo changes against documentation and setup guidance. It catches stale instructions before future work starts from bad assumptions.

This skill is safe for weekly cloud routines because it can operate from a fresh clone using git history and repo files. Live infrastructure verification is optional and must be configured separately.

## Invocation

Default seven-day scan:

```bash
/docs-drift
```

Explicit window:

```bash
/docs-drift --since 7d
/docs-drift --since 2026-05-01
```

Greenlit docs PR:

```bash
/docs-drift --since 7d --greenlit-pr
```

## Modes

### Default

Read-only. Scan recent changes, classify drift, draft surgical patches. Do not edit files. Do not open a PR.

### `--since <window>`

Override the default 7-day window. Accepts relative (`7d`, `14d`) or absolute (`YYYY-MM-DD`) values.

### `--greenlit-pr`

The user has explicitly authorized opening a docs-only PR for high-confidence drift. Apply only high-confidence edits. Operate against the repo's default branch (never a feature branch). If high-confidence edits would touch more than 10 files, stop and present the report instead. Never edit code, only docs.

## Local State

docs-drift holds no local state. Each run rereads git history and the working tree.

## Project Config

If present, read project-specific guidance:

```text
.claude/docs-drift.md
```

Use it to learn:
- priority docs
- source-of-truth files
- paths to ignore
- claims that need live verification
- whether PR creation is allowed

If no config exists, infer from repo structure.

## Inputs

Collect:
- merged PRs in the requested window
- commits in the requested window
- changed files and diffs
- current docs and setup files
- project config if present

Default window: last 7 days.

Default docs to inspect:
- `README.md`
- `CLAUDE.md`
- `AGENTS.md`
- `docs/**`
- `runbooks/**`
- `.claude/**`
- `skills/**`
- package or setup docs
- deployment and workflow docs

Default source files that often imply docs changes:
- commands and scripts
- config files
- workflows
- Makefiles
- Dockerfiles
- env examples
- migrations
- public APIs
- CLI entrypoints
- skills and prompts
- monitoring or deploy definitions

## Workflow

### 1. Establish Window

Determine the scan window from args. Default to 7 days.

Use git and GitHub when available:

```bash
git log --since="<window>" --oneline
gh pr list --state merged --search "merged:>=<date>" --json number,title,mergedAt,author,headRefName,url
```

If GitHub CLI is unavailable, use git history only and report that PR metadata was not checked.

### 2. Classify Changes

Group recent changes by drift risk:
- setup or install behavior
- commands or scripts
- CI or deploy workflows
- infrastructure or monitoring
- environment variables or secrets names
- public APIs or user-facing behavior
- data models or schemas
- skill or agent behavior
- ownership or handoff guidance

Ignore changes that clearly do not affect docs:
- formatting-only changes
- test-only changes with no new behavior
- generated lockfile churn unless setup instructions changed
- private scratch files
- vendored or generated paths (`node_modules`, `dist`, `build`, `.venv`, `.next`, `target`, `out`)

### 3. Inspect Relevant Docs

For each risk group, inspect the docs most likely to mention it.

Look for:
- stale commands
- missing commands
- stale path names
- wrong environment variables
- wrong schedules
- wrong service names
- missing ownership notes
- obsolete setup steps
- docs claiming work is not done when it is now done
- docs claiming work is live when code changed behavior

### 4. Optional Live Verification

Only perform live verification if the project config explicitly asks for it and the required auth/tools are available.

Examples:
- `gcloud` to verify Cloud Run jobs
- `bq` to verify datasets or tables
- `gh` to verify workflow names or repo settings

If live verification is not available, separate "repo-confirmed drift" from "needs live verification."

### 5. Decide Output

Every finding must include:
- changed source evidence
- doc location
- why the doc may be stale
- recommended edit
- confidence: high, medium, or low

High confidence:
- command/path/name changed and docs still reference old value
- docs say a thing is TODO but recent PR shipped it
- workflow or script behavior changed and runbook is stale

Medium confidence:
- behavior likely changed but docs wording is broad
- docs omit a new important setup or operational step

Low confidence:
- possible mismatch but needs owner judgment or live verification

### 6. Draft Edits

Draft concrete edits for high-confidence drift.

Do not rewrite whole docs unless needed. Prefer surgical patches.

If `--greenlit-pr` is present:
- apply high-confidence doc edits only
- run formatting if relevant
- create a docs-only branch
- open a PR titled `chore: reconcile docs with recent changes`

Without `--greenlit-pr`, produce a report and draft patches but do not edit files.

## Output Format

```text
Docs drift
Window: <window>

Summary
- <count> high-confidence drift items
- <count> medium-confidence review items
- <count> low-confidence notes

High confidence
- <source change> -> <doc path>: <recommended edit>

Needs review
- <item and why judgment is needed>

No drift found
- <important surfaces checked>

Draft edits
- <patch summary or exact suggested wording>

Next
- <one recommended action>
```

For cloud routines, keep the report self-contained and link PRs or commits when possible.

## Hard Rules

- Do not edit code.
- Do not create a PR unless explicitly greenlit.
- Do not treat live infrastructure claims as verified unless actually checked.
- Do not bury high-confidence stale docs under broad summaries.
- Do not rewrite docs stylistically.
- Do not update docs based only on failed experiments unless the final state is clear.
- Do not include secrets or credential values in reports or patches.
- When formatting in `--greenlit-pr` mode, scope formatting to files this skill is editing. Never reformat unrelated files.
- Operate against the repo's default branch unless instructed otherwise. Never base a docs PR on a feature branch.
- Do not edit `.claude/docs-drift.md` or this skill's own files (recursion guard).
- If high-confidence edits would touch more than 10 files, stop and present the report even with `--greenlit-pr`. Hand control back to the user for scope review.
- Do not edit a doc when the underlying change was reverted later in the window.
- Prefer exact commands, paths, service names, and dates.
