#!/bin/bash
# ollama-modify.sh — Use local Ollama to modify a target file
# Zero API cost alternative to claude-code mode
# Usage: ollama-modify.sh <project-dir> <experiment-number> <current-metric>
set -euo pipefail

PROJECT_DIR="$1"
EXP_N="$2"
CURRENT_METRIC="$3"

OLLAMA_URL="${OLLAMA_MODIFY_URL:-http://100.74.12.125:11434}"
OLLAMA_MODEL="${OLLAMA_MODIFY_MODEL:-qwen3:30b}"

PROGRAM_MD="$PROJECT_DIR/program.md"
TARGET_FILE="$PROJECT_DIR/system-prompt.md"

# Read current files
PROGRAM="$(cat "$PROGRAM_MD")"
CURRENT_PROMPT="$(cat "$TARGET_FILE")"

# Build the modification request
MODIFY_REQUEST="You are running experiment #${EXP_N} in an autonomous improvement loop.

INSTRUCTIONS:
${PROGRAM}

CURRENT TARGET FILE (system-prompt.md):
\`\`\`
${CURRENT_PROMPT}
\`\`\`

Current metric (higher_is_better): ${CURRENT_METRIC}

YOUR TASK: Output an IMPROVED version of the system prompt. Make ONE targeted change to improve the accuracy score.

RULES:
1. Output ONLY the new prompt text — no explanation, no markdown fences, no commentary
2. Make exactly ONE coherent improvement
3. Keep it under 2000 characters
4. Do NOT remove the ContractAI identity or FIDIC citation instruction
5. Start your output with the first word of the new prompt

OUTPUT THE IMPROVED PROMPT NOW:"

# Call Ollama
RESPONSE=$(curl -s --connect-timeout 30 "$OLLAMA_URL/api/chat" \
  -d "$(python3 -c "
import json
print(json.dumps({
    'model': '$OLLAMA_MODEL',
    'messages': [{'role': 'user', 'content': '''$MODIFY_REQUEST'''}],
    'stream': False,
    'options': {'temperature': 0.7, 'num_predict': 2000, 'num_ctx': 8192}
}))
")" 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(d.get('message',{}).get('content',''))
" 2>/dev/null)

if [[ -z "$RESPONSE" ]]; then
  echo "ERROR: Empty response from Ollama" >&2
  exit 1
fi

# Write the new prompt
echo "$RESPONSE" > "$TARGET_FILE"
echo "NOTES: Ollama experiment #${EXP_N} — modified prompt via ${OLLAMA_MODEL}"
