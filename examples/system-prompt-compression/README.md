# Example: System Prompt Compression

**Goal:** Reduce system prompt token count while maintaining task accuracy.

This example shows how to use Free Context AutoResearch to automatically compress and optimize an AI system prompt overnight.

## What You'll Learn

- How to set up a project for prompt optimization
- How to write evaluation scripts that measure accuracy
- How to interpret the experiment log
- How to extract the best optimized prompt

## Files in This Example

```
├── README.md                  # This file
├── system-prompt.md           # Sample system prompt (target)
├── test-set.json              # Evaluation test cases (Q&A pairs)
├── agent-codex.py             # Mutation instructions for LLM
└── eval-accuracy.py           # Evaluation script
```

---

## Quick Start

### 1. Copy This Example

```bash
cp -r examples/system-prompt-compression ~/my-prompt-optim
cd ~/my-prompt-optim
```

### 2. Set Up Environment

Ensure your `.env` is configured with at least one free API key:

```bash
# In the root of free-autoresearch/
cat .env  # Should have OPENROUTER_API_KEY, NVIDIA_API_KEY, or HF_TOKEN
```

### 3. Initialize the Project

From the **root** of `free-autoresearch/`:

```bash
bash scripts/init-project.sh demo-prompt-compress examples/system-prompt-compression/system-prompt.md "python examples/system-prompt-compression/eval-accuracy.py"

# This creates: projects/demo-prompt-compress/
```

### 4. Run the Engine (Single Cycle)

```bash
# One full optimization cycle
python engine.py --project demo-prompt-compress --once

# Or run forever
python engine.py --project demo-prompt-compress
```

### 5. Monitor Progress

In another terminal:

```bash
python dashboard/dashboard-server.py
# → Open http://localhost:8830
```

Or tail the experiment log:

```bash
tail -f projects/demo-prompt-compress/experiments.jsonl | jq .
```

### 6. Extract Best Prompt

Once the engine finishes (or after a few cycles):

```bash
# Best prompt is here
cat projects/demo-prompt-compress/best/system-prompt.md

# Compare to original
diff examples/system-prompt-compression/system-prompt.md \
     projects/demo-prompt-compress/best/system-prompt.md
```

---

## How It Works

### The Target: `system-prompt.md`

A sample AI agent system prompt (~5500 chars):

```markdown
# System Prompt

You are an expert AI assistant...
[multi-page instructions]
```

**Goal:** Reduce token count while keeping task accuracy ≥85%.

### The Test Set: `test-set.json`

Evaluation cases in Q&A format:

```json
[
  {
    "question": "What are the contract terms?",
    "expected": "Price: $100k, Duration: 12 months"
  },
  {
    "question": "Who is the primary contact?",
    "expected": "John Doe, john@example.com"
  }
]
```

The engine uses this to measure if mutations degrade accuracy.

### The Evaluator: `eval-accuracy.py`

Runs each test case against the **current** system prompt:

```python
# Pseudocode
for test in test_set:
    response = ai_model.generate(test["question"])
    correct += evaluate_response(response, test["expected"])

accuracy = correct / len(test_set)
print(accuracy)
```

**Contract:** Output single float (0.0–1.0) to stdout, exit code 0.

### The Mutation Instructions: `agent-codex.py`

Tells the free LLM **how** to mutate the prompt:

```markdown
You are optimizing a system prompt for an AI agent.

The current prompt is in target.md (5500 chars).
Your goal: reduce token count while keeping accuracy ≥85%.

Ideas:
- Remove redundant sentences
- Consolidate similar instructions
- Eliminate low-value examples
- Clarify ambiguous phrases
- Use abbreviations where safe
```

The engine sends this + the current prompt to the free LLM, which returns a mutated version.

### The Loop

**Each cycle:**

1. **Engine** reads target.md + agent-codex.py
2. **Router** picks a free LLM
3. **Generator** sends prompt mutation request
4. **File system** updates target.md with mutation
5. **Your eval** runs, measures accuracy
6. **Decision:**
   - Accuracy ≥85% AND token reduction? → Git commit (keep)
   - Accuracy <85%? → Git revert (discard)
7. **Log** entry written with delta, status, timestamp

---

## Expected Results

After **26 experiments in ~13 minutes**:

```
Baseline:  5500 chars, 85% accuracy
Best:      4605 chars, 85% accuracy maintained
Reduction: 16.3% compression
Cost:      $0.006 (free tier overflow)
```

Your actual results may vary based on:
- System prompt complexity
- Test set quality (more rigorous → slower compression)
- Eval script accuracy
- LLM mutation quality (free vs. paid)

---

## Customizing This Example

### Use Your Own System Prompt

Replace `system-prompt.md` with your actual prompt:

```bash
cp /path/to/your/system-prompt.md examples/system-prompt-compression/system-prompt.md
```

### Use Your Own Test Cases

Replace `test-set.json` with your evaluation cases:

```json
[
  {
    "question": "Your question here",
    "expected": "Expected answer here"
  }
]
```

### Implement Your Own Evaluator

Replace `eval-accuracy.py` with your metric:

```python
#!/usr/bin/env python3

import json
import subprocess
import sys

# Read the current prompt
with open("target.md") as f:
    prompt = f.read()

# Read test cases
with open("test-set.json") as f:
    tests = json.load(f)

# Evaluate (your logic here)
score = my_evaluation_function(prompt, tests)

# Output
print(f"{score}")
```

**Key requirement:** Output single float to stdout, exit code 0.

---

## Interpreting the Experiment Log

After running, `projects/demo-prompt-compress/experiments.jsonl` contains:

```json
{
  "experiment": 0,
  "timestamp": "2026-04-03T00:09:52.860852",
  "status": "baseline",
  "score": 0.85,
  "delta": 0.0,
  "description": "Original 5500 chars"
}

{
  "experiment": 1,
  "timestamp": "2026-04-03T00:10:10.501339",
  "status": "keep",
  "score": 1.0152,
  "prev_score": 0.85,
  "delta": 0.1652,
  "description": "+0.1652, 4750 chars, acc=0.87"
}

{
  "experiment": 2,
  "timestamp": "2026-04-03T00:10:31.329231",
  "status": "discard-accuracy",
  "score": 0.9147,
  "prev_score": 1.0152,
  "delta": -0.1005,
  "description": "acc=0.79 < 0.85, reverted"
}
```

**Fields:**
- `experiment` — sequence number
- `status` — baseline / keep / discard-accuracy / discard-*
- `score` — compression score (lower = fewer tokens)
- `delta` — change from previous best
- `description` — human-readable summary

**Reading the log:**
- `status: keep` = improvement found, committed to git
- `status: discard-accuracy` = accuracy dropped, reverted
- `delta > 0` = worse compression (higher score = more chars preserved)
- `delta < 0` = better compression (lower score = fewer chars)

---

## Tips for Best Results

### 1. Start with a Good Baseline

- Your original prompt should be reasonably well-written
- Fuzzy, contradictory, or bloated prompts are harder to compress
- Add 2–3 examples to your test set before optimizing

### 2. Tune Your Evaluation Threshold

Edit `eval-accuracy.py` to require accuracy ≥X%:

```python
ACCURACY_THRESHOLD = 0.85  # or higher for stricter requirements
```

Lower threshold → more aggressive compression (but quality risk).
Higher threshold → slower compression (but safer).

### 3. Run Overnight

```bash
# Fire this off at bedtime, check results in the morning
nohup python engine.py --project demo-prompt-compress > engine.log 2>&1 &
```

Or use cron/scheduler for recurring overnight runs.

### 4. Monitor the Dashboard

```bash
python dashboard/dashboard-server.py
```

Watch for:
- Plateaus (no improvement after N cycles → compression maxed out)
- Anomalies (sudden accuracy drop → eval script issue)
- Cost creep (if using paid tiers → adjust budget cap)

### 5. Try Multiple Runs

Run the same project multiple times. Different random seeds in LLM = different mutations = may find different optimizations.

---

## Troubleshooting

### "API key not found"

Check `.env` in root of `free-autoresearch/`:

```bash
cat .env | grep -E "OPENROUTER|NVIDIA|HF_TOKEN"
```

Must have at least one.

### "eval-accuracy.py not found"

Run from **root** of `free-autoresearch/`, not from `examples/`:

```bash
cd ~/Projects/free-autoresearch
python engine.py --project demo-prompt-compress --once
```

### "Accuracy keeps dropping"

1. **Check your test set:** Are test cases representative?
2. **Check your eval script:** Does it correctly measure accuracy?
3. **Adjust threshold:** Reduce `ACCURACY_THRESHOLD` to allow more mutations
4. **Check the mutations:** Review git diffs to see what changed

```bash
cd projects/demo-prompt-compress/
git log --oneline | head -5
git show HEAD  # Latest kept mutation
```

### "Not finding improvements"

Free LLMs have limited mutation creativity. Try:
- Longer eval cycles (more attempts = more variety)
- Modify `agent-codex.py` with more mutation ideas
- Add specific examples/constraints to the program
- Or: enable paid tiers in `router.py` for better mutations

---

## Next Steps

### Adapt for Your Use Case

1. **Code optimization:** Change target to `.py` file, eval to measure speed/quality
2. **Config tuning:** Use `model_config.json`, eval to measure ML metrics
3. **Documentation:** Use markdown docs, eval for readability score
4. **Agent prompts:** Use your actual system prompt, test for task completion

### Add More Providers

Edit `router.py` to include Anthropic, OpenAI, or other APIs:

```python
# Uncomment paid tiers in MODEL_POOL
MODEL_POOL[1] = [
    ("xai/grok-3", "xai"),
    ("deepseek/deepseek-chat", "deepseek"),
]
```

### Run Multiple Projects

```bash
# Create another project
bash scripts/init-project.sh my-code-optim code.py "python benchmark.py"

# Engine will now round-robin between both
python engine.py
```

---

## Questions?

- **How do I extract the best prompt?**
  ```bash
  cat projects/demo-prompt-compress/best/system-prompt.md
  ```

- **How do I replay an experiment?**
  ```bash
  cd projects/demo-prompt-compress/
  git checkout <experiment-commit-hash>
  # Now target.md is at that state
  ```

- **How do I change the evaluation metric?**
  Replace `eval-accuracy.py` with your own script that outputs a float.

- **Can I parallelize multiple projects?**
  Yes. Run multiple `engine.py` instances with `--project` filter.

---

**Ready to compress?** Start the engine and check back in the morning! 🚀
