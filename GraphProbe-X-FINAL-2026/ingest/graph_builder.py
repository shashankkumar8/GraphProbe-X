import collections
from ingest.entity_extractor import extract
from ingest.entity_normalizer import eid

def build_graph_data(chunks, min_df=2):
    """Chunk-mediated entity graph. Edge Chunk-MENTIONS->Entity carries provenance by construction (source chunk id,
    extraction_method='rule:capitalised-span|year|title'). Optional typed relations: see ingest/relation_rules.py."""
    per_chunk, df, meta = {}, collections.Counter(), {}
    for c in chunks:
        ents = extract(c); per_chunk[c["chunk_id"]] = ents
        for k, (name, et) in ents.items():
            df[k] += 1; meta.setdefault(k, (name, et))
    keep = {k for k, n in df.items() if n >= min_df or meta[k][1] == "TITLE"}
    entities, ent2chunks, chunk2ents, alias = {}, collections.defaultdict(list), {}, {}
    for cid, ents in per_chunk.items():
        for k in ents:
            if k not in keep: continue
            e = eid(k)
            entities.setdefault(e, {"name": meta[k][0], "etype": meta[k][1], "df": df[k]})
            ent2chunks[e].append(cid); chunk2ents.setdefault(cid, []).append(e); alias[k] = e
    return {"entities": entities, "ent2chunks": dict(ent2chunks), "chunk2ents": chunk2ents, "alias": alias}
