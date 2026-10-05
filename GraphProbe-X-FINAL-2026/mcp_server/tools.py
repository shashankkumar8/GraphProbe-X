"""Shared tool layer: used by the MCP stdio server AND the HTTP API. Lazy context; every tool returns JSON-serialisable data."""
import os
from app.core.config import load_config, P

_CTX = None
def ctx():
    global _CTX
    if _CTX is None:
        from app.core.context import build_context
        _CTX = build_context(load_config())
    return _CTX

def _pipe(name):
    from app.pipelines import rag, graphrag, agentic
    return {"rag": rag, "graphrag": graphrag, "agentic": agentic}[name]

def _summ(r):
    o = {"pipeline": r["pipeline"], "answer": r["answer"], "citations": r["citations"], "tokens": r["tokens"]["total"], "input_tokens": r["tokens"]["input"],
         "output_tokens": r["tokens"]["output"], "latency_ms": r["latency_ms"], "chunks": r["n_chunks"]}
    t = r.get("trace")
    if t and "stop_reason" in t:
        o.update(stop_reason=t["stop_reason"], steps=t["tool_sequence"], coverage=t["final_judge"].get("coverage"), confidence=t.get("confidence"),
                 strategy_changes=t["strategy_changes"], fallback=r.get("fallback"))
    return o

def ask(a):
    q = str(a["question"])[:500]; return _summ(_pipe(a.get("pipeline", "agentic")).run(ctx(), q, "api"))

def ask_all(a):
    q = str(a["question"])[:500]; out = {}
    for p in ("rag", "graphrag", "agentic"):
        try:
            r = _pipe(p).run(ctx(), q, "api"); out[p] = _summ(r)
            if p == "agentic": out[p]["trace"] = {k: r["trace"][k] for k in ("question_type", "contract", "steps", "ledger", "stop_reason", "unresolved", "verification")}
        except Exception as e: out[p] = {"error": repr(e)[:300]}
    return {"question": q, "results": out}

def trace(a):
    r = _pipe("agentic").run(ctx(), str(a["question"])[:500], "mcp"); return {"answer": r["answer"], "citations": r["citations"], "trace": r["trace"]}

def search(a):
    k = max(1, min(int(a.get("k", 5)), 20)); r = ctx().cfg["retrieval"]
    return [{"chunk_id": h["chunk_id"], "doc_id": h["doc_id"], "score": round(h["score"], 4), "text": h["text"][:500]} for h in ctx().index.hybrid(str(a["query"])[:500], k=k, cands=r["candidates"], rrf_k=r["rrf_k"])]

def entity(a):
    c = ctx(); ids = c.gd.link(str(a["name"])) or c.gd.link_text(str(a["name"]))
    return [{"id": e, **c.gd.entities[e], "n_chunks": len(c.gd.ent2chunks.get(e, [])), "sample_chunks": c.gd.ent2chunks.get(e, [])[:5]} for e in ids[:5]]

def verify_quote_tool(a):
    from app.evidence.verifier import verify_quote
    c = ctx(); i = c.index.by_id.get(str(a["chunk_id"]))
    if i is None: return {"verified": False, "reason": "unknown chunk_id"}
    ok, sc, ex = verify_quote(str(a["quote"]), c.index.chunks[i]["text"]); return {"verified": ok, "score": sc, "exact": ex, "chunk_id": a["chunk_id"]}

def aggregate(a):
    from app.agents import aggregation as AG
    c = ctx(); o = AG.run(str(a["question"])[:500], AG.records_for(c), c.cfg)
    return o or {"result": None, "reason": "not deterministically answerable from structured corpus fields"}

def status(a=None):
    c = ctx(); cfg = c.cfg
    return {"graph_backend": c.graph.name, "chunks": len(c.index.chunks), "entities": len(c.gd.entities), "embedder": c.index.ename,
            "llm_model": getattr(c.llm, "model", "?"), "llm_fallback": bool(getattr(c.llm, "providers", [0])[1:]), "mock_llm": getattr(c.llm, "model", "") == "mock",
            "structured_records": len(__import__("app.agents.aggregation", fromlist=["x"]).records_for(c)), "results_present": (P(cfg["paths"]["results"]) / "summary.json").exists(),
            "budgets": {k: cfg["agentic"][k] for k in ("max_steps", "max_tokens", "max_llm_calls", "min_gain", "patience")}}

S = lambda **props: {"type": "object", "properties": {k: {"type": v} for k, v in props.items()}, "required": list(props)}
TOOLS = {
    "gpx_ask": (ask, "Answer a question from the corpus with RAG, fixed GraphRAG or adaptive Agentic GraphRAG; returns answer, citations, tokens, stop reason.",
                {"type": "object", "properties": {"question": {"type": "string"}, "pipeline": {"type": "string", "enum": ["rag", "graphrag", "agentic"]}}, "required": ["question"]}),
    "gpx_trace": (trace, "Run the agentic investigation and return the full structured trace: evidence contract, ledger, per-step candidates/utility/coverage/tokens, stop reason.", S(question="string")),
    "gpx_search": (search, "Hybrid BM25+dense+RRF chunk search (no LLM).", S(query="string")),
    "gpx_entity": (entity, "Link a name to corpus entities and show provenance-backed chunk counts (no LLM).", S(name="string")),
    "gpx_verify_quote": (verify_quote_tool, "Deterministically verify that a quote occurs in a chunk (no LLM).", S(chunk_id="string", quote="string")),
    "gpx_aggregate": (aggregate, "Deterministic count/threshold/max/min over structured corpus fields with provenance (no LLM).", S(question="string")),
    "gpx_status": (status, "Backend, index, model, budgets and results availability.", {"type": "object", "properties": {}}),
}
