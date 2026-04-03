#!/usr/bin/env python3
"""
agent-codex.py — System prompt compressor.

Compresses SOUL+AGENTS+USER+TOOLS.md while preserving all critical info.
Metric: accuracy × compression_ratio (higher = better).
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

# ── ModelRouter ─────────────────────────────────────────────────────
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

# ── Config ──────────────────────────────────────────────────────────
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_FILE = os.path.join(PROJECT_DIR, "system-prompt.md")
PROGRAM_FILE = os.path.join(PROJECT_DIR, "program.md")
TEST_SET_FILE = os.path.join(PROJECT_DIR, "test-set.json")
RESULTS_FILE = os.path.join(PROJECT_DIR, "experiments.jsonl")
BEST_DIR = os.path.join(PROJECT_DIR, "best")
STATUS_FILE = f"/tmp/skill-yt-tutorial-learner-status.json"

ORIGINAL_SIZE = None  # set at startup

# ── Status ──────────────────────────────────────────────────────────
status = {
    "phase": "initializing", "experiment": 0, "max_experiments": 50,
    "best_score": 0.0, "current_score": 0.0, "baseline_score": 0.0,
    "model": "initializing", "started_at": datetime.now().isoformat(),
    "last_update": "", "current_question": "", "current_question_id": 0,
    "total_questions": 0, "question_scores": [], "experiments_log": [],
    "improvements": 0, "regressions": 0, "skips": 0,
    "codex_calls": 0, "elapsed_seconds": 0, "eta_minutes": 0,
    "rate_limited": False, "error": None, "model_log": [],
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
    if status["experiment"] > 0:
        avg = status["elapsed_seconds"] / status["experiment"]
        remaining = status["max_experiments"] - status["experiment"]
        status["eta_minutes"] = round(avg * remaining / 60, 1)
    try:
        with open(STATUS_FILE, "w") as f:
            json.dump(status, f, indent=2)
    except Exception:
        pass


def handle_signal(sig, _frame):
    global shutdown_requested
    shutdown_requested = True
    log(f"Signal {sig} received — finishing current experiment then exiting")

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)


# ── LLM Call ────────────────────────────────────────────────────────
def llm_call(prompt: str, role: str = "mutator", max_tokens: int = 4096) -> str:
    router = get_router()
    try:
        text, model_used, cost = router.complete(prompt, role=role, max_tokens=max_tokens)
        status["codex_calls"] += 1
        status["model"] = model_used
        status["model_log"] = status.get("model_log", [])[-19:] + [
            {"model": model_used, "cost": cost, "status": "ok", "ts": datetime.now().isoformat()}
        ]
        update_status()
        return text.strip() if text else ""
    except AllModelsExhausted as e:
        log(f"  [router] All models exhausted: {e}")
        status["model_log"].append({"model": "ALL", "cost": 0, "status": "exhausted"})
        update_status(rate_limited=True, error=str(e))
        time.sleep(60)
        update_status(rate_limited=False, error=None)
        return ""
    except Exception as e:
        log(f"  [router] Error: {e}")
        update_status(error=str(e))
        return ""


# ── Evaluator (deterministic, no LLM judge) ─────────────────────────
def evaluate_prompt(prompt_text: str, tests: list) -> tuple[float, list]:
    """
    Score = keyword_accuracy × compression_ratio.
    
    keyword_accuracy: for each test case, check if expected_keywords appear in prompt_text.
    compression_ratio: original_chars / current_chars (capped at 2.0 to prevent empty results scoring high).
    """
    # Keyword accuracy: does the compressed prompt still contain the info?
    total_score = 0.0
    details = []
    prompt_lower = prompt_text.lower()
    
    for test in tests:
        qid = test["id"]
        keywords = test.get("expected_keywords", [])
        category = test.get("category", "?")
        
        if not keywords:
            details.append({"id": qid, "category": category, "score": 1.0})
            total_score += 1.0
            continue
        
        matched = sum(1 for k in keywords if k.lower() in prompt_lower)
        ratio = matched / len(keywords)
        
        # Strict: all keywords must be present for full score
        if ratio >= 1.0:
            sc = 1.0
        elif ratio >= 0.75:
            sc = 0.75
        elif ratio >= 0.5:
            sc = 0.5
        else:
            sc = 0.0
        
        total_score += sc
        details.append({"id": qid, "category": category, "score": sc, "matched": matched, "total": len(keywords)})
    
    accuracy = total_score / len(tests) if tests else 0.0
    
    # Compression ratio: reward shorter prompts
    current_size = len(prompt_text)
    if current_size < 100:  # Too short = destroyed
        compression_bonus = 0.0
    else:
        compression_ratio = ORIGINAL_SIZE / current_size
        compression_bonus = min(compression_ratio, 2.0)  # Cap at 2x
    
    # Final score: accuracy * compression_bonus
    # At baseline (no compression), compression_bonus = 1.0, so score = accuracy
    # With 50% compression and same accuracy, score = accuracy * 2.0
    final_score = accuracy * compression_bonus
    
    return final_score, details


# ── File Helpers ────────────────────────────────────────────────────
def read_file(path):
    with open(path) as f:
        return f.read()

def write_file(path, content):
    # Safety: never write outside project directory
    real_path = os.path.realpath(path)
    real_project = os.path.realpath(PROJECT_DIR)
    if not real_path.startswith(real_project):
        raise RuntimeError(f"SAFETY: refusing to write outside project dir: {real_path}")
    with open(path, "w") as f:
        f.write(content)

def log_experiment(n, score, prev, exp_status, desc):
    entry = {
        "experiment": n, "timestamp": datetime.now().isoformat(),
        "score": round(score, 4), "prev_score": round(prev, 4),
        "delta": round(score - prev, 4), "status": exp_status,
        "description": desc,
        "chars": len(read_file(TARGET_FILE)),
    }
    with open(RESULTS_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    status["experiments_log"].append(entry)
    update_status()

def save_best(score, prompt):
    os.makedirs(BEST_DIR, exist_ok=True)
    write_file(os.path.join(BEST_DIR, "system-prompt.md"), prompt)
    write_file(os.path.join(BEST_DIR, "score.txt"), f"{score:.4f}\n")


# ── Modifier ────────────────────────────────────────────────────────
def generate_modification(current_prompt: str, best_score: float, history: str) -> str:
    current_chars = len(current_prompt)
    original_chars = ORIGINAL_SIZE
    compression_pct = round((1 - current_chars / original_chars) * 100, 1)
    
    modify_prompt = f"""You are optimizing a system prompt for an AI assistant. The goal is to make it SHORTER while keeping ALL critical information.

Current prompt ({current_chars} chars, {compression_pct}% compressed from {original_chars} original):
```
{current_prompt}
```

Recent experiment history:
{history if history else "  (first modification)"}

RULES:
1. Preserve ALL: port numbers, URLs, IDs, phone numbers, group IDs, API keys, paths
2. Preserve ALL: personality traits, safety rules, anti-patterns
3. Compress by: removing filler words, using abbreviations, combining sections, using tables
4. Use shorthand (e.g., "→" instead of "leads to", "|" as separator, tables for data)
5. Do NOT remove any data point — only compress the presentation
6. Target: 20-40% smaller than current, same information density

Output ONLY the complete compressed prompt. No explanation, no markdown fences."""

    return llm_call(modify_prompt, role="mutator", max_tokens=4096)


# ── Main Loop ───────────────────────────────────────────────────────
def main():
    global ORIGINAL_SIZE
    
    import argparse
    parser = argparse.ArgumentParser(description="System prompt compressor")
    parser.add_argument("--max", type=int, default=30, help="Max experiments")
    parser.add_argument("--forever", action="store_true", help="Loop until killed")
    parser.add_argument("--hours", type=float, default=0, help="Stop after N hours (0=no limit)")
    parser.add_argument("--resume", action="store_true", help="Resume from last")
    args = parser.parse_args()

    max_exp = args.max if not args.forever and not args.hours else 999999
    deadline = time.time() + (args.hours * 3600) if args.hours > 0 else None
    status["max_experiments"] = max_exp

    log("=" * 60)
    log("  System Prompt Compressor — Free LLM Edition")
    log(f"  Max experiments: {max_exp}")
    log("=" * 60)

    tests = json.load(open(TEST_SET_FILE))
    current_prompt = read_file(TARGET_FILE)
    ORIGINAL_SIZE = len(current_prompt)
    log(f"Original prompt: {ORIGINAL_SIZE} chars, {len(tests)} test cases")

    # ── Baseline ────────────────────────────────────────────────────
    best_score, q_scores = evaluate_prompt(current_prompt, tests)
    update_status(phase="baseline_done", baseline_score=best_score, best_score=best_score)
    log(f"Baseline: {best_score:.4f} (accuracy × compression)")
    log_experiment(0, best_score, 0.0, "baseline", f"Original {ORIGINAL_SIZE} chars")
    save_best(best_score, current_prompt)
    best_prompt = current_prompt

    # Show per-category baseline
    from collections import defaultdict
    cat_scores = defaultdict(list)
    for d in q_scores:
        cat_scores[d["category"]].append(d["score"])
    for cat, scores in sorted(cat_scores.items()):
        avg = sum(scores) / len(scores)
        log(f"  {cat}: {avg:.2f}")

    # ── Experiment Loop ─────────────────────────────────────────────
    consecutive_exhausted = 0
    MAX_CONSECUTIVE_EXHAUSTED = 3  # Stop after 3 consecutive all-models-exhausted
    for exp_n in range(1, max_exp + 1):
        if shutdown_requested:
            break
        if deadline and time.time() > deadline:
            log(f"\nTime limit reached ({args.hours}h). Stopping gracefully.")
            break

        update_status(phase="modifying", experiment=exp_n)
        log(f"\n{'─' * 50}")
        log(f"Experiment #{exp_n} | Best: {best_score:.4f} | Size: {len(best_prompt)} chars")

        # Build history
        history = ""
        if os.path.exists(RESULTS_FILE):
            lines = open(RESULTS_FILE).readlines()
            for line in lines[-5:]:
                try:
                    e = json.loads(line.strip())
                    history += f"  #{e['experiment']}: {e['score']:.4f} ({e['status']}) {e.get('chars', '?')} chars — {e['description']}\n"
                except Exception:
                    pass

        # Generate modification
        new_prompt = generate_modification(read_file(TARGET_FILE), best_score, history)

        # Check if all models exhausted (empty return from llm_call)
        if new_prompt == "":
            consecutive_exhausted += 1
            log(f"  Empty response (exhausted count: {consecutive_exhausted}/{MAX_CONSECUTIVE_EXHAUSTED})")
            if consecutive_exhausted >= MAX_CONSECUTIVE_EXHAUSTED:
                log(f"\nAll free APIs exhausted after {consecutive_exhausted} consecutive failures. Stopping gracefully.")
                break
            time.sleep(30)
            continue
        else:
            consecutive_exhausted = 0  # Reset on successful call

        # Validate
        if not new_prompt or len(new_prompt) < 200:
            log("  Too short or empty, skipping")
            status["skips"] += 1
            log_experiment(exp_n, best_score, best_score, "skip", "Too short/empty")
            time.sleep(2)
            continue

        # Strip markdown fences
        if new_prompt.startswith("```"):
            lines = new_prompt.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            new_prompt = "\n".join(lines).strip()

        # ── Evaluate ────────────────────────────────────────────────
        update_status(phase="evaluating")
        write_file(TARGET_FILE, new_prompt)
        new_score, new_details = evaluate_prompt(new_prompt, tests)
        
        # Also check pure accuracy (without compression bonus)
        accuracy_only = sum(d["score"] for d in new_details) / len(new_details)
        compression_pct = round((1 - len(new_prompt) / ORIGINAL_SIZE) * 100, 1)
        
        update_status(current_score=new_score)
        log(f"  Score: {new_score:.4f} (acc={accuracy_only:.2f}, compressed={compression_pct}%)")

        delta = new_score - best_score

        # ── Keep or Discard ─────────────────────────────────────────
        # Only keep if accuracy stays >= 0.9 (90%) — compression at cost of info loss is useless
        if accuracy_only < 0.85:
            log(f"  REJECTED: accuracy dropped to {accuracy_only:.2f} (< 0.85 threshold)")
            write_file(TARGET_FILE, best_prompt)
            status["regressions"] += 1
            log_experiment(exp_n, new_score, best_score, "discard-accuracy",
                          f"acc={accuracy_only:.2f} < 0.85, {len(new_prompt)} chars")
            update_status(phase="discarded")
        elif new_score > best_score:
            log(f"  ✓ IMPROVEMENT! {best_score:.4f} → {new_score:.4f} (+{delta:.4f}), {len(new_prompt)} chars")
            best_score = new_score
            best_prompt = new_prompt
            save_best(new_score, new_prompt)
            status["improvements"] += 1
            log_experiment(exp_n, new_score, new_score - delta, "keep",
                          f"+{delta:.4f}, {len(new_prompt)} chars, acc={accuracy_only:.2f}")
            update_status(phase="improved", best_score=best_score)
        elif new_score == best_score and len(new_prompt) < len(best_prompt):
            log(f"  ✓ Same score, shorter: {len(best_prompt)} → {len(new_prompt)} chars")
            best_prompt = new_prompt
            save_best(new_score, new_prompt)
            log_experiment(exp_n, new_score, best_score, "keep-shorter",
                          f"Same score, {len(best_prompt)} → {len(new_prompt)} chars")
            update_status(phase="simplified")
        else:
            log(f"  ✗ No improvement: {new_score:.4f} vs {best_score:.4f}")
            write_file(TARGET_FILE, best_prompt)
            status["regressions"] += 1
            log_experiment(exp_n, new_score, best_score, "discard",
                          f"{new_score:.4f}, {len(new_prompt)} chars")
            update_status(phase="discarded")

        gc.collect()
        time.sleep(2)

    # ── Summary ─────────────────────────────────────────────────────
    elapsed = int(time.time() - start_time)
    final_compression = round((1 - len(best_prompt) / ORIGINAL_SIZE) * 100, 1)
    update_status(phase="complete")
    log(f"\n{'=' * 50}")
    log(f"Done! Best: {best_score:.4f}")
    log(f"Original: {ORIGINAL_SIZE} chars → Best: {len(best_prompt)} chars ({final_compression}% compressed)")
    log(f"Improvements: {status['improvements']} | LLM calls: {status['codex_calls']} | Time: {elapsed}s")
    log("=" * 50)


if __name__ == "__main__":
    main()
