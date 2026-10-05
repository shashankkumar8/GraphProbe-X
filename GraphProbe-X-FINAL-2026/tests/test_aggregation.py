import os, re, pytest
os.environ["LLM_PROVIDER"] = "mock"; os.environ["GPX_EMBED"] = "hash"; os.environ["GPX_CONFIG"] = "configs/sample.yaml"
from app.core.config import load_config
from app.agents import aggregation as AG

CFG = load_config()
def D(i, title, text="x", **raw): return {"doc_id": i, "title": title, "text": text, "raw": {"id": i, "title": title, "text": text, **raw}}
DOCS = [D("a", "Curling Men", games="1988 Winter Olympics", sport="Curling", competitors=60), D("b", "Curling Women", games="1988 Winter Olympics", sport="Curling", competitors="75 (from 9 nations)"),
        D("c", "Biathlon 20km", games="1988 Winter Olympics", sport="Biathlon", competitors=75), D("d", "Curling 1992", games="1992 Winter Olympics", sport="Curling", competitors=99),
        D("e", "Prose only", "The event attracted 500 competitors.", games="1988 Winter Olympics", sport="Curling"),
        D("f", "Header doc", "Competitors: 80\nSport: Curling\nGames: 1988 Winter Olympics\nbody")]
R = AG.build_records(DOCS, CFG)

def test_count_threshold_data_driven_constraints():       # 'curling' is in no hard-coded list; constraints come from data values
    o = AG.run("How many curling events at the 1988 Winter Olympics had more than 60 competitors?", R, CFG)
    assert o["value"] == "2" and {s["doc_id"] for s in o["sources"]} == {"b", "f"}          # b (75), f (80 via strict header line); a=60 excluded (strict >)
    assert AG.run("How many curling events at the 1988 Winter Olympics had at least 60 competitors?", R, CFG)["value"] == "3"

def test_prose_is_never_parsed():
    o = AG.run("Which curling event at the 1988 Winter Olympics had the most competitors?", R, CFG)
    assert "Prose only" not in o["value"] and o["value"] == "Header doc"                    # 80 > 75 > 60; the 500 in prose is ignored

def test_superlative_ties_and_min_and_number():
    assert AG.run("Which event at the 1988 Winter Olympics had the most competitors?", R, CFG)["value"] == "Header doc"
    assert AG.run("Which event at the 1988 Winter Olympics had the fewest competitors?", R, CFG)["value"] == "Curling Men"
    T = AG.build_records([D("x", "A", games="G1", competitors=70), D("y", "B", games="G1", competitors=70), D("z", "C", games="G1", competitors=5)], CFG)
    assert AG.run("Which event at G1 had the most competitors?", T, CFG)["value"] == "A; B"       # tie -> candidate set
    assert AG.run("What was the highest number of competitors at G1?", T, CFG)["value"] == "70"

def test_not_answerable_returns_none():
    assert AG.run("Who won the 1988 Curling event?", R, CFG) is None
    assert AG.run("How many events had more than 5 competitors?", AG.build_records([D("p", "P")], CFG), CFG) is None

def test_provenance_and_reverify():
    from app.evidence.ledger import Ledger
    o = AG.run("How many curling events at the 1988 Winter Olympics had more than 60 competitors?", R, CFG)
    c = Ledger().add(req_id="R1", value=o["value"], claim_text=o["claim_text"], status="SUPPORTED", evidence_type="INFERENCE", sources=o["sources"], meta=o["meta"])
    assert all({"doc_id", "field", "value", "src", "quote"} <= set(s) for s in c.sources) and AG.reverify(c, R, CFG)
    c.value = "7"; assert not AG.reverify(c, R, CFG)                                            # tampered result fails
    c.value = o["value"]; c.sources[0]["value"] = "1"; assert not AG.reverify(c, R, CFG)        # tampered source field fails

@pytest.fixture(scope="module")
def ctx():
    from app.core.context import build_context
    c = build_context(load_config())
    for d in c.corpus_docs:                                                    # attach structured fields to the synthetic sample corpus (test fixture only)
        m = re.search(r"attracted (\d+) competitors", d["text"])
        if m: d["raw"]["competitors"] = int(m.group(1)); d["raw"]["sport"] = d["title"].split(" ", 1)[1]
    return c

def test_end_to_end_agentic_uses_deterministic_aggregate(ctx):
    from app.pipelines import agentic
    docs = [d for d in ctx.corpus_docs if "competitors" in d["raw"]]; thr = 60
    truth = sum(1 for d in docs if d["raw"]["competitors"] > thr)
    r = agentic.run(ctx, f"How many events had more than {thr} competitors?", "t"); t = r["trace"]
    assert "aggregate" in t["tool_sequence"] and t["stop_reason"] == "sufficient_evidence" and r["answer"].startswith(str(truth))
    c = [c for c in t["ledger"] if c["meta"].get("method") == "structured_aggregate"][0]
    assert c["status"] == "SUPPORTED" and c["evidence_type"] == "INFERENCE" and t["verification"]["failed"] == 0
    assert r["tokens"]["total"] > 0 and not any(o["name"] == "aggregate" for o in r["tokens"]["operations"])    # aggregate costs no LLM call

def test_aggregate_not_offered_for_lookup(ctx):
    from app.agents.orchestrator import Orchestrator
    from app.agents.harness import State
    from app.evidence.contract import Req
    st = State("Who won the 1990 Lumen Cup?", "t", "single_fact", [Req("R1", "entity", "winner", "w")]); o = Orchestrator(ctx); o.ctx_meter_total = 0
    j = {"gap_type": "ENTITY_GAP", "missing": ["R1"], "contradictions": [], "recommended_action": "entity_link"}
    assert "aggregate" not in [c["tool"] for c in o._candidates(st, j)]
