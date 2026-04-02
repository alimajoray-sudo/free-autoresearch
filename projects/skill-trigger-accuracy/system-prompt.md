# Skill Trigger Descriptions

## advanced-memory-system
description: Advanced OpenClaw memory system setup, diagnostics, and repair for QMD-backed recall across agents and Telegram/WhatsApp. Use when configuring or auditing memory (shared vault paths, QMD scope rules, snippet limits), running or fixing the Dream Cycle cron, ingesting daily logs + noise-gated session transcripts + uploaded imports, repairing session-indexing gaps by mirroring session alerts into memory files, scanning memory for leaked API keys, fixing credentials permissions, forcing QMD reindex, or generating a durable “memory playbook” for future troubleshooting.
---

## ambient-pipeline
description: Ambient YouTube video production pipeline (Flux/KIE image → window masking → Kling animation → ffmpeg compositing + optional music).
---
---

## The 3-Layer Pipeline

## api-bridge
description: Lightweight wrappers for local REST APIs (ContractAI :8800, FIDIC RAG :8799). Use instead of raw curl — saves 200-500 tokens per call and handles errors gracefully.
metadata: {"clawdbot":{"emoji":"🌉","requires":{"bins":["curl","jq"]}}}
---

## autoresearch.disabled
description: >
Autonomous improvement loop for ANY measurable target — prompt optimization,
code performance, config tuning, content readability, trading backtests, agent
instruction quality. Inspired by Karpathy's autoresearch (github.com/karpathy/autoresearch).
Run overnight and wake up to a log of experiments with the best result kept.
Triggers on: "run autoresearch", "optimize this autonomously", "overnight experiment loop",

## claims-optimizer
description: FIDIC Claims Optimizer for Hebron RWWTP. Proactively identifies time extension and claims opportunities from indexed correspondence, contract documents, and regional news. Monitors war/conflict escalation for force majeure and EOT triggers. Delegates sub-agents for deep analysis.
---

## cloudflare
description: Comprehensive Cloudflare API skill for DNS, Tunnels, Zero Trust, Workers, Pages, R2, KV, D1, and more. Supports token creation for granular permissions.
metadata: {"openclaw":{"emoji":"☁️","requires":{"bins":["curl","jq"]}}}
---

## company-research
description: Company intelligence tool. Fetches structured profiles (description, team size, tech stack, socials, key facts) from a company domain or URL using Apify's Company Research Intelligence actor.
metadata: {"clawdbot":{"emoji":"🏢","requires":{"bins":["curl","jq"]}}}
---

## config-edit
description: Safe OpenClaw configuration editing workflow. Use whenever making ANY change to ~/.openclaw/openclaw.json (adding bindings, tokens, memory settings, heartbeats, models, agents). Enforces backup→temp→jq edit→schema validation→atomic move→restart gateway→verify RPC.
---

## contract-search
description: Search the Hebron RWWTP (Hebron Wastewater Treatment Plant) contract documents via RAG. Use when Ali asks about contract clauses, performance security, bank guarantees, advance payment, variation orders, extension of time, defects liability, change orders, O&M obligations, contractor/employer rights, payment terms, FIDIC provisions, or any contract-related question. Documents include the signed EPC contract, O&M contract, amendments, general conditions, bid documents, civil/mechanical specs, and FIDIC Yellow/Red Books (~19,000 indexed chunks).
---
---

## Step 1 — Verify RAG is running

## document-translator
description: High-quality document translation using DeepL API. Preserves formatting for PDF, DOCX, PPTX files.
metadata: {"openclaw":{"emoji":"🌐","requires":{"bins":["curl","jq"]}}}
---

## email-assistant
description: Smart email assistant using Google Gmail API with push notifications. Context-aware analysis, draft responses, and task extraction.
metadata: {"openclaw":{"emoji":"📬","requires":{"bins":["python3"]}}}
---
---

## How It Works

## email
description: Send emails via Gmail SMTP. Use for sending reports, notifications, contact info, or any email communication on behalf of the user.
metadata: {"clawdbot":{"emoji":"📧","requires":{"bins":["python3"],"env":["GMAIL_USER","GMAIL_APP_PASSWORD"]},"primaryEnv":"GMAIL_APP_PASSWORD"}}
---

## exchange-rates
description: Monitor exchange rates (TRY, ILS, MDL, RON vs EUR) with alerts on significant moves. Uses frankfurter.app — free, no API key, ECB data. Run alert.py in cron daily for margin protection.
metadata: {"clawdbot":{"emoji":"💱","requires":{"bins":["bash","python3","curl","jq"]}}}
---

## finance-tracker
description: Personal finance tracker with multi-currency holdings, exchange rate monitoring, gold tracking, and investment analysis. Use for bank balance updates, net worth calculations, financial reports, and investment recommendations.
---

## free-autoresearch
description: >
Launch autonomous improvement loops on any measurable target for $0.
Cycles through free LLM APIs (OpenRouter, NVIDIA NIM, xAI, HuggingFace, DeepSeek).
Use when: asked to "optimize this", "run experiments overnight", "improve X autonomously",
"run autoresearch on", "continuously improve", or any task needing iterative AI-powered improvement.
---

## free-router
description: >
Zero-cost LLM API router. Drop-in Python library that automatically selects
from a pool of free and cheap LLM providers (OpenRouter free, HuggingFace,
xAI Grok, DeepSeek), handles rate limits, falls back across providers, and
enforces a daily budget cap. One import, one call. Use in any skill that
needs LLM calls without burning API quota or money.

## google-api
description: Google APIs (Gmail, Calendar, Drive, Docs, Tasks) via gog CLI. Use for email search, scheduling, file management, document creation, and task tracking.
metadata: {"openclaw":{"emoji":"📧","requires":{"bins":["gog","jq"]}}}
---
---

## Quick Setup

## here-now
description: >
Publish files and folders to the web instantly. Static hosting for HTML sites,
images, PDFs, and any file type. Use when asked to "publish this", "host this",
"deploy this", "share this on the web", "make a website", "put this online",
"upload to the web", "create a webpage", "share a link", "serve this site",
or "generate a URL". Outputs a live, shareable URL at {slug}.here.now.

## homeassistant
description: Control and monitor Home Assistant smart home. Use for lights, switches, climate, covers, scenes, automations, sensors, and any HA entity. Triggers on "turn on/off lights", "set temperature", "open/close blinds", "activate scene", "run automation", "what's the temperature", "show sensors", "HA status", or any smart home control request.
metadata: {"clawdbot":{"emoji":"🏠","requires":{"bins":["curl"],"env":["HA_URL","HA_TOKEN"]},"primaryEnv":"HA_TOKEN"}}
---

## hybrid-rag
description: "Build hybrid RAG systems that combine semantic vector search with exploration-based retrieval. Use when setting up any new RAG system, knowledge base, or document retrieval pipeline. Covers: chunking strategy, embedding model selection, vector store setup, retrieval method (semantic + exploration tools), reranking, ingestion pipeline, and evaluation. Triggers on: 'build a RAG', 'set up knowledge base', 'document retrieval', 'RAG system', 'search pipeline', 'knowledge retrieval', 'index documents', 'vector search setup'."
---

## ideas-catcher
description: Capture, store, and generate business ideas. Tracks Ali's ideas from conversations and Alice's AI-generated ideas from cross-project pattern analysis. Uses Google Sheets for index and Google Drive for detailed docs.
---

## infographic
description: Generate beautiful infographics using Google Nano Banana Pro and send as images. Use when the user asks for an infographic, visual summary, visual comparison, data card, process flow, or any visual/graphical representation of information.
metadata: {"openclaw":{"emoji":"🎨"}}
---

## invoice-tracker
description: Track invoices, payments, milestones, and cash flow for ALKE Construction projects. Multi-currency support (TRY, EUR, USD, ILS, MDL). Use for payment tracking, cash flow forecasting, milestone status, FX impact analysis.
---

## jerusalem-announcements
description: Generate voice announcements for the Jerusalem apartment living room speaker. Supports Zaina's cloned voice (wife) and default voice. Use when Ali wants to announce messages to the living room (e.g., "announce hello to Jerusalem" or "announce with zaina voice"). Handles TTS generation, audio streaming, and playback verification.
---

## knowledge-rag
description: "Query domain-specific knowledge bases via the Knowledge RAG service (port 8820). Use when agents need academic or practical reference knowledge beyond what the model knows — FIDIC clauses, valuation formulas, SRE principles, YouTube algorithm mechanics, HA automation patterns, startup frameworks, code review standards. Each agent has its own collection and should only query that collection."
---

## linkedin-employees
description: Search LinkedIn company employee lists by keyword. Uses the same free linkedin-scraper session as skills/linkedin/. No API costs. Map competitor teams, find key contacts, identify talent.
metadata: {"clawdbot":{"emoji":"👥","requires":{"bins":["python3"],"pip":["linkedin-scraper","playwright"]}}}
---

## machine-learning
description: "Machine Learning feedback loop for OpenClaw — in-context learning via Action Logger, Outcome Collector, Pattern Analyzer, and Rule Promoter. Use when: (1) errors or corrections occur, (2) before risky operations (config edits, tunnel changes, deployments), (3) periodic pattern review, (4) promoting confirmed patterns to hard rules."
---
---

## Architecture

## office-hours
description: >
YC Office Hours — Garry Tan's gstack framework adapted for OpenClaw + Paperclip.
Two modes: Startup mode (6 forcing questions) and Builder mode (design thinking).
Produces a design doc, then — if GO — creates the Paperclip project under EMAYGROUP,
files all initial issues, assigns to CTO/Terminal/CEO agents, and starts execution.

## omc-orchestrator
description: Orchestrate development tasks using oh-my-claudecode (omc) and oh-my-codex (omx) multi-agent CLI tools. Use when asked to spawn dev teams, run code review, architect a solution, debug issues, do autonomous research, create worktrees, or execute any coding task that benefits from multi-agent collaboration. Triggers on phrases like "spin up a team", "fix this code", "review this PR", "design the architecture", "research this topic", "run autoresearch", "launch a hackathon", "use omc", "use omx", "team up on this", or any development task targeting a git repo.
---

## openclaw-sysadmin
description: OpenClaw system administration agent — continuous integrity verification, context optimization, bloat prevention, responsiveness monitoring, and safe config management. Dedicated to keeping the OpenClaw deployment healthy 24/7.
---
---

## 1. Health Check Protocol

## openrouter-usage
description: Track OpenRouter API usage and costs. Shows account balance, per-model breakdown, and generation stats. Use for monitoring Alex's Maximus instance or any OpenRouter-powered setup.
---

## opportunity-scanner
description: Scan markets for opportunities — government tenders, domains, equipment auctions. Configurable scoring and alerts. Use for finding deals, tenders, auctions, market opportunities.
---

## paperclip
description: >
Interact with the Paperclip control plane API to manage the AjanPazarı AI company:
agents, tasks (issues), goals, projects, costs, approvals, and routines.
Use when: checking task status, creating/assigning issues, reading agent activity,
monitoring costs, managing approvals, querying org structure, or delegating work to
Paperclip agents (Kerem, Defne, Elif, Cem, SEO, CTO, Terminal, CEO).

## pattern-analyzer
description: Analyze tool/agent outcome patterns. Detect failure clusters, success streaks, time correlations, and degradation trends. Use for ML pattern analysis, failure debugging, reliability monitoring.
---

## perplexity
description: Real-time web research with citations using Perplexity AI. Use for current events, fact-checking, research questions, or when you need up-to-date information with sources.
---

## project-dashboard
description: View EMAY GROUP venture portfolio — stages, revenue, costs, ROI, time invested. Use for portfolio overview, venture status, revenue attribution, ROI analysis.
---

## rss-monitor
description: RSS feed monitoring. Use to check and track news feeds for construction tenders, FIDIC news, KfW, and tech/AI updates. The `digest` command is designed for cron/heartbeat automation.
metadata: {"clawdbot":{"emoji":"📡","requires":{"bins":["python3"]}}}
---

## self-improving-agent
description: "Captures learnings, errors, and corrections to enable continuous improvement. Use when: (1) A command or operation fails unexpectedly, (2) User corrects Claude ('No, that's wrong...', 'Actually...'), (3) User requests a capability that doesn't exist, (4) An external API or tool fails, (5) Claude realizes its knowledge is outdated or incorrect, (6) A better approach is discovered for a recurring task. Also review learnings before major tasks."
metadata:
---
---

## Generic Setup (Other Agents)

## service-doctor
description: "Health check, diagnose, restart, and monitor EMAY launchd services. Use when: (1) checking if services are running, (2) diagnosing why a service is down, (3) restarting dead services, (4) viewing service logs, (5) checking port allocation, (6) any 'is X running?' or 'why is X down?' question about local services. Covers all com.emaygroup.* launchd agents including ContractAI, FIDIC RAG, FileBrowser, TTS, Gmail IMAP, Cloudflare tunnel, Hub, Flip Finder, and microservices (decision-journal, delegation-pipeline, ideas-incubator, etc)."
---

## stock-analysis
description: Analyze stocks and cryptocurrencies using Yahoo Finance data. Supports portfolio management (create, add, remove assets), crypto analysis (Top 20 by market cap), and periodic performance reports (daily/weekly/monthly/quarterly/yearly). 8 analysis dimensions for stocks, 3 for crypto. Use for stock analysis, portfolio tracking, earnings reactions, or crypto monitoring.
homepage: https://finance.yahoo.com
metadata: {"clawdbot":{"emoji":"📈","requires":{"bins":["uv"],"env":[]},"install":[{"id":"uv-brew","kind":"brew","formula":"uv","bins":["uv"],"label":"Install uv (brew)"}]}}
---

## superdesign-nano
description: >
Build stunning animated web pages combining SuperDesign (UI/UX design agent) with Nano Banana Pro (AI image generation).
Use when Ali asks for beautiful web pages, landing pages, dashboards, or any frontend with cool visuals and effects.
SuperDesign handles layout/design/animations, Nano Banana generates custom hero images, backgrounds, and visual assets.
metadata:
author: alice

## superdesign
description: >
Superdesign is a design agent specialized in frontend UI/UX design. Use this skill before implementing any UI that requires design thinking. Common commands: superdesign create-project --title "X" (setup project), superdesign create-design-draft --project-id <id> --title "Current UI" -p "Faithfully reproduce..." --context-file src/Component.tsx (faithful reproduction), superdesign iterate-design-draft --draft-id <id> -p "dark theme" -p "minimal" --mode branch --context-file src/Component.tsx (design variations), superdesign execute-flow-pages --draft-id <id> --pages '[...]' --context-file src/Component.tsx (extend to more pages), superdesign create-component --project-id <id> --name "NavBar" --html-file /tmp/navbar.html --props '[...]' (extract reusable component), superdesign update-component --component-id <id> --html-file /tmp/navbar.html (update existing component), superdesign list-components --project-id <id> (list existing components). Supports line ranges: --context-file path:startLine:endLine
metadata:
author: superdesign
version: "0.0.2"
---

## tailscale
description: Comprehensive Tailscale VPN management - secure private networking, mesh VPN, peer-to-peer connections, MagicDNS, subnet routing, exit nodes, and SSH.
metadata: {"openclaw":{"emoji":"🔐","requires":{"bins":["tailscale"]}}}
---

## tavily-search
description: Fast web search using Tavily API. Use for quick lookups, current events, and light research when you don't need deep cited analysis. Use Perplexity instead for deep research with citations.
metadata: {"clawdbot":{"emoji":"🔍","requires":{"bins":["curl","jq"]}}}
---

## ted-tenders
description: EU public tender monitoring via TED (Tenders Electronic Daily). Search and monitor water/wastewater/construction tenders by keyword, country, and CPV code. Free API, no key required. Run monitor.py in cron for automated alerts.
metadata: {"clawdbot":{"emoji":"📋","requires":{"bins":["python3"]}}}
---

## tv-player
description: Play videos on TV via Home Assistant. Supports Samsung TV (AirPlay) and Android TV. Manages video streaming server, handles format conversion, and provides playback controls. Use when user wants to play/stream videos on TV, cast to TV, or manage TV video playback.
---

## vapi-caller
description: Make AI phone calls on behalf of the user via Vapi. Use when user asks to call someone, make a phone call, or convey a message to someone by phone.
---
---

## Contacts Directory

## voice-reply
description: >
Send voice replies using TTS. Use whenever the user's last message was an audio/voice message,
or when Ali explicitly asks for a voice reply. Handles language detection, voice selection,
and cloned voice routing automatically.
triggers:
- user sent audio/voice message

## voice-translator
description: Translate voice messages using Whisper (transcribe) + DeepL (translate). Use for Telegram/WhatsApp voice notes translation.
---

## youtube-manager
description: Manage a YouTube channel via YouTube Data API v3. Use for uploading videos, setting metadata/thumbnails, scheduling publishes, updating channel branding (icon, banner), listing uploads, and changing video privacy. Triggers on: upload video, set thumbnail, schedule video, publish at, set channel icon, set channel banner, update branding, list videos, list uploads, set privacy, change visibility, channel info.
---
---

## Subcommands

## youtube-seo-suite
description: Unified YouTube SEO toolkit — keyword research, video optimization, competitor channel tracking, trend finding, and bulk metadata scraping. Consolidates youtube-seo, youtube-competitor-tracker, youtube-trend-finder, and youtube-metadata-scraper into one skill.
metadata: {"clawdbot":{"emoji":"📺","requires":{"bins":["python3","bash","curl","jq"],"pip":["google-api-python-client","google-auth","requests","beautifulsoup4"],"env":["YOUTUBE_API_KEY","APIFY_API_TOKEN"]}}}
---
---

## 1. SEO Optimization

## youtube-summarizer
description: Automatically fetch YouTube video transcripts, generate structured summaries, and send full transcripts to messaging platforms. Detects YouTube URLs and provides metadata, key insights, and downloadable transcripts.
version: 1.0.0
author: abe238
tags: [youtube, transcription, summarization, video, telegram]
---

## yt-tutorial-learner
description: "Extract actionable knowledge and skills from any YouTube tutorial. Works for any topic: AI tools (Kling, Higgsfield, fal.ai, Flux, Suno, RunwayML), RAG systems, memory architectures, context management, LLM engineering, coding frameworks, DevOps, automation (n8n, Home Assistant), trading systems, or any technical tutorial. Use when a user shares a YouTube link and wants to learn from it, extract techniques, settings, workflows, or prompts. Saves structured learnings to memory for future reference."
---

