#!/usr/bin/env python3
"""
agent-codex.py — Skill trigger accuracy optimizer.

Improves skill description texts for better query→skill routing.
Metric: how well test queries match the correct skill description keywords.
Uses free LLMs via ModelRouter.
"""
import gc
import json
import os
import re
import signal
import sys
import time
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from router import ModelRouter, AllModelsExhausted

_router = None
def get_router():
    global _router
    if _router is None:
        _router = ModelRouter(verbose=True)
    return _router

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_FILE = os.path.join(PROJECT_DIR, "system-prompt.md")
TEST_SET_FILE = os.path.join(PROJECT_DIR, "test-set.json")
RESULTS_FILE = os.path.join(PROJECT_DIR, "experiments.jsonl")
BEST_DIR = os.path.join(PROJECT_DIR, "best")
STATUS_FILE = "/tmp/skill-trigger-accuracy-status.json"

status = {
    "phase": "initializing", "experiment": 0, "max_experiments": 30,
    "best_score": 0.0, "model": "initializing",
    "started_at": datetime.now().isoformat(), "last_update": "",
    "improvements": 0, "regressions": 0, "skips": 0,
    "codex_calls": 0, "elapsed_seconds": 0, "model_log": [],
    "question_scores": [], "experiments_log": [],
}
start_time = time.time()
shutdown_requested = False

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def update_status(**kwargs):
    status.update(kwargs)
    status["last_update"] = datetime.now().isoformat()
    status["elapsed_seconds"] = int(time.time() - start_time)
    try:
        with open(STATUS_FILE, "w") as f:
            json.dump(status, f, indent=2)
    except Exception:
        pass

def handle_signal(sig, _frame):
    global shutdown_requested
    shutdown_requested = True
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

def llm_call(prompt, role="mutator", max_tokens=4096):
    router = get_router()
    try:
        text, model_used, cost = router.complete(prompt, role=role, max_tokens=max_tokens)
        status["codex_calls"] += 1
        status["model"] = model_used
        status["model_log"] = status.get("model_log", [])[-19:] + [
            {"model": model_used, "cost": cost, "status": "ok"}
        ]
        update_status()
        return text.strip() if text else ""
    except AllModelsExhausted:
        log("  All models exhausted, sleeping 60s")
        update_status(rate_limited=True)
        time.sleep(60)
        update_status(rate_limited=False)
        return ""
    except Exception as e:
        log(f"  Router error: {e}")
        return ""


def evaluate_descriptions(desc_text, tests):
    """
    For each test query, check if the expected keywords appear in the 
    description text. This simulates skill routing accuracy.
    """
    desc_lower = desc_text.lower()
    total = 0.0
    details = []
    
    for test in tests:
        keywords = test.get("expected_keywords", [])
        category = test.get("category", "?")
        matched = sum(1 for k in keywords if k.lower() in desc_lower)
        ratio = matched / len(keywords) if keywords else 0
        sc = 1.0 if ratio >= 0.5 else 0.0
        total += sc
        details.append({"id": test["id"], "category": category, "score": sc})
    
    return total / len(tests) if tests else 0.0, details


def generate_modification(current_text, best_score, history, weak_categories):
    modify_prompt = f"""You are optimizing skill description texts for an AI assistant's skill router.
Each skill has a description section. When a user sends a query, the router matches it against descriptions.

Current descriptions (accuracy: {best_score:.2f}):
```
{current_text[:6000]}
```

Weak categories (these skills are NOT being triggered correctly):
{weak_categories}

Recent history:
{history if history else "  (first modification)"}

TASK: Improve the skill descriptions so they better match user queries.
- Add common trigger phrases and synonyms
- Keep descriptions concise (<200 chars each)
- Don't add keywords that would cause false positives
- Focus on the weak categories above

Output the COMPLETE updated skill descriptions file. No explanation."""

    return llm_call(modify_prompt, role="mutator", max_tokens=8192)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=30)
    parser.add_argument("--forever", action="store_true")
    args = parser.parse_args()
    max_exp = args.max if not args.forever else 999999

    log("=" * 50)
    log("  Skill Trigger Accuracy Optimizer")
    log("=" * 50)

    tests = json.load(open(TEST_SET_FILE))
    current_text = open(TARGET_FILE).read()

    # Baseline
    best_score, q_scores = evaluate_descriptions(current_text, tests)
    log(f"Baseline accuracy: {best_score:.4f}")
    best_text = current_text
    
    os.makedirs(BEST_DIR, exist_ok=True)
    with open(os.path.join(BEST_DIR, "score.txt"), "w") as f:
        f.write(f"{best_score:.4f}\n")
    with open(os.path.join(BEST_DIR, "system-prompt.md"), "w") as f:
        f.write(current_text)

    for exp_n in range(1, max_exp + 1):
        if shutdown_requested:
            break

        update_status(phase="modifying", experiment=exp_n)
        log(f"\nExperiment #{exp_n} | Best: {best_score:.4f}")

        # Find weak categories
        cat_scores = defaultdict(list)
        for d in q_scores:
            cat_scores[d["category"]].append(d["score"])
        weak = [c for c, scores in cat_scores.items() if sum(scores)/len(scores) < 1.0]
        weak_text = "\n".join(f"  - {c}" for c in weak) if weak else "  (all good)"

        history = ""
        if os.path.exists(RESULTS_FILE):
            for line in open(RESULTS_FILE).readlines()[-5:]:
                try:
                    e = json.loads(line.strip())
                    history += f"  #{e['experiment']}: {e['score']:.4f} ({e['status']})\n"
                except Exception:
                    pass

        new_text = generate_modification(open(TARGET_FILE).read(), best_score, history, weak_text)
        
        if not new_text or len(new_text) < 100:
            log("  Empty/short, skipping")
            status["skips"] += 1
            entry = {"experiment": exp_n, "score": best_score, "status": "skip", "timestamp": datetime.now().isoformat()}
            with open(RESULTS_FILE, "a") as f:
                f.write(json.dumps(entry) + "\n")
            continue

        if new_text.startswith("```"):
            lines = new_text.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            new_text = "\n".join(lines).strip()

        # Evaluate
        with open(TARGET_FILE, "w") as f:
            f.write(new_text)
        new_score, new_details = evaluate_descriptions(new_text, tests)
        
        entry = {"experiment": exp_n, "score": round(new_score, 4), "prev_score": round(best_score, 4),
                 "delta": round(new_score - best_score, 4), "timestamp": datetime.now().isoformat()}

        if new_score > best_score:
            log(f"  ✓ IMPROVED: {best_score:.4f} → {new_score:.4f}")
            best_score = new_score
            best_text = new_text
            q_scores = new_details
            with open(os.path.join(BEST_DIR, "score.txt"), "w") as f:
                f.write(f"{best_score:.4f}\n")
            with open(os.path.join(BEST_DIR, "system-prompt.md"), "w") as f:
                f.write(new_text)
            status["improvements"] += 1
            entry["status"] = "keep"
        else:
            log(f"  ✗ No improvement: {new_score:.4f}")
            with open(TARGET_FILE, "w") as f:
                f.write(best_text)
            status["regressions"] += 1
            entry["status"] = "discard"
        
        with open(RESULTS_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        gc.collect()
        time.sleep(2)

    log(f"\nDone! Best accuracy: {best_score:.4f}")
    log(f"Improvements: {status['improvements']} | LLM calls: {status['codex_calls']}")


if __name__ == "__main__":
    main()
