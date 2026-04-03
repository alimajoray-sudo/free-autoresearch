---
name: office-hours
version: 1.0.0
source: https://github.com/garrytan/gstack (adapted for OpenClaw + Paperclip)
description: >
  YC Office Hours — Garry Tan's gstack framework adapted for OpenClaw + Paperclip.
  Two modes: Startup mode (6 forcing questions) and Builder mode (design thinking).
  Produces a design doc, then — if GO — creates the Paperclip project under EMAYGROUP,
  files all initial issues, assigns to CTO/Terminal/CEO agents, and starts execution.
  
  Trigger when Ali says: "I have an idea", "let's think through this", "is this worth
  building", "brainstorm this", "start a new project", "/office-hours", "/gstack".
  
  Proactively invoke this skill when Ali describes a new product/venture concept that
  doesn't already exist as a Paperclip project.
tags: [gstack, office-hours, ideation, startup, paperclip, project-launch, emaygroup]
---

# Office Hours — gstack for OpenClaw

Garry Tan's YC office hours framework. The job is to ensure the problem is understood
before solutions are proposed. This skill produces a design doc first, then turns it
into a running Paperclip project.

**HARD GATE in Phases 1-2:** Do NOT create Paperclip projects or file issues. Your only
output during validation is a design document. Phase 3 is where Paperclip comes in.

---

## Phase 0: Setup

Check if design docs exist for this idea:

```bash
mkdir -p ~/.gstack/sessions ~/.gstack/projects ~/.gstack/analytics
ls -t ~/.openclaw/workspace-main/design-docs/*.md 2>/dev/null | head -10
```

List any prior design docs. If relevant ones exist, mention them to Ali.

---

## Phase 1: Context & Mode

Ask Ali **one question** to determine mode:

> Before we dig in — what's the goal with this?
>
> **A) Startup / venture** — this is or could be a real business (EMAYGROUP ventures)
> **B) Internal tool / intrapreneurship** — solving a real operational problem at ALKE or EMAYGROUP
> **C) Builder** — hackathon, side project, open source, just exploring
>
> And: where is this in terms of validation? Pre-idea (just thinking), has a concept,
> has talked to potential users, or has demand signals already?

**Mode mapping:**
- A, B → Startup mode (Phase 2A) — the six forcing questions
- C → Builder mode (Phase 2B) — design thinking, lighter touch

**Smart routing based on stage:**
- Pre-idea → Q1, Q2, Q3 only
- Has concept → Q1, Q2, Q3, Q4
- Has talked to users → Q2, Q4, Q5
- Has demand signals → Q4, Q5, Q6

---

## Phase 2A: Startup Mode — The Six Forcing Questions

Ask **ONE AT A TIME**. Wait for Ali's answer. Push on each one.

### Operating Principles (internalize these)

**Specificity is the only currency.** Vague answers get pushed. "Enterprises in healthcare"
is not a customer. "Everyone needs this" means you can't find anyone.

**Interest is not demand.** Waitlists, signups, "that's interesting" — none of it counts.
Behavior counts. Money counts. Someone calling you when it's down counts.

**The status quo is the real competitor.** Not another startup — the spreadsheet-and-Slack
workaround the user is already living with.

**Narrow beats wide, early.** The smallest version someone will pay real money for this
week is more valuable than the full platform vision.

### Anti-Sycophancy Rules

Never say during Q1-Q6:
- "That's interesting" — take a position instead
- "There are many ways to think about this" — pick one
- "That could work" — say whether it WILL based on evidence
- "I can see why you'd think that" — if wrong, say why

Always: take a position on every answer. State what evidence would change your mind.

### Q1: Demand Reality

Ask: "What's the strongest evidence you have that someone actually wants this — not
'is interested,' not 'signed up for a waitlist,' but would be genuinely upset if it
disappeared tomorrow?"

Push until you hear: Specific behavior. Someone paying. Someone expanding usage.
Someone building their workflow around it.

Red flags: "People say it's interesting." "We got signups." "VCs are excited."

After first answer — check framing:
1. Are key terms defined? Challenge vague language.
2. Hidden assumptions — name one and ask if it's verified.
3. Real vs. hypothetical — is there actual pain or a thought experiment?

If imprecise: "Let me restate what I think you're actually building: [reframe]. Does
that capture it?" Then proceed with the corrected framing.

### Q2: Status Quo

Ask: "What are users doing right now to solve this — even badly? What does that
workaround cost them?"

Push until you hear: A specific workflow. Hours spent. Dollars wasted. Tools duct-taped
together. People hired to do it manually.

Red flag: "Nothing — there's no solution." If truly nothing exists, the problem probably
isn't painful enough.

### Q3: Desperate Specificity

Ask: "Name the actual human who needs this most. Their title, what gets them promoted,
what gets them fired, what keeps them up at night."

Push until you hear: A name. A role. A specific consequence they face. Something heard
directly from that person.

Red flag: Category-level answers. "Healthcare enterprises." "SMBs." You can't email
a category.

### Q4: Narrowest Wedge

Ask: "What's the smallest possible version of this that someone would pay real money
for — this week, not after the platform is built?"

Push until you hear: One feature. One workflow. Something shippable in days, not months,
that someone would pay for.

Red flag: "We need to build the full platform first." That's attachment to architecture
over value.

Bonus push: "What if the user didn't have to do anything at all to get value? No login,
no integration, no setup — what would that look like?"

### Q5: Observation & Surprise

Ask: "Have you sat down and watched someone use this without helping them? What did
they do that surprised you?"

Push until you hear: A specific surprise. Something the user did that contradicted
assumptions.

Red flag: "We sent a survey." "Nothing surprising." Surveys lie. "As expected" means
filtered through assumptions.

The gold: Users doing something the product wasn't designed for.

### Q6: Future-Fit

Ask: "If the world looks different in 3 years — and it will — does this product become
more essential or less? Why specifically?"

Push until you hear: A specific claim about how their users' world changes and why
that makes the product more valuable. Not "AI keeps improving so we improve" — that's
a rising tide argument every competitor can make.

---

## Phase 2B: Builder Mode — Design Thinking

Lighter touch. Be an enthusiastic collaborator, not an interrogator.

1. **Understand the idea** — what is it, what does it do, who's it for?
2. **Explore the design space** — what are 3 different approaches? What are the tradeoffs?
3. **Search before building** — is there existing art? Layer 1 (standard), Layer 2 (current
   best practices), Layer 3 (first principles that contradict conventional wisdom)?
4. **Scope the v1** — what's the smallest thing that's interesting/useful/fun?
5. **Capture it in a design doc** — save to workspace for future reference

---

## Phase 2: Validation Summary

After questions, produce this summary and show it to Ali:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IDEA: [name]
VERDICT: 🟢 GO / 🟡 PIVOT / 🔴 STOP
CONFIDENCE: [1-10]
KEY RISK: [the one thing that could kill this]
MOAT: [defensible advantage]
BEACHHEAD: [specific first target user]
WEDGE: [smallest payable v1]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**STOP** → Do not create Paperclip project. Tell Ali clearly why.
**PIVOT** → Discuss the pivot. Get Ali's reaction. If pivot is GO, continue.
**GO** → Proceed to Phase 3.

---

## Phase 3: Design Document

Generate the design doc. Save it.

### Document structure

```markdown
# [PROJECT NAME] — Design Doc

> Generated: [date] | gstack office-hours v1.0 | Status: APPROVED

## One-liner
[What it does in 1 sentence: who it's for, what it does, why it's different]

## Problem
[2-3 sentences. Specific pain, specific user. No vague language.]

## Solution
[Core value prop. What we build in v1.]

## Target User
[Persona. Name a specific person if possible.]

## Revenue Model
[How money comes in. Even rough numbers.]

## Tech Stack
[Stack + rationale. Match EMAYGROUP defaults: Node/Python, Docker, Postgres/Redis,
Cloudflare tunnel. Prototype → emaygroup.org, Prod → *.com.tr]

## v1 Scope (MVP)
### In
- [ruthlessly small list]
### Out (explicitly deferred)
- [what we're NOT building]

## Success Metrics (30 days)
- [2-3 measurable outcomes]

## Key Risks
1. [risk + mitigation]
2. [risk + mitigation]
3. [risk + mitigation]

## Timeline
- Phase 1 (Setup + Arch): [X days]
- Phase 2 (MVP): [X days]
- Phase 3 (Deploy + Test): [X days]

## Validation Evidence
[What was learned in office hours. Demand signals. Status quo. Wedge.]
```

Save to:
```bash
mkdir -p ~/.openclaw/workspace-main/design-docs
SLUG=$(echo "[project-name]" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
DATE=$(date +%Y-%m-%d)
FILE=~/.openclaw/workspace-main/design-docs/${DATE}-${SLUG}-design.md
# Write the design doc to $FILE
echo "Design doc saved to: $FILE"
```

Share with Ali and get explicit approval: "Should I create the Paperclip project
and start filing issues?"

---

## Phase 4: Paperclip Project Creation

**Only proceed after Ali says yes.**

### Paperclip API Config
- Base URL: `http://localhost:3100`
- Company ID: `20a41380-37ae-4798-aa6a-d6b6577a5a05`
- API Key: `pcp_02a4913fb7e64146a9c858361bbe8f4dc3e445e383ad4ad5`
- Issue prefix: `AJA`

### Agent IDs
- **CTO**: `301201bc-b634-4da1-940d-fa3f6ddb342c` — code, architecture, bugs
- **CEO**: `1d96b567-1eaf-4452-a803-fbf3b5821167` — strategy, stakeholder updates
- **Terminal**: fetch via list-agents below — VPS/infra/deploy tasks

### Step 1: Check for existing project

```bash
curl -s http://localhost:3100/api/projects \
  -H "Authorization: Bearer pcp_02a4913fb7e64146a9c858361bbe8f4dc3e445e383ad4ad5" \
  -H "x-company-id: 20a41380-37ae-4798-aa6a-d6b6577a5a05" | \
  python3 -c "
import json,sys
data = json.load(sys.stdin)
projects = data if isinstance(data,list) else data.get('data', data.get('projects',[]))
for p in projects:
    print(p.get('id'), '-', p.get('name'))
"
```

If exists: ask Ali if he wants to continue the existing one or start fresh.

### Step 2: Create project

```bash
curl -s -X POST http://localhost:3100/api/projects \
  -H "Authorization: Bearer pcp_02a4913fb7e64146a9c858361bbe8f4dc3e445e383ad4ad5" \
  -H "x-company-id: 20a41380-37ae-4798-aa6a-d6b6577a5a05" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "[PROJECT NAME]",
    "description": "[one-liner from design doc]"
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('Project ID:', d.get('id') or d.get('data',{}).get('id','ERROR'))"
```

Capture the `projectId`.

### Step 3: Get Terminal agent ID

```bash
curl -s "http://localhost:3100/api/agents?companyId=20a41380-37ae-4798-aa6a-d6b6577a5a05" \
  -H "Authorization: Bearer pcp_02a4913fb7e64146a9c858361bbe8f4dc3e445e383ad4ad5" | \
  python3 -c "
import json,sys
data = json.load(sys.stdin)
agents = data if isinstance(data,list) else data.get('data', data.get('agents',[]))
for a in agents:
    name = a.get('name','').lower()
    if 'terminal' in name or 'vps' in name or 'infra' in name:
        print('Terminal agent:', a.get('id'), '-', a.get('name'))
"
```

### Step 4: File the initial issue set

Create these issues. Use the design doc for descriptions.

**Boil the Lake — file all of them, not just MVP.** The marginal cost is seconds.

#### Issue 1: SETUP (CTO, high priority)
```
Title: [PROJECT] Initialize repo and development environment
Description:
- Create GitHub repo under alimajoray-sudo
- Set up project structure per EMAYGROUP standards
- README with setup instructions, .env.example
- Initial dependencies installed, dev server runs
- Push to main branch

Reference: [design doc path]
```

#### Issue 2: ARCH (CTO, high priority)
```
Title: [PROJECT] Architecture decision: tech stack + data model
Description:
- Finalize tech stack (align with design doc)
- Design database schema
- Define API contracts / endpoints
- Document architecture decisions in /docs/architecture.md
- Get Ali approval before starting MVP build
```

#### Issue 3: MVP (CTO, high priority)
```
Title: [PROJECT] Build MVP: [core feature from v1 scope]
Description: [copy v1 scope "In" list from design doc]
- All items in v1 scope
- Basic error handling
- Works end-to-end for the beachhead user: [beachhead from design doc]
- No auth required for v1 if possible (speed over security at this stage)
```

#### Issue 4: DEPLOY (Terminal agent, medium priority)
```
Title: [PROJECT] Setup deployment pipeline
Description:
- Docker Compose with all services
- Cloudflare tunnel configured
- Prototype domain: [project-slug].emaygroup.org
- LaunchAgent for auto-start on boot
- Test: deploy from scratch on VPS, verify it works

EMAYGROUP deploy policy: prototype → emaygroup.org, prod → *.com.tr
```

#### Issue 5: CEO-BRIEF (CEO, low priority, depends on ARCH)
```
Title: [PROJECT] CEO briefing: project overview and timeline
Description:
Once ARCH issue is resolved by CTO, prepare a 5-bullet project overview for Ali:
- What we're building and why
- Target user and key demand signal
- v1 scope
- Timeline to first user
- First success metric

Format: Telegram message to Ali
```

**For each issue, POST:**
```bash
curl -s -X POST http://localhost:3100/api/issues \
  -H "Authorization: Bearer pcp_02a4913fb7e64146a9c858361bbe8f4dc3e445e383ad4ad5" \
  -H "x-company-id: 20a41380-37ae-4798-aa6a-d6b6577a5a05" \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "[PROJECT_ID]",
    "title": "[TITLE]",
    "description": "[DESCRIPTION]",
    "assignedAgentId": "[AGENT_ID]",
    "priority": "[high|medium|low]",
    "status": "open"
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('Created:', d.get('id') or d.get('data',{}).get('id','ERROR'), '-', d.get('title') or d.get('data',{}).get('title',''))"
```

### Step 5: Final report to Ali

```
✅ [PROJECT NAME] is live in Paperclip

📄 Design doc: ~/.openclaw/workspace-main/design-docs/[date]-[slug]-design.md

📋 5 issues filed:
  • AJA-XXX: SETUP → CTO [high]
  • AJA-XXX: ARCH → CTO [high]
  • AJA-XXX: MVP → CTO [high]
  • AJA-XXX: DEPLOY → Terminal [medium]
  • AJA-XXX: CEO-BRIEF → CEO [low]

🚀 CTO is on it. Next: wait for ARCH decision before MVP starts.
   I'll notify you when ARCH is done and ready for approval.
```

---

## Boil the Lake Principle

From gstack ETHOS:

> AI makes completeness near-free. When the complete implementation costs minutes more
> than the shortcut — do the complete thing. Every time.

Applied here: file all 5 issues, not just MVP. The delta is 2 minutes. Never leave
office hours without something created in Paperclip.

**Compression reference:**
| Task | Human team | Alice+Paperclip |
|------|------------|-----------------|
| Project setup | 2 days | 15 min |
| Issue filing | 1 hour | 2 min |
| Architecture decision | 3 days | 4 hours (CTO) |
| MVP build | 1 week | 30 min-2 hours (CTO) |

---

## Completion Status

End with one of:
- **DONE** — Design doc saved, project created, all 5 issues filed.
- **DONE_WITH_CONCERNS** — Completed but [list concerns].
- **BLOCKED** — Cannot proceed. Reason: [what's blocking].
- **NEEDS_CONTEXT** — Need: [exactly what's missing].

---

## Integration with other skills

After `/office-hours` launches a project:
- Await CTO ARCH issue → ask Ali to review architecture before MVP starts
- Use `delegation-rules` skill for task assignment discipline
- Use `ideas-catcher` for loose follow-up ideas on the project
- Use `company-research` for market validation research if needed
