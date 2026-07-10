# Host adapter: OpenCode

**Default tier path:** T2 sequential.

## Execution

1. Do not assume Claude plugins exist.
2. Run each pass checklist from `passes/*.md`; emit artifacts.
3. Use subagents only if the host exposes them and isolation is real.
4. tier_declaration: `adapter: opencode-sequential`, `tier: T2` (or T3 if parallel isolated).

## Forbidden

- `/review-pr`, pr-review-toolkit IDs, Agent tool assumptions
- Unconditional external bot waits
