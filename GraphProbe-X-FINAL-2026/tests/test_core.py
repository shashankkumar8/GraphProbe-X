import os, json, pytest
os.environ["LLM_PROVIDER"] = "mock"; os.environ["GPX_EMBED"] = "hash"; os.environ["GPX_CONFIG"] = "configs/sample.yaml"
from app.core.config import load_config
from app.core.context import build_context
from app.evidence.verifier import verify_quote
from app.evidence.ledger import Ledger
from app.evidence.judge import judge
from app.evidence.contract import Req
from app.agents.harness import Governor
from app.core.meter import Meter
from ingest.chunker import chunk_doc

def test_verifier_exact_fuzzy_reject():
    t = "The 1990 Lumen Cup was won by Marta Velkov, a sprinter."
    assert verify_quote("was won by Marta Velkov", t)[:3:2] == (True, True)
    assert verify_quote("was won by Marta  Velkov,", t)[0]
    assert not verify_quote("was won by Someone Else entirely", t)[0]
    assert not verify_quote("x", t)[0]

def test_chunker_sections_and_ids():
    ch = chunk_doc({"doc_id": "d", "title": "T", "text": "== A ==\nfoo bar.\n\n== B ==\nbaz."})
    assert [c["section"] for c in ch] == ["A", "B"] and ch[0]["chunk_id"] == "d::0"

def test_coverage_and_contradiction():
    reqs = [Req("R1", "entity", "w", "d"), Req("R2", "relation", "c", "d")]; L = Ledger(); a = load_config()["agentic"]
    L.add(req_id="R1", value="Ann", claim_text="x", status="SUPPORTED", confidence=1)
    j = judge(reqs, L, "multi_hop", a); assert j["coverage"] == 0.5 and j["gap_type"] == "RELATION_GAP" and not j["sufficient"]
    L.add(req_id="R2", value="A-land", claim_text="x", status="PARTIALLY_SUPPORTED"); assert judge(reqs, L, "multi_hop", a)["coverage"] == 0.75
    L.add(req_id="R1", value="Bob", claim_text="y", status="SUPPORTED", confidence=1)
    j = judge(reqs, L, "single_fact", a); assert j["contradictions"] and j["recommended_action"] == "verify_evidence"

def test_governor_stops():
    g = Governor({"max_steps": 2, "max_tokens": 100, "patience": 2}); m = Meter()
    class S: zero_streak = 0
    j = {"sufficient": False}
    assert g.check(S, j, m, 2) == "max_steps_reached"
    m.add("x", 100, 10, 1); assert g.check(S, j, m, 0) == "budget_exceeded"
    S.zero_streak = 2; assert g.check(S, j, Meter(), 0) == "no_information_gain"
    assert g.check(S, {"sufficient": True}, Meter(), 0) == "sufficient_evidence"

@pytest.fixture(scope="module")
def ctx(): return build_context(load_config())

def test_three_pipelines_run(ctx):
    from app.pipelines import rag, graphrag, agentic
    q = "Which country did the winner of the 1990 Lumen Cup represent?"
    for m in (rag, graphrag, agentic):
        r = m.run(ctx, q, "t"); assert r["answer"] and r["tokens"]["total"] > 0 and r["n_chunks"] > 0
    t = agentic.run(ctx, q, "t")["trace"]
    assert t["stop_reason"] in ("sufficient_evidence", "max_steps_reached", "budget_exceeded", "no_information_gain", "no_untried_actions")
    assert all(s["candidates"] is not None for s in t["steps"]) and t["steps"][0]["tool"] == "initial_retrieval"

def test_graphrag_has_no_adaptivity(ctx):
    import inspect, app.pipelines.graphrag as g
    src = inspect.getsource(g); assert "while" not in src and "fallback(" not in src.lower().replace("no fallback", "")

def test_fallback_rules(ctx):
    from app.agents.harness import State
    from app.agents.tools import Tools
    st = State("q", "t", "single_fact", [Req("R1", "attribute", "venue", "d")]); T = Tools(ctx, st, Meter())
    r = T.graph_traverse("", "1990 Lumen Cup venue")            # empty seeds -> 0 edges -> document_retrieve fallback
    assert r["fallback"] == "graph_traverse->document_retrieve" and r["chunks"]
    ctx.cfg["agentic"]["min_dense_score"] = 0.99                # force weak-vector-match -> entity_link fallback
    r = T.vector_search("zzz qqq unrelated words")
    assert r["fallback"] == "vector_search->entity_link"
    ctx.cfg["agentic"]["min_dense_score"] = 0.05

def test_dedup_memory_blocks_repeat(ctx):
    from app.agents.orchestrator import Orchestrator
    from app.agents.harness import State
    st = State("Who won the 1990 Lumen Cup?", "t", "single_fact", [Req("R1", "entity", "winner", "winner")])
    o = Orchestrator(ctx); o.ctx_meter_total = 0; j = {"gap_type": "ENTITY_GAP", "missing": ["R1"], "contradictions": [], "recommended_action": "entity_link"}
    c1 = o._candidates(st, j); st.memory.add(("vector_search", c1[1]["target"], "ENTITY_GAP")); c2 = o._candidates(st, j)
    assert [c for c in c2 if c["tool"] == "vector_search"][0]["reject_reason"] == "duplicate_action"

def test_gateway_fallback_cache_and_telemetry(monkeypatch, tmp_path):
    from app.core.llm import LLM
    cfg = load_config(); cfg["llm"]["cache_dir"] = str(tmp_path); calls = []
    class R:
        def __init__(s, c, j): s.status_code, s._j = c, j
        def json(s): return s._j
    def fake(url, json=None, headers=None, timeout=None):
        calls.append(url); return R(429, {}) if "primary" in url else R(200, {"choices": [{"message": {"content": "ok"}}], "usage": {"prompt_tokens": 5, "completion_tokens": 1}})
    monkeypatch.setattr("app.core.llm.requests.post", fake); monkeypatch.setattr("app.core.llm.time.sleep", lambda s: None)
    for k, v in {"LLM_BASE_URL": "http://primary/v1", "LLM_FALLBACK_BASE_URL": "http://fallback/v1", "LLM_FALLBACK_MODEL": "fb"}.items(): monkeypatch.setenv(k, v)
    llm = LLM(cfg); m = Meter(); assert llm.chat("s", "u", m, "x") == "ok"
    assert m.ops[0].provider == "fallback" and [a["status"] for a in m.ops[0].attempts][:3] == ["429"] * 3
    n = len(calls); m2 = Meter(); assert llm.chat("s", "u", m2, "x") == "ok"
    assert len(calls) == n and m2.ops[0].cached and m2.total == m.total       # cache hit replays identical token accounting

def test_accepted_answers_and_team_members():
    from benchmark.evaluator import accepted, det_match
    q = {"id": "1", "gold": "Team Alpha", "raw": {"team_members": ["Ann Lee", "Bo Chan"]}}
    base, acc = accepted(q, {"1": ["Other Event Winner"]})
    assert det_match("The winner was Ann Lee.", base, acc, "any") and det_match("Other Event Winner won", base, acc, "any")
    assert not det_match("Someone Else", base, acc, "any") and not det_match("Ann Leeson", base, acc, "any")

def test_agent_crash_falls_back_and_is_recorded(ctx, monkeypatch):
    import app.pipelines.agentic as A
    monkeypatch.setattr(A.Orchestrator, "run", lambda self, q, qid="", meter=None: (_ for _ in ()).throw(RuntimeError("boom")))
    r = A.run(ctx, "Who won the 1990 Lumen Cup?", "t")
    assert r["fallback"]["to"] == "graphrag" and r["trace"]["stop_reason"] == "agent_crash_fallback" and r["answer"]

def test_llm_call_budget_stops():
    g = Governor({"max_steps": 9, "max_tokens": 10**9, "patience": 9, "max_llm_calls": 2}); m = Meter(); m.add("a", 1, 1, 1); m.add("b", 1, 1, 1)
    class S: zero_streak = 0
    assert g.check(S, {"sufficient": False}, m, 0) == "budget_exceeded"
