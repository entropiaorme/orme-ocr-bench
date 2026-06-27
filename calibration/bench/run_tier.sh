#!/usr/bin/env bash
# Staged Experiment-A runner: run one tier (or an explicit engine list) of the
# CUDA "research breadth" track, capturing everything needed to interpret the
# run now and for the article later.
#
# Usage (from repo root):
#   calibration/bench/run_tier.sh gpu            # a --tier preset (gpu|fast|vlm|ship)
#   calibration/bench/run_tier.sh vlm
#   calibration/bench/run_tier.sh --engines florence2_large,got_ocr2
#
# Idempotent: passes --skip-existing, so results already in results/cuda/ are
# reused. Each invocation writes a timestamped log + metadata header under
# calibration/bench/runs/cuda/ and regenerates the cuda report at the end.
#
# Edit DRIVER_PY / HF_HOME below if your paths differ (see SETUP.md).
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

DRIVER_PY="${DRIVER_PY:-$REPO_ROOT/.venv/bin/python}"
export HF_HOME="${HF_HOME:-/home/lunet/comw2/.cache/huggingface}"
SUBDIR="cuda"
RUNS_DIR="$REPO_ROOT/calibration/bench/runs/$SUBDIR"
mkdir -p "$RUNS_DIR"

# Resolve the tier/engines argument into orchestrator flags + a label.
if [[ "${1:-}" == "--engines" ]]; then
  SEL_FLAG=(--engines "${2:?need engine list}")
  LABEL="engines-$(echo "${2}" | tr ',' '_' | cut -c1-40)"
elif [[ -n "${1:-}" ]]; then
  SEL_FLAG=(--tier "$1")
  LABEL="tier-$1"
else
  SEL_FLAG=()           # no selection => all engines
  LABEL="all"
fi

# Timestamp is taken from the shell (the bench code itself avoids wall-clock).
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$RUNS_DIR/${STAMP}_${LABEL}.log"

# ---- Provenance header: host, GPU, drivers, git state -----------------------
{
  echo "# orme-ocr-bench Experiment-A run log"
  echo "# track:        $SUBDIR (unconstrained research breadth; best device per engine)"
  echo "# selection:    ${SEL_FLAG[*]:-<all engines>}"
  echo "# started_utc:  $STAMP"
  echo "# host:         $(hostname)"
  echo "# os:           $(uname -srm)"
  echo "# python:       $($DRIVER_PY --version 2>&1)"
  echo "# git_commit:   $(git rev-parse --short HEAD 2>/dev/null) $(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
  echo "# git_dirty:    $([[ -n "$(git status --porcelain 2>/dev/null)" ]] && echo yes || echo no)"
  echo "# HF_HOME:      $HF_HOME"
  echo "# --- nvidia-smi ---"
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv 2>&1 | sed 's/^/# /'
  echo "# ---------------------------------------------------------------"
  echo
} | tee "$LOG"

# ---- Run the tier -----------------------------------------------------------
echo ">>> benchmark_panel_ocr ${SEL_FLAG[*]:-} --results-subdir $SUBDIR --skip-existing" | tee -a "$LOG"
"$DRIVER_PY" -m backend.ocr.calibration.benchmark_panel_ocr \
  "${SEL_FLAG[@]}" --results-subdir "$SUBDIR" --skip-existing 2>&1 | tee -a "$LOG"
RUN_RC=${PIPESTATUS[0]}

# ---- Regenerate the cuda report so leaderboard reflects all results so far ---
echo | tee -a "$LOG"
echo ">>> report --results-subdir $SUBDIR" | tee -a "$LOG"
"$DRIVER_PY" -m backend.ocr.calibration.bench.report --results-subdir "$SUBDIR" 2>&1 | tee -a "$LOG"

echo | tee -a "$LOG"
echo "# finished_utc: $(date -u +%Y%m%dT%H%M%SZ) | orchestrator_rc=$RUN_RC" | tee -a "$LOG"
echo "# log:          $LOG" | tee -a "$LOG"
echo "# leaderboard:  calibration/bench/report/$SUBDIR/leaderboard.md" | tee -a "$LOG"
echo
echo "Done. Ping the agent with: this run's log path is $LOG"
