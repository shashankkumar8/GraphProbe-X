"""Deterministic offline stand-in for an LLM. ONLY for plumbing tests (`make smoke`); its outputs are NOT benchmark results."""
import re, json
from .util import norm, toks
STOPW = set("the a an of in on at to for and or is was were what which who where when how did does do by with from that this country represent represents held venue winner won".split())
KEYS = {"winner": ["won by"], "country": ["represents"], "venue": ["held at"]}
PAT = {"winner": r"won by ([A-Z][a-z]+ [A-Z][a-z]+)", "country": r"represents ([A-Z][a-z]+)", "venue": r"held at ([A-Z][\w ]+?)[.,]"}

def _chunks(user):
    return re.findall(r"\[([^\[\]\n]+)\] (.*?)(?=\n\n\[|\Z)", user.split("CHUNKS:")[-1] if "CHUNKS:" in user else user.split("EVIDENCE:")[-1], re.S)

class MockLLM:
    model = "mock"
    def chat(self, system, user, meter=None, op="llm", json_mode=False, max_out=None):
        t = self._route(system, user)
        if meter is not None: meter.add(op, (len(system) + len(user)) // 4, len(t) // 4, 1.0, True)
        return t
    def _route(self, system, user):
        if "TASK:ANALYZE" in user:
            q = user.split("QUESTION:")[-1].strip(); ql = q.lower(); reqs = []
            if "who" in ql or "winner" in ql or "won" in ql: reqs.append(("entity", "winner", "winner of the event"))
            if "country" in ql or "represent" in ql: reqs.append(("relation", "country", "country the winner represents"))
            if "where" in ql or "venue" in ql or "held" in ql: reqs.append(("attribute", "venue", "venue of the event"))
            if not reqs: reqs = [("attribute", "answer", q)]
            ents = re.findall(r"\b\d{4} [A-Z][a-z]+ [A-Z][a-z]+|[A-Z][a-z]+ Cup", q)
            return json.dumps({"question_type": "multi_hop" if "country" in ql else "single_fact", "entities": ents,
                               "requirements": [{"req_id": f"R{i}", "type": t, "slot": s, "description": d, "required": True} for i, (t, s, d) in enumerate(reqs, 1)]})
        if "TASK:EXTRACT" in user:
            q = re.search(r"QUESTION: (.*)", user).group(1); known = user.split("KNOWN CLAIMS:")[1].split("CHUNKS:")[0]
            anchor = set(toks(q)) | set(toks(known)); anchor -= STOPW
            claims = []
            for line in user.split("OPEN REQUIREMENTS:")[1].split("KNOWN CLAIMS:")[0].strip().splitlines():
                m = re.match(r"(R\d+) \((\w+)\) (\w+):", line)
                if not m: continue
                rid, _, slot = m.groups()
                if slot not in KEYS: continue
                for cid, txt in _chunks(user):
                    for s in re.split(r"(?<=[.!?])\s+", txt):
                        if any(k in s for k in KEYS[slot]) and len(anchor & set(toks(s))) >= (2 if slot != "country" else 2):
                            mm = re.search(PAT[slot], s)
                            claims.append({"req_id": rid, "value": mm.group(1) if mm else s, "claim": s, "chunk_id": cid, "quote": s.strip()}); break
                    else: continue
                    break
            return json.dumps({"claims": claims})
        if "TASK:VERIFY" in user or "TASK:DERIVE" in user: return json.dumps({"claim": None})
        if "TASK:JUDGE" in user:
            g = re.search(r"GOLD: (.*)", user).group(1); p = user.split("PREDICTION:")[-1]
            ok = norm(g) in norm(p); return json.dumps({"correct": ok, "complete": ok, "reason": "mock substring match"})
        if "TASK:PLAN" in user: return json.dumps({"choice": 0, "reason": "mock"})
        # answer
        if "VERIFIED CLAIMS:" in user and "(none)" not in user.split("VERIFIED CLAIMS:")[1].split("EVIDENCE:")[0]:
            vc = user.split("VERIFIED CLAIMS:")[1].split("EVIDENCE:")[0]
            vals = re.findall(r"^- R\d+ \(\w+\): (.*?) \[(?:FACT|GRAPH_DERIVATION|INFERENCE)\].*?\[([^\]]+)\]", vc, re.M)
            if vals: return "; ".join(f"{v} [{c}]" for v, c in vals)
        q = re.search(r"QUESTION: (.*)", user).group(1); a = set(toks(q)) - STOPW; best = None
        for cid, txt in _chunks(user):
            for s in re.split(r"(?<=[.!?])\s+", txt):
                sc = len(a & set(toks(s)))
                if best is None or sc > best[0]: best = (sc, s, cid)
        return f"{best[1]} [{best[2]}]" if best else "Not confirmed."
