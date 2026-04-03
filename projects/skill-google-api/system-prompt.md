---
name: google-api
description: Google APIs (Gmail, Calendar, Drive, Docs, Tasks) via gog CLI. Use for email search, scheduling, file management, document creation, and task tracking.
metadata: {"openclaw":{"emoji":"📧","requires":{"bins":["gog","jq"]}}}
---

# Google API Skill (gog CLI)

Access Google services via the **gog** CLI — native, zero-config support for Gmail, Calendar, Drive, Docs, and Tasks.

**Timezone:** Always use `Asia/Hebron` for all calendar operations unless Ali specifies otherwise.

---

## Quick Setup

Install gog (already installed):
```bash
brew install usame-aleem/tap/gog
# or: npm install -g gogcli
```

Set timezone once:
```bash
gog config set timezone "Asia/Hebron"
```

Authenticate (first time only):
```bash
gog gmail auth --account alimajor.ay@gmail.com
# Follow browser prompt to grant OAuth scope
# Tokens stored securely in system keyring
```

---

## Gmail Search & Read

```bash
# List unread emails
gog gmail list --account alimajor.ay@gmail.com --unread --plain

# Search emails
gog gmail search 'is:unread label:INBOX' --account alimajor.ay@gmail.com --plain

# Advanced search
gog gmail search 'from:pwajordan.org is:unread' --account alimajor.ay@gmail.com

# Read email headers + body
gog gmail read <message_id> --account alimajor.ay@gmail.com --plain

# Count unread
gog gmail search 'is:unread' --account alimajor.ay@gmail.com --json --results-only | jq 'length'
```

**Common search queries:**
- `is:unread label:INBOX` — Unread inbox
- `from:sender@domain.com` — From specific sender
- `subject:keyword` — By subject
- `has:attachment` — With attachments
- `before:2026-03-01 after:2026-02-01` — Date range
- `label:IMPORTANT` — By label

---

## Gmail Send (via email skill)

For composing and sending emails, use the dedicated `email` skill:
```bash
python3 ~/.openclaw/workspace-main/skills/email/scripts/send.py
```

---

## Calendar

**Always pass times in ISO 8601 with Asia/Hebron offset (+03:00).**

```bash
# List upcoming events
gog calendar list --account alimajor.ay@gmail.com --plain

# Today's schedule
gog calendar today --account alimajor.ay@gmail.com --plain

# Create event (10am–11am Hebron time)
gog calendar create \
  --summary "Site Meeting - Hebron WWTP" \
  --start "2026-04-02T10:00:00+03:00" \
  --end "2026-04-02T11:00:00+03:00" \
  --account alimajor.ay@gmail.com

# Create event with description
gog calendar create \
  --summary "KfW Review Call" \
  --start "2026-04-05T14:00:00+03:00" \
  --end "2026-04-05T15:00:00+03:00" \
  --description "Agenda: Q1 progress, disbursement schedule" \
  --account alimajor.ay@gmail.com
```

**Scheduling rules:**
- Working hours: 08:00–18:00 Asia/Hebron (don't schedule outside unless Ali asks)
- Friday afternoon + Saturday = off (Jewish/Muslim overlap — confirm before booking)
- Always check `calendar today` or `calendar list` before creating new events to avoid conflicts

---

## Tasks

Ali has 3 task lists (in Google Tasks):

| List | Use for |
|------|---------|
| **ALKE** | Construction project tasks (Hebron, Cahul, site, contracts) |
| **Ventures** | EMAYGROUP ventures (ContractAI, Flip Finder, YouTube, Trading) |
| **Personal** | Personal tasks, family, finance |

```bash
# List all task lists
gog tasks lists --account alimajor.ay@gmail.com --plain

# List tasks in ALKE list
gog tasks list --tasklist "ALKE" --account alimajor.ay@gmail.com --plain

# Create task
gog tasks create \
  --tasklist "ALKE" \
  --title "Submit EOT claim documentation" \
  --account alimajor.ay@gmail.com

# Complete task
gog tasks complete \
  --tasklist "ALKE" \
  --task <task_id> \
  --account alimajor.ay@gmail.com
```

---

## Drive

```bash
# List files
gog drive list --account alimajor.ay@gmail.com --plain

# Search files by name
gog drive search "Hebron WWTP payment certificate" --account alimajor.ay@gmail.com

# Upload file
gog drive upload /path/to/file.pdf --account alimajor.ay@gmail.com

# Download file
gog drive get <file_id> --account alimajor.ay@gmail.com > ~/Downloads/file.pdf
```

---

## Docs

```bash
# Create new document
gog docs create --title "Monthly Progress Report - March 2026" --account alimajor.ay@gmail.com

# Get document content
gog docs get <doc_id> --account alimajor.ay@gmail.com

# Append content
gog docs append <doc_id> "Text to append" --account alimajor.ay@gmail.com
```

---

## Troubleshooting

**"no TTY available for keyring"**
- This happens in non-interactive shells. Use environment variables:
  ```bash
  export GOG_KEYRING_PASSWORD="your_keyring_password"
  gog gmail list --account alimajor.ay@gmail.com
  ```
  Or store in ~/.openclaw/.env.gog:
  ```bash
  export GOG_KEYRING_PASSWORD="..."
  source ~/.openclaw/.env.gog
  ```

**Token expired?**
- Tokens auto-refresh. If expired, re-auth:
  ```bash
  gog gmail auth --account alimajor.ay@gmail.com
  ```

**OAuth scope missing?**
- Re-authenticate to grant full scopes:
  ```bash
  gog gmail auth --account alimajor.ay@gmail.com
  # Follow browser to grant: Calendar, Drive, Docs, Tasks, Contacts, Sheets
  ```

---

## References

- [gog GitHub](https://github.com/usame-aleem/gog) — CLI source
- [Google API Scopes](https://developers.google.com/identity/protocols/oauth2/scopes) — Full scope list
- [Gmail API](https://developers.google.com/gmail/api) — Search syntax, batch ops
