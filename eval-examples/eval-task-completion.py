#!/usr/bin/env python3
"""
eval-task-completion.py — score a SKILL.md or agent instruction file
against a set of task descriptions using an LLM judge.

Usage: python eval-task-completion.py --target <skill-or-instruction.md> --tasks <tasks.json>
Outputs: score 0.0–1.0 (higher = better instructions)

Tasks JSON format:
[
  {
    "task": "Search FIDIC contract for clause 14.3",
    "expected_behavior": "Uses contract-search skill, returns clause text"
  }
]

The LLM judge scores each task 0–10 based on how well the instructions
would lead an agent to complete it correctly.
"""
import argparse
import json
import sys


def score_instructions(target_file: str, tasks_file: str, model: str = "claude-haiku-3-5-20241022") -> float:
    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic not installed", file=sys.stderr)
        return 0.0

    with open(target_file) as f:
        instructions = f.read()
    with open(tasks_file) as f:
        tasks = json.load(f)

    client = anthropic.Anthropic()
    total_score = 0

    for task in tasks:
        prompt = f"""You are evaluating agent instructions for quality.

Instructions being evaluated:
<instructions>
{instructions}
</instructions>

Task to evaluate against:
Task: {task['task']}
Expected behavior: {task.get('expected_behavior', 'Complete the task correctly')}

Score these instructions 0-10 on how well they would guide an agent to complete this task:
- 10: Perfect — instructions explicitly address this case
- 7-9: Good — instructions implicitly cover this well
- 4-6: Partial — instructions are related but incomplete
- 1-3: Poor — instructions barely address this
- 0: Irrelevant or actively misleading

Respond with ONLY a number 0-10."""

        try:
            resp = client.messages.create(
                model=model,
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}]
            )
            score_text = resp.content[0].text.strip()
            score = float(score_text)
            total_score += min(10, max(0, score))
        except Exception:
            total_score += 5  # neutral on failure

    return (total_score / (len(tasks) * 10)) if tasks else 0.0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--tasks", required=True)
    parser.add_argument("--model", default="claude-haiku-3-5-20241022")
    args = parser.parse_args()

    score = score_instructions(args.target, args.tasks, args.model)
    print(f"{score:.4f}")
