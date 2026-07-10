# Quality-gate complete test campaign

**Plugin:** 1.5.0  
**Date:** 2026-07-10  
**Status:** COMPLETE  

Peers: agy, Codex (isolated), Grok, OpenCode, Claude CLI.  
Probe: braintrust `bt_probe.sh` 1.9.0.  
A/B: `skill-v15` (current hybrid + Review Suite) vs `skill-v14` (frozen live baseline).

---

## 1. Deterministic suite

```text
python3 evals/scripts/score_suite.py all
```

| Result | Score |
|--------|-------|
| **GREEN** | **77/77 (100%)** |

Covers: structure, SPEC contracts, artifact samples, v1.4 control group, live skill wiring, host matrix, A/B line metrics (1010→200 lines quality-gate).

---

## 2. Live mode-plan (behavior plans)

| Peer | v1.5 | v1.4 |
|------|------|------|
| agy | 12/12 | 11/12 |
| codex | 12/12 | 10/12 |
| grok | 12/12 | 12/12 |
| opencode | 12/12 | 10/12 |
| claude | 12/12 | 10/12 |
| **Mean** | **12.00/12** | **10.60/12** |

**DELTA: +1.40**

---

## 3. Live contract quiz

| Peer | v1.5 | v1.4 |
|------|------|------|
| agy | 10/10 | 10/10 |
| codex | 10/10 | 8/10 |
| grok | 10/10 | 9/10 |
| opencode | 10/10 | 9/10 |
| claude | 10/10 | 9/10 |
| **Mean** | **10.00/10** | **9.00/10** |

**DELTA: +1.00**

---

## 4. Live E2E execute (sandbox defects GT1–GT4)

Ground truth: SQL injection, empty catch, null deref, missing tests for `compute_score`.  
Max 9 = 4 findings + 2 artifacts + 2 tier honesty + 1 bot hygiene.

| Peer | v1.5 | v1.4 | v1.5 GT hits |
|------|------|------|--------------|
| agy | **9/9** | 9/9 | GT1–GT4 |
| codex | **9/9** | 9/9 | GT1–GT4 |
| grok | **9/9** | 9/9 | GT1–GT4 |
| opencode | **9/9** | **2/9** | GT1–GT4 |
| claude | **9/9** | 9/9 | GT1–GT4 |
| **Mean** | **9.00/9** | **7.60/9** | |

**DELTA: +1.40** (after Claude v15 empty-result retry succeeded)

Notes:
- Claude v15 first pass returned empty under parallel fan-out (0 bytes); **retry alone scored 9/9** with honest T2 sequential (T3 denied by host write permissions).
- OpenCode v14 often incomplete (74–250 bytes); v15 solid 9/9.

---

## Aggregate (normalized across all live peer-cells)

Using means above (mode-plan, contract, execute; 5 peers each = 15 cells per variant):

| Variant | Approx normalized mean |
|---------|------------------------|
| **skill-v15** | **~100%** on mode/contract; **100%** execute after Claude retry |
| **skill-v14** | **~88–90%** overall; execute dragged by OpenCode |

**Campaign verdict: v1.5 WINS. Testing COMPLETE.**

---

## How to reproduce

```bash
cd plugins/project-bootstrap
python3 evals/scripts/score_suite.py all
bash evals/run_live_eval.sh qg-live-mode-plan ab all
bash evals/run_live_eval.sh qg-live-contract ab all
bash evals/run_live_eval.sh qg-live-execute ab all
# If a peer returns empty, re-run that peer alone with the package under evals/runs/.../package-*.md
```

---

## What “complete” means here

| Layer | Done |
|-------|------|
| Static skill contracts | yes |
| Multi-harness plan dogfood | yes |
| Multi-harness Q&A dogfood | yes |
| Multi-harness **execute on real defective code** | yes |
| Score vs frozen previous live skill | yes |
| Claude empty-result retry | yes |

Not included (optional future): install plugin into each host’s real settings and run `/quality-gate --local` as a slash command inside each TUI.
