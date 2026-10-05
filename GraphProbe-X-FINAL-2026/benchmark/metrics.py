"""Aggregates raw results + eval files into results/summary.json (all numbers come from real runs)."""
import json, collections, statistics as S
from app.core.config import load_config, P
from benchmark.runner import out_path

def load(cfg, pipe, variant="full"):
    f = out_path(cfg, pipe, "public", variant)
    if not f.exists(): return None
    rows = {r["id"]: r for r in json.load(open(f))["results"]}
    ef = f.with_name(f.stem.replace("_results", "") + "_eval.json")
    if ef.exists():
        for e in json.load(open(ef)): rows[e["id"]].update(e)
    return rows

def mean(x): x = list(x); return round(S.mean(x), 4) if x else None

def summarize(rows):
    R = list(rows.values()); ok = [r for r in R if "correct" in r]; ops = [o for r in R for o in r["tokens"].get("operations", [])]
    return {"n": len(R), "errors": sum(1 for r in R if r.get("error")),
            "accuracy": mean(r["correct"] for r in ok), "completeness": mean(r["complete"] for r in ok), "em": mean(r["em"] for r in ok),
            "f1": mean(r["f1"] for r in ok), "gold_in_context": mean(r["gold_in_context"] for r in ok),
            "avg_tokens": mean(r["tokens"]["total"] for r in R), "avg_input_tokens": mean(r["tokens"]["input"] for r in R),
            "avg_output_tokens": mean(r["tokens"]["output"] for r in R), "avg_latency_ms": mean(r["latency_ms"] for r in R),
            "avg_citations": mean(len(r["citations"]) for r in R), "avg_chunks": mean(r["n_chunks"] for r in R),
            "llm_calls": mean(len(r["tokens"].get("operations", [])) for r in R), "cached_call_rate": mean(1 if o.get("cached") else 0 for o in ops),
            "fallback_call_rate": mean(1 if o.get("provider") == "fallback" else 0 for o in ops), "judge_free_rate": mean(0 if r.get("judge_used", True) else 1 for r in ok)}

def agentic_extras(rows):
    R = [r for r in rows.values() if r.get("trace")]
    if not R: return {}
    T = [r["trace"] for r in R]; tools = collections.Counter(t for x in T for t in x["tool_sequence"] if t != "initial_retrieval")
    seqs = [tuple(x["tool_sequence"]) for x in T]
    return {"avg_actions": mean(x["n_actions"] for x in T), "avg_strategy_changes": mean(x["strategy_changes"] for x in T),
            "fallback_rate": mean(1 if x["fallbacks"] else 0 for x in T), "escalation_rate": mean(1 if x["n_actions"] > 0 else 0 for x in T),
            "early_stop_rate": mean(1 if x["n_actions"] == 0 else 0 for x in T), "stop_reasons": dict(collections.Counter(x["stop_reason"] for x in T)),
            "tool_usage": dict(tools), "avg_final_coverage": mean(x["final_judge"]["coverage"] for x in T),
            "distinct_tool_sequences": len(set(seqs)), "unresolved_rate": mean(1 if x["unresolved"] else 0 for x in T)}

def falsification(rows, n=10):
    """Must pass before calling the system 'agentic': tool-call sequences over a diverse sample must not all be identical."""
    R = [r for r in rows.values() if r.get("trace")]; by = collections.defaultdict(list)
    for r in R: by[r["trace"]["question_type"]].append(r)
    pick = []; 
    while len(pick) < min(n, len(R)) and any(by.values()):
        for k in list(by):
            if by[k] and len(pick) < n: pick.append(by[k].pop(0))
    seqs = {tuple(r["trace"]["tool_sequence"]) for r in pick}
    return {"sample": len(pick), "distinct_sequences": len(seqs), "passed": len(seqs) >= 3, "sequences": [list(s) for s in seqs]}

def compare(cfg=None):
    cfg = cfg or load_config(); D = {p: load(cfg, p) for p in ("closed_book", "rag", "rag_matched", "graphrag", "agentic")}; D = {k: v for k, v in D.items() if v}
    out = {"pipelines": {p: summarize(r) for p, r in D.items()}}
    if "agentic" in D: out["agentic"] = agentic_extras(D["agentic"]); out["falsification"] = falsification(D["agentic"])
    if "agentic" in D and "rag" in D:
        common = [i for i in D["agentic"] if i in D["rag"] and "correct" in D["agentic"][i] and "correct" in D["rag"][i]]
        tax = [D["agentic"][i]["tokens"]["total"] - D["rag"][i]["tokens"]["total"] for i in common]
        gain = [int(D["agentic"][i]["correct"]) - int(D["rag"][i]["correct"]) for i in common]
        qt = {i: D["agentic"][i].get("question_type", "?") for i in common}
        rescued = sum(1 for g in gain if g > 0); broke = sum(1 for g in gain if g < 0)
        tr = lambda i: D["agentic"][i].get("trace") or {}
        esc = [i for i in common if tr(i).get("n_actions", 0) > 0]; early = [i for i in common if tr(i).get("n_actions", 0) == 0]
        ag, rg = (lambda i: bool(D["agentic"][i]["correct"])), (lambda i: bool(D["rag"][i]["correct"]))
        extra = {"escalation_yield": mean(1 if ag(i) and not rg(i) else 0 for i in esc), "unnecessary_escalation": mean(1 if rg(i) else 0 for i in esc),
                 "early_stop_precision": mean(1 if ag(i) else 0 for i in early), "n_escalated": len(esc), "n_early_stop": len(early)}
        out["agentic_vs_rag"] = extra | {"n": len(common), "avg_agentic_tax_tokens": mean(tax), "avg_accuracy_gain": mean(gain), "rescued": rescued, "regressed": broke,
                                 "accuracy_gain_per_1k_extra_tokens": round(1000 * (mean(gain) or 0) / (mean(tax) or 1), 4) if mean(tax) else None,
                                 "per_question": [{"id": i, "type": qt[i], "tax": t, "gain": g} for i, t, g in zip(common, tax, gain)]}
        per = collections.defaultdict(lambda: collections.defaultdict(list))
        for i in common:
            for p in D: 
                if i in D[p] and "correct" in D[p][i]: per[qt[i]][p].append(int(D[p][i]["correct"]))
        out["accuracy_by_type"] = {t: {p: mean(v) for p, v in d.items()} | {"n": len(next(iter(d.values())))} for t, d in per.items()}
        core = [p for p in ("rag", "graphrag", "agentic") if p in D]
        best = [max(int(D[p][i]["correct"]) for p in core if i in D[p] and "correct" in D[p][i]) for i in common]
        out["oracle"] = {"actual_agentic": mean(int(D["agentic"][i]["correct"]) for i in common), "oracle_best_of_3": mean(best),
                         "note": "gap = routing/stopping loss vs. a perfect router; oracle itself bounds what better retrieval could give"}
        bins = collections.defaultdict(list)
        for i in common:
            c = D["agentic"][i].get("confidence", 0); bins["<0.5" if c < .5 else "0.5-0.8" if c < .8 else ">=0.8"].append(int(D["agentic"][i]["correct"]))
        out["calibration"] = {b: {"n": len(v), "accuracy": mean(v)} for b, v in bins.items()}
    dst = P(cfg["paths"]["results"]) / "summary.json"; json.dump(out, open(dst, "w"), indent=1); return out

if __name__ == "__main__":
    o = compare(); print(json.dumps({k: v for k, v in o.items() if k not in ("agentic_vs_rag",)}, indent=1)[:3500])
