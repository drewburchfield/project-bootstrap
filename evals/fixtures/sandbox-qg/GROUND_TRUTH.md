# Ground truth for sandbox-qg dogfood

Known defects that a thorough Review Suite **must** surface (any severity Critical/High counts as a hit if the issue class is correct).

| ID | Class | Pass lens | File | Signal (any of) |
|----|-------|-----------|------|-----------------|
| GT1 | SQL injection | code-correctness | `src/user_service.py` | sql injection, string concat, user_id, query, SELECT, injection |
| GT2 | Silent failure / empty catch | silent-failures | `src/user_service.py` | empty catch, bare except, pass, swallow, silent |
| GT3 | Null deref risk | code-correctness | `src/user_service.py` | None, null, format_display_name, user\[\"name\"\] without guard |
| GT4 | Missing tests for compute_score | tests | `src/user_service.py` or tests | compute_score, no test, uncovered, test gap |

Optional (bonus, not required for Pass threshold):
- connection close / resource notes
- return None after silent catch

## Auto-score

- **Finding hits:** +1 per GT1–GT4 detected in peer output (max 4)
- **Artifact shape:** +2 if all of code-correctness, silent-failures, tests appear with findings or none_found
- **Tier honesty:** +2 if tier is T2 or T3 and gate is Blocked (clean Pass would be wrong)
- **Bot hygiene:** +1 if does not invent Devin wait for this local fixture
- **Max:** 9

Gate status should be **Blocked** (Critical/High remain), not Pass.
