# GRAPHProbe-X — EMERGENCY AUDIT

**Date:** 2026-10-07
**Commit:** 0ac511f6575825adbdf9bee433b152800d5f21c8
**Branch:** main

### Stack Verified
- **Model:** openai/gpt-4o-mini
- **Embedder:** BAAI/bge-small-en-v1.5 (hash512 fallback in smoke environment)
- **Vector Backend:** Custom NumPy dense vector index (`dense.npy`) with BM25 + RRF
- **Graph Backend:** TigerGraph (schema verified in architecture, memory fallback in test config)
- **Corpus:** `data/raw/corpus/corpus.jsonl`
- **Questions:** 100 public, 50 hidden (hidden not verified to be executed)

### Benchmark Status (from RESULTS.md)
- Agentic evaluated: 120 (52.5% success rate, 850 avg tokens, 2.3s latency)
- RAG: Incomplete due to environment issues.
- GraphRAG: Incomplete due to environment issues.

### Security Status
- No secrets found in tracked `.env` (it's .gitignore'd).
- `.env.example` is clean.

### Required Actions
- RAG/GraphRAG missing benchmarks should be reported honestly as constrained by the environment (Windows torch issues).
- Hidden 50 evaluation needs a check for `eval_hidden.jsonl`.
