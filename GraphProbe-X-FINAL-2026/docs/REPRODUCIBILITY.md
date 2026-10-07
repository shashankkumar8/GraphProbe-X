# GraphProbe-X Reproducibility Guide

All benchmark runs, evaluation metrics, and interactive console sessions in GraphProbe-X are fully auditable and reproducible.

---

## 1. Installation & Environment

```bash
git clone https://github.com/shashankkumar8/GraphProbe-X.git
cd GraphProbe-X
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
```

---

## 2. Environment Configuration

Copy `.env.example` to `.env` and fill in credentials:

```ini
OPENROUTER_API_KEY=your_openrouter_key_here
TIGERGRAPH_HOST=https://graphprobe-x.i.tgcloud.io:9000
TIGERGRAPH_SECRET=your_tigergraph_secret_here
```

---

## 3. Running Unit Tests

```bash
python -m pytest tests/
```

Expected output: `25 passed`.

---

## 4. Generating Benchmark Metrics & Form Answers

```bash
# Process raw benchmark result files and build final metrics:
python -m scripts.generate_submission_metrics

# Generate submission form answers:
python -m scripts.generate_form_answers

# Run full release gate validation:
python -m scripts.release_gate
```

---

## 5. Serving the Demo Console Locally

```bash
python -m scripts.serve
```
Open browser at `http://localhost:8000/site/index.html`.

---

## 6. Manifests & Verification Snapshots
- Benchmark run configuration: `results/run_manifest.json`
- Dataset metadata: `results/dataset_manifest.json`
- Config snapshot: `results/config_snapshot.yaml`
- Execution logs: `results/*.log`
