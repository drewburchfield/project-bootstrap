# Fixture: quality-gate contract quiz (LLM optional; Phase 0 docs only)

Use with multi-peer inject later. Deterministic scorer does not grade this file yet.

## Questions

1. If `review.externalBots` is empty, do you `sleep 60` for Devin? → **No.**
2. Can tier T1 emit gate_status Pass? → **No** (Incomplete only).
3. What is minimum tier for suite Pass? → **T2 or T3** with all pass artifacts.
4. Is T2 equivalent to Claude parallel toolkit? → **No** (methodology coverage only).
5. Where do lens checklists live? → **`references/review-suite/passes/`**
6. Who owns merge when ship-loop drives? → **ship-loop**
7. Codex adapter may require `/review-pr`? → **No.**
