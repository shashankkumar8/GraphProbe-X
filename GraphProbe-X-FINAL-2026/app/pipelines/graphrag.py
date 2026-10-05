import time
from app.core.meter import Meter
from .common import synthesize, package

def run(ctx, question, qid=""):
    """Pipeline B: FIXED GraphRAG. entity link -> fixed top-K vector -> fixed-hop TigerGraph traversal -> merge/dedup -> LLM.
    Deliberately NO retry, NO branching, NO fallback (adaptivity belongs exclusively to Pipeline C)."""
    m, t0, g, r = Meter(), time.time(), ctx.cfg["graphrag"], ctx.cfg["retrieval"]
    vec = ctx.index.hybrid(question, k=g["vector_k"], cands=r["candidates"], rrf_k=r["rrf_k"])
    seeds = ctx.gd.link_text(question)
    cand = ctx.graph.entity_context(seeds) if seeds else []
    have = {c["chunk_id"] for c in vec}
    gr = ctx.index.rank_within([x["chunk_id"] for x in cand], question, k=g["graph_k"], exclude=have)
    chunks = vec + gr
    ans, cites, ct = synthesize(ctx, m, question, chunks)
    paths = {c["chunk_id"]: ctx.gd.explain_path(c["chunk_id"], seeds) for c in gr}
    return package("graphrag", qid, question, ans, cites, m, t0, chunks, ct,
                   trace={"seeds": [ctx.gd.entities[e]["name"] for e in seeds], "graph_candidates": len(cand), "graph_paths": paths})
