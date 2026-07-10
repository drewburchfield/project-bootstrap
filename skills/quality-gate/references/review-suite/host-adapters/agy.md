# Host adapter: agy (Antigravity / Google path)

**Default tier path:** T2 sequential.

## Execution

Same as OpenCode: sequential multi-pass from suite files; emit artifacts; label honestly.

tier_declaration: `adapter: agy-sequential`, `tier: T2`.

Watch rate limits if attempting parallel fan-out; default is sequential.

## Forbidden

- Pretending multi-agent T3 without real parallel isolated runs
- Claude-only command names (`/review-pr`, pr-review-toolkit agent IDs as required steps)
