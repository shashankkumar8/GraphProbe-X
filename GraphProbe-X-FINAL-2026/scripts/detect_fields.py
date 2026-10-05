"""No-LLM discovery of structured fields in the REAL corpus (streams the file; prints a compact report). python -m scripts.detect_fields"""
import re, collections, json
from app.core.config import load_config
from ingest.loader import read_jsonl
WANT = "event games venue date dates competitors nations gold silver bronze goldNOC silverNOC bronzeNOC prev next sport discipline year city country".split()

def main(limit=3000):
    cfg = load_config(); keys, prefixes, n = collections.Counter(), collections.Counter(), 0
    for r in read_jsonl(cfg["data"]["corpus"]):
        n += 1; keys.update(r.keys())
        txt = " ".join(str(v) for k, v in r.items() if isinstance(v, str))
        for m in re.finditer(r"(?m)^\s*(?:\|\s*)?([A-Za-z][A-Za-z _/-]{1,24}?)\s*(?::|=)\s*\S", txt): prefixes[m.group(1).strip().lower()] += 1
        for k, v in r.items():
            if isinstance(v, dict): keys.update(f"{k}.{kk}" for kk in v)
        if n >= limit: break
    print(f"scanned {n} docs\ntop-level keys: {dict(keys)}\ntop 'Key: value' line prefixes: {prefixes.most_common(25)}")
    allk = {k.lower().split('.')[-1] for k in keys} | set(prefixes)
    print("expected fields present:", {w: (w.lower() in allk) for w in WANT})
    first = next(read_jsonl(cfg["data"]["corpus"])); print("first record (truncated):", json.dumps(first)[:700])

if __name__ == "__main__": main()
