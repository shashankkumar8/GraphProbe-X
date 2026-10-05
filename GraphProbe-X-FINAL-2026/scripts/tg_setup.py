"""Create schema, load graph.json (entities, chunks, MENTIONS, HAS_CHUNK), install query, run a gate test.
python -m scripts.tg_setup [--skip-schema] [--test-only]. If gsql() fails on your TG version, paste graph/schema.gsql and
graph/queries/entity_context.gsql into the Savanna GSQL editor, then re-run with --skip-schema."""
import os, sys, json, argparse
from app.core.config import load_config, P

def conn():
    import pyTigerGraph as tg
    c = tg.TigerGraphConnection(host=os.environ["TG_HOST"], graphname=os.environ.get("TG_GRAPH", "GraphProbeX"),
                                username=os.environ.get("TG_USER", "tigergraph"), password=os.environ.get("TG_PASS", ""))
    if os.environ.get("TG_SECRET"): c.getToken(os.environ["TG_SECRET"])
    return c

def batches(x, n=4000):
    for i in range(0, len(x), n): yield x[i:i + n]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--skip-schema", action="store_true"); ap.add_argument("--test-only", action="store_true"); a = ap.parse_args()
    cfg = load_config(); proc = P(cfg["paths"]["processed"]); c = conn()
    if not a.test_only:
        if not a.skip_schema:
            print(c.gsql(open(P("graph/schema.gsql")).read())); print(c.gsql(open(P("graph/queries/entity_context.gsql")).read() + "\nINSTALL QUERY entity_context"))
        gd = json.load(open(proc / "graph.json")); chunks = [json.loads(l) for l in open(proc / "chunks.jsonl", encoding="utf-8")]
        docs = {ch["doc_id"]: ch["title"] for ch in chunks}
        for b in batches(list(docs.items())): c.upsertVertices("Document", [(d, {"title": t}) for d, t in b])
        for b in batches(chunks): c.upsertVertices("Chunk", [(x["chunk_id"], {"doc_id": x["doc_id"], "section": x["section"]}) for x in b])
        for b in batches(list(gd["entities"].items())): c.upsertVertices("Entity", [(e, {"name": m["name"], "etype": m["etype"], "df": m["df"]}) for e, m in b])
        for b in batches(chunks): c.upsertEdges("Document", "HAS_CHUNK", "Chunk", [(x["doc_id"], x["chunk_id"], {}) for x in b])
        edges = [(cid, e, {"extraction_method": "rule:capitalised-span|year|title", "confidence": 0.8}) for cid, es in gd["chunk2ents"].items() for e in es]
        for b in batches(edges, 5000): c.upsertEdges("Chunk", "MENTIONS", "Entity", b)
        print("loaded", c.getVertexCount("*"), c.getEdgeCount("*"))
    gd = json.load(open(proc / "graph.json")); e = max(gd["entities"], key=lambda k: gd["entities"][k]["df"] if gd["entities"][k]["df"] < 50 else 0)
    r = c.runInstalledQuery("entity_context", {"ents": [e], "hops": 2, "hub_df": cfg["graph"]["hub_df"], "k": 20})
    print("GATE D: entity", e, "->", len(r[0].get("Top", [])), "chunks;", "PASS" if r[0].get("Top") else "FAIL")

if __name__ == "__main__": main()
