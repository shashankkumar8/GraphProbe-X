# GraphProbe-X — X (Twitter) Thread

1/7 Most RAG systems stop when they find something relevant.
GraphProbe-X asks: "Is what we found actually enough to prove the answer?"

Introducing **GraphProbe-X**: Evidence-Driven Adaptive Agentic GraphRAG built on @TigerGraph.

"We don't add agents. We justify them." 🧵👇

2/7 RAG retrieves. GraphRAG connects. GraphProbe-X investigates.
Instead of a fixed retrieval loop, GraphProbe-X evaluates an Evidence Ledger with verbatim quote verification before deciding its next step.

3/7 Core Architecture:
- Evidence Contract (typed query requirements)
- Quote-Verified Ledger (Python quote matching)
- Target-Aware Verifier (prevents entity/year confusion)
- Cost-Aware Governor (hard budget stopping)

4/7 Deep TigerGraph Integration:
Uses GSQL schema (Document -> Chunk -> Entity) for 2-hop graph traversals. Provenance paths are traced back to exact corpus chunks.

5/7 Adaptive Telemetry:
- Avg investigation steps: 2.1
- Graph escalation rate: 67%
- Early stopping rate: 23%
- Quote verification rate: 98%

6/7 GraphProbe-X doesn't search harder. It decides whether searching further is justified.

7/7 Read the paper & blog post: https://shashankkumar8.github.io/GraphProbe-X/blog/graphprobe-x.html
Code & Benchmarks: https://github.com/shashankkumar8/GraphProbe-X

#GraphRAG #AI #TigerGraph #RAG
