# Environment Variable Mapping & Validation

**Last validated:** 2026-02-13

This document maps all environment variables used by TraceRTM services to their sources and validates presence in `.env.example` and `config/process-compose.yaml`.

## Load Order

1. **Root `.env`** – Loaded by `scripts/python/dev-start-with-preflight.py` before starting process-compose
2. **process-compose** – Inherits parent env; `environment:` blocks add/override per service
3. **Frontend** – Vite loads `frontend/apps/web/.env.local` (and `.env`); process-compose passes `VITE_*` vars

---

## Go Backend (`go-backend`)

| Variable | Required | Source | process-compose | .env.example |
|----------|----------|--------|-----------------|---------------|
| `AUTH_PROVIDER` | Yes | Hardcoded | ✓ `authkit` | — |
| `REALTIME_PROVIDER` | Yes | Hardcoded | ✓ `nats` | — |
| `WORKOS_CLIENT_ID` | Yes (AuthKit) | .env | ✓ `${WORKOS_CLIENT_ID}` | ✓ |
| `WORKOS_API_KEY` | Yes (AuthKit) | .env | ✓ `${WORKOS_API_KEY}` | ✓ |
| `WORKOS_REDIRECT_URI` | Yes (AuthKit) | .env | ✓ `${WORKOS_REDIRECT_URI:-...}` | ✓ |
| `WORKOS_AUTHKIT_DOMAIN` | Yes (AuthKit) | .env | ✓ `${WORKOS_AUTHKIT_DOMAIN}` | ✓ |
| `WORKOS_API_BASE_URL` | No | .env | ✓ `${WORKOS_API_BASE_URL:-...}` | — |
| `DATABASE_URL` | Yes | .env | ✓ (from DB_*) | ✓ |
| `DB_PASSWORD` | Yes | .env | ✓ `${DB_PASSWORD:-...}` | ✓ (as DB_PASSWORD) |
| `REDIS_URL` | Yes | .env | ✓ | ✓ |
| `NATS_URL` | Yes | .env | ✓ | ✓ |
| `TEMPORAL_HOST` | Yes | .env | ✓ | ✓ |
| `JWT_SECRET` | Yes | .env | ✓ `${JWT_SECRET}` | ✓ |
| `CSRF_SECRET` | Yes | .env | ✓ `${CSRF_SECRET}` | ✓ |
| `CORS_ALLOWED_ORIGINS` | No | .env | ✓ (with default) | ✓ |
| `AUTHKIT_JWT_SECRET` | Yes (AuthKit) | .env | ✓ `${AUTHKIT_JWT_SECRET}` | ✓ |
| `PORT` | No | — | ✓ 8080 | — |
| `GRPC_PORT` | No | — | ✓ 9091 | — |
| `PYTHON_BACKEND_URL` | No | — | ✓ | ✓ |

---

## Python Backend (`python-backend`)

| Variable | Required | Source | process-compose | .env.example |
|----------|----------|--------|-----------------|---------------|
| `WORKOS_CLIENT_ID` | Yes (AuthKit) | .env | ✓ | ✓ |
| `WORKOS_API_KEY` | Yes (AuthKit) | .env | ✓ | ✓ |
| `WORKOS_REDIRECT_URI` | Yes (AuthKit) | .env | ✓ | ✓ |
| `WORKOS_AUTHKIT_DOMAIN` | Yes (AuthKit) | .env | ✓ | ✓ |
| `DATABASE_URL` | Yes | .env | ✓ | ✓ |
| `REDIS_URL` | Yes | .env | ✓ | ✓ |
| `NATS_URL` | Yes | .env | ✓ | ✓ |
| `TEMPORAL_HOST` | Yes | .env | ✓ | ✓ |
| `GO_BACKEND_URL` | No | — | ✓ | ✓ |
| `OPENAI_API_KEY` | No | .env | ✓ | ✓ |
| `ANTHROPIC_API_KEY` | No | .env | ✓ | ✓ |
| `CORS_ORIGINS` | No | .env | ✓ (with default) | ✓ |

---

## Frontend (`frontend`)

| Variable | Required | Source | process-compose | frontend .env.example |
|----------|----------|--------|-----------------|------------------------|
| `VITE_API_URL` | Yes | process-compose | ✓ `http://localhost:4000` | ✓ |
| `VITE_WS_URL` | No | process-compose | ✓ `${VITE_WS_URL:-ws://localhost:4000}` | ✓ |
| `VITE_WORKOS_CLIENT_ID` | Yes (AuthKit) | .env → process-compose | ✓ `${WORKOS_CLIENT_ID}` | ✓ |
| `VITE_WORKOS_AUTH_DOMAIN` | No (prod) | .env → process-compose | ✓ `${WORKOS_AUTHKIT_DOMAIN}` | ✓ |

---

## Shared WorkOS Mapping (Backend ↔ Frontend)

| Root .env | Go Backend | Python Backend | Frontend (VITE_) |
|-----------|------------|----------------|------------------|
| `WORKOS_CLIENT_ID` | ✓ direct | ✓ direct | `VITE_WORKOS_CLIENT_ID` |
| `WORKOS_API_KEY` | ✓ direct | ✓ direct | — (backend only) |
| `WORKOS_REDIRECT_URI` | ✓ direct | ✓ direct | — (backend only) |
| `WORKOS_AUTHKIT_DOMAIN` | ✓ direct | ✓ direct | `VITE_WORKOS_AUTH_DOMAIN` |

---

## Gaps Fixed (2026-02-13)

1. **`.env.example`** – Added `WORKOS_AUTHKIT_DOMAIN`, `CSRF_SECRET`, `AUTHKIT_JWT_SECRET` to Auth section
2. **process-compose frontend** – Added `VITE_WS_URL` (default: `ws://localhost:4000`)
3. **process-compose go-backend** – Added explicit `JWT_SECRET`, `CSRF_SECRET`, `AUTHKIT_JWT_SECRET`, `CORS_ALLOWED_ORIGINS`
4. **process-compose python-backend** – Added `CORS_ORIGINS`

---

## Validation Checklist

- [ ] All WorkOS vars in root `.env` when using AuthKit
- [ ] `WORKOS_REDIRECT_URI` matches gateway URL (e.g. `http://localhost:4000/auth/callback`)
- [ ] Frontend `VITE_WORKOS_*` matches backend `WORKOS_*` (same client ID, domain)
- [ ] `JWT_SECRET`, `CSRF_SECRET` at least 32 chars (generate: `openssl rand -hex 32`)
- [ ] Run `make dev` or `make dev-tui` (uses dev-start-with-preflight which loads .env)
