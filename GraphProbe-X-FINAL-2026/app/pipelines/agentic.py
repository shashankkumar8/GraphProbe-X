from app.core.meter import Meter
from app.agents.orchestrator import Orchestrator
from . import graphrag, rag

def run(ctx, question, qid=""):
    """Pipeline C with agent-crash fallback: Agentic -> GraphRAG -> RAG. The failure and its wasted tokens are recorded, never hidden."""
    m = Meter()
    try: return Orchestrator(ctx).run(question, qid, m)
    except Exception as e:
        err = repr(e)
        for name, mod in (("graphrag", graphrag), ("rag", rag)):
            try: r = mod.run(ctx, question, qid); break
            except Exception as e2: err += f" | {name}: {e2!r}"
        else: raise
        r["pipeline"] = "agentic"; r["fallback"] = {"from": "agentic", "to": name, "error": err, "wasted_tokens": m.total}
        r["tokens"]["total"] += m.total; r["tokens"]["input"] += m.tin; r["tokens"]["output"] += m.tout
        r["confidence"] = 0.0; r["question_type"] = "?"
        r["trace"] = {"question_type": "?", "contract": {"requirements": []}, "steps": [], "tool_sequence": ["initial_retrieval", f"fallback_{name}"],
                      "n_actions": 0, "strategy_changes": 0, "fallbacks": 1, "stop_reason": "agent_crash_fallback", "final_judge": {"coverage": 0.0},
                      "unresolved": [], "verification": {}, "ledger": [], "confidence": 0.0}
        return r
