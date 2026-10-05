import re
from ingest.entity_normalizer import canon
CONN = r"(?:of|the|de|la|von|van|and|&)"
CAP = re.compile(rf"\b[A-Z][\w'\u2019.\-]*(?:\s+(?:{CONN}\s+)*[A-Z][\w'\u2019.\-]*)*")
YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
STOP = set("the a an in on at of and but or if it he she they we his her their its this that these those after before during when while "
           "as by for from with to is was were are be been has have had also however although since until then there here who which what "
           "one two three first second third his hers monday tuesday wednesday thursday friday saturday sunday".split())

def extract(chunk):
    """Rule-based: capitalised spans, years, and the document title. Deterministic => every MENTIONS edge is reproducible."""
    text = chunk["text"].split("\n", 1)[-1]; ents = {}
    for m in CAP.finditer(text):
        s = m.group(0).strip(" .-'")
        if not s: continue
        single = " " not in s
        prev = text[max(0, m.start() - 2):m.start()]
        if single and (s.lower() in STOP or m.start() == 0 or prev.endswith((". ", "\n", "? ", "! "))): continue
        if s.lower() in STOP: continue
        ents[canon(s)] = (s, "NAME")
    for y in YEAR.findall(text): ents[y] = (y, "YEAR")
    ents[canon(chunk["title"])] = (chunk["title"], "TITLE")
    return ents
