---
name: omc-orchestrator
description: Orchestrate development tasks using oh-my-claudecode (omc) and oh-my-codex (omx) multi-agent CLI tools. Use when asked to spawn dev teams, run code review, architect a solution, debug issues, do autonomous research, create worktrees, or execute any coding task that benefits from multi-agent collaboration. Triggers on phrases like "spin up a team", "fix this code", "review this PR", "design the architecture", "research this topic", "run autoresearch", "launch a hackathon", "use omc", "use omx", "team up on this", or any development task targeting a git repo.
---

# OMC/OMX Orchestrator

Dispatch development work to `omc` (Claude Code) and `omx` (Codex CLI) multi-agent teams via tmux.

## Tool Locations
- `omc` → `/opt/homebrew/bin/omc` (oh-my-claudecode v4.9.3)
- `omx` → `/opt/homebrew/bin/omx` (oh-my-codex v0.11.12)

## Decision: omc vs omx

| Use **omc** (Claude) | Use **omx** (Codex) |
|---|---|
| Complex architecture, design, UX | Fast execution, boilerplate, tests |
| Code review (Opus-grade) | Parallel grunt work |
| Security audit | Quick file edits |
| Research, planning | When Claude quota is low |

Default to **omc** unless there's a reason to prefer Codex.

## Core Commands

### 1. Team Mode (primary use case)

Spawn N workers with optional roles on a task:

```bash
# omc — Claude workers
omc team N:claude[:role] "task description"
omc team 2:claude:designer,1:claude:executor "redesign the landing page"

# omx — Codex workers
omx team N:executor "fix all failing tests"
```

**Available roles:** architect, executor, planner, analyst, critic, debugger, verifier, code-reviewer, security-reviewer, test-engineer, designer, writer, scientist

**Role selection guide:**
- Architecture/design decisions → `architect` or `planner`
- Bug fixing → `debugger` + `executor`
- Code quality → `code-reviewer` + `verifier`
- UI/UX work → `designer` + `executor`
- Security → `security-reviewer`
- Research → `scientist` or use `autoresearch`

**Team management:**
```bash
omc team status <team-name>     # Check progress
omc team shutdown <team-name>   # Stop team
```

### 2. Solo Launch

```bash
omc launch          # Interactive Claude Code with HUD
omc --yolo          # Skip all permission prompts
omx                 # Interactive Codex with HUD
omx --yolo          # Codex no-approval mode
```

### 3. Isolated Worktrees

```bash
omc teleport '#42'           # Create worktree for issue/PR #42
omc teleport feature-name    # Create worktree for feature branch
omc teleport list            # List worktrees
omc teleport remove ./path   # Cleanup
```

### 4. Autoresearch

```bash
omc autoresearch --mission "research topic" --eval "check_script.sh"
omx autoresearch --mission "compare frameworks" --eval "eval.sh"
```

### 5. Ralphthon (Autonomous Hackathon)

```bash
omc ralphthon "build feature X from scratch"
omc ralphthon --resume   # Resume existing session
```

### 6. Quick Ask (one-shot, no session)

```bash
omc ask "explain this error: <paste>"
```

### 7. Rate Limit Recovery

```bash
omc wait              # Auto-detect and resume blocked sessions
omc wait --start      # Start auto-resume daemon
```

### 8. Interop Mode

```bash
omc interop    # Split tmux: Claude left, Codex right
```

## Execution Pattern

All commands run in **tmux**. To dispatch from OpenClaw:

```bash
# Navigate to target repo first
cd /path/to/repo

# Launch team in new tmux window
tmux new-window -n "task-name" "omc team 2:claude:executor 'fix the auth bug'"

# Or in detached session
tmux new-session -d -s task-name "cd /path/to/repo && omc team 3:claude 'implement feature'"
```

**Monitoring:**
```bash
omc team status <name>              # Task progress
tmux capture-pane -t <session> -p   # See output
```

## Model Tiers (pre-configured)

| Tier | Model | Agents |
|---|---|---|
| HIGH (Opus) | claude-opus-4-6 | architect, planner, analyst, critic, code-reviewer |
| MEDIUM (Sonnet) | claude-sonnet-4-6 | executor, debugger, verifier, security-reviewer, designer, test-engineer |
| LOW (Haiku) | claude-haiku-4-5 | explore, writer |

## Task-to-Command Mapping

| Task Type | Command |
|---|---|
| Fix bug in repo | `omc team 1:claude:debugger,1:claude:executor "fix: <description>"` |
| Code review | `omc team 1:claude:code-reviewer "review recent changes in <path>"` |
| Design + implement feature | `omc team 1:claude:architect,2:claude:executor "design and build <feature>"` |
| Security audit | `omc team 1:claude:security-reviewer "audit auth flow"` |
| Full test suite | `omc team 2:claude:test-engineer "write comprehensive tests for <module>"` |
| UI redesign | `omc team 1:claude:designer,1:claude:executor "redesign <component>"` |
| Research topic | `omc autoresearch --mission "<topic>" --eval "echo ok"` |
| Prototype sprint | `omc ralphthon "build <thing> from scratch"` |
| Quick exploration | `omc ask "where is <thing> defined?"` |
| Parallel grunt work | `omx team 3:executor "migrate all files to new format"` |

## Integration Notes

- **Paperclip issues → omc team:** When a Paperclip issue needs code work, `cd` to the repo and dispatch via `omc team`
- **AjanPazarı repo:** `/opt/ajanpazari` on VPS — SSH first, then run locally or use omc teleport
- **Local repos:** `~/Projects/<repo>` — cd there before dispatching
- **Results:** Teams commit to branches; review via `git log` or `omc team status`
- **Cost:** Teams use Claude Max subscription, not API credits. Haiku workers are free-tier.
