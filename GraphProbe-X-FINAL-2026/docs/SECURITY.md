# Security Audit & Secrets Management Policy

## Secrets Isolation
- All API keys, OpenRouter tokens, TigerGraph database passwords, and secrets are strictly stored in local `.env` files or system environment variables.
- `.env` and `cache/` directories are explicitly ignored in `.gitignore`.
- Precomputed public demo traces (`site/data/demo_fixtures.json`) contain zero credentials or private keys.

## Automated Secret Scanning
Run security scan prior to release:
```bash
python -m scripts.release_gate
```

The release gate inspects all committed files for exposed API key patterns (`sk-or-`, `bearer`, passwords) and fails if any plain-text secrets are detected.
