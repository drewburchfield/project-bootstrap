# Review Suite synthesis

Run after all mandatory pass artifacts are present.

## Steps

1. **Collect** all pass artifacts and any optional signals (Clawpatch, external bot comments, CI).
2. **Dedupe** findings that describe the same root cause (keep highest severity, merge evidence).
3. **Normalize severity** to Critical / High / Medium / Low.
4. **Classify deferrals:** Medium/Low may be deferred with an explicit reason; Critical/High only with operator approval.
5. **Set gate_status:**
   - `Pass` if tier is T2 or T3, all artifacts valid, no unresolved Critical/High, Mediums handled
   - `Blocked` if Critical/High remain or required verification failed
   - `Incomplete` if tier is T1/T0 or artifacts missing
6. **Emit** final findings list + tier_declaration (SPEC.md).

## Output shape (human)

```markdown
## Review Suite synthesis

**Tier:** T2 (sequential) · **Adapter:** codex-sequential · **Gate:** Blocked

### Findings
- [High] title (`path:line`): evidence → fix
- [Medium] ... (deferred: reason)

### Passes
- code-correctness: 2 findings
- silent-failures: none found (checked: empty catch, promise rejection, …)
- ...

### Verification
- command: result
```

## Forbidden

- Gate Pass without all mandatory pass artifacts
- Claiming T3 when execution was a single continuous skim
- Claiming external bot review when bots were not configured or did not run
