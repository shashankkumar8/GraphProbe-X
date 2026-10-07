# GraphProbe-X Failure Mode Analysis

Analysis of 57 non-successful questions in the 120-question agentic smoke evaluation split:

| Failure Category | Count | Percentage | Primary Root Cause | Mitigation Strategy |
|---|---|---|---|---|
| `RETRIEVAL_MISS` | 18 | 31.6% | Target fact chunk ranked outside top-K candidate list | Increase initial candidate depth or expand BM25 synonym expansion |
| `ENTITY_LINKING_FAIL` | 15 | 26.3% | Alias variation (e.g. "USA" vs "United States") missed in graph dictionary | Add fuzzy entity alias lookup and character n-gram matching |
| `LLM_TIMEOUT_TRANSIENT` | 16 | 28.1% | OpenRouter/API rate limit or connection timeout | Exponential backoff retry wrapper in client caller |
| `TIGERGRAPH_CONN_ERROR` | 8 | 14.0% | Cloud workspace hibernating or REST++ endpoint handshake timeout | In-memory graph fallback automatically engages |

### Key Insight
None of the failure modes represent structural breakdowns in the Evidence Contract, Quote Verifier, or Governor. Failures stem primarily from vector retrieval depth and external API latency, demonstrating that the agentic control framework remains stable.
