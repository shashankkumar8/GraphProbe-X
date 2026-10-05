$ErrorActionPreference = "Stop"
$py = ".\.venv\Scripts\python.exe"; if (-not (Test-Path $py)) { $py = "python" }
Write-Host "=== GraphProbe-X FINAL | PUBLIC 100 benchmark ===" -ForegroundColor Cyan
& $py -m benchmark.runner --pipeline rag --split public --limit 100 --force
& $py -m benchmark.evaluator --pipeline rag
& $py -m benchmark.runner --pipeline graphrag --split public --limit 100 --force
& $py -m benchmark.evaluator --pipeline graphrag
& $py -m benchmark.runner --pipeline agentic --split public --limit 100 --force
& $py -m benchmark.evaluator --pipeline agentic
& $py -m benchmark.metrics
& $py -m benchmark.error_analysis
& $py -m benchmark.report
& $py -m scripts.publish_results
Write-Host "PUBLIC 100 complete. Hidden data was not used." -ForegroundColor Green
