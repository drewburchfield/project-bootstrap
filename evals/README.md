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
