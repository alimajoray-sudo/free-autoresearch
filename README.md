# 🔬 Free Autoresearch Engine

**Run 100+ AI experiments overnight for $0 — autonomous improvement loops powered by free LLM APIs**

This is a zero-cost autonomous research engine inspired by [Andrej Karpathy's autoresearch](https://github.com/karpathy/autoresearch). It cycles through free LLM providers to continuously improve code, prompts, configs, or any measurable target without spending a cent.

## What is this?

Free Autoresearch is a self-improving loop engine that:
1. **Mutates** your target (prompt, code, config) using a free LLM
2. **Evaluates** the change by running your custom metric command
3. **Keeps improvements** and **reverts regressions** via Git
4. **Cycles** through multiple free providers (OpenRouter :free models, NVIDIA NIM free tier)

Perfect for overnight optimization. Perfect for zero budget. Perfect for staying focused on ideas instead of infrastructure.

## Features

- ✅ **Zero cost** — uses only free LLM API tiers + credits
- 🔄 **Multi-provider router** — automatic failover when tier exhausted
- 🎯 **Git-backed** — reverts failed experiments instantly
- 📊 **Real-time dashboard** — monitor all projects from one UI
- 🪵 **Full audit trail** — experiments.jsonl logs every attempt
- 🔌 **Framework-agnostic** — works with prompts, code, configs, anything measurable
- ⚡ **Round-robin scheduling** — fair cycles through multiple projects
- 🛡️ **Budget caps** — never exceed daily spend limit

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    engine.py (main loop)                    │
│   Picks project → reads target → calls router for mutation  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    router.py (LLM selector)                 │
│   NVIDIA NIM (free) → OpenRouter :free → error             │
└────┬──────────────────┬─────────────────────────────────────┘
     │                  │
     ▼                  ▼
┌──────────┐     ┌─────────────┐
│  NVIDIA  │     │  OpenRouter  │
│  (nim)   │     │  (:free)     │
│   $0     │     │    $0        │
└──────────┘     └─────────────┘
                 │
                 ▼
    ┌─────────────────────────────┐
    │   generator.py (mutation)   │
    │  Rewrites prompt/code/cfg   │
    └────────────────┬────────────┘
                     │
                     ▼
    ┌─────────────────────────────┐
    │   eval_command (your test)  │
    │   Returns: score (float)    │
    └────────────────┬────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
    ┌────────┐              ┌──────────┐
    │ Score  │              │  Revert  │
    │ better │              │  via git │
    │ Keep   │              │ Discard  │
    └────────┘              └──────────┘
        │                         │
        └─────────────┬───────────┘
                      ▼
        ┌──────────────────────────┐
        │ experiments.jsonl (log)  │
        │ {attempt, score, delta}  │
        └──────────────────────────┘
```

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/alimajoray-sudo/free-autoresearch.git
cd free-autoresearch
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
# Edit .env with your keys (only ONE required)
export $(cat .env | xargs)
```

### 3. Create a Project

```bash
# Example: optimize a system prompt
bash scripts/init-project.sh my-prompt-optim prompts/system.txt "python eval.py"

# This creates:
# projects/my-prompt-optim/
#   ├── target.md               # your system prompt
#   ├── test-set.json           # evaluation test cases
#   ├── program.md              # instructions for mutation
#   ├── best/score.txt          # best score found
#   └── experiments.jsonl       # full log
```

### 4. Run the Engine

```bash
# Single project
python engine.py --project my-prompt-optim

# All projects (round-robin forever)
python engine.py

# One full cycle then exit
python engine.py --once
```

### 5. Monitor

```bash
# In another terminal
python dashboard/dashboard-server.py
# → http://localhost:8830
```

## Dashboard

Real-time web UI showing:
- **Projects overview** — status, best score, experiment count per project
- **Live experiment log** — last 100 mutations with score deltas
- **Router state** — which provider is active, quota status
- **Budget tracking** — daily spend vs cap
- **Engine events** — cycle timeline, project rotation

Built with FastAPI + live JSON polling. No database needed.

## Supported Providers

| Provider | Tier | Free Tier | Auth | Rate Limit | Notes |
|----------|------|-----------|------|-----------|-------|
| **OpenRouter** | 0 | Free models (Qwen, Llama, etc) | OPENROUTER_API_KEY | 20 req/min | Many models, strict limits |
| **NVIDIA NIM** | 0 | Free credits | NVIDIA_API_KEY | varies | Fast inference |

**Optional paid providers** (uncomment in `router.py` MODEL_POOL if desired):

| Provider | Tier | Cost | Auth | Notes |
|----------|------|------|------|-------|
| **xAI Grok** | 1 | ~$0.0003/call | XAI_API_KEY | Fast, reliable |
| **DeepSeek** | 2 | ~$0.0004/call | DEEPSEEK_API_KEY | Cheap fallback |

## How the Router Works

The router implements a **tiered failover strategy**:

1. **Tier 0 (free, preferred):** OpenRouter free models + NVIDIA NIM
   - Zero cost, rate-limited
   - Router tries all Tier 0 pools before moving on
   
2. **Optional paid tiers** (disabled by default):
   - Uncomment xAI/DeepSeek in `router.py` if you want faster fallbacks
   - Budget-capped to $0.50/day max

### Quota Tracking

Router tracks rate-limit rejections per provider in `state/quota.json`:
```json
{
  "openrouter/qwen:free": [
    {"timestamp": 1711975200, "wait_seconds": 60}
  ]
}
```

When a provider rejects, router:
1. Records the rate-limit window
2. Skips that provider for N seconds
3. Tries next tier
4. If all exhausted: waits gracefully, retries

### Budget Enforcement

Daily budget cap (default $0.50, configurable via `AUTORESEARCH_DAILY_BUDGET`):
```python
today_spend = sum(calls_today) * cost_per_token
if today_spend >= cap:
    skip_tier_2_providers()
```

## Use Cases

### 1. Prompt Optimization

```bash
# projects/contract-qa/program.md
You are optimizing a FIDIC contract Q&A system.
The target file is `target.md` (system prompt).
Improve accuracy on test-set.json (Q&A pairs).

Mutation ideas:
- Add better instruction for multi-clause synthesis
- Clarify section numbering format
- Add examples of exact value extraction
```

**Metric:** `python eval-qa.py` returns accuracy (0.0–1.0)

### 2. Code Optimization

```bash
# projects/fast-sort/program.md
Target file: sort.py (sorting implementation)
Metric: execution time (seconds)

Ideas for mutation:
- Change algorithm (quicksort → mergesort)
- Optimize inner loop
- Add caching
```

**Metric:** `time python sort.py data.json` extracts seconds

### 3. Config Tuning

```bash
# projects/model-config/program.md
Target: model_config.json
Metric: F1 score on validation set

Vary:
- learning_rate (0.0001–0.01)
- batch_size (16–512)
- regularization strength
```

**Metric:** `python train.py --config target.json` outputs JSON with f1_score

### 4. Content Quality

```bash
# projects/youtube-scripts/program.md
Target: scripts/intro.md (video script)
Metric: readability score

Improve:
- sentence length
- word choice
- pacing
```

**Metric:** `python readability-score.py scripts/intro.md` outputs float

### 5. Agent Instructions

```bash
# projects/agent-prompt/program.md
Target: agent_system.txt (system prompt for Claude)
Metric: task completion rate

Refine:
- action clarity
- error handling
- output format
```

**Metric:** `python eval-agent.py --prompt target.txt` outputs 0.0–1.0

## Configuration

### Environment Variables

```bash
# Required: at least ONE free provider
OPENROUTER_API_KEY=sk-or-v1-...    # Free :free models
NVIDIA_API_KEY=nvapi-...            # Free NIM credits

# Optional paid providers (uncomment in router.py to enable)
# XAI_API_KEY=xai-...              # ~$0.0003/call
# DEEPSEEK_API_KEY=sk-...          # ~$0.0004/call
# HF_TOKEN=hf_...                  # Free tier available

# Optional
AUTORESEARCH_DAILY_BUDGET=0.50          # USD/day, default 0.50
AUTORESEARCH_CYCLES_PER_PROJECT=5       # mutations per project before rotation
AUTORESEARCH_LOG_DIR=./logs             # where to write engine.jsonl
```

### Project Structure

Each project (`projects/<name>/`) contains:

```
projects/my-optim/
├── target.md              # File to mutate (prompt, code, config, etc)
├── test-set.json          # Eval test cases (JSON array)
├── program.md             # Mutation instructions for LLM
├── best/
│   └── score.txt          # Best score found so far
├── .git/                  # Git repo for reverting
├── experiments.jsonl      # Full log (one JSON per line)
└── .baseline              # Optional: initial score baseline
```

### Initialization Script

```bash
bash scripts/init-project.sh <project-name> <target-file-path> "<eval-command>"

# Example:
bash scripts/init-project.sh my-prompt prompts/system.txt "python eval.py"
```

This:
1. Creates `projects/<name>/` with git init
2. Copies target file → `target.md`
3. Generates `program.md` with generic mutation instructions
4. Runs eval command once for baseline
5. Stores baseline in `.baseline` for reference

## Project Structure

```
.
├── README.md
├── LICENSE
├── requirements.txt
├── .env.example
├── .gitignore
├── engine.py              # Main loop
├── router.py              # Multi-provider LLM router
├── generator.py           # Mutation generator
├── SKILL.md               # OpenClaw integration
│
├── dashboard/
│   ├── dashboard-server.py
│   └── dashboard.html
│
├── scripts/
│   ├── init-project.sh    # Create new project
│   ├── benchmark-models.py
│   └── monitor.sh
│
├── templates/             # Prompt templates for mutations
│   └── default.txt
│
├── eval-examples/         # Reference evaluation scripts
│   ├── eval-accuracy-ollama.py
│   ├── eval-task-completion.py
│   └── eval-latency.py
│
├── projects/              # User projects (git-ignored)
│   └── my-first-optim/
│       ├── target.md
│       ├── test-set.json
│       ├── program.md
│       ├── best/score.txt
│       └── experiments.jsonl
│
├── state/                 # Router state (git-ignored)
│   ├── quota.json
│   ├── budget.json
│   └── generator.jsonl
│
└── logs/                  # Engine logs (git-ignored)
    └── engine.jsonl
```

## Contributing

Contributions welcome! Areas:
- Additional evaluator templates
- Provider integrations (Anthropic, OpenAI with credits, etc.)
- Dashboard features (export, comparison, replay)
- Cost analysis and provider recommendations
- Project templates for specific domains

## License

MIT — see LICENSE file

## Credits

Inspired by [Andrej Karpathy's autoresearch](https://github.com/karpathy/autoresearch) concept and the philosophy of continuous AI-powered improvement loops.

---

**Questions?** Open an issue or start a discussion. Happy optimizing! 🚀
