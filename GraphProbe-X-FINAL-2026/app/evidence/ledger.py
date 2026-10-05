import re
from dataclasses import dataclass, field, asdict
from app.core.util import norm

@dataclass
class Claim:
    claim_id: str; req_id: str; value: str; claim_text: str
    status: str = "UNSUPPORTED"          # SUPPORTED | PARTIALLY_SUPPORTED | UNSUPPORTED | CONTRADICTED | UNRESOLVED
    evidence_type: str = "FACT"          # FACT | GRAPH_DERIVATION | INFERENCE  (INFERENCE is never presented as FACT)
    sources: list = field(default_factory=list)   # [{doc_id, chunk_id, quote}]
    graph_paths: list = field(default_factory=list)
    confidence: float = 0.0
    derived_from: list = field(default_factory=list)
    attempts: int = 0
    meta: dict = field(default_factory=dict)      # e.g. {'method':'structured_aggregate', ...} for deterministic derivations

CREDIT = {"SUPPORTED": 1.0, "PARTIALLY_SUPPORTED": 0.5}

class Ledger:
    def __init__(self): self.claims, self._n = [], 0
    def new_id(self): self._n += 1; return f"C{self._n}"
    def add(self, **kw):
        c = Claim(claim_id=self.new_id(), **kw); self.claims.append(c); return c
    def get(self, cid): return next((c for c in self.claims if c.claim_id == cid), None)
    def for_req(self, rid, statuses=None): return [c for c in self.claims if c.req_id == rid and (statuses is None or c.status in statuses)]
    def best(self, rid):
        cs = [c for c in self.claims if c.req_id == rid and c.status in CREDIT]
        return max(cs, key=lambda c: (CREDIT[c.status], c.confidence), default=None)
    def credit(self, rid):
        b = self.best(rid); return CREDIT[b.status] if b else 0.0
    def detect_contradictions(self, qtype):
        """Same requirement, >=2 SUPPORTED claims with different normalised values => CONTRADICTED (not for aggregation/superlative)."""
        if qtype in ("aggregation", "superlative", "multi_document"): return []
        bad = []
        for rid in {c.req_id for c in self.claims}:
            cs = [c for c in self.for_req(rid, {"SUPPORTED"}) if c.evidence_type != "INFERENCE"]
            vals = {norm(c.value) for c in cs}
            distinct = [v for v in vals if not any(v != w and (v in w or w in v) for w in vals)]
            if len(distinct) > 1:
                for c in cs: c.status = "CONTRADICTED"; bad.append(c.claim_id)
        return bad
    def to_json(self): return [asdict(c) for c in self.claims]
