"""python -m scripts.final_audit  -> integrity gate before submission (exit 1 on any FAIL)."""
import json, re, subprocess, sys, pathlib
from app.core.config import load_config, P
from app.core.util import sha
from app.evidence.verifier import verify_quote
from ingest.loader import read_jsonl

def main():
    cfg = load_config(); R = P(cfg["paths"]["results"]); bad = []
    def chk(ok, msg, warn=False):
        print(("PASS " if ok else ("WARN " if warn else "FAIL ")) + msg)
        if not ok and not warn: bad.append(msg)
    for f in ["README.md", "requirements.txt", "graph/schema.gsql", "graph/queries/entity_context.gsql", "app/agents/orchestrator.py", "docs/RUNBOOK.md"]: chk(P(f).exists(), f"file {f}")
    chk(cfg["graph"]["backend"] == "tigergraph", "final runs use TigerGraph backend", warn=True)
    chunks = {}
    pf = P(cfg["paths"]["processed"]) / "chunks.jsonl"
    if pf.exists():
        for l in open(pf, encoding="utf-8"): c = json.loads(l); chunks[c["chunk_id"]] = c
    nq = sum(1 for _ in read_jsonl(cfg["data"]["public"])) if pathlib.Path(cfg["data"]["public"]).exists() else 0
    for p in ("rag", "graphrag", "agentic"):
        f = R / f"{p}_results.json"; chk(f.exists(), f"{p}_results.json exists")
        if not f.exists(): continue
        rows = json.load(open(f))["results"]; chk(len(rows) == nq, f"{p}: {len(rows)}/{nq} public questions"); chk(not any(r.get("error") for r in rows), f"{p}: no errored rows")
        chk(not any(r["tokens"].get("estimated_usage") for r in rows), f"{p}: token usage from provider (not estimated)", warn=True)
        badc = [(r["id"], c) for r in rows for c in r["citations"] if c not in chunks]; chk(not badc, f"{p}: every citation resolves to a chunk ({len(badc)} bad)")
        if p == "agentic":
            nb = 0
            for r in rows:
                for c in (r.get("trace") or {}).get("ledger", []):
                    if c["status"] == "SUPPORTED" and c["evidence_type"] != "INFERENCE" and c["sources"]:
                        s = c["sources"][0]; nb += 0 if s["chunk_id"] in chunks and verify_quote(s["quote"], chunks[s["chunk_id"]]["text"])[0] else 1
            chk(nb == 0, f"agentic: every SUPPORTED quote re-verifies ({nb} failures)")
    sm = R / "summary.json"; chk(sm.exists(), "summary.json exists"); 
    if sm.exists(): chk(json.load(open(sm)).get("falsification", {}).get("passed", False), "falsification test passed (>=3 distinct tool sequences)")
    ho = R / "hidden_set_output.json"; chk(ho.exists(), "hidden_set_output.json exists")
    if ho.exists():
        nh = sum(1 for _ in read_jsonl(cfg["data"]["hidden"])); h = json.load(open(ho)); chk(len(h["questions"]) == nh, f"hidden: {len(h['questions'])}/{nh} answered")
        chk(h["manifest"]["corpus_hash"] == sha(cfg["data"]["corpus"]), "hidden manifest corpus hash matches")
    chk(".env" in open(P(".gitignore")).read(), ".env is git-ignored")
    leaks = [str(f) for f in P("").rglob("*") if f.is_file() and f.suffix in (".py", ".md", ".yaml", ".json", ".txt", ".sh") and "results" not in f.parts and "cache" not in f.parts
             and re.search(r"sk-(or-)?[A-Za-z0-9_-]{24,}", f.read_text(errors="ignore"))]
    chk(not leaks, f"no API keys in repo {leaks}")
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests"], capture_output=True, text=True); chk(r.returncode == 0, "unit tests pass")
    print("\nAUDIT:", "FAIL" if bad else "PASS"); sys.exit(1 if bad else 0)

if __name__ == "__main__": main()
