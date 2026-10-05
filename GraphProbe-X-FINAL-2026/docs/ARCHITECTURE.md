# GraphProbe-X Architecture

## System Architecture

```mermaid
graph TB
    subgraph Clients
        WEB[Web Dashboard]
        MCP[MCP Clients<br/>Claude Code, Cursor]
    end

    subgraph API
        HTTP[HTTP API<br/>/api/ask]
        MCP_SVR[MCP Server<br/>7 Tools]
    end

    subgraph Pipelines
        RAG[RAG Pipeline<br/>BM25+Dense→RRF→Answer]
        GR[GraphRAG Pipeline<br/>Vector+Graph→Answer]
        AGENT[Agentic Pipeline<br/>Contract→Ledger→Investigate→Answer]
    end

    subgraph Core
        IDX[Hybrid Index<br/>BM25 + Dense Embeddings]
        TG[TigerGraph<br/>Doc→Chunk→Entity]
        LLM[LLM Gateway<br/>OpenRouter→Fallback]
        GOV[Governor<br/>Budget + Intelligence Guards]
    end

    subgraph Evidence
        CONTRACT[Evidence Contract<br/>Requirements]
        LEDGER[Evidence Ledger<br/>Claims + Verification]
        JUDGE[Evidence Judge<br/>Coverage + Contradiction]
    end

    WEB --> HTTP
    MCP --> MCP_SVR
    HTTP --> RAG
    HTTP --> GR
    HTTP --> AGENT
    MCP_SVR --> AGENT

    RAG --> IDX
    RAG --> LLM
    GR --> IDX
    GR --> TG
    GR --> LLM
    AGENT --> CONTRACT
    CONTRACT --> IDX
    AGENT --> LEDGER
    LEDGER --> JUDGE
    JUDGE --> GOV
    GOV -->|STOP/CONTINUE| AGENT
    AGENT --> TG
    AGENT --> LLM
```

## Three-Pipeline Comparison

```mermaid
graph LR
    subgraph Input
        Q[Question]
    end

    subgraph RAG_Pipeline[RAG Pipeline]
        R1[Hybrid Retrieval<br/>BM25 + Dense → RRF]
        R2[Top-K Selection]
        R3[Answer Generation]
    end

    subgraph GraphRAG_Pipeline[GraphRAG Pipeline]
        G1[Entity Linking]
        G2[Vector Retrieval<br/>+ Graph Traversal]
        G3[Merge + Dedup]
        G4[Answer Generation]
    end

    subgraph Agentic_Pipeline[Agentic Pipeline]
        A1[Evidence Contract]
        A2[Initial Retrieval]
        A3[Evidence Ledger]
        A4{Gap?}
        A5[Adaptive Planner]
        A6[Tool Execution]
        A7[Verify Evidence]
        A8{Governor}
        A9[Answer Generation]
    end

    Q --> R1
    R1 --> R2
    R2 --> R3

    Q --> G1
    G1 --> G2
    G2 --> G3
    G3 --> G4

    Q --> A1
    A1 --> A2
    A2 --> A3
    A3 --> A4
    A4 -->|Yes| A5
    A5 --> A6
    A6 --> A7
    A7 --> A8
    A8 -->|CONTINUE| A4
    A8 -->|STOP| A9
    A4 -->|No| A9
```

## Agentic Investigation Loop

```mermaid
stateDiagram-v2
    [*] --> Question
    Question --> EvidenceContract
    EvidenceContract --> InitialRetrieval
    InitialRetrieval --> EvidenceLedger

    EvidenceLedger --> GapDetection
    GapDetection --> HasGaps

    HasGaps --> No: No gaps
    No --> Answer

    HasGaps --> Yes: Gaps found
    Yes --> AdaptivePlanner

    AdaptivePlanner --> ToolExecution
    ToolExecution --> EvidenceVerification
    EvidenceVerification --> EvidenceLedger

    EvidenceLedger --> Governor
    Governor --> StopBudget: MAX_STEPS<br/>MAX_TOKENS
    Governor --> StopNoProgress: No progress<br/>Low gain
    Governor --> StopEvidence: Sufficient<br/>evidence
    Governor --> Continue: Continue

    StopBudget --> Answer
    StopNoProgress --> Answer
    StopEvidence --> Answer

    Continue --> GapDetection

    Answer --> [*]
```

## Evidence Contract & Ledger Flow

```mermaid
sequenceDiagram
    participant Q as Question
    participant C as Contract Generator
    participant L as Ledger
    participant R as Retriever
    participant V as Verifier
    participant J as Judge
    participant G as Governor

    Q->>C: Analyze question
    C->>C: Extract requirements
    C->>L: Create initial ledger

    loop Until Sufficient or Budget Exhausted
        L->>J: Check coverage
        J->>J: Compute coverage score
        J->>G: Report status

        alt Coverage < 1.0
            G->>R: Request next action
            R->>R: Retrieve evidence
            R->>V: Verify quote + source
            V->>L: Update claim status
        else Coverage = 1.0
            G->>G: STOP
        end
    end

    G->>Q: Return answer + citations
```

## TigerGraph Data Model

```mermaid
erDiagram
    Document ||--o{ Chunk : HAS_CHUNK
    Chunk ||--o{ Entity : MENTIONS
    Entity ||--o{ Entity : RELATED_TO

    Document {
        string doc_id PK
        string title
        string url
    }

    Chunk {
        string chunk_id PK
        string doc_id FK
        string section
        text text
        int position
    }

    Entity {
        string entity_id PK
        string name
        string entity_type
        int document_frequency
        float importance
    }

    MENTIONS {
        string extraction_method
        float confidence
        string provenance
    }
```

## Benchmark Architecture

```mermaid
graph TB
    subgraph Data
        CORPUS[Corpus<br/>2,951 docs]
        PUB[Public Questions<br/>100 with gold]
        HID[Hidden Questions<br/>50 no gold]
    end

    subgraph Indexing
        CHUNK[Chunker<br/>24,695 chunks]
        EMB[Embedder<br/>BAAI/bge-small-en-v1.5]
        IDX[Index Builder<br/>BM25 + Dense]
        GRAPH[Graph Builder<br/>54,194 entities]
    end

    subgraph Execution
        RUN[Benchmark Runner<br/>Resumable, Cached]
        RAG[RAG Pipeline]
        GR[GraphRAG Pipeline]
        AG[Agentic Pipeline]
    end

    subgraph Evaluation
        EVAL[Evaluator<br/>Accuracy, Completeness]
        MET[Metrics<br/>Tokens, Latency, Gain]
        AUDIT[Final Audit]
    end

    subgraph Results
        JSON[Per-Question JSON<br/>Full Trace]
        SUM[Summary Metrics]
        REPORT[Final Report]
    end

    CORPUS --> CHUNK
    CHUNK --> EMB
    EMB --> IDX
    CHUNK --> GRAPH

    PUB --> RUN
    HID --> RUN

    RUN --> RAG
    RUN --> GR
    RUN --> AG

    IDX --> RAG
    IDX --> GR
    IDX --> AG
    GRAPH --> GR
    GRAPH --> AG

    RAG --> JSON
    GR --> JSON
    AG --> JSON

    JSON --> EVAL
    EVAL --> MET
    MET --> AUDIT
    AUDIT --> SUM
    SUM --> REPORT
```

## Deployment Flow

```mermaid
graph LR
    subgraph Local[Local Development]
        CODE[Source Code]
        TESTS[Tests]
        CONFIG[Config]
    end

    subgraph Cloud[Cloud Services]
        TG[TigerGraph Cloud<br/>Free Tier]
        OR[OpenRouter API<br/>LLM Gateway]
        HF[HuggingFace<br/>Embeddings]
    end

    subgraph Output[Outputs]
        DASH[Streamlit Dashboard<br/>localhost:8501]
        MCP[MCP Server<br/>stdio]
        RES[Results JSON]
    end

    CODE --> TESTS
    CONFIG --> TG
    CONFIG --> OR

    CODE --> DASH
    CODE --> MCP
    TG --> DASH
    OR --> DASH

    HF --> CODE
    OR --> CODE
    TG --> CODE

    CODE --> RES
```

## Token Accounting Flow

```mermaid
graph TB
    subgraph LLM_Ops[LLM Operations]
        OP1[Contract Generation]
        OP2[Gap Detection]
        OP3[Action Planning]
        OP4[Answer Generation]
    end

    subgraph Meter[Token Meter]
        TIN[Input Tokens]
        TOUT[Output Tokens]
        TOT[Total Tokens]
        CACHE[Cache Check]
    end

    subgraph Budget[Budget Enforcement]
        CHECK{Within Budget?}
        BLOCK[Block Operation]
        ALLOW[Allow Operation]
    end

    OP1 --> CACHE
    OP2 --> CACHE
    OP3 --> CACHE
    OP4 --> CACHE

    CACHE -->|Cache Hit| TIN
    CACHE -->|Cache Miss| TOUT

    TIN --> TOT
    TOUT --> TOT

    TOT --> CHECK
    CHECK -->|No| BLOCK
    CHECK -->|Yes| ALLOW
```

## Evidence Verification Pipeline

```mermaid
graph TB
    subgraph Input
        CLAIM[Claim from LLM]
        CHUNK[Source Chunk]
    end

    subgraph Verification
        QUOTE{Quote in Chunk?<br/>Python string match}
        TARGET{Target Event/Entity<br/>matches source?}
        GRAPH{Graph path<br/>provenance valid?}
        FIELD{Structured field<br/>value matches?}
    end

    subgraph Output
        SUPPORTED[SUPPORTED<br/>High confidence]
        PARTIAL[PARTIALLY_SUPPORTED<br/>Medium confidence]
        UNSUPPORTED[UNSUPPORTED<br/>No evidence]
        CONTRADICTED[CONTRADICTED<br/>Conflicting]
    end

    CLAIM --> QUOTE
    CHUNK --> QUOTE

    QUOTE -->|Yes| TARGET
    QUOTE -->|No| UNSUPPORTED

    TARGET -->|Yes| GRAPH
    TARGET -->|Partial| PARTIAL
    TARGET -->|No| CONTRADICTED

    GRAPH -->|Valid| FIELD
    GRAPH -->|Invalid| UNSUPPORTED

    FIELD -->|Match| SUPPORTED
    FIELD -->|Mismatch| CONTRADICTED
```

## Cost-Benefit Decision Tree

```mermaid
graph TB
    START[Question Received]

    START --> EASY{Easy Question?<br/>Simple lookup}

    EASY -->|Yes| RAG[Use RAG<br/>Low cost, fast]
    EASY -->|No| MEDIUM{Medium Complexity?<br/>Multi-hop or aggregation}

    MEDIUM -->|Yes| GR[Use GraphRAG<br/>Moderate cost]
    MEDIUM -->|No| COMPLEX{Complex Question?<br/>Missing evidence, verification needed}

    COMPLEX -->|Yes| AGENT[Use Agentic<br/>Higher cost, adaptive]
    COMPLEX -->|No| RAG

    RAG --> STOP[Return Answer]
    GR --> STOP
    AGENT --> GOV{Governor Check}

    GOV -->|Budget OK| CONTINUE[Continue Investigation]
    GOV -->|Budget Exhausted| FALLBACK[Fallback to GraphRAG]

    CONTINUE --> VERIFY{Evidence Gain?}
    VERIFY -->|Positive| GOV
    VERIFY -->|Negative| FALLBACK

    FALLBACK --> STOP
```

---

## Key Architectural Principles

1. **Same Substrate**: All pipelines share corpus, chunks, embeddings, answer model, evaluator
2. **Fair Comparison**: Only retrieval/control mechanism differs
3. **Evidence-First**: Never answer without verified evidence
4. **Cost-Aware**: Measure token cost at every step
5. **Governor Control**: LLM proposes, Python validates and enforces
6. **Target-Aware Verification**: Prevent wrong-event contamination
7. **Reproducible**: Immutable results, resumable runner, full traces
8. **Honest**: Never fake benchmarks, never bypass validation

---

For implementation details, see:
- [`app/pipelines/`](../app/pipelines/) - Pipeline implementations
- [`app/evidence/`](../app/evidence/) - Evidence Contract, Ledger, Verifier
- [`app/agents/`](../app/agents/) - Orchestrator, Tools, Governor
- [`benchmark/`](../benchmark/) - Runner, Evaluator, Metrics
