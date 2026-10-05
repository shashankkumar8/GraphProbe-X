# Judge Q&A

## About the System

### Q: Why Agentic GraphRAG?

**A**: Traditional RAG retrieves chunks. GraphRAG connects entities. But neither knows when to stop or what's still missing. GraphProbe-X investigates missing evidence, verifies it, and stops when sufficient.

The key question isn't "How do we add agents?" but **"When does additional investigation improve answers enough to justify its cost?"**

---

### Q: Why not always use agents?

**A**: Because additional investigation has a cost in tokens, latency, and tool calls.

For simple questions, direct retrieval can already satisfy the evidence contract, so escalating would add cost without a corresponding evidence gain.

For complex questions, GraphProbe-X can spend additional investigation budget when the ledger shows unresolved requirements.

The principle is:

> **Use the cheapest sufficient strategy. Escalate only when evidence is missing.**

---

### Q: What makes this genuinely adaptive?

**A**: The next action depends on state, not a fixed script.

State includes:
- Question type (lookup, aggregation, multi-hop)
- Current evidence ledger (what's proven, what's missing)
- Previous actions (avoid duplicates)
- Budget remaining (tokens, steps)
- Observed evidence gain (new claims per token)

Fixed sequence: `Vector → Graph → Answer` ❌

Adaptive decision: `Current state → Planner → Tool → Verify → Update state → Decide continue/stop` ✓

---

### Q: How is evidence verified?

**A**: Four layers:

1. **Quote verification**: Exact quote must exist in cited chunk (Python string match)
2. **Target verification**: Evidence must refer to correct event/entity, not just similar names
3. **Graph provenance**: Graph paths must trace to correct entities
4. **Field verification**: Structured field values verified against raw corpus

A claim saying "Athlete X won an event" cannot prove "Athlete X won men's 20km walk at 2012 Olympics" unless event/edition identity is also verified.

---

### Q: Why TigerGraph?

**A**:
1. Native graph queries for entity-centric questions
2. Provenance tracking (every MENTIONS edge has extraction method, confidence)
3. GSQL allows custom traversal logic
4. Free tier sufficient for research
5. Graph traversal is deterministic and auditable

Alternative (Neo4j, NetworkX) would work, but TigerGraph's query language and performance at scale make it suitable for Agentic GraphRAG.

---

### Q: How do you control cost?

**A**: The Governor enforces hard limits:

- `MAX_STEPS` (default: 8)
- `MAX_TOKENS` (default: 20,000)
- Duplicate action guard
- No-progress guard (stop if ledger unchanged for N steps)
- Low-gain guard (stop if `new_evidence / tokens < threshold`)

The LLM **cannot override** these guards. Python enforces them.

---

### Q: How do you prevent hallucination?

**A**:
1. **Quote verification**: Claims must quote source verbatim
2. **Source linking**: Every claim links to chunk_id
3. **Evidence states**: UNSUPPORTED, PARTIALLY_SUPPORTED, CONTRADICTED (not just "LLM said it")
4. **Target verification**: Evidence must match the target event/entity
5. **Deterministic operations**: Aggregation uses Python code, not LLM prose

LLM extracts claims, but verification happens in code.

---

### Q: How do you prevent wrong-event contamination?

**A**: This is the most critical failure mode.

Example:
- Question: "Who won men's 20km walk at 2012 Olympics?"
- Retrieved chunk: "Athlete X won hammer throw at 2012 Olympics"
- Wrong: Accepting "Athlete X" as winner

Prevention:
1. Evidence Contract requires: "event = men's 20km walk", "year = 2012"
2. Verifier checks: Does chunk mention "20km walk" AND "2012"?
3. If event mismatch → claim marked UNSUPPORTED or WRONG_EVENT
4. Governor continues investigation until correct event found

---

### Q: How is RAG vs GraphRAG vs Agentic fair?

**A**: They share everything except retrieval/control:

**Identical**:
- Corpus (2,951 docs)
- Chunks (24,695)
- Embeddings (BAAI/bge-small-en-v1.5)
- Answer model (gpt-4o-mini)
- Answer prompt
- Evaluator
- Token accounting

**Different**:
- RAG: BM25 + dense → RRF → top-K → answer
- GraphRAG: Entity link + vector + graph → merge → answer (NO retry)
- Agentic: Contract → Ledger → adaptive investigation → Governor → answer

This isolates the retrieval/control mechanism as the variable.

---

### Q: What happens on hidden questions?

**A**:
1. Never tune on hidden (no gold answers visible)
2. Configuration frozen before hidden run
3. Results saved to `results/hidden_agentic.json`
4. Metrics computed by organizer's evaluation script
5. No per-question hidden hacks in code

If hidden file contains answer-like fields, the runner **refuses to run** (safety check).

---

### Q: What happens when the agent is wrong?

**A**: Multiple layers:

1. **Evidence verification catches unsupported claims** → marked UNSUPPORTED
2. **Contradiction detection** → requires resolution or marks as CONTRADICTED
3. **Governor fallback** → if agent crashes, falls back to GraphRAG → RAG
4. **Failure recorded** → wasted tokens, fallback path logged in trace

The system never hides failures. Every error is recorded.

---

### Q: Why deterministic solvers?

**A**: For aggregation/superlative questions:

**LLM approach**:
- "Count events with >73 competitors"
- LLM reads chunks, generates count
- Risk: Miscount, hallucinated events, no provenance

**Deterministic approach**:
- Extract competitor counts from structured fields (infobox)
- Python: `sum(1 for e in events if e.competitors > 73)`
- Exact count, re-checkable, provenance preserved

Code is safer than text generation for structured operations.

---

### Q: How do you prove it is not hard-coded?

**A**:
1. **No per-question conditionals**: Solvers use generic parsers, not `if question_id == "pub-042"`
2. **Ablation support**: Run `--variant no_structured` to disable deterministic solvers
3. **Trace shows investigation**: Complex questions show multi-step tool sequences
4. **Source code is open**: Inspect `app/agents/aggregation.py`, `app/agents/orchestrator.py`
5. **Early stop varies**: Different questions stop at different steps (1, 3, 5 steps)

The adaptive path emerges from state, not from hard-coded question logic.

---

## About Results

### Q: What accuracy did you achieve?

**A**: The repository distinguishes architecture/smoke-test validation from publishable benchmark results.

Current smoke-test results use the hash512 synthetic embedding substrate and are **not presented as real semantic-retrieval accuracy**. Real RAG/GraphRAG benchmark accuracy requires rebuilding the real embedding index and rerunning the public benchmark under the same evaluation setup.

We do not quote expected or illustrative accuracy numbers as achieved results.

---

### Q: Why not show the real numbers?

**A**: Honesty.

The repository currently has a hash512 index (synthetic embeddings for fast architecture testing). Publishing accuracy numbers from this would be misleading.

We chose to:
- ✅ Show architecture is working (25/25 tests pass)
- ✅ Show smoke-test results (proves system runs end-to-end)
- ✅ Provide clear instructions for real benchmark
- ❌ Not fake real benchmark results

A smaller truthful repository is stronger than a polished one with false claims.

---

### Q: What if the real benchmark shows Agentic is worse?

**A**: Then we publish that.

The research question is "When does agentic investigation help?" not "How do we prove agentic is better?"

If Agentic costs 3× tokens but only gains 2% accuracy, that's a valid finding. It tells users: "Don't use agents for this domain."

The value is in the measurement, not in a predetermined outcome.

---

## About Implementation

### Q: What LLM do you use?

**A**: The configured answer model is **gpt-4o-mini** through an OpenAI-compatible gateway. LLM calls are metered and traced.

The repository keeps benchmark claims tied to saved results rather than using estimated performance figures.

---

### Q: What embeddings?

**A**: BAAI/bge-small-en-v1.5 (384 dimensions).

Alternative: OpenAI text-embedding-3-small (same dimensions, lower quality).

BGE was chosen for:
- Strong semantic retrieval
- Open-source
- 384-dim (smaller than 768/1536 alternatives)
- Good performance on domain-specific benchmarks

---

### Q: What graph relationships exist?

**A**:
- `Document → HAS_CHUNK → Chunk`
- `Chunk → MENTIONS → Entity` (with extraction method, confidence)

Domain relationships (when extracted):
- `PART_OF` (event → sport)
- `IN_SPORT`, `IN_DISCIPLINE`
- `AT_VENUE`, `ON_DATE`
- `COMPETED_IN`, `REPRESENTS`
- `WON`, `PRECEDES`

Only relationships with provenance are added. No decorative ontology.

---

### Q: What is the MCP server?

**A**: Model Context Protocol server exposing 7 tools:
1. `entity_link` - Extract entities from question
2. `vector_search` - Semantic similarity search
3. `graph_traverse` - N-hop traversal
4. `document_retrieve` - Fetch document
5. `aggregate` - Deterministic count/max/min
6. `verify_evidence` - Check evidence support
7. `answer` - Generate final answer

Allows Claude Code, Cursor, other MCP clients to use GraphProbe-X as a tool.

---

### Q: How long does the index take to build?

**A**:
- Corpus: 2,951 docs
- Chunks: 24,695
- Entities: 54,194
- Time: ~2-3 hours on CPU (depends on embedding model download)

Once built, cached. Incremental updates possible.

---

### Q: What if I don't have TigerGraph?

**A**: Pipeline A (RAG) works without TigerGraph.

Pipelines B (GraphRAG) and C (Agentic) require graph traversal, but can fallback to document retrieval if graph is unavailable.

Free TigerGraph Cloud tier is sufficient.

---

## About the Hackathon

### Q: What is the core innovation?

**A**: Three innovations:

1. **Evidence Contract + Ledger**: Explicit representation of what must be proven and its verification status
2. **Adaptive investigation**: Next action depends on state, not fixed sequence
3. **Cost-aware Governor**: Stop when sufficient, measure gain per token

Combined: A system that investigates when justified, stops when sufficient, and measures cost/benefit.

---

### Q: What would you do with more time?

**A**:
1. **Real embedding index** (2-3 hours one-time)
2. **Full real benchmark** (run all three pipelines)
3. **Hidden evaluation** (after freezing config)
4. **Error analysis** (classify failure modes)
5. **Improved graph relations** (NER for domain relationships)
6. **Learned information-gain model** (predict which action will help most)
7. **Multi-corpus validation** (test on non-Olympic domains)

---

### Q: What are the limitations?

**A**:
1. **Index build time**: 2-3 hours initial, then cached
2. **Token cost**: Agentic uses 2-5× tokens on complex questions
3. **Latency**: Additional investigation adds round-trips
4. **Graph coverage**: Only MENTIONS fully extracted; domain relations need NER
5. **LLM dependency**: Evidence extraction quality depends on LLM
6. **Target verification**: Requires explicit entity/event resolution
7. **Contradiction resolution**: Simple prioritization, not full belief revision

---

### Q: How can others use this?

**A**:
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up `.env` (LLM API key, TigerGraph credentials)
4. Build index: `python -m scripts.build_index`
5. Run pipelines: `python -m benchmark.runner --pipeline agentic --split public --limit 10`
6. Evaluate: `python -m benchmark.evaluator`

Works on any corpus. Adapt chunker and entity extractor for your domain.

---

### Q: What is the most important takeaway?

**A**: We don't add agents. We justify them.

The system's value isn't in using agents everywhere, but in knowing **when** additional investigation is worth its cost and **when** to stop.

Simple questions → RAG (cheap, fast)
Medium questions → GraphRAG (moderate cost)
Complex questions → Agentic (higher cost, better evidence)

Measure the trade-off. Don't assume agents are always better.
