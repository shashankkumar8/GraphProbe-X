import numpy as np, re, zlib
from app.core.util import toks

class HashEmbedder:
    """Dependency-free fallback (tests / smoke). Use the sentence-transformers model for real runs."""
    name, dim = "hash512", 512
    def encode(self, texts, batch=256):
        M = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, t in enumerate(texts):
            w = toks(t)
            for f in w + [a + "_" + b for a, b in zip(w, w[1:])]:
                M[i, zlib.crc32(f.encode()) % self.dim] += 1.0
        n = np.linalg.norm(M, axis=1, keepdims=True); n[n == 0] = 1
        return M / n

class STEmbedder:
    def __init__(self, model):
        from sentence_transformers import SentenceTransformer
        self.name = model; self.m = SentenceTransformer(model, device="cpu")
    def encode(self, texts, batch=64):
        return np.asarray(self.m.encode(texts, batch_size=batch, normalize_embeddings=True, show_progress_bar=len(texts) > 500), dtype=np.float32)

def get_embedder(cfg, force_hash=False):
    import os
    if force_hash or os.environ.get("GPX_EMBED") == "hash": return HashEmbedder()
    try: return STEmbedder(cfg["retrieval"]["dense_model"])
    except Exception as e:
        print(f"[warn] sentence-transformers unavailable ({e}); using HashEmbedder (weaker!)"); return HashEmbedder()
