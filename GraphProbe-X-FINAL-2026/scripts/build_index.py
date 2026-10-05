"""Corpus -> chunks -> entities/graph -> BM25 + dense index. Usage: python -m scripts.build_index"""
import json, time
from app.core.config import load_config, P
from app.retrieval.embed import get_embedder
from app.retrieval.index import Index
from ingest.loader import load_corpus
from ingest.chunker import chunk_doc
from ingest.graph_builder import build_graph_data

def main():
    cfg = load_config(); out = P(cfg["paths"]["processed"]); out.mkdir(parents=True, exist_ok=True)
    t = time.time(); docs = load_corpus(cfg); print(f"docs: {len(docs)}")
    chunks = [c for d in docs for c in chunk_doc(d, cfg["chunk"]["max_words"], cfg["chunk"]["overlap_words"])]
    print(f"chunks: {len(chunks)}  avg words: {sum(len(c['text'].split()) for c in chunks)/max(1,len(chunks)):.0f}")
    gd = build_graph_data(chunks); print(f"entities: {len(gd['entities'])}  mentions: {sum(len(v) for v in gd['ent2chunks'].values())}")
    json.dump(gd, open(out / "graph.json", "w"))
    idx = Index.build(chunks, get_embedder(cfg)); idx.save(out)
    print(f"done in {time.time()-t:.0f}s -> {out}")

if __name__ == "__main__": main()
