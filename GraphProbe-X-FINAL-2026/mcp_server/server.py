"""Minimal MCP stdio server (JSON-RPC 2.0, newline-delimited). No third-party deps. python -m mcp_server.server"""
import sys, json
from . import tools as T

def handle(msg):
    mid, m, p = msg.get("id"), msg.get("method"), msg.get("params") or {}
    if mid is None: return None                                              # notifications (initialized, cancelled...) need no reply
    ok = lambda r: {"jsonrpc": "2.0", "id": mid, "result": r}
    if m == "initialize":
        return ok({"protocolVersion": p.get("protocolVersion", "2024-11-05"), "capabilities": {"tools": {}}, "serverInfo": {"name": "graphprobe-x", "version": "1.0.0"}})
    if m == "ping": return ok({})
    if m == "tools/list": return ok({"tools": [{"name": n, "description": d, "inputSchema": s} for n, (_, d, s) in T.TOOLS.items()]})
    if m == "tools/call":
        name, args = p.get("name"), p.get("arguments") or {}
        if name not in T.TOOLS: return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": f"unknown tool {name}"}}
        try: return ok({"content": [{"type": "text", "text": json.dumps(T.TOOLS[name][0](args), ensure_ascii=False, default=str)}]})
        except Exception as e: return ok({"isError": True, "content": [{"type": "text", "text": f"{type(e).__name__}: {e}"[:500]}]})
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"method not found: {m}"}}

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try: r = handle(json.loads(line))
        except json.JSONDecodeError: r = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}
        if r is not None: sys.stdout.write(json.dumps(r) + "\n"); sys.stdout.flush()

if __name__ == "__main__": main()
