import json, pickle, pathlib, re
import numpy as np
from rank_bm25 import BM25Okapi
from app.core.util import toks, norm

class Index:
    def __init__(self, chunks, emb, dense, bm25, ename):
        self.chunks, self.emb, self.dense, self.bm25, self.ename = chunks, emb, dense, bm25, ename
        self.by_id = {c["chunk_id"]: i for i, c in enumerate(chunks)}
        self.by_doc = {}
        for i, c in enumerate(chunks): self.by_doc.setdefault(c["doc_id"], []).append(i)

    @classmethod
    def build(cls, chunks, emb):
        texts = [c["text"] for c in chunks]
        return cls(chunks, emb, emb.encode(texts), BM25Okapi([toks(t) for t in texts]), emb.name)

    def save(self, d):
        d = pathlib.Path(d); d.mkdir(parents=True, exist_ok=True)
        with open(d / "chunks.jsonl", "w", encoding="utf-8") as f:
            for c in self.chunks: f.write(json.dumps(c, ensure_ascii=False) + "\n")
        np.save(d / "dense.npy", self.dense)
        pickle.dump(self.bm25, open(d / "bm25.pkl", "wb"))
        json.dump({"embedder": self.ename, "n_chunks": len(self.chunks)}, open(d / "index_meta.json", "w"))

    @classmethod
    def load(cls, d, emb):
        d = pathlib.Path(d); meta = json.load(open(d / "index_meta.json"))
        if meta["embedder"] != emb.name: raise RuntimeError(f"index built with {meta['embedder']} but runtime embedder is {emb.name}")
        chunks = [json.loads(l) for l in open(d / "chunks.jsonl", encoding="utf-8")]
        return cls(chunks, emb, np.load(d / "dense.npy"), pickle.load(open(d / "bm25.pkl", "rb")), meta["embedder"])

    def scores(self, q):
        return np.asarray(self.bm25.get_scores(toks(q)), dtype=np.float32), self.dense @ self.emb.encode([q])[0]

    @staticmethod
    def _rank(x, idx):
        order = idx[np.argsort(-x[idx], kind="stable")]
        r = np.empty(len(x), dtype=np.int32); r[order] = np.arange(len(order)); return order, r

    def _fuse(self, b, d, idx, k, rrf_k, exclude):
        ob, rb = self._rank(b, idx); od, rd = self._rank(d, idx)
        fused = 1.0 / (rrf_k + rb[idx]) + 1.0 / (rrf_k + rd[idx])
        out, seen_txt = [], set()
        for j in np.argsort(-fused, kind="stable"):
            i = int(idx[j]); c = self.chunks[i]
            if c["chunk_id"] in exclude: continue
            key = norm(c["text"])[:160]
            if key in seen_txt: continue                       # dedup near-identical chunks
            seen_txt.add(key); out.append({**c, "score": float(fused[j]), "dense": float(d[i])})
            if len(out) >= k: break
        return out

    def hybrid(self, q, k=8, cands=40, rrf_k=60, exclude=()):
        b, d = self.scores(q); n = len(self.chunks)
        top = np.unique(np.concatenate([np.argsort(-b)[:cands], np.argsort(-d)[:cands]]))
        return self._fuse(b, d, top, k, rrf_k, set(exclude))

    def dense_search(self, q, k=4, exclude=()):
        b, d = self.scores(q); ex = set(exclude); out = []
        for i in np.argsort(-d)[: k + len(ex) + 5]:
            c = self.chunks[int(i)]
            if c["chunk_id"] in ex: continue
            out.append({**c, "score": float(d[i]), "dense": float(d[i])})
            if len(out) >= k: break
        return out

    def rank_within(self, chunk_ids, q, k=4, exclude=(), rrf_k=60):
        idx = np.array([self.by_id[c] for c in chunk_ids if c in self.by_id], dtype=np.int64)
        if len(idx) == 0: return []
        b, d = self.scores(q)
        return self._fuse(b, d, idx, k, rrf_k, set(exclude))
