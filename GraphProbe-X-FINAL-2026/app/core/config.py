import os, pathlib, yaml
ROOT = pathlib.Path(__file__).resolve().parents[2]

def _dotenv():
    f = ROOT / ".env"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1); v = v.strip().strip('"').strip("'")
                if v and k.strip() not in os.environ: os.environ[k.strip()] = v      # empty values ignored; real env wins
_dotenv()

def _merge(a, b):
    for k, v in (b or {}).items():
        if isinstance(v, dict) and isinstance(a.get(k), dict): _merge(a[k], v)
        else: a[k] = v
    return a

def load_config(path=None, overrides=None):
    path = pathlib.Path(path or os.environ.get("GPX_CONFIG", ROOT / "configs" / "config.yaml"))
    if not path.is_absolute(): path = ROOT / path
    cfg = yaml.safe_load(open(path))
    if "_base" in cfg:
        base = load_config(path.parent / cfg.pop("_base"))
        cfg = _merge(base, cfg)
    return _merge(cfg, overrides or {})

def P(rel): return ROOT / rel
