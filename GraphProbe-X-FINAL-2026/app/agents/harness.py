from dataclasses import dataclass, field
from app.evidence.ledger import Ledger

@dataclass
class State:
    question: str; qid: str; qtype: str; reqs: list
    ledger: Ledger = field(default_factory=Ledger)
    entity_ids: list = field(default_factory=list)
    seen: dict = field(default_factory=dict)        # chunk_id -> chunk
    prov: dict = field(default_factory=dict)        # chunk_id -> {"tool":..., "path": [...]}
    memory: set = field(default_factory=set)        # Investigation Memory: (tool, target, gap_type)
    tool_hist: list = field(default_factory=list)   # (tool, gain)
    steps: list = field(default_factory=list)
    strategy_changes: int = 0
    zero_streak: int = 0
    last_tool: str = None
    fallbacks: int = 0

    def req(self, rid): return next(r for r in self.reqs if r.req_id == rid)
    def known_values(self): return [c.value for c in self.ledger.claims if c.status == "SUPPORTED"]

class Governor:
    """Deterministic stop rules. The LLM can propose actions or 'sufficient'; it can never override these."""
    def __init__(self, a): self.a = a
    def check(self, st, j, meter, n_actions):
        if j["sufficient"]: return "sufficient_evidence"
        if n_actions >= self.a["max_steps"]: return "max_steps_reached"
        if meter.total >= self.a["max_tokens"] or len(meter.ops) >= self.a.get("max_llm_calls", 10**9): return "budget_exceeded"
        if st.zero_streak >= self.a["patience"]: return "no_information_gain"
        return None
