import time
from app.core.meter import Meter
from .common import synthesize, package

def run(ctx, question, qid=""):
    """CONTROL: identical to RAG but with k scaled so average tokens ~ Agentic (k set by benchmark.runner.matched_k). Asks: is adaptive
    investigation better than simply spending the same token budget on a bigger non-agentic context?"""
    k = ctx.cfg["rag_matched"]["k"]; assert k, "rag_matched.k unset (runner computes it from rag+agentic results)"
    m, t0, r = Meter(), time.time(), ctx.cfg["retrieval"]
    chunks = ctx.index.hybrid(question, k=k, cands=max(r["candidates"], 3 * k), rrf_k=r["rrf_k"])
    ans, cites, ct = synthesize(ctx, m, question, chunks)
    return package("rag_matched", qid, question, ans, cites, m, t0, chunks, ct, matched_k=k)
