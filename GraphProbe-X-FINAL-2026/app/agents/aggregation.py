"""Deterministic aggregation (count/threshold, list, max/min) over STRUCTURED corpus fields. No LLM, no regex over prose.
Source of truth per record = raw JSONL keys (one nested level allowed); fallback = strict header lines `Key: value` / `| key = value` for the
configured keys only. Constraints are data-driven: a facet value constrains the query only if that exact value occurs in the question."""
import re, operator
from app.core.util import norm

K = lambda s: re.sub(r"[^a-z0-9]+", "_", str(s).lower()).strip("_")
CMP = {">": operator.gt, ">=": operator.ge, "<": operator.lt, "<=": operator.le}
THRESH = re.compile(r"\b(more than|greater than|over|exceed(?:ed|s|ing)?|at least|no fewer than|fewer than|less than|under|below|at most|no more than)\s+([\d,]+)\b")
CMPW = {"more than": ">", "greater than": ">", "over": ">", "exceed": ">", "at least": ">=", "no fewer than": ">=",
        "fewer than": "<", "less than": "<", "under": "<", "below": "<", "at most": "<=", "no more than": "<="}
MAXW = re.compile(r"\b(most|highest|largest|greatest|biggest|maximum|largest)\b"); MINW = re.compile(r"\b(fewest|lowest|smallest|minimum|least)\b")
COUNTW = re.compile(r"\bhow many\b|\bnumber of\b|\bcount\b")
NUMQ = re.compile(r"\b(highest|largest|greatest|maximum|most|lowest|smallest|fewest|minimum)\s+(number|count|total)\b")

def _scalar(v): return "; ".join(map(str, v)) if isinstance(v, list) else v

def build_records(docs, cfg):
    sc = cfg["structured"]; want = {K(x) for x in sc["count_fields"] + sc["facet_fields"] + sc["answer_fields"]}; recs = []
    for d in docs:
        raw = d.get("raw") or {}; f = {}
        for k, v in raw.items():
            if isinstance(v, dict):
                for kk, vv in v.items():
                    if isinstance(vv, (str, int, float, list)): f.setdefault(K(kk), {"v": _scalar(vv), "src": "raw"})
            elif isinstance(v, (str, int, float, list)) and K(k) not in ("text", "contents", "content", "body"): f.setdefault(K(k), {"v": _scalar(v), "src": "raw"})
        f.setdefault("title", {"v": d["title"], "src": "raw"})
        for line in str(d.get("text", "")).splitlines()[:40]:               # strict header lines only, configured keys only, never overrides raw
            m = re.match(r"^\s*(?:[|*-]\s*)?([A-Za-z][A-Za-z _]{1,30}?)\s*[:=]\s*(.+?)\s*$", line)
            if m and K(m.group(1)) in want and K(m.group(1)) not in f: f[K(m.group(1))] = {"v": m.group(2), "src": "text_kv", "line": line.strip()}
        for x in f.values(): x["norm"] = norm(x["v"])
        recs.append({"doc_id": d["doc_id"], "title": d["title"], "fields": f})
    return recs

def num(v):
    if isinstance(v, (int, float)): return int(v)
    m = re.match(r"\s*(\d[\d,]*)(?:\.\d+)?\b", str(v)); return int(m.group(1).replace(",", "")) if m else None

def plan(question, recs, cfg):
    """Parse the aggregation intent from the question + resolve which structured count field exists. None => not deterministically answerable."""
    ql = question.lower(); sc = cfg["structured"]
    cf = max(((sum(1 for r in recs if K(c) in r["fields"] and num(r["fields"][K(c)]["v"]) is not None), K(c)) for c in sc["count_fields"]), default=(0, None))
    cf = cf[1] if cf[0] else None
    m = THRESH.search(ql); p = {"count_field": cf, "thr": None, "cmp": None, "op": None, "want_number": bool(NUMQ.search(ql)), "strong": False}
    if m:
        p.update(thr=int(m.group(2).replace(",", "")), cmp=next(v for k, v in CMPW.items() if m.group(1).startswith(k[:6])), op="count" if COUNTW.search(ql) else "list", strong=True)
    elif MAXW.search(ql) and cf: p["op"] = "argmax"
    elif MINW.search(ql) and cf: p["op"] = "argmin"
    elif COUNTW.search(ql): p.update(op="count", strong=True)
    if p["op"] is None or (p["op"] != "count" or p["thr"] is not None) and not cf: return None
    return p

def _years(q): return re.findall(r"\b(?:1[89]|20)\d{2}\b", q)

def constraints(question, recs, cfg):
    qn = f" {norm(question)} "; cons = {}
    for f in (K(x) for x in cfg["structured"]["facet_fields"]):
        vals = {r["fields"][f]["norm"] for r in recs if f in r["fields"]}
        best = max((v for v in vals if len(v) >= 3 and f" {v} " in qn), key=len, default=None)
        if best: cons[f] = best
    ys = [y for y in _years(question) if not any(y in v.split() for v in cons.values())]
    return {"facets": cons, "years": ys}

def _match(r, cons, cfg):
    for f, v in cons["facets"].items():
        if f not in r["fields"] or f" {v} " not in f" {r['fields'][f]['norm']} ": return False
    facets = [K(x) for x in cfg["structured"]["facet_fields"]]
    return all(any(f in r["fields"] and y in r["fields"][f]["norm"].split() for f in facets) for y in cons["years"])

def _name(r, cfg):
    for f in cfg["structured"]["answer_fields"]:
        if K(f) in r["fields"]: return str(r["fields"][K(f)]["v"])
    return r["title"]

def compute(recs, p, cons, cfg):
    cf = p["count_field"]; uni = "event" if p["op"] == "count" and p["thr"] is None and any("event" in r["fields"] for r in recs) else cf
    pool = [(num(r["fields"][cf]["v"]) if cf and cf in r["fields"] else None, r) for r in recs if uni in r["fields"] and _match(r, cons, cfg)]
    if p["op"] in ("argmax", "argmin", "list") or p["thr"] is not None: pool = [(n, r) for n, r in pool if n is not None]
    if not pool: return None
    op = p["op"]
    if op in ("count", "list"):
        sel = [(n, r) for n, r in pool if p["thr"] is None or CMP[p["cmp"]](n, p["thr"])]
        value = str(len(sel)) if op == "count" else "; ".join(sorted(_name(r, cfg) for _, r in sel)[:30])
    else:
        t = (max if op == "argmax" else min)(n for n, _ in pool); sel = [(n, r) for n, r in pool if n == t]
        value = str(t) if p["want_number"] else "; ".join(sorted(_name(r, cfg) for _, r in sel))
    return {"value": value, "selected": sel, "n_universe": len(pool)}

def run(question, recs, cfg):
    """-> dict(value, claim_text, sources, meta) or None. sources = structured records (doc_id, field, value, src) that determine the result."""
    p = plan(question, recs, cfg)
    if not p: return None
    cons = constraints(question, recs, cfg); res = compute(recs, p, cons, cfg)
    if not res: return None
    cf = p["count_field"]; cap = cfg["structured"]["max_support"]
    sel = sorted(res["selected"], key=lambda x: (-(x[0] or 0), x[1]["title"]))[:cap]
    sources = [{"doc_id": r["doc_id"], "field": cf, "value": r["fields"][cf]["v"], "src": r["fields"][cf]["src"], "name": _name(r, cfg),
                "quote": f"{_name(r, cfg)}: {cf}={r['fields'][cf]['v']}"} for n, r in sel if cf and cf in r["fields"]]
    desc = f"{p['op']}({cf or 'records'}{(' ' + p['cmp'] + ' ' + str(p['thr'])) if p['thr'] is not None else ''}) | constraints={ {**cons['facets'], **({'years': cons['years']} if cons['years'] else {})} } = {res['value']} over {res['n_universe']} matching records"
    return {"value": res["value"], "claim_text": desc, "sources": sources,
            "meta": {"method": "structured_aggregate", "plan": p, "constraints": cons, "n_universe": res["n_universe"], "n_selected": len(res["selected"])}}

def reverify(claim, recs, cfg):
    """Deterministic re-check: (1) every cited source field == stored value in the raw record, (2) recomputation reproduces the value."""
    by = {r["doc_id"]: r for r in recs}
    for s in claim.sources:
        r = by.get(s["doc_id"])
        if not r or s["field"] not in r["fields"] or str(r["fields"][s["field"]]["v"]) != str(s["value"]): return False
    m = claim.meta; res = compute(recs, m["plan"], m["constraints"], cfg)
    return bool(res) and res["value"] == claim.value

def records_for(ctx):
    """Build once per context; [] when the corpus carries no structured fields (then aggregate is simply not offered)."""
    if not hasattr(ctx, "_agg_records"): ctx._agg_records = build_records(getattr(ctx, "corpus_docs", None) or [], ctx.cfg)
    return ctx._agg_records
