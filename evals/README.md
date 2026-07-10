# project-bootstrap evals

Deterministic Review Suite checks (Phase 0–1b). No LLM peers required for green.

## Why

Material skill changes need fixture-backed signals. This harness validates:

1. **Structure** — Review Suite SPEC, six pass files, five host adapters
2. **Contracts** — artifact + tier + capability probe language in SPEC
3. **Artifacts** — sample runs: valid T2 Pass, invalid T1 Pass, rubber-stamp none_found
4. **Host matrix** — non-Claude adapters forbid toolkit-only paths; Claude allows T3
5. **Baseline (v1.4.0 control)** — frozen skills under `evals/baselines/` still Claude-shaped
6. **Wired** — live skills reference Review Suite, multi-host, no bare Devin sleep
7. **A/B (`ab`)** — v1.4.0 vs live improvement (suite wired, leaner quality-gate, debt cleared)

## Quick start

```bash
cd /path/to/project-bootstrap
bash evals/run_eval.sh
python3 evals/scripts/score_suite.py ab
python3 evals/scripts/score_suite.py wired
```

`evals/runs/` is gitignored.

## Layout

```text
evals/
  baselines/               # frozen v1.4.0 SKILL.md snapshots
  samples/                 # YAML suite runs
  scripts/score_suite.py
  run_eval.sh
skills/quality-gate/references/review-suite/
```

## Pass criteria

`score_suite.py all` must exit 0 (77 checks as of 1.5.0).

## Live multi-harness dogfood (braintrust-style)

Text scoring cannot prove host behavior. Live evals **inject the skill package into peer CLIs** (agy, Codex, Grok, OpenCode, Claude) the same way braintrust consults work, then auto-score plans/answers.

```bash
# Mode-plan A/B: v1.5 package vs frozen v1.4 skill (all peers)
bash evals/run_live_eval.sh qg-live-mode-plan ab all

# Contract quiz A/B
bash evals/run_live_eval.sh qg-live-contract ab all

# E2E execute on sandbox repo (known defects GT1–GT4)
bash evals/run_live_eval.sh qg-live-execute ab all

# Full matrix (all live fixtures x both variants)
bash evals/run_live_eval.sh matrix
```

Uses braintrust `bt_probe.sh` when available (`../braintrust/scripts/bt_probe.sh`). Writes `evals/runs/<ts>-live-<fixture>/` with packages, per-peer `result.txt`, `score.json`, `summary.tsv`.

| Fixture | What peers must do | Max |
|---------|-------------------|-----|
| `qg-live-mode-plan` | Plan scenarios A–F (Claude/Codex/Grok/OpenCode bots/agy) | 12 |
| `qg-live-contract` | 10 short contract questions | 10 |
| `qg-live-execute` | **Run** Review Suite on `fixtures/sandbox-qg` code; emit findings + tier | 9 |

### Execute ground truth (`sandbox-qg`)

| ID | Defect |
|----|--------|
| GT1 | SQL injection via string concat |
| GT2 | Empty `except` / silent failure |
| GT3 | Null deref in `format_display_name` |
| GT4 | `compute_score` has no tests |

Score: 4 finding hits + 2 artifact shape + 2 tier honesty (Blocked, not Pass) + 1 bot hygiene.

Heuristic scores are smoke signals; spot-check `result.txt` when peers diverge.
