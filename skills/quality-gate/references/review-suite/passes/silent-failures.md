# Pass: silent-failures

**id:** `silent-failures`  
**Maps to:** pr-review-toolkit `silent-failure-hunter` · quality-gate-codex §2

## Checklist

- Empty catch blocks / swallowed errors
- Generic catch-all that hides specific failures
- Fallback logic that continues after failure without signal
- Missing error propagation
- Swallowed promise rejections / fire-and-forget without handling
- Error paths that log but still return success
- Defaults that turn bad upstream data into plausible output
- Retry/timeout/cancellation that masks real failure

## Rules

- Silent failures that can corrupt data, lose work, or hide automation failure are usually Critical/High
- This pass is mandatory for code diffs

## Artifact reminder

Emit `pass_id: silent-failures` with full artifact contract (SPEC.md).
