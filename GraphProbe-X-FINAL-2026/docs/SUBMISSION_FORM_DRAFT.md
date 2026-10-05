# TigerGraph Agentic GraphRAG Hackathon — Round 1 Submission Form

## Team Information

**Team / Participant Name:** [USER TO FILL]

**Email Address:** [USER TO FILL]

**Team Leader Contact Number:** [USER TO FILL]

**Team Members (Name & Email):**
- [USER TO FILL]
- [USER TO FILL]

## Project Information

**Project Title:** GraphProbe-X: Evidence-Driven Adaptive Agentic GraphRAG

**Project Description:**

GraphProbe-X is an evidence-driven adaptive Agentic GraphRAG system built on TigerGraph that answers the central research question: when does additional agentic investigation improve answer quality enough to justify its retrieval, latency, and token cost—and when should the system stop or fall back?

### Key Innovation
The system uses an **Evidence Contract** that explicitly defines what must be proven before answering. It then adaptively selects the cheapest sufficient evidence acquisition method:
- **Deterministic operations** (counts, max/min, thresholds) where data structure makes them objectively safer
- **Graph traversal** for connected evidence
- **Targeted retrieval** when initial results lack required evidence
- **Multi-hop reasoning** when evidence is fragmented

A hard **Governor** enforces stopping rules (max steps, tokens, LLM calls) and no-progress guards.

### Three Pipelines (Same Corpus, Fair Comparison)
1. **RAG:** BM25 + dense embeddings + RRF dedup → answer
2. **GraphRAG:** Entity linking → fixed 2-hop graph traversal (no retry)
3. **Agentic GraphRAG:** Evidence Contract → adaptive investigation → Governor stop → answer

### Core Deliverables
- **Benchmarks:** 100 public questions per pipeline
- **Hidden:** 50 hidden questions (freeze before evaluation)
- **Evidence Ledger:** Claims tracked with verbatim quotes verified in Python
- **MCP Server:** 7 tools for Claude Code, Cursor, Cline integration
- **Dashboard:** Live investigation traces, side-by-side pipeline comparison
- **TigerGraph Integration:** Entity/chunk provenance tracking

### Results & Metrics
- Accuracy, completeness, token efficiency, latency, citations
- **Agentic Tax:** Cost of adaptive investigation
- **Escalation Rate:** When Agentic diverges from cheaper paths
- **Evidence Gain:** Measured benefit per investigation step

### Project Links
- **GitHub:** [USER TO FILL — will be provided after push]
- **Dashboard:** [USER TO FILL — will be provided after deployment]
- **Demo Video:** [USER TO FILL — optional]

## Submission Confirmation

- [ ] I confirm all information above is accurate.
- [ ] I have tested the project locally and it runs without errors.
- [ ] I have not fabricated or tuned on hidden data.
- [ ] I understand the three pipelines are benchmarked on the same corpus.
- [ ] I have read and agree to the hackathon terms.

---

**Submission Date:** [AUTO-FILL with UTC timestamp when submitted]
