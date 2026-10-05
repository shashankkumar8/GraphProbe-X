# GraphProbe-X — Judge Q&A

## Why This Project?

**Core Question:** When does additional agentic investigation justify its cost?

This is not about "Agentic is always better." It's about **measuring when it is**, and honestly reporting when it's wasteful. That's the real innovation.

## Design Decisions

### Why Three Pipelines?
To measure fairly, we need a baseline (RAG), a control (GraphRAG), and the innovation (Agentic). Without all three on the same corpus, we cannot claim anything.

### Why Evidence Contracts?
Because claiming "Person X won Event Y" without proving you found the RIGHT event is false. Contracts make requirements explicit and verifiable.

### Why Deterministic Solvers?
For **counts, max/min, thresholds**, structured data (Olympic infoboxes) allows exact, re-checkable provenance without LLM. This is safer and cheaper. But solvers must abstain when unsafe.

### Why Hash Embeddings?
Due to a Windows/torch DLL environment issue, we fell back to `hash512` embeddings. This is documented and trades embedder quality for system stability. Real dense embeddings are planned for future runs.

### Why a Governor?
LLMs cannot be trusted to stop investigating. Hard budget limits (steps, tokens, calls) prevent runaway costs and forced decisions.

### Why TigerGraph?
It's the challenge requirement. We use it for entity/chunk provenance, supporting the Evidence Ledger with graph paths and relationships.

## Benchmark Integrity

### No Tuning on Hidden
We freeze code and prompts before evaluating hidden data. Every hidden result is traced and verifiable in the same way as public results.

### Resumable Runs
The benchmark runner is designed to resume from partial progress. No manual re-runs or cherry-picking.

### Real LLM, Real Tokens
Token counts are from the LLM provider's response headers. Fallback behavior is documented. Cached calls replay original counts for reproducibility.

## Known Limitations

### 1. Embedder Quality
Hash embeddings are weaker than BAAI/bge-small-en-v1.5. This affects retrieval quality across all three pipelines equally. Dense embeddings should be substituted when torch/Windows issues are resolved.

### 2. Benchmark Scale
Due to time constraints and benchmarking timeouts, final results may be from a reduced question set (e.g., 20–50 questions). This is documented in results/.

### 3. TigerGraph Setup
If REST schema installation fails on Savanna, GSQL can be manually pasted into the cloud console. This is a known Savanna limitation, not a system design flaw.

### 4. Agentic Complexity
The Agentic pipeline is more complex than RAG/GraphRAG. Some questions may not benefit from additional investigation, resulting in "Agentic Tax" (extra cost for no gain). This is expected and measured.

## Scoring Expectations

We optimize for **Accuracy** + **Efficiency** + **Integrity**:

- **Accuracy:** Can the system find and verify the correct answer?
- **Efficiency:** Does Agentic justify its tokens and latency vs. RAG?
- **Integrity:** Are results auditable and reproducible?

We do NOT optimize for:
- Beating competitors on every question
- Claiming Agentic always wins
- Speed over correctness
- Cosmetic dashboard polish

## What to Look For

1. **Evidence Ledger:** Can you trace every claim to a quoted source?
2. **Tool Sequences:** Do three distinct investigation strategies appear (Pilot section)?
3. **Stopping Behavior:** Does the Governor stop when no progress is made?
4. **Token Accounting:** Are tokens accurately counted and reported?
5. **Hidden Results:** Are they traced and verifiable like public results?

---

**Questions?** Contact: [USER TO FILL — team email]
