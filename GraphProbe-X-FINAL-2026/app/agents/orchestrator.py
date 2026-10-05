import time
from app.core import prompts as PR
from app.core.meter import Meter
from app.core.util import parse_json
from app.evidence.contract import analyze, contract_json
from app.evidence.judge import judge
from app.evidence.verifier import verify_quote
from app.pipelines.common import fmt_chunks, synthesize, package
from .harness import State, Governor
from .tools import Tools

# (gain prior, est. tokens) per (tool, gap). Priors are heuristics (label as such); observed gains decay repeated zero-gain tools.
PRIORS = {("entity_link", "ENTITY_GAP"): (.5, 400), ("entity_link", "RELATION_GAP"): (.45, 400), ("entity_link", "COVERAGE_GAP"): (.2, 400),
          ("graph_traverse", "ENTITY_GAP"): (.2, 1800), ("graph_traverse", "RELATION_GAP"): (.6, 1800), ("graph_traverse", "COVERAGE_GAP"): (.3, 1800),
          ("vector_search", "ENTITY_GAP"): (.3, 1500), ("vector_search", "RELATION_GAP"): (.3, 1500), ("vector_search", "COVERAGE_GAP"): (.5, 1500),
          ("document_retrieve", "ENTITY_GAP"): (.2, 1800), ("document_retrieve", "RELATION_GAP"): (.4, 1800), ("document_retrieve", "COVERAGE_GAP"): (.45, 1800),
          ("verify_evidence", "*"): (.5, 1200), ("multi_hop_reason", "*"): (.35, 700), ("aggregate", "*"): (.4, 50)}
CHUNK_TOOLS = {"entity_link", "vector_search", "graph_traverse", "document_retrieve"}

class Orchestrator:
    def __init__(self, ctx): self.ctx, self.a, self.gov = ctx, ctx.cfg["agentic"], Governor(ctx.cfg["agentic"])

    # ---------- ledger update ----------
    def _ingest(self, st, chunks, meter):
        for c in chunks: st.seen[c["chunk_id"]] = c
        j = judge(st.reqs, st.ledger, st.qtype, self.a, mode="contract")
        open_ids = [r.req_id for r in st.reqs if r.req_id in j["missing"] or not r.required]
        open_ids = [i for i in open_ids if st.ledger.credit(i) < 1.0] or []
        if not chunks or not open_ids: return []
        use = chunks[: self.a["extract_chunks"]]
        raw = self.ctx.llm.chat(PR.JSON_SYSTEM, PR.EXTRACT.format(question=st.question,
              reqs="\n".join(f"{r.req_id} ({r.type}) {r.slot}: {r.description}" for r in st.reqs if r.req_id in open_ids),
              known="\n".join(f"{c.claim_id}: {c.claim_text}" for c in st.ledger.claims if c.status == "SUPPORTED") or "(none)",
              chunks=fmt_chunks(use, self.a["extract_words"])), meter, "extract", json_mode=True, max_out=700)
        new = []
        for cl in (parse_json(raw) or {}).get("claims", []) or []:
            rid, ch = cl.get("req_id"), st.seen.get(cl.get("chunk_id"))
            if rid not in open_ids or not ch: continue
            ok, sc, ex = verify_quote(cl.get("quote", ""), ch["text"])          # attempt 1: deterministic quote check
            prov = st.prov.get(ch["chunk_id"], {})
            et = "GRAPH_DERIVATION" if prov.get("tool") == "graph_traverse" and prov.get("path") and st.req(rid).type == "relation" else "FACT"
            c = st.ledger.add(req_id=rid, value=str(cl.get("value", "")), claim_text=str(cl.get("claim", "")),
                              status="SUPPORTED" if ok else "PARTIALLY_SUPPORTED", evidence_type=et,
                              sources=[{"doc_id": ch["doc_id"], "chunk_id": ch["chunk_id"], "quote": cl.get("quote", "")}],
                              graph_paths=[prov["path"]] if et == "GRAPH_DERIVATION" else [], confidence=round(sc / 100, 2) if ok else 0.4, attempts=1)
            new.append(c)
            if ok:
                for e in self.ctx.gd.link(c.value):
                    if e not in st.entity_ids: st.entity_ids.append(e)
        return new

    # ---------- planning ----------
    def _candidates(self, st, j):
        gap = j["gap_type"] or "COVERAGE_GAP"; rid = j["contradictions"] and st.ledger.get(j["contradictions"][0]).req_id or (j["missing"][0] if j["missing"] else st.reqs[0].req_id)
        r = st.req(rid); q = f"{st.question} {r.description}"; vals = st.known_values()
        C = [("entity_link", vals[-1] if vals else r.slot.replace("_", " "))]
        C.append(("vector_search", q))
        if st.entity_ids: C.append(("graph_traverse", ",".join(sorted(st.entity_ids)[:6])))
        docs = list(dict.fromkeys(c["doc_id"] for c in st.seen.values()))
        for d in docs[:3]: C.append(("document_retrieve", d))
        C.append(("document_retrieve", f"auto:{rid}"))
        if j["contradictions"] or st.ledger.for_req(rid, {"PARTIALLY_SUPPORTED"}): C.append(("verify_evidence", rid))
        from . import aggregation as AG
        recs = AG.records_for(self.ctx); ap = AG.plan(st.question, recs, self.ctx.cfg) if recs else None
        if ap and (st.qtype in ("aggregation", "superlative") or ap["strong"]) and not st.ledger.for_req(rid, {"SUPPORTED"}): C.append(("aggregate", rid))
        if st.qtype in ("multi_hop", "comparison", "temporal", "superlative", "relationship") and len(st.known_values()) >= 2: C.append(("multi_hop_reason", rid))
        used = self.ctx_meter_total
        out = []
        for tool, target in C:
            g0, cost = PRIORS.get((tool, gap)) or PRIORS[(tool, "*")]
            zero = sum(1 for t, g in st.tool_hist if t == tool and g < self.a["min_gain"])
            gain = g0 * (self.a["gain_decay"] ** zero) * (1.25 if tool == j["recommended_action"] else 1.0)
            key = (tool, target, gap); status, why = "eligible", ""
            if tool in self.a["disabled_tools"]: status, why = "rejected", "tool_disabled"
            elif self.a["use_memory"] and key in st.memory: status, why = "rejected", "duplicate_action"
            elif used + cost > self.a["max_tokens"]: status, why = "rejected", "budget"
            out.append({"tool": tool, "target": target, "gap_type": gap, "req_id": rid, "expected_gain": round(gain, 3), "est_tokens": cost,
                        "utility": round(gain / (cost / 1000), 3), "status": status, "reject_reason": why})
        return out

    def _choose(self, st, cands, j, meter):
        ok = [c for c in cands if c["status"] == "eligible"]
        if not ok: return None
        best = max(ok, key=lambda c: c["utility"])
        if self.a["planner"] == "llm":       # LLM proposes; code validates membership + budget before execution
            raw = self.ctx.llm.chat(PR.JSON_SYSTEM, PR.PLAN.format(question=st.question, gap=f"{j['gap_type']} missing={j['missing']}",
                  cands="\n".join(f"{i}: {c['tool']}({c['target'][:60]}) utility={c['utility']}" for i, c in enumerate(ok))), meter, "plan", json_mode=True, max_out=120)
            ch = (parse_json(raw) or {}).get("choice")
            if isinstance(ch, int) and 0 <= ch < len(ok): best = ok[ch]
        return best

    # ---------- main loop ----------
    def run(self, question, qid="", meter=None):
        ctx, a = self.ctx, self.a; meter, t0 = meter or Meter(), time.time()
        reqs, qtype, ents = analyze(ctx.llm, meter, question)
        st = State(question, qid, qtype, reqs)
        for n in ents:
            for e in ctx.gd.link(n): st.entity_ids.append(e) if e not in st.entity_ids else None
        for e in ctx.gd.link_text(question):
            if e not in st.entity_ids: st.entity_ids.append(e)
        T = Tools(ctx, st, meter); self.ctx_meter_total = 0
        # step 0: cheap initial retrieval (always runs once): hybrid vector + entity_link
        m0 = meter.mark(); r1 = T.vector_search(question, k=a["initial_k"], initial=True)
        r2 = T.entity_link("; ".join(ents), question) if ents else {"chunks": [], "note": "no entities"}
        chunks = r1["chunks"] + r2["chunks"]; new = self._ingest(st, chunks, meter)
        j = judge(reqs, st.ledger, qtype, a, mode=a["judge_mode"]); cov = j["coverage"]
        st.steps.append({"step": 0, "tool": "initial_retrieval", "target": question[:80], "gap_type": None, "reason": "always-run cheap retrieval",
                         "candidates": [], "fallback": None, "new_chunks": len(chunks), "new_claims": [c.claim_id for c in new],
                         "coverage_before": 0.0, "coverage_after": cov, "gain": cov, "note": f"{r1['note']}; {r2['note']}", **meter.since(m0)})
        n_actions, stop = 0, None
        while True:
            self.ctx_meter_total = meter.total
            stop = self.gov.check(st, j, meter, n_actions)
            if stop: break
            cands = self._candidates(st, j); ch = self._choose(st, cands, j, meter)
            if ch is None: stop = "no_untried_actions"; break
            st.memory.add((ch["tool"], ch["target"], ch["gap_type"]))
            m1 = meter.mark(); cb = j["coverage"]; fb = None; note = ""; new = []; tel = None
            if ch["tool"] in CHUNK_TOOLS:
                q = f"{question} {st.req(ch['req_id']).description}"
                res = getattr(T, ch["tool"])(ch["target"], q) if ch["tool"] != "vector_search" else T.vector_search(ch["target"])
                fb, note, chunks, tel = res.get("fallback"), res["note"], res["chunks"], res.get("telemetry")
                new = self._ingest(st, chunks, meter)
            else:
                c = getattr(T, ch["tool"])(ch["req_id"]); chunks = []; new = [c] if c else []; note = "claim produced" if c else "no result"
            j = judge(reqs, st.ledger, qtype, a, mode=a["judge_mode"]); gain = round(j["coverage"] - cb, 3)
            st.tool_hist.append((ch["tool"], gain)); st.zero_streak = st.zero_streak + 1 if gain < a["min_gain"] else 0
            if fb: st.fallbacks += 1
            if st.last_tool and (ch["tool"] != st.last_tool or fb): st.strategy_changes += 1
            st.last_tool = ch["tool"]; n_actions += 1
            st.steps.append({"step": n_actions, "tool": ch["tool"], "target": ch["target"][:80], "gap_type": ch["gap_type"],
                             "reason": f"{ch['gap_type']} on {ch['req_id']}; chose {ch['tool']} (utility {ch['utility']}); judge recommended {j.get('recommended_action')}",
                             "candidates": cands, "fallback": fb, "new_chunks": len(chunks), "new_claims": [c.claim_id for c in new],
                             "coverage_before": cb, "coverage_after": j["coverage"], "gain": gain, "note": note, "telemetry": tel, **meter.since(m1)})
        # ---------- mandatory final verification ----------
        vm = meter.mark(); ver = {"reverified": 0, "failed": 0, "attempt2": 0}
        for c in st.ledger.claims:
            if c.status == "SUPPORTED" and c.evidence_type != "INFERENCE":
                ok = verify_quote(c.sources[0]["quote"], st.seen[c.sources[0]["chunk_id"]]["text"])[0]; ver["reverified"] += 1
                if not ok: c.status = "UNRESOLVED"; ver["failed"] += 1
        from . import aggregation as AG
        for c in st.ledger.claims:                                   # deterministic derivations: field==value on raw records + recomputation
            if c.status == "SUPPORTED" and c.meta.get("method") == "structured_aggregate":
                ver["reverified"] += 1
                if not AG.reverify(c, AG.records_for(ctx), ctx.cfg): c.status = "UNRESOLVED"; ver["failed"] += 1
        for r in st.reqs:
            if r.required and st.ledger.credit(r.req_id) < 1.0 and st.ledger.for_req(r.req_id, {"PARTIALLY_SUPPORTED"}) and "verify_evidence" not in {t for t, _ in st.tool_hist}:
                T.verify_evidence(r.req_id); ver["attempt2"] += 1
        for c in st.ledger.claims:
            if c.status == "PARTIALLY_SUPPORTED" and c.evidence_type != "INFERENCE": c.status = "UNRESOLVED"
        jf = judge(reqs, st.ledger, qtype, a, mode="contract")
        # ---------- answer ----------
        cited = list(dict.fromkeys(s["chunk_id"] for c in st.ledger.claims if c.status == "SUPPORTED" for s in c.sources))
        pool = [st.seen[i] for i in cited if i in st.seen][: a["answer_chunks"]]
        pool += [c for c in st.seen.values() if c not in pool][: max(0, 2 - len(pool))]
        lines = [f"- {c.req_id} ({st.req(c.req_id).slot}): {c.value} [{c.evidence_type}]" + (f" \"{c.sources[0]['quote'][:160]}\" [{c.sources[0]['chunk_id']}]" if c.sources else f" (derived from {c.derived_from})")
                 for r in st.reqs for c in [st.ledger.best(r.req_id)] if c]
        unres = [f"{r.req_id} ({r.slot})" for r in st.reqs if r.required and st.ledger.credit(r.req_id) < 1.0]
        extra = "VERIFIED CLAIMS:\n" + ("\n".join(lines) or "(none)") + (f"\nNOT CONFIRMED in available evidence: {', '.join(unres)}. State this explicitly.\n" if unres else "\n") + "\n"
        ans, cites, ct = synthesize(ctx, meter, question, pool, extra)
        best = [st.ledger.best(r.req_id) for r in st.reqs if r.required]
        conf = round(sum((b.confidence if b else 0) for b in best) / max(1, len(best)), 3)
        tools_used = [s["tool"] for s in st.steps]
        trace = {"question_type": qtype, "contract": contract_json(reqs), "steps": st.steps, "tool_sequence": tools_used,
                 "n_actions": n_actions, "strategy_changes": st.strategy_changes, "fallbacks": st.fallbacks, "stop_reason": stop,
                 "final_judge": jf, "unresolved": unres, "verification": ver, "ledger": st.ledger.to_json(), "confidence": conf,
                 "confidence_note": "mean confidence of best verified claim per required slot; NOT a calibrated probability"}
        return package("agentic", qid, question, ans, cites, meter, t0, pool, ct, trace=trace, question_type=qtype, confidence=conf,
                       context_chunk_ids_all=list(st.seen))

def run(ctx, question, qid=""): return Orchestrator(ctx).run(question, qid)
