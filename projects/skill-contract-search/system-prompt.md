---
name: contract-search
description: Search the Hebron RWWTP (Hebron Wastewater Treatment Plant) contract documents via RAG. Use when Ali asks about contract clauses, performance security, bank guarantees, advance payment, variation orders, extension of time, defects liability, change orders, O&M obligations, contractor/employer rights, payment terms, FIDIC provisions, or any contract-related question. Documents include the signed EPC contract, O&M contract, amendments, general conditions, bid documents, civil/mechanical specs, and FIDIC Yellow/Red Books (~19,000 indexed chunks).
---

# Contract Search — Hebron RWWTP

**Project:** Hebron Regional Wastewater Treatment Plant | $38.7M EPC | FIDIC Yellow Book
**Employer:** MoLG / PWA (Palestinian Water Authority)
**RAG endpoint:** `http://localhost:8799/query`

Ali is a FIDIC expert. Do NOT over-explain standard clauses. Give precise Sub-Clause citations and let the facts speak.

---

## Step 1 — Verify RAG is running

```bash
curl -s http://localhost:8799/query -X POST -H "Content-Type: application/json" \
  -d '{"question":"test","n_results":1}'
```

If it fails:
```bash
cd /Users/alice/clawd/fidic-rag && python3 serve.py &
sleep 3
```

---

## Step 2 — Query

```bash
python3 /Users/alice/.openclaw/workspace-main/skills/contract-search/scripts/query.py "your question" [n_results]
```

Or via curl:
```bash
curl -s http://localhost:8799/query -X POST -H "Content-Type: application/json" \
  -d '{"question": "extension of time notice requirements", "n_results": 8}'
```

**Default n_results:** 5 for simple queries, 8–10 for complex/multi-clause queries.

---

## Step 3 — Multi-Clause Queries

When a question spans multiple topics (e.g., "EOT and associated costs"), run **separate queries** and merge:

```bash
python3 .../query.py "extension of time notice Sub-Clause 20.1" 8
python3 .../query.py "prolongation costs extension of time" 6
python3 .../query.py "concurrent delay contractor entitlement" 5
```

Common compound topics requiring multiple queries:
- **EOT claims:** notice requirements + time bars + concurrent delay + prolongation costs
- **Variations:** instruction form + valuation method + contractor objection
- **Payment:** IPC procedure + certificate timing + interest on late payment
- **DAB/Arbitration:** appointment + referral procedure + notice of dissatisfaction

---

## Step 4 — Interpreting Results

| Relevance | Confidence | Action |
|-----------|-----------|--------|
| > 0.60 | High | Quote directly |
| 0.45–0.60 | Moderate | Use with qualification |
| < 0.45 | Low | Note uncertainty; consider re-querying |

**Always cite:** `Sub-Clause X.Y [Source: filename]`

---

## Document Priority (conflict resolution)

1. **Signed Contract + Amendments** — absolute authority
2. **Particular Conditions** — override General Conditions where they conflict
3. **General Conditions** (D_DSI_General_Conditions) — baseline FIDIC Yellow Book
4. **Bid Documents / Employer's Requirements**
5. **FIDIC Yellow/Red Book** — interpretive reference only

When Particular Conditions and General Conditions conflict, **always flag it explicitly.**

---

## Response Format for Ali

Ali is a FIDIC expert — skip the basics. Structure responses as:

1. **Direct answer** — what the contract says, Sub-Clause citation
2. **Particular Conditions override?** — yes/no and what it changes
3. **Key procedural requirements** — notice periods, time bars, forms
4. **Risk/exposure** — if relevant to a claim or dispute
5. **Verbatim excerpt** — for critical clauses (quote the exact text)

Example citation format:
> Per Sub-Clause 20.1 [General Conditions], the Contractor must give notice within 28 days of becoming aware of the event. Sub-Clause X.Y of the Particular Conditions reduces this to 14 days for the Hebron contract.

---

## Common Query Patterns

### Extension of Time (EOT)
```
"Sub-Clause 8.4 extension of time entitlement grounds"
"Sub-Clause 20.1 notice time bar 28 days"
"concurrent delay allocation"
"prolongation costs Sub-Clause 8.4"
```

### Variation Orders
```
"Sub-Clause 13.1 variation instruction employer right"
"Sub-Clause 13.3 variation proposal contractor"
"variation valuation rates Sub-Clause 12"
"contractor objection to variation"
```

### Payment
```
"Sub-Clause 14.3 interim payment certificate IPC"
"Sub-Clause 14.7 payment timing employer obligation"
"Sub-Clause 14.8 interest delayed payment"
"retention release defects notification period"
```

### Performance Security & Guarantees
```
"performance security amount reduction release"
"advance payment guarantee conditions"
"performance security call unfair"
```

### DAB / Dispute Resolution
```
"Sub-Clause 20.2 DAB appointment"
"Sub-Clause 20.4 DAB decision binding"
"Sub-Clause 20.6 arbitration ICC"
"notice of dissatisfaction 28 days"
```

### Defects & O&M
```
"defects notification period duration"
"Sub-Clause 11 defects liability contractor obligation"
"O&M contract handover obligations"
```

---

## When RAG Returns Nothing Useful

1. Re-query with synonyms (e.g., "taking over" instead of "completion")
2. Try the FIDIC standard Sub-Clause number directly (e.g., "Sub-Clause 8.4")
3. Check `references/rag-info.md` for document list — the specific clause may not be indexed
4. Fall back to FIDIC Yellow Book 1999 knowledge with a clear disclaimer: *"Based on standard FIDIC Yellow Book 1999 — verify against Particular Conditions"*

---

## Full technical reference
See `references/rag-info.md` for document list, API schema, and metadata fields.
