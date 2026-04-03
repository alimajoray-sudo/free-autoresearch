---
name: hybrid-rag
description: "Build hybrid RAG systems that combine semantic vector search with exploration-based retrieval. Use when setting up any new RAG system, knowledge base, or document retrieval pipeline. Covers: chunking strategy, embedding model selection, vector store setup, retrieval method (semantic + exploration tools), reranking, ingestion pipeline, and evaluation. Triggers on: 'build a RAG', 'set up knowledge base', 'document retrieval', 'RAG system', 'search pipeline', 'knowledge retrieval', 'index documents', 'vector search setup'."
---

# Hybrid RAG System Builder

Build RAG systems that combine semantic search with agent-driven exploration — don't rely on vector search alone.

## Core Insight

Semantic search fails on structured/versioned content (contracts, reports, codebases). Let the agent explore the knowledge base like Claude Code explores code: `list`, `tree`, `glob`, `grep`, `read`.

## When to Use Which

| Query Type | Method | Why |
|---|---|---|
| Open-ended ("what does X say about Y?") | Semantic search | Conceptual matching |
| Structured ("show me clause 20.1") | Exploration | Path/hierarchy encodes the answer |
| Versioned ("latest version of X") | Exploration | Folder structure reveals recency |
| Cross-reference ("compare A and B") | Both | Search finds candidates, explore verifies |

## Step 1: Choose Architecture

Read `references/architecture.md` for the full decision framework.

**Quick pick:**
- **Simple Q&A over flat docs** → Semantic-only (skip exploration)
- **Structured/hierarchical docs** (contracts, specs, reports) → Hybrid (semantic + exploration)
- **Codebase/repo navigation** → Exploration-heavy

## Step 2: Ingestion Pipeline

### Chunking
```python
# Default: RecursiveCharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # chars — tune per domain
    chunk_overlap=200,    # overlap for context continuity
    separators=["\n\n", "\n", ". ", " "]
)
chunks = splitter.split_documents(docs)
```

**Domain-specific chunking — read `references/chunking-strategies.md` for:**
- Legal/FIDIC: clause-aware splitting (preserve sub-clause boundaries)
- Code: function/class-level splitting
- Reports: section-header splitting
- Conversations: turn-based splitting

### Embedding
- **Default:** `nomic-embed-text` (local, free, 768d) or `text-embedding-3-small` (OpenAI, cheap)
- **High accuracy:** `text-embedding-3-large` (3072d) or `voyage-3` (best for code)
- **Local-only:** `nomic-embed-text` via Ollama

### Vector Store
- **Quick/local:** ChromaDB or SQLite-vss
- **Production:** Supabase (pgvector), Pinecone, Qdrant
- **Our stack:** Knowledge RAG service at localhost:8820

```bash
# Create collection in our Knowledge RAG
curl -X POST http://localhost:8820/collections \
  -H "Content-Type: application/json" \
  -d '{"name": "my-collection", "description": "..."}'

# Ingest documents
curl -X POST http://localhost:8820/collections/my-collection/ingest \
  -H "Content-Type: application/json" \
  -d '{"documents": [{"text": "...", "metadata": {"source": "file.pdf", "page": 1}}]}'
```

## Step 3: Retrieval Setup

### Semantic Search (always include)
```python
# Basic similarity search
results = vector_store.similarity_search(query, k=5)

# With MMR for diversity (recommended)
results = vector_store.max_marginal_relevance_search(query, k=5, fetch_k=20)
```

### Exploration Tools (add for structured content)

Build these 5 tools and give them to the agent:

| Tool | What it does | SQL/API backing |
|---|---|---|
| `list(path)` | List documents in a folder/section | `SELECT * FROM docs WHERE folder = ?` |
| `tree(path?, depth?)` | Show full hierarchy | Recursive folder query |
| `glob(pattern)` | Find by name pattern | `WHERE name LIKE ?` or regex |
| `grep(pattern)` | Find by content match | `WHERE content LIKE ?` full-text search |
| `read(doc_id)` | Get full document content | `SELECT content FROM docs WHERE id = ?` |

Read `references/exploration-tools.md` for implementation templates (Supabase, SQLite, filesystem).

### Reranking (optional, improves precision)
```python
# Cohere reranker (best quality)
from cohere import Client
reranker = Client(api_key).rerank(query=query, documents=results, top_n=3)

# Cross-encoder reranker (local, free)
from sentence_transformers import CrossEncoder
model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
scores = model.predict([(query, doc) for doc in results])
```

## Step 4: Agent Integration

Give the agent both retrieval methods and let it choose:

```python
SYSTEM_PROMPT = """You have two ways to find information:

1. **search(query)** — Semantic search across the knowledge base. 
   Best for: conceptual questions, topic exploration.

2. **Exploration tools** — Navigate the knowledge base structure.
   - list(path) — see what's in a section
   - tree() — see full structure  
   - glob(pattern) — find by name
   - grep(pattern) — find by content
   - read(id) — read full document
   Best for: specific documents, versioned content, structured navigation.

Choose the right tool for each query. Use search for broad questions,
exploration for specific lookups. Combine both when needed."""
```

## Step 5: Evaluation

Read `references/evaluation.md` for metrics and test frameworks.

**Quick eval checklist:**
- [ ] Retrieval recall: does the right chunk appear in top-5?
- [ ] Answer faithfulness: is the answer grounded in retrieved content?
- [ ] Latency: <2s for search, <5s for exploration chains
- [ ] Edge cases: empty results handling, ambiguous queries
