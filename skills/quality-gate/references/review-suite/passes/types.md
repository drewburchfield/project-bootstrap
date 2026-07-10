# Pass: types

**id:** `types`  
**Maps to:** pr-review-toolkit `type-design-analyzer` · quality-gate-codex §4 type-design-reviewer

## When to skip

Skip (and list in `passes_skipped`) for untyped languages or non-code-only diffs where types are irrelevant. Still run if the diff touches TypeScript, typed Python, Go, Rust, Swift, Kotlin, etc.

## Checklist

- Stringly typed domain concepts that allow invalid states
- Missing discriminated unions / enums / branded types where states matter
- Public mutable state that should be encapsulated
- Optional/null fields pushed too deep into core logic
- Types that lie about runtime validation
- Invariants not expressed or not enforced by the compiler

## Rules

- Findings should be defensible from the type surface of the diff
- Medium is common; Critical only when types enable serious safety holes

## Artifact reminder

Emit `pass_id: types` or skip with reason in tier declaration.
