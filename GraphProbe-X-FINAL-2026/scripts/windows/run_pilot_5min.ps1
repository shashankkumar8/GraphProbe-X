$ErrorActionPreference="Stop"; $py=".\.venv\Scripts\python.exe"; if(-not(Test-Path $py)){$py="python"}
& $py -m scripts.detect_fields
& $py -m scripts.inspect_data --rules-only
& $py -m scripts.build_index
& $py -m benchmark.runner --pipeline rag --split public --limit 10
& $py -m benchmark.evaluator --pipeline rag
& $py -m benchmark.runner --pipeline graphrag --split public --limit 10
& $py -m benchmark.evaluator --pipeline graphrag
& $py -m benchmark.runner --pipeline agentic --split public --limit 10
& $py -m benchmark.evaluator --pipeline agentic
Write-Host "10-question pilot complete. Inspect results before the 100-question run." -ForegroundColor Green
