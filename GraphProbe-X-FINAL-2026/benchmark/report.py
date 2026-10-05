"""results/summary.json -> results/dashboard.html (self-contained, charts embedded). python -m benchmark.report"""
import json, io, base64, html
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from app.core.config import load_config, P
from benchmark.metrics import compare

def img():
    b = io.BytesIO(); plt.tight_layout(); plt.savefig(b, format="png", dpi=110); plt.close(); return f'<img src="data:image/png;base64,{base64.b64encode(b.getvalue()).decode()}"/>'

def main():
    cfg = load_config(); s = compare(cfg); pp = s["pipelines"]; h = ["<h1>GraphProbe-X — metrics dashboard</h1><p>All numbers are computed from saved runs in results/.</p>"]
    cols = ["accuracy", "completeness", "avg_tokens", "llm_calls", "fallback_call_rate", "cached_call_rate", "avg_input_tokens", "avg_output_tokens", "avg_latency_ms", "avg_citations", "gold_in_context", "f1", "em"]
    h.append("<h2>Three-way comparison</h2><table><tr><th>metric</th>" + "".join(f"<th>{p}</th>" for p in pp) + "</tr>" +
             "".join(f"<tr><td>{c}</td>" + "".join(f"<td>{pp[p].get(c)}</td>" for p in pp) + "</tr>" for c in cols) + "</table>")
    plt.figure(figsize=(5, 3.6))
    for p, v in pp.items():
        if v["accuracy"] is not None: plt.scatter(v["avg_tokens"], v["accuracy"], s=90); plt.annotate(p, (v["avg_tokens"], v["accuracy"]), textcoords="offset points", xytext=(6, 4))
    plt.xlabel("avg total tokens / question"); plt.ylabel("accuracy"); plt.title("Cost-accuracy"); h.append(img())
    if "agentic_vs_rag" in s:
        a = s["agentic_vs_rag"]; types = sorted({x["type"] for x in a["per_question"]}); plt.figure(figsize=(5.4, 3.8))
        for t in types:
            xs = [x["tax"] for x in a["per_question"] if x["type"] == t]; ys = [x["gain"] for x in a["per_question"] if x["type"] == t]; plt.scatter(xs, ys, label=t, alpha=.7)
        plt.axhline(0, c="gray", lw=.5); plt.xlabel("Agentic Tax (agentic - RAG tokens)"); plt.ylabel("Accuracy Gain (-1/0/+1)"); plt.legend(fontsize=6); plt.title("Tax vs Gain by question type"); h.append(img())
        h.append(f"<p>Rescued by agentic: <b>{a['rescued']}</b> · regressed: <b>{a['regressed']}</b> · avg tax: <b>{a['avg_agentic_tax_tokens']}</b> tokens · avg gain: <b>{a['avg_accuracy_gain']}</b> · gain per 1k extra tokens: <b>{a['accuracy_gain_per_1k_extra_tokens']}</b> <i>(our own metrics)</i></p>")
        o = s["oracle"]; plt.figure(figsize=(4.4, 3.2)); plt.bar(["agentic", "oracle best-of-3"], [o["actual_agentic"], o["oracle_best_of_3"]], color=["#4477aa", "#ccbb44"]); plt.ylabel("accuracy"); plt.title("Oracle analysis"); h.append(img())
        if s.get("calibration"):
            plt.figure(figsize=(4.4, 3.2)); b = s["calibration"]; plt.bar(list(b), [v["accuracy"] or 0 for v in b.values()]); plt.ylabel("actual accuracy"); plt.xlabel("reported confidence"); plt.title("Calibration"); h.append(img())
        h.append("<h2>Accuracy by question type</h2><pre>" + html.escape(json.dumps(s["accuracy_by_type"], indent=1)) + "</pre>")
    if "agentic" in s:
        e = s["agentic"]; plt.figure(figsize=(4.6, 3.2)); plt.bar(list(e["stop_reasons"]), list(e["stop_reasons"].values())); plt.xticks(rotation=25, fontsize=7); plt.title("Stop reasons"); h.append(img())
        h.append("<h2>Agentic behaviour</h2><pre>" + html.escape(json.dumps(e, indent=1)) + "</pre><h2>Falsification test</h2><pre>" + html.escape(json.dumps(s["falsification"], indent=1)) + "</pre>")
    for name, title in (("ablation_results.json", "Ablation"), ("failure_taxonomy.json", "Failure taxonomy")):
        f = P(cfg["paths"]["results"]) / name
        if f.exists(): h.append(f"<h2>{title}</h2><pre>" + html.escape(json.dumps(json.load(open(f)), indent=1)[:4000]) + "</pre>")
    css = "<style>body{font-family:system-ui;max-width:980px;margin:2rem auto;padding:0 1rem}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:4px 10px}img{max-width:48%}pre{background:#f6f6f6;padding:8px;overflow:auto}</style>"
    dst = P(cfg["paths"]["results"]) / "dashboard.html"; dst.write_text(css + "\n".join(h), encoding="utf-8"); print("wrote", dst)

if __name__ == "__main__": main()
