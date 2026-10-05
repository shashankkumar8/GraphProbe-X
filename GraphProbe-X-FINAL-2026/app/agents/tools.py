import re, time
from app.core import prompts as PR
from app.core.util import parse_json
from app.pipelines.common import fmt_chunks

class Tools:
    """entity_link, vector_search, graph_traverse, document_retrieve (chunk-returning) + aggregate, multi_hop_reason, verify_evidence (claim-producing)."""
    def __init__(self, ctx, st, meter): self.c, self.st, self.m, self.a = ctx, st, meter, ctx.cfg["agentic"]

    def _fresh(self, chunks, tool, paths=None):
        out = []
        for ch in chunks:
            if ch["chunk_id"] in self.st.seen: continue
            self.st.prov[ch["chunk_id"]] = {"tool": tool, "path": (paths or {}).get(ch["chunk_id"], [])}
            out.append(ch)
        return out

    def entity_link(self, target, query):
        ids = self.c.gd.link(target) or self.c.gd.link_text(target)
        for e in ids:
            if e not in self.st.entity_ids: self.st.entity_ids.append(e)
        cids = [c for e in ids[:3] for c in self.c.gd.ent2chunks.get(e, [])]
        hits = self.c.index.rank_within(cids, query, k=3, exclude=self.st.seen)
        return {"chunks": self._fresh(hits, "entity_link"), "note": f"linked {[self.c.gd.entities[e]['name'] for e in ids]}"}

    def vector_search(self, query, k=4, initial=False):
        hits = self.c.index.dense_search(query, k=k, exclude=self.st.seen) if not initial else self.c.index.hybrid(query, k=k)
        top = hits[0]["dense"] if hits else 0.0
        res = {"chunks": self._fresh(hits, "vector_search"), "note": f"top dense {top:.2f}", "fallback": None}
        if not initial and top < self.a["min_dense_score"]:      # FALLBACK RULE: weak vector match -> entity_link
            fb = self.entity_link(query, query); res["chunks"] += fb["chunks"]
            res["fallback"] = "vector_search->entity_link"; res["note"] += f"; weak match -> {fb['note']}"
        return res

    def graph_traverse(self, target, query):
        seeds = [e for e in target.split(",") if e]; t0 = time.time(); err = None
        try: cand = self.c.graph.entity_context(seeds)
        except Exception as ex: cand, err = [], repr(ex)           # TigerGraph failure == empty graph -> fallback below
        paths = {}
        ranked = self.c.index.rank_within([x["chunk_id"] for x in cand], query, k=4, exclude=self.st.seen)
        for ch in ranked: paths[ch["chunk_id"]] = self.c.gd.explain_path(ch["chunk_id"], seeds)
        res = {"chunks": self._fresh(ranked, "graph_traverse", paths), "note": f"{len(cand)} candidate chunks via {self.c.graph.name}", "fallback": None}
        res["telemetry"] = {"tool": "graph_traverse", "backend": self.c.graph.name, "seeds": len(seeds), "hops": self.c.cfg["graph"]["hops"],
                            "latency_ms": round((time.time() - t0) * 1000, 1), "candidate_chunks": len(cand), "useful_chunks": len(res["chunks"]), "error": err}
        if not cand:                                                # FALLBACK RULE: empty graph path -> document_retrieve
            fb = self.document_retrieve("auto", query); res["chunks"] += fb["chunks"]
            res["fallback"] = "graph_traverse->document_retrieve"; res["note"] += "; 0 edges -> document fallback"
        return res

    def document_retrieve(self, target, query):
        if target == "auto" or target.startswith("auto:"):
            docs = list(dict.fromkeys(h["doc_id"] for h in self.c.index.hybrid(query, k=6, exclude=self.st.seen)))[:2]
        else: docs = [target]
        out = []
        for d in docs:
            ids = [self.c.index.chunks[i]["chunk_id"] for i in self.c.index.by_doc.get(d, [])]
            out += self.c.index.rank_within(ids, query, k=2, exclude=self.st.seen)
        return {"chunks": self._fresh(out, "document_retrieve"), "note": f"docs {docs}"}

    # ---- claim-producing tools ----
    def aggregate(self, rid):
        """Deterministic structured aggregation (app/agents/aggregation.py). Claim = INFERENCE/SUPPORTED with structured-record sources + meta
        (re-verified in the final verification stage). Returns None when the structured data cannot answer."""
        from . import aggregation as AG
        recs = AG.records_for(self.c)
        out = AG.run(self.st.question, recs, self.c.cfg) if recs else None
        if not out: return None
        for src in out["sources"][:3]:                       # make support citeable: register the record's best chunk in the evidence pool
            idx = self.c.index.by_doc.get(src["doc_id"], [])
            ch = next((self.c.index.chunks[i] for i in idx if str(src["value"]) in self.c.index.chunks[i]["text"]), self.c.index.chunks[idx[0]] if idx else None)
            if ch: src["chunk_id"] = ch["chunk_id"]; self.st.seen.setdefault(ch["chunk_id"], ch); self.st.prov.setdefault(ch["chunk_id"], {"tool": "aggregate", "path": []})
        return self.st.ledger.add(req_id=rid, value=out["value"], claim_text=out["claim_text"], status="SUPPORTED", evidence_type="INFERENCE",
                                  sources=[x for x in out["sources"] if "chunk_id" in x] or out["sources"], confidence=0.95, meta=out["meta"])

    def multi_hop_reason(self, rid):
        sup = [c for c in self.st.ledger.claims if c.status == "SUPPORTED"]
        if len(sup) < 2: return None
        r = self.st.req(rid)
        raw = self.c.llm.chat(PR.JSON_SYSTEM, PR.DERIVE.format(req=f"{r.slot}: {r.description}",
              claims="\n".join(f"{c.claim_id} [{c.req_id}] {c.claim_text}" for c in sup)), self.m, "multi_hop_reason", json_mode=True)
        cl = (parse_json(raw) or {}).get("claim")
        if not cl or len(cl.get("derived_from") or []) < 2: return None
        parents = [self.st.ledger.get(x) for x in cl["derived_from"]]
        ok = all(p and p.status == "SUPPORTED" for p in parents)     # INFERENCE only counts if every parent is verified
        return self.st.ledger.add(req_id=rid, value=str(cl.get("value", "")), claim_text=str(cl.get("claim", "")),
                                  status="SUPPORTED" if ok else "PARTIALLY_SUPPORTED", evidence_type="INFERENCE",
                                  derived_from=cl["derived_from"], confidence=0.7 if ok else 0.4)

    def verify_evidence(self, rid):
        """Attempt-2 verification & contradiction resolution: LLM re-quotes; Python re-checks the quote."""
        from app.evidence.verifier import verify_quote
        L = self.st.ledger; cands = [c for c in L.for_req(rid) if c.status in ("PARTIALLY_SUPPORTED", "CONTRADICTED", "UNSUPPORTED") and c.sources]
        if not cands: return None
        ids = list(dict.fromkeys(s["chunk_id"] for c in cands for s in c.sources))
        chunks = [self.st.seen[i] for i in ids if i in self.st.seen][:4]
        r = self.st.req(rid)
        raw = self.c.llm.chat(PR.JSON_SYSTEM, PR.VERIFY.format(req=f"{r.slot}: {r.description}", rid=rid,
              cands="\n".join(f"{c.claim_id}: {c.value} | quote: {c.sources[0]['quote']}" for c in cands), chunks=fmt_chunks(chunks, 220)),
              self.m, "verify_evidence", json_mode=True)
        for c in cands: c.attempts += 1
        cl = (parse_json(raw) or {}).get("claim")
        if not cl: return None
        ch = self.st.seen.get(cl.get("chunk_id"))
        ok, sc, ex = verify_quote(cl.get("quote", ""), ch["text"]) if ch else (False, 0, False)
        if not ok: return None
        for c in cands: c.status = "UNSUPPORTED"                       # superseded by the re-verified claim
        return L.add(req_id=rid, value=str(cl.get("value", "")), claim_text=str(cl.get("claim", "")), status="SUPPORTED", evidence_type="FACT",
                     sources=[{"doc_id": ch["doc_id"], "chunk_id": ch["chunk_id"], "quote": cl["quote"]}], confidence=round(sc / 100, 2), attempts=2)
