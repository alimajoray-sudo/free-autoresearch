---
name: openclaw-sysadmin
description: OpenClaw system administration agent — continuous integrity verification, context optimization, bloat prevention, responsiveness monitoring, and safe config management. Dedicated to keeping the OpenClaw deployment healthy 24/7.
---

# OpenClaw SysAdmin Skill

## Purpose

This skill powers a dedicated **system administration agent** that continuously monitors and optimizes an OpenClaw deployment with 14+ agents. It prevents the recurring issues:

- Context bloat causing agents to slow down and stop responding
- Config corruption from unsafe jq/JSON operations
- Session accumulation without cleanup
- Memory pressure on the host machine (M1 16GB)
- Rate limit storms from concurrent heartbeats
- QMD memory search failures

---

## 1. Health Check Protocol

Run `scripts/health-check.sh` — it outputs a JSON report covering:

| Check | What | Threshold |
|-------|------|-----------|
| Gateway | Running, RPC OK | Must pass |
| Node.js RSS | Gateway memory | Warn >500MB, Critical >800MB |
| System RAM | Free memory | Warn <2GB, Critical <1GB |
| Sessions | Active session count + token usage | Warn if any >80% of contextTokens |
| Agents | All agents responsive | Any stuck = alert |
| Config | JSON validity + schema sanity | Must parse, required keys present |
| QMD | Memory search operational | Must return results |
| Tailscale | Serve proxy active | Must be proxying |
| Logs | Error rate in last hour | Warn >10 errors, Critical >50 |
| Disk | Workspace + log size | Warn >1GB logs |

### Usage
```bash
bash scripts/health-check.sh              # Full report (JSON)
bash scripts/health-check.sh --quick      # Gateway + sessions only
bash scripts/health-check.sh --fix        # Auto-fix what's fixable
```

---

## 2. Context Optimization

### Proactive Context Management

Run `scripts/context-monitor.sh` to check all active sessions:

```bash
bash scripts/context-monitor.sh           # Report all sessions
bash scripts/context-monitor.sh --bloated # Only sessions >70% context
bash scripts/context-monitor.sh --reset   # Reset sessions >90% context
```

### Rules
- Sessions above **80%** context capacity → warn the owner
- Sessions above **90%** → auto-reset (send `/new` via gateway RPC)
- Sessions idle >2h → should auto-reset (verify `session.reset.idleMinutes` is set)
- After any agent does 3+ tool calls in one turn → context is likely bloated

### Context Budget Reference
| Setting | Current | Safe Range |
|---------|---------|------------|
| contextTokens | 40000 | 30000-60000 |
| softTrimRatio | 0.5 | 0.4-0.6 |
| hardClearRatio | 0.3 | 0.2-0.4 |
| keepLastAssistants | 2 | 2-3 |
| pruning TTL | 5m | 3m-10m |

---

## 3. Config Safety (CRITICAL)

### NEVER do this:
```bash
# DANGEROUS — jq full-file rewrite can corrupt when paths are null
cat config.json | jq '.some.null.path = value' > config.json

# DANGEROUS — channels key on agent object is INVALID
# This BREAKS config:
jq '.agents.list[] | select(.id=="x") |= . + {"channels": {...}}'
# Channel routing belongs in top-level bindings[] array:
jq '.bindings += [{"agentId":"x","match":{"channel":"telegram","peer":{"kind":"group","id":"..."}}}]'
```

### ALWAYS do this:
```bash
# 1. Read current value first
cat ~/.openclaw/openclaw.json | jq '.path.to.check'

# 2. If parent is null, build the object properly
# 3. Write to temp file, validate, then move
cat ~/.openclaw/openclaw.json | jq '...' > /tmp/openclaw-candidate.json
node -e "JSON.parse(require('fs').readFileSync('/tmp/openclaw-candidate.json','utf8'))" && \
  cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak && \
  mv /tmp/openclaw-candidate.json ~/.openclaw/openclaw.json

# 4. Restart gateway and verify
openclaw gateway restart
sleep 5
openclaw gateway status
```

### Config Validation Script
```bash
bash scripts/config-validate.sh           # Validate current config
bash scripts/config-validate.sh --backup  # Backup before changes
bash scripts/config-validate.sh --diff    # Show diff from last backup
```

### Required Config Keys (must exist and be valid)
- `agents.defaults.contextTokens` — number, 10000-200000
- `agents.defaults.maxConcurrent` — number, 1-10
- `agents.defaults.compaction` — object with mode, reserveTokensFloor
- `agents.defaults.contextPruning` — object with mode, ttl
- `agents.defaults.heartbeat` — object with every, model
- `agents.list` — array with all agent objects (currently 14)
- `models.providers` — object with provider configs

---

## 4. Responsiveness Monitoring

### Agent Response Time Check
```bash
bash scripts/agent-responsiveness.sh      # Ping all agents, measure response
```

Checks:
- Send a lightweight message to each agent session
- Measure time to first token
- Flag agents taking >30s (normal is 3-10s)
- Detect stuck agents (no response in 60s)

### Common Causes of Slowdown
| Symptom | Cause | Fix |
|---------|-------|-----|
| All agents slow | Context bloat across sessions | Reset bloated sessions |
| All agents slow | Rate limiting (429) | Reduce maxConcurrent |
| All agents slow | Node.js memory pressure | Restart gateway |
| Single agent slow | That agent's session bloated | Reset that session |
| Single agent stuck | Infinite tool loop | Kill session, check HEARTBEAT.md |
| Gradual slowdown over hours | No idle session reset | Set session.reset.idleMinutes |

---

## 5. Bloat Prevention

### Automated Checks (run on heartbeat)
1. **Session token count** — flag any >80% of contextTokens
2. **Gateway RSS** — flag if >500MB
3. **Log file size** — rotate if >100MB
4. **QMD index freshness** — flag if >1h stale
5. **Heartbeat storm detection** — count concurrent API calls in last 5m

### Prevention Config
These settings MUST be maintained:
```json
{
  "agents.defaults.session.reset.idleMinutes": 120,
  "agents.defaults.contextTokens": 40000,
  "agents.defaults.contextPruning.hardClear.enabled": true,
  "agents.defaults.compaction.memoryFlush.enabled": true
}
```

---

## 6. Log Analysis

```bash
bash scripts/log-analyzer.sh              # Analyze last hour
bash scripts/log-analyzer.sh --errors     # Errors only
bash scripts/log-analyzer.sh --rates      # Rate limit events
bash scripts/log-analyzer.sh --slow       # Slow responses (>30s)
```

---

## 7. Heartbeat Schedule for SysAdmin Agent

The sysadmin agent should run its own heartbeat every **30 minutes** during active hours:

```
Heartbeat flow:
1. Run scripts/health-check.sh --quick
2. If any CRITICAL → alert immediately in topic
3. If any WARN → note in topic, auto-fix if possible
4. If all OK → HEARTBEAT_OK (silent)
```

---

## 8. Emergency Procedures

### Gateway Unresponsive
```bash
openclaw gateway restart
sleep 5
openclaw gateway status
# If still dead:
launchctl bootout gui/$(id -u)/ai.openclaw.gateway
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.openclaw.gateway.plist
```

### All Agents Frozen
```bash
# Nuclear option: restart gateway (resets all sessions)
openclaw gateway restart
```

### Config Corrupted
```bash
# Restore from backup
cp ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json
openclaw gateway restart
```

### Memory Search Broken (QMD)
```bash
# Check QMD status
qmd status
# Reindex
qmd index --force
# If still broken, check searchMode
cat ~/.openclaw/openclaw.json | jq '.memory.qmd'
```
