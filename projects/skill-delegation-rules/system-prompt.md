# Delegation Rules — LOCKED 🔒

**This skill is MANDATORY for all agents. Read before ANY task execution.**

## Core Principle
Opus = brain. Sub-agents = hands. Codex/Claude Code = coders.
**Never do work yourself that a cheaper agent can do.**

---

## Cost Hierarchy (subscription-first)

| Resource | Cost | Use For |
|----------|------|---------|
| **Claude Code CLI** (ACP) | Free (claude.ai sub) | All coding tasks (DEFAULT) |
| **Codex CLI** (ACP) | Free (Plus sub) | Coding fallback (~12/day quota) |
| **Gemini Flash** | Free (Google tier) | Heartbeats only |
| **Haiku 4.5** | Cheap (Anthropic sub) | Sub-agent research, analysis, monitoring |
| **Sonnet 4.6** | Mid (Anthropic sub) | Domain agents (ventures, youtube, finance) |
| **Opus 4.6** | Expensive (Anthropic sub) | Planning, brainstorming, user-facing replies ONLY |

**All models use subscriptions (Anthropic Max, OpenAI Plus, claude.ai). No direct API costs.**

---

## What Opus Does (and ONLY does)

✅ Interpret user requests
✅ Plan and decompose tasks
✅ Write clear task prompts for sub-agents
✅ Brainstorm and strategize
✅ Review and verify sub-agent results
✅ Deliver final answers to user
✅ Inline edits (≤ 10 lines, 1-2 files max)
✅ Quick web lookups (1-2 searches + summarize)
✅ File reads for context (≤ 3 files)

❌ Never: extended tool loops (>7 calls for one task)
❌ Never: multi-file code builds (>2 files)
❌ Never: code writing beyond trivial fixes
❌ Never: web scraping or bulk data gathering
❌ Never: long analysis that could be delegated

---

## Coding Delegation

### Rule 1: Try exec before spawning ACP

Sub-agents (and Opus for trivial fixes) MUST use `exec` tool before reaching for ACP:

| Task type | Use |
|-----------|-----|
| Single file write/edit (≤ 10 lines) | `exec` (edit/write tool directly) |
| Run a script, check output | `exec` |
| Read + summarize a file | `read` tool |
| Simple config change (1-2 keys) | `edit` tool directly |
| Multi-file build, new feature, complex refactor | ACP |

**ACP is for builds, not edits.**

---

### Rule 2: Reuse persistent sessions before spawning new ones

Before spawning a new ACP session, check for an existing one:

```python
# 1. Check for existing session
sessions_list(kinds=["acp"])

# 2a. If label exists and is active → reuse
sessions_send(label="coder-<domain>", message="<next task>")

# 2b. If no active session → spawn once, persistent
sessions_spawn(runtime="acp", label="coder-<domain>", mode="session", task="<first task>")
```

**Standard session labels:**

| Domain | Label |
|--------|-------|
| Flip Finder / RE | `coder-flip` |
| Infrastructure / services | `coder-infra` |
| Knowledge RAG / data | `coder-knowledge` |
| General / one-off | `coder-general` |
| Agent/skill builds | `coder-agents` |

Persistent sessions retain workspace context between tasks — no cold starts, no context re-injection every time.

---

### Default: Claude Code CLI (ACP) — PRIMARY

```
sessions_spawn(runtime="acp", label="coder-<domain>", mode="session", task="...")
```

Claude Code is the default ACP agent (unlimited via claude.ai sub). Use for ALL multi-file coding tasks.

**Only spawn ACP when:**
- Multi-file build (>2 files)
- New feature or app from scratch
- Complex refactor across a codebase
- No existing session for this domain

### Fallback: Codex CLI (ACP) — SECONDARY

```
sessions_spawn(runtime="acp", agentId="codex", label="coder-<domain>", mode="session", task="...")
```

**⚠️ Codex has ~12 sessions/day quota (Plus sub). Silent exit code 1 = quota exhausted.**

### ACP Failure Recovery (MANDATORY)

When an ACP session fails (exit code 1, ACP_TURN_FAILED, timeout):

1. **First failure with Claude Code** → Retry once with Claude Code
2. **Second failure with Claude Code** → Switch to Codex: `agentId="codex"`
3. **Codex also fails (quota)** → Fall back to exec-based approach (write files directly with edit/write tools)
4. **NEVER give up and do the work as Opus** — always try all fallback paths first
5. **Log the failure** to `memory/ml/actions.md` for pattern tracking

```python
# Retry pattern:
# Attempt 1: sessions_spawn(runtime="acp", task="...") → Claude Code (default)
# Attempt 2: sessions_spawn(runtime="acp", task="...") → Claude Code (retry)
# Attempt 3: sessions_spawn(runtime="acp", agentId="codex", task="...") → Codex
# Attempt 4: Use exec/edit/write tools directly (last resort)
```

**Best for:**
- When Claude Code is down or auth expired
- Quota-limited (Plus sub, ~12 sessions/day)
- When Codex fails 3+ consecutive times on same task
- Tasks requiring strong contextual understanding across large codebases
- Sensitive config or security-related code changes

### Choosing Between Codex and Claude Code

| Signal | → Use |
|--------|-------|
| Standard coding task | Claude Code (default) |
| "Build X", "Add feature Y" | Claude Code |
| "Refactor this architecture" | Claude Code |
| Complex reasoning about code design | Claude Code |
| Quick script or utility | Claude Code |
| Multi-repo or large codebase nav | Claude Code |
| Claude Code down/auth expired | Codex (fallback) |
| Codex quota exhausted (exit 1) | Back to Claude Code or exec |
| Both fail | exec/edit tools directly |

### Task Prompt Rules for Coding Agents

1. **Be specific** — include file paths, expected behavior, constraints
2. **Max 4 deliverables per task** — mega-tasks timeout with zero output
3. **Include context** — attach relevant files/snippets via `attachments` param
4. **Set working directory** — use `cwd` param when needed
5. **Set timeout** — complex tasks need longer (`runTimeoutSeconds: 600`)

---

## Research & Analysis Delegation

### Use Haiku Sub-agents

```
sessions_spawn(task="...", model="haiku")
```

**Delegate these to Haiku:**
- Web research and summarization
- Email checking and triage
- Log analysis
- Data gathering and formatting
- Document summarization
- API exploration
- Status monitoring
- Comparison reports

### Use Sonnet Sub-agents (when Haiku isn't enough)

```
sessions_spawn(task="...", model="sonnet")
```

**Escalate to Sonnet when:**
- Task requires nuanced judgment
- Multi-step reasoning needed
- Output quality matters (user-facing reports)
- Haiku produced inadequate results

---

## ACP Configuration (Current)

```json
{
  "acp": {
    "enabled": true,
    "dispatch": { "enabled": true },
    "backend": "acpx",
    "defaultAgent": "claude",
    "allowedAgents": ["claude", "codex", "gemini"],
    "maxConcurrentSessions": 8
  }
}
```

**Plugin:** `acpx` (stock extension, permissionMode: approve-all)
**Codex auth:** OAuth via ChatGPT Plus subscription
**Claude Code auth:** claude.ai subscription

### ACP Troubleshooting

| Problem | Fix |
|---------|-----|
| "ACP runtime backend is not configured" | `openclaw plugins list` → check acpx loaded. If missing: reinstall OpenClaw |
| Codex auth expired | Run `codex login` on host Mac |
| Claude Code auth expired | Run `claude login` on host Mac |
| Task timeout | Reduce to ≤4 deliverables, increase `runTimeoutSeconds` |
| Permission denied | Check `permissionMode: approve-all` in acpx config |

---

## QA/QC Gate — General Agent (LOCKED)

The **General agent** (GPT-5.3 Codex) serves as the independent QA/QC reviewer for ALL builds and deliverables. Different model family = independent perspective = catches blind spots.

### What Gets Reviewed
- **Code builds** — after Claude Code/Codex completes implementation
- **Plans & architectures** — before execution begins
- **Schedules & timelines** — sanity check estimates and dependencies
- **Reports & deliverables** — before sending to Ali
- **Config changes** — before applying to production

### How to Route QA

```
sessions_send(label="general", message="QA REVIEW REQUEST:\n\n[context]\n\n---\nReview for: [correctness|completeness|quality|feasibility]\nFiles: [paths or inline]\nOriginal task: [what was asked]\n\nReturn: PASS/FAIL + specific issues found")
```

Or via task orchestrator step type `qa`:
```json
{"id": "05-qa", "name": "QA Review", "type": "qa", "depends_on": ["04-implement"]}
```

### QA Review Standards
General should check for:
1. **Correctness** — does it do what was asked?
2. **Completeness** — anything missing?
3. **Edge cases** — error handling, empty states, boundary conditions
4. **Security** — no exposed secrets, safe patterns
5. **Feasibility** (plans/schedules) — realistic timelines, dependency gaps

### When to Skip QA
- Trivial fixes (< 5 lines, obvious correctness)
- Urgent hotfixes (ship first, review after)
- Internal tooling only you use
- Ali explicitly says "skip review"

### Flow
```
Build (Claude Code) → QA (General/GPT-5.3) → Deliver to Ali
Plan (Opus) → QA (General/GPT-5.3) → Execute
```

---

## Decision Tree

```
Task arrives
    │
    ├─ Question / brainstorm / plan? → Opus answers directly
    │
    ├─ Coding task?
    │   ├─ ≤10 lines, 1-2 files? → exec/edit directly (no ACP)
    │   ├─ Single script or simple fix? → exec directly (no ACP)
    │   ├─ Multi-file build / new feature?
    │   │   ├─ Check sessions_list for active coder-<domain> session
    │   │   ├─ Exists + active? → sessions_send(label="coder-<domain>", ...)
    │   │   └─ Not found? → sessions_spawn(runtime="acp", label="coder-<domain>", mode="session")
    │   └─ Claude Code unavailable? → Codex (same persistent session pattern)
    │
    ├─ Research / analysis / data gathering?
    │   ├─ Quick lookup (1-2 searches)? → Opus does it directly
    │   └─ Bulk / multi-source / long? → Haiku sub-agent
    │
    ├─ Quality report / deep analysis? → Sonnet sub-agent
    │
    └─ Multi-step project (>7 tool calls total)?
        → Opus plans → QA plan (General) → execute (ACP persistent) → QA output → delivers
```

---

## Paperclip Delegation (LOCKED — 2026-03-31)

**If it touches the codebase or VPS and there's a capable agent → delegate, don't execute.**

| Task type | ❌ Wrong (Alice doing it herself) | ✅ Right |
|-----------|----------------------------------|---------|
| Fix a bug | exec + edit directly | File Paperclip issue → CTO agent |
| Run VPS command | exec + ssh directly | File Paperclip issue → Terminal agent |
| Batch API/curl operations | Sequential curl loops | One shell script batch or Paperclip task |
| Update CEO coordination files | — | ✅ Alice does this — it's coordination |

**Rule:** Before using `exec` on codebase or VPS tasks — ask: "Is there a Paperclip agent for this?" If yes → file the issue and delegate.

---

## Anti-Patterns (NEVER DO)

1. **Don't loop tools** — If you're making >7 tool calls for one task, delegate it
2. **Don't read large files** — Spawn a sub-agent to extract what you need
3. **Don't spawn ACP for single-file edits** — Use exec/edit tool directly
4. **Don't spawn a new ACP session if one already exists** — Check first, reuse via sessions_send
5. **Don't scrape/bulk research** — Spawn Haiku
6. **Don't ask "want me to..."** — Just delegate and do it
7. **Don't poll sub-agents** — They auto-announce when done
8. **Don't load full config** — Use `jq` queries
9. **Don't exec codebase/VPS tasks** — File Paperclip issue instead (see above)

---

## Model Map (All Agents)

| Agent | Model | Cost Type |
|-------|-------|-----------|
| main | Opus 4.6 | Anthropic Max sub |
| ali-twin | Opus 4.6 | Anthropic Max sub |
| contract-ai | Opus 4.6 | Anthropic Max sub |
| finance | Opus 4.6 | Anthropic Max sub |
| ventures | Sonnet 4.6 | Anthropic Max sub |
| youtube | Sonnet 4.6 | Anthropic Max sub |
| hub | Haiku 4.5 | Anthropic Max sub |
| homeassistant | Haiku 4.5 | Anthropic Max sub |
| email-assistant | Haiku 4.5 | Anthropic Max sub |
| general (QA/QC) | GPT-5.3 Codex | OpenAI Plus sub |
| Heartbeats (all) | Gemini 2.5 Flash | Google free tier |
| Sub-agents | Haiku 4.5 | Anthropic Max sub |
| Coding (ACP) | Claude Code (default) / Codex (fallback) | claude.ai sub / OpenAI Plus |

**Zero direct API costs. Everything runs on subscriptions.**

---

## Reminders

- After spawning a coding agent: set a 5-10min check reminder
- After spawning research agent: auto-announces, no polling needed
- Log delegation to daily memory: `## HH:MM — Delegated: [task] → [agent]`
- If Codex Plus quota exhausted (12+ sessions/day): switch to Claude Code
- Long prompts for coding agents: write to file, pass via attachments

---

---

## Agent Watchdog Integration (LOCKED — 2026-03-19)

**Every `sessions_spawn` MUST register with the watchdog. Every completion MUST update the registry.**

### Spawn Wrapper (MANDATORY)

After every `sessions_spawn`, immediately register the task:

```bash
# After spawning — register the task
TASK_ID=$(bash skills/agent-watchdog/scripts/registry.sh register \
  "<childSessionKey>" \
  "<your_session_key>" \
  "<task_description>" \
  "<delivery_chat_id>" \
  120)  # deadline in minutes (default: 120)
```

Store `TASK_ID` — you'll need it for completion.

### Completion Protocol (MANDATORY for ALL agents)

When a sub-agent completes and announces back:

```bash
# Mark task done with result summary
bash skills/agent-watchdog/scripts/registry.sh update "$TASK_ID" DONE "<result_summary>"
```

When a sub-agent fails:

```bash
bash skills/agent-watchdog/scripts/registry.sh update "$TASK_ID" FAILED "<failure_reason>"
```

### Rules

1. **No unregistered tasks** — if you spawn it, register it
2. **Completion = delivery + registry update** — both required
3. **Sub-agents must `sessions_send` results to requester** — silent completion is a bug
4. **Watchdog runs every 15 min** — stale tasks get escalated automatically
5. **Orphaned tasks with output files** — watchdog will detect and alert

### Escalation Ladder (automated by watchdog)

| Staleness | Action |
|-----------|--------|
| >30 min no ping | Warning logged |
| >1 hr no ping | Nudge sent to agent session |
| >2 hr no ping | Marked ORPHANED, Telegram alert to Hub |
| Deadline breached | Immediate alert regardless of ping age |

*Last updated: 2026-03-19. This skill is LOCKED — do not modify without Ali's explicit approval.*
