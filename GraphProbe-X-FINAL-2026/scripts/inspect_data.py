"""PHASE 1 gate: python -m scripts.inspect_data  -> prints schema, samples, stats; writes data manifest + question_taxonomy.csv (with --taxonomy)."""
import json, sys, csv, re, statistics as S, collections
from app.core.config import load_config, P
from app.core.util import sha
from ingest.loader import read_jsonl, load_corpus, load_questions

RULES = [("aggregation", r"\bhow many\b|\bnumber of\b|\bcount\b|\btotal\b"),
         ("superlative", r"\b(most|highest|largest|fewest|lowest|smallest|oldest|youngest|longest|shortest|maximum|minimum|biggest)\b"),
         ("temporal", r"\b(before|after|previous|preceding|prior|next|following|earlier|later|prev)\b|\bedition\b")]
def rule_type(q):
    """1) dataset-provided label  2) deterministic regex (heuristic!)  3) None -> LLM only for these."""
    for k in ("type", "qtype", "category", "question_type", "reasoning_type", "level"):
        if q["raw"].get(k): return str(q["raw"][k]), "dataset"
    for name, pat in RULES:
        if re.search(pat, q["question"].lower()): return name, "rule"
    ql = q["question"].lower().split()
    if len(ql) <= 12 and ql and ql[0] in ("who", "what", "which", "where", "when", "in"): return "lookup", "rule"     # short single-clause wh-question (heuristic)
    return None, "unresolved"

def main():
    cfg = load_config(); d = cfg["data"]; docs = load_corpus(cfg)
    first = next(read_jsonl(d["corpus"])); print("corpus keys:", list(first)); print("docs:", len(docs)); L = [len(x["text"].split()) for x in docs]
    print(f"words/doc median {S.median(L):.0f} max {max(L)} total {sum(L)}")
    for x in docs[:3]: print("---", x["doc_id"], x["title"], "\n", x["text"][:400])
    for s in ("public", "hidden"):
        qs = load_questions(cfg, s); print(f"\n{s}: {len(qs)} questions; keys: {list(qs[0]['raw'])}")
        for q in qs[:8]: print(" -", q["id"], q["question"][:140], "=>", str(q["gold"])[:80])
    man = {"corpus_hash": sha(d["corpus"]), "public_hash": sha(d["public"]), "hidden_hash": sha(d["hidden"]), "n_docs": len(docs)}
    P(cfg["paths"]["processed"]).mkdir(parents=True, exist_ok=True); json.dump(man, open(P(cfg["paths"]["processed"]) / "dataset_manifest.json", "w"), indent=1); print(man)
    if "--taxonomy" in sys.argv or "--rules-only" in sys.argv:
        from app.core.llm import get_llm; from app.core.meter import Meter; from app.evidence.contract import analyze
        llm = get_llm(cfg); rows = []; nllm = 0
        for q in load_questions(cfg, "public"):
            qt, how = rule_type(q); ents, slots = [], ""
            if qt is None:                       # only genuinely unresolved questions cost an LLM call (cached by the gateway)
                reqs, qt, ents = analyze(llm, Meter(), q["question"]); slots = "|".join(r.slot for r in reqs); how = "llm"; nllm += 1
            rows.append([q["id"], qt, how, "|".join(ents), slots, q["question"]])
        with open(P(cfg["paths"]["processed"]) / "question_taxonomy.csv", "w", newline="", encoding="utf-8") as f: w = csv.writer(f); w.writerow(["id", "type", "method", "entities", "slots", "question"]); w.writerows(rows)
        print(collections.Counter(r[1] for r in rows), "methods:", collections.Counter(r[2] for r in rows), "LLM calls:", nllm)

if __name__ == "__main__": main()
