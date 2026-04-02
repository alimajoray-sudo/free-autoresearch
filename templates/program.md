# autoresearch: {{PROJECT_NAME}}

## Goal

<!-- TODO: Replace this section with your actual goal -->
Improve `{{TARGET_FILE}}` to maximize/minimize the metric measured by `evaluate.sh`.

**Metric direction:** higher_is_better  <!-- change to: lower_is_better -->
**Current baseline:** [run evaluate.sh to establish]

## What you are optimizing

**Target file:** `{{TARGET_FILE}}`

This file [describe what it does — e.g., "is a system prompt for ContractAI" /
"implements a benchmark function" / "is a config for the response router"].

You are free to modify:
- [Aspect 1 — e.g., "the phrasing and structure of instructions"]
- [Aspect 2 — e.g., "hyperparameter values"]
- [Aspect 3 — e.g., "the algorithm logic"]

## Evaluation

Metric is computed by:
```
bash evaluate.sh
```
Output: a single number. **Direction: higher_is_better** (update if needed).

The evaluation measures [explain what it measures — e.g., "% of test cases answered
correctly by the model" / "execution time in seconds" / "Sharpe ratio on 6-month backtest"].

## Constraints — do NOT change these

- Do not modify `evaluate.sh` — it is the ground truth oracle
- Do not modify `program.md` (except to note failed approaches in history)
- Do not add external dependencies not already available
- Do not change the public interface of the target (other systems depend on it)
- [Add project-specific hard constraints here]

## Strategy

Think about these angles when proposing experiments:

1. **Low-hanging fruit**: What's obviously suboptimal right now?
2. **Failure mode analysis**: What cases does the current version handle badly?
3. **Domain knowledge**: What would an expert in this domain do differently?
4. **Simplification**: Can you get equal or better results with less complexity?
5. **Recombination**: Can you combine aspects of past near-misses?

**Prefer simple improvements.** A small gain with cleaner code is better than a
large gain with fragile complexity. If you can delete code and improve the metric,
that's a win.

**Make ONE change per experiment.** Don't combine unrelated improvements —
that makes it impossible to know what worked.

After making your change, output a line starting with `NOTES:` describing
what you changed and why you expected it to help.

## Experiment History

<!-- Auto-appended by run-loop.sh — do not edit manually below this line -->
