$ErrorActionPreference = "Stop"
$py = ".\.venv\Scripts\python.exe"; if (-not (Test-Path $py)) { $py = "python" }
Write-Host "=== GraphProbe-X FINAL | 10-question pilot ===" -ForegroundColor Cyan
& $py -m scripts.detect_fields
& $py -m scripts.inspect_data --rules-only
& $py -m scripts.build_index
& $py -m benchmark.runner --pipeline rag --split public --limit 10 --force
& $py -m benchmark.evaluator --pipeline rag
& $py -m benchmark.runner --pipeline graphrag --split public --limit 10 --force
& $py -m benchmark.evaluator --pipeline graphrag
& $py -m benchmark.runner --pipeline agentic --split public --limit 10 --force
& $py -m benchmark.evaluator --pipeline agentic
Write-Host "Pilot complete. Inspect results before running the 100-question benchmark." -ForegroundColor Green
