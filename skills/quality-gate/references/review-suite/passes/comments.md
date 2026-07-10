# Pass: comments

**id:** `comments`  
**Maps to:** pr-review-toolkit `comment-analyzer` · quality-gate-codex §5 comment-reviewer

## Checklist

- Comments or docs that contradict the code
- Comments describing old behavior after the diff changed it
- TODOs without useful context or tracking
- Public API docs missing new params, errors, or returns
- Misleading test names
- Comment rot in touched files

## Rules

- Prefer deleting misleading comments over adding more text
- High when comment would cause incorrect production use

## Artifact reminder

Emit `pass_id: comments` with full artifact contract.
