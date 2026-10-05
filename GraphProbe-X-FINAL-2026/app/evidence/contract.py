from dataclasses import dataclass, asdict
from app.core import prompts as PR
from app.core.util import parse_json

@dataclass
class Req:
    req_id: str; type: str; slot: str; description: str; required: bool = True

def analyze(llm, meter, question):
    """Question Analyzer -> (Evidence Contract, question_type, entities). Cheap LLM call, temp 0, validated strictly."""
    raw = llm.chat(PR.JSON_SYSTEM, PR.ANALYZE.format(qtypes=PR.QTYPES, question=question), meter, "analyze", json_mode=True)
    js = parse_json(raw) or {}
    reqs = []
    for i, r in enumerate((js.get("requirements") or [])[:5], 1):
        t = r.get("type") if r.get("type") in ("entity", "attribute", "relation") else "attribute"
        reqs.append(Req(f"R{i}", t, str(r.get("slot") or f"slot{i}"), str(r.get("description") or r.get("slot") or question), bool(r.get("required", True))))
    if not reqs: reqs = [Req("R1", "attribute", "answer", question, True)]
    qt = js.get("question_type") if js.get("question_type") in PR.QTYPES else "single_fact"
    return reqs, qt, [str(e) for e in (js.get("entities") or [])][:8]

def contract_json(reqs): return {"requirements": [asdict(r) for r in reqs]}
