---
name: autoresearch
description: >
  Autonomous improvement loop for ANY measurable target — prompt optimization,
  code performance, config tuning, content readability, trading backtests, agent
  instruction quality. Inspired by Karpathy's autoresearch (github.com/karpathy/autoresearch).
  Run overnight and wake up to a log of experiments with the best result kept.
  Triggers on: "run autoresearch", "optimize this autonomously", "overnight experiment loop",
  "improve X until metric improves", "run improvement loop on", "autoresearch project".
---

# autoresearch

> *"Give the agent a target and a metric. Let it experiment while you sleep."*
> Inspired by Andrej Karpathy's [autoresearch](https://github.com/karpathy/autoresearch) —
> adapted here as a generic OpenClaw skill for ANY measurable improvement task.

## Core Concept

The agent modifies a target file → runs an evaluation → compares the metric →
keeps improvements, reverts failures → logs everything → repeats.

```
LOOP:
  git commit (safety checkpoint)
  agent modifies target
  run evaluate.sh → capture metric
  if improved: keep + update best/
  else: git revert
  append to experiments.jsonl
```

## Quick Start (3 commands)

```bash
# 1. Scaffold a new project
bash skills/autoresearch/scripts/init-project.sh my-prompt-opt prompts/system.md "python score.py"

# 2. Edit program.md to describe your goal
nano projects/my-prompt-opt/program.md

# 3. Run the loop (20 experiments, 5 min each)
bash skills/autoresearch/scripts/run-loop.sh projects/my-prompt-opt 20 5m
```

## Use Cases

### 1. Prompt Optimization (ContractAI accuracy)
```bash
bash skills/autoresearch/scripts/init-project.sh contract-prompt \
  ~/.openclaw/workspace-main/skills/contract-search/prompts/system.md \
  "python skills/autoresearch/eval-examples/eval-accuracy.py"
```
Metric: % correct answers on a test set. Agent rewrites prompt phrasing,
adds chain-of-thought hints, adjusts tone, removes noise.

### 2. Code Performance
```bash
bash skills/autoresearch/scripts/init-project.sh bench-optimizer \
  src/critical_function.py \
  "python -c 'import time, importlib; t=time.time(); importlib.import_module(\"bench\"); print(time.time()-t)'"
```
Metric: execution time in seconds (lower = better). Agent tries algorithmic
improvements, caching, early exits, vectorization.

### 3. Config Tuning (response latency)
```bash
bash skills/autoresearch/scripts/init-project.sh latency-tuner \
  ~/.openclaw/openclaw.json \
  "bash skills/autoresearch/eval-examples/eval-latency.sh"
```
Metric: p95 response time in ms. Agent adjusts timeouts, concurrency, model
routing. Uses git safety net to revert bad configs.

### 4. Agent Instruction Quality
```bash
bash skills/autoresearch/scripts/init-project.sh agent-instructions \
  skills/my-skill/SKILL.md \
  "python skills/autoresearch/eval-examples/eval-task-completion.py"
```
Metric: task completion rate (0.0–1.0). Agent rewrites instructions, adds
examples, tightens constraints.

### 5. Trading Strategy
```bash
bash skills/autoresearch/scripts/init-project.sh strategy-opt \
  trading/strategy.py \
  "python trading/backtest.py --quiet | tail -1"
```
Metric: Sharpe ratio. Agent modifies signal logic, position sizing, filters.

## Project Structure

```
<project-dir>/
├── program.md          # Agent instructions — goal, constraints, history
├── target.*            # File being optimized (symlinked or copied)
├── evaluate.sh         # Outputs ONE number to stdout (the metric)
├── experiments.jsonl   # Auto-generated experiment log
└── best/               # Best-performing version of target
    └── target.*
```

## experiment.jsonl Format

Each line is a JSON object:
```json
{
  "n": 3,
  "timestamp": "2026-03-23T02:00:00Z",
  "commit": "a1b2c3d",
  "metric_before": 0.72,
  "metric_after": 0.81,
  "delta": 0.09,
  "direction": "higher_is_better",
  "decision": "kept",
  "diff_lines": 12,
  "notes": "Added chain-of-thought instruction"
}
```

## program.md Template

See `templates/program.md` for the full template. Key sections:
- **Goal** — what you're optimizing and why
- **Target** — the file path and what's fair game to modify
- **Metric** — what `evaluate.sh` measures, which direction is better
- **Constraints** — what NOT to change
- **History** — auto-appended by run-loop.sh

## LLM Judge: Local Ollama (Zero Cost)

For overnight loops, use **M5 MacBook Pro** Ollama models — no API cost.

```bash
# M5 Ollama endpoint (Tailscale)
OLLAMA_URL=http://100.74.12.125:11434

# Available models:
# - qwen3:30b    — MoE 30.5B, fast, good for judging + answering
# - qwen3:32b    — dense 32.8B, slower but more capable
# - qwen3-coder:30b — coding variant

# Run evaluation with Ollama judge:
python skills/autoresearch/eval-examples/eval-accuracy-ollama.py \
  --target prompts/system.md \
  --tests test-set.json \
  --ollama-url http://100.74.12.125:11434 \
  --model qwen3:30b \
  --judge-model qwen3:30b \
  --verbose
```

The Ollama evaluator uses a two-phase approach:
1. **Answer phase**: System prompt + question → model generates answer
2. **Judge phase**: Same or different model scores answer vs expected (1.0 / 0.5 / 0.0)

Throughput: ~2 min per question on M5 (30B model). 25-question test set ≈ 50 min.
Overnight capacity: ~15 full evaluations in 12 hours → enough for 15 experiments.

## Agent Modes

### Mode A: OpenClaw sub-agent (default)
`run-loop.sh` spawns a sub-agent per experiment via `openclaw acp exec`.
Each agent reads `program.md`, makes ONE targeted change, exits.

### Mode B: Direct Claude Code
```bash
AUTORESEARCH_MODE=claude-code bash skills/autoresearch/scripts/run-loop.sh projects/my-proj
```
Uses `claude --print --permission-mode bypassPermissions` for each experiment.

### Mode C: Manual / Cron
Set `AUTORESEARCH_MODE=manual` — loop pauses and prompts before each experiment.
Useful for debugging or slow/expensive evaluations.

## Safety

- **Always git-commits before any modification** — every experiment is recoverable
- **git checkout reverts** bad experiments atomically
- **evaluate.sh timeout** — experiments killed after `TIME_BUDGET` (default 5m)
- **Never modifies files outside project dir** without explicit `TARGET` path

## Complementary Skills

- **self-improvement** — passive logging of errors and corrections. Think of autoresearch as
  *active experimentation* vs self-improvement's *passive observation*. Use both: let
  self-improvement capture organic corrections, use autoresearch for structured overnight runs.
- **decision-journal** — log autoresearch campaign decisions (why you chose this target, what
  you hypothesized, what you learned).

## Active Projects (2026-03-29)

| Project | Dir | Score | Status |
|---------|-----|-------|--------|
| contract-search-skill | `projects/contract-search-skill/` | 0.825 baseline | ✅ Done |
| email-assistant | `projects/email-assistant/` | 0.85 baseline | 🔄 Running |
| google-api | `projects/google-api/` | — | 🔄 Queued |
| vapi-caller | `projects/vapi-caller/` | — | ⏳ Queued |
| contractai-prompts | `projects/contractai-prompts/` | 0.28 (3 exp) | 🔄 Paused |

Queue runner: `bash /tmp/run-remaining.sh` (runs google-api → vapi-caller sequentially)
Dashboard: https://autoresearch.emaygroup.org

## Core Architecture (agent-codex.py)

The actual loop uses `agent-codex.py` in each project dir. Key design decisions:

```
LOOP:
  establish baseline (full 20-question eval)
  for each experiment:
    read BEST prompt (not current!) → generate modification via Codex
    quick eval (5 questions) → skip if much worse
    full eval (20 questions)
    if improved: save to best/, git commit
    else: restore best prompt, git checkout
```

**Critical patterns (from reference implementation):**
1. **Always mutate from best** — `BEST_DIR/system-prompt.md`, not `TARGET_FILE`
2. **Per-category failure rates** — mutation prompt shows which categories score low
3. **Quick screen** — 5-question pre-filter saves 75% of eval time on bad candidates
4. **Deterministic scorer** — keyword matching, no LLM judge (no API cost, no circular eval)

**LLM calls:** All via `codex exec --model gpt-5.3-codex` (free via ChatGPT Plus)
**RAG:** `http://localhost:8820/query` (knowledge RAG, collection-aware)

## Karpathy Inspiration

Karpathy's original: agent edits `train.py`, trains for 5 min fixed budget, checks `val_bpb`
(validation bits per byte), keeps if lower, reverts if higher, loops overnight.

Key insight adapted here: **fixed time budget makes experiments comparable**. We generalize this:
your `evaluate.sh` is the budget-aware oracle. Whether it's a 5-second readability score or a
5-minute backtest, the loop structure is identical.

Reference implementation at: `/tmp/autoresearch-ref/` (downloaded from Ali's Drive 2026-03-29)
See `references/karpathy-program.md` for the original agent instructions verbatim.
