"""Heuristic failure taxonomy (first pass) + a CSV for the manual human audit. Refine labels by hand for the README."""
import json, csv, random, collections
from app.core.config import load_config, P
from benchmark.metrics import load

def label(r):
    if r.get("error"): return "FORMAT_ERROR"
    if not r.get("gold_in_context", True): return "GRAPH_MISS" if r["pipeline"] != "rag" and r.get("trace") and r["trace"].get("final_judge", {}).get("coverage", 1) == 0 else "RETRIEVAL_MISS"
    t = r.get("trace") or {}; qt = r.get("question_type") or t.get("question_type", "")
    if t.get("unresolved"): return "INCOMPLETE_ANSWER"
    if any(c["status"] == "CONTRADICTED" for c in t.get("ledger", [])): return "CONTRADICTION"
    if qt == "aggregation" or qt == "superlative": return "AGGREGATION_ERROR"
    if qt in ("multi_hop", "relationship", "comparison"): return "MULTI_HOP_BREAK"
    if qt == "temporal": return "TEMPORAL_ERROR"
    if not r.get("complete", True) and r.get("correct"): return "INCOMPLETE_ANSWER"
    return "WRONG_ENTITY"      # default bucket: verify manually (could be UNSUPPORTED_CLAIM)

def main():
    cfg = load_config(); out = {}
    for p in ("rag", "graphrag", "agentic"):
        rows = load(cfg, p)
        if rows: out[p] = dict(collections.Counter(label(r) for r in rows.values() if "correct" in r and not r["correct"]))
    json.dump(out, open(P(cfg["paths"]["results"]) / "failure_taxonomy.json", "w"), indent=1); print(json.dumps(out, indent=1))
    rows = load(cfg, "agentic") or load(cfg, "rag")
    if rows:
        random.seed(3); pick = random.sample([r for r in rows.values() if "correct" in r], min(20, len(rows)))
        with open(P(cfg["paths"]["results"]) / "manual_audit.csv", "w", newline="") as f:
            w = csv.writer(f); w.writerow(["id", "question", "answer", "llm_correct", "human_correct"])
            for r in pick: w.writerow([r["id"], r["question"], r["answer"][:300], r["correct"], ""])
        print("fill human_correct in results/manual_audit.csv then: python -m benchmark.evaluator --pipeline agentic --audit_csv results/manual_audit.csv")

if __name__ == "__main__": main()
