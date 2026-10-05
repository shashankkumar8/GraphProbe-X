"""GraphProbe-X investigation cockpit."""
import json
from pathlib import Path
import streamlit as st

from app.core.config import load_config
from app.core.context import build_context
from app.pipelines import rag, graphrag, agentic

st.set_page_config(page_title="GraphProbe-X", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { --bg:#07111f; --panel:#0c1a2b; --panel2:#10253a; --line:#20425c; --text:#edf6ff; --muted:#8fa8ba; --cyan:#5ee7ff; --green:#62f0ae; --amber:#ffd166; --purple:#bca7ff; }
.stApp { background: radial-gradient(circle at 10% 0%, #0e2940 0, #07111f 32%, #050b14 100%); color:var(--text); }
.block-container { max-width: 1500px; padding-top: 1.2rem; padding-bottom: 3rem; }
section[data-testid="stSidebar"] { background:#08111d; }
* { font-family:'Space Grotesk',system-ui,sans-serif; }
code, pre, .mono { font-family:'IBM Plex Mono',monospace !important; }
.hero { border:1px solid var(--line); background:linear-gradient(135deg,rgba(15,35,54,.94),rgba(8,17,29,.92)); border-radius:20px; padding:28px 32px; box-shadow:0 18px 60px rgba(0,0,0,.28); }
.kicker { color:var(--cyan); font-family:'IBM Plex Mono',monospace; font-weight:600; font-size:.78rem; letter-spacing:.14em; text-transform:uppercase; }
.hero h1 { font-size: clamp(2.2rem, 4vw, 4rem); line-height:1; margin: .35rem 0 .85rem; letter-spacing:-.05em; }
.hero p { max-width:980px; color:#b9ccda; font-size:1rem; line-height:1.65; }
.tag { display:inline-block; padding:5px 9px; border-radius:999px; border:1px solid #2b516c; color:#b8d3e5; background:#0b1d2d; margin-right:6px; font:500 .72rem 'IBM Plex Mono',monospace; }
.panel { border:1px solid var(--line); background:rgba(12,26,43,.78); border-radius:16px; padding:18px; }
.panel h3 { margin:0 0 8px; font-size:1rem; }
.panel .sub { color:var(--muted); font-size:.78rem; }
.metric { font-size:1.85rem; font-weight:700; margin-top:5px; letter-spacing:-.03em; }
.small { color:var(--muted); font-size:.74rem; }
.good { color:var(--green); }
.cyan { color:var(--cyan); }
.warn { color:var(--amber); }
.purple { color:var(--purple); }
div[data-testid="stTextInput"] input { background:#081727 !important; color:var(--text) !important; border:1px solid #244761 !important; border-radius:12px !important; padding:14px !important; }
.stButton>button { border:1px solid #2c7692; background:linear-gradient(180deg,#17394d,#10273a); color:#eafaff; border-radius:12px; font-weight:700; }
[data-testid="stExpander"] { border:1px solid #1f4158 !important; background:#0b1928 !important; }
div[data-testid="stDataFrame"] { border-radius:12px; overflow:hidden; }
hr { border-color:#173247 !important; }
@keyframes fadeUp { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }
.fade-up { animation: fadeUp .35s ease both; }
@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:.55; } }
.pulse { animation: pulse 1.6s ease-in-out infinite; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_ctx():
    return build_context(load_config())


def metric_card(title, value, detail, accent="cyan"):
    st.markdown(f"""
    <div class="panel fade-up">
      <div class="sub">{title}</div>
      <div class="metric {accent}">{value}</div>
      <div class="small">{detail}</div>
    </div>
    """, unsafe_allow_html=True)


def compact_result(name, r, accent):
    st.markdown(f"<div class='kicker'>{name}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:1.05rem;line-height:1.55'>{r['answer']}</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='small' style='margin-top:10px'>tokens <b>{r['tokens']['total']:,}</b> · {r['latency_ms']:.0f} ms · {len(r['citations'])} citations · {r['n_chunks']} chunks</div>",
        unsafe_allow_html=True,
    )


def render_graph(paths):
    if not paths:
        st.info("No graph path was required for this answer.")
        return
    rows = []
    for p in paths:
        if p:
            rows.append(" → ".join(map(str, p)))
    for x in rows[:10]:
        st.code(x, language="text")

st.markdown("""
<div class='hero'>
  <div class='kicker'>TIGERGRAPH AGENTIC GRAPHRAG · EVIDENCE-FIRST RESEARCH SYSTEM</div>
  <h1>GraphProbe-X</h1>
  <div>
    <span class='tag'>RAG</span><span class='tag'>GRAPHRAG</span><span class='tag'>AGENTIC</span><span class='tag'>TIGERGRAPH</span><span class='tag'>VERIFIABLE CITATIONS</span>
  </div>
  <p><b>Retrieve. Connect. Verify. Escalate only when necessary.</b><br>
  GraphProbe-X treats investigation as a controlled loop: define what must be proven, retrieve cheap evidence first, identify gaps, choose the next action, verify the result, and stop when the evidence contract is satisfied.</p>
</div>
""", unsafe_allow_html=True)

st.write("")
q = st.text_input("", placeholder="Ask an Olympic corpus question…", label_visibility="collapsed")
run = st.button("◈  INVESTIGATE", use_container_width=True)
ctx = get_ctx()

if q and run:
    with st.spinner("Running RAG, fixed GraphRAG, and adaptive GraphProbe-X…"):
        results = {
            "RAG": rag.run(ctx, q, "live-rag"),
            "GraphRAG": graphrag.run(ctx, q, "live-graphrag"),
            "GraphProbe-X": agentic.run(ctx, q, "live-agentic"),
        }

    st.markdown("### Three-pipeline view")
    cols = st.columns(3)
    accents = {"RAG":"cyan", "GraphRAG":"purple", "GraphProbe-X":"good"}
    for col, (name, r) in zip(cols, results.items()):
        with col:
            st.markdown(f"<div class='panel fade-up'>", unsafe_allow_html=True)
            compact_result(name, r, accents[name])
            st.markdown("</div>", unsafe_allow_html=True)

    a = results["GraphProbe-X"]
    trace = a.get("trace", {})
    contract = trace.get("contract", {}).get("requirements", [])
    ledger = trace.get("ledger", [])

    st.markdown("### Evidence cockpit")
    left, mid, right = st.columns([1.0, 1.5, 1.0])
    with left:
        st.markdown("<div class='panel'><h3>Evidence Contract</h3>", unsafe_allow_html=True)
        for r in contract:
            st.markdown(f"<div class='small'><b>{r['req_id']}</b> · {r['slot']}<br>{r['description']}</div><hr>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with mid:
        st.markdown("<div class='panel'><h3>Investigation Timeline</h3>", unsafe_allow_html=True)
        for s in trace.get("steps", []):
            title = f"STEP {s['step']} · {s['tool']} · {s['coverage_before']:.2f} → {s['coverage_after']:.2f} · +{s['gain']:.2f}"
            with st.expander(title, expanded=(s["step"] == trace.get("steps", [{}])[-1].get("step", -1))):
                st.markdown(f"**Reason**  {s['reason']}")
                st.markdown(f"**Note**  {s['note']}")
                if s.get("fallback"):
                    st.markdown(f"**Fallback**  `{s['fallback']}`")
                if s.get("candidates"):
                    st.dataframe(s["candidates"], use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='panel'><h3>Decision</h3>", unsafe_allow_html=True)
        st.markdown(f"<div class='kicker'>STOP REASON</div><div class='metric good'>{trace.get('stop_reason','—')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='small'>strategy changes · <b>{trace.get('strategy_changes',0)}</b><br>actions · <b>{trace.get('n_actions',0)}</b><br>confidence · <b>{trace.get('confidence',0)}</b> <i>(not a probability)</i></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Verified evidence ledger")
    if ledger:
        st.dataframe(
            [
                {"claim_id": c["claim_id"], "req": c["req_id"], "value": c["value"], "status": c["status"], "type": c["evidence_type"], "confidence": c["confidence"]}
                for c in ledger
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No ledger claims were produced.")

    paths = [p for c in ledger for p in c.get("graph_paths", []) if p]
    st.markdown("### Graph provenance")
    render_graph(paths)

    st.markdown("### Why GraphProbe-X stopped")
    st.markdown(
        f"<div class='panel'><span class='good'><b>{trace.get('stop_reason','unknown')}</b></span> · "
        f"coverage <b>{trace.get('final_judge',{}).get('coverage',0):.2f}</b> · "
        f"{trace.get('n_actions',0)} adaptive actions · "
        f"{sum(c['tokens']['total'] for c in results.values()):,} combined tokens across the three displayed runs</div>",
        unsafe_allow_html=True,
    )

st.markdown("---")
st.markdown("<div class='small mono'>GraphProbe-X · corpus-grounded · structured telemetry, not chain-of-thought · no hidden-set tuning in the cockpit</div>", unsafe_allow_html=True)
