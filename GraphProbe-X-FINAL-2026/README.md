<div align="center">

# GraphProbe-X
### Evidence-driven adaptive Agentic GraphRAG on TigerGraph
**Retrieve. Connect. Verify. Escalate only when necessary.**
*We don't add agents. We justify them — and measure whether they were worth the cost.*

`3 pipelines` · `quote-verified evidence ledger` · `deterministic aggregation` · `MCP server (7 tools)` · `live dashboard` · `resumable, cached, auditable benchmark`

</div>

## The question
When does additional agentic investigation improve answers enough to justify its extra retrieval, latency and tokens — and when should the system stop or fall back? GraphProbe-X answers this with a controlled three-way benchmark (same corpus, chunks, embeddings, answer prompt, evaluator, token accounting) plus controls (closed-book, RAG-matched) and component ablations.

## Architecture
```
┌──────────────────────────────────────────────────────────────────────────┐
│  CLIENTS: web dashboard · MCP agents (Claude Code, Cursor, Cline, Codex)  │
└───────────────┬───────────────────────────────┬──────────────────────────┘
                │ HTTP /api/ask                 │ MCP stdio (7 tools)
┌───────────────▼───────────────────────────────▼──────────────────────────┐
│ A RAG        B GraphRAG (fixed 2-hop)        C GraphProbe-X (adaptive)    │
│ BM25+dense   4 hybrid + 4 graph chunks       Contract → Ledger → Judge →  │
│ +RRF top-k   no retry / no fallback          Gap → Planner → Tool → Verify│
└───────┬──────────────────┬───────────────────────────┬───────────────────┘
        │                  │ GSQL entity_context       │ HARD GOVERNOR
┌───────▼───────┐  ┌───────▼────────────┐  ┌───────────▼──────────────────┐
│ hybrid index  │  │ TigerGraph (Doc,   │  │ LLM gateway: OpenRouter →    │
│ (BM25+dense)  │  │ Chunk, Entity +    │  │ fallback, disk cache, usage  │
│               │  │ provenance edges)  │  │ telemetry                    │
└───────────────┘  └────────────────────┘  └──────────────────────────────┘
```
**Agentic loop:** Question Analyzer → *Evidence Contract* → cheap initial retrieval → *Evidence Ledger* (claim + verbatim quote, verified in Python) → *Judge* (coverage over verified slots) → if gap: typed gap (ENTITY / RELATION / COVERAGE) → planner logs **all** candidate actions with utility → code validates (budget, dedup, tool) → execute → verify → Governor decides stop. **LLM proposes → code validates → code executes.**

## 12 contracts, each enforced in code
| # | Contract | Guarantee | Module |
|---|---|---|---|
| C1 | Hybrid retrieval | BM25 + dense + RRF + dedup, identical substrate for all pipelines | `app/retrieval/index.py` |
| C2 | Graph traversal | Fixed-hop GSQL; every `MENTIONS` edge carries provenance | `graph/queries/entity_context.gsql`, `app/graph/store.py` |
| C3 | Evidence Contract | Explicit list of what must be proven (typed, required slots) | `app/evidence/contract.py` |
| C4 | Evidence Ledger | `SUPPORTED/PARTIAL/UNSUPPORTED/CONTRADICTED/UNRESOLVED`; `FACT/GRAPH_DERIVATION/INFERENCE` (never inference-as-fact) | `app/evidence/ledger.py` |
| C5 | Verification | A claim is SUPPORTED only if its quote is found in the chunk (Python) or its field equals the raw record | `app/evidence/verifier.py` |
| C6 | Evidence Judge | `coverage = Σ credit(required slots)/#required`, contradictions block sufficiency | `app/evidence/judge.py` |
| C7 | Action planning | Gap-typed candidates, `utility = gain/cost`, rejected candidates logged | `app/agents/orchestrator.py` |
| C8 | Hard Governor | max steps / tokens / LLM calls / low-gain patience; LLM cannot override | `app/agents/harness.py` |
| C9 | Deterministic aggregation | count/threshold/max/min over **structured fields**, tie-aware, re-verified, no prose regex | `app/agents/aggregation.py` |
| C10 | LLM gateway | Retry → documented fallback, disk cache, every attempt logged | `app/core/llm.py` |
| C11 | Accounting | One method (provider usage) for all pipelines; cached calls replay original tokens | `app/core/meter.py` |
| C12 | Reproducibility | Immutable results, resumable runner, hidden-gold guard, manifest hash, `final_audit` | `benchmark/`, `scripts/final_audit.py` |

Resilience layers: provider fallback · TigerGraph error/empty → document retrieval · agent crash → GraphRAG → RAG (failure + wasted tokens recorded).

## Results
<!-- RESULTS:START -->
| Metric |  |
|---|
| Accuracy |  |
| Completeness |  |
| Avg tokens |  |
| Avg latency (ms) |  |
| Avg citations |  |
| LLM calls |  |
| Fallback-call rate |  |

_Generated from `results/summary.json`; every number traces to saved per-question runs._
<!-- RESULTS:END -->

## Windows 5-minute path
For Windows/PowerShell, use `RUN_5_MIN_WINDOWS.md` and `scripts/windows/`. It avoids `make` entirely. The intended sequence is `setup_5min.ps1` → `.env` → copy real public data → `preflight_5min.ps1` → `run_pilot_5min.ps1` → TigerGraph setup → `run_public_100.ps1` → `start_dashboard.ps1`.

Official setup references: OpenRouter API developers: https://openrouter.ai/developers · TigerGraph Cloud cluster creation: https://docs.tigergraph.com/cloud/solutions/create-a-solution · pyTigerGraph Cloud connection: https://docs.tigergraph.com/pytigergraph/current/getting-started/connection

## Quickstart
```bash
pip install -r requirements.txt
cp .env.example .env        # PowerShell: Copy-Item .env.example .env  -> fill OpenRouter key + TG_* (auto-loaded)
make smoke                  # offline self-test (mock LLM + synthetic data; NOT results)
```
**Real run** (put data in `data/raw/corpus/corpus.jsonl`, `data/raw/questions/eval_{public,hidden}.jsonl`):
```bash
python -m scripts.detect_fields && python -m scripts.inspect_data --rules-only   # fix configs/config.yaml data.fields / structured.*
make index                                    # BM25 + dense + entity graph
make tg                                       # TigerGraph schema + load + gate test  (then set graph.backend: tigergraph)
make rag closed graphrag agentic matched      # each: pilot with --limit 10 first; all resumable + cached
make analysis ablation publish                # summary.json, dashboard.html, README results block
make serve                                    # http://127.0.0.1:8000  live ask + trace + results
make hidden && make audit                     # freeze first; never tune on hidden
```

## Web dashboard & API
`make serve` → neo-brutalist dashboard at `http://127.0.0.1:8000`: ask a question and see RAG vs GraphRAG vs Agentic side by side, the evidence contract, every step (candidates with utility, coverage change, tokens, fallbacks), the ledger, stop reason, and the measured results. API: `GET /api/status`, `GET /api/summary`, `POST /api/ask {"question": "..."}`. Binds to `127.0.0.1`; set `GPX_CORS_ORIGIN` to allow exactly one external origin. Static hosting: deploy `site/` (Vercel root dir `site`) after `make publish` for the results view; live asking needs the local API.

## Connect an agent (MCP)
```bash
claude mcp add graphprobe-x -- python -m mcp_server.server          # Claude Code
```
Cursor / Cline / Windsurf / Roo: use `.mcp.json` (`{"mcpServers":{"graphprobe-x":{"command":"python","args":["-m","mcp_server.server"]}}}`). Codex: `[mcp_servers.graphprobe-x] command="python" args=["-m","mcp_server.server"]`.

| Tool | Purpose | LLM? |
|---|---|---|
| `gpx_ask` | answer via `rag` / `graphrag` / `agentic`; tokens, citations, stop reason | yes |
| `gpx_trace` | full structured investigation trace (contract, ledger, candidates, coverage) | yes |
| `gpx_search` | hybrid chunk search | no |
| `gpx_entity` | entity linking + provenance chunk counts | no |
| `gpx_verify_quote` | deterministic quote verification | no |
| `gpx_aggregate` | deterministic count/threshold/max/min over structured fields | no |
| `gpx_status` | backend, index, model, budgets | no |

## Metrics
Official: accuracy (deterministic accepted-answer match, then an LLM judge; same prompt for all), completeness, input/output/total tokens, latency, chunks, citations, steps, tools, strategy changes, stop reasons. Own (labelled): Agentic Tax, Accuracy Gain, gain per 1k tokens, escalation yield, unnecessary escalation, early-stop precision, oracle-router gap, calibration, fallback-call rate.

## Testing
`make test` — unit/integration suite (verifier, ledger, judge, governor, gateway fallback/cache, accepted answers, aggregation, MCP protocol, HTTP API incl. path-traversal guard). `make audit` — citations resolve, SUPPORTED quotes re-verify, hashes, hidden count, no secrets.

## Non-goals & limitations
This system does not attempt perfect recall on every question type; it optimises for measurable, honest evidence sufficiency. Entity extraction is rule-based (homonyms not disambiguated). Planner gain priors are heuristics. Confidence is not a calibrated probability. Deterministic aggregation needs structured fields (raw keys or `Key: value` headers) and otherwise abstains. Vector search runs locally; TigerGraph provides graph traversal and provenance.

MIT License.
