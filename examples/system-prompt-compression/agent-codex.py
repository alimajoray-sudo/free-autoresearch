#!/usr/bin/env python3
"""
Mutation instructions for system prompt compression.

This file tells the free LLM HOW to improve the system prompt.
The LLM will read this + target.md, then generate a compressed version.
"""

MUTATION_PROGRAM = """
You are optimizing a system prompt for a legal contract analysis AI agent.

### Current State
- Target file: target.md (~3800 chars)
- Test set: test-set.json (10 Q&A pairs, all accuracy ≥85% required)
- Goal: Reduce token count while maintaining task accuracy ≥85%

### What to Preserve
- All core responsibilities (document comprehension, data extraction, legal analysis)
- All quality standards (cite clauses, plain English, accuracy requirements)
- All handling instructions (multi-part analysis, error handling, uncertainty)
- The key examples showing expected response quality

### Compression Strategies (choose 2-3 per mutation)

1. **Consolidate sections:** Merge "Capabilities" and "Output Requirements" - combine related concepts
2. **Remove redundancy:** The prompt repeats "cite specific clauses" multiple times - consolidate
3. **Shorten definitions:** "You are an expert AI assistant specializing in... [long list]" → "You are an expert contract analyst"
4. **Eliminate low-value content:** Revision history section doesn't affect behavior - remove
5. **Tighten examples:** Current examples are verbose - keep the essence, cut filler words
6. **Use abbreviations:** "Section" → "§", "liquidated damages" → "LD" (with first use definition)
7. **Merge instructions:** Error handling + edge cases can be one section
8. **Simplify tone:** Remove "Tone & Communication" section - demonstrate through instructions, don't describe
9. **Condense error handling:** Remove the long explanations of what to do when, just state the rule
10. **Tighten response requirements:** Instead of 5 numbered points, use 2-3 critical rules

### Constraints
- MUST maintain all 10 test cases passing (85% accuracy minimum)
- MUST preserve the actual rules (don't skip clause citations, etc.)
- MUST keep examples showing expected response format
- SHOULD NOT remove the Definitions handling guidance
- SHOULD NOT change the core role statement beyond tightening

### Evaluation Metric
After compression, your output will be tested on test-set.json.
- If accuracy ≥85%: compression succeeds, keep mutation
- If accuracy <85%: compression failed, revert to previous version

### Output Format
Return ONLY the optimized system prompt (target.md format).
Remove this instruction block - just output the prompt itself.

### Example Compression (not the actual target)
Before (verbose):
"You are an expert AI assistant specializing in legal contract analysis, document comprehension, and data extraction. Your primary purpose is to provide accurate, detailed information from contractual documents."

After (terse, same meaning):
"You are an expert contract analyst. Provide accurate, detailed contract information."

Begin your compression now. Output only the optimized prompt.
"""

print(MUTATION_PROGRAM)
