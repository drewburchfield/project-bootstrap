# Fixture: qg-live-contract (live dogfood quiz)

Answer from **skill text in this package only**. Short bullets.

1. What is the minimum tier for a Review Suite **Pass**?
2. If `external_bots` is empty, do you sleep/wait 60s for Devin? Quote the rule.
3. On **Codex**, may you require `/review-pr` or `pr-review-toolkit` agents? What should you do instead?
4. On **Claude Code** with toolkit available, what tier path is preferred?
5. What must each pass artifact include when `none_found: true`?
6. Can tier T1 emit `gate_status: Pass`?
7. Who owns merge when **ship-loop** is driving?
8. List the six mandatory Review Suite pass ids (or say if skill only points at them).
9. What does the capability probe check before review (name at least 3 capabilities)?
10. End **GROUNDED** or **NOT GROUNDED**.

## Rubric (host auto-score)

| ID | Points if answer includes |
|----|---------------------------|
| Q1 | T2 or T3 |
| Q2 | no / never unconditional wait / only if bots configured |
| Q3 | no; sequential / pass files / quality-gate-codex / T2 |
| Q4 | T3 / parallel / pr-review-toolkit / review-pr |
| Q5 | checked / non-empty checklist |
| Q6 | no |
| Q7 | ship-loop |
| Q8 | code-correctness, silent-failures, tests, types, comments, simplify (or review-suite passes) |
| Q9 | host, bots, agent suite, clawpatch, issue tracker (any 3) |
| Q10 | GROUNDED |
| Max | 10 |
