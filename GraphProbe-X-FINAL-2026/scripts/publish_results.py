"""results/summary.json -> README results block + results/RESULTS.md + site/data/summary.json (static hosting). Numbers come ONLY from saved runs."""
import json, shutil, re
from app.core.config import load_config, P

def render(s):
    pp = s["pipelines"]; names = list(pp); cols = [("accuracy", "Accuracy"), ("completeness", "Completeness"), ("avg_tokens", "Avg tokens"), ("avg_latency_ms", "Avg latency (ms)"),
                                                  ("avg_citations", "Avg citations"), ("llm_calls", "LLM calls"), ("fallback_call_rate", "Fallback-call rate")]
    md = "| Metric | " + " | ".join(names) + " |\n|---|" + "---|" * len(names) + "\n" + "\n".join(f"| {lab} | " + " | ".join(str(pp[n].get(k)) for n in names) + " |" for k, lab in cols)
    a = s.get("agentic_vs_rag")
    if a: md += (f"\n\n**Agentic vs RAG** (n={a['n']}): rescued **{a['rescued']}**, regressed **{a['regressed']}**, avg Agentic Tax **{a['avg_agentic_tax_tokens']}** tokens, avg accuracy gain **{a['avg_accuracy_gain']}**, "
                 f"escalation yield **{a.get('escalation_yield')}**, unnecessary escalation **{a.get('unnecessary_escalation')}**, early-stop precision **{a.get('early_stop_precision')}**.")
    if "oracle" in s: md += f"\n\nOracle router (best of RAG/GraphRAG/Agentic): **{s['oracle']['oracle_best_of_3']}** vs actual Agentic **{s['oracle']['actual_agentic']}**."
    if "falsification" in s: md += f"\n\nFalsification test (distinct tool sequences on a diverse sample): **{s['falsification']['distinct_sequences']}** → {'PASS' if s['falsification']['passed'] else 'FAIL'}."
    return md + "\n\n_Generated from `results/summary.json`; every number traces to saved per-question runs._"

def main():
    cfg = load_config(); R = P(cfg["paths"]["results"]); s = json.load(open(R / "summary.json")); md = render(s); (R / "RESULTS.md").write_text(md, encoding="utf-8")
    rd = P("README.md"); t = rd.read_text(encoding="utf-8")
    t = re.sub(r"<!-- RESULTS:START -->.*<!-- RESULTS:END -->", lambda m: f"<!-- RESULTS:START -->\n{md}\n<!-- RESULTS:END -->", t, flags=re.S); rd.write_text(t, encoding="utf-8")
    (P("site") / "data").mkdir(parents=True, exist_ok=True); shutil.copy(R / "summary.json", P("site/data/summary.json"))
    if (R / "dashboard.html").exists(): shutil.copy(R / "dashboard.html", P("site/data/dashboard.html"))
    print("published: README block, results/RESULTS.md, site/data/summary.json")

if __name__ == "__main__": main()
