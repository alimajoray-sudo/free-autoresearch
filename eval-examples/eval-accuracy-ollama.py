#!/usr/bin/env python3
"""
eval-accuracy-ollama.py — evaluate a prompt/instruction against a test set using local Ollama.
Zero API cost. Designed for overnight autoresearch loops.

Usage:
  python eval-accuracy-ollama.py --target <prompt-file> --tests <tests.json>
  python eval-accuracy-ollama.py --target <prompt-file> --tests <tests.json> --ollama-url http://100.74.12.125:11434

Outputs: accuracy as float 0.0–1.0 (single number to stdout)

Test JSON format:
[
  {"id": 1, "question": "What is X?", "expected_answer": "Y", "category": "...", "difficulty": "..."},
  ...
]

Two-phase evaluation:
  1. ANSWER phase: Send system prompt + question → get response
  2. JUDGE phase: LLM judge scores the response vs expected (1.0 / 0.5 / 0.0)
"""
import argparse
import json
import sys
import time
import urllib.request
import urllib.error

DEFAULT_OLLAMA_URL = "http://100.74.12.125:11434"  # M5 MacBook Pro via Tailscale
DEFAULT_MODEL = "phi4"          # 14B, no thinking mode, fast + accurate
DEFAULT_JUDGE_MODEL = "phi4"    # Same model judges — perfect scores on contract Q&A
DEFAULT_RAG_URL = "http://localhost:8799/query"  # FIDIC RAG backend
DEFAULT_RAG_CHUNKS = 8


def fetch_rag_context(question: str, rag_url: str = DEFAULT_RAG_URL,
                      n_results: int = DEFAULT_RAG_CHUNKS, timeout: int = 30) -> str:
    """Query the FIDIC RAG backend and return formatted context chunks."""
    payload = json.dumps({"question": question, "n_results": n_results}).encode("utf-8")
    req = urllib.request.Request(
        rag_url, data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            chunks = result.get("chunks", [])
            if not chunks:
                return ""
            context_parts = []
            for i, chunk in enumerate(chunks, 1):
                text = chunk.get("content", chunk.get("text", ""))
                source = chunk.get("metadata", {}).get("source", "unknown")
                if text.strip():
                    context_parts.append(f"[Evidence {i} — {source}]\n{text.strip()}")
            return "\n\n".join(context_parts)
    except Exception as e:
        print(f"  RAG error: {e}", file=sys.stderr)
        return ""


def ollama_chat(url: str, model: str, prompt: str, system: str = "", timeout: int = 120) -> str:
    """Call Ollama /api/chat endpoint. Handles Qwen3 thinking mode correctly."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        # num_predict must be high enough for Qwen3 thinking + answer
        "options": {"temperature": 0.3, "num_ctx": 8192, "num_predict": 1500},
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{url}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            # /api/chat returns content in message.content (separate from thinking)
            return result.get("message", {}).get("content", "").strip()
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        print(f"  Ollama error: {e}", file=sys.stderr)
        return ""


# Backward compat alias
ollama_generate = ollama_chat


def judge_answer(url: str, model: str, question: str, expected: str, actual: str) -> float:
    """LLM judge scores the answer. Returns 1.0, 0.5, or 0.0."""
    judge_prompt = f"""You are a strict evaluator. Score the ACTUAL answer against the EXPECTED answer.

QUESTION: {question}

EXPECTED ANSWER: {expected}

ACTUAL ANSWER: {actual}

Scoring:
- 1.0 = Actual answer is correct and covers the key facts from expected answer
- 0.5 = Partially correct — gets some facts right but misses important details
- 0.0 = Wrong, irrelevant, or completely misses the expected answer

Reply with ONLY a number: 1.0, 0.5, or 0.0
Do not explain. Just the number."""

    response = ollama_chat(url, model, "Reply with ONLY a single number: 1.0, 0.5, or 0.0.\n\n" + judge_prompt, timeout=90)

    # Parse score from response
    for token in response.replace(",", " ").split():
        token = token.strip().rstrip(".")
        try:
            score = float(token)
            if score in (0.0, 0.5, 1.0):
                return score
            if score >= 0.8:
                return 1.0
            if score >= 0.3:
                return 0.5
            return 0.0
        except ValueError:
            continue
    return 0.0


def evaluate(target_file: str, tests_file: str, ollama_url: str,
             model: str, judge_model: str, verbose: bool = False,
             rag_url: str = DEFAULT_RAG_URL, rag_chunks: int = DEFAULT_RAG_CHUNKS) -> float:
    with open(target_file) as f:
        system_prompt = f.read()
    with open(tests_file) as f:
        tests = json.load(f)

    total_score = 0.0
    total = len(tests)

    for i, test in enumerate(tests):
        question = test.get("question", test.get("input", ""))
        expected = test.get("expected_answer", test.get("expected", ""))
        test_id = test.get("id", i + 1)
        category = test.get("category", "unknown")

        if verbose:
            print(f"  [{test_id}/{total}] {category}: {question[:60]}...", file=sys.stderr)

        t0 = time.time()

        # Phase 0: Fetch RAG context (contract document chunks)
        rag_context = ""
        if rag_url:
            rag_context = fetch_rag_context(question, rag_url=rag_url, n_results=rag_chunks)

        # Phase 1: Generate answer (system prompt + RAG context + question)
        user_prompt = question
        if rag_context:
            user_prompt = f"EVIDENCE:\n{rag_context}\n\nQUESTION: {question}"

        actual = ollama_generate(ollama_url, model, user_prompt, system=system_prompt)
        if not actual:
            if verbose:
                print(f"    → EMPTY response, score=0.0", file=sys.stderr)
            continue

        # Phase 2: Judge
        score = judge_answer(ollama_url, judge_model, question, expected, actual)
        total_score += score
        elapsed = time.time() - t0

        if verbose:
            print(f"    → score={score} ({elapsed:.1f}s)", file=sys.stderr)

    accuracy = total_score / total if total > 0 else 0.0
    if verbose:
        print(f"\n  Total: {total_score}/{total} = {accuracy:.4f}", file=sys.stderr)

    return accuracy


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate prompt accuracy via Ollama (zero API cost)")
    parser.add_argument("--target", required=True, help="System prompt file to evaluate")
    parser.add_argument("--tests", required=True, help="Test set JSON file")
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL, help=f"Ollama API URL (default: {DEFAULT_OLLAMA_URL})")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model for answering (default: {DEFAULT_MODEL})")
    parser.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL, help=f"Model for judging (default: {DEFAULT_JUDGE_MODEL})")
    parser.add_argument("--rag-url", default=DEFAULT_RAG_URL, help=f"RAG endpoint (default: {DEFAULT_RAG_URL}, use 'none' to disable)")
    parser.add_argument("--rag-chunks", type=int, default=DEFAULT_RAG_CHUNKS, help=f"Number of RAG chunks (default: {DEFAULT_RAG_CHUNKS})")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print per-question details to stderr")
    args = parser.parse_args()

    rag = args.rag_url if args.rag_url != "none" else ""

    score = evaluate(
        args.target, args.tests,
        ollama_url=args.ollama_url,
        model=args.model,
        judge_model=args.judge_model,
        verbose=args.verbose,
        rag_url=rag,
        rag_chunks=args.rag_chunks,
    )
    # Output ONLY the number (autoresearch loop reads this)
    print(f"{score:.4f}")
