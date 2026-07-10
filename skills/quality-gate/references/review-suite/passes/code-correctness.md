# Pass: code-correctness

**id:** `code-correctness`  
**Maps to:** pr-review-toolkit `code-reviewer` · quality-gate-codex §1

## Checklist (examine; list those you checked in the artifact)

- Logic bugs and incorrect edge-case behavior
- Mismatches with repo conventions (CLAUDE.md / AGENTS.md / nearby patterns)
- Resource leaks, race conditions, state bugs, unsafe async
- Security issues obvious from the diff (injection, XSS, command injection, secrets)
- Behavior that contradicts product intent or surrounding code
- Performance anti-patterns that matter on this path

## Rules

- Report only issues defensible from code evidence (file + line when possible)
- Prefer high-confidence findings; suppress speculative noise
- Critical/High for security and primary-path bugs

## Artifact reminder

Emit `pass_id: code-correctness` with `checked`, `line_ranges_or_files`, `findings` or `none_found: true`.
