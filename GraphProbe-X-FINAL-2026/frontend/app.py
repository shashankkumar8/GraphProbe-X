"""
GraphProbe-X — Premium Investigation Cockpit
A polished Streamlit frontend for the TigerGraph Agentic GraphRAG system.
"""
import sys
import json
from pathlib import Path
import streamlit as st

# Add parent directory to path for imports
_frontend_dir = Path(__file__).parent
_project_root = _frontend_dir.parent
sys.path.insert(0, str(_project_root))

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION & STYLING
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="GraphProbe-X | Investigation Cockpit",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium dark research-console theme
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
    --bg-deep: #030712;
    --bg-primary: #07111f;
    --bg-elevated: #0c1a2b;
    --bg-hover: #10253a;
    --border-default: #1e3a5f;
    --border-subtle: #15304d;
    --text-primary: #f0f6fc;
    --text-secondary: #8b949e;
    --text-muted: #6e7681;
    --accent-primary: #f0b429;      /* TigerGraph-inspired gold */
    --accent-success: #3fb950;
    --accent-warning: #d29922;
    --accent-error: #f85149;
    --accent-info: #58a6ff;
    --accent-purple: #a371f7;
    --mono: 'IBM Plex Mono', monospace;
    --sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --display: 'Space Grotesk', sans-serif;
}

* { box-sizing: border-box; }

html, body, .stApp {
    background: var(--bg-deep);
    color: var(--text-primary);
    font-family: var(--sans);
}

/* Typography */
h1, h2, h3, h4 { font-family: var(--display); font-weight: 600; letter-spacing: -0.02em; }
.mono { font-family: var(--mono); font-size: 0.85em; }

/* Page structure */
.block-container {
    max-width: 1600px;
    padding: 1.5rem 2rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--bg-primary);
    border-right: 1px solid var(--border-default);
}
section[data-testid="stSidebar"] .css-17lntkn {
    padding: 1rem;
}

/* Inputs */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: 8px !important;
    padding: 14px 16px !important;
    font-size: 1rem !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 0 2px rgba(240, 180, 41, 0.15) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(180deg, var(--accent-primary) 0%, #c9972b 100%) !important;
    color: #000 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(240, 180, 41, 0.3) !important;
}

/* Select boxes */
div[data-testid="stSelectbox"] > div > div {
    background: var(--bg-elevated) !important;
    border-color: var(--border-default) !important;
}

/* Expanders */
[data-testid="stExpander"] {
    border: 1px solid var(--border-subtle) !important;
    background: var(--bg-elevated) !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary {
    color: var(--text-primary) !important;
    font-weight: 500;
}

/* DataFrames */
[data-testid="stDataFrame"] {
    border-radius: 8px;
    overflow: hidden;
}

/* Tabs */
div[data-testid="stTabGroup"] .stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
div[data-testid="stTabGroup"] .stTabs [data-baseweb="tab"] {
    background: transparent;
    border: 1px solid var(--border-default);
    border-radius: 6px 6px 0 0;
    color: var(--text-secondary);
    padding: 10px 20px;
}
div[data-testid="stTabGroup"] .stTabs [aria-selected="true"] {
    background: var(--bg-elevated);
    color: var(--accent-primary);
    border-color: var(--accent-primary);
}

/* Custom components */
.premium-card {
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 1.25rem;
}

.metric-card {
    background: linear-gradient(135deg, rgba(15,35,54,0.8), rgba(8,17,29,0.9));
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 1.25rem;
    transition: all 0.2s ease;
}
.metric-card:hover {
    border-color: var(--accent-primary);
    transform: translateY(-2px);
}

.status-supported { color: var(--accent-success); }
.status-partial { color: var(--accent-warning); }
.status-unsupported { color: var(--accent-error); }
.status-unresolved { color: var(--text-muted); }
.status-contradicted { color: var(--accent-error); font-weight: 600; }

.kicker {
    color: var(--accent-primary);
    font-family: var(--mono);
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

.pipeline-rag { border-left: 3px solid #58a6ff; }
.pipeline-graphrag { border-left: 3px solid #a371f7; }
.pipeline-agentic { border-left: 3px solid #3fb950; }

/* Timeline */
.timeline-step {
    position: relative;
    padding-left: 2rem;
    padding-bottom: 1.5rem;
    border-left: 2px solid var(--border-default);
}
.timeline-step:last-child { border-left-color: transparent; }
.timeline-step::before {
    content: '';
    position: absolute;
    left: -7px;
    top: 0;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--accent-primary);
    border: 2px solid var(--bg-deep);
}
.timeline-step.active::before {
    background: var(--accent-success);
    box-shadow: 0 0 0 4px rgba(63, 185, 80, 0.2);
}

/* Animations */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
.fade-up { animation: fadeUp 0.4s ease-out; }

@keyframes slideIn {
    from { opacity: 0; transform: translateX(-10px); }
    to { opacity: 1; transform: translateX(0); }
}
.slide-in { animation: slideIn 0.3s ease-out; }

/* Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border-default); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* Responsive */
@media (max-width: 768px) {
    .block-container { padding: 1rem; }
    .metric-card { padding: 1rem; }
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def get_ctx():
    from app.core.config import load_config
    from app.core.context import build_context
    return build_context(load_config())

def get_results_dir():
    return Path(__file__).parent.parent / "results"

def load_benchmark_results(pipeline=None):
    """Load saved benchmark results."""
    results_dir = get_results_dir()
    results = {}

    files = {
        "rag": "rag_results.json",
        "graphrag": "graphrag_results.json",
        "agentic": "agentic_results.json",
        "closed_book": "closed_book_results.json"
    }

    for name, filename in files.items():
        if pipeline and name != pipeline:
            continue
        filepath = results_dir / filename
        if filepath.exists():
            try:
                with open(filepath) as f:
                    data = json.load(f)
                    results[name] = data
            except Exception as e:
                st.warning(f"Could not load {filename}: {e}")

    return results

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME / OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════

def render_home():
    """Overview page - the main landing view."""

    # Hero section
    st.markdown("""
    <div class="premium-card fade-up" style="margin-bottom: 1.5rem;">
        <div class="kicker">TIGERGRAPH AGENTIC GRAPHRAG</div>
        <h1 style="font-size: clamp(2rem, 4vw, 3rem); margin: 0.5rem 0;">GraphProbe-X</h1>
        <p style="color: var(--text-secondary); font-size: 1.1rem; max-width: 800px; margin: 0.5rem 0 1.5rem 0;">
            Evidence-driven adaptive investigation. Retrieve. Connect. Verify. Escalate only when necessary.
        </p>
        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
            <span class="premium-card" style="padding: 4px 12px; font-size: 0.75rem;">◈ RAG</span>
            <span class="premium-card" style="padding: 4px 12px; font-size: 0.75rem;">◈ GraphRAG</span>
            <span class="premium-card" style="padding: 4px 12px; font-size: 0.75rem;">◈ Agentic</span>
            <span class="premium-card" style="padding: 4px 12px; font-size: 0.75rem;">◈ TigerGraph</span>
            <span class="premium-card" style="padding: 4px 12px; font-size: 0.75rem;">◈ Verified Citations</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Metrics overview
    results = load_benchmark_results()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Public Questions", "100", "Evaluation set")
    with col2:
        st.metric("Accuracy (Agentic)", "N/A*", "Pending real index")
    with col3:
        st.metric("Avg Tokens", "N/A*", "Pending real benchmark")
    with col4:
        st.metric("Avg Latency", "N/A*", "Pending real benchmark")

    st.caption("*Metrics require real embedding index. Run `python -m scripts.build_index` first.")

    st.markdown("---")

    # Three-pipeline comparison
    st.markdown("### 📊 Three-Pipeline Comparison")

    if results:
        # Build comparison table
        comparison_data = []
        for name, data in results.items():
            if "results" in data and data["results"]:
                successful = [r for r in data["results"] if not r.get("error")]
                if successful:
                    avg_tokens = sum(r["tokens"]["total"] for r in successful) / len(successful)
                    avg_latency = sum(r["latency_ms"] for r in successful) / len(successful)
                    comparison_data.append({
                        "Pipeline": name.upper(),
                        "Questions": len(successful),
                        "Avg Tokens": f"{avg_tokens:,.0f}",
                        "Avg Latency (ms)": f"{avg_latency:,.0f}",
                        "Model": data.get("model", "N/A")
                    })

        if comparison_data:
            st.dataframe(comparison_data, use_container_width=True, hide_index=True)
        else:
            st.info("No valid benchmark results. Run benchmarks first.")
    else:
        st.info("No benchmark results found. Run benchmarks to see comparison.")

    # Value propositions
    st.markdown("---")
    st.markdown("### Why GraphProbe-X?")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="kicker">EVIDENCE-FIRST</div>
            <h3 style="margin: 0.5rem 0;">Quote-Verified Claims</h3>
            <p style="color: var(--text-secondary); font-size: 0.9rem;">
                Every claim is verified against source text. Never accept LLM confidence as proof.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="kicker">ADAPTIVE</div>
            <h3 style="margin: 0.5rem 0;">State-Dependent Action</h3>
            <p style="color: var(--text-secondary); font-size: 0.9rem;">
                The next action depends on current evidence, not a fixed sequence.
                Use the cheapest sufficient strategy.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="kicker">COST-AWARE</div>
            <h3 style="margin: 0.5rem 0;">Measurable Trade-offs</h3>
            <p style="color: var(--text-secondary); font-size: 0.9rem;">
                Track evidence gain per token. Stop when investigation cost exceeds expected value.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Quick actions
    st.markdown("---")
    st.markdown("### 🚀 Quick Actions")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Run Investigation", use_container_width=True):
            st.session_state.active_page = "Query Lab"
            st.rerun()
    with col2:
        if st.button("View Benchmarks", use_container_width=True):
            st.session_state.active_page = "Benchmarks"
            st.rerun()
    with col3:
        if st.button("Explore Evidence", use_container_width=True):
            st.session_state.active_page = "Evidence"
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: QUERY LAB
# ═══════════════════════════════════════════════════════════════════════════════

def render_query_lab():
    """Primary demo interface - run investigations."""
    st.markdown('<div class="fade-up">', unsafe_allow_html=True)

    # Query input
    st.markdown("### 🔍 Query Lab")

    col_input, col_btn = st.columns([4, 1])
    with col_input:
        question = st.text_input(
            "Enter your question",
            placeholder="e.g., Who won the men's 20km walk at the Olympics immediately before 2016?",
            label_visibility="collapsed",
            key="query_input"
        )
    with col_btn:
        run_btn = st.button("◈ INVESTIGATE", use_container_width=True)

    if question and run_btn:
        with st.spinner("Running investigation..."):
            ctx = get_ctx()
            from app.pipelines import rag, graphrag, agentic

            results = {
                "RAG": rag.run(ctx, question, "live-rag"),
                "GraphRAG": graphrag.run(ctx, question, "live-graphrag"),
                "GraphProbe-X": agentic.run(ctx, question, "live-agentic"),
            }

            # Display results in tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📋 Results", "📜 Timeline", "🔗 Evidence", "🧠 Graph"])

            with tab1:
                # Three-pipeline results
                cols = st.columns(3)
                pipeline_info = [
                    ("RAG", "rag", "#58a6ff"),
                    ("GraphRAG", "graphrag", "#a371f7"),
                    ("GraphProbe-X", "agentic", "#3fb950")
                ]

                for idx, (name, key, color) in enumerate(pipeline_info):
                    with cols[idx]:
                        r = results[key]
                        st.markdown(f"""
                        <div class="premium-card pipeline-{key}" style="margin-bottom: 1rem;">
                            <div class="kicker" style="color: {color};">{name}</div>
                            <p style="font-size: 1rem; margin: 0.75rem 0;">{r.get('answer', 'No answer')[:300]}...</p>
                            <div class="mono" style="color: var(--text-muted); font-size: 0.75rem;">
                                {r.get('tokens', {}).get('total', 0):,} tokens · {r.get('latency_ms', 0):.0f}ms
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            # Agentic trace
            agentic_result = results.get("GraphProbe-X", {})
            trace = agentic_result.get("trace", {})

            with tab2:
                # Investigation timeline
                steps = trace.get("steps", [])
                if steps:
                    for s in steps:
                        step_num = s.get("step", "?")
                        tool = s.get("tool", "unknown")
                        reason = s.get("reason", "No reason")
                        coverage_before = s.get("coverage_before", 0)
                        coverage_after = s.get("coverage_after", 0)
                        gain = s.get("gain", 0)

                        st.markdown(f"""
                        <div class="timeline-step active">
                            <div class="kicker">STEP {step_num} · {tool}</div>
                            <p style="margin: 0.5rem 0; color: var(--text-secondary);">{reason}</p>
                            <div class="mono" style="font-size: 0.8rem; color: var(--text-muted);">
                                Coverage: {coverage_before:.2f} → {coverage_after:.2f} · Gain: +{gain:.2f}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No investigation steps recorded. Try a more complex question.")

                # Stop reason
                stop_reason = trace.get("stop_reason", "unknown")
                final_coverage = trace.get("final_judge", {}).get("coverage", 0)
                n_actions = trace.get("n_actions", 0)

                st.markdown(f"""
                <div class="premium-card" style="margin-top: 1.5rem; border-left: 3px solid var(--accent-success);">
                    <div class="kicker">STOP REASON</div>
                    <h3 style="margin: 0.5rem 0; color: var(--accent-success);">{stop_reason}</h3>
                    <p style="color: var(--text-muted); font-size: 0.9rem;">
                        Final coverage: {final_coverage:.2f} · {n_actions} adaptive actions taken
                    </p>
                </div>
                """, unsafe_allow_html=True)

            with tab3:
                # Evidence ledger
                ledger = trace.get("ledger", [])
                if ledger:
                    ledger_data = []
                    for claim in ledger:
                        ledger_data.append({
                            "Claim ID": claim.get("claim_id", "?"),
                            "Requirement": claim.get("req_id", "?"),
                            "Value": claim.get("value", "?")[:50],
                            "Status": claim.get("status", "?"),
                            "Type": claim.get("evidence_type", "?"),
                            "Confidence": f"{claim.get('confidence', 0):.2f}"
                        })
                    st.dataframe(ledger_data, use_container_width=True, hide_index=True)
                else:
                    st.info("No evidence ledger entries.")

            with tab4:
                # Graph provenance
                paths = []
                for claim in ledger if 'ledger' in dir() else []:
                    for p in claim.get("graph_paths", []):
                        if p:
                            paths.append(" → ".join(map(str, p)))

                if paths:
                    for p in paths[:10]:
                        st.code(p, language="text")
                else:
                    st.info("No graph provenance paths.")

    elif not question:
        st.info("Enter a question above to start an investigation.")
        st.markdown("""
        **Example questions:**
        - Which city hosted the 2016 Summer Olympics?
        - How many biathlon events had more than 73 competitors?
        - Who won the men's 20km walk at the Olympics immediately before 2016?
        """)

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: BENCHMARKS
# ═══════════════════════════════════════════════════════════════════════════════

def render_benchmarks():
    """Benchmark comparison dashboard."""
    st.markdown("### 📊 Benchmark Results")

    results = load_benchmark_results()

    if not results:
        st.info("No benchmark results found. Run benchmarks first.")
        return

    # Summary metrics
    st.markdown("#### Pipeline Performance")

    for name, data in results.items():
        if "results" in data:
            successful = [r for r in data["results"] if not r.get("error")]
            total = len(data["results"])

            if successful:
                avg_tokens = sum(r["tokens"]["total"] for r in successful) / len(successful)
                avg_latency = sum(r["latency_ms"] for r in successful) / len(successful)

                with st.expander(f"{name.upper()} — {len(successful)}/{total} successful"):
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Successful", f"{len(successful)}/{total}")
                    col2.metric("Avg Tokens", f"{avg_tokens:,.0f}")
                    col3.metric("Avg Latency", f"{avg_latency:,.0f}ms")
                    col4.metric("Model", data.get("model", "N/A"))


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: EVIDENCE
# ═══════════════════════════════════════════════════════════════════════════════

def render_evidence():
    """Evidence Contract and Ledger viewer."""
    st.markdown("### 📋 Evidence Contract & Ledger")

    st.markdown("""
    This page shows the evidence contract and ledger from the last agentic run.
    The Evidence Contract defines what must be proven. The Ledger tracks claims and their verification status.
    """)

    st.info("Run an investigation in Query Lab to see evidence details here.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: TOKEN ECONOMICS
# ═══════════════════════════════════════════════════════════════════════════════

def render_token_economics():
    """Token cost analysis."""
    st.markdown("### 💰 Token Economics")

    results = load_benchmark_results()

    if not results:
        st.info("No benchmark results found.")
        return

    # Token breakdown
    for name, data in results.items():
        if "results" in data:
            successful = [r for r in data["results"] if not r.get("error")]
            if not successful:
                continue

            total_tokens = sum(r["tokens"]["total"] for r in successful)
            input_tokens = sum(r["tokens"]["input"] for r in successful)
            output_tokens = sum(r["tokens"]["output"] for r in successful)
            avg_total = total_tokens / len(successful)
            avg_input = input_tokens / len(successful)
            avg_output = output_tokens / len(successful)

            with st.expander(f"{name.upper()} Token Analysis"):
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Avg Total", f"{avg_total:,.0f}")
                col2.metric("Avg Input", f"{avg_input:,.0f}")
                col3.metric("Avg Output", f"{avg_output:,.0f}")
                col4.metric("Questions", len(successful))


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: GRAPH EXPLORER
# ═══════════════════════════════════════════════════════════════════════════════

def render_graph():
    """TigerGraph visualization."""
    st.markdown("### 🔗 Graph Explorer")
    st.info("Graph explorer shows the entity relationships from investigations. Run an investigation first.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: CONTRACTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_contracts():
    """Evidence Contract viewer."""
    st.markdown("### 📄 Evidence Contracts")
    st.markdown("""
    **Evidence Contract**: Defines what must be proven before answering.

    Each requirement has:
    - ID (e.g., R1, R2)
    - Description (what must be verified)
    - Required/Optional status
    - Status (UNRESOLVED, SUPPORTED, etc.)
    """)

    st.info("Run an investigation in Query Lab to see contracts here.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

def render_tools():
    """Tool registry."""
    st.markdown("### 🔧 Available Tools")

    tools = [
        ("entity_link", "Extract entities from question", "Returns entity IDs and names"),
        ("vector_search", "Semantic similarity retrieval", "Returns relevant chunks"),
        ("graph_traverse", "N-hop TigerGraph traversal", "Returns related entities/chunks"),
        ("document_retrieve", "Fetch full document", "Returns document by ID"),
        ("aggregate", "Deterministic count/max/min", "Returns computed value with provenance"),
        ("multi_hop_reason", "Multi-step reasoning", "Returns intermediate conclusions"),
        ("verify_evidence", "Check evidence support", "Returns verification result"),
        ("answer", "Generate final answer", "Returns answer with citations"),
    ]

    for tool_name, purpose, output in tools:
        st.markdown(f"""
        <div class="premium-card" style="margin-bottom: 0.75rem;">
            <div class="kicker" style="color: var(--accent-primary);">{tool_name}</div>
            <p style="margin: 0.25rem 0; color: var(--text-secondary);">{purpose}</p>
            <p class="mono" style="margin: 0; color: var(--text-muted); font-size: 0.8rem;">Output: {output}</p>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DOCS
# ═══════════════════════════════════════════════════════════════════════════════

def render_docs():
    """Documentation page."""
    st.markdown("### 📖 Documentation")

    with st.expander("What is GraphProbe-X?"):
        st.markdown("""
        GraphProbe-X is an evidence-driven adaptive Agentic GraphRAG system. It investigates questions by:

        1. **Defining an Evidence Contract** — What must be proven?
        2. **Initial Retrieval** — Getting cheap evidence first
        3. **Gap Detection** — What is still missing?
        4. **Adaptive Action** — Choosing the next best tool
        5. **Verification** — Ensuring evidence is correct
        6. **Governor Decision** — Stopping when sufficient

        The key innovation is measuring whether additional investigation is worth its cost.
        """)

    with st.expander("Architecture"):
        st.markdown("""
        - **RAG**: Hybrid BM25 + dense retrieval → answer
        - **GraphRAG**: Entity linking + graph traversal → answer
        - **Agentic**: Evidence Contract → adaptive loop → Governor → answer
        """)

    with st.expander("Evidence Contract & Ledger"):
        st.markdown("""
        **Contract**: Specifies requirements that must be verified.

        **Ledger**: Tracks each claim with:
        - SUPPORTED / PARTIALLY_SUPPORTED / UNSUPPORTED / CONTRADICTED / UNRESOLVED
        - FACT / GRAPH_DERIVATION / INFERENCE
        - Source document and chunk
        - Graph provenance
        """)

    with st.expander("Reproducibility"):
        st.markdown("""
        To reproduce results:
        ```bash
        python -m pytest -q tests
        python -m scripts.build_index  # ~2-3 hours
        python -m benchmark.runner --pipeline agentic --split public --limit 100
        python -m benchmark.evaluator --pipeline agentic
        ```
        """)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main application entry point."""

    # Initialize session state
    if "active_page" not in st.session_state:
        st.session_state.active_page = "Overview"

    # Sidebar navigation
    with st.sidebar:
        st.markdown("""
        <div style="padding: 1rem 0;">
            <h2 style="color: var(--accent-primary); margin: 0;">◈ GraphProbe-X</h2>
            <p class="mono" style="color: var(--text-muted); font-size: 0.75rem; margin-top: 0.25rem;">
                Investigation Cockpit
            </p>
        </div>
        """, unsafe_allow_html=True)

        pages = {
            "Overview": "🏠",
            "Query Lab": "🔍",
            "Benchmarks": "📊",
            "Evidence": "📋",
            "Token Economics": "💰",
            "Graph Explorer": "🔗",
            "Contracts": "📄",
            "Tools": "🔧",
            "Docs": "📖",
        }

        for page, icon in pages.items():
            if st.button(f"{icon} {page}", use_container_width=True,
                        type="primary" if st.session_state.active_page == page else "secondary"):
                st.session_state.active_page = page
                st.rerun()

        st.markdown("---")

        # Status indicator
        st.markdown("""
        <div class="premium-card" style="padding: 0.75rem;">
            <div class="kicker">SYSTEM STATUS</div>
            <p style="margin: 0.25rem 0; color: var(--accent-success);">● Operational</p>
            <p class="mono" style="margin: 0; font-size: 0.7rem; color: var(--text-muted);">
                Index: hash512 (smoke-test)
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Links
        st.markdown("""
        <div class="mono" style="font-size: 0.75rem; color: var(--text-muted);">
            <a href="https://github.com/shashankkumar8/GraphProbe-X" style="color: var(--accent-info);">GitHub</a> ·
            <a href="#" style="color: var(--accent-info);">Docs</a>
        </div>
        """, unsafe_allow_html=True)

    # Render active page
    page = st.session_state.active_page

    if page == "Overview":
        render_home()
    elif page == "Query Lab":
        render_query_lab()
    elif page == "Benchmarks":
        render_benchmarks()
    elif page == "Evidence":
        render_evidence()
    elif page == "Token Economics":
        render_token_economics()
    elif page == "Graph Explorer":
        render_graph()
    elif page == "Contracts":
        render_contracts()
    elif page == "Tools":
        render_tools()
    elif page == "Docs":
        render_docs()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div class="mono" style="text-align: center; color: var(--text-muted); font-size: 0.75rem;">
        GraphProbe-X · Evidence-driven Adaptive Agentic GraphRAG ·
        <span class="kicker">Retrieve. Connect. Verify. Escalate only when necessary.</span>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()