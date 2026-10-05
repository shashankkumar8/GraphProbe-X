from dataclasses import dataclass, asdict

@dataclass
class Op:
    name: str; tokens_in: int; tokens_out: int; latency_ms: float; estimated: bool = False
    provider: str = ""; cached: bool = False; attempts: list = None

class Meter:
    """One accounting method for ALL pipelines: provider `usage` fields (estimate only if provider omits them; flagged)."""
    def __init__(self): self.ops = []
    def add(self, name, tin, tout, ms, est=False, provider="", cached=False, attempts=None):
        self.ops.append(Op(name, int(tin), int(tout), float(ms), est, provider, cached, attempts))
    def mark(self): return len(self.ops)
    def since(self, m):
        o = self.ops[m:]
        return {"tokens": sum(x.tokens_in + x.tokens_out for x in o), "latency_ms": round(sum(x.latency_ms for x in o), 1), "ops": [asdict(x) for x in o]}
    @property
    def tin(self): return sum(o.tokens_in for o in self.ops)
    @property
    def tout(self): return sum(o.tokens_out for o in self.ops)
    @property
    def total(self): return self.tin + self.tout
    @property
    def any_estimated(self): return any(o.estimated for o in self.ops)
