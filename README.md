# 🔬 Free Context AutoResearch

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/downloads/)
[![Zero Cost](https://img.shields.io/badge/Cost-$0-brightgreen.svg)](https://github.com/alimajoray-sudo/free-autoresearch)

**Compress your system prompts by 15–20% overnight. For free.**

Free Context AutoResearch is the first open-source autonomous improvement engine that optimizes AI system prompts, agent instructions, and context windows using only free LLM API tiers. Run 26 experiments in 10 minutes, achieve 16.3% prompt compression while maintaining 85% task accuracy—all for **$0.006 total cost**.

Perfect for developers who want to:
- ✅ Reduce token usage and inference latency
- ✅ Optimize system prompts without spending a cent
- ✅ Run overnight experiments on a free tier budget
- ✅ Improve code, configs, and any measurable artifact

## The Idea

Inspired by [Andrej Karpathy's autoresearch](https://github.com/karpathy/autoresearch), this engine treats **system prompt optimization as a search problem**. It:

1. **Mutates** your system prompt or config using a free LLM
2. **Evaluates** the change by running your test suite
3. **Keeps improvements**, reverts failures via Git
4. **Cycles** through multiple free providers to avoid rate limits

No paid APIs. No monthly bills. Just smart, automated improvement loops.

---

## Key Results

**Production Example: System Prompt Compression**

```
Baseline:  5,500 characters, 85% task accuracy
Run:       26 experiments in ~13 minutes
Best:      4,605 characters, 85% task accuracy maintained

Compression: 5500 → 4605 chars = 16.3% reduction
Cost:        $0.006 total (free tier overflow)
Improvements: 9 successful mutations, 17 discarded
Time:        ~30 seconds per experiment (free LLM latency)
```

**Why this matters:**
- **16.3% fewer tokens** = faster inference + lower latency
- **Same accuracy** = no quality loss
- **Overnight runs** = fire-and-forget improvement
- **$0 cost** = can optimize every repo, every night

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│         engine.py — Main Orchestration Loop                  │
│  Discover projects → round-robin cycling → error handling   │
└─────────────────┬──────────────────────────────────────────┘
                  │
      ┌───────────┴────────────┐
      ▼                        ▼
  ┌─────────────┐         ┌──────────────┐
  │ Router      │         │ Generator    │
  │ (LLM pool)  │         │ (mutation)   │
  └─────────────┘         └──────────────┘
      ▲                        ▲
      │                        │
  ┌───┴────────────────────────┘
  │
  ├─ NVIDIA NIM (free)
  │  → Qwen, Llama, Mixtral
  │  → Zero cost, fast
  │
  ├─ OpenRouter :free
  │  → Qwen, Llama, Gemma
  │  → 20 req/min, $0
  │
  └─ HuggingFace API
     → 70B models free
     → 30 req/min, $0
        │
        ▼
    ┌──────────────┐
    │ Your eval.py │
    │ Returns: score
    └──────────────┘
        │
        ├─ Score improved? → Git commit, keep
        │
        └─ Score dropped? → Git revert, discard
             │
             ▼
        experiments.jsonl
        (full audit trail)
```

---

## Quick Start (2 Minutes)

### 1. Clone & Install

```bash
git clone https://github.com/alimajoray-sudo/free-autoresearch.git
cd free-autoresearch
pip install -r requirements.txt
```

### 2. Get One Free API Key

Pick **one** of these free tiers (no credit card needed for NVIDIA/HuggingFace):

```bash
# Option A: NVIDIA NIM (simplest, fastest)
# → Sign up: https://build.nvidia.com/
# → Copy your key

# Option B: OpenRouter :free models
# → Sign up: https://openrouter.ai/
# → Copy your key

# Option C: HuggingFace Inference API
# → Sign up: https://huggingface.co/
# → Create read token
```

### 3. Configure

```bash
cp .env.example .env
nano .env  # or vi .env

# Paste ONE key:
# NVIDIA_API_KEY=nvapi-...
# OR
# OPENROUTER_API_KEY=sk-or-v1-...
# OR
# HF_TOKEN=hf_...

export $(cat .env | xargs)
```

### 4. Create Your First Project

```bash
# Initialize: target file + eval command
bash scripts/init-project.sh my-prompt-optim prompts/system.txt "python eval.py"

# This creates:
# projects/my-prompt-optim/
#   ├── target.md              # Your system prompt
#   ├── test-set.json          # Evaluation test cases
#   ├── program.md             # Mutation instructions
#   ├── best/score.txt         # Best score found
#   └── experiments.jsonl      # Full log
```

### 5. Run the Engine

```bash
# Single optimization run
python engine.py --project my-prompt-optim

# Monitor in another terminal
python dashboard/dashboard-server.py
# → Open http://localhost:8830
```

Done. The engine will now:
- Mutate your prompt using a free LLM
- Run your eval command
- Keep improvements, revert failures
- Log every experiment
- Repeat forever (or until Ctrl+C)

---

## Free Provider Support

| **Provider** | **Free Tier** | **Models** | **Rate Limit** | **Auth** |
|---|---|---|---|---|
| **NVIDIA NIM** | ✅ Yes | Qwen, Llama, Mixtral | varies | `NVIDIA_API_KEY` |
| **OpenRouter** | ✅ Yes (:free) | Qwen, Llama, Gemma | 20/min | `OPENROUTER_API_KEY` |
| **HuggingFace** | ✅ Yes | Qwen-72B, Llama-70B | 30/min | `HF_TOKEN` |

**18 free models tested across 3 providers.** Router automatically:
- Tries all Tier-0 providers before hitting rate limits
- Skips exhausted providers for cool-down period
- Tracks quota in `state/quota.json`
- Fails gracefully when all tiers exhausted

**Optional paid tiers** (disabled by default):
- xAI Grok (~$0.0003/call) — uncomment in `router.py`
- DeepSeek (~$0.0004/call) — uncomment in `router.py`

---

## Use Cases

### 1. System Prompt Compression

Reduce token count while maintaining task accuracy.

```bash
# Create project
bash scripts/init-project.sh system-prompt prompts/system.md "python eval-accuracy.py"

# projects/system-prompt/program.md:
# "You are optimizing a system prompt for an AI agent.
#  The file is target.md. Your goal: remove redundant sentences,
#  clarify instructions, eliminate examples that don't add value.
#  Keep task accuracy ≥85% (check via test-set.json)"

python engine.py --project system-prompt
```

**Result:** 5500 → 4605 chars (16.3% reduction), 85% accuracy maintained.

### 2. Agent Instructions Refinement

Improve action clarity, error handling, output format for autonomous agents.

```bash
bash scripts/init-project.sh agent-prompt agent_system.txt "python eval-completion.py"

# mutations focus on:
# - Clarifying step-by-step reasoning
# - Reducing instruction length
# - Improving structured output format
```

### 3. Code Optimization

Rewrite function implementations for speed, readability, or token efficiency.

```bash
bash scripts/init-project.sh sort-optimizer sort.py "time python sort.py | grep real"

# mutations:
# - Algorithm changes (quicksort → mergesort)
# - Loop optimizations
# - Cache strategies
```

### 4. Config Tuning

Automatically adjust hyperparameters, model settings, or service configs.

```bash
bash scripts/init-project.sh model-config model_config.json "python train.py --config target.json"

# mutations:
# - learning_rate: 0.0001 → 0.01
# - batch_size: 16 → 512
# - dropout, regularization, warmup
```

### 5. Content Quality Improvement

Optimize video scripts, documentation, or content for readability.

```bash
bash scripts/init-project.sh youtube-script scripts/intro.md "python eval-readability.py"

# mutations:
# - Sentence length (goal: <15 words avg)
# - Word choice (common → precise)
# - Pacing and transitions
```

---

## How It Works (Details)

### Project Structure

Each project (`projects/<name>/`) is a self-contained optimization loop:

```
projects/my-optim/
├── target.md               # File to improve (prompt, code, config, etc)
├── test-set.json           # Test cases for evaluation (JSON array)
├── program.md              # Instructions for how to mutate
├── best/
│   └── score.txt          # Best score found so far
├── .git/                   # Git repo for safe reverting
└── experiments.jsonl       # Full log (one JSON per line)
```

### The Optimization Loop

**Each cycle:**

1. **Engine** picks next project (round-robin)
2. **Router** selects a free LLM (tries Tier-0, then paid if enabled)
3. **Generator** reads target + program.md, calls LLM for mutation
4. **Your eval** runs, returns score (float)
5. **Decision:**
   - Score improved? → Git commit (keep), update best/score.txt
   - Score dropped? → Git revert (discard), mark as failed
6. **Log** entry written to experiments.jsonl with delta, status, timestamp

### Experiment Log Example

```json
{
  "experiment": 28,
  "timestamp": "2026-04-03T00:23:47.633435",
  "status": "keep",
  "score": 1.0187,
  "prev_score": 1.0152,
  "delta": 0.0035,
  "description": "+0.0035, 4589 chars, acc=0.85"
}
```

### Evaluation Contract

Your eval command must:
- Accept zero arguments (reads `target.md` or `target.*` internally)
- Return **single float** to stdout (the score)
- Exit with code 0 on success, non-zero on error

```python
# eval-accuracy.py example
import json

with open("test-set.json") as f:
    tests = json.load(f)

correct = 0
for test in tests:
    result = run_your_model(test)
    correct += evaluate(result, test["expected"])

accuracy = correct / len(tests)
print(accuracy)
```

---

## Configuration

### Environment Variables

```bash
# Required: at least ONE free provider
OPENROUTER_API_KEY=sk-or-v1-...    # OpenRouter :free models
NVIDIA_API_KEY=nvapi-...            # NVIDIA NIM free tier
HF_TOKEN=hf_...                     # HuggingFace free tier

# Optional
AUTORESEARCH_DAILY_BUDGET=0.50      # USD/day max (default: $0.50)
AUTORESEARCH_CYCLES_PER_PROJECT=5   # Mutations per project before rotating
AUTORESEARCH_LOG_DIR=./logs         # Engine log location
```

### Budget Enforcement

Router tracks spend via `state/budget.json`:

```json
{
  "date": "2026-04-03",
  "spent": 0.006,
  "limit": 0.50
}
```

When daily budget exhausted:
1. Skip all paid tier providers (xAI, DeepSeek)
2. Retry free tiers only (NVIDIA, OpenRouter, HuggingFace)
3. If all free exhausted: sleep for 1 hour, check budget again

---

## Dashboard

**Real-time monitoring UI** (zero database required):

```bash
python dashboard/dashboard-server.py
# → http://localhost:8830
```

Shows:
- **Projects overview** — status, best score, experiment count
- **Live mutation log** — last 100 mutations with score deltas
- **Provider health** — active provider, quota status, cool-down timers
- **Budget tracking** — daily spend vs cap
- **Timeline** — cycle start/end, project rotation events

Updates via live JSON polling. Lightweight, no persistence.

---

## Examples & Templates

**Included templates:**

- `eval-examples/eval-accuracy.py` — Task accuracy (0.0–1.0)
- `eval-examples/eval-task-completion.py` — Completion rate
- `eval-examples/eval-readability.py` — Readability score
- `eval-examples/eval-latency.py` — Response time

**In `examples/system-prompt-compression/`:**
- Sample system prompt to compress
- Sample test-set.json (Q&A pairs)
- Sample agent-codex.py (mutation instructions)
- README with copy-paste setup

---

## Contributing

Contributions welcome! Areas:
- Additional evaluator templates (cost, sustainability, etc.)
- Provider integrations (Anthropic, Claude credits, etc.)
- Dashboard enhancements (export, replay, comparison)
- Project templates for specific domains
- Cost analysis and provider recommendations

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## FAQ

**Q: Why does it need 40 minutes per run?**
A: Free tier rate limits. At 20 req/min, each mutation takes 30–60 seconds. Budget model latency into your cycle time.

**Q: Can I use paid APIs?**
A: Yes. Uncomment xAI/DeepSeek in `router.py`. Budget cap enforces daily limits.

**Q: What if my eval command fails?**
A: Engine logs the error, marks as failed, reverts git. Next project rotates in.

**Q: Can I run multiple projects?**
A: Yes. Engine cycles through all `projects/*/` round-robin. Add projects anytime.

**Q: Is my code safe from git errors?**
A: Yes. Every mutation is committed before eval. If eval fails, git revert restores previous state.

**Q: Can I pause the engine?**
A: Yes. Ctrl+C stops cleanly. Run `python engine.py --once` to test single cycle.

---

## License

MIT — see [LICENSE](LICENSE) file.

---

## Inspiration

Built on the philosophy of [Andrej Karpathy's autoresearch](https://github.com/karpathy/autoresearch): **continuous AI-powered improvement loops that run forever, finding better solutions faster than humans can analyze them.**

This implementation adds **zero-cost operation** through multi-provider routing and free API tier orchestration.

---

**Ready to optimize?** [Quickstart above](#quick-start-2-minutes) gets you running in 120 seconds.

Questions? Open an issue or start a discussion. 🚀
