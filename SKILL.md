---
name: free-autoresearch
description: >
  Launch autonomous improvement loops on any measurable target for $0.
  Cycles through free LLM APIs (OpenRouter, NVIDIA NIM, xAI, HuggingFace, DeepSeek).
  Use when: asked to "optimize this", "run experiments overnight", "improve X autonomously",
  "run autoresearch on", "continuously improve", or any task needing iterative AI-powered improvement.
---

# Free Autoresearch Engine

## Quick Start

### 1. Create a new optimization project
```bash
cd ~/Projects/free-autoresearch
bash scripts/init-project.sh <project-name> <target-file-to-optimize> "<evaluation-command>"
```

### 2. Run the engine
```bash
python engine.py --project <project-name>        # Single project
python engine.py                                   # All projects, continuous
python engine.py --once                            # One full cycle then exit
```

### 3. Monitor via dashboard
```bash
python dashboard/dashboard-server.py                # http://localhost:8830
```

### 4. Check results
```bash
cat projects/<project-name>/best/score.txt         # Best score
cat projects/<project-name>/experiments.jsonl       # Full experiment log
```

## How It Works
1. Agent reads target file + program.md instructions
2. Makes a modification using free LLM
3. Runs evaluation command → captures metric
4. If improved: keeps change + updates best/
5. If worse: reverts via git
6. Logs to experiments.jsonl
7. Moves to next project (round-robin)
8. Repeats forever at $0 cost

## Provider Priority
| Tier | Provider | Cost | Notes |
|------|----------|------|-------|
| 0 | OpenRouter (:free models) | $0 | Rate-limited, many models |
| 0 | NVIDIA NIM | $0 | Fast evaluator, free credits |
| 0 | xAI Grok Mini Fast | ~$0 | Reliable mutator |
| 1 | HuggingFace Inference | $0 | Good fallback |
| 2 | DeepSeek | $0.0004/1K | Budget-capped |

## Use Cases
- Prompt optimization (accuracy improvement)
- Code performance tuning (latency/throughput)
- Config optimization (resource usage)
- Content quality improvement (readability scores)
- Agent instruction refinement (task completion rate)
