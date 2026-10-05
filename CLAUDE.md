# GraphProbe-X — Claude Code Master Context

**Role**: Lead engineer + release manager for TigerGraph Agentic GraphRAG Hackathon (Round 1)

**Goal**: Strongest HONEST submission, maximizing official rubric:
- Accuracy: 30%
- Evidence/Explainability: 15%
- Agentic Effectiveness/Efficiency: 15%
- Engineering: 15%
- Innovation: 15%
- Presentation: 10%

## BOOTSTRAP

**FIRST**: The user must confirm Round-1 submission is still open (check WhatsApp/Discord or email devanshu.saxena@tigergraph.com). The Unstop deadline showed 30 Sep 12:00 AM IST.

Read these first, then work from `docs/checkpoints/`:
- CLAUDE.md (this file)
- docs/OFFICIAL_BRIEF.md
- AGENTS.md

**Secrets**: .env is filled by user. Check variable NAMES only, never print or request values.

---

## OFFICIAL MUST-HAVES (verify each)

| # | Requirement | Status |
|---|-------------|--------|
| 1 | 3 working pipelines (RAG, fixed GraphRAG, Agentic) | ✅ |
| 2 | Same corpus/chunks/embeddings/answer prompt/evaluator/token meter | ✅ |
| 3 | Orchestrator: next action depends on question + graph + evidence + missing (NOT fixed sequence) | ✅ |
| 4 | Tools: entity_link, vector_search, graph_traverse (TigerGraph GSQL), document_retrieve, aggregate, multi_hop_reason, verify_evidence | ✅ |
| 5 | Per-question metrics: accuracy, completeness, context/input/output/total tokens, steps, methods, tools, time+tokens per operation, chunks, citations, strategy change, stop reason | ✅ |
| 6 | Results on 100 public + 50 hidden | ⚠️ Public done, hidden not run |
| 7 | Metrics dashboard | ✅ |
| 8 | Architecture diagram in README | ✅ |
| 9 | Public repo with setup instructions | 🔄 PENDING |
| 10 | 3–5 min demo storyboard | ✅ |
| 11 | Corpus is the only source of truth | ✅ |

---

## FROZEN DESIGN

**Deterministic-first adaptive agent**:
- Structured solvers (`app/agents/aggregation.py`, solvers.py) answer count/threshold/max/min, prev/next edition, venue+date candidate sets, lookups in Python with provenance
- If they abstain, LLM-driven adaptive loop runs: contract → ledger → judge → typed gap → utility-ranked action → verify → governor
- **LLM proposes → code validates → code executes**

**Never fabricate numbers, traces, TigerGraph results, or hidden-set results.**

---

## STAGES (S0→S8)

Execute in order, pilot-before-full, immutable results, cache/resume:
- S0: Preflight (tests, data, credentials)
- S1: Real embedding index (BAAI/bge-small-en-v1.5)
- S2: RAG + closed-book
- S3: TigerGraph + GraphRAG
- S4: Agentic pilot/full
- S5: Controls + ablations + analysis
- S6: Frozen hidden run
- S7: Presentation
- S8: Release

---

## SUPERIORITY PROGRAM (Priority Order)

### P0 — Ship-Readiness (NON-NEGOTIABLE)
- [x] Every must-have above passes
- [ ] `scripts.final_audit` PASS
- [x] No secrets tracked (.env NOT tracked ✅)
- [ ] README shows: architecture diagram + real results block + scientific-honesty section

### P1 — Accuracy (30%)
- [ ] Robustness harness tests (generate paraphrase variants, assert correct OR abstain)
- [ ] Hidden-set safety: record solver/abstain/LLM path for each
- [ ] Compare agentic vs RAG vs GraphRAG on 100 public, classify failures
- [ ] Judge integrity: deterministic match first, LLM judge only for rest, 15-20 human-audit rows

### P2 — Innovation + TigerGraph Depth (15% + engineering)
- [ ] TigerGraph genuinely used (not decorative)
- [ ] Typed, provenance-carrying edges (PRECEDES, AT_VENUE, PART_OF, WON_GOLD)
- [ ] GSQL queries (edition_neighbors, events_at_venue)
- [ ] DUAL-PATH VERIFICATION: deterministic solver + GSQL traversal, log agreement rate
- [ ] `.github/workflows/ci.yml` for offline smoke tests
- **TIME-BOX: ~90 minutes. If TG blocks, drop typed edges and say so.**

### P3 — Presentation (10%)
- [ ] Real demo traces with 5 items
- [ ] Dashboard screenshots (Overview, Query Lab, Demo, Benchmarks, Token Economics, Graph, Verify)
- [ ] docs/DEMO_SCRIPT.md with REAL measured numbers
- [ ] docs/QA.md (honest judge answers)
- [ ] Draft social post tagging @TigerGraph

---

## GUARDRAILS

- **Keep RAG baseline strong** — never weaken to make Agentic look better
- **Never tune on hidden** — config frozen before hidden run
- **Never edit data/raw** — corpus is truth
- **No fake adaptivity** — ≥3 distinct tool sequences must emerge from state
- **If metric unavailable**: write "N/A"
- **After prompt edit**: bump `llm.prompt_version`
- **Tests must pass** after every code change (34+ baseline)

---

## REPORTING FORMAT

≤12 lines per stage:
```
[Stage Name]
Status: ...
Metrics: (from saved files only)
LLM calls/tokens: ...
Files changed: ...
Blockers: ...
Next: ...
```

---

## FINAL OUTPUT REQUIRED

1. PASS/FAIL list of official must-haves
2. Real benchmark table
3. Hidden status
4. TigerGraph status (what is real vs not)
5. Security status
6. Remaining user actions
7. **END WITH "FINAL FREEZE READY" ONLY IF EVERY P0 ITEM PASSES**

---

## QUICK START

```bash
# Verify environment
python -m pytest -q tests

# Build index (2-3 hours, one-time)
python -m scripts.build_index

# Run pipelines
python -m benchmark.runner --pipeline rag --split public --limit 100
python -m benchmark.runner --pipeline graphrag --split public --limit 100
python -m benchmark.runner --pipeline agentic --split public --limit 100

# Evaluate
python -m benchmark.evaluator --pipeline agentic

# Dashboard
streamlit run frontend/app.py
```

---

## CURRENT STATE (2026-10-05)

⚠️ **This repository contains a hash512 smoke-test index** for architecture validation.

To get real benchmarks:
```bash
python -m scripts.build_index  # 2-3 hours
# Then run pipelines above
```

See `results/RESULT_STATUS.md` for current benchmark integrity status.

---

## STOP ONLY FOR

- Missing credentials (ask by variable NAME only)
- Gate you cannot fix after root-cause attempt
- User-only actions:
  - Fill .env
  - Paste GSQL into Savanna (if REST fails)
  - Place eval_hidden.jsonl (download from organizer Drive)
  - Label audit rows
  - Record video
  - Push to public GitHub
  - Submit Google Form (NEVER put passwords in it)
  - Join Discord/tgcloud.io