# Changelog

## [1.5.0] - 2026-07-10

### Added
- Portable Review Suite (SPEC, six lenses, host adapters for Claude Code, Codex, Grok, OpenCode, agy)
- Deterministic evals (`evals/scripts/score_suite.py`) and live multi-harness dogfood (`evals/run_live_eval.sh`)
- Frozen v1.4.0 skill baselines and sandbox GT execute fixture

### Changed
- quality-gate hybrid rewrite (capability probe, tier honesty, no unconditional Devin sleep)
- ship-loop and supervision-loop wire to Review Suite; supervision uses generic operator

### Previously
- 1.4.0: docs-drift skill
