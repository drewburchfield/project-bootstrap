# Pass: simplify

**id:** `simplify`  
**Maps to:** pr-review-toolkit `code-simplifier` · quality-gate-codex §6 simplifier

## When

Run **after** correctness-oriented passes (code-correctness, silent-failures, tests). Still required for suite Pass on code diffs.

## Checklist

- Unnecessary abstraction, duplication, dead code
- Over-generalized config for a single use
- Conditionals or state machines that can be clearer without behavior change
- Local style churn that should be avoided (flag as Low or drop)
- Opportunities to reduce support burden without rewrite

## Rules

- Do not suggest simplification that changes behavior or broadens scope
- Findings are often Medium/Low; rarely Critical
- Do not rewrite working code for taste alone

## Artifact reminder

Emit `pass_id: simplify` with full artifact contract.
