#!/bin/bash
# autoresearch/scripts/init-project.sh
# Scaffolds a new autoresearch project directory.
#
# Usage:
#   bash init-project.sh <project-name> <target-file> <eval-command> [output-dir]
#
# Arguments:
#   project-name   Short slug for this project (e.g. "prompt-opt", "bench-v2")
#   target-file    Path to the file the agent will modify
#   eval-command   Shell command that outputs a single number to stdout
#   output-dir     Where to create the project (default: ./projects/)
#
# Example:
#   bash init-project.sh contract-prompt prompts/system.md "python eval_acc.py"

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# --- Args ---
PROJECT_NAME="${1:?Usage: init-project.sh <project-name> <target-file> <eval-command> [output-dir]}"
TARGET_FILE="${2:?Provide path to the target file to optimize}"
EVAL_COMMAND="${3:?Provide evaluation command that outputs a number}"
OUTPUT_BASE="${4:-$(pwd)/projects}"

PROJECT_DIR="${OUTPUT_BASE}/${PROJECT_NAME}"

# --- Validate ---
if [[ -e "$PROJECT_DIR" ]]; then
  echo "ERROR: Project directory already exists: $PROJECT_DIR" >&2
  exit 1
fi

TARGET_ABS="$(realpath "$TARGET_FILE" 2>/dev/null || echo "$TARGET_FILE")"
if [[ ! -f "$TARGET_ABS" ]]; then
  echo "WARNING: Target file not found: $TARGET_ABS (you can create it later)" >&2
fi

TARGET_BASENAME="$(basename "$TARGET_FILE")"

# --- Create structure ---
mkdir -p "$PROJECT_DIR/best"

echo "Creating autoresearch project: $PROJECT_NAME"
echo "  Project dir : $PROJECT_DIR"
echo "  Target file : $TARGET_ABS"
echo "  Eval command: $EVAL_COMMAND"

# --- program.md from template (substituted) ---
cat > "$PROJECT_DIR/program.md" <<PROGRAM_MD
# autoresearch: ${PROJECT_NAME}

## Goal

<!-- TODO: Describe what you want to improve and why. Be specific. -->
Improve the target file to maximize/minimize the metric output by evaluate.sh.

**Target file:** \`${TARGET_ABS}\`
**Metric direction:** higher_is_better  <!-- change to lower_is_better if needed -->

## What you are optimizing

<!-- TODO: Explain what this file does and what aspects can be changed. -->
The target file implements [describe functionality here]. You should experiment with:
- [Dimension 1 to vary]
- [Dimension 2 to vary]
- [Dimension 3 to vary]

## Evaluation

The metric is computed by running:
\`\`\`
${EVAL_COMMAND}
\`\`\`

It outputs a **single number** to stdout. Higher = better (or lower = better — edit above).
Current baseline: **[run evaluate.sh to find out]**

## Constraints — DO NOT change these

- Do not modify evaluate.sh or the evaluation harness
- Do not add new dependencies that are not already available
- Do not change the interface/signature of the target (other callers depend on it)
- [Add project-specific constraints here]

## Strategy hints

Think about:
1. What is the simplest possible improvement?
2. What are the failure modes of the current version?
3. Are there any obvious inefficiencies or missing edge cases?
4. What would a domain expert do differently?

Prefer **simple improvements** over complex ones. A small gain with cleaner code beats a
large gain with fragile hacks. If you can delete code and improve the metric, that's a win.

## Experiment history

<!-- Auto-appended by run-loop.sh after each experiment -->
PROGRAM_MD

# --- evaluate.sh ---
cat > "$PROJECT_DIR/evaluate.sh" <<EVAL_SH
#!/bin/bash
# evaluate.sh — outputs a single metric number to stdout
# This is the ground truth oracle. Do not modify during a campaign.
#
# Target: ${TARGET_ABS}
# Command: ${EVAL_COMMAND}

set -euo pipefail

# Run the evaluation and capture output
RESULT=\$(${EVAL_COMMAND} 2>/dev/null)

# Output ONLY the number — no labels, no newlines other than the final one
echo "\$RESULT"
EVAL_SH
chmod +x "$PROJECT_DIR/evaluate.sh"

# --- experiments.jsonl (empty, ready for appending) ---
touch "$PROJECT_DIR/experiments.jsonl"

# --- .gitignore ---
cat > "$PROJECT_DIR/.gitignore" <<GITIGNORE
# autoresearch project — keep experiments log untracked (per Karpathy pattern)
# Uncomment to also exclude best/ from git:
# best/
GITIGNORE

# --- Copy or link target ---
if [[ -f "$TARGET_ABS" ]]; then
  cp "$TARGET_ABS" "$PROJECT_DIR/${TARGET_BASENAME}"
  echo "  Copied target → $PROJECT_DIR/${TARGET_BASENAME}"
  echo ""
  echo "NOTE: run-loop.sh will modify the copy at:"
  echo "  $PROJECT_DIR/${TARGET_BASENAME}"
  echo "Set TARGET_PATH in run-loop.sh or pass it explicitly if you want to"
  echo "modify the original in-place."
else
  echo "  Target file not found — create it at: $PROJECT_DIR/${TARGET_BASENAME}"
fi

# --- Initialize git if needed ---
GIT_ROOT="$(git -C "$PROJECT_DIR" rev-parse --show-toplevel 2>/dev/null || echo '')"
if [[ -z "$GIT_ROOT" ]]; then
  echo ""
  echo "Initializing git repo in $PROJECT_DIR ..."
  git -C "$PROJECT_DIR" init -q
  git -C "$PROJECT_DIR" add .
  git -C "$PROJECT_DIR" commit -q -m "autoresearch: init project ${PROJECT_NAME}"
  echo "  git initialized and initial commit created."
else
  echo ""
  echo "Using existing git repo: $GIT_ROOT"
fi

echo ""
echo "✅ Project ready: $PROJECT_DIR"
echo ""
echo "Next steps:"
echo "  1. Edit $PROJECT_DIR/program.md — describe your goal and constraints"
echo "  2. Verify evaluate.sh works: bash $PROJECT_DIR/evaluate.sh"
echo "  3. Run the loop: bash ${SKILL_DIR}/scripts/run-loop.sh $PROJECT_DIR"
