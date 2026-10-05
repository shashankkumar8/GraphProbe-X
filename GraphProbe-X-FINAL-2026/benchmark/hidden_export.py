"""Freeze -> run hidden set -> export. NEVER tune with hidden data. Adapt `export()` keys to the organisers' exact format if they publish one."""
import json, hashlib, argparse
from app.core.config import load_config, P
from app.core.util import sha
from benchmark.runner import run_pipeline, out_path

def manifest(cfg):
    h = hashlib.sha256()
    for f in ["configs/config.yaml", "app/core/prompts.py", "app/agents/orchestrator.py"]: h.update(open(P(f), "rb").read())
    return {"code_config_prompts_hash": h.hexdigest()[:16], "corpus_hash": sha(cfg["data"]["corpus"]), "graph_backend": cfg["graph"]["backend"],
            "embedder": json.load(open(P(cfg["paths"]["processed"]) / "index_meta.json"))["embedder"], "agentic_params": cfg["agentic"]}

def export(cfg=None):
    cfg = cfg or load_config(); out = {"manifest": manifest(cfg), "questions": []}; per = {}
    for p in ("rag", "graphrag", "agentic"):
        per[p] = {r["id"]: r for r in json.load(open(out_path(cfg, p, "hidden", "full")))["results"]}
    for qid, a in per["agentic"].items():
        out["questions"].append({"id": qid, "question": a["question"], "answer": a["answer"], "tokens": a["tokens"], "agentic_trace": a.get("trace"),
                                 "citations": a["citations"], "baselines": {p: {"answer": per[p][qid]["answer"], "tokens": per[p][qid]["tokens"]} for p in ("rag", "graphrag") if qid in per[p]}})
    dst = P(cfg["paths"]["results"]) / "hidden_set_output.json"; json.dump(out, open(dst, "w"), indent=1, ensure_ascii=False); print("wrote", dst, len(out["questions"]), "questions")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--run", action="store_true", help="run all 3 pipelines on hidden first"); ap.add_argument("--workers", type=int, default=4); a = ap.parse_args()
    if a.run:
        for p in ("rag", "graphrag", "agentic"): run_pipeline(p, "hidden", None, a.workers)
    export()
