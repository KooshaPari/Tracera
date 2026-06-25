# Tracera Quickstart

```bash
# 1) create environment
python -m venv .venv
. .venv/bin/activate

# 2) install dependencies (repo-specific; currently placeholder package)
pip install -r requirements.txt

# 3) run API app (development)
python -m uvicorn tracertm.api.main:app --reload

# 4) health check
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/healthz
```

## Optional: start with token-aware middleware

Set one env var for local signature hardening and API authorization checks:

```bash
export TRACERA_JWT_SECRET=<development-secret>
export TRACERA_JWT_AUDIENCE=<aud>
export TRACERA_JWT_ISSUER=<iss>
```

## API verification

After startup, confirm one endpoint schema (protected route) returns 401 without
`Authorization` to verify middleware is active.

```bash
curl -i -X GET http://127.0.0.1:8000/api/v1/evidence
```
