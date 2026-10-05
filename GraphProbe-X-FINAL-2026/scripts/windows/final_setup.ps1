$ErrorActionPreference = "Stop"
Write-Host "=== GraphProbe-X FINAL 2026 | Windows setup ===" -ForegroundColor Cyan
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python 3.11+ is required and must be on PATH." }
python --version
if (-not (Test-Path ".venv")) { python -m venv .venv }
$py = ".\.venv\Scripts\python.exe"
& $py -m pip install --upgrade pip
& $py -m pip install -r requirements.txt
if (-not (Test-Path ".env")) { Copy-Item .env.example .env }
New-Item -ItemType Directory -Force data\raw\corpus,data\raw\questions,results,cache\llm,data\processed | Out-Null
Write-Host "Public corpus/questions are already included in this package." -ForegroundColor Green
Write-Host "Next: edit .env (DO NOT paste secrets into chat), then run final_validate.ps1." -ForegroundColor Yellow
