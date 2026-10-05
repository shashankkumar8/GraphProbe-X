# GraphProbe-X — 5-minute Windows run card

This is the shortest reliable path. It assumes Python is already installed and that you already have the public corpus/questions and provider credentials. **It cannot make external credentials or a TigerGraph cluster appear; those are the only external prerequisites.**

## 0. Extract
Open PowerShell in the extracted `GraphProbe-X` folder.

## 1. Install once
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\windows\setup_5min.ps1
```

## 2. Configure `.env` — never paste secrets into chat
Open `.env` and fill:
```text
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=<YOUR_NEW_KEY>
LLM_MODEL=<MODEL_SLUG>
TG_HOST=https://<YOUR-SOLUTION>.i.tgcloud.io
TG_USER=tigergraph
TG_PASS=<if your deployment uses password auth>
TG_GRAPH=GraphProbeX
TG_SECRET=<YOUR_TIGERGRAPH_SECRET>
```
OpenRouter documents API-key creation and its OpenAI-compatible endpoint. TigerGraph Cloud supports a free tier and its current pyTigerGraph Cloud connection uses host + graph + user secret. See the official links in the main run guide.

## 3. Copy real public data
```powershell
New-Item -ItemType Directory -Force data\raw\questions,data\raw\corpus | Out-Null
Copy-Item "C:\Users\LENOVO\Downloads\eval_public.jsonl" "data\raw\questions\eval_public.jsonl" -Force
Copy-Item "C:\Users\LENOVO\Downloads\corpus.jsonl" "data\raw\corpus\corpus.jsonl" -Force
```
Expected: **100 questions / 2,951 documents**.

## 4. Preflight
```powershell
.\scripts\windows\preflight_5min.ps1
```
Do not continue if `provider_mock=True`, the key is absent, or TigerGraph credentials are absent.

## 5. Build + pilot
```powershell
.\scripts\windows\run_pilot_5min.ps1
```
Then configure `graph.backend: tigergraph` in `configs/config.yaml`, and load the graph:
```powershell
.\.venv\Scripts\python.exe -m scripts.tg_setup
```
If schema installation fails on your TigerGraph version, use the two GSQL files under `graph/` in Savanna/GraphStudio, then rerun `-m scripts.tg_setup --skip-schema`.

## 6. Public benchmark
Only after the 10-question pilot is sane:
```powershell
.\scripts\windows\run_public_100.ps1
```
This script references **public only**. It does not read the hidden file.

## 7. Dashboard
```powershell
.\scripts\windows\start_dashboard.ps1
```
Open `http://127.0.0.1:8000`.

## 8. MCP
```powershell
.\.venv\Scripts\python.exe -m mcp_server.server
```
For Claude Code:
```powershell
claude mcp add graphprobe-x -- .\.venv\Scripts\python.exe -m mcp_server.server
```

## If you do NOT have TigerGraph yet
Create a TigerGraph Cloud cluster from the official Cloud console, choose a blank solution for your own schema, wait until Ready, open the Admin/User Management area and create a user secret. The current TigerGraph documentation says free-tier clusters are available subject to limits and that Cloud connections use the solution hostname, graph name and secret. This provisioning step is external and may take longer than five minutes.

## If you do NOT have an LLM key yet
Create an OpenRouter API key from the dashboard, put it only in local `.env`, and never commit `.env`. OpenRouter states that its API is OpenAI-compatible and can be used by changing the base URL/key.

## Final submission order
1. `python -m pytest -q tests`
2. public RAG/GraphRAG/Agentic artifacts
3. `python -m benchmark.metrics`
4. `python -m benchmark.error_analysis`
5. `python -m benchmark.report`
6. freeze code/config/prompts
7. only then run hidden export/audit required by the official submission workflow

**Never tune on hidden answers. Never report mock/synthetic numbers as benchmark results.**
