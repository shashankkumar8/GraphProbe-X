def judge(reqs, ledger, qtype, a, initial_dense=None, mode="contract"):
    """Evidence Judge. Coverage is computed over the VERIFIED ledger (an LLM can never mark a slot supported).
    coverage = sum(credit of required slots)/#required, credit: SUPPORTED=1, PARTIALLY_SUPPORTED=0.5."""
    contradictions = ledger.detect_contradictions(qtype)
    req = [r for r in reqs if r.required] or reqs
    if mode == "heuristic":      # ablation: no contract-driven sufficiency; "enough" as soon as ANY claim exists
        got = any(c.status in ("SUPPORTED", "PARTIALLY_SUPPORTED") for c in ledger.claims)
        return {"sufficient": got, "coverage": 1.0 if got else 0.0, "missing": [] if got else [r.req_id for r in req],
                "contradictions": [], "gap_type": "COVERAGE_GAP", "recommended_action": "vector_search"}
    credits = {r.req_id: ledger.credit(r.req_id) for r in req}
    cov = sum(credits.values()) / len(req)
    missing = [r.req_id for r in req if credits[r.req_id] < 1.0]
    first = next((r for r in req if r.req_id in missing), None)
    gap = {"entity": "ENTITY_GAP", "relation": "RELATION_GAP"}.get(first.type, "COVERAGE_GAP") if first else None
    rec = {"ENTITY_GAP": "entity_link", "RELATION_GAP": "graph_traverse", "COVERAGE_GAP": "vector_search"}.get(gap)
    partial = first and ledger.for_req(first.req_id, {"PARTIALLY_SUPPORTED"})
    if contradictions or (partial and not ledger.for_req(first.req_id, {"SUPPORTED"})): rec = "verify_evidence"
    suff = (not missing and not contradictions) or (cov >= a["coverage_threshold"] and not contradictions)
    return {"sufficient": bool(suff), "coverage": round(cov, 3), "missing": missing, "contradictions": contradictions,
            "gap_type": gap, "recommended_action": rec}
