from rapidfuzz import fuzz
from app.core.util import norm

def verify_quote(quote, chunk_text, thr=92):
    """Deterministic (NOT an LLM self-report): normalised exact substring, else fuzzy partial match >= thr. Returns (ok, score, exact)."""
    q, t = norm(quote), norm(chunk_text)
    if len(q) < 8: return False, 0.0, False
    if q in t: return True, 100.0, True
    s = fuzz.partial_ratio(q, t)
    return s >= thr, float(s), False
