---
name: free-router
description: >
  Zero-cost LLM API router. Drop-in Python library that automatically selects
  from a pool of free and cheap LLM providers (OpenRouter free, HuggingFace,
  xAI Grok, DeepSeek), handles rate limits, falls back across providers, and
  enforces a daily budget cap. One import, one call. Use in any skill that
  needs LLM calls without burning API quota or money.
  Triggers on: "use free LLM", "free model router", "add LLM to this skill",
  "route to free model", "add AI call", "use ModelRouter".
---

# free-router

> One import. Unlimited free LLM calls. Auto-fallback. Budget-safe.

## Quick Start

```python
from router import ModelRouter, AllModelsExhausted

router = ModelRouter()
text, model, cost = router.complete("Summarize this contract clause: ...")
print(f"Used: {model} | Cost: ${cost:.5f}")
```

**That's it.** The router handles everything else:
- Tries free OpenRouter models first
- Falls back to HuggingFace if rate-limited
- Falls back to xAI/DeepSeek only if both free tiers exhausted
- Enforces $0.50/day cap on paid models
- Tracks quota across restarts (survives process restarts)

---

## Usage Patterns

### Basic call
```python
text, model, cost = router.complete("Your prompt here")
```

### With system prompt
```python
text, model, cost = router.complete(
    "What is the advance payment clause?",
    system="You are a construction contract expert. Answer concisely.",
)
```

### With message history
```python
text, model, cost = router.complete(
    messages=[
        {"role": "user", "content": "What does Sub-Clause 14.3 say?"},
    ],
    system="You are a FIDIC contract expert.",
)
```

### Role-based routing (for autoresearch)
```python
# "mutator" → creative/coding models (Qwen3-Coder, GLM)
text, model, cost = router.complete(prompt, role="mutator")

# "evaluator" → fast/cheap models (Nemotron, Llama-3B)
text, model, cost = router.complete(prompt, role="evaluator")
```

### Budget control
```python
# Hard $0.10/day cap (only use free models until that's hit)
router = ModelRouter(daily_budget=0.10)

# Check current spend
print(router.budget.status())
# → {"today_usd": 0.001, "cap_usd": 0.50, "remaining_usd": 0.499, "ok": true}
```

### Handle exhaustion gracefully
```python
try:
    text, model, cost = router.complete(prompt)
except AllModelsExhausted:
    # All 12 models rate-limited — wait and retry
    wait = router.get_wait_seconds()
    time.sleep(wait)
    text, model, cost = router.complete(prompt)
```

---

## Adding to a Skill

1. Copy `router.py` into your skill directory (or symlink it):
```bash
cp skills/free-router/router.py skills/my-skill/router.py
# or for system-wide access:
python3 skills/free-router/router.py --install
```

2. Import in your skill's Python script:
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../free-router"))
from router import ModelRouter, AllModelsExhausted
```

3. Replace any `codex exec` subprocess calls:
```python
# Before (Codex CLI — quota-limited, fragile):
result = subprocess.run(["codex", "exec", "--model", "gpt-5.3-codex", "-"],
                        input=prompt, capture_output=True, text=True, timeout=180)
response = result.stdout.strip()

# After (free-router — auto-fallback, budget-safe):
router = ModelRouter()
response, model_used, cost = router.complete(prompt)
```

---

## Model Pool (12 models)

| Tier | Provider | Model | Role | Cost |
|------|----------|-------|------|------|
| T0 | OpenRouter | `qwen/qwen3-coder:free` | both | FREE |
| T0 | OpenRouter | `z-ai/glm-4.5-air:free` | both | FREE |
| T0 | OpenRouter | `google/gemma-3-27b-it:free` | both | FREE |
| T0 | OpenRouter | `nvidia/nemotron-3-nano-30b-a3b:free` | evaluator | FREE |
| T0 | OpenRouter | `meta-llama/llama-3.2-3b-instruct:free` | evaluator | FREE |
| T1 | HuggingFace | `Qwen/Qwen2.5-72B-Instruct` | both | FREE |
| T1 | HuggingFace | `meta-llama/Llama-3.3-70B-Instruct` | both | FREE |
| T1 | HuggingFace | `Qwen/Qwen2.5-Coder-32B-Instruct` | both | FREE |
| T1 | HuggingFace | `Qwen/Qwen3-4B-Thinking-2507` | evaluator | FREE |
| T2 | xAI | `grok-3-mini` | both | $0.0005/1K |
| T2 | xAI | `grok-3-mini-fast` | evaluator | $0.00025/1K |
| T3 | DeepSeek | `deepseek-chat` | both | $0.00042/1K |

Free daily capacity: ~1,000 OpenRouter + ~unlimited HuggingFace ≈ **effectively unlimited at $0**.

---

## API Keys Required

Set in `~/.openclaw/.env`:

```bash
OPENROUTER_API_KEY=sk-or-v1-...   # Required for Tier 0 (free models)
HF_TOKEN=hf_...                   # Required for Tier 1 (free, read-only token ok)
XAI_API_KEY=xai-...               # Optional: Tier 2 (paid, cheap backup)
DEEPSEEK_API_KEY=sk-...           # Optional: Tier 3 (paid, cheapest backup)
```

The router silently skips any provider whose key is missing — no crash.

---

## CLI

```bash
# Show model pool + budget status
python3 skills/free-router/router.py --status

# Test all available models live
python3 skills/free-router/router.py --test

# Run a single prompt
python3 skills/free-router/router.py --prompt "What is 2+2?"

# Install system-wide (copy to site-packages)
python3 skills/free-router/router.py --install
```

---

## State Files

Router writes two JSON files in `skills/free-router/state/` (or `$ROUTER_STATE_DIR`):
- `quota.json` — per-model rolling request timestamps (2-min window)
- `budget.json` — per-day USD spend

Override state location:
```bash
ROUTER_STATE_DIR=/tmp/my-project-state python3 my_script.py
```

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `OPENROUTER_API_KEY` | — | OpenRouter auth |
| `HF_TOKEN` | — | HuggingFace token |
| `XAI_API_KEY` | — | xAI auth |
| `DEEPSEEK_API_KEY` | — | DeepSeek auth |
| `ROUTER_STATE_DIR` | `skills/free-router/state/` | Where quota.json + budget.json live |
| `ROUTER_DAILY_BUDGET` | `0.50` | Daily USD cap for paid tiers |

---

## Skills Using This Router

- `autoresearch` — continuous prompt optimizer (all 5 projects)
- Add yours here when integrated

## Related Skills

- `autoresearch` — uses this router for overnight experiment loops
- `machine-learning` — for structured ML training workflows
