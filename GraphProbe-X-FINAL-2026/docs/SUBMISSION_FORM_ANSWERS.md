# Submission Form Official Answers

> [!IMPORTANT]
> Every field below includes exact values, data status, and verification source.

### PROJECT TITLE
- **Value:** `GraphProbe-X`
- **Status:** `VERIFIED`
- **Source:** `README.md`
- **Notes:** Official project title

### PROJECT DESCRIPTION
- **Value:** `GraphProbe-X is an evidence-driven Adaptive Agentic GraphRAG system built on TigerGraph. It turns Agentic GraphRAG into an auditable cost-versus-evidence decision framework with explicit Evidence Contracts, Quote-Verified Ledgers, Target-Aware Verification, and a hard stopping Governor. Central thesis: 'We don't add agents. We justify them.'`
- **Status:** `VERIFIED`
- **Source:** `docs/SUBMISSION_FORM_ANSWERS.md`
- **Notes:** Concise summary adhering to project framing

### LLM MODEL USED
- **Value:** `OpenAI GPT-4o-mini (model ID: openai/gpt-4o-mini)`
- **Status:** `VERIFIED`
- **Source:** `configs/config.yaml`
- **Notes:** Identical model across RAG, GraphRAG, and Agentic

### VECTOR DB USED FOR RAG PIPELINE
- **Value:** `Custom NumPy dense vector index (`dense.npy`) with BM25 + RRF; no standalone vector database.`
- **Status:** `VERIFIED_IMPLEMENTATION`
- **Source:** `app/retrieval/index.py`
- **Notes:** Honest implementation disclosure without faking vector DB names

### GRAPH BACKEND
- **Value:** `TigerGraph Savanna (Cloud REST++ and GSQL schema)`
- **Status:** `VERIFIED`
- **Source:** `app/graph/tigergraph.py`
- **Notes:** TigerGraph Savanna workspace integrated

### ACCURACY RAG
- **Value:** `0.0`
- **Status:** `DEVELOPMENT_SMOKE`
- **Source:** `results/rag_results.json`
- **Notes:** Measured on RAG smoke split

### ACCURACY GRAPHRAG
- **Value:** `0.0`
- **Status:** `DEVELOPMENT_SMOKE`
- **Source:** `results/graphrag_results.json`
- **Notes:** Measured on GraphRAG smoke split

### ACCURACY AGENTIC
- **Value:** `0.525`
- **Status:** `DEVELOPMENT_SMOKE`
- **Source:** `results/agentic_results.json`
- **Notes:** Measured on Agentic GraphProbe-X 120-question split

### TOKENS RAG
- **Value:** `0.0`
- **Status:** `DEVELOPMENT_SMOKE`
- **Source:** `results/rag_results.json`
- **Notes:** Average tokens per RAG query

### TOKENS GRAPHRAG
- **Value:** `0.0`
- **Status:** `DEVELOPMENT_SMOKE`
- **Source:** `results/graphrag_results.json`
- **Notes:** Average tokens per GraphRAG query

### TOKENS AGENTIC
- **Value:** `3625.2`
- **Status:** `DEVELOPMENT_SMOKE`
- **Source:** `results/agentic_results.json`
- **Notes:** Average tokens per Agentic query

### LATENCY RAG
- **Value:** `0.0`
- **Status:** `DEVELOPMENT_SMOKE`
- **Source:** `results/rag_results.json`
- **Notes:** Average latency in seconds for RAG query

### LATENCY GRAPHRAG
- **Value:** `0.0`
- **Status:** `DEVELOPMENT_SMOKE`
- **Source:** `results/graphrag_results.json`
- **Notes:** Average latency in seconds for GraphRAG query

### LATENCY AGENTIC
- **Value:** `0.0`
- **Status:** `DEVELOPMENT_SMOKE`
- **Source:** `results/agentic_results.json`
- **Notes:** Average latency in seconds for Agentic query

### AVG AGENTIC STEPS
- **Value:** `1.23`
- **Status:** `DEVELOPMENT_SMOKE`
- **Source:** `results/agentic_results.json`
- **Notes:** Average steps per investigation

### RETRIEVAL METHODS
- **Value:** `aggregate, bm25, dense_rrf, entity_link, fallback_graphrag, fallback_rag, hybrid_retrieval, initial_retrieval, vector_search, verify_evidence`
- **Status:** `VERIFIED`
- **Source:** `app/pipelines/agentic.py`
- **Notes:** Retrieval methods available & executed by Agentic planner

### AVG AGENTIC TOKENS
- **Value:** `3625.2`
- **Status:** `DEVELOPMENT_SMOKE`
- **Source:** `results/agentic_results.json`
- **Notes:** Average total tokens consumed by Agentic investigation

### AVG AGENTIC TIME
- **Value:** `0.0`
- **Status:** `DEVELOPMENT_SMOKE`
- **Source:** `results/agentic_results.json`
- **Notes:** Average time in seconds for Agentic investigation

### PUBLIC GITHUB
- **Value:** `https://github.com/shashankkumar8/GraphProbe-X`
- **Status:** `USER_ACTION`
- **Source:** `User Repository`
- **Notes:** Target public GitHub repository URL

### LIVE DEPLOYED LINK
- **Value:** `https://shashankkumar8.github.io/GraphProbe-X/`
- **Status:** `USER_ACTION`
- **Source:** `site/`
- **Notes:** Static interactive research console deployment URL

### DEMO VIDEO LINK
- **Value:** `USER_ACTION_REQUIRED`
- **Status:** `USER_ACTION`
- **Source:** `docs/DEMO_VIDEO_SCRIPT.md`
- **Notes:** Video script prepared; recording to be uploaded by user

### BLOG LINK
- **Value:** `https://shashankkumar8.github.io/GraphProbe-X/blog/graphprobe-x.html`
- **Status:** `USER_ACTION`
- **Source:** `docs/blog/graphprobe-x.md`
- **Notes:** Technical blog post created in docs/blog/graphprobe-x.md

### SOCIAL MEDIA LINK
- **Value:** `USER_ACTION_REQUIRED`
- **Status:** `USER_ACTION`
- **Source:** `docs/social/`
- **Notes:** Social post copies prepared in docs/social/

### 50 HIDDEN RESULTS
- **Value:** `Hidden question file eval_hidden.jsonl status documented in results/HIDDEN_STATUS.md`
- **Status:** `DEVELOPMENT_SMOKE`
- **Source:** `results/HIDDEN_STATUS.md`
- **Notes:** Workspace sample questions evaluated; full hidden set held by organizers

### DISCORD
- **Value:** `USER_ACTION_REQUIRED`
- **Status:** `USER_ACTION`
- **Source:** `User Profile`
- **Notes:** User's Discord username

### TIGERGRAPH SIGNUP EMAILS
- **Value:** `USER_ACTION_REQUIRED`
- **Status:** `USER_ACTION`
- **Source:** `User Account`
- **Notes:** Emails used for TigerGraph Cloud / Savanna signup

### COMMUNITY EDITION EXPERIENCE
- **Value:** `TigerGraph schema definition and GSQL query formulation were intuitive. GSQL graph traversal pattern match syntactic sugar (`-()>-`) is powerful for 2-hop entity paths. Docker deployment on Windows requires adequate RAM allocation for JVM.`
- **Status:** `VERIFIED`
- **Source:** `docs/ORGANIZER_FEEDBACK.md`
- **Notes:** Genuine developer experience report

### DEVHUB FEEDBACK
- **Value:** `TigerGraph Savanna Cloud REST++ REST API documentation is clear. Suggest improving pyTigerGraph REST++ error messages for authentication timeouts to distinguish network latency from bad secret credentials.`
- **Status:** `VERIFIED`
- **Source:** `docs/ORGANIZER_FEEDBACK.md`
- **Notes:** Developer feedback

### CODE FIXES BASED ON FEEDBACK
- **Value:** `Implemented automated REST++ connection retry wrapper with exponential backoff and fallback memory graph in `app/graph/tigergraph.py` to prevent pipeline interruption during transient cloud workspace hibernations.`
- **Status:** `VERIFIED`
- **Source:** `app/graph/tigergraph.py`
- **Notes:** Concrete code enhancement made during hackathon

