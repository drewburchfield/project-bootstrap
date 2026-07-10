# project-bootstrap evals

Deterministic Review Suite checks (Phase 0 / 1a). No LLM peers required for green.

## Why

Material skill changes need fixture-backed signals. This harness validates:

1. **Structure** — Review Suite SPEC, six pass files, five host adapters
2. **Contracts** — artifact + tier + capability probe language in SPEC
3. **Artifacts** — sample runs: valid T2 Pass, invalid T1 Pass, rubber-stamp none_found
4. **Host matrix** — non-Claude adapters forbid toolkit-only paths; Claude allows T3
5. **Baseline** — documents current quality-gate/ship-loop/supervision Claude coupling (migration debt)

## Quick start

```bash
cd /path/to/project-bootstrap
bash evals/run_eval.sh
# or
python3 evals/scripts/score_suite.py
python3 evals/scripts/score_suite.py artifacts
```

`evals/runs/` is gitignored.

## Layout

```text
evals/
  README.md
  run_eval.sh
  scripts/score_suite.py
  samples/                 # YAML suite runs for artifact validation
  fixtures/                # future LLM contract quizzes (optional)
  runs/                    # gitignored
skills/quality-gate/references/review-suite/
  SPEC.md
  synthesis.md
  passes/*.md
  host-adapters/*.md
```

## Pass criteria

`score_suite.py all` must exit 0.

Baseline checks **expect** current skills to still mention `/review-pr`, Devin, pr-review-toolkit. That is intentional until Phase 1b rewrites wire the suite.

## Adding tests

1. Add a sample under `evals/samples/` for artifact edge cases.
2. Extend `validate_run()` in `score_suite.py` if the contract grows.
3. Re-run `bash evals/run_eval.sh`.

## Later (not Phase 0)

- Multi-peer LLM contract quizzes (braintrust-style)
- Execution evals that parse live gate transcripts
