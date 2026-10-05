# GraphProbe-X — Quick Start Guide

## Setup (5 minutes)

1. **Clone the repository**:
```bash
git clone https://github.com/shashankkumar8/GraphProbe-X.git
cd GraphProbe-X/GraphProbe-X-FINAL-2026
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and add:
# - LLM_API_KEY (get from https://openrouter.ai/keys)
# - TG_HOST, TG_USER, TG_PASS, TG_GRAPH, TG_SECRET (TigerGraph Cloud)
```

4. **Run tests** (verify setup):
```bash
python -m pytest -q tests
```

---

## Run It Live (Dashboard)

**Option 1: Use existing smoke-test index (INSTANT)**
```bash
streamlit run frontend/app.py
```
Opens at: http://localhost:8501

This uses the hash512 smoke-test index (fast, architecture demo only).

**Option 2: Build real index first (2-3 hours, then use)**
```bash
# Build real embeddings index (one-time, 2-3 hours)
python -m scripts.build_index

# Start dashboard
streamlit run frontend/app.py
```

---

## Run Benchmarks

### Pilot (10 questions, quick test)
```bash
python -m benchmark.runner --pipeline rag --split public --limit 10
```

### Full (100 questions)
```bash
# RAG baseline
python -m benchmark.runner --pipeline rag --split public --limit 100 --workers 4

# GraphRAG baseline
python -m benchmark.runner --pipeline graphrag --split public --limit 100 --workers 4

# Agentic (adaptive investigation)
python -m benchmark.runner --pipeline agentic --split public --limit 100 --workers 4
```

### Evaluate
```bash
python -m benchmark.evaluator --pipeline rag
python -m benchmark.evaluator --pipeline graphrag
python -m benchmark.evaluator --pipeline agentic
python -m benchmark.metrics
```

---

## Dashboard Views

Once running at http://localhost:8501:

1. **Overview** — System status, metrics summary
2. **Query Lab** — Try your own questions, see investigation traces
3. **Evidence** — Evidence Contract, Ledger, verification status
4. **Investigation Timeline** — Step-by-step adaptive actions
5. **Graph** — TigerGraph entity/chunk visualization
6. **Benchmarks** — RAG vs GraphRAG vs Agentic comparison
7. **Token Economics** — Cost analysis, Agentic Tax
8. **Demo** — Pre-recorded demo questions with traces

---

## Try Example Questions

In Query Lab, try:

**Easy (RAG sufficient)**:
- "Which city hosted the 2016 Summer Olympics?"

**Graph-friendly**:
- "Which events did Usain Bolt compete in at 2016 Olympics?"

**Complex (Agentic investigation required)**:
- "Who won the men's 20 kilometres walk at the Summer Olympics held immediately before 2016?"

**Aggregation**:
- "How many biathlon events at the 2018 Winter Olympics had more than 73 competitors?"

---

## API Access

Start MCP server (for Claude Code, Cursor, etc.):
```bash
python -m mcp_server.server
```

7 tools available:
- `entity_link`
- `vector_search`
- `graph_traverse`
- `document_retrieve`
- `aggregate`
- `verify_evidence`
- `answer`

---

## Troubleshooting

### "RuntimeError: index built with hash512"
You're trying to use real embeddings with smoke-test index.

**Fix**: Build real index first:
```bash
python -m scripts.build_index
```

### "No module named 'app'"
You're in the wrong directory.

**Fix**:
```bash
cd GraphProbe-X-FINAL-2026  # The inner directory
python -m pytest -q tests
```

### "Missing LLM_API_KEY"
Environment variable not set.

**Fix**: Edit `.env` and add your OpenRouter API key.

### "TigerGraph connection failed"
TG credentials missing or cluster down.

**Fix**: 
1. Get free cluster at https://tgcloud.io
2. Update `.env` with credentials
3. Run: `python -m scripts.tg_setup`

---

## What You'll See

### With Smoke-Test Index (Instant)
- ✅ Dashboard loads
- ✅ Architecture demonstration
- ✅ Tool sequences visible
- ✅ Evidence Ledger operational
- ⚠️ Accuracy metrics not real (hash embeddings)

### With Real Index (After 2-3 hour build)
- ✅ Everything above
- ✅ Real semantic retrieval
- ✅ Valid accuracy metrics
- ✅ Production-quality results

---

## Files You Can Edit

- `configs/config.yaml` — System parameters
- `.env` — Credentials (never commit!)
- `data/raw/questions/` — Add your own questions

---

## Need Help?

1. Check `docs/` directory for detailed docs
2. Run `python -m pytest -v tests` to verify setup
3. See `results/RESULT_STATUS.md` for current status
4. Read `CLAUDE.md` for developer context

---

## Quick Commands Reference

```bash
# Tests
pytest -v tests

# Build index
python -m scripts.build_index

# Run benchmark
python -m benchmark.runner --pipeline agentic --split public --limit 10

# Evaluate
python -m benchmark.evaluator --pipeline agentic

# Dashboard
streamlit run frontend/app.py

# MCP Server
python -m mcp_server.server
```

---

**Ready to go! Start with `streamlit run frontend/app.py` for instant demo.**
