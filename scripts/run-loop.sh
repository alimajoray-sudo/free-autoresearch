#!/bin/bash
# autoresearch/scripts/run-loop.sh
# Autonomous improvement loop — modifies target, evaluates, keeps or reverts.
#
# Usage:
#   bash run-loop.sh <project-dir> [max-experiments] [time-budget]
#
# Arguments:
#   project-dir      Path to autoresearch project (created by init-project.sh)
#   max-experiments  Number of experiments to run (default: 20)
#   time-budget      Max time per experiment as 'Xm' or 'Xs' (default: 5m)
#
# Environment:
#   AUTORESEARCH_MODE  Agent mode: acp (default), claude-code, manual
#   AUTORESEARCH_MODEL Model to use for agent (default: anthropic/claude-sonnet-4-6)
#   AUTORESEARCH_DIRECTION  higher_is_better or lower_is_better (default: auto-detect from program.md)
#
# Example:
#   bash run-loop.sh projects/prompt-opt 30 3m
#   AUTORESEARCH_MODE=claude-code bash run-loop.sh projects/bench 10 10m

set -euo pipefail

# ── macOS compat: use gtimeout if timeout is missing ────────────────────────
if ! command -v timeout &>/dev/null; then
  if command -v gtimeout &>/dev/null; then
    timeout() { gtimeout "$@"; }
  else
    echo "ERROR: 'timeout' (coreutils) not found. Install: brew install coreutils" >&2
    exit 1
  fi
fi

# ── Config ──────────────────────────────────────────────────────────────────
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_DIR="${1:?Usage: run-loop.sh <project-dir> [max-experiments] [time-budget]}"
MAX_EXPERIMENTS="${2:-20}"
TIME_BUDGET="${3:-5m}"
MODE="${AUTORESEARCH_MODE:-acp}"
MODEL="${AUTORESEARCH_MODEL:-anthropic/claude-sonnet-4-6}"

PROJECT_DIR="$(realpath "$PROJECT_DIR")"
PROGRAM_MD="$PROJECT_DIR/program.md"
EVALUATE_SH="$PROJECT_DIR/evaluate.sh"
EXPERIMENTS_JSONL="$PROJECT_DIR/experiments.jsonl"
BEST_DIR="$PROJECT_DIR/best"

# ── Validate ─────────────────────────────────────────────────────────────────
if [[ ! -d "$PROJECT_DIR" ]]; then
  echo "ERROR: Project directory not found: $PROJECT_DIR" >&2
  exit 1
fi
if [[ ! -f "$PROGRAM_MD" ]]; then
  echo "ERROR: program.md not found in $PROJECT_DIR" >&2
  exit 1
fi
if [[ ! -f "$EVALUATE_SH" ]]; then
  echo "ERROR: evaluate.sh not found in $PROJECT_DIR" >&2
  exit 1
fi

# ── Convert time budget to seconds ───────────────────────────────────────────
budget_to_seconds() {
  local b="$1"
  if [[ "$b" =~ ^([0-9]+)m$ ]]; then
    echo $(( ${BASH_REMATCH[1]} * 60 ))
  elif [[ "$b" =~ ^([0-9]+)s$ ]]; then
    echo "${BASH_REMATCH[1]}"
  elif [[ "$b" =~ ^([0-9]+)h$ ]]; then
    echo $(( ${BASH_REMATCH[1]} * 3600 ))
  elif [[ "$b" =~ ^[0-9]+$ ]]; then
    echo "$b"
  else
    echo "300"
  fi
}
BUDGET_SECS="$(budget_to_seconds "$TIME_BUDGET")"

# ── Metric direction ─────────────────────────────────────────────────────────
detect_direction() {
  if grep -qi "lower_is_better" "$PROGRAM_MD" 2>/dev/null; then
    echo "lower_is_better"
  else
    echo "higher_is_better"
  fi
}
DIRECTION="${AUTORESEARCH_DIRECTION:-$(detect_direction)}"

# ── Helper: is metric A better than B? ───────────────────────────────────────
is_better() {
  local new="$1" old="$2"
  if [[ "$DIRECTION" == "lower_is_better" ]]; then
    awk "BEGIN { exit ($new < $old) ? 0 : 1 }"
  else
    awk "BEGIN { exit ($new > $old) ? 0 : 1 }"
  fi
}

# ── Helper: run evaluate.sh with timeout ─────────────────────────────────────
run_evaluate() {
  local result
  result="$(timeout "${BUDGET_SECS}s" bash "$EVALUATE_SH" 2>/dev/null | tail -1 | tr -d '[:space:]')"
  if [[ -z "$result" ]]; then
    echo "ERROR"
    return 1
  fi
  # Validate it's a number
  if ! awk "BEGIN { exit ($result == $result) ? 0 : 1 }" 2>/dev/null; then
    echo "ERROR"
    return 1
  fi
  echo "$result"
}

# ── Helper: get short git commit hash ────────────────────────────────────────
git_short() {
  git -C "$PROJECT_DIR" rev-parse --short HEAD 2>/dev/null || echo "unknown"
}

# ── Helper: append to experiments.jsonl ──────────────────────────────────────
log_experiment() {
  local n="$1" commit="$2" before="$3" after="$4" decision="$5" diff_lines="$6" notes="$7"
  local ts delta
  ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  if [[ "$before" == "null" || "$after" == "ERROR" ]]; then
    delta="null"
  else
    delta="$(awk "BEGIN { printf \"%.6f\", $after - $before }")"
  fi
  cat >> "$EXPERIMENTS_JSONL" <<JSON
{"n":${n},"timestamp":"${ts}","commit":"${commit}","metric_before":${before},"metric_after":"${after}","delta":${delta},"direction":"${DIRECTION}","decision":"${decision}","diff_lines":${diff_lines},"notes":"${notes}"}
JSON
}

# ── Helper: count diff lines ──────────────────────────────────────────────────
count_diff_lines() {
  git -C "$PROJECT_DIR" diff HEAD~1 HEAD --stat 2>/dev/null | grep -oP '\d+ insertion' | grep -oP '\d+' || echo 0
}

# ── Helper: build agent prompt ────────────────────────────────────────────────
build_agent_prompt() {
  local exp_n="$1" current_metric="$2"
  # Find target file(s) — everything except evaluate.sh, program.md, experiments.jsonl, best/
  local target_files
  target_files="$(find "$PROJECT_DIR" -maxdepth 1 -type f \
    ! -name "program.md" ! -name "evaluate.sh" ! -name "experiments.jsonl" \
    ! -name ".gitignore" ! -name "*.log" 2>/dev/null | head -5 | tr '\n' ' ')"

  cat <<PROMPT
You are running experiment #${exp_n} in an autoresearch autonomous improvement loop.

Read the project instructions at: ${PROGRAM_MD}

Current metric (${DIRECTION}): ${current_metric}
Experiment number: ${exp_n}

Your task: Make ONE targeted improvement to the target file(s) in: ${PROJECT_DIR}
Target file(s): ${target_files}

Rules:
1. Make exactly ONE coherent change (not multiple unrelated changes)
2. The change should be motivated by the current metric and experiment history
3. Do NOT modify evaluate.sh or program.md
4. Do NOT add new external dependencies
5. After making the change, output a single line starting with "NOTES:" describing what you changed

Read program.md first, then the target file(s), then make your change.
PROMPT
}

# ── Helper: call agent ────────────────────────────────────────────────────────
call_agent() {
  local prompt="$1"
  local notes="unknown"

  case "$MODE" in
    claude-code)
      # Direct Claude Code invocation
      local tmp_prompt
      tmp_prompt="$(mktemp /tmp/autoresearch-prompt.XXXXXX.md)"
      echo "$prompt" > "$tmp_prompt"
      local output
      output="$(timeout "$(( BUDGET_SECS * 2 ))s" \
        claude --print --permission-mode bypassPermissions \
        "$(cat "$tmp_prompt")" 2>/dev/null || true)"
      rm -f "$tmp_prompt"
      notes="$(echo "$output" | grep "^NOTES:" | head -1 | sed 's/^NOTES: *//')"
      ;;

    manual)
      echo ""
      echo "── MANUAL MODE ──────────────────────────────────────────────────"
      echo "$prompt"
      echo ""
      echo "Make your change to the target file, then press ENTER to evaluate."
      read -r -p "Notes (what did you change?): " notes
      ;;

    ollama)
      # Local Ollama — zero cost modification
      local output
      output="$(timeout "$(( BUDGET_SECS * 2 ))s" \
        python3 "${SKILL_DIR}/scripts/ollama-modify.py" \
        "$PROJECT_DIR" "$exp_n" "$current_metric" 2>/dev/null || true)"
      notes="$(echo "$output" | grep "^NOTES:" | head -1 | sed 's/^NOTES: *//')"
      ;;

    acp|*)
      # OpenClaw ACP — spawn sub-agent
      local tmp_prompt
      tmp_prompt="$(mktemp /tmp/autoresearch-prompt.XXXXXX.md)"
      echo "$prompt" > "$tmp_prompt"
      local output
      output="$(timeout "$(( BUDGET_SECS * 2 ))s" \
        openclaw acp exec --model "$MODEL" --print \
        "$(cat "$tmp_prompt")" 2>/dev/null || true)"
      rm -f "$tmp_prompt"
      notes="$(echo "$output" | grep "^NOTES:" | head -1 | sed 's/^NOTES: *//')"
      ;;
  esac

  echo "${notes:-no notes}"
}

# ── Main loop ─────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              autoresearch — improvement loop                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo "  Project   : $PROJECT_DIR"
echo "  Target    : $MAX_EXPERIMENTS experiments"
echo "  Budget    : ${TIME_BUDGET} per experiment (${BUDGET_SECS}s)"
echo "  Direction : $DIRECTION"
echo "  Mode      : $MODE"
echo "  Model     : $MODEL"
echo ""

# ── Establish baseline ────────────────────────────────────────────────────────
echo "📊 Establishing baseline metric..."
BASELINE_METRIC="$(run_evaluate)" || { echo "ERROR: evaluate.sh failed on baseline run" >&2; exit 1; }
echo "  Baseline: $BASELINE_METRIC"

BEST_METRIC="$BASELINE_METRIC"
IMPROVEMENTS=0
DISCARDS=0
CRASHES=0

mkdir -p "$BEST_DIR"
# Copy current target files to best/
find "$PROJECT_DIR" -maxdepth 1 -type f \
  ! -name "program.md" ! -name "evaluate.sh" ! -name "experiments.jsonl" \
  ! -name ".gitignore" ! -name "*.log" 2>/dev/null | \
  while IFS= read -r f; do cp "$f" "$BEST_DIR/"; done

# Ensure we're in a git repo
if ! git -C "$PROJECT_DIR" rev-parse HEAD >/dev/null 2>&1; then
  git -C "$PROJECT_DIR" init -q
  git -C "$PROJECT_DIR" add .
  git -C "$PROJECT_DIR" commit -q -m "autoresearch: baseline (metric=${BASELINE_METRIC})"
fi

BASELINE_COMMIT="$(git_short)"

# Log baseline
log_experiment 0 "$BASELINE_COMMIT" "null" "$BASELINE_METRIC" "baseline" 0 "initial baseline"

# ── Append baseline to program.md ─────────────────────────────────────────────
cat >> "$PROGRAM_MD" <<HISTORY

---
## Experiment History (auto-appended)

| # | Commit | Metric | Decision | Notes |
|---|--------|--------|----------|-------|
| 0 | ${BASELINE_COMMIT} | ${BASELINE_METRIC} | baseline | initial baseline |
HISTORY

echo ""
echo "Starting experiment loop..."
echo ""

# ── Experiment loop ───────────────────────────────────────────────────────────
for (( EXP=1; EXP<=MAX_EXPERIMENTS; EXP++ )); do
  echo "── Experiment ${EXP}/${MAX_EXPERIMENTS} ──────────────────────────────────────────────"
  echo "  Best so far: $BEST_METRIC"

  # Safety checkpoint
  PRE_COMMIT="$(git_short)"

  # Call agent
  echo "  🤖 Calling agent (mode=$MODE)..."
  AGENT_NOTES="$(call_agent "$(build_agent_prompt "$EXP" "$BEST_METRIC")")"
  echo "  Notes: $AGENT_NOTES"

  # Check if anything changed
  CHANGED_FILES="$(git -C "$PROJECT_DIR" status --porcelain 2>/dev/null | grep -v "^??" | wc -l | tr -d ' ')"
  if [[ "$CHANGED_FILES" -eq 0 ]]; then
    echo "  ⚠️  Agent made no changes — skipping evaluation"
    log_experiment "$EXP" "$PRE_COMMIT" "$BEST_METRIC" "$BEST_METRIC" "no-change" 0 "$AGENT_NOTES"
    continue
  fi

  # Commit the agent's changes
  git -C "$PROJECT_DIR" add -A
  git -C "$PROJECT_DIR" commit -q -m "autoresearch: experiment ${EXP} — ${AGENT_NOTES}"
  NEW_COMMIT="$(git_short)"
  DIFF_LINES="$(count_diff_lines)"

  # Evaluate
  echo "  📊 Evaluating..."
  NEW_METRIC="$(run_evaluate)" || { NEW_METRIC="ERROR"; }

  if [[ "$NEW_METRIC" == "ERROR" ]]; then
    echo "  ❌ Evaluation failed — reverting"
    git -C "$PROJECT_DIR" revert --no-edit HEAD -q 2>/dev/null || \
      git -C "$PROJECT_DIR" reset --hard "${PRE_COMMIT}" -q
    log_experiment "$EXP" "$NEW_COMMIT" "$BEST_METRIC" "null" "crash" "$DIFF_LINES" "$AGENT_NOTES"
    (( CRASHES++ ))
    # Append to history table in program.md
    echo "| ${EXP} | ${NEW_COMMIT} | crash | crash | ${AGENT_NOTES} |" >> "$PROGRAM_MD"
    echo "  CRASHES: $CRASHES"
    continue
  fi

  echo "  Metric: $NEW_METRIC (was: $BEST_METRIC)"

  # Keep or discard
  if is_better "$NEW_METRIC" "$BEST_METRIC"; then
    DECISION="kept"
    BEST_METRIC="$NEW_METRIC"
    (( IMPROVEMENTS++ ))
    # Update best/
    find "$PROJECT_DIR" -maxdepth 1 -type f \
      ! -name "program.md" ! -name "evaluate.sh" ! -name "experiments.jsonl" \
      ! -name ".gitignore" ! -name "*.log" 2>/dev/null | \
      while IFS= read -r f; do cp "$f" "$BEST_DIR/"; done
    echo "  ✅ KEPT — new best: $BEST_METRIC (improvement: $(awk "BEGIN { printf \"%.4f\", $NEW_METRIC - ${BEST_METRIC} }")... wait, best updated)"
  else
    DECISION="discarded"
    (( DISCARDS++ ))
    git -C "$PROJECT_DIR" revert --no-edit HEAD -q 2>/dev/null || \
      git -C "$PROJECT_DIR" reset --hard "${PRE_COMMIT}" -q
    echo "  ⛔ DISCARDED — reverted to $BEST_METRIC"
  fi

  log_experiment "$EXP" "$NEW_COMMIT" "$BEST_METRIC" "$NEW_METRIC" "$DECISION" "$DIFF_LINES" "$AGENT_NOTES"
  # Append to history table
  echo "| ${EXP} | ${NEW_COMMIT} | ${NEW_METRIC} | ${DECISION} | ${AGENT_NOTES} |" >> "$PROGRAM_MD"

  echo ""
done

# ── Summary ───────────────────────────────────────────────────────────────────
TOTAL_DELTA="$(awk "BEGIN { printf \"%.6f\", $BEST_METRIC - $BASELINE_METRIC }")"
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    autoresearch DONE                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo "  Experiments  : $MAX_EXPERIMENTS"
echo "  Improvements : $IMPROVEMENTS"
echo "  Discards     : $DISCARDS"
echo "  Crashes      : $CRASHES"
echo "  Baseline     : $BASELINE_METRIC"
echo "  Best metric  : $BEST_METRIC"
echo "  Total delta  : $TOTAL_DELTA ($DIRECTION)"
echo "  Best files   : $BEST_DIR"
echo "  Experiment log: $EXPERIMENTS_JSONL"
echo ""

# Append summary to program.md
cat >> "$PROGRAM_MD" <<SUMMARY

---
## Campaign Summary

- **Experiments run:** $MAX_EXPERIMENTS
- **Improvements:** $IMPROVEMENTS | **Discards:** $DISCARDS | **Crashes:** $CRASHES
- **Baseline metric:** $BASELINE_METRIC
- **Best metric:** $BEST_METRIC
- **Total delta:** $TOTAL_DELTA
- **Direction:** $DIRECTION
SUMMARY
