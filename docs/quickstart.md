# Tracera Quickstart

## 1) Bootstrap

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows (PowerShell)
. .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

## 2) Configure runtime security inputs

```bash
export TRACERA_JWT_SECRET=<production-secret>
export TRACERA_JWT_AUDIENCE=tracera-api
export TRACERA_JWT_ISSUER=tracera
```

## 3) Start API

```bash
python -m uvicorn tracertm.api.main:app --reload --port 8000
```

## 4) Verify hardening points

```bash
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/ready
curl -i http://127.0.0.1:8000/api/v1/evidence
```

Expected behavior:

- `/health` and `/ready` return 200 without auth (public probes).
- `/api/v1/...` returns `401` until bearer token is supplied to `Authorization`.
- Middleware validation errors return JSON with `detail`.

## 5) Authenticated smoke checks

```bash
TOKEN="Bearer <jwt>"
curl -i -H "Authorization: $TOKEN" http://127.0.0.1:8000/api/v1/evidence
curl -i -H "Authorization: $TOKEN" -H "Content-Type: application/json" \
  -d '{"sources":["demo"],"targets":["demo"]}' \
  http://127.0.0.1:8000/api/v1/coverage-matrix
```

## 6) API surface checks

- Review stubs and route coverage in [`API_REFERENCE.md`](API_REFERENCE.md).
- Confirm FR→endpoint mapping in
  [`docs/governance/policy/endpoint_traceability_map.md`](governance/policy/endpoint_traceability_map.md).
