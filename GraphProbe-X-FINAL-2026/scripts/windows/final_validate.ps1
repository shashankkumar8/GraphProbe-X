$ErrorActionPreference = "Stop"
$py = ".\.venv\Scripts\python.exe"; if (-not (Test-Path $py)) { $py = "python" }
Write-Host "=== GraphProbe-X FINAL | validation ===" -ForegroundColor Cyan
& $py -m compileall -q app ingest benchmark scripts mcp_server
& $py -m pytest -q
& $py -c "from ingest.loader import load_questions,load_corpus; from app.core.config import load_config; c=load_config(); q=load_questions(c,'public'); d=load_corpus(c); print('PUBLIC QUESTIONS =',len(q)); print('CORPUS DOCS =',len(d)); assert len(q)==100; assert len(d)==2951"
Write-Host "Validation passed: syntax + tests + 100 public questions + 2951 corpus docs." -ForegroundColor Green
