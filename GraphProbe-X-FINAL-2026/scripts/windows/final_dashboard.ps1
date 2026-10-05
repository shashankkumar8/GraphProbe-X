$py = ".\.venv\Scripts\python.exe"; if (-not (Test-Path $py)) { $py = "python" }
Write-Host "GraphProbe-X dashboard: http://127.0.0.1:8000" -ForegroundColor Cyan
& $py -m scripts.serve --port 8000
