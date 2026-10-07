# GraphProbe-X — Executive Judge One-Pager

> **"An agent should not investigate because it can. It should investigate because the evidence says it must."**

---

### PROBLEM
Retrieval-Augmented Generation (RAG) is passive—retrieving top-K chunks without knowing if required facts are missing. GraphRAG connects entities but incurs fixed graph expansion overhead even for trivial queries. Unconstrained agents waste tokens in endless loops.

### SOLUTION
**GraphProbe-X**: An evidence-driven, cost-aware Adaptive Agentic GraphRAG system built on TigerGraph. It turns investigation into an auditable trade-off between evidence gain and token cost.

---

### CORE ARCHITECTURAL INNOVATIONS
1. **Evidence Contract:** Query parsing into typed slot requirements (`target_entity`, `year`, `discipline`, `relation`).
2. **Quote-Verified Evidence Ledger:** All claims must pass Python verbatim string matching against source text chunks.
3. **Target-Aware Verifier:** Rejects wrong-target, wrong-year context to prevent hallucinated entity joins.
4. **Adaptive Action Planner:** Dynamically selects actions (`vector_search`, `entity_link`, `graph_traverse`, `document_retrieve`, `aggregate`) based on evidence utility per token cost.
5. **Cost-Aware Governor:** Hard operational stopping rules (`MAX_STEPS=5`, `MAX_TOKENS=10,000`, duplicate action detection) that cannot be overridden by LLM.

---

### TIGERGRAPH INTEGRATION
- **Schema:** `Document` → `Chunk` → `Entity` with `HAS_CHUNK`, `MENTIONS`, and `RELATED_TO` edges.
- **Traversal:** GSQL 2-hop entity paths with REST++ API endpoints (`graphprobe-x.i.tgcloud.io`).
- **Provenance:** Every graph edge maps back to verbatim chunk text.

---

### MEASURED TELEMETRY (Agentic Split, n=120)
- **Avg Investigation Steps:** 2.1
- **Graph Escalation Rate:** 67% (invoked TigerGraph when vector retrieval was insufficient)
- **Early Stopping Rate:** 23% (Governor stopped execution upon contract satisfaction)
- **Quote Verification Rate:** 98%
- **Avg Tokens / Latency:** 850 tokens / 2.3 seconds

---

### FAIR COMPARISON FRAMEWORK
- **RAG:** BM25 + dense hybrid retrieval (RRF)
- **GraphRAG:** Fixed 2-hop TigerGraph retrieval
- **GraphProbe-X:** Adaptive Evidence-Driven Agentic GraphRAG
- *All three use identical answer model (`openai/gpt-4o-mini`), corpus, and evaluation meter.*

---

### KEY TAKEAWAY FOR JUDGES
GraphProbe-X doesn't search harder. It decides whether searching further is justified.
