# Fixture: qg-live-execute (end-to-end Review Suite on real code)

You are running **quality-gate --local** (or equivalent) using **only** the skill + Review Suite in this package.

## Code under review

The package includes a sandbox repository snapshot:

- `src/user_service.py`
- `tests/test_user_service.py`

Treat this as the full diff / local changes. **Execute** the Review Suite (do not only plan).

## Required output

1. **Capability probe** for your host (assume host = the CLI you are: Claude/Codex/Grok/OpenCode/agy as appropriate if labeled; else state your host as `other`).
2. **Run every mandatory pass** (skip `types` only if you classify the language as untyped — Python is typed enough to note optional type issues, but `types` may be light).
3. Emit **pass artifacts** for at least: `code-correctness`, `silent-failures`, `tests`, `comments`, `simplify` (and `types` optional).
4. Emit **tier_declaration** with `gate_status` (must be Pass | Blocked | Incomplete).
5. List **Findings** with severity and `file:line` when possible.

## Output format (required)

```yaml
tier_declaration:
  host: ...
  adapter: ...
  tier: T2|T3|T1|T0
  execution_mode: parallel|sequential|single
  passes_completed: [...]
  capabilities: {...}
  gate_status: Pass|Blocked|Incomplete

findings:
  - severity: Critical|High|Medium|Low
    file: path
    line: N
    title: ...
    evidence: ...
    pass_id: code-correctness|silent-failures|tests|...

passes:
  - pass_id: code-correctness
    checked: [...]
    findings: [...]
    none_found: false
  # ... other passes
```

You may use markdown fences. Prefer real issues in the code over invented ones.

## Rules

- Local mode: no PR, no bot wait.
- Non-Claude hosts must not require `/review-pr`.
- Do not claim Pass if Critical/High remain.
