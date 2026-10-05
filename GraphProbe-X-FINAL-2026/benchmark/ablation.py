"""Fixed stratified subset (default 30, seed 7) x agentic variants. Report honestly even if a component does not matter."""
import argparse, json, random, collections
from app.core.config import load_config, P
from benchmark.runner import run_pipeline, VARIANTS
from benchmark.evaluator import evaluate
from benchmark.metrics import load, summarize

def main(n=30, workers=4):
    cfg = load_config(); full = load(cfg, "agentic") or {}
    by = collections.defaultdict(list)
    for i, r in full.items(): by[r.get("question_type", "?")].append(i)
    random.seed(7); ids = []
    while len(ids) < n and any(by.values()):
        for k in sorted(by):
            if by[k] and len(ids) < n: ids.append(by[k].pop(random.randrange(len(by[k]))))
    res = {}
    for v in VARIANTS:
        c = load_config(overrides=VARIANTS[v]); run_pipeline("agentic", "public", None, workers, v, True, ids, c); evaluate("agentic", v, workers, c)
        res[v] = summarize(load(c, "agentic", v)) | {"agentic": None}
    json.dump({"subset_ids": ids, "n": len(ids), "variants": res}, open(P(cfg["paths"]["results"]) / "ablation_results.json", "w"), indent=1)
    for v, s in res.items(): print(f"{v:12s} acc={s['accuracy']} tokens={s['avg_tokens']} latency={s['avg_latency_ms']}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=30); ap.add_argument("--workers", type=int, default=4); a = ap.parse_args(); main(a.n, a.workers)
