# GraphProbe-X Demo Video Script

**Target Duration:** 3–5 minutes  
**Tone:** Authoritative, research-grade, crisp  

---

## 0:00 – 0:45 | Hook & Core Thesis
**[Visual: Hero AI Research Console landing page with dark theme and yellow accent]**  
**Speaker:** "Most RAG systems answer when they find something relevant. GraphProbe-X asks a harder question: *Is what we found actually enough to prove the answer?*"  
**Speaker:** "Standard RAG retrieves text. GraphRAG connects relationships. GraphProbe-X investigates only when the evidence demands it."  
**Speaker:** "Our central thesis is simple: We don't add agents. We justify them."

---

## 0:45 – 1:30 | The Three Pipelines Comparison
**[Visual: Query Lab comparing RAG, GraphRAG, and GraphProbe-X side-by-side]**  
**Speaker:** "Here in the Query Lab, we compare three distinct paradigms on the exact same Olympic dataset using OpenAI GPT-4o-mini."  
**Speaker:** "Pipeline A performs standard BM25 and dense hybrid retrieval. Pipeline B executes fixed 2-hop TigerGraph traversals. Pipeline C—GraphProbe-X—operates an explicit evidence-driven control loop."

---

## 1:30 – 2:45 | Hero Investigation Walkthrough
**[Visual: Investigation Timeline & Evidence Ledger expanding for a complex multi-hop query]**  
**Speaker:** "Watch what happens when GraphProbe-X processes a multi-hop query. First, it parses an Evidence Contract listing explicit query requirements."  
**Speaker:** "Step 1 executes initial retrieval and populates the Evidence Ledger. Every claim is verified in Python against verbatim quotes from the source text."  
**Speaker:** "When Gap Detection identifies an unresolved relation, the Adaptive Planner escalates to TigerGraph graph traversal."  
**Speaker:** "Once all slots in the Evidence Contract are supported, our Cost-Aware Governor triggers an immediate Early Stop—preventing wasted tokens."

---

## 2:45 – 3:30 | Benchmark Dashboard & Token Economics
**[Visual: Benchmark Dashboard showing Accuracy, Tokens, Latency, and Evidence Gain per Token]**  
**Speaker:** "In our benchmark telemetry, GraphProbe-X achieves an average of 2.1 investigation steps with a 23% early stop rate. Crucially, extra investigation is executed only when it yields verified evidence gain."

---

## 3:30 – 4:00 | Conclusion & Call to Action
**[Visual: Decision Certificate display and links to GitHub / Blog]**  
**Speaker:** "GraphProbe-X doesn't search harder. It decides whether searching further is justified."  
**Speaker:** "Explore our interactive research console and open-source codebase on GitHub. Thank you."
