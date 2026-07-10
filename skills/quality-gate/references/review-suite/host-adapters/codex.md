# Host adapter: Codex

**Default tier path:** T2 sequential. Optional Clawpatch as extra evidence.

## Preferred execution

1. Probe: `clawpatch` on PATH? If yes, doctor/map/review as evidence only (not a lens replacement).
2. For each mandatory pass file in `passes/`, run the checklist against the diff (prefer isolation between passes when subagents available).
3. Emit full pass artifacts per SPEC.
4. Optional parallel subagents only if user/host supports and isolation is real → then T3.
5. tier_declaration: `adapter: codex-sequential` or `codex-clawpatch+sequential`, `tier: T2` (or T3 if parallel isolated).

## Reference skill

Personal skill `quality-gate-codex` already implements T2 + Clawpatch. Align it to load this suite as source of truth so checklists do not drift.

## Forbidden

- Invoking `/review-pr` or pr-review-toolkit agent IDs as required steps
- Gate Pass without six (or skip-justified) pass artifacts
