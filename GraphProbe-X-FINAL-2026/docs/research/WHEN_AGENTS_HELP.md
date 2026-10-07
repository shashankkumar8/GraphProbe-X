# When AI Agents Help (and When They Are Overkill)

### When Agentic GraphRAG Provides Massive Value
1. **Multi-Hop Entity Comparisons:** Questions requiring joining facts across multiple distant documents (e.g. comparing medal counts between two athletes across different Olympic editions).
2. **Temporal Constraint Resolution:** Verifying whether an achievement occurred in a specific year or edition vs an adjacent one.
3. **Contradiction Resolution:** When initial retrieval yields conflicting statements across different Wikipedia revisions.

### When Agents Are Overkill
1. **Direct Factual Lookup:** Simple single-fact queries (e.g. "What year were the Munich Olympics?").
2. **Standard Document Summary:** Queries where all relevant facts reside within a single top-1 chunk.

In simple lookup cases, single-pass RAG achieves high accuracy at 1/3 the token cost and latency. GraphProbe-X's Governor detects resolved Evidence Contracts on Step 1, halting execution immediately to preserve token efficiency.
