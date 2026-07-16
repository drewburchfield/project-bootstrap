# Pass: spec-conformance

**id:** `spec-conformance`
**Maps to:** mattpocock/skills code-review Spec axis (adapted; conformance-matrix variant, eval winner 20260716)

## When

Run when a spec source exists: the originating issue/ticket, a PRD under `docs/` or `specs/`,
or a spec path the operator supplied. If no spec source can be identified, skip with reason
`"no spec source"` in the tier declaration — never invent requirements.

## Procedure

1. Enumerate every requirement in the spec (numbered items, MUST/SHOULD lines, out-of-scope statements).
2. Build a conformance matrix — one row per requirement — before writing any findings:

   | Req | Status | Evidence (file:line) |
   |-----|--------|----------------------|
   | R1  | met / partial / missing / contradicted / not-verifiable | where you looked |

3. Sweep the diff once more for behavior that maps to **no** requirement row — that is scope creep,
   and anything under an explicit out-of-scope section is automatically a finding.
4. Convert every non-`met` row and every scope-creep hit into a finding.

## Rules

- Quote or cite the exact spec line for every finding; a conformance finding without a spec citation is invalid
- Stay in lane: correctness bugs that don't contradict a spec line belong to code-correctness, not here (a one-line off-lens note is fine)
- Severity: missing/contradicted requirement with security or data impact = High; other missing/contradicted = Medium; scope creep = Medium; not-verifiable, ambiguity, or a spec silence the implementation resolved one way = Low with the chosen interpretation noted
- Absence of a test is not a conformance finding (tests pass owns that)

## Artifact reminder

Emit the conformance matrix, then `pass_id: spec-conformance` with full artifact contract
(`checked`, `line_ranges_or_files`, `findings` with severity/file/evidence/fix, or `none_found: true`).
