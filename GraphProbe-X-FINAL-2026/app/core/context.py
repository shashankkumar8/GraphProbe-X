from dataclasses import dataclass
from .config import P
from .llm import get_llm
from app.retrieval.embed import get_embedder
from ingest.loader import load_corpus
from app.retrieval.index import Index
from app.graph.store import GraphData, get_graph

@dataclass
class Ctx:
    cfg: dict; llm: object; index: Index; gd: GraphData; graph: object
    corpus_docs: list | None = None

def build_context(cfg, need_llm=True):
    proc = P(cfg["paths"]["processed"])
    index = Index.load(proc, get_embedder(cfg))
    gd = GraphData.load(proc)
    try:
        corpus_docs = load_corpus(cfg)
    except Exception:
        corpus_docs = []
    return Ctx(cfg, get_llm(cfg) if need_llm else None, index, gd, get_graph(cfg, gd), corpus_docs)
