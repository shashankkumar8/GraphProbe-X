# GraphProbe-X
## Evidence-Driven Adaptive Agentic GraphRAG

**Retrieve. Connect. Verify. Escalate only when necessary.**

[![Tests](https://img.shields.io/badge/tests-25%20passed-success)]()
[![Python](https://img.shields.io/badge/python-3.10+-blue)]()
[![TigerGraph](https://img.shields.io/badge/TigerGraph-integrated-orange)]()

> **Research Question**: When does additional agentic investigation improve answer quality enough to justify its additional retrieval, latency, and token cost?

> **Core Principle**: We don't add agents. We justify them—and measure whether they were worth the cost.

---

## Why GraphProbe-X

**RAG retrieves.** It finds relevant chunks and generates answers.

**GraphRAG connects.** It uses knowledge graphs to find related entities and traverse relationships.

**GraphProbe-X investigates.** It detects missing evidence, adaptively selects the next action, verifies what it finds, measures the gain, and stops when further investigation is not justified.

This is not about always using agents. It's about **knowing when to stop**.

---

## Three-Pipeline Architecture

Fair comparison requires identical substrate:

```
                    SAME CORPUS (2,951 docs)
                    SAME CHUNKS (24,695)
                    SAME EMBEDDINGS
                    SAME ANSWER MODEL (gpt-4o-mini)
                    SAME EVALUATOR
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
        RAG          GraphRAG      Agentic GraphProbe-X
          │              │              │
      Hybrid         Hybrid +      Evidence Contract
      Retrieval      Graph            ↓
      (BM25+Dense)   Traversal     Initial Retrieval
          │              │              ↓
          │              │          Evidence Ledger
          │              │              ↓
      Answer ←──────────────→      Gap Detection
          │              │              ↓
      Citations      Citations     Adaptive Planner
                                       ↓
                               ┌───────┼───────┐
                               ▼       ▼       ▼
                            Vector  Graph  Document
                               │       │       │
                               └───────┼───────┘
                                       ▼
                                  Verify Evidence
                                       ↓
                                  Evidence Gain?
                                       ↓
                                   GOVERNOR
                                  ↙         ↘
                                STOP     CONTINUE
```

**Pipeline A (RAG)**: Hybrid retrieval (BM25 + dense → RRF) → top-K → answer

**Pipeline B (GraphRAG)**: Entity linking → hybrid retrieval + fixed 2-hop graph traversal → merge/dedup → answer (NO retry, NO adaptive branching)

**Pipeline C (Agentic GraphProbe-X)**: Evidence Contract → initial retrieval → Evidence Ledger → gap detection → adaptive investigation loop → Governor → answer

---

## Agentic Investigation Loop

```
Question
   ↓
Evidence Contract
   "What must be proven?"
   ↓
Initial Retrieval
   ↓
Evidence Ledger
   claim → SUPPORTED | UNSUPPORTED | CONTRADICTED
   ↓
Gap Detection
   "Which requirements are unresolved?"
   ↓
Adaptive Action Selection
   utility = expected_gain / cost
   ↓
Tool Execution
   entity_link | vector_search | graph_traverse | 
   document_retrieve | aggregate | verify
   ↓
Evidence Verification
   "Does this evidence support the target requirement?"
   ↓
Observed Evidence Gain
   new_claims / tokens_spent
   ↓
Governor
   MAX_STEPS | MAX_TOKENS | no-progress | low-gain
   ├── STOP
   └── CONTINUE
```

**The next action depends on state.** This is NOT a fixed sequence like:
```
Vector → Graph → Vector → Answer  ❌
```

It is:
```
Current evidence + requirements + gaps + history → adaptive decision
```

---

## Evidence Contract + Ledger

Before answering, GraphProbe-X creates an **Evidence Contract** specifying what must be proven:

```json
{
  "requirements": [
    {
      "id": "R1",
      "description": "identity of the target Olympic edition/year",
      "status": "UNRESOLVED"
    },
    {
      "id": "R2",
      "description": "identity of the target event (men's 20km walk)",
      "status": "UNRESOLVED"
    },
    {
      "id": "R3",
      "description": "gold medal winner of that event",
      "status": "UNRESOLVED"
    }
  ]
}
```

As evidence is found, it enters the **Evidence Ledger**:

```json
{
  "claim_id": "C17",
  "requirement_id": "R3",
  "claim": "Chen Ding won gold",
  "status": "SUPPORTED",
  "evidence_type": "FACT",
  "sources": [
    {
      "doc_id": "Q47091419",
      "chunk_id": "Q47091419::2",
      "quote": "Chen Ding (China) won the gold medal"
    }
  ],
  "graph_paths": [
    ["Chen Ding", "WON_MEDAL", "Gold", "IN_EVENT", "Men's 20km Walk"]
  ],
  "confidence": 0.96
}
```

**Evidence states:**
- `SUPPORTED`: Verified in source
- `PARTIALLY_SUPPORTED`: Some evidence found
- `UNSUPPORTED`: No evidence found
- `CONTRADICTED`: Conflicting evidence
- `UNRESOLVED`: Not yet investigated

**Evidence types:**
- `FACT`: Direct textual evidence
- `GRAPH_DERIVATION`: Derived from graph traversal
- `INFERENCE`: Logical inference (flagged, never treated as fact)

**Critical principle:** LLM confidence is not proof.

---

## Target-Aware Verification

### The Contamination Problem

A chunk saying:
> "Athlete X won an event"

**Cannot prove:**
> "Athlete X won the men's 20km walk at the 2012 Olympics"

**Unless** event/edition/entity identity is also verified.

### Protection Layers

1. **Quote verification**: The exact quote must exist in the cited source chunk (Python string match)
2. **Source verification**: The source must match the target event/entity/context
3. **Graph-path provenance**: Graph evidence must trace back to the correct entities
4. **Structured-field verification**: Aggregations verify against raw corpus fields
5. **Contradiction detection**: Conflicting evidence blocks sufficiency

This prevents the system from accepting semantically related but **wrong-event evidence**.

---

## Adaptive Tools

The agent proposes actions. Python validates and executes them.

| Tool | Purpose | Output |
|------|---------|--------|
| `entity_link` | Extract entities from question | Entity IDs |
| `vector_search` | Semantic similarity retrieval | Chunks |
| `graph_traverse` | N-hop graph traversal from seed entities | Related chunks |
| `document_retrieve` | Fetch full document by ID | Document |
| `aggregate` | Deterministic count/max/min over structured fields | Numeric result + provenance |
| `multi_hop_reason` | Multi-step reasoning chain | Intermediate conclusions |
| `verify_evidence` | Check if evidence supports requirement | Verification result |
| `answer` | Generate final answer with citations | Answer + citations |

**LLM proposes → Python validates → Tool executes → Evidence verifies → State updates**

---

## TigerGraph Integration

### Graph Schema

```
Document
   │ HAS_CHUNK
   ↓
Chunk
   │ MENTIONS (provenance: extraction_method, confidence)
   ↓
Entity (name, entity_type, document_frequency)
```

Domain relationships (when extracted with provenance):
- `PART_OF` (event → sport)
- `IN_SPORT`, `IN_DISCIPLINE`
- `AT_VENUE`, `ON_DATE`
- `COMPETED_IN`, `REPRESENTS`
- `WON`, `PRECEDES`

**Every edge carries provenance.** No decorative ontology.

### Graph Query Example

```gsql
CREATE QUERY entity_context(SET<VERTEX<Entity>> ents, INT hops, INT hub_df, INT k) {
  Start = ents;
  Candidates = SELECT c FROM Start -(MENTIONS>:e)- Chunk:c
               WHERE e.confidence > 0.5
               ACCUM c.@score += 1.0 / (1.0 + log(Start.df));
  RETURN Candidates ORDER BY @score DESC LIMIT k;
}
```

Graph retrieval is deterministic and auditable.

---

## Cost-Aware Governor

The Governor enforces **hard limits** that the LLM cannot override:

### Budget Guards
- `MAX_STEPS` (default: 8)
- `MAX_TOKENS` (default: 20,000)
- `MAX_LLM_CALLS` (default: 12)

### Intelligence Guards
- **Duplicate action**: Same tool + same args within N steps → blocked
- **No progress**: Evidence ledger unchanged for N steps → stop
- **Low gain**: `new_evidence / tokens_spent < threshold` → stop
- **Contradiction unresolved**: Contradictory evidence + no resolution path → stop or fallback

### Metrics Tracked
- Total tokens (input + output)
- Context tokens (estimated)
- Latency (ms)
- Evidence gain per token
- **Agentic Tax**: `(agentic_tokens - rag_tokens) / rag_tokens`
- Escalation rate: % of questions requiring >1 action
- Early-stop rate: % stopped before budget exhausted

**One-step correct answers are successful agentic outcomes.**

---

## Benchmark Methodology

### Dataset
- **100 public questions** (with gold answers for validation)
- **50 hidden questions** (organizer-held, no tuning)
- **Corpus**: 2,951 Olympic-related documents

### Fair Comparison
All three pipelines use:
- ✅ Same corpus
- ✅ Same chunks (24,695)
- ✅ Same embeddings
- ✅ Same answer model (gpt-4o-mini)
- ✅ Same answer prompt
- ✅ Same evaluator
- ✅ Same token accounting

**What differs**: Retrieval and control mechanism

### No Hidden Tuning
- Configuration frozen before hidden evaluation
- No per-question hidden heuristics
- No gold-answer-driven logic
- Results immutable (resumable runner, never overwritten without `--force`)

### Per-Question Telemetry
```json
{
  "id": "pub-042",
  "question": "...",
  "answer": "...",
  "citations": ["doc_123", "doc_456"],
  "tokens": {"input": 1847, "output": 89, "total": 1936},
  "latency_ms": 1247,
  "n_chunks": 8,
  "trace": {
    "contract": {...},
    "steps": [...],
    "tool_sequence": ["initial_retrieval", "entity_link", "graph_traverse"],
    "stop_reason": "sufficient_evidence",
    "evidence_gain": 0.042
  }
}
```

---

## Current Repository State

⚠️ **The repository currently contains a hash512 smoke-test index** (fast synthetic embeddings for architecture validation).

### What Works Right Now
✅ Architecture fully implemented  
✅ 25/25 tests pass  
✅ Evidence Contract + Ledger  
✅ Target-aware verification  
✅ Adaptive investigation (demonstrated in smoke-test)  
✅ Governor with budget/patience guards  
✅ TigerGraph schema defined  
✅ MCP server (7 tools)  
✅ Dashboard  
✅ Three-pipeline infrastructure  
✅ Deterministic aggregation  
✅ Benchmark harness (resumable, cached)  

### What Requires Real Index
❌ Real embedding accuracy  
❌ Real embedding completeness  
❌ Real embedding token efficiency  
❌ Final hidden evaluation  

**See [`results/RESULT_STATUS.md`](results/RESULT_STATUS.md) for detailed status.**

---

## Quickstart

### Prerequisites
```bash
Python 3.10+
OpenRouter API key (or OpenAI-compatible endpoint)
TigerGraph Cloud account (free tier works)
```

### Installation
```bash
git clone https://github.com/YOUR_USERNAME/GraphProbe-X.git
cd GraphProbe-X
pip install -r requirements.txt
cp .env.example .env
# Edit .env: add LLM_API_KEY, TG_* credentials
```

### Build Real Index (~2-3 hours, one-time)
```bash
python -m scripts.build_index
```

This creates:
- 24,695 chunks
- 54,194 entities
- BM25 + BAAI/bge-small-en-v1.5 (384-dim) dense index
- Graph data for TigerGraph

### Run Benchmarks
```bash
# RAG baseline
python -m benchmark.runner --pipeline rag --split public --limit 100

# GraphRAG baseline
python -m benchmark.runner --pipeline graphrag --split public --limit 100

# Agentic (adaptive)
python -m benchmark.runner --pipeline agentic --split public --limit 100

# Evaluate
python -m benchmark.evaluator --pipeline rag
python -m benchmark.evaluator --pipeline graphrag
python -m benchmark.evaluator --pipeline agentic

# Compare
python -m benchmark.metrics
```

### Run Tests
```bash
pytest -v tests
```

### Start Dashboard
```bash
streamlit run frontend/app.py
```

### MCP Server
```bash
python -m mcp_server.server
```

---

## Failure Taxonomy

From error analysis:

| Category | Description | Mitigation |
|----------|-------------|------------|
| `RETRIEVAL_MISS` | Gold evidence not in top-K | Increase K, improve chunking |
| `WRONG_ENTITY` | Correct name, wrong entity/event | Target-aware verification |
| `MULTI_HOP_BREAK` | Missing intermediate step | Multi-hop reasoning tool |
| `GRAPH_MISS` | Relationship not in graph | Expand relation extraction |
| `AGGREGATION_ERROR` | Incorrect count/max/min | Deterministic field verification |
| `TEMPORAL_ERROR` | Wrong edition/year | Explicit temporal reasoning |
| `CONTRADICTION` | Conflicting evidence, no resolution | Contradiction detection + source prioritization |
| `INCOMPLETE_ANSWER` | Partial evidence accepted | Stricter coverage threshold |
| `UNSUPPORTED_CLAIM` | LLM hallucination | Quote verification |
| `FORMAT_ERROR` | Answer not parseable | Structured output validation |

---

## Ablations

| Variant | Description | Status |
|---------|-------------|--------|
| `full` | All features enabled | ✅ Implemented |
| `no_structured` | Disable deterministic aggregation solvers | ✅ Implemented |
| `no_judge` | Replace Evidence Judge with heuristic | ✅ Implemented |
| `no_hardstop` | Remove Governor budget limits | ✅ Implemented |
| `no_graph` | Disable graph traversal tool | ✅ Implemented |
| `no_memory` | Disable investigation memory | ✅ Implemented |

Run with:
```bash
python -m benchmark.runner --pipeline agentic --variant no_structured
```

---

## Demo

See [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) for a 3-5 minute walkthrough.

**Suggested questions:**
1. Easy: "Which city hosted the 2016 Summer Olympics?" (RAG sufficient)
2. Graph: "Which events did Usain Bolt compete in?" (Graph helpful)
3. Complex: "Who won the men's 20km walk immediately before 2016?" (Adaptive investigation required)
4. Aggregation: "How many biathlon events had >73 competitors?" (Deterministic solver)
5. Cost: Compare token usage across pipelines

---

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for detailed diagrams.

---

## Reproducibility

Full reproduction requires:
1. Same corpus (2,951 Olympic documents)
2. Same embedding model (BAAI/bge-small-en-v1.5)
3. Same LLM (gpt-4o-mini via OpenRouter)
4. Same config (frozen in `configs/config.yaml`)
5. Same questions (public in `data/raw/questions/`)

All benchmark results trace to saved per-question JSON with:
- Full trace
- Token accounting
- Tool sequence
- Evidence ledger
- Stop reason

**No result can be published without its trace.**

---

## Judge Q&A

See [`docs/JUDGE_QA.md`](docs/JUDGE_QA.md) for detailed answers to expected competition questions.

---

## Limitations

1. **Index build time**: 2-3 hours for 2,951 docs (one-time)
2. **Token cost**: Agentic uses 2-5× RAG tokens on complex questions
3. **Latency**: Additional investigation adds retrieval round-trips
4. **Graph coverage**: Only MENTIONS relation fully extracted; domain relations require NLP/NER
5. **LLM dependency**: Evidence extraction depends on LLM quality
6. **Target verification**: Requires explicit entity/event resolution
7. **Contradiction resolution**: Simple prioritization (not full belief revision)

---

## Contributing

This is a hackathon submission repository. Post-competition contributions welcome.

---

## License

MIT

---

## Citation

```bibtex
@software{graphprobe_x_2024,
  title={GraphProbe-X: Evidence-Driven Adaptive Agentic GraphRAG},
  author={Your Team},
  year={2024},
  url={https://github.com/YOUR_USERNAME/GraphProbe-X}
}
```

---

## Acknowledgments

- **TigerGraph** for the Agentic GraphRAG Hackathon
- **OpenRouter** for LLM API
- Built with: pyTigerGraph, Sentence-Transformers, rank-bm25, Streamlit

---

**Core Philosophy**: We don't add agents. We justify them.

**Research Output**: When is additional investigation worth its cost?

**Practical Impact**: Use the cheapest sufficient strategy. Escalate only when evidence is missing. Stop when further investigation is not justified.
