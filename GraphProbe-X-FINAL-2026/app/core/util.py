import json, re, unicodedata, hashlib
WORD = re.compile(r"\w+")

def toks(s): return WORD.findall(s.lower())
def est_tokens(s): return max(1, len(s) // 4)

def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).casefold()
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def parse_json(text):
    if not text: return None
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.M).strip()
    cands = [t]
    m = re.search(r"\{.*\}", t, re.S)
    if m: cands.append(m.group(0))
    for c in cands:
        try: return json.loads(c)
        except Exception: pass
    return None

def sha(path, n=12):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()[:n]

def pick(d, keys, default=None):
    for k in keys:
        if k in d and d[k] not in (None, ""): return d[k]
    return default
