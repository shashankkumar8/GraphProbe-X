# Runbook cheat-sheet (full narrative guide is in the chat hand-off)
```
# .env is auto-loaded (no export needed)
make smoke                      # offline plumbing (mock)   | make inspect  -> fix configs/config.yaml data.fields
make index                      # BM25 + dense + entity graph
python -m benchmark.runner --pipeline rag --limit 10 && python -m benchmark.evaluator --pipeline rag   # PILOT first (check $ cost via meter)
make rag closed                 # full 100 (resumable; rerun the same command after any crash)
make tg   # then set graph.backend: tigergraph in configs/config.yaml
make graphrag
python -m benchmark.runner --pipeline agentic --limit 10 --force   # read traces, tune configs only
make agentic matched analysis ablation audit
make hidden                     # only after FREEZE (commit)
```
Resume rule: errored rows are retried automatically; the LLM cache makes reruns free. Bump `llm.prompt_version` after ANY prompt edit.
