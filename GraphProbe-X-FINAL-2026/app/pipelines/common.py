import re, time
from app.core import prompts as PR
from app.core.util import est_tokens

def fmt_chunks(chunks, max_words=None):
    out = []
    for c in chunks:
        t = c["text"]
        if max_words: t = " ".join(t.split()[:max_words])
        out.append(f"[{c['chunk_id']}] {t}")
    return "\n\n".join(out)

def synthesize(ctx, meter, question, chunks, extra=""):
    """IDENTICAL answer step for all three pipelines (same prompt, same rules, same model)."""
    ev = fmt_chunks(chunks)
    ans = ctx.llm.chat(PR.ANSWER_SYSTEM, f"QUESTION: {question}\n\n{extra}EVIDENCE:\n{ev}", meter, "answer",
                       max_out=ctx.cfg["llm"].get("answer_max_tokens", 300))
    ids = {c["chunk_id"] for c in chunks}
    cites = list(dict.fromkeys(m for m in re.findall(r"\[([^\[\]]+)\]", ans) if m in ids))
    return ans.strip(), cites, est_tokens(ev)

def package(pipeline, qid, question, ans, cites, meter, t0, chunks, ctx_tokens, **extra):
    return {"id": qid, "question": question, "pipeline": pipeline, "answer": ans, "citations": cites,
            "tokens": {"context_est": ctx_tokens, "input": meter.tin, "output": meter.tout, "total": meter.total,
                       "estimated_usage": meter.any_estimated, "operations": [o.__dict__ for o in meter.ops]},
            "latency_ms": round((time.time() - t0) * 1000, 1), "n_chunks": len(chunks),
            "context_chunk_ids": [c["chunk_id"] for c in chunks], **extra}
