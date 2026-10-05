import os, re, json, pathlib, collections
from rapidfuzz import process, fuzz
from ingest.entity_extractor import CAP, YEAR, STOP
from ingest.entity_normalizer import canon

class GraphData:
    """Local copy of the entity graph: used for entity linking, path explanation and the in-memory backend."""
    def __init__(self, d):
        self.entities, self.ent2chunks, self.chunk2ents, self.alias = d["entities"], d["ent2chunks"], d["chunk2ents"], d["alias"]
        self._names = list(self.alias.keys())
    @classmethod
    def load(cls, folder): return cls(json.load(open(pathlib.Path(folder) / "graph.json")))
    def is_hub(self, e, hub_df): return self.entities[e]["df"] > hub_df

    def link(self, name, fuzzy=92):
        k = canon(name)
        if k in self.alias: return [self.alias[k]]
        if not self._names or len(k) < 4: return []
        m = process.extractOne(k, self._names, scorer=fuzz.ratio, score_cutoff=fuzzy)
        return [self.alias[m[0]]] if m else []

    def link_text(self, text):
        spans = {m.group(0).strip(" .-'") for m in CAP.finditer(text)} | set(YEAR.findall(text))
        ids = []
        for s in sorted(spans, key=len, reverse=True):
            if s.lower() in STOP: continue
            for e in self.link(s):
                if e not in ids: ids.append(e)
        return ids

    def explain_path(self, chunk_id, seeds):
        ents = self.chunk2ents.get(chunk_id, [])
        for s in seeds:
            if s in ents: return [self.entities[s]["name"], "MENTIONED_IN", chunk_id]
        for s in seeds:
            for c1 in self.ent2chunks.get(s, [])[:200]:
                for e2 in self.chunk2ents.get(c1, []):
                    if e2 in ents and e2 != s:
                        return [self.entities[s]["name"], "MENTIONED_IN", c1, "MENTIONS", self.entities[e2]["name"], "MENTIONED_IN", chunk_id]
        return []

class MemoryGraph:
    name = "memory"
    def __init__(self, gd, cfg): self.gd, self.hops, self.hub, self.lim = gd, cfg["graph"]["hops"], cfg["graph"]["hub_df"], cfg["graph"]["cand_limit"]
    def entity_context(self, seeds, hops=None):
        hops = hops or self.hops; score = collections.Counter(); seeds = set(seeds)
        for s in seeds:
            for c in self.gd.ent2chunks.get(s, []): score[c] += 2
        if hops >= 2:
            n1 = {e for c in list(score) for e in self.gd.chunk2ents.get(c, []) if e not in seeds and not self.gd.is_hub(e, self.hub)}
            for e in n1:
                for c in self.gd.ent2chunks.get(e, []):
                    if c not in score: score[c] += 1
        return [{"chunk_id": c, "score": s} for c, s in score.most_common(self.lim)]

class TigerGraphStore:
    """Traversal executed by the installed GSQL query `entity_context` (graph/queries/entity_context.gsql)."""
    name = "tigergraph"
    def __init__(self, cfg, hops=2):
        import pyTigerGraph as tg
        self.hops, self.hub, self.lim = cfg["graph"]["hops"], cfg["graph"]["hub_df"], cfg["graph"]["cand_limit"]
        kw = dict(host=os.environ["TG_HOST"], graphname=os.environ.get("TG_GRAPH", "GraphProbeX"),
                  username=os.environ.get("TG_USER", "tigergraph"), password=os.environ.get("TG_PASS", ""))
        self.conn = tg.TigerGraphConnection(**kw)
        if os.environ.get("TG_SECRET"): self.conn.getToken(os.environ["TG_SECRET"])
    def entity_context(self, seeds, hops=None):
        if not seeds: return []
        r = self.conn.runInstalledQuery("entity_context", {"ents": list(seeds), "hops": hops or self.hops, "hub_df": self.hub, "k": self.lim})
        rows = r[0].get("Top", []) if r else []
        return [{"chunk_id": x["attributes"]["chunk_id"] if "attributes" in x else x["chunk_id"], "score": x.get("@score", x.get("attributes", {}).get("@score", 1))} for x in rows]

def get_graph(cfg, gd):
    return TigerGraphStore(cfg) if cfg["graph"]["backend"] == "tigergraph" else MemoryGraph(gd, cfg)
