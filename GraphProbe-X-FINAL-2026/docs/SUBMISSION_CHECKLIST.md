# GraphProbe-X Round 1 Submission Checklist

**Deadline:** Oct 6, 2026
**Status:** IN PROGRESS

## Deliverables

### 1. Code Repository ✓
- [x] All source code in `app/`, `benchmark/`, `ingest/`, `scripts/`
- [x] Tests pass: `pytest -q tests` (25/25)
- [x] `.gitignore` configured
- [x] `requirements.txt` pinned
- [ ] Final audit and secret scan

### 2. Benchmarks
- [ ] RAG pipeline 100q results
- [ ] GraphRAG pipeline 100q results
- [ ] Agentic pipeline 100q results
- [ ] Metrics computed
- [ ] Error analysis complete

### 3. Hidden Evaluation
- [ ] Hidden 50 questions export

### 4. Documentation
- [ ] README.md with architecture and results
- [ ] AGENTS.md project rules
- [ ] Architecture diagram
- [ ] Demo script

### 5. Dashboard
- [ ] results/dashboard.html
- [ ] results/summary.json with metrics

### 6. Submission Form
- [ ] Team/participant name
- [ ] Email address
- [ ] Project title & description
- [ ] Links to repo/dashboard

## Known Issues
- **Embedder:** Using hash512 due to Windows torch/DLL issue (documented in results)
- **Benchmarks:** Partial results due to timeout (resumable)

## Next Steps
1. Complete benchmark runs
2. Generate evaluation metrics
3. Finalize dashboard
4. Push to GitHub
5. Submit via Google Form

---
Last updated: 2026-10-04T20:22 UTC
