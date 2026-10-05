"""LLMGateway: OpenRouter (or any OpenAI-compatible) primary -> documented fallback, disk cache, retries, full telemetry.
Every provider attempt is recorded on the Meter op. Cached calls replay their ORIGINAL token counts so accounting is reproducible."""
import os, time, json, hashlib, pathlib, requests
from .config import P

class Provider:
    def __init__(self, name, base, key, model):
        self.name, self.base, self.model = name, base.rstrip("/"), model
        self.headers = {"Authorization": f"Bearer {key}", "HTTP-Referer": "https://github.com/graphprobe-x", "X-Title": "GraphProbe-X"}

class LLM:
    def __init__(self, cfg):
        c = cfg["llm"]; e = os.environ
        key = e.get("LLM_API_KEY") or e.get("OPENROUTER_API_KEY", "")
        self.providers = [Provider("primary", e.get("LLM_BASE_URL", "https://openrouter.ai/api/v1"), key, e.get("LLM_MODEL", c.get("model", "openai/gpt-4o-mini")))]
        if e.get("LLM_FALLBACK_MODEL"):
            self.providers.append(Provider("fallback", e.get("LLM_FALLBACK_BASE_URL", e.get("LLM_BASE_URL", "https://openrouter.ai/api/v1")),
                                           e.get("LLM_FALLBACK_API_KEY", key), e["LLM_FALLBACK_MODEL"]))
        self.model = self.providers[0].model
        self.temp, self.max_out = c.get("temperature", 0), c.get("max_output_tokens", 500)
        self.json_mode, self.mtp = c.get("json_mode", True), c.get("max_tokens_param", "max_tokens")
        self.retries, self.timeout, self.pv = c.get("retries", 3), c.get("timeout_s", 90), c.get("prompt_version", "v1")
        self.cache_dir = pathlib.Path(c.get("cache_dir", "cache/llm")); self.cache_dir = self.cache_dir if self.cache_dir.is_absolute() else P(str(self.cache_dir))
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key(self, system, user, max_out, json_mode, op):
        return hashlib.sha256(json.dumps([self.pv, self.model, self.temp, max_out, json_mode, op, system, user]).encode()).hexdigest()

    def _cget(self, k):
        f = self.cache_dir / k[:2] / f"{k}.json"
        try: return json.load(open(f)) if f.exists() else None
        except Exception: return None

    def _cput(self, k, v):
        d = self.cache_dir / k[:2]; d.mkdir(exist_ok=True); tmp = d / f"{k}.{os.getpid()}.tmp"
        json.dump(v, open(tmp, "w")); os.replace(tmp, d / f"{k}.json")

    def _call(self, pv, system, user, max_out, use_json):
        body = {"model": pv.model, "temperature": self.temp, self.mtp: max_out,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        if use_json and self.json_mode: body["response_format"] = {"type": "json_object"}
        t = time.time()
        try: r = requests.post(f"{pv.base}/chat/completions", json=body, headers=pv.headers, timeout=self.timeout)
        except requests.Timeout: return "timeout", None, 0
        except requests.RequestException: return "conn_error", None, 0
        ms = (time.time() - t) * 1000
        if r.status_code != 200: return str(r.status_code), None, ms
        try: d = r.json()
        except ValueError: return "bad_json", None, ms
        if d.get("error"): return "provider_error", None, ms
        text = ((d.get("choices") or [{}])[0].get("message") or {}).get("content")
        return ("200", d, ms) if text else ("empty", None, ms)

    def chat(self, system, user, meter=None, op="llm", json_mode=False, max_out=None):
        max_out = max_out or self.max_out; k = self._key(system, user, max_out, json_mode, op); hit = self._cget(k)
        if hit:
            if meter is not None: meter.add(op, hit["tin"], hit["tout"], hit["ms"], hit["est"], hit["provider"], True, [])
            return hit["text"]
        attempts = []
        for pv in self.providers:
            use_json = json_mode
            for i in range(self.retries):
                status, d, ms = self._call(pv, system, user, max_out, use_json); attempts.append({"provider": pv.name, "model": pv.model, "status": status})
                if status == "200":
                    text = d["choices"][0]["message"]["content"]; u = d.get("usage") or {}
                    est = not (u.get("prompt_tokens") and u.get("completion_tokens") is not None)
                    tin = u.get("prompt_tokens") or (len(system) + len(user)) // 4; tout = u.get("completion_tokens") or len(text) // 4
                    self._cput(k, {"text": text, "tin": tin, "tout": tout, "ms": ms, "est": est, "provider": pv.name, "model": pv.model})
                    if meter is not None: meter.add(op, tin, tout, ms, est, pv.name, False, attempts)
                    return text
                if status == "400" and use_json: use_json = False; continue      # model lacks JSON mode -> retry plain
                if status in ("401", "402", "403"): break                        # auth / credits exhausted: switch provider now
                time.sleep(min(2 ** i, 8))                                       # 429 / 5xx / timeout / empty: backoff
        raise RuntimeError(f"all providers failed: {attempts}")

def get_llm(cfg):
    if os.environ.get("LLM_PROVIDER") == "mock" or cfg["llm"].get("provider") == "mock":
        from .mock import MockLLM
        return MockLLM()
    return LLM(cfg)
