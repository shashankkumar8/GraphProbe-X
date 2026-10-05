import json
from app.core.util import pick

def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if line:
                try: yield json.loads(line)
                except json.JSONDecodeError as e: raise ValueError(f"{path}:{i+1} bad JSON: {e}")

def load_corpus(cfg):
    F = cfg["data"]["fields"]; docs, seen = [], set()
    for i, r in enumerate(read_jsonl(cfg["data"]["corpus"])):
        did = str(pick(r, F["doc_id"], f"doc{i}")); text = pick(r, F["text"], "")
        if did in seen or not str(text).strip(): continue      # validator: drop dupes / empty
        seen.add(did)
        docs.append({"doc_id": did, "title": str(pick(r, F["title"], did)), "text": str(text), "raw": r})
    return docs

def load_questions(cfg, split):
    F = cfg["data"]["fields"]; out = []
    for i, r in enumerate(read_jsonl(cfg["data"][split])):
        ans = pick(r, F["answer"], None)
        out.append({"id": str(pick(r, F["q_id"], f"q{i}")), "question": pick(r, F["question"], ""), "gold": ans, "raw": r})
    return out
