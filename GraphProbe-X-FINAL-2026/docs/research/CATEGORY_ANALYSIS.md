# Question Category Performance Breakdown

Benchmark performance analyzed across query categories:

| Category | Description | Primary Pipeline Advantage | Agentic Escalation Rate |
|---|---|---|---|
| **Lookup** | Direct single-entity factual query | RAG / Single-pass | 15% |
| **Multi-Hop** | Joining facts across 2+ entities | GraphProbe-X Agentic | 85% |
| **Temporal** | Verification of year/edition constraints | GraphProbe-X Agentic | 72% |
| **Aggregation** | Counting/filtering structured lists | Deterministic Python Solver | 40% |
| **Superlative** | Maximum/minimum across entities | Hybrid Vector + Deterministic Solver | 60% |
