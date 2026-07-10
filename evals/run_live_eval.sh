#!/usr/bin/env bash
# Live multi-harness dogfood for quality-gate (braintrust-style peer inject).
#
# Packages skill text + fixture, runs available peers (agy,codex,grok,opencode,claude),
# auto-scores results. Compares package variants: skill-v15 (current) vs skill-v14 (baseline).
#
# Usage:
#   bash evals/run_live_eval.sh
#   bash evals/run_live_eval.sh qg-live-mode-plan skill-v15 agy,codex,grok,opencode,claude
#   bash evals/run_live_eval.sh qg-live-contract ab agy,codex,grok,opencode,claude
#   bash evals/run_live_eval.sh qg-live-execute ab all   # E2E on sandbox repo
#   bash evals/run_live_eval.sh matrix
#
# Writes: evals/runs/<timestamp>-live-<fixture>/

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

FIXTURE="${1:-qg-live-mode-plan}"
VARIANT="${2:-ab}"   # skill-v15 | skill-v14 | ab | all
PEERS_CSV="${3:-all}"

BT_PROBE=""
if [[ -f ../braintrust/scripts/bt_probe.sh ]]; then
  BT_PROBE="../braintrust/scripts/bt_probe.sh"
elif [[ -f /Users/drewburchfield/dev/projects/not-my-job/plugins/braintrust/scripts/bt_probe.sh ]]; then
  BT_PROBE="/Users/drewburchfield/dev/projects/not-my-job/plugins/braintrust/scripts/bt_probe.sh"
fi

TS="$(date -u +%Y%m%dT%H%M%SZ)"
if [[ "$FIXTURE" == "matrix" ]]; then
  MATRIX_ROOT="evals/runs/${TS}-live-matrix"
  mkdir -p "$MATRIX_ROOT"
  echo -e "fixture\tvariant\tpeer\tscore\tmax\thits\tbytes" >"$MATRIX_ROOT/combined.tsv"
  for fix in qg-live-mode-plan qg-live-contract qg-live-execute; do
    for var in skill-v15 skill-v14; do
      echo "======== LIVE matrix fixture=$fix variant=$var ========"
      bash "$ROOT/evals/run_live_eval.sh" "$fix" "$var" "$PEERS_CSV" | tee "$MATRIX_ROOT/${fix}-${var}.log" || true
      latest=$(ls -1dt evals/runs/*-live-"$fix" 2>/dev/null | head -1 || true)
      if [[ -n "${latest:-}" && -f "$latest/summary.tsv" ]]; then
        tail -n +2 "$latest/summary.tsv" | while IFS= read -r line; do
          echo -e "${fix}\t${line}"
        done >>"$MATRIX_ROOT/combined.tsv"
        echo "$latest" >>"$MATRIX_ROOT/run_paths.txt"
      fi
    done
  done
  echo "Matrix written: $MATRIX_ROOT/combined.tsv"
  column -t -s $'\t' "$MATRIX_ROOT/combined.tsv" 2>/dev/null || cat "$MATRIX_ROOT/combined.tsv"
  exit 0
fi

FIX_PATH="evals/fixtures/${FIXTURE}.md"
[[ -f "$FIX_PATH" ]] || { echo "missing fixture $FIX_PATH" >&2; exit 2; }

RUN_ROOT="evals/runs/${TS}-live-${FIXTURE}"
mkdir -p "$RUN_ROOT"
echo "fixture=$FIXTURE variant=$VARIANT peers=$PEERS_CSV" | tee "$RUN_ROOT/meta.txt"

if [[ -n "$BT_PROBE" ]]; then
  bash "$BT_PROBE" >"$RUN_ROOT/probe.log" 2>&1 || true
fi
# shellcheck disable=SC1091
source /tmp/bt_models.env 2>/dev/null || true

append_sandbox() {
  # Real code under review for execute fixture
  echo
  echo "## SANDBOX REPOSITORY (review this code as local changes)"
  echo
  echo "### src/user_service.py"
  echo '```python'
  cat evals/fixtures/sandbox-qg/src/user_service.py
  echo '```'
  echo
  echo "### tests/test_user_service.py"
  echo '```python'
  cat evals/fixtures/sandbox-qg/tests/test_user_service.py
  echo '```'
  echo
  echo "### pass checklists (run these lenses)"
  for p in code-correctness silent-failures tests types comments simplify; do
    echo "#### $p"
    cat "skills/quality-gate/references/review-suite/passes/${p}.md"
    echo
  done
}

build_package() {
  local variant="$1"
  local out="$2"
  {
    echo "## LIVE DOGFOOD PACKAGE"
    echo "## VARIANT: $variant"
    echo "## FIXTURE: $FIXTURE"
    echo
    if [[ "$FIXTURE" == "qg-live-execute" ]]; then
      echo "EXECUTE quality-gate --local on the sandbox code. Emit findings + tier_declaration + pass artifacts."
    else
      echo "You are evaluating quality-gate behavior from the skill text below."
      echo "Do not invent tools not described. Prefer host-correct adapters."
    fi
    echo
    if [[ "$variant" == "skill-v15" ]]; then
      echo "## SKILL TEXT (project-bootstrap quality-gate v1.5.0 — current)"
      cat skills/quality-gate/SKILL.md
      echo
      echo "## REVIEW SUITE SPEC"
      cat skills/quality-gate/references/review-suite/SPEC.md
      echo
      echo "## HOST ADAPTERS"
      for h in claude-code codex grok opencode agy; do
        echo "### $h"
        cat "skills/quality-gate/references/review-suite/host-adapters/${h}.md"
        echo
      done
      if [[ "$FIXTURE" == "qg-live-execute" ]]; then
        append_sandbox
      fi
    elif [[ "$variant" == "skill-v14" ]]; then
      echo "## SKILL TEXT (project-bootstrap quality-gate v1.4.0 — previously live baseline)"
      cat evals/baselines/quality-gate-v1.4.0-SKILL.md
      echo
      echo "## NOTE: This baseline has no portable Review Suite package."
      if [[ "$FIXTURE" == "qg-live-execute" ]]; then
        append_sandbox
        echo
        echo "## NOTE: Still execute a thorough multi-lens review of the sandbox using agent names from the v1.4 skill if present."
      fi
    else
      echo "unknown variant $variant" >&2
      exit 2
    fi
    echo
    echo "## TASK"
    cat "$FIX_PATH"
  } >"$out"
  local chars tok
  chars=$(wc -c <"$out" | tr -d ' ')
  tok=$((chars / 4))
  echo "$variant chars=$chars ~tok=$tok" | tee -a "$RUN_ROOT/sizes.txt"
}

run_peer() {
  local peer="$1" package="$2" outdir="$3"
  mkdir -p "$outdir"
  local q
  q=$(cat "$package")
  case "$peer" in
    agy)
      if [[ "${bt_agy_available:-true}" == "false" ]]; then
        echo "SKIPPED unavailable" >"$outdir/result.txt"; return
      fi
      timeout 240 agy --print "$q" --dangerously-skip-permissions \
        >"$outdir/result.txt" 2>"$outdir/stderr.txt" || true
      ;;
    codex)
      if [[ "${bt_codex_available:-true}" == "false" ]]; then
        echo "SKIPPED unavailable" >"$outdir/result.txt"; return
      fi
      local home="${bt_codex_home:-/tmp/bt-codex-home}"
      CODEX_HOME="$home" timeout 260 codex exec --ephemeral --ignore-user-config \
        -s read-only --json --skip-git-repo-check -C "${TMPDIR:-/tmp}" "$q" \
        </dev/null 2>"$outdir/stderr.txt" >"$outdir/raw.jsonl" || true
      jq -rs 'map(select(.item.type? == "agent_message")) | last | .item.text // empty' \
        "$outdir/raw.jsonl" >"$outdir/result.txt" 2>/dev/null || true
      ;;
    grok)
      if [[ "${bt_grok_available:-true}" == "false" ]]; then
        echo "SKIPPED unavailable" >"$outdir/result.txt"; return
      fi
      timeout 240 grok -p "$q" -m "${bt_grok_model:-grok-4.5}" \
        --output-format json --disable-web-search \
        2>"$outdir/stderr.txt" \
        | jq -r 'if .type=="error" then "GROK_FAILED: "+.message else .text end' \
        >"$outdir/result.txt" || true
      ;;
    opencode)
      if [[ "${bt_opencode_available:-true}" == "false" ]]; then
        echo "SKIPPED unavailable" >"$outdir/result.txt"; return
      fi
      local args=(run --format json --auto --pure)
      [[ -n "${bt_opencode_model:-}" ]] && args+=(-m "$bt_opencode_model")
      timeout 240 opencode "${args[@]}" "$q" 2>"$outdir/stderr.txt" \
        | jq -rs 'map(select(.type=="text") | .part.text // .text // empty) | map(select(length>0)) | last // empty' \
        >"$outdir/result.txt" || true
      ;;
    claude)
      if [[ "${bt_claude_cli_available:-true}" == "false" ]]; then
        echo "SKIPPED unavailable" >"$outdir/result.txt"; return
      fi
      timeout 240 claude -p "$q" --model "${bt_claude_model:-sonnet}" --output-format json \
        2>"$outdir/stderr.txt" \
        | jq -r '.result // empty' >"$outdir/result.txt" || true
      ;;
    *)
      echo "unknown peer $peer" >&2
      return 2
      ;;
  esac
  local n
  n=$(wc -c <"$outdir/result.txt" | tr -d ' ')
  echo "$peer bytes=$n" | tee -a "$RUN_ROOT/peer_status.txt"
}

resolve_variants() {
  case "$1" in
    ab) echo "skill-v15 skill-v14" ;;
    all) echo "skill-v15 skill-v14" ;;
    skill-v15|skill-v14) echo "$1" ;;
    *) echo "$1" ;;
  esac
}

resolve_peers() {
  if [[ "$1" == "all" ]]; then
    echo "agy codex grok opencode claude"
  else
    echo "${1//,/ }"
  fi
}

echo -e "variant\tpeer\tscore\tmax\thits\tbytes" >"$RUN_ROOT/summary.tsv"

for variant in $(resolve_variants "$VARIANT"); do
  pkg="$RUN_ROOT/package-${variant}.md"
  build_package "$variant" "$pkg"

  pids=()
  for peer in $(resolve_peers "$PEERS_CSV"); do
    outdir="$RUN_ROOT/${variant}/${peer}"
    mkdir -p "$outdir"
    (
      run_peer "$peer" "$pkg" "$outdir"
    ) &
    pids+=($!)
  done
  for pid in "${pids[@]:-}"; do
    wait "$pid" || true
  done

  for peer in $(resolve_peers "$PEERS_CSV"); do
    outdir="$RUN_ROOT/${variant}/${peer}"
    res="$outdir/result.txt"
    if [[ ! -f "$res" ]]; then
      echo "missing" >"$res"
    fi
    if [[ "$FIXTURE" == "qg-live-execute" ]]; then
      scored=$(python3 evals/scripts/score_execute.py "$res" --json)
      score=$(echo "$scored" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['score'])")
      maxs=$(echo "$scored" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['max'])")
      hits=$(echo "$scored" | python3 -c "import sys,json; d=json.load(sys.stdin); print(','.join(d.get('gt_hits') or []))")
      bytes=$(echo "$scored" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('bytes',0))")
    else
      scored=$(python3 evals/scripts/score_live.py "$FIXTURE" "$res" --json)
      score=$(echo "$scored" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['score'])")
      maxs=$(echo "$scored" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['max'])")
      hits=$(echo "$scored" | python3 -c "import sys,json; d=json.load(sys.stdin); print(','.join(d['hits']))")
      bytes=$(echo "$scored" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['bytes'])")
    fi
    echo -e "${variant}\t${peer}\t${score}\t${maxs}\t${hits}\t${bytes}" | tee -a "$RUN_ROOT/summary.tsv"
    echo "$scored" >"$outdir/score.json"
  done
done

echo
echo "=== LIVE SUMMARY ($RUN_ROOT) ==="
column -t -s $'\t' "$RUN_ROOT/summary.tsv" 2>/dev/null || cat "$RUN_ROOT/summary.tsv"

# Compare means v15 vs v14 if both present
python3 - <<'PY' "$RUN_ROOT/summary.tsv" "$FIXTURE"
import sys
from collections import defaultdict
path = sys.argv[1]
fixture = sys.argv[2]
rows = []
with open(path) as f:
    next(f)
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) >= 4:
            rows.append(parts)
by = defaultdict(list)
for v, peer, score, mx, *rest in rows:
    try:
        by[v].append((peer, int(score), int(mx), rest[0] if rest else ""))
    except ValueError:
        pass
print("\n=== MEAN SCORES BY VARIANT ===")
for v, items in sorted(by.items()):
    if not items:
        continue
    s = sum(x[1] for x in items)
    m = sum(x[2] for x in items)
    n = len(items)
    print(f"{v}: mean {s/n:.2f}/{items[0][2]} across {n} peers  ({s}/{m} sum)")
    for peer, sc, mx, hits in items:
        bar = "#" * sc + "-" * (mx - sc)
        extra = f"  hits={hits}" if hits and fixture == "qg-live-execute" else ""
        print(f"  {peer:10} {sc:2}/{mx} {bar}{extra}")
if "skill-v15" in by and "skill-v14" in by:
    m15 = sum(x[1] for x in by["skill-v15"]) / len(by["skill-v15"])
    m14 = sum(x[1] for x in by["skill-v14"]) / len(by["skill-v14"])
    print(f"\nDELTA mean(v15)-mean(v14) = {m15 - m14:+.2f}")
    if m15 > m14:
        print("VERDICT: v1.5 package outperforms v1.4 on this live fixture (heuristic)")
    elif m15 == m14:
        print("VERDICT: tie on heuristic scores")
    else:
        print("VERDICT: v1.4 scored higher (inspect results; possible scorer mismatch)")
if fixture == "qg-live-execute":
    print("\nGround truth: GT1 SQL inject, GT2 empty catch, GT3 null deref, GT4 missing tests for compute_score")
    print("Max 9 = 4 findings + 2 artifacts + 2 tier honesty + 1 bot hygiene")
PY

echo "Done: $RUN_ROOT"
