import os, json, re, subprocess, sys, pathlib
os.environ["LLM_PROVIDER"] = "mock"; os.environ["GPX_EMBED"] = "hash"; os.environ["GPX_CONFIG"] = "configs/sample.yaml"
from mcp_server.server import handle
from scripts.publish_results import render

def rpc(m, p=None, i=1): return handle({"jsonrpc": "2.0", "id": i, "method": m, "params": p or {}})
def call(n, a): r = rpc("tools/call", {"name": n, "arguments": a}); assert "error" not in r and not r["result"].get("isError"), r; return json.loads(r["result"]["content"][0]["text"])

def test_mcp_handshake_and_listing():
    assert rpc("initialize", {"protocolVersion": "2024-11-05"})["result"]["serverInfo"]["name"] == "graphprobe-x"
    assert handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
    names = {t["name"] for t in rpc("tools/list")["result"]["tools"]}; assert names == {"gpx_ask", "gpx_trace", "gpx_search", "gpx_entity", "gpx_verify_quote", "gpx_aggregate", "gpx_status"}
    assert rpc("nope")["error"]["code"] == -32601 and rpc("tools/call", {"name": "zzz"})["error"]["code"] == -32602

def test_mcp_tools_work_offline():
    a = call("gpx_ask", {"question": "Who won the 1990 Lumen Cup?", "pipeline": "agentic"}); assert a["answer"] and a["tokens"] > 0 and a["stop_reason"]
    hits = call("gpx_search", {"query": "1990 Lumen Cup winner", "k": 3}); assert len(hits) == 3
    v = call("gpx_verify_quote", {"chunk_id": hits[0]["chunk_id"], "quote": hits[0]["text"].split("\n", 1)[1][:40]}); assert v["verified"]
    assert not call("gpx_verify_quote", {"chunk_id": hits[0]["chunk_id"], "quote": "completely invented sentence here"})["verified"]
    assert call("gpx_verify_quote", {"chunk_id": "nope", "quote": "x" * 20})["verified"] is False
    assert call("gpx_status", {})["chunks"] > 0 and call("gpx_aggregate", {"question": "Who won it?"})["result"] is None
    t = call("gpx_trace", {"question": "Which country did the winner of the 1990 Lumen Cup represent?"}); assert t["trace"]["steps"][0]["tool"] == "initial_retrieval"
    assert call("gpx_entity", {"name": "Lumen Cup"}) is not None

def test_mcp_stdio_subprocess():
    reqs = "\n".join(json.dumps(x) for x in [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}, {"jsonrpc": "2.0", "method": "notifications/initialized"},
                                             {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}]) + "\nnot json\n"
    out = subprocess.run([sys.executable, "-m", "mcp_server.server"], input=reqs, capture_output=True, text=True, timeout=60).stdout.strip().splitlines()
    assert len(out) == 3 and json.loads(out[1])["result"]["tools"] and json.loads(out[2])["error"]["code"] == -32700

def test_http_api_and_traversal_guard():
    import threading, urllib.request, urllib.error
    from http.server import ThreadingHTTPServer
    from scripts.serve import H
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H); port = srv.server_address[1]; threading.Thread(target=srv.serve_forever, daemon=True).start()
    g = lambda p: urllib.request.urlopen(f"http://127.0.0.1:{port}{p}", timeout=30)
    assert b"GraphProbe-X" in g("/").read() and json.load(g("/api/status"))["chunks"] > 0
    sm = json.load(g("/api/summary")); assert sm.get("status") == "not_run" or "pipelines" in sm
    r = json.load(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{port}/api/ask", json.dumps({"question": "Who won the 1990 Lumen Cup?"}).encode(), {"Content-Type": "application/json"}), timeout=60))
    assert set(r["results"]) == {"rag", "graphrag", "agentic"} and r["results"]["agentic"]["trace"]["steps"]
    for bad in ("/../../AGENTS.md", "/..%2f..%2fAGENTS.md", "/%2e%2e/AGENTS.md"):
        try: g(bad); assert False, bad
        except urllib.error.HTTPError as e: assert e.code == 404
    try: urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{port}/api/ask", b'{"question": ""}', {"Content-Type": "application/json"}), timeout=30); assert False
    except urllib.error.HTTPError as e: assert e.code == 400
    srv.shutdown()

def test_results_render_from_summary_only():
    s = {"pipelines": {"rag": {"accuracy": .5, "completeness": .4, "avg_tokens": 100, "avg_latency_ms": 9, "avg_citations": 2, "llm_calls": 1, "fallback_call_rate": 0}},
         "agentic_vs_rag": {"n": 10, "rescued": 2, "regressed": 1, "avg_agentic_tax_tokens": 300, "avg_accuracy_gain": .1}, "falsification": {"distinct_sequences": 4, "passed": True}}
    md = render(s); assert "| Accuracy | 0.5 |" in md and "rescued **2**" in md and "PASS" in md

def test_site_has_no_external_dependencies_and_no_innerhtml():
    h = pathlib.Path("site/index.html").read_text(encoding="utf-8")
    assert not re.search(r"(src|href)=[\"']https?://", h) and "innerHTML" not in h
