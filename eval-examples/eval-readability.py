#!/usr/bin/env python3
"""
eval-readability.py — score a text file on Flesch Reading Ease (0–100, higher = more readable)
Usage: python eval-readability.py <file>
Outputs: Flesch score as float (higher_is_better)

Install: pip install textstat
"""
import sys
import os


def score(filepath: str) -> float:
    try:
        import textstat
    except ImportError:
        # Fallback: rough approximation without textstat
        text = open(filepath).read()
        words = len(text.split())
        sentences = text.count('.') + text.count('!') + text.count('?')
        if sentences == 0:
            return 50.0
        avg_words = words / sentences
        # Very rough Flesch approximation
        return max(0, min(100, 206 - 1.3 * avg_words))

    text = open(filepath).read()
    return textstat.flesch_reading_ease(text)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: eval-readability.py <file>", file=sys.stderr)
        sys.exit(1)
    print(f"{score(sys.argv[1]):.2f}")
