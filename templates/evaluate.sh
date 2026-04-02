#!/bin/bash
# evaluate.sh — autoresearch evaluation harness
# Output: ONE number to stdout. Nothing else.
# This is the ground truth oracle. Do not modify during a campaign.
#
# ============================================================
# REPLACE the body below with your actual evaluation logic.
# ============================================================

set -euo pipefail

# Example 1: Python script that prints accuracy (0.0 – 1.0)
# python eval_accuracy.py 2>/dev/null | tail -1

# Example 2: Shell benchmark (lower time = better, use lower_is_better in program.md)
# /usr/bin/time -f "%e" bash benchmark.sh 2>&1 | tail -1

# Example 3: Extract metric from JSON output
# python run_backtest.py 2>/dev/null | python -c "import sys,json; print(json.load(sys.stdin)['sharpe'])"

# Example 4: Word count as readability proxy
# python -c "import textstat; print(textstat.flesch_reading_ease(open('target.md').read()))"

# ── Your evaluation command goes here ──────────────────────────────────────
RESULT=$(echo "TODO: replace this with your eval command" >&2; echo "0")

# Output only the number
echo "$RESULT"
