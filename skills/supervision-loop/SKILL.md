---
name: supervision-loop
description: >
  Use when the user wants to check in on, supervise, or catch up on another developer,
  consolidate their Slack/GitHub/Linear activity into one brief, draft feedback, or run a
  recurring teammate management loop. Prefer this over quality-gate when PRs belong to someone else.
version: 1.5.0
---

# Supervision Loop

Turns teammate activity across configured sources into one management brief. Advances work: review what changed, infer what the **operator** already handled, draft feedback, suggest next assignments.

**Not** a notification stream. Draft-only by default (no auto-send/post/approve/merge).

## Invocation

```bash
/supervision-loop
```

If `.claude/supervision-loop/default.md` exists, use it. Hot: `/loop 10m /supervision-loop --hot` when the host supports loops.

## Profile

Repo-local gitignored folder:

```text
.claude/supervision-loop/
  default.md
  state.json
  current-brief.md
  history/
  review-cache/
  pattern-log.md
```

Ensure `.gitignore` covers this path before writing private drafts.

### Profile fields (generic)

| Field | Meaning |
|-------|---------|
| operator | Who runs the loop (name, voice skill path optional) |
| target developer | Handles on GitHub/Slack/Linear |
| sources | each of github/slack/linear/localRepo: `required` \| `optional` \| `off` |
| review policy | suite required? cache by SHA? |
| write policy | draft-only default |
| external bots | auto \| list \| none |

If no profile: use `default.md` or ask for target, repo, sources, review policy.

## Capability probe

Same idea as quality-gate:

- **github** required fails → block run with hint
- **slack/linear** optional + missing tools → skip section, note unavailable
- **Review Suite** host adapter from quality-gate references
- **external_bots** only if configured; no blind wait

## Workflow

### 1. Read profile

Operator, target, sources, policies.

### 2. Gather live inputs

Only configured sources. Re-read live each run; state is aid not truth.

**GitHub (typical required):** open/merged PRs by target, comments, CI, operator reviews.  
**Slack (optional):** updates, questions, blockers, operator replies.  
**Linear (optional):** assigned/stale issues, operator actions.  
**Local repo:** diffs for PRs under review when needed.

### 3. Infer addressed state

No homework for the operator. Mark addressed when live evidence shows they advanced it (reply, review, status move, commit). Ambiguous → “possibly addressed,” stay conservative.

### 4. Review work (Review Suite)

For each open PR with a **new head SHA** where the operator is the responsible reviewer:

1. Load `skills/quality-gate/references/review-suite/SPEC.md` + host adapter.
2. Run **Review Suite** at T2 or T3 when possible:
   - Claude Code: parallel pr-review-toolkit / mapped agents when available.
   - Other hosts: sequential pass files or host subagents (see adapters). **Do not** require Claude-only tool IDs.
3. Emit pass artifacts + tier_declaration; synthesize findings with severity.
4. Also check CI, human comments, external bots if configured, ticket fit.
5. Cache under `review-cache/<pr>-<sha>.md` until SHA changes.
6. Draft approval / changes / feedback in **operator voice** (profile). Never post without operator approval this session.

If suite cannot run: do a labeled **manual/T1** review; **do not** claim quality-gate or Review Suite Pass.

**Merged PRs:** batch unaddressed ranges; suite or manual on merge range; draft follow-ups; no revert/ticket without approval.

### 5. Draft advancing actions

Buckets: already handled | no action | draft Slack/GitHub/Linear | next assignment | new ticket | needs operator judgment.

Draft only. Match operator voice from profile (or neutral professional if no voice skill).

### 6. Patterns

Append useful coaching notes to `pattern-log.md`; surface only when useful now.

## Output

```text
Supervision brief: <target>
Operator: <operator>
Updated: <local time>

Top line
- <no action | needs operator | draft ready | blocker>

Needs operator approval
- <drafts that require send/post/assign/review/merge>

Already addressed
- <items advanced via live evidence>

PR review
- Open: <Review Suite tier/status + draft feedback>
- Merged: <post-merge batch>

Tracker / Slack
- <only configured sources>

Pattern notes
- <if useful>
```

## Hard rules

- Consolidate live state; do not only replay last scheduled run.
- No auto-send/post/approve/merge/revert.
- Do not claim Review Suite / quality-gate without suite execution (artifacts + tier).
- Manual review must be labeled manual/T1.
- Sources marked optional must not fail the whole run when missing.
- Sources marked required missing → blocked with setup hint.
