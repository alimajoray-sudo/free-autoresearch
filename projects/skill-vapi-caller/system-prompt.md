---
name: vapi-caller
description: Make AI phone calls on behalf of the user via Vapi. Use when user asks to call someone, make a phone call, or convey a message to someone by phone.
---

# Vapi AI Phone Caller

Make outbound phone calls with an AI agent that speaks, listens, and completes tasks.

---

## Contacts Directory

**Always check `docs/contacts.md` first** when asked to call someone by name.
- "Call Ali" → `+972559754237` (Ali's default)
- "Call Zaina" → `+972584054431`
- Unknown contact → ask for the number, then add to `docs/contacts.md`

---

## Language Selection

| Situation | Language | Flag |
|-----------|----------|------|
| Turkish-sounding name, Turkish company, Turkey number (+90) | Turkish | `--language tr` |
| Israel number (+972), English-speaking contact | English | `--language en` |
| Romania number (+40), Moldovan contact | Romanian | `--language ro` |
| Palestinian/Arabic contacts, Ali says "call in Arabic" | Arabic | `--language ar` |
| Ali explicitly specifies a language | Use that | — |

**Default rule:** If unsure, use English for business calls. Ask Ali only if the call is sensitive or language mismatch could cause problems.

---

## Quick Start

```bash
cd /Users/alice/.openclaw/workspace-main/skills/vapi-caller

# English call
python3 scripts/call.py call "+972501234567" \
  "Tell them the meeting is confirmed for 3pm tomorrow at the Hebron WWTP site" \
  --language en --wait

# Turkish call
python3 scripts/call.py call "+905551234567" \
  "Yarınki toplantıyı sabah 10'a aldık, geleceklerini teyit et" \
  --language tr --wait

# Romanian call
python3 scripts/call.py call "+40721234567" \
  "Spune-i că factura a fost aprobată și plata va fi procesată săptămâna viitoare" \
  --language ro --wait
```

---

## Message Preparation (MANDATORY before calling)

Before passing text to the call script:

1. **Write the objective, not a script.** The AI caller is conversational — give it the goal, key info, and desired outcome. Not a word-for-word transcript.
2. **HUMANIZE.** Phrases must sound like a real person talking. Natural, conversational, contractions. No corporate AI phrasing.
3. **Include fallback instructions** if person doesn't answer or is unavailable.

### Good message format:
```
"Call to confirm that the site inspection is scheduled for Tuesday April 2nd at 10am at the Hebron WWTP. 
Ask if Engineer Khalil will attend. If they ask to reschedule, say Ali will confirm a new time. 
If no answer, leave a voicemail with the same information."
```

### Bad message format (avoid):
```
"Please inform the relevant party that the aforementioned meeting has been confirmed..."
```

---

## CRITICAL RULES

1. **ONE CALL AT A TIME.** Never initiate a new call until the previous one has fully ended. Always use `--wait`.
2. **Wait for user feedback** after a test call before making more calls.
3. **Never spam calls.** If a call fails, diagnose first — don't retry immediately.
4. **Never impersonate Ali** in a way that could create legal commitments. The caller is Alice (Ali's assistant) calling on Ali's behalf. Introduce as: *"Hi, I'm calling on behalf of Ali Yıldırım..."*
5. **Sensitive topics** (legal, financial commitments, disputes) — confirm with Ali before calling. Don't ad-lib on contract disputes.

---

## If No Answer / Voicemail

Default behavior when the line isn't picked up:
- Leave a voicemail with: who's calling (Ali Yıldırım / ALKE Construction), the key message, and a callback number (+972559754237)
- Report back to Ali: "No answer — voicemail left with [summary]"

If voicemail is not possible (line rings out):
- Report back: "No answer, no voicemail option. Retry manually or try again later?"

---

## Call Status & Review

```bash
# List recent calls
python3 scripts/call.py list

# Check specific call status + transcript
python3 scripts/call.py status <call_id>
```

After every call, summarize for Ali:
- ✅ Connected / ❌ No answer / 📨 Voicemail
- What was communicated
- Any response or commitment from the other party
- Any follow-up needed

---

## Voice Configuration (LOCKED — Feb 26, 2026)

| Language | Code | Provider | Voice | Transcriber |
|----------|------|----------|-------|-------------|
| English | `en` | vapi | Emma | Deepgram nova-2 multi |
| Turkish | `tr` | openai | nova | Deepgram nova-2 tr |
| Romanian | `ro` | openai | nova | Deepgram nova-3 ro |
| Arabic | `ar` | vapi | Emma | Deepgram nova-2 multi |
| Hebrew | `he` | vapi | Emma | Deepgram nova-2 multi |

Do NOT change voice config without Ali's approval.

Available Vapi voices (for overrides if Ali asks): Clara, Godfrey, Elliot, Kylie, Rohan, Lily, Savannah, Hana, Neha, Cole, Harry, Paige, Spencer, Nico, Kai, Emma, Sagar, Neil, Naina, Leah, Tara, Jess, Leo, Dan, Mia, Zac, Zoe

---

## Phone Number Format

E.164 format: `+[country code][number]`
- Israel: `+972501234567`
- Turkey: `+905551234567`
- Romania: `+40721234567`
- Palestine: `+970591234567`

---

## Costs

~$0.05–0.15 per minute depending on destination. Prefer short, objective calls. Don't initiate calls for things that can be handled by message.

---

## Configuration

API keys stored in `.secrets/vapi.env`
