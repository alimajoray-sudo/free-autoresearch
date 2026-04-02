#!/usr/bin/env python3
"""
Benchmark Ollama models for autoresearch tasks.
Tests modifier capability (prompt rewriting) and evaluator capability (judging).

Usage:
  python3 benchmark-models.py --ollama-url http://localhost:11434 --task modifier
  python3 benchmark-models.py --ollama-url http://localhost:11434 --task evaluator
  python3 benchmark-models.py --ollama-url http://localhost:11434 --task both
  python3 benchmark-models.py --ollama-url http://localhost:11434 --models "llama2,qwen3.5:4b"
"""

import argparse
import json
import time
import urllib.request
import sys

DEFAULT_OLLAMA_URL = "http://localhost:11434"

# --- Test prompts ---

MODIFIER_TEST_PROMPT = """You are running an autonomous improvement loop.

CURRENT SYSTEM PROMPT:
```
You are an expert assistant tasked with answering user questions.

Rules:
- Answer using the provided evidence below
- Always cite sources with specific reference numbers or section labels
- Be precise, practical, and actionable
- If the evidence doesn't contain the answer, say so and suggest which sections to check
- Format responses clearly with bullet points and bold for key terms
```

Current accuracy score: 0.4000 (10/25 correct)

YOUR TASK: Output an IMPROVED version of this system prompt. Make ONE targeted change to improve accuracy. The model answering questions gets document chunks as evidence.

Focus areas:
- Better instructions for synthesizing multiple evidence chunks
- Clearer structure for citing specific amounts, dates, percentages
- Instructions to extract exact values from source text

OUTPUT THE IMPROVED PROMPT ONLY (start with "You are"):"""

EVALUATOR_TEST = {
    "question": "What is the key metric mentioned in the document?",
    "expected": "The document specifies a key performance metric of 15%",
    "context": "The reference document states that the key performance metric is 15%, with detailed explanations in section 2.1."
}


def ollama_chat(url, model, prompt, system="", timeout=180):
    """Send a chat request to Ollama and return (content, duration_seconds)."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = json.dumps({
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 1500, "num_ctx": 4096},
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{url}/api/chat", data=payload,
        headers={"Content-Type": "application/json"},
    )

    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            content = result.get("message", {}).get("content", "")
            elapsed = time.time() - t0
            return content, elapsed
    except Exception as e:
        elapsed = time.time() - t0
        return f"ERROR: {e}", elapsed


def pull_model(url, model):
    """Pull a model if not already available."""
    # Check if model exists
    try:
        req = urllib.request.Request(f"{url}/api/tags")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            existing = [m["name"] for m in data.get("models", [])]
            # Normalize names (ollama uses name:tag format)
            for name in existing:
                if model in name or name.startswith(model.split(":")[0]):
                    print(f"  ✓ {model} already available as {name}", file=sys.stderr)
                    return True
    except Exception:
        pass

    # Pull model
    print(f"  ⬇ Pulling {model}...", file=sys.stderr)
    payload = json.dumps({"name": model, "stream": False}).encode("utf-8")
    req = urllib.request.Request(
        f"{url}/api/pull", data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            result = json.loads(resp.read())
            status = result.get("status", "unknown")
            print(f"  ✓ Pull complete: {status}", file=sys.stderr)
            return status == "success"
    except Exception as e:
        print(f"  ✗ Pull failed: {e}", file=sys.stderr)
        return False


def test_modifier(url, model):
    """Test model as a prompt modifier."""
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"MODIFIER TEST: {model}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    content, elapsed = ollama_chat(url, model, MODIFIER_TEST_PROMPT, timeout=300)

    result = {
        "model": model,
        "task": "modifier",
        "time_seconds": round(elapsed, 1),
        "output_length": len(content),
        "has_content": bool(content.strip()),
        "starts_correctly": content.strip().startswith("You are") if content.strip() else False,
        "is_error": content.startswith("ERROR:"),
    }

    if content.startswith("ERROR:"):
        print(f"  ✗ ERROR after {elapsed:.1f}s: {content[:200]}", file=sys.stderr)
    elif not content.strip():
        print(f"  ✗ EMPTY response after {elapsed:.1f}s", file=sys.stderr)
    else:
        lines = content.strip().split("\n")
        print(f"  ✓ {len(content)} chars in {elapsed:.1f}s", file=sys.stderr)
        print(f"  First line: {lines[0][:80]}", file=sys.stderr)
        print(f"  Starts with 'You are': {result['starts_correctly']}", file=sys.stderr)

    return result


def test_evaluator(url, model):
    """Test model as an answer evaluator/judge."""
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"EVALUATOR TEST: {model}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    t = EVALUATOR_TEST
    # Phase 1: Generate answer
    user_prompt = f"EVIDENCE:\n{t['context']}\n\nQUESTION: {t['question']}"
    system = "You are an expert assistant. Answer using the provided evidence. Cite specific references."

    answer, answer_time = ollama_chat(url, model, user_prompt, system=system, timeout=180)

    # Phase 2: Judge answer
    judge_prompt = f"""Compare the ACTUAL answer to the EXPECTED answer.
Score 1.0 if the key facts match, 0.5 if partially correct, 0.0 if wrong.

QUESTION: {t['question']}
EXPECTED: {t['expected']}
ACTUAL: {answer[:500]}

Reply with ONLY a JSON object: {{"score": <number>, "reason": "<brief>"}}"""

    judge_response, judge_time = ollama_chat(url, model, judge_prompt, timeout=120)

    # Parse score
    score = None
    try:
        # Try to find JSON in response
        for line in judge_response.split("\n"):
            line = line.strip()
            if line.startswith("{"):
                parsed = json.loads(line)
                score = parsed.get("score")
                break
        if score is None and "1.0" in judge_response:
            score = 1.0
        elif score is None and "0.5" in judge_response:
            score = 0.5
        elif score is None and "0.0" in judge_response:
            score = 0.0
    except Exception:
        pass

    result = {
        "model": model,
        "task": "evaluator",
        "answer_time": round(answer_time, 1),
        "judge_time": round(judge_time, 1),
        "total_time": round(answer_time + judge_time, 1),
        "answer_length": len(answer),
        "score": score,
        "has_answer": bool(answer.strip()),
        "is_error": answer.startswith("ERROR:"),
    }

    print(f"  Answer: {len(answer)} chars in {answer_time:.1f}s", file=sys.stderr)
    print(f"  Judge: score={score} in {judge_time:.1f}s", file=sys.stderr)
    print(f"  Total: {answer_time + judge_time:.1f}s", file=sys.stderr)

    return result


def main():
    parser = argparse.ArgumentParser(description="Benchmark Ollama models for autoresearch")
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--models", default="llama2,neural-chat",
                        help="Comma-separated list of models to test")
    parser.add_argument("--task", choices=["modifier", "evaluator", "both"], default="modifier",
                        help="Which task to benchmark")
    parser.add_argument("--pull", action="store_true", help="Pull models before testing")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    models = [m.strip() for m in args.models.split(",")]
    results = []

    for model in models:
        if args.pull:
            pull_model(args.ollama_url, model)

        if args.task in ("modifier", "both"):
            r = test_modifier(args.ollama_url, model)
            results.append(r)

        if args.task in ("evaluator", "both"):
            r = test_evaluator(args.ollama_url, model)
            results.append(r)

    # Summary
    print(f"\n{'='*60}", file=sys.stderr)
    print("SUMMARY", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    for r in results:
        model = r["model"]
        task = r["task"]
        if task == "modifier":
            status = "✓" if r["has_content"] and r["starts_correctly"] else "✗"
            print(f"  {status} {model:25s} modifier  {r['time_seconds']:6.1f}s  {r['output_length']:5d} chars  correct_start={r['starts_correctly']}", file=sys.stderr)
        else:
            status = "✓" if r["score"] and r["score"] >= 0.5 else "✗"
            print(f"  {status} {model:25s} evaluator {r['total_time']:6.1f}s  score={r['score']}  answer={r['answer_length']} chars", file=sys.stderr)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        # Print best modifier
        mod_results = [r for r in results if r["task"] == "modifier" and r["has_content"] and not r["is_error"]]
        if mod_results:
            best = min(mod_results, key=lambda r: r["time_seconds"])
            print(f"\n  🏆 Best modifier: {best['model']} ({best['time_seconds']}s)", file=sys.stderr)


if __name__ == "__main__":
    main()
