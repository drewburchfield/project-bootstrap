# Pass: tests

**id:** `tests`  
**Maps to:** pr-review-toolkit `pr-test-analyzer` · quality-gate-codex §3 test-coverage-reviewer

## Checklist

- Changed behavior covered by tests (or justified why not)
- Error-path / boundary / permission coverage for risky changes
- Weak assertions (truthiness where exact values matter)
- Flaky timing, shared state, network without isolation
- Snapshots of implementation detail that hide regressions
- Missing integration coverage when unit tests cannot prove the change

## Rules

- Do not demand broad coverage for trivial diffs
- Untested risky core behavior is Critical/High
- Prefer focused tests that prove the changed behavior

## Artifact reminder

Emit `pass_id: tests` with full artifact contract.
