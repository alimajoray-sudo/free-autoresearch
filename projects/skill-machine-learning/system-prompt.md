---
name: machine-learning
description: "Machine Learning feedback loop for OpenClaw — in-context learning via Action Logger, Outcome Collector, Pattern Analyzer, and Rule Promoter. Use when: (1) errors or corrections occur, (2) before risky operations (config edits, tunnel changes, deployments), (3) periodic pattern review, (4) promoting confirmed patterns to hard rules."
---

# Machine Learning Skill (Alice's In-Context Learning Loop)

> "We're not fine-tuning model weights. We're giving information to in-context learning combined with automated prompt engineering to make output better." — Matt Ganzak

Four layers. One loop. Gets smarter every session.

---

## Architecture

```
Action Taken
    ↓
[1] ACTION LOGGER      → memory/ml/actions.md
    ↓
[2] OUTCOME COLLECTOR  → update action entry with result
    ↓
[3] PATTERN ANALYZER   → memory/ml/patterns.md  (3+ occurrences = pattern)
    ↓
[4] RULE PROMOTER      → memory/ml/rules.md     (confirmed pattern = hard rule)
    ↑___________ Pre-Action Rule Check ___________↑
```

---

## Layer 1: Action Logger

**When**: After every significant action (infra changes, config edits, API calls, deployments, data operations).

**Append to `memory/ml/actions.md`**:

```markdown
## [ACT-YYYYMMDD-NNN] category

- **Timestamp**: 2026-02-28T14:30:00+02:00
- **Category**: infra | config | coding | communication | data
- **Action**: What was done (1 sentence)
- **Context**: Why + relevant env details
- **Expected**: What should happen
- **Outcome**: ⏳ pending
- **Result**: —
- **Feedback**: —
```

Categories:
- `infra` — tunnels, DNS, servers, ports, LaunchD
- `config` — openclaw.json, skill files, AGENTS.md edits
- `coding` — scripts, sub-agents, deployments
- `communication` — messages, calls, Telegram ops
- `data` — files, databases, memory edits

---

## Layer 2: Outcome Collector

**When**: After result is known (immediate or deferred).

**Update the action entry** — find by ACT ID and fill:

```markdown
- **Outcome**: ✅ success | ❌ failure | ⚠️ partial
- **Result**: What actually happened
- **Feedback**: User said X / Error was Y / Verified by Z
```

If outcome is failure, also note:
- Root cause (what went wrong)
- How it was resolved (or left unresolved)

---

## Layer 3: Pattern Analyzer

**When**: 
- After 5+ new action entries
- When a failure occurs that feels familiar
- On explicit trigger ("review patterns", "what am I getting wrong?")
- Run `scripts/analyze-patterns.py` for automated analysis

**Write to `memory/ml/patterns.md`**:

```markdown
## [PAT-NNN] pattern_name

- **First seen**: date
- **Last seen**: date
- **Occurrences**: N
- **Category**: infra | config | coding | communication | data
- **Pattern**: What keeps happening
- **Trigger**: What causes it
- **Resolution**: What fixes it
- **Confidence**: low (1-2) | medium (3-4) | high (5+)
- **Status**: emerging | confirmed | promoted
```

A pattern is **confirmed** when it has 3+ occurrences with the same root cause.

---

## Layer 4: Rule Promoter

**When**: Pattern reaches `confirmed` status (3+ occurrences).

**Append to `memory/ml/rules.md`**:

```markdown
## [RULE-NNN] rule_name

- **Promoted**: date
- **Category**: infra | config | coding | communication | data
- **Priority**: critical | high | medium | low
- **Rule**: The hard rule in one sentence
- **Why**: What went wrong without it
- **How to verify**: Concrete check to do
- **Evidence**: PAT-NNN, ACT-IDs
```

Also consider promoting to permanent workspace files:
- `TOOLS.md` — tool-specific gotchas
- `AGENTS.md` — workflow rules
- `SOUL.md` — behavioral patterns

---

## Pre-Action Rule Check (MANDATORY)

**Before ANY of these operations**, read `memory/ml/rules.md` first:

- Editing `~/.openclaw/openclaw.json` or any OpenClaw config
- Cloudflare tunnel / DNS / CNAME changes
- Restoring backups or overwriting files
- Changing port mappings or service routing
- Sub-agent tasks that modify shared resources (hub HTML, config files)
- Any operation where a past rule says "check first"

**How to check**:
```bash
cat ~/.openclaw/workspace-main/memory/ml/rules.md
```

Or grep for the relevant category:
```bash
grep -A5 "Category.*: infra" ~/.openclaw/workspace-main/memory/ml/rules.md
```

If a rule applies → follow it before proceeding.

---

## Trigger Keywords

Activate this skill when you see or hear:
- "you got that wrong", "actually", "no that's not right"
- "check what you learned", "review patterns"
- "what rules do we have", "before I change X"
- Any error, failed command, or unexpected output
- "add a rule", "remember this"
- Sub-agent completes and results need verification

---

## Integration with Existing Skills

- **self-improving-agent**: Feeds into `.learnings/` — ML skill reads patterns from there too
- **learning-engine**: Learned rules from `memory/learned-rules/` can be promoted to `memory/ml/rules.md`
- **config-edit skill**: Always check `memory/ml/rules.md` → config category before editing

---

## Quick Commands

```bash
# View current rules
cat memory/ml/rules.md

# Run pattern analysis
python3 skills/machine-learning/scripts/analyze-patterns.py

# Quick status
bash skills/machine-learning/scripts/review.sh

# Count pending outcomes
grep "pending" memory/ml/actions.md | wc -l
```

---

## Weekly Review

Every Monday (or when triggered):
1. Run `scripts/analyze-patterns.py`
2. Promote confirmed patterns to rules
3. Review rules for TOOLS.md / AGENTS.md promotion
4. Archive resolved actions older than 30 days
