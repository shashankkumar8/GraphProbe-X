# GraphProbe-X FINAL 2026 — Windows Run Guide

## What is included
- Real public corpus: `data/raw/corpus/corpus.jsonl` — 2,951 documents.
- Real public benchmark: `data/raw/questions/eval_public.jsonl` — 100 questions.
- Hidden evaluation is intentionally **not included** and must never be used for tuning.
- RAG, fixed GraphRAG, adaptive Agentic GraphRAG, TigerGraph integration, deterministic evidence verification, structured aggregation, benchmark/evaluation, MCP server, HTTP API, and interactive web dashboard.

## 1. Install
Open PowerShell in the project root:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\windows\final_setup.ps1
```

If dependency installation fails, fix the Python/network/package issue first; do not switch the benchmark to mock mode and report those numbers as real.

## 2. Configure
Open `.env` locally. Fill `LLM_API_KEY` and the TigerGraph variables. Never paste the key into chat, screenshots, GitHub, or logs.

For a free plumbing check only, use:

```powershell
$env:LLM_PROVIDER="mock"
$env:GPX_EMBED="hash"
```

Mock/hash mode is only for tests and UI plumbing, not benchmark claims.

## 3. Validate
```powershell
.\scripts\windows\final_validate.ps1
```
Expected data checks: `PUBLIC QUESTIONS = 100`, `CORPUS DOCS = 2951`.

## 4. Build the production index
```powershell
python -m scripts.detect_fields
python -m scripts.inspect_data --rules-only
python -m scripts.build_index
```
Use the configured sentence-transformer dense model for the real benchmark. Hash embeddings are an offline fallback only.

## 5. TigerGraph
Configure the live TigerGraph workspace in `.env`, run:

```powershell
python -m scripts.tg_setup
```
Then set `graph.backend: tigergraph` in `configs/config.yaml` and run the graph gate before benchmarking.

## 6. 10-question pilot
```powershell
.\scripts\windows\final_pilot.ps1
```
Check errors, evidence, traces, token accounting, and the aggregation path before proceeding.

## 7. Public 100
```powershell
.\scripts\windows\final_public_100.ps1
```
This runs RAG, GraphRAG, and Agentic on the same public corpus/question set and writes the measured results. Do not hand-edit results.

## 8. Dashboard
```powershell
.\scripts\windows\final_dashboard.ps1
```
Open `http://127.0.0.1:8000`.

The UI exposes:
- live question investigation
- RAG vs GraphRAG vs Agentic answers
- evidence contract
- structured investigation timeline
- candidate actions and utilities
- evidence ledger and citations
- graph provenance
- stop reason and token/latency telemetry
- benchmark results
- MCP connection instructions

## 9. MCP
Claude Code:

```powershell
claude mcp add graphprobe-x -- python -m mcp_server.server
```

Other MCP clients can use the included `.mcp.json`.

## 10. Freeze / hidden evaluation
Only after the public system is frozen:
- add the official hidden set locally if required by the submission process
- run the hidden export/audit commands
- never tune code/config against hidden answers

## Research integrity rules
1. Same corpus/chunks/embeddings/answer policy for RAG, GraphRAG, Agentic.
2. GraphRAG is fixed; adaptivity exists only in Agentic.
3. A quote existing in a chunk is not automatically semantic support.
4. Aggregation uses structured fields and provenance; prose guessing is rejected.
5. LLM proposes; deterministic code validates, verifies, budgets, and stops.
6. Never invent benchmark numbers.
7. Never claim TigerGraph results when the run used local/mock graph mode.
8. Never expose chain-of-thought; show structured telemetry only.
