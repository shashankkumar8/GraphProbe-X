# GraphProbe-X — Comprehensive Judge Q&A Guide

### Q1: Why Agentic GraphRAG instead of standard RAG or GraphRAG?
**Answer:** Standard RAG is passive and retrieval-blind; it returns top-K chunks regardless of whether key relations are missing. Standard GraphRAG always executes graph traversal, incurring unnecessary graph query overhead for simple lookups. GraphProbe-X's agentic loop evaluates an Evidence Ledger dynamically, invoking graph traversal only when gap detection proves that simple vector retrieval is insufficient.

### Q2: Why not always use agents?
**Answer:** Agents add token cost, latency, and operational complexity. For direct factual queries (e.g. "Where were the 2016 Olympics held?"), single-pass RAG gets the right answer instantly. GraphProbe-X uses a Governor and Evidence Contract to halt on Step 1 when evidence is complete, avoiding agent overhead when unnecessary.

### Q3: What makes the agent adaptive?
**Answer:** Rather than executing a hardcoded tool chain (e.g. Vector → Graph → Answer), GraphProbe-X selects its next action based on unresolved contract slots, evidence ledger state, past tool yields, and remaining budget.

### Q4: How is the next action selected?
**Answer:** The planner ranks candidate tools (e.g. `entity_link`, `vector_search`, `graph_traverse`, `document_retrieve`, `aggregate`) using an expected evidence gain model divided by estimated token cost. Actions that previously returned zero gain undergo exponential utility decay.

### Q5: Why TigerGraph?
**Answer:** TigerGraph provides sub-second multi-hop graph traversal and GSQL pattern matching (`-()>-`), allowing GraphProbe-X to discover 2-hop entity paths (e.g. Athlete → Event → Venue) with complete provenance back to corpus chunks.

### Q6: What vector backend is used?
**Answer:** GraphProbe-X uses a custom NumPy dense vector index (`dense.npy`) coupled with BM25 keyword search and Reciprocal Rank Fusion (RRF). No external third-party vector database is claimed.

### Q7: How is evidence verified?
**Answer:** Claims extracted by the LLM must pass Python verbatim quote verification. The system checks that the supporting quote exists exactly in the source chunk text and that target entity and temporal constraints match.

### Q8: How is wrong-event / wrong-target contamination prevented?
**Answer:** Target-Aware Verification enforces slot matching for entity name, edition, year, and event discipline. If a retrieved quote mentions "Athlete X winning in 2016" for a query about "2012", the Python verifier flags it as `WRONG_TARGET_EVIDENCE` and marks the slot `UNRESOLVED`.

### Q9: How do you stop infinite loops and control costs?
**Answer:** The Governor enforces hard constraints: `MAX_STEPS` (5), `MAX_TOKENS` (10,000), `MAX_LLM_CALLS` (10), duplicate action detection, and patience thresholds. The LLM cannot override Governor stop signals.

### Q10: Why use deterministic solvers for aggregation?
**Answer:** LLMs frequently make arithmetic and counting errors when summarizing tabular or list context. GraphProbe-X parses structured corpus fields and calculates aggregations deterministically in Python.

### Q11: How is comparison fairness maintained across pipelines?
**Answer:** All three pipelines (RAG, GraphRAG, GraphProbe-X) use the exact same LLM model (`openai/gpt-4o-mini`), same embedding configuration, same answer generation prompts, and same evaluation meter.

### Q12: How are hidden questions handled?
**Answer:** Hidden evaluation questions are executed through frozen pipeline code without prompt tuning or parameter tweaking. Results and traces are recorded in structured JSON format.

### Q13: What happens if the graph is incomplete?
**Answer:** If TigerGraph traversal returns empty subgraphs, the planner falls back to dense document retrieval or BM25 keyword expansion, updating the ledger state accordingly.

### Q14: What happens if retrieved evidence conflicts?
**Answer:** The Evidence Ledger flags conflicting claims as `CONTRADICTED`. The planner attempts targeted document retrieval to resolve the dispute or reports the contradiction in the final output certificate.

### Q15: What were the actual measured results?
**Answer:** On the 120-question agentic smoke evaluation: 52.5% accuracy on valid runs, 850 avg tokens per query, 2.3s avg latency, 2.1 average steps, 67% graph escalation rate, 23% early stop rate, and 98% quote verification rate.

### Q16: What are the main limitations?
**Answer:** Embeddings currently use a 512-dim smoke index due to Windows torch DLL limitations. Rebuilding the full BAAI/bge-small-en-v1.5 dense index requires ~2-3 hours.

### Q17: What would you build in Round 2?
**Answer:** Learned utility functions for the Governor, integration of native TigerGraph Savanna vector search, and temporal validity graph edges.
