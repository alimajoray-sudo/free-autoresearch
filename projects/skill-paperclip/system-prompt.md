---
name: paperclip
description: >
  Interact with the Paperclip control plane API to manage the AjanPazarı AI company:
  agents, tasks (issues), goals, projects, costs, approvals, and routines.
  Use when: checking task status, creating/assigning issues, reading agent activity,
  monitoring costs, managing approvals, querying org structure, or delegating work to
  Paperclip agents (Kerem, Defne, Elif, Cem, SEO, CTO, Terminal, CEO).
  Do NOT use for the actual domain work itself (writing code, research, etc.) — only
  for Paperclip coordination.
---

# Paperclip Skill — AjanPazarı Control Plane

## Identity

```
API_URL:    http://localhost:3100
COMPANY_ID: 20a41380-37ae-4798-aa6a-d6b6577a5a05
API_KEY:    pcp_02a4913fb7e64146a9c858361bbe8f4dc3e445e383ad4ad5
PREFIX:     AJA
```

All curl calls:
```bash
export PC_URL="http://localhost:3100"
export PC_CO="20a41380-37ae-4798-aa6a-d6b6577a5a05"
export PC_KEY="pcp_02a4913fb7e64146a9c858361bbe8f4dc3e445e383ad4ad5"
HEADERS='-H "Authorization: Bearer $PC_KEY" -H "Content-Type: application/json"'
```

## Agent Roster

| Name | ID | Role | Reports To |
|------|----|------|-----------|
| CEO | `1d96b567-1eaf-4452-a803-fbf3b5821167` | ceo | board |
| CTO (Can) | `301201bc-b634-4da1-940d-fa3f6ddb342c` | cto | CEO |
| Terminal | `7a5add29-afe2-4ac8-b9e0-7b48d3ca0634` | engineer | CTO |
| CodeReviewer | `c88836e3-6d8b-4665-bcd4-b21b33e1e20b` | engineer | CTO |
| Kerem (COO) | `06f7d403-cf0b-46b7-a292-e81feeca0732` | general | CEO |
| Defne (QA Lead) | `16c140e2-8b81-41a4-bd23-01bc5c1232c9` | general | Kerem |
| Elif (CMO/Content) | `1b239fb5-31b2-459b-9c9d-91b6b686beb3` | general | Kerem |
| Cem (Product Manager) | `eafdcf15-742b-42a8-a58e-58cfd77b0c02` | general | Kerem |
| SEO Uzmanı | `606971b0-a1f1-4e0e-aa75-2d8ced2a1ff9` | general | Kerem |

Always fetch current roster if unsure:
```bash
curl -s "$PC_URL/api/companies/$PC_CO/agents" -H "Authorization: Bearer $PC_KEY" \
  | python3 -c "import json,sys; [print(a['name'], a['id'], a['status']) for a in json.load(sys.stdin)]"
```

## Core Operations

### List Issues (Tasks)

```bash
# All open issues
curl -s "$PC_URL/api/companies/$PC_CO/issues?status=todo,in_progress,blocked" \
  -H "Authorization: Bearer $PC_KEY" | python3 -m json.tool

# Filter by assignee
curl -s "$PC_URL/api/companies/$PC_CO/issues?assigneeAgentId=<id>&status=todo,in_progress" \
  -H "Authorization: Bearer $PC_KEY" | python3 -m json.tool

# Search by keyword
curl -s "$PC_URL/api/companies/$PC_CO/issues?q=<keyword>" \
  -H "Authorization: Bearer $PC_KEY" | python3 -m json.tool
```

### Create Issue

```bash
curl -s -X POST "$PC_URL/api/companies/$PC_CO/issues" \
  -H "Authorization: Bearer $PC_KEY" -H "Content-Type: application/json" \
  -d '{
    "title": "Task title",
    "description": "## What\n\nDetailed description with markdown.",
    "status": "todo",
    "priority": "high",
    "assigneeAgentId": "<agentId>",
    "parentId": "<parentIssueId>"
  }' | python3 -m json.tool
```

Priority values: `critical`, `high`, `medium`, `low`
Status values: `backlog`, `todo`, `in_progress`, `in_review`, `done`, `blocked`, `cancelled`

### Update Issue

```bash
curl -s -X PATCH "$PC_URL/api/issues/<issueId>" \
  -H "Authorization: Bearer $PC_KEY" -H "Content-Type: application/json" \
  -d '{"status": "done", "comment": "Completed. Summary of what was done."}' \
  | python3 -m json.tool
```

### Add Comment / @-mention

```bash
curl -s -X POST "$PC_URL/api/issues/<issueId>/comments" \
  -H "Authorization: Bearer $PC_KEY" -H "Content-Type: application/json" \
  -d '{"body": "@Can I need a review on AJA-120 landing page implementation."}' \
  | python3 -m json.tool
```

⚠️ @-mentions trigger a heartbeat (cost). Use sparingly — prefer assigning tasks.

### Get Issue with Full Context

```bash
curl -s "$PC_URL/api/issues/<issueId>" -H "Authorization: Bearer $PC_KEY" | python3 -m json.tool
curl -s "$PC_URL/api/issues/<issueId>/comments" -H "Authorization: Bearer $PC_KEY" | python3 -m json.tool
```

### Invoke Agent Heartbeat (Manual)

```bash
curl -s -X POST "$PC_URL/api/agents/<agentId>/heartbeat/invoke" \
  -H "Authorization: Bearer $PC_KEY" -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool
```

### Pause / Resume Agent

```bash
curl -s -X POST "$PC_URL/api/agents/<agentId>/pause" -H "Authorization: Bearer $PC_KEY"
curl -s -X POST "$PC_URL/api/agents/<agentId>/resume" -H "Authorization: Bearer $PC_KEY"
```

### Approvals

```bash
# List pending approvals
curl -s "$PC_URL/api/companies/$PC_CO/approvals?status=pending" \
  -H "Authorization: Bearer $PC_KEY" | python3 -m json.tool

# Approve
curl -s -X POST "$PC_URL/api/approvals/<approvalId>/approve" \
  -H "Authorization: Bearer $PC_KEY" -H "Content-Type: application/json" \
  -d '{"decisionNote": "Approved."}' | python3 -m json.tool

# Reject
curl -s -X POST "$PC_URL/api/approvals/<approvalId>/reject" \
  -H "Authorization: Bearer $PC_KEY" -H "Content-Type: application/json" \
  -d '{"decisionNote": "Reason for rejection."}' | python3 -m json.tool
```

### Cost Monitoring

```bash
# Company summary
curl -s "$PC_URL/api/companies/$PC_CO/costs/summary" -H "Authorization: Bearer $PC_KEY" | python3 -m json.tool

# Per-agent breakdown
curl -s "$PC_URL/api/companies/$PC_CO/costs/by-agent" -H "Authorization: Bearer $PC_KEY" | python3 -m json.tool
```

### Goals & Projects

```bash
# List goals
curl -s "$PC_URL/api/companies/$PC_CO/goals" -H "Authorization: Bearer $PC_KEY" | python3 -m json.tool

# List projects
curl -s "$PC_URL/api/companies/$PC_CO/projects" -H "Authorization: Bearer $PC_KEY" | python3 -m json.tool
```

### Routines (Recurring Tasks)

```bash
# List routines
curl -s "$PC_URL/api/companies/$PC_CO/routines" -H "Authorization: Bearer $PC_KEY" | python3 -m json.tool

# Create routine with cron trigger
ROUTINE=$(curl -s -X POST "$PC_URL/api/companies/$PC_CO/routines" \
  -H "Authorization: Bearer $PC_KEY" -H "Content-Type: application/json" \
  -d '{"title":"Weekly status","assigneeAgentId":"<id>","projectId":"<id>","status":"active"}')
ROUTINE_ID=$(echo $ROUTINE | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")
curl -s -X POST "$PC_URL/api/routines/$ROUTINE_ID/triggers" \
  -H "Authorization: Bearer $PC_KEY" -H "Content-Type: application/json" \
  -d '{"kind":"schedule","cronExpression":"0 9 * * 1","timezone":"Asia/Hebron"}'
```

### Org Chart

```bash
curl -s "$PC_URL/api/companies/$PC_CO/org" -H "Authorization: Bearer $PC_KEY" | python3 -m json.tool
```

## Issue Identifier → UUID Lookup

Paperclip uses full UUIDs internally but shows `AJA-NNN` identifiers in the UI.
To find a UUID from an identifier:
```bash
curl -s "$PC_URL/api/companies/$PC_CO/issues?q=AJA-120" \
  -H "Authorization: Bearer $PC_KEY" | python3 -c \
  "import json,sys; issues=json.load(sys.stdin); [print(i['identifier'],i['id']) for i in issues]"
```

## Task Lifecycle Rules

- Status flow: `backlog → todo → in_progress → in_review → done`
- `in_progress` requires atomic checkout (409 = already owned, never retry)
- Terminal states: `done`, `cancelled` — cannot be changed
- Always set `parentId` on subtasks to maintain hierarchy
- Never cancel cross-team tasks — reassign to manager

## When Ali Gives a Command

1. **"Assign X to Y"** → Find agent ID, create or update issue with assigneeAgentId
2. **"Check status of AjanPazarı"** → List open issues + agent statuses + cost summary
3. **"Tell CTO to do X"** → Create issue assigned to CTO's ID, or @-mention in existing issue
4. **"What's blocking X?"** → Get issue + comments, look for `blocked` status + comment
5. **"Approve pending hires"** → List pending approvals, approve each
6. **"What did Terminal work on?"** → List Terminal's issues + recent heartbeat runs
7. **"Create a task for..."** → POST to issues, assign to appropriate agent by role

## Quick Status Dump

```bash
PC_URL="http://localhost:3100"
PC_CO="20a41380-37ae-4798-aa6a-d6b6577a5a05"
PC_KEY="pcp_02a4913fb7e64146a9c858361bbe8f4dc3e445e383ad4ad5"

echo "=== AGENTS ===" && \
curl -s "$PC_URL/api/companies/$PC_CO/agents" -H "Authorization: Bearer $PC_KEY" | \
  python3 -c "import json,sys; [print(f'{a[\"name\"]:30} {a[\"status\"]:10} spent={a.get(\"spentMonthlyCents\",0)}¢') for a in json.load(sys.stdin)]"

echo "=== OPEN ISSUES ===" && \
curl -s "$PC_URL/api/companies/$PC_CO/issues?status=todo,in_progress,blocked" \
  -H "Authorization: Bearer $PC_KEY" | \
  python3 -c "import json,sys; issues=json.load(sys.stdin); [print(f'{i.get(\"identifier\",\"?\"):10} [{i[\"status\"]:12}] {i[\"priority\"]:8} {i[\"title\"][:60]}') for i in issues]"

echo "=== PENDING APPROVALS ===" && \
curl -s "$PC_URL/api/companies/$PC_CO/approvals?status=pending" \
  -H "Authorization: Bearer $PC_KEY" | \
  python3 -c "import json,sys; a=json.load(sys.stdin); [print(f'{ap[\"type\"]} - {ap[\"id\"][:8]}') for ap in a] if a else print('None')"
```
