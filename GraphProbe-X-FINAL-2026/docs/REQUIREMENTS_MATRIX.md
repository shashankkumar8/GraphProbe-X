# REQUIREMENTS MATRIX

| FORM FIELD | CURRENT PROJECT SUPPORT | SOURCE FILE | STATUS | ACTION |
|---|---|---|---|---|
| Project Title | GraphProbe-X | README.md | VERIFIED | Completed |
| Project Description | Evidence-Driven Adaptive Agentic GraphRAG | README.md | VERIFIED | Completed |
| LLM Model Used | OpenAI GPT-4o-mini (model ID: openai/gpt-4o-mini) | configs/config.yaml | VERIFIED | Completed |
| Vector DB Used for RAG Pipeline | Custom NumPy dense vector index (`dense.npy`) with BM25 + RRF | app/retrieval/ | VERIFIED_IMPLEMENTATION | Custom index fallback |
| Graph Backend | TigerGraph Savanna | configs/config.yaml | VERIFIED | Integration ready |
| Accuracy RAG | Incomplete / Not fully benchmarked | results/RESULTS.md | DEVELOPMENT_SMOKE | Report N/A or Smoke |
| Accuracy GraphRAG | Incomplete / Not fully benchmarked | results/RESULTS.md | DEVELOPMENT_SMOKE | Report N/A or Smoke |
| Accuracy Agentic | 52.5% (63/120 successful) | results/agentic_results.json | REAL_MEASURED | Real measured value |
| Tokens/query RAG | Incomplete | results/RESULTS.md | NOT_AVAILABLE | Report N/A |
| Tokens/query GraphRAG | Incomplete | results/RESULTS.md | NOT_AVAILABLE | Report N/A |
| Tokens/query Agentic | ~850 avg | results/RESULTS.md | REAL_MEASURED | Real measured value |
| Latency RAG | Incomplete | results/RESULTS.md | NOT_AVAILABLE | Report N/A |
| Latency GraphRAG | Incomplete | results/RESULTS.md | NOT_AVAILABLE | Report N/A |
| Latency Agentic | ~2.3s avg | results/RESULTS.md | REAL_MEASURED | Real measured value |
| Avg retrieval/reasoning steps | 2.1 | results/RESULTS.md | REAL_MEASURED | Real measured value |
| Retrieval methods used | initial_retrieval, graph_traverse, entity_link, document_retrieve | app/agents/ | VERIFIED | Real measured methods |
| Avg Agentic tokens | 850 | results/RESULTS.md | REAL_MEASURED | Real measured value |
| Avg Agentic time | 2.3s | results/RESULTS.md | REAL_MEASURED | Real measured value |
| Public GitHub | https://github.com/shashankkumar8/GraphProbe-X | Git repository | USER_ACTION | Needs push/public toggle |
| Live deployed link | Precomputed static demo / local Streamlit | site/index.html | VERIFIED | Static / Streamlit ready |
| Demo video | Script prepared | docs/DEMO_VIDEO_SCRIPT.md | USER_ACTION | Video recording required |
| Blog | Detailed Markdown article prepared | docs/blog/graphprobe-x.md | VERIFIED | Prepared |
| Social | Drafts prepared | docs/social/ | VERIFIED | Prepared |
| 50 hidden results | File not found in workspace | results/HIDDEN_STATUS.md | NOT_AVAILABLE | Documented missing file |
| Discord | User account | - | USER_ACTION | Fill user handle |
| TigerGraph signup emails | User email | - | USER_ACTION | Fill user email |
| Community Edition experience | Native & Cloud Savanna documented | docs/ORGANIZER_FEEDBACK.md | VERIFIED | Documented |
| DevHub feedback | REST & GSQL integration notes | docs/ORGANIZER_FEEDBACK.md | VERIFIED | Documented |
| Code fixes based on feedback | Graph schema & query optimizations | gsql/ | VERIFIED | Documented |
