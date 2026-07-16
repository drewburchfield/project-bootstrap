# Host adapter: Claude Code

**Default tier path:** T3 when pr-review-toolkit is available.

## Preferred execution

1. Probe: toolkit / Agent tool / `/review-pr` available?
2. If yes: run parallel reviewers (or `/review-pr`) covering all seven suite lenses.
3. Map toolkit agent names → suite pass ids:
   - code-reviewer → code-correctness
   - silent-failure-hunter → silent-failures
   - pr-test-analyzer → tests
   - type-design-analyzer → types
   - comment-analyzer → comments
   - code-simplifier → simplify
   - (no toolkit agent) → spec-conformance: run a general-purpose subagent with `passes/spec-conformance.md` and the spec source; skip with reason if no spec source
4. Ensure each pass has a valid artifact (convert toolkit output if needed).
5. Probe external bots from project-meta; wait only if configured.
6. Synthesize + tier_declaration `adapter: claude-pr-review-toolkit`, `tier: T3`.

## Fallback

If toolkit missing: sequential T2 using `passes/*.md` checklists in-process. Label `tier: T2`, never T3.

## Forbidden

- Claiming T3 after only a manual diff skim
- Unconditional Devin sleep when bots not configured
