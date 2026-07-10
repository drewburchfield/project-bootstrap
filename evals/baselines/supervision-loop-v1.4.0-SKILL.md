---
name: supervision-loop
description: Use when the user wants to check in on, supervise, or catch up on another developer ("what did X do today", "catch me up on X", "review my offshore dev's work", "review my contractor's PRs", "review my teammate's PRs"), consolidate that teammate's Slack/GitHub/Linear activity into one brief, draft feedback or replies, or run a recurring teammate or offshore dev management loop. Use this rather than quality-gate when the PRs being reviewed belong to someone else.
version: 1.0.0
---

# Supervision Loop

Supervision loop turns developer activity across Slack, GitHub, Linear, and the local repo into one current management brief. It is built for recurring Claude Code routines, `/loop`, and manual checks.

The loop is not a notification stream. Its job is to advance work: review what changed, infer what Drew already handled, identify blockers, draft feedback, and suggest next assignments.

## Invocation

Preferred:

```bash
/supervision-loop
```

If the current repo has `.claude/supervision-loop/default.md`, use it automatically.

Hot mode during active review:

```bash
/loop 10m /supervision-loop --hot
```

Scheduled routine profile example:

```text
10:00 AM America/Chicago
4:00 PM America/Chicago
```

## Profile Loading

Use one repo-local, gitignored folder for private config and runtime state:

```text
.claude/supervision-loop/
```

If no profile is provided:
1. Use `.claude/supervision-loop/default.md` if present.
2. If none exists, ask for the target developer, repo, Slack surface, GitHub repo, Linear team or prefix, and review policy.

## Local State

Use the same repo-local, gitignored folder for state:

```text
.claude/supervision-loop/
  default.md
  state.json
  current-brief.md
  history/
  review-cache/
  pattern-log.md
```

Create the directory if it does not exist. Do not commit it.

Before writing anything to `.claude/supervision-loop/`, verify the path is covered by `.gitignore`. If it is not, stop and ask the user to add it (suggested entry: `.claude/supervision-loop/`). The folder contains private feedback drafts, pattern observations about a teammate, and consolidated Slack/Linear context. None of it should ever land in a commit.

State is an aid, not the source of truth. Each run must reread live Slack, GitHub, Linear, and repo state. Use state to avoid re-running expensive review on the same PR head SHA or merged commit range.

Each run must:
- overwrite `.claude/supervision-loop/current-brief.md` with the latest consolidated brief
- append a timestamped copy under `.claude/supervision-loop/history/`
- update `.claude/supervision-loop/state.json` with observed PR SHAs, merged ranges, source timestamps, cached review keys, and addressed-state evidence
- avoid requiring a manual acknowledgement command

The visible brief should always be "what matters now." If multiple scheduled runs happened while Drew was away, the next brief must consolidate them into the current state rather than presenting stale run-by-run updates.

## Core Workflow

Run these phases every time.

### 1. Read the Profile

Extract:
- target developer name and handles
- local repo path
- GitHub owner/repo
- Slack channels and DMs to inspect
- Linear workspace, team, prefixes, and relevant statuses
- review policy
- write policy
- schedule expectations
- risk notes

### 2. Gather Live Inputs

All configured source types are mandatory unless the profile marks one optional.

Slack:
- target developer updates
- questions to Drew
- blockers
- end-of-day update if relevant
- Drew replies that may have addressed prior blockers
- project channel messages that create work for the target developer

GitHub:
- open PRs authored by the target developer
- PRs where the target developer pushed new commits
- merged PRs authored by the target developer
- review comments, approvals, requested changes, Devin or other automated review findings
- CI and deploy workflow status
- Drew reviews, comments, approvals, or requested changes

Linear:
- issues assigned to the target developer
- issues recently commented on or moved by the target developer
- issues assigned to Drew that are waiting on developer execution
- stale In Progress or In Review work
- Drew comments, status changes, assignments, or new issues that addressed prior items

Local repo:
- fetch latest state if needed
- inspect diffs for PRs or merged ranges
- run project-specific verification only when required by review policy

Health:
- only include external health or alerting signals if the profile explicitly opts in, or if a live alert clearly correlates with target developer work

### 3. Infer Addressed State

Do not require Drew to maintain explicit acknowledgements.

Treat an item as addressed if live evidence shows Drew advanced it:
- Slack reply answering the question or giving next direction
- GitHub review, comment, approval, requested changes, or post-merge comment
- Linear comment, status move, reassignment, or new ticket
- commit, merge, revert, or fix-forward touching the same issue

If the evidence is ambiguous, mark it as "possibly addressed" and keep the recommendation conservative.

### 4. Review Work

Open PRs ready for review:
- run full quality-gate style review for each new PR head SHA
- include CI, Devin, review comments, tests, diff review, and Linear fit
- draft approval, requested changes, or feedback
- do not post the review or approve without Drew's approval

Merged PRs:
- bundle unaddressed merged PRs into a post-merge review batch
- review the merged commit range against main
- identify regressions, missing tests, unresolved review findings, deploy gaps, or follow-up tickets
- draft feedback or follow-up Linear work
- recommend revert or fix-forward only when warranted
- do not revert or create tickets without Drew's approval

Caching rule:
- run expensive review once per new PR head SHA or merged commit range
- reuse cached findings when nothing changed
- update status every run

### 5. Draft Advancing Actions

Every item must resolve to one of:
- already handled
- no action
- draft Slack reply
- draft GitHub PR feedback
- draft Linear comment
- draft next assignment
- draft new ticket
- needs Drew judgment

The loop may draft anything. It must not send, post, approve, request changes, merge, revert, assign, or create tickets unless Drew explicitly approves in the current session.

When drafting any message that will be sent on Drew's behalf (Slack replies, Linear comments, GitHub PR feedback), match Drew's voice from the global writing profile: short sentences, "Hey [name]," opener when applicable, "Let me know" closer, sign as "Drew", no corporate buzzwords, never use em dashes or en dashes (use commas, colons, periods, or parentheses instead). If a project CLAUDE.md or a per-developer note overrides voice, follow that override.

### 6. Track Patterns Quietly

Append only useful coaching patterns to `.claude/supervision-loop/pattern-log.md`:
- repeated review findings
- missed tests
- misunderstood architecture
- strong improvements
- unclear ticket scopes causing rework
- places where Drew was the bottleneck

Surface patterns only when they help the current feedback or delegation.

## Output Format

Keep the brief concise and current.

```text
Supervision brief: <target>
Updated: <local time>

Top line
- <no action / needs Drew / draft ready / blocker>

Needs Drew approval
- <drafts that require send, post, assign, review, approve, merge, or revert approval>

Already addressed
- <items Drew already advanced via Slack, GitHub, Linear, or commits>

PR review
- Open PRs: <quality-gate status and draft feedback>
- Merged PRs: <post-merge batch status and follow-ups>

Linear
- Current work
- Stale or unclear work
- Next assignment from Linear
- Possible new ticket from Slack or client context

Slack
- End-of-day update status if configured
- Questions answered or unanswered
- Draft reply

Pattern notes
- <only if useful>
```

## Scheduling Guidance

For offshore developer supervision, prefer twice daily scheduled routines rather than a constant loop:
- morning catch-up
- afternoon end-of-day review

Use `/loop` only during active review windows.

## Hard Rules

- Do not rely only on the last scheduled run. Always consolidate the current live state.
- Do not make Drew do checkpoint homework.
- Do not repeat old noise if Drew has already advanced it.
- Do not auto-send or auto-write by default.
- Do not treat status updates as blockers.
- Do draft cadence replies when they advance feedback, unblock work, or assign the next task.
- Do not bury blockers below routine status.
- Do not claim a PR is clean without checking CI, reviews, and relevant merged/deploy state.
