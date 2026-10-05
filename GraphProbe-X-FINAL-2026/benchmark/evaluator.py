"""python -m benchmark.evaluator --pipeline rag [--variant full]  -> results/<pipeline>_eval.json (separate file; raw results untouched)
Same judge prompt/model for all pipelines + deterministic metrics (normalised EM, token-F1, gold-in-context)."""
import argparse, json, collections, re
from concurrent.futures import ThreadPoolExecutor
from app.core.config import load_config, P
from app.core.llm import get_llm
from app.core import prompts as PR
from app.core.util import norm, toks, parse_json
from benchmark.runner import out_path

def golds(g): return [str(x) for x in g] if isinstance(g, (list, tuple)) else [str(g)]
def f1(pred, gold):
    p, g = toks(norm(pred)), toks(norm(gold)); c = collections.Counter(p) & collections.Counter(g); n = sum(c.values())
    if not n: return 0.0
    pr, rc = n / len(p), n / len(g); return 2 * pr * rc / (pr + rc)

def accepted(q, overrides):
    """Acceptable strings for a question: gold + dataset aliases + data/processed/accepted_answers.json (qid -> list; build it from the corpus for
    multi-hop 'any event at that venue/date' and team events 'any member of the gold team' -- deterministic, never LLM-decided)."""
    base = golds(q["gold"]); extra = list(overrides.get(q["id"], []))
    for k in ("accepted_answers", "alt_answers", "aliases", "acceptable_answers", "team_members"):
        if q["raw"].get(k): extra += golds(q["raw"][k])
    return base, list(dict.fromkeys(base + extra))

def det_match(pred, base, acc, mode):
    hit = lambda a: re.search(rf"(?<!\w){re.escape(norm(a))}(?!\w)", norm(pred)) is not None
    return all(hit(b) for b in base) if mode == "all" and len(base) > 1 else any(hit(a) for a in acc)

def evaluate(pipeline, variant="full", workers=4, cfg=None):
    cfg = cfg or load_config(); llm = get_llm(cfg); fin = out_path(cfg, pipeline, "public", variant)
    data = json.load(open(fin)); from ingest.loader import load_questions
    Q = {q["id"]: q for q in load_questions(cfg, "public")}; mode = cfg["eval"]["gold_list_semantics"]
    ov = P(cfg["paths"]["processed"]) / "accepted_answers.json"; ov = json.load(open(ov)) if ov.exists() else {}
    chunks = {}
    for l in open(P(cfg["paths"]["processed"]) / "chunks.jsonl", encoding="utf-8"): c = json.loads(l); chunks[c["chunk_id"]] = norm(c["text"])
    def one(r):
        q = Q[r["id"]]; base, gl = accepted(q, ov); pred = r.get("answer", "")
        ctx_ids = r.get("context_chunk_ids_all") or r.get("context_chunk_ids", [])
        gic = any(norm(x) in " ".join(chunks.get(i, "") for i in ctx_ids) for x in gl)
        em = any(norm(x) == norm(pred) for x in gl); tf = max(f1(pred, x) for x in gl)
        if det_match(pred, base, gl, mode):
            return {"id": r["id"], "correct": True, "complete": True, "judge_reason": "deterministic accepted-answer match", "judge_used": False, "em": em, "f1": round(tf, 3), "gold_in_context": gic}
        js = parse_json(llm.chat(PR.JSON_SYSTEM, PR.JUDGE.format(question=r["question"], gold=" | ".join(gl), pred=pred), None, "judge", json_mode=True, max_out=150)) or {}
        cor = bool(js.get("correct")); return {"id": r["id"], "correct": cor, "complete": bool(js.get("complete")) and cor, "judge_reason": js.get("reason", ""), "judge_used": True,
                                               "em": em, "f1": round(tf, 3), "gold_in_context": gic}
    with ThreadPoolExecutor(workers) as ex: ev = list(ex.map(one, data["results"]))
    dst = fin.with_name(fin.stem.replace("_results", "") + "_eval.json"); json.dump(ev, open(dst, "w"), indent=1); print("saved", dst)
    return dst

def agreement(csv_path):
    """Human audit: CSV with columns id, llm_correct, human_correct (true/false) -> agreement rate."""
    import pandas as pd
    d = pd.read_csv(csv_path).dropna(subset=["human_correct"]); a = (d["llm_correct"].astype(str).str.lower() == d["human_correct"].astype(str).str.lower()).mean()
    print(f"human/LLM-judge agreement: {a:.1%} on {len(d)} rows"); return a

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--pipeline", required=True); ap.add_argument("--variant", default="full"); ap.add_argument("--audit_csv")
    a = ap.parse_args(); agreement(a.audit_csv) if a.audit_csv else evaluate(a.pipeline, a.variant)
