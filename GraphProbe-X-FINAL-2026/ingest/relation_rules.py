"""OPTIONAL typed relations (e.g. WON, REPRESENTS, AT_VENUE). Add ONLY after `make inspect` shows the corpus supports them.
Each rule = regex with named groups subj/obj; every produced edge keeps {source_chunk_id, quote, extraction_method='rule:<name>', confidence}.
Golden rule: no rule, no edge. Example (uncomment & adapt to the real corpus wording):
RULES = [("won_by", "WON", r"(?P<obj>[A-Z][\\w ]+?) was won by (?P<subj>[A-Z][\\w ]+?)[.,]")]
"""
import re
RULES = []

def extract_relations(chunk):
    out = []
    for name, rel, pat in RULES:
        for m in re.finditer(pat, chunk["text"]):
            out.append({"subj": m.group("subj"), "rel": rel, "obj": m.group("obj"), "source_chunk_id": chunk["chunk_id"],
                        "quote": m.group(0), "extraction_method": f"rule:{name}", "confidence": 0.9})
    return out
