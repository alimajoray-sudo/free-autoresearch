#!/usr/bin/env python3
"""
eval-accuracy.py — evaluate a prompt/instruction file against a test set.
Usage: python eval-accuracy.py --target <prompt-file> --tests <tests.json>
Outputs: accuracy as float 0.0–1.0

Test JSON format:
[
  {"input": "What is X?", "expected": "Y"},
  ...
]

The prompt file is sent as system prompt, input as user message,
and response is checked against expected (substring match by default).
"""
import argparse
import json
import os
import sys

def evaluate(target_file: str, tests_file: str, model: str = "claude-haiku-3-5") -> float:
    try:
        import anthropic
    except ImportError:
        print("0.0", file=sys.stderr)
        print("ERROR: anthropic package not installed", file=sys.stderr)
        return 0.0

    with open(target_file) as f:
        system_prompt = f.read()
    with open(tests_file) as f:
        tests = json.load(f)

    client = anthropic.Anthropic()
    correct = 0
    total = len(tests)

    for test in tests:
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=256,
                system=system_prompt,
                messages=[{"role": "user", "content": test["input"]}]
            )
            answer = resp.content[0].text.strip()
            if test["expected"].lower() in answer.lower():
                correct += 1
        except Exception:
            pass

    return correct / total if total > 0 else 0.0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--tests", required=True)
    parser.add_argument("--model", default="claude-haiku-3-5-20241022")
    args = parser.parse_args()

    score = evaluate(args.target, args.tests, args.model)
    print(f"{score:.4f}")
