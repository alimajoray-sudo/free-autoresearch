---
name: yt-tutorial-learner
description: "Extract actionable knowledge and skills from any YouTube tutorial. Works for any topic: AI tools (Kling, Higgsfield, fal.ai, Flux, Suno, RunwayML), RAG systems, memory architectures, context management, LLM engineering, coding frameworks, DevOps, automation (n8n, Home Assistant), trading systems, or any technical tutorial. Use when a user shares a YouTube link and wants to learn from it, extract techniques, settings, workflows, or prompts. Saves structured learnings to memory for future reference."
---

# YT Tutorial Learner

Turn any YouTube tutorial into structured, actionable knowledge — then save it to memory.

## Step 1: Fetch Transcript

Extract video ID from URL (supports youtube.com/watch?v=, youtu.be/, /shorts/).

```bash
cd /root/clawd/mcp-server-youtube-transcript && node --input-type=module -e "
import { getSubtitles } from './dist/youtube-fetcher.js';
const result = await getSubtitles({ videoID: 'VIDEO_ID', lang: 'en' });
console.log(JSON.stringify(result, null, 2));
" > /tmp/yt-tutorial-raw.json 2>&1
```

**macOS path fallback:**
```bash
cd ~/.openclaw/workspace-main && node --input-type=module -e "
import { getSubtitles } from '/root/clawd/mcp-server-youtube-transcript/dist/youtube-fetcher.js';
..." 
```

Parse full text: `result.lines.map(l => l.text).join(' ')`  
Metadata: `result.metadata.title`, `.author`, `.viewCount`, `.publishDate`

**If no transcript:** Try `lang: 'tr'` or `lang: 'ar'` fallback. If still fails, use `web_fetch` on the URL for description/comments, or ask the user to paste key timestamps.

## Step 2: Detect Topic Domain

Scan title + transcript for domain signals. May cover multiple.

| Domain | Signals |
|--------|---------|
| **AI Video** | kling, higgsfield, runway, hailuo, pika, wan, sora, video generation |
| **AI Image** | flux, midjourney, dalle, imagen, stable diffusion, comfyui, automatic1111 |
| **AI Audio/Music** | suno, udio, elevenlabs, bark, whisper, tts |
| **AI Platforms** | fal.ai, kie.ai, replicate, huggingface, together.ai, fireworks |
| **RAG / Knowledge** | rag, retrieval augmented, vector store, embedding, chroma, pinecone, weaviate, pgvector |
| **Memory Systems** | memory, long-term memory, episodic, semantic memory, memgpt, letta |
| **Context Mgmt** | context window, prompt caching, token optimization, context compression |
| **LLM Engineering** | prompt engineering, chain of thought, agents, tool use, function calling, structured output |
| **Agentic AI** | multi-agent, langgraph, crewai, autogen, swarm, orchestration |
| **Automation** | n8n, make.com, zapier, home assistant, node-red |
| **Coding/DevOps** | docker, kubernetes, ci/cd, github actions, fastapi, nextjs |
| **Trading/Finance** | algo trading, backtesting, strategy, indicators, ibkr, binance |
| **Other** | anything not listed above |

## Step 3: Extract Learnings

Read the full transcript and extract structured knowledge. **Be specific** — exact values, not vague descriptions.

**For every domain, extract:**
- Key concepts introduced
- Step-by-step workflow (if shown)
- Exact settings, parameters, or values mentioned
- Prompts, templates, or formulas (copy verbatim)
- Tools/libraries/APIs used with versions
- Gotchas, bugs, or warnings
- Cost, rate limits, or performance data if mentioned
- Links or resources referenced

**Domain-specific focus — see `references/domain-focus.md` for detailed extraction guides per topic.**

## Step 4: Format Output

```
🎓 TUTORIAL LEARNINGS
📹 [Video Title]
📺 [Channel] | 📅 [Date] | 👁️ [Views]
🔧 Topics: [detected domains]

━━━ KEY CONCEPTS ━━━
[2-3 sentence summary of what this tutorial teaches]

━━━ WORKFLOW / STEPS ━━━
(if a process is demonstrated)
1. [Step with specifics]
2. ...

━━━ SETTINGS & PARAMETERS ━━━
[Setting name]: [value] — [what it controls]
...

━━━ PROMPTS / CODE / TEMPLATES ━━━
[Copy verbatim from transcript — the most reusable artifacts]

━━━ TOOLS USED ━━━
• [Tool/library/API] — [version if given] — [purpose]

━━━ GOTCHAS & WARNINGS ━━━
• [anything the tutorial warned about]

━━━ COST / PERFORMANCE ━━━
• [any numbers mentioned]

━━━ KEY TAKEAWAY ━━━
[1-2 sentences: the single most important thing to remember]

━━━ APPLICATION TO OUR PROJECTS ━━━
[How this applies to active projects — be specific: Sürgün pipeline, Cozy Ambience, Contract AI, trading system, etc.]
```

## Step 5: Save to Memory

Save learnings to the workspace `memory/tutorials/` directory:

```
memory/tutorials/YYYY-MM-DD_VIDEO_ID_[topic-slug].md
```

Append a one-liner to `memory/tutorial-index.md`:
```
YYYY-MM-DD | [VIDEO_ID] | [topics] | [Title] | [key takeaway in <15 words]
```

Create both files/dirs if missing.

## Step 6: Surface Action Items

After delivering the output, ask:
> "Want me to apply any of these techniques to a current project?"

If yes, delegate to a coding sub-agent or relevant workspace agent via `sessions_send`.

## Notes

- Keep the **PROMPTS / CODE** section as the highest-value part — this is what gets reused
- If the video is long (>30 min), focus extraction on the most novel/actionable sections
- For non-English tutorials, translate key terms and prompts; keep code/commands as-is
- Cross-reference with existing `memory/tutorials/` to note if this updates or contradicts prior learnings
