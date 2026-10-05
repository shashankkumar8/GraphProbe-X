$ErrorActionPreference="Stop"; $py=".\.venv\Scripts\python.exe"; if(-not(Test-Path $py)){$py="python"}
# Production-only: public split. Hidden data is never referenced here.
& $py -m benchmark.runner --pipeline rag --split public --limit 100
& $py -m benchmark.evaluator --pipeline rag
& $py -m benchmark.runner --pipeline graphrag --split public --limit 100
& $py -m benchmark.evaluator --pipeline graphrag
& $py -m benchmark.runner --pipeline agentic --split public --limit 100
& $py -m benchmark.evaluator --pipeline agentic
& $py -m benchmark.metrics
& $py -m benchmark.error_analysis
& $py -m benchmark.report
Write-Host "PUBLIC 100 benchmark complete. Hidden set untouched." -ForegroundColor Green
