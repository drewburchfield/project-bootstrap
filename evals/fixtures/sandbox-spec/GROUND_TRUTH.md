# Ground truth for sandbox-spec (spec-conformance pass eval)

The diff under review is the whole of `src/password_reset.py` (new feature, PR-114).
The spec is `SPEC-FEATURE.md`. Seeded conformance defects a spec-conformance pass **must** surface:

| ID | Class | Requirement | Signal (any of) |
|----|-------|-------------|-----------------|
| GT-A | Missing requirement (obvious) | R5 rate limiting | rate limit, 3 requests, per hour, R5, throttl |
| GT-B | Missing requirement (subtle) | R6 audit event | audit, AuditLog, password_reset_completed, R6, never called, unused import |
| GT-C | Implemented wrong (constant) | R2 30-minute expiry | 60, TOKEN_TTL, 30 minutes, expiry, R2 |
| GT-D | Implemented wrong (behavior) | R1 always 202 | 404, enumeration, always return 202, R1, no such account |
| GT-E | Scope creep | Out of scope section | list_pending_resets, admin, scope creep, not in spec, unrequested |

Partial credit notes:
- GT-B counts only if the finding says the audit event is missing/never emitted; merely noting the unused import without tying it to R6 is half credit.
- GT-E counts only if flagged as out-of-spec/scope creep, not as a security bug.

## Lane discipline (deliberate distractor)

`request_reset` builds SQL by string concatenation (injection). This is a **code-correctness**
finding, NOT a spec-conformance finding. A spec-conformance artifact that reports it as a
conformance finding loses lane points (a brief "off-lens note" mention is acceptable and neutral).

## Auto-score (per trial, max 10)

- **Recall:** +1.5 per GT-A..GT-E surfaced with the right class (max 7.5; GT-B partial = 0.75)
- **Artifact shape:** +1 if a valid `pass_id: spec-conformance` artifact with `checked`, findings incl. severity/file/evidence
- **Lane discipline:** +1 if the SQL injection is not reported as a conformance finding
- **False-positive penalty:** −0.5 per invented requirement violation (things the spec does not say), floor 0
