#!/bin/bash
# eval-latency.sh — measure HTTP endpoint p95 latency
# Usage: TARGET_URL=http://localhost:8800/health bash eval-latency.sh
# Outputs: p95 latency in milliseconds (lower_is_better)

set -euo pipefail

URL="${TARGET_URL:-http://localhost:8800/health}"
REQUESTS="${LATENCY_REQUESTS:-20}"

times=()
for (( i=0; i<REQUESTS; i++ )); do
  ms="$( { time curl -s -o /dev/null "$URL"; } 2>&1 | grep real | awk '{print $2}' | \
    sed 's/m/\* 60000 + /; s/s/* 1000/' | bc -l 2>/dev/null || echo 9999 )"
  times+=("$ms")
done

# Sort and get p95
p95="$(printf '%s\n' "${times[@]}" | sort -n | awk -v n="$REQUESTS" 'NR==int(n*0.95)+1{print}')"
echo "${p95:-9999}"
