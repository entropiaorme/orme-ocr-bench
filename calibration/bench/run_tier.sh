#!/usr/bin/env bash
# Staged tier runner: run one tier (or an explicit engine list) of any track,
# capturing everything needed to interpret the run now and for the article later.
# Cross-platform (Linux/CUDA Experiment A and Windows/DirectML+CPU Experiment B):
# the driver interpreter and GPU query are autodetected per host.
#
# Usage (from repo root):
#   calibration/bench/run_tier.sh gpu            # a --tier preset (gpu|fast|vlm|ship)
#   calibration/bench/run_tier.sh vlm
#   calibration/bench/run_tier.sh --engines florence2_large,got_ocr2
#
# Env overrides:
#   SUBDIR=cuda-batched BATCH=16 calibration/bench/run_tier.sh gpu
#     -> batched throughput track (writes results/cuda-batched/, batch size 16).
#   SKIP=0 calibration/bench/run_tier.sh gpu
#     -> re-run even if a result exists (default SKIP=1 reuses landed results).
#
# For a CPU latency track on a GPU host, pin CPU: OCR_BENCH_DEVICE=cpu.
#
# Each invocation writes a timestamped log + provenance header under
# calibration/bench/runs/<SUBDIR>/ and regenerates the <SUBDIR> report at the
# end. DRIVER_PY autodetects the venv layout; HF_HOME (if set) is inherited from
# the environment, not hardcoded (see SETUP.md).
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# Driver interpreter: honour an explicit DRIVER_PY, else autodetect the venv
# layout (Windows uses Scripts/python.exe, POSIX uses bin/python).
if [[ -z "${DRIVER_PY:-}" ]]; then
  if [[ -x "$REPO_ROOT/.venv/Scripts/python.exe" ]]; then
    DRIVER_PY="$REPO_ROOT/.venv/Scripts/python.exe"
  else
    DRIVER_PY="$REPO_ROOT/.venv/bin/python"
  fi
fi
# HF_HOME is host-specific and never hardcoded here: if the caller exported it,
# the orchestrator already forwards it to subprocesses; otherwise HuggingFace
# uses its default cache. (See SETUP.md.)
SUBDIR="${SUBDIR:-cuda}"
BATCH="${BATCH:-1}"
SKIP="${SKIP:-1}"
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

# ---- Build orchestrator flags from env knobs --------------------------------
RUN_FLAGS=(--results-subdir "$SUBDIR")
[[ "$BATCH" -gt 1 ]] && RUN_FLAGS+=(--batch-size "$BATCH")
[[ "$SKIP" == "1" ]] && RUN_FLAGS+=(--skip-existing)

# ---- Provenance header: host, GPU, drivers, git state -----------------------
{
  echo "# orme-ocr-bench Experiment run log"
  echo "# track:        $SUBDIR"
  echo "# mode:         $([[ "$BATCH" -gt 1 ]] && echo "batched (batch_size=$BATCH)" || echo "serial")"
  echo "# skip_existing: $SKIP"
  echo "# selection:    ${SEL_FLAG[*]:-<all engines>}"
  echo "# started_utc:  $STAMP"
  echo "# host:         $(hostname)"
  echo "# os:           $(uname -srm)"
  echo "# python:       $($DRIVER_PY --version 2>&1)"
  echo "# device_pin:   ${OCR_BENCH_DEVICE:-<auto: best available provider>}"
  echo "# git_commit:   $(git rev-parse --short HEAD 2>/dev/null) $(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
  echo "# git_dirty:    $([[ -n "$(git status --porcelain 2>/dev/null)" ]] && echo yes || echo no)"
  echo "# HF_HOME:      ${HF_HOME:-<inherit HuggingFace default>}"
  echo "# --- GPU ---"
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv 2>&1 | sed 's/^/# /'
  elif command -v powershell >/dev/null 2>&1; then
    powershell -NoProfile -Command \
      "Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion | Format-Table -HideTableHeaders" \
      2>&1 | sed 's/^/# /' | grep -v '^# *$'
  else
    echo "# (no GPU query tool found)"
  fi
  echo "# ---------------------------------------------------------------"
  echo
} | tee "$LOG"

# ---- Run the tier -----------------------------------------------------------
echo ">>> benchmark_panel_ocr ${SEL_FLAG[*]:-} ${RUN_FLAGS[*]}" | tee -a "$LOG"
"$DRIVER_PY" -m backend.ocr.calibration.benchmark_panel_ocr \
  "${SEL_FLAG[@]}" "${RUN_FLAGS[@]}" 2>&1 | tee -a "$LOG"
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
