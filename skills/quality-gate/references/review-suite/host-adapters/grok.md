# Host adapter: Grok

**Default tier path:** T2 sequential. **T3 multi-subagent deferred** until isolation is verified.

## Preferred execution (ship now)

1. Sequential map over `passes/*.md` with full artifacts.
2. Optional: map-reduce (structured multi-lens output + synthesis pass).
3. tier_declaration: `adapter: grok-sequential`, `tier: T2`.

## Bundled `/review`

Single persona subagent = **T1** if used alone. Do not claim suite Pass from `/review` only.

## Future T3

Only if capability probe shows independent subagent contexts: spawn one subagent per pass file, synthesize. Then `adapter: grok-multi-subagent`, `tier: T3`.

## Forbidden

- Claiming T3 without isolation verification
- Gate Pass after one generic review
- Invoking `/review-pr` or pr-review-toolkit agent IDs as required steps
