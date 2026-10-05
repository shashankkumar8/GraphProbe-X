# GraphProbe-X Demo Script (3-5 Minutes)

## Setup (Pre-demo)
```bash
cd GraphProbe-X
streamlit run frontend/app.py
```

Open: http://localhost:8501

---

## Demo Questions (5 Examples)

### 1. Easy Question (RAG Sufficient)
**Question**: "Which city hosted the 2016 Summer Olympics?"

**Expected**: Direct retrieval should be sufficient; demonstrate the actual pipeline/trace produced by the current run.

**Show**:
- Answer: "Rio de Janeiro"
- Evidence: 1-2 chunks
- Low token cost (~500 tokens)
- Early stop (1 step)
- Pipeline used: RAG or structured

**Why**: Simple lookup, no investigation needed

---

### 2. Graph-Friendly Question
**Question**: "Which events did Usain Bolt compete in at the 2016 Olympics?"

**Expected**: GraphRAG or Agentic uses graph traversal

**Show**:
- Entity linking: "Usain Bolt" → Entity node
- Graph traversal: Entity → MENTIONS → Chunks
- Answer: List of events
- Graph paths visualization
- Citations with chunk IDs

**Why**: Entity-centric question benefits from graph

---

### 3. Complex Adaptive Question (Hero)
**Question**: "Who won the men's 20 kilometres walk athletics event at the Summer Olympics held immediately before 2016?"

**Expected**: Agentic investigation required

**Show**:
- Evidence Contract: Requirements extracted
  - R1: Identify "immediately before 2016" Olympics (2012)
  - R2: Identify "men's 20km walk" event
  - R3: Find gold medal winner
- Initial retrieval: Finds 2016, 2012, various events
- Gap detection: 2012 winner not in initial chunks
- Adaptive action: Entity link → Graph traverse → Document retrieve
- Evidence Ledger updates with each step
- Verification: Quote matched, event verified
- Governor: Stops when sufficient evidence found
- Answer: "Chen Ding (China)"
- Token cost: Higher (~2000-3000 tokens)
- Tool sequence: [initial_retrieval, entity_link, graph_traverse, verify]

**Why**: Multi-hop reasoning with temporal constraint requires investigation

---

### 4. Aggregation (Deterministic Solver)
**Question**: "How many biathlon events at the 2018 Winter Olympics had more than 73 competitors?"

**Expected**: Deterministic aggregation solver

**Show**:
- Structured field detection
- Deterministic count from infobox fields
- No LLM needed for count operation
- Provenance: List of events with competitor counts
- Answer: "3 events"
- Low token cost (~300 tokens, mostly retrieval)

**Why**: Aggregation over structured fields is safer with deterministic code

---

### 5. Cost / Quality Comparison

**Show Dashboard → Benchmarks / Token Economics**

Use the **actual values displayed by the current run**. Do not use hard-coded or illustrative accuracy/token/latency numbers.

Show:
- Accuracy and completeness
- Input / output / total tokens
- Latency
- Tool calls and investigation steps
- Early-stop / escalation behavior
- Evidence gain per token
- Agentic Tax, only when a real RAG baseline exists for the same run

**Explain the research result, not a predetermined winner:**
- RAG is the low-cost baseline for questions already supported by direct retrieval.
- GraphRAG adds structural retrieval when relationships matter.
- Agentic GraphRAG spends additional investigation budget only when the evidence state indicates a gap.
- The important comparison is **quality gained per additional cost**.

> **Demo integrity:** every displayed benchmark number must come from the saved result files/dashboard. If a metric is unavailable, display **N/A** rather than an illustrative value.

---

## Demo Flow

### Opening (30 seconds)
"GraphProbe-X is an evidence-driven adaptive Agentic GraphRAG system. It doesn't always use agents—it decides when additional investigation is worth the cost."

### Demo 1-2 (2 minutes)
Show easy and graph questions. Emphasize:
- RAG works for simple cases
- Graph helps for entity-centric questions
- Low cost, fast answers

### Demo 3 (1.5 minutes)
Show complex question. Emphasize:
- Evidence Contract creates requirements
- Adaptive investigation fills gaps
- Governor stops when sufficient
- Higher cost, but justified for complex questions

### Demo 4 (30 seconds)
Show aggregation. Emphasize:
- Deterministic solver avoids LLM errors
- Provenance preserved
- Very low cost

### Demo 5 (30 seconds)
Show comparison table. Emphasize:
- Fair three-way comparison
- Use cheapest sufficient strategy
- Measure cost/benefit trade-off

### Closing (15 seconds)
"We don't add agents. We justify them—and measure whether they were worth the cost."

---

## Backup Questions (If Time Permits)

1. "Who won gold in the women's 100m at the 2012 Olympics?" (Easy)
2. "How many swimming events did Michael Phelps win in 2008?" (Aggregation)
3. "What was the final score of the men's basketball final in 2016?" (Simple retrieval)
4. "Which country won the most medals at the 2018 Winter Olympics?" (Aggregation + verification)
5. "Who was the oldest medalist at the 2016 Olympics?" (Complex, requires cross-referencing)

---

## Common Questions from Judges

**Q: Why not always use agents?**
A: Cost. Agentic can cost more than simpler pipelines because investigation adds actions; the dashboard measures whether that extra cost produced additional verified evidence.

**Q: How do you prevent wrong-event contamination?**
A: Target-aware verification. We check that evidence refers to the correct event/entity, not just any event with similar names.

**Q: What if the agent goes into a loop?**
A: Governor enforces hard limits: MAX_STEPS, MAX_TOKENS, duplicate-action guard, no-progress guard.

**Q: How do you know when to stop?**
A: Evidence Judge computes coverage over required slots. Governor stops when coverage = 1.0 or budget exhausted or no progress.

**Q: What happens if the agent is wrong?**
A: Evidence verification catches unsupported claims. Contradiction detection flags conflicts. Fallback to GraphRAG if agent crashes.

**Q: Why deterministic solvers?**
A: Aggregation over structured fields is safer with code than LLM text generation. Deterministic = re-checkable, exact, provenance-preserved.

---

## Technical Demo (If Requested)

### Show MCP Tools
```bash
python -m mcp_server.server
```

Tools available:
1. `entity_link` - Extract entities from question
2. `vector_search` - Semantic similarity search
3. `graph_traverse` - N-hop traversal from entities
4. `document_retrieve` - Fetch document by ID
5. `aggregate` - Deterministic count/max/min
6. `verify_evidence` - Check if evidence supports requirement
7. `answer` - Generate final answer with citations

### Show TigerGraph Query
```sql
-- In TigerGraph GSQL editor
RUN QUERY entity_context(["Usain_Bolt"], 2, 50, 20)
```

### Show Evidence Ledger (JSON)
Open: `results/agentic_results.json`

Find a question's `trace.ledger` to show SUPPORTED/PARTIALLY_SUPPORTED/UNSUPPORTED claims.

---

## Key Metrics to Emphasize

1. **Evidence Gain per Token**: How much new evidence did we get per token spent?
2. **Early Stop Rate**: % of questions where Governor stopped before budget exhausted
3. **Escalation Rate**: % of questions requiring >1 action
4. **Agentic Tax**: (Agentic_tokens - RAG_tokens) / RAG_tokens
5. **Accuracy vs Cost Trade-off**: Is the accuracy gain worth the token cost?

---

## Demo Checklist

- [ ] Dashboard running at localhost:8501
- [ ] Sample questions prepared
- [ ] TigerGraph cluster accessible
- [ ] LLM API working
- [ ] Results JSON available for inspection
- [ ] Backup slides ready
- [ ] Timing practiced (3-5 minutes)

---

Good luck! 🎯
