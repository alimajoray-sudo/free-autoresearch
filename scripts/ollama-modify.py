#!/usr/bin/env python3
"""
ollama-modify.py — Use local Ollama to modify the target file.
Zero API cost. For use in autoresearch loops.

Usage: python ollama-modify.py <project-dir> <experiment-number> <current-metric>
"""
import json
import os
import sys
import urllib.request

OLLAMA_URL = os.environ.get("OLLAMA_MODIFY_URL", "http://100.74.12.125:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODIFY_MODEL", "qwen3:30b")


def ollama_chat(prompt: str, timeout: int = 180) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": 2000, "num_ctx": 8192},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        result = json.loads(resp.read())
        return result.get("message", {}).get("content", "").strip()


def main():
    if len(sys.argv) < 4:
        print("Usage: ollama-modify.py <project-dir> <exp-number> <current-metric>", file=sys.stderr)
        sys.exit(1)

    project_dir = sys.argv[1]
    exp_n = sys.argv[2]
    current_metric = sys.argv[3]

    program_md = os.path.join(project_dir, "program.md")
    target_file = os.path.join(project_dir, "system-prompt.md")

    with open(program_md) as f:
        program = f.read()
    with open(target_file) as f:
        current_prompt = f.read()

    modify_request = f"""You are running experiment #{exp_n} in an autonomous improvement loop.

INSTRUCTIONS:
{program}

CURRENT TARGET FILE (system-prompt.md):
```
{current_prompt}
```

Current metric (higher_is_better): {current_metric}

YOUR TASK: Output an IMPROVED version of the system prompt. Make ONE targeted change to improve the accuracy score.

RULES:
1. Output ONLY the new prompt text — no explanation, no markdown fences, no commentary
2. Make exactly ONE coherent improvement
3. Keep it under 2000 characters
4. Do NOT remove the ContractAI identity or FIDIC citation instruction
5. Start your output immediately with "You are ContractAI"

OUTPUT THE IMPROVED PROMPT NOW:"""

    response = ollama_chat(modify_request)

    if not response:
        print("ERROR: Empty response from Ollama", file=sys.stderr)
        sys.exit(1)

    # Clean up: remove markdown fences if model wrapped it
    if response.startswith("```"):
        lines = response.split("\n")
        lines = [l for l in lines if not l.startswith("```")]
        response = "\n".join(lines).strip()

    # Write the modified prompt
    with open(target_file, "w") as f:
        f.write(response + "\n")

    print(f"NOTES: Ollama exp#{exp_n} via {OLLAMA_MODEL}")


if __name__ == "__main__":
    main()
