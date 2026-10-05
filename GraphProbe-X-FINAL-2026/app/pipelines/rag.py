import time
from app.core.meter import Meter
from .common import synthesize, package

def run(ctx, question, qid=""):
    """Pipeline A: strong hybrid RAG (BM25 + dense -> RRF -> dedup -> top-K). No graph, no loop."""
    m, t0, r = Meter(), time.time(), ctx.cfg["retrieval"]
    chunks = ctx.index.hybrid(question, k=r["k"], cands=r["candidates"], rrf_k=r["rrf_k"])
    ans, cites, ct = synthesize(ctx, m, question, chunks)
    return package("rag", qid, question, ans, cites, m, t0, chunks, ct)
