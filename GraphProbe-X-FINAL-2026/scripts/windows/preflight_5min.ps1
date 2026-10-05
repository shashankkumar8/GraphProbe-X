$ErrorActionPreference = "Stop"
$py = ".\.venv\Scripts\python.exe"; if (-not (Test-Path $py)) { $py = "python" }
Write-Host "=== GraphProbe-X production preflight ===" -ForegroundColor Cyan
$checks=@("data/raw/questions/eval_public.jsonl","data/raw/corpus/corpus.jsonl")
foreach($p in $checks){ if(-not(Test-Path $p)){ throw "Missing: $p" } }
& $py -c "from ingest.loader import load_questions,load_corpus; from app.core.config import load_config; import os; c=load_config('configs/config.yaml'); q=load_questions(c,'public'); d=load_corpus(c); print({'public':len(q),'unique_qids':len({x['id'] for x in q}),'corpus':len(d),'provider_mock':os.getenv('LLM_PROVIDER')=='mock','llm_key_present':bool(os.getenv('LLM_API_KEY') or os.getenv('OPENROUTER_API_KEY')),'tg_host_present':bool(os.getenv('TG_HOST')),'tg_secret_present':bool(os.getenv('TG_SECRET')),'graph_backend':c['graph']['backend']})"
Write-Host "If counts are 100/2951, provider is real, and TG credentials are present, continue." -ForegroundColor Green
