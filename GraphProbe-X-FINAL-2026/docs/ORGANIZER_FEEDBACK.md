# TigerGraph Organizer Feedback & Developer Experience

## 1. Community Edition Experience
- **Schema Definition:** Defining vertex types (`Document`, `Chunk`, `Entity`) and edge types (`HAS_CHUNK`, `MENTIONS`, `RELATED_TO`) in GSQL was clear and straightforward.
- **Query Language:** GSQL pattern-matching syntax (`-()>-`) makes multi-hop graph traversal intuitive for 2-hop entity relation queries.
- **Resource Considerations:** When running Community Edition in Docker on local development machines, JVM heap sizing should be explicitly pre-configured to avoid out-of-memory errors on large bulk entity loads.

## 2. TigerGraph DevHub / Cloud Savanna Feedback
- **REST++ API:** The REST++ endpoints (`POST /query/{graph_name}/{query_name}`) provide fast graph query responses.
- **Documentation:** REST++ API documentation is well-structured.
- **Improvement Suggestion:** Error responses for REST++ token expiration or hibernation could return specific HTTP status codes (e.g. 401 vs 503) rather than generic 500 error messages to enable cleaner client-side handling.

## 3. Code Fixes Implemented Based on Feedback
- **Connection Resiliency (`app/graph/tigergraph.py`):** Added automatic REST++ token refresh, retry logic with exponential backoff, and seamless fallback to an in-memory graph structure when cloud endpoints undergo hibernation.
- **Deterministic Traversal Bounds:** Implemented hub degree capping (`hub_df: 300`) to prevent high-degree hub entities (e.g. "Olympics") from exploding traversal path counts and slowing down retrieval.
