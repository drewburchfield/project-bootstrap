# Changelog

## [1.5.1] - 2026-07-16

### Added
- Review Suite spec 1.1.0: seventh lens `spec-conformance` (adapted from mattpocock/skills code-review Spec axis) — per-requirement conformance matrix, scope-creep sweep, skip-with-reason when no spec source
- Fowler smell baseline (12 smells) appended to `simplify` pass, also from mattpocock code-review Standards axis
- Eval fixture `sandbox-spec` (5 seeded conformance defects + lane-discipline distractor) and variant eval run `20260716T152713Z-spec-conformance-variants` (matrix variant won; minimal port failed lane discipline 2/3)

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
