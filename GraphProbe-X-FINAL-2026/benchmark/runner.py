"""python -m benchmark.runner --pipeline rag|graphrag|agentic --split public|hidden [--limit N] [--workers 4] [--variant full] [--force]
Results are immutable: an existing final file is never overwritten without --force. Partial progress is resumable."""
import argparse, json, sys, pathlib, importlib
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from app.core.config import load_config, P
from app.core.context import build_context
from ingest.loader import load_questions

VARIANTS = {"full": {}, "no_judge": {"agentic": {"judge_mode": "heuristic"}},
            "no_hardstop": {"agentic": {"max_steps": 12, "max_tokens": 10**9, "patience": 10**9}},
            "no_graph": {"agentic": {"disabled_tools": ["graph_traverse"]}}, "no_memory": {"agentic": {"use_memory": False}}}

def out_path(cfg, pipeline, split, variant):
    r = P(cfg["paths"]["results"]); r.mkdir(parents=True, exist_ok=True)
    if variant != "full": (r / "ablation").mkdir(exist_ok=True); return r / "ablation" / f"agentic_{variant}.json"
    return r / (f"{pipeline}_results.json" if split == "public" else f"hidden_{pipeline}.json")

PIPES = ["closed_book", "rag", "rag_matched", "graphrag", "agentic"]

def matched_k(cfg):
    """k for RAG-matched: scale RAG's k by agentic_avg_tokens / rag_avg_tokens (approximation; the achieved average is reported)."""
    import statistics as S
    g = lambda p: [r["tokens"]["total"] for r in json.load(open(out_path(cfg, p, "public", "full")))["results"] if not r.get("error")]
    return int(max(cfg["retrieval"]["k"], min(40, round(cfg["retrieval"]["k"] * S.mean(g("agentic")) / S.mean(g("rag"))))))

def run_pipeline(pipeline, split="public", limit=None, workers=4, variant="full", force=False, ids=None, cfg=None):
    cfg = cfg or load_config(overrides=VARIANTS[variant]); fin = out_path(cfg, pipeline, split, variant)
    if fin.exists() and not force: sys.exit(f"{fin} exists (results are immutable). Use --force to overwrite.")
    if pipeline == "rag_matched" and not cfg["rag_matched"]["k"]: cfg["rag_matched"]["k"] = matched_k(cfg); print("rag_matched k =", cfg["rag_matched"]["k"])
    ctx = build_context(cfg); mod = importlib.import_module(f"app.pipelines.{pipeline}")
    qs = load_questions(cfg, split)
    if split == "hidden" and any(q["gold"] is not None for q in qs): sys.exit("hidden file contains answer-like fields; refusing (never tune on hidden).")
    if ids: qs = [q for q in qs if q["id"] in set(ids)]
    if limit: qs = qs[:limit]
    part = fin.with_suffix(".partial.jsonl"); done = {}
    if part.exists() and not force:
        for l in open(part, encoding="utf-8"):
            r = json.loads(l)
            if not r.get("error"): done[r["id"]] = r       # errored rows are retried on resume
    todo = [q for q in qs if q["id"] not in done]
    def work(q):
        try: r = mod.run(ctx, q["question"], q["id"])
        except Exception as e: r = {"id": q["id"], "question": q["question"], "pipeline": pipeline, "answer": "", "citations": [], "error": repr(e),
                                   "tokens": {"input": 0, "output": 0, "total": 0, "context_est": 0, "operations": []}, "latency_ms": 0, "n_chunks": 0, "context_chunk_ids": []}
        return r
    with open(part, "a", encoding="utf-8") as pf, ThreadPoolExecutor(workers) as ex:
        for r in tqdm(ex.map(work, todo), total=len(todo), desc=f"{pipeline}/{variant}/{split}"):
            done[r["id"]] = r; pf.write(json.dumps(r, ensure_ascii=False) + "\n"); pf.flush()
    rows = [done[q["id"]] for q in qs if q["id"] in done]
    json.dump({"pipeline": pipeline, "variant": variant, "split": split, "model": getattr(ctx.llm, "model", "?"), "n": len(rows), "results": rows},
              open(fin, "w"), ensure_ascii=False, indent=1)
    part.unlink(missing_ok=True); print(f"saved {fin} ({len(rows)} rows, errors: {sum(1 for r in rows if r.get('error'))})"); return fin

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pipeline", required=True, choices=PIPES); ap.add_argument("--split", default="public")
    ap.add_argument("--limit", type=int); ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--variant", default="full", choices=list(VARIANTS)); ap.add_argument("--force", action="store_true")
    a = ap.parse_args(); run_pipeline(a.pipeline, a.split, a.limit, a.workers, a.variant, a.force)
