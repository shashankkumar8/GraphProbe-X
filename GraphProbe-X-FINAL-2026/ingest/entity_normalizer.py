import re
from app.core.util import norm
# Small, conservative alias table. Ambiguous names (e.g. "Georgia", "Great Britain") are deliberately NOT merged.
ALIASES = {"usa": "united states", "u s": "united states", "u s a": "united states", "us": "united states",
           "united states of america": "united states", "uk": "united kingdom", "u k": "united kingdom",
           "ussr": "soviet union", "u s s r": "soviet union", "prc": "china", "people s republic of china": "china"}

def canon(name):
    n = norm(name)
    n = re.sub(r"^(the)\s+", "", n)
    return ALIASES.get(n, n)

def eid(name): return "E_" + re.sub(r"\s+", "_", canon(name))
