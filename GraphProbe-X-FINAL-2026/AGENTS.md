# AGENTS.md — rules for any coding agent in this repo (read this FIRST; do not re-derive it)
Project: GraphProbe-X for TigerGraph Agentic GraphRAG Hackathon. Round 1 deliverable: 3 pipelines (RAG, GraphRAG, Agentic) benchmarked on the same data + hidden-50 output + repo + diagram + dashboard + demo. Corpus is the ONLY source of truth.

## Operating rules
- Reuse, patch, test. Never rebuild or add a second architecture. Read files selectively (grep/ranges); never load JSONL into context — stream with Python.
- Deterministic Python for counting/MAX/MIN/temporal/dedup/quote-matching/metrics/budgets. LLM only for analyze/extract/answer/judge. All LLM calls go through `app/core/llm.py` (cache+fallback). Never hardcode keys.
- Never edit raw data (`data/raw/**`), never inspect/tune on hidden answers, never fabricate numbers/TigerGraph/API results. Mark blocked things BLOCKED.
- Pilot (10 q) before any 100-q run. Never run full benchmarks after each edit. Results are immutable (use `--force` deliberately). Runner resumes; cache makes reruns free. After ANY prompt edit bump `llm.prompt_version` in `configs/config.yaml`.
- Fix order on failure: earliest failing component -> smallest patch -> targeted test -> continue.
- Be terse. Report only at stage end, using the checkpoint format below. No long plans.

## Layout / entry points (works without `make`; PowerShell: `$env:VAR="x"`)
`configs/config.yaml` (all knobs) · `.env` auto-loaded · `ingest/` (loader, chunker, entities) · `app/retrieval` (BM25+dense+RRF) · `app/graph` (memory|tigergraph) · `app/evidence` (contract, ledger, verifier, judge) · `app/agents` (orchestrator, tools, governor) · `app/pipelines` (closed_book, rag, rag_matched, graphrag, agentic) · `benchmark/` · `graph/*.gsql` · `mcp_server/` (stdio MCP, 7 tools) · `scripts/serve.py` (dashboard+API) · `site/` (static UI) · `scripts/publish_results.py` (README/site numbers from summary.json)
Commands: `python -m pytest -q tests` · `python -m scripts.detect_fields` · `python -m scripts.inspect_data --rules-only` · `python -m scripts.build_index` · `python -m scripts.tg_setup` · `python -m benchmark.runner --pipeline <closed_book|rag|rag_matched|graphrag|agentic> [--split hidden] [--limit N] [--force]` · `python -m benchmark.evaluator --pipeline <p>` · `python -m benchmark.metrics` · `python -m benchmark.error_analysis` · `python -m benchmark.report` · `python -m benchmark.ablation --n 30` · `python -m benchmark.hidden_export --run` · `python -m scripts.final_audit`
Offline smoke (mock LLM, synthetic data, NOT results): set `LLM_PROVIDER=mock GPX_EMBED=hash GPX_CONFIG=configs/sample.yaml`, run `python scripts/make_sample.py` and `python -m scripts.build_index` first.

## Frozen design (do not change without a measured reason)
RAG = BM25+dense+RRF top-k. GraphRAG = 4 hybrid + 4 graph chunks, fixed 2-hop, NO retry/fallback. Agentic = Evidence Contract -> initial retrieval -> Ledger (claim+verbatim quote, Python-verified) -> deterministic Judge -> gap-typed, utility-ranked, code-validated action -> Governor (max_steps/max_tokens/max_llm_calls/patience) -> final verification -> answer. Fallbacks (Agentic only): weak vector->entity_link, empty/errored graph->document_retrieve, agent crash->GraphRAG->RAG. multi_document questions = candidate-set semantics (no contradiction flagging).

## Checkpoint format (`docs/checkpoints/<STAGE>.md`, <= 25 lines)
Status PASS|FAIL|BLOCKED · counts/metrics (from saved files only) · LLM calls & tokens used · tests · files changed · blockers · exact next command.
 also use the tailwind astra and frontend and web design skills from the respective files here 