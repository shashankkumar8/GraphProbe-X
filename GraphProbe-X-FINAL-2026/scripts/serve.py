"""Local dashboard + API. python -m scripts.serve [--port 8000]. Binds 127.0.0.1 only; set GPX_CORS_ORIGIN to allow ONE external origin (e.g. your Vercel site)."""
import json, os, argparse, pathlib
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from app.core.config import load_config, P
from mcp_server import tools as T

SITE = P("site"); MIME = {".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".json": "application/json", ".svg": "image/svg+xml"}

class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else json.dumps(body, default=str).encode()
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(b))); self.send_header("X-Content-Type-Options", "nosniff")
        if os.environ.get("GPX_CORS_ORIGIN"): self.send_header("Access-Control-Allow-Origin", os.environ["GPX_CORS_ORIGIN"]); self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers(); self.wfile.write(b)
    def do_OPTIONS(self): self._send(204, b"")
    def do_GET(self):
        path = self.path.split("?")[0]
        try:
            if path == "/api/status": return self._send(200, T.status())
            if path == "/api/summary":
                f = P(load_config()["paths"]["results"]) / "summary.json"
                return self._send(200, json.loads(f.read_text()) if f.exists() else {"status": "not_run"})
            rel = "index.html" if path in ("/", "") else path.lstrip("/")
            f = (SITE / rel).resolve()
            if SITE.resolve() not in f.parents and f != SITE.resolve() / "index.html" or not f.is_file(): return self._send(404, {"error": "not found"})
            return self._send(200, f.read_bytes(), MIME.get(f.suffix, "application/octet-stream"))
        except Exception as e: return self._send(500, {"error": repr(e)[:300]})
    def do_POST(self):
        if self.path != "/api/ask": return self._send(404, {"error": "not found"})
        try:
            n = int(self.headers.get("Content-Length", 0))
            if n > 10_000: return self._send(413, {"error": "body too large"})
            q = str(json.loads(self.rfile.read(n)).get("question", "")).strip()
            if not q or len(q) > 500: return self._send(400, {"error": "question must be 1-500 chars"})
            return self._send(200, T.ask_all({"question": q}))
        except Exception as e: return self._send(500, {"error": repr(e)[:300]})
    def log_message(self, *a): pass

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--port", type=int, default=8000); a = ap.parse_args()
    print(f"GraphProbe-X dashboard: http://127.0.0.1:{a.port}"); ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()
