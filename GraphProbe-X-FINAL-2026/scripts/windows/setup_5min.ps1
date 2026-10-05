$ErrorActionPreference = "Stop"
Write-Host "GraphProbe-X | Windows setup" -ForegroundColor Cyan
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python 3 is not installed/on PATH. Install Python 3.11+ and rerun." }
python --version
if (-not (Test-Path ".venv")) { python -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path ".env")) { Copy-Item .env.example .env; Write-Host "Created .env. Fill LLM_API_KEY and TG_* before real runs." -ForegroundColor Yellow }
New-Item -ItemType Directory -Force data\raw\corpus,data\raw\questions | Out-Null
Write-Host "Setup complete. Next: edit .env, copy corpus/questions, then run preflight_5min.ps1" -ForegroundColor Green
