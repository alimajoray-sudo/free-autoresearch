# Contributing to Free Context AutoResearch

Thanks for considering a contribution! This guide explains how to help improve the engine.

## Areas We Need Help

### 1. Provider Integrations

Add support for new free or cheap LLM APIs:
- Anthropic Claude (if credits available)
- Together.ai free tier
- Inference endpoints (any new provider)

**File:** `router.py` — add to `MODEL_POOL` and implement provider adapter

### 2. Evaluation Templates

New `eval-examples/` scripts for specific use cases:
- Cost estimation (tokens → USD)
- Sustainability metrics (carbon footprint)
- Latency benchmarking
- Code quality (cyclomatic complexity, test coverage)
- Content safety/toxicity

**Requirements:**
- Read from `target.md` (or `target.*`)
- Output single float to stdout
- Exit code 0 on success

### 3. Project Templates

Add new `examples/` folders for specific domains:
- `examples/code-optimization/` — sorting, ML models, etc.
- `examples/prompt-engineering/` — chatbot, Q&A, retrieval
- `examples/config-tuning/` — database, service configs
- `examples/content-quality/` — docs, scripts, marketing copy

**Include:**
- Minimal working example
- Sample target file
- Sample test-set.json
- Instructions in README

### 4. Dashboard Features

Enhance `dashboard/`:
- Export experiments to CSV/JSON
- Replay mutation history (timeline scrubber)
- Compare projects side-by-side
- Anomaly detection (unexpected score swings)
- Cost breakdown per provider

### 5. Engine Improvements

Core `engine.py`, `router.py`, `generator.py`:
- Better error messages
- Smarter rate-limit prediction
- Cost-accuracy trade-offs
- Parallel project execution (careful: API limits!)
- Experiment replay/undo functionality

### 6. Documentation

- Language guides (German, Spanish, French)
- Video tutorial walkthrough
- Blog post: "Optimizing prompts for 50% less token cost"
- Case studies from real projects

---

## Development Setup

### 1. Clone Locally

```bash
git clone https://github.com/yourusername/free-autoresearch.git
cd free-autoresearch
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
pip install pytest pytest-cov  # for testing
```

### 3. Configure Env

```bash
cp .env.example .env
# Add at least ONE API key for testing
```

### 4. Run Tests

```bash
# If tests exist, run them
pytest tests/ -v

# Otherwise, manual test:
python engine.py --once
```

---

## Code Style

**Keep it simple.** We prefer:
- 100-character line limit
- Type hints where helpful (not everywhere)
- Docstrings for functions + classes
- Comments for *why*, not *what*

Example:

```python
def select_provider(tier: int, exhausted: set[str]) -> str:
    """Pick next LLM provider, skipping exhausted ones.
    
    Args:
        tier: 0 (free) or 1+ (paid)
        exhausted: set of provider names at rate-limit
        
    Returns:
        Provider name (e.g., "openrouter/qwen:free")
    """
    # Try free tier providers in order of reliability
    for provider in FREE_PROVIDERS:
        if provider not in exhausted:
            return provider
    
    # All free exhausted, raise for retry logic
    raise RateLimitError("All free providers exhausted")
```

---

## Submission Process

### For Small Changes (docs, typos, eval templates)

1. Fork repo
2. Create feature branch: `git checkout -b add-llm-eval`
3. Make changes
4. Test locally
5. Commit: `git commit -m "feat: add LLM cost evaluator"`
6. Push: `git push origin add-llm-eval`
7. Open Pull Request

### For Major Features (new providers, engine rewrite)

1. **Open an Issue first** — describe the idea, why it matters
2. **Wait for feedback** — maintainers will discuss approach
3. **Create a draft PR** — reference the issue
4. **Iterate** — expect feedback, revise based on direction
5. **Merge** — once approved and tested

---

## Commit Message Style

```
type(scope): brief description

Longer explanation if needed. Keep to 72 chars per line.

Fixes #123
```

**Types:**
- `feat` — new feature
- `fix` — bug fix
- `docs` — documentation
- `refactor` — code reorganization (no behavior change)
- `test` — tests added/modified
- `perf` — performance improvement

**Examples:**
```
feat(router): add together.ai provider support
fix(engine): handle missing .git directory gracefully
docs(readme): clarify budget enforcement behavior
refactor(generator): simplify mutation prompt generation
```

---

## Testing

### Adding a New Eval Template

Create `eval-examples/eval-whatever.py`:

```python
#!/usr/bin/env python3
"""
Evaluation template: whatever metric.
Output: single float (score) to stdout.
"""

import json

def evaluate():
    # Read target file
    with open("target.md") as f:
        content = f.read()
    
    # Read test cases
    with open("test-set.json") as f:
        tests = json.load(f)
    
    # Your evaluation logic
    score = compute_score(content, tests)
    
    # Output
    print(f"{score:.4f}")

if __name__ == "__main__":
    evaluate()
```

Test it:

```bash
cd projects/test-project/
python ../../eval-examples/eval-whatever.py
# Should output: 0.8234
```

### Adding a New Provider

Modify `router.py`:

```python
# In MODEL_POOL, add tier 0 or 1

MODEL_POOL = {
    0: [  # Free tier
        ("openrouter/qwen:free", "openrouter"),
        ("my-new-provider/model", "my_provider"),  # NEW
    ],
    # ...
}

# Implement adapter function

def call_my_provider(prompt: str, api_key: str) -> str:
    """Call my new provider's API."""
    import requests
    
    response = requests.post(
        "https://api.myprovider.com/generate",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"prompt": prompt, "max_tokens": 2000}
    )
    
    if response.status_code != 200:
        raise RuntimeError(f"API error: {response.text}")
    
    return response.json()["text"]

# Register it

@router.register_provider("my_provider")
def route_my_provider(prompt: str) -> str:
    api_key = os.getenv("MY_PROVIDER_API_KEY")
    if not api_key:
        raise ValueError("MY_PROVIDER_API_KEY not set")
    return call_my_provider(prompt, api_key)
```

---

## Pull Request Checklist

Before submitting:

- [ ] Code follows style guide (100-char lines, type hints)
- [ ] All functions have docstrings
- [ ] Tests pass (if applicable)
- [ ] No hardcoded API keys or credentials
- [ ] No personal references (names, emails, etc.)
- [ ] Commit messages are descriptive
- [ ] README updated if new feature/breaking change
- [ ] CHANGELOG.md entry added (if exists)

---

## Questions?

- **Issues:** Use GitHub Issues for bugs, feature requests
- **Discussions:** Use GitHub Discussions for questions, ideas
- **Email:** Maintainers prefer issues over direct email

---

## Licensing

By contributing, you agree that your code will be licensed under the MIT License (same as the repo).

---

**Thank you for helping make prompt optimization accessible to everyone!** 🚀
