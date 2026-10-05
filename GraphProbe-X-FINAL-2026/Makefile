PY=python
install:      ; pip install -r requirements.txt
smoke:        ; LLM_PROVIDER=mock GPX_EMBED=hash GPX_CONFIG=configs/sample.yaml sh -c "$(PY) scripts/make_sample.py && $(PY) -m scripts.build_index && $(PY) -m pytest -q tests"
inspect:      ; $(PY) -m scripts.inspect_data --taxonomy
index:        ; $(PY) -m scripts.build_index
tg:           ; $(PY) -m scripts.tg_setup
rag:          ; $(PY) -m benchmark.runner --pipeline rag && $(PY) -m benchmark.evaluator --pipeline rag
graphrag:     ; $(PY) -m benchmark.runner --pipeline graphrag && $(PY) -m benchmark.evaluator --pipeline graphrag
closed:       ; $(PY) -m benchmark.runner --pipeline closed_book && $(PY) -m benchmark.evaluator --pipeline closed_book
matched:      ; $(PY) -m benchmark.runner --pipeline rag_matched && $(PY) -m benchmark.evaluator --pipeline rag_matched   # run AFTER rag+agentic
audit:        ; $(PY) -m scripts.final_audit
agentic:      ; $(PY) -m benchmark.runner --pipeline agentic && $(PY) -m benchmark.evaluator --pipeline agentic
analysis:     ; $(PY) -m benchmark.metrics && $(PY) -m benchmark.error_analysis && $(PY) -m benchmark.report
ablation:     ; $(PY) -m benchmark.ablation --n 30
hidden:       ; $(PY) -m benchmark.hidden_export --run
demo:         ; streamlit run frontend/app.py
test:         ; $(PY) -m pytest -q tests
serve:        ; $(PY) -m scripts.serve --port 8000
mcp:          ; $(PY) -m mcp_server.server
publish:      ; $(PY) -m scripts.publish_results
