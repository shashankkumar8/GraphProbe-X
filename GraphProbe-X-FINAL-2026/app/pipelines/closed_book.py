import time
from app.core.meter import Meter
from .common import package

def run(ctx, question, qid=""):
    """CONTROL: no retrieval. Shows how much of the benchmark is answerable without the corpus (should be low)."""
    m, t0 = Meter(), time.time()
    ans = ctx.llm.chat("Answer the question concisely from your own knowledge. If you do not know, say so.", f"QUESTION: {question}", m, "answer",
                       max_out=ctx.cfg["llm"].get("answer_max_tokens", 300))
    return package("closed_book", qid, question, ans.strip(), [], m, t0, [], 0)
