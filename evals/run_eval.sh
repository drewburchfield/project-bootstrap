#!/usr/bin/env bash
# Project-bootstrap Review Suite eval runner (Phase 0 / 1a).
#
# Usage:
#   bash evals/run_eval.sh              # full deterministic suite
#   bash evals/run_eval.sh structure
#   bash evals/run_eval.sh artifacts
#   bash evals/run_eval.sh baseline
#   bash evals/run_eval.sh all
#
# Writes: evals/runs/<timestamp>/summary.txt
# Requires: python3, pyyaml (pip install pyyaml)

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SUITE_ARG="${1:-all}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_ROOT="evals/runs/${TS}-${SUITE_ARG}"
mkdir -p "$RUN_ROOT"

echo "project-bootstrap eval: suite=${SUITE_ARG}" | tee "$RUN_ROOT/meta.txt"
echo "root=$ROOT" | tee -a "$RUN_ROOT/meta.txt"
echo "time=$TS" | tee -a "$RUN_ROOT/meta.txt"

# Prefer venv-less system python; install pyyaml user-local if needed
if ! python3 -c "import yaml" 2>/dev/null; then
  echo "Installing PyYAML for scorer..." | tee -a "$RUN_ROOT/meta.txt"
  python3 -m pip install --user pyyaml -q
fi

set +e
python3 evals/scripts/score_suite.py "$SUITE_ARG" | tee "$RUN_ROOT/summary.txt"
RC=${PIPESTATUS[0]}
set -e

python3 evals/scripts/score_suite.py "$SUITE_ARG" --json >"$RUN_ROOT/summary.json" || true

echo "exit=$RC" | tee -a "$RUN_ROOT/meta.txt"
echo "Wrote $RUN_ROOT"
exit "$RC"
