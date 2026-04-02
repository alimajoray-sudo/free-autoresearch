# System Prompt Compression

## Goal
Compress the combined system prompt (SOUL.md + AGENTS.md + USER.md + TOOLS.md) to use fewer characters while preserving ALL critical information that the AI assistant needs.

## Metric
Score = keyword_match_accuracy × (original_chars / current_chars)

Higher is better. Perfect compression with perfect accuracy = best score.

## Constraints
- ALL IDs, ports, URLs, phone numbers, group IDs must be preserved exactly
- Personality directives must be preserved (concise, no sycophancy, etc.)
- Safety rules (config lock, gateway rules) must be preserved
- Ali's personal details must be preserved
- Can restructure, abbreviate prose, use tables, use shorthand
- Cannot remove any factual data point

## Strategy
- Replace verbose sentences with compact bullet points
- Use abbreviations (e.g., "HB" for Hebron, "JER" for Jerusalem)
- Combine redundant sections
- Use tables for reference data
- Remove filler words and redundant instructions
- Keep technical precision (exact ports, IDs, paths)
