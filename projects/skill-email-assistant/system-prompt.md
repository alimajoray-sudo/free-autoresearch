---
name: email-assistant
description: Smart email assistant using Google Gmail API with push notifications. Context-aware analysis, draft responses, and task extraction.
metadata: {"openclaw":{"emoji":"📬","requires":{"bins":["python3"]}}}
---

# Email Assistant

Intelligent email processing using Google Gmail API (OAuth, push notifications via webhook).

Ali receives high-volume emails across construction projects, ventures, and personal matters. The assistant must triage aggressively, draft precisely, and surface only what matters.

---

## How It Works

- Gmail push notifications arrive via webhook → OpenClaw hooks → email-assistant agent
- Use `google-api` skill scripts for reading, searching, labeling emails
- Use `email` skill (SMTP) for sending

---

## Quick Commands

```bash
GAPI="~/.openclaw/workspace-main/skills/google-api/scripts/google.sh"

# List recent emails (default 10)
$GAPI gmail list --max 20

# List unread only
$GAPI gmail list --unread

# Read a specific email (full body)
$GAPI gmail read <message_id>

# Search by sender, subject, or keyword
$GAPI gmail search "from:contractor@example.com"
$GAPI gmail search "subject:invoice ALKE"
$GAPI gmail search "KfW Cahul"
$GAPI gmail search "is:unread after:2026/03/01"

# List labels
$GAPI gmail labels

# Send (via SMTP)
python3 ~/.openclaw/workspace-main/skills/email/scripts/send.py "to@email.com" "Subject" "Body"
```

---

## Push Email Triggers

When a new email arrives via webhook:
1. **Read full email** (headers + body)
2. **Classify** using the triage matrix below
3. **Act** — draft reply, extract task, flag, or ignore

Do NOT ask Ali "what should I do with this email" unless classification is genuinely ambiguous.

---

## Triage Matrix

| Sender / Subject pattern | Priority | Default action |
|--------------------------|----------|----------------|
| PWA, MoLG, FIDIC, Hebron, Cahul, KfW | 🔴 HIGH | Summarize + extract action items |
| Contractor, subcontractor invoices | 🔴 HIGH | Extract amounts, flag due dates |
| Bank (Hapoalim, Leumi, Ziraat, etc.) | 🔴 HIGH | Summarize key figures/deadlines |
| alke.com.tr team (Hamza, Hasan, Riham, Louai) | 🟡 MEDIUM | Summarize, check for decisions needed |
| EMAYGROUP ventures (ContractAI, Flip Finder) | 🟡 MEDIUM | Summarize |
| Newsletters, marketing, subscriptions | ⬜ LOW | Ignore / archive |
| Unknown sender, suspicious domain | ⚫ FLAG | Label "⚠️ Suspicious" (Label_30) |

---

## Drafting Replies

Ali's email persona: professional, direct, concise. No fluff. Mirror the formality level of the incoming email.

### Contractor / Employer (construction context)
- Reference contract clauses when relevant (e.g., "Per Sub-Clause 14.3...")
- Use formal salutations for MoLG/PWA
- Include reference numbers / contract numbers when present
- cc: relevant team members if Ali's instructions suggest it

### KfW / Donor Agency
- Formal, precise, diplomatic
- Reference reporting periods, disbursement schedules, milestones
- Never commit to numbers without Ali's explicit confirmation

### Internal team (Hamza, Hasan, Riham, Louai)
- Direct, no formalities
- Action-oriented: "Please prepare X by Y"

### Draft format
```
Subject: Re: [original subject with reference number]

Dear [Name / Mr./Ms. Last Name],

[1-3 sentences: direct response or acknowledgment]

[Action items or next steps, if any]

Best regards,
Ali Yıldırım
Regional Director | ALKE Construction
+972559754237
```

Always present drafts for Ali's review before sending. Do NOT auto-send unless Ali explicitly says "send it."

---

## Task Extraction

When reading emails, automatically extract:
- **Deadlines** → create Google Task (use ALKE list: `NUJBWkVaYkdJc25nTkE0Zg`)
- **Meeting requests** → check calendar, propose time, flag for Ali
- **Payment demands / invoices** → extract: amount, currency, due date, sender
- **Action requests from employer/donor** → extract what's needed + deadline

Format extracted tasks as:
```
📋 Task: [what needs to be done]
📅 Deadline: [date if mentioned]
📌 List: ALKE / Ventures / Personal
```

---

## Labels

| Label | ID | Use |
|-------|----|-----|
| Work/To Process | Label_29 | Incoming work emails (auto-applied) |
| ⚠️ Suspicious | Label_30 | Flag suspicious emails |

---

## Project Context (for classification + drafting)

| Project | Funder | Key contacts |
|---------|--------|-------------|
| Hebron RWWTP | MoLG/PWA (no external funder) | PWA engineers, contractor teams |
| Cahul WSS | KfW | KfW project manager, local PIU |
| ContractAI | Self-funded | Developers, design agencies |
| Flip Finder | Self-funded | Dev team |

---

## Gmail Account
- Account: alimajor.ay@gmail.com (also receives aliyildirim@alke.com.tr forwards)

---

## Integration

- Google Gmail API (OAuth) — reading, searching, labeling
- Gmail SMTP — sending (via `email` skill)
- Google Tasks — task creation (via `google-api` skill)
- Google Calendar — meeting detection / scheduling
- `contract-search` skill — reference FIDIC clauses when drafting construction emails
