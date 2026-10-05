import re
HEAD = re.compile(r"^\s*(?:={2,}\s*(.+?)\s*={2,}|#{1,4}\s+(.+?))\s*$")

def _sections(text):
    sec, buf, out = "Lead", [], []
    for line in text.splitlines():
        m = HEAD.match(line)
        if m:
            if "".join(buf).strip(): out.append((sec, "\n".join(buf)))
            sec, buf = (m.group(1) or m.group(2)).strip(), []
        else: buf.append(line)
    if "".join(buf).strip(): out.append((sec, "\n".join(buf)))
    return out

def chunk_doc(doc, max_words=220, overlap=40):
    chunks, i = [], 0
    for sec, body in _sections(doc["text"]):
        paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        cur, n = [], 0
        def flush():
            nonlocal cur, n, i
            if cur:
                txt = " ".join(cur)
                chunks.append({"chunk_id": f"{doc['doc_id']}::{i}", "doc_id": doc["doc_id"], "title": doc["title"], "section": sec,
                               "text": f"{doc['title']} | {sec}\n{txt}"}); i += 1
        for p in paras:
            w = p.split()
            if len(w) > max_words:                       # long paragraph -> sliding window (tables/lists stay in one paragraph when short)
                flush(); cur, n = [], 0
                step = max(1, max_words - overlap)
                for s in range(0, len(w), step):
                    cur = [" ".join(w[s:s + max_words])]; flush(); cur = []
                    if s + max_words >= len(w): break
                continue
            if n + len(w) > max_words: flush(); cur, n = [], 0
            cur.append(p); n += len(w)
        flush()
    return chunks
