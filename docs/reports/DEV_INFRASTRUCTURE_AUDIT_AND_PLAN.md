# Dev Infrastructure & Gateway – Audit + Plan

**Date:** 2026-01-31  
**Scope:** process-compose, Caddy gateway (:4000), config reload, CORS, frontend–backend wiring, WebSocket, platform variants.

---

## 1. Audit Summary

### 1.1 Gateway (Caddy :4000)

| Area | Status | Notes |
|------|--------|--------|
| Single entrypoint | ✅ | All external clients use `localhost:4000`; frontend uses `VITE_API_URL=http://localhost:4000`. |
| CORS preflight | ✅ | `route { }` preserves order; OPTIONS handled first; `Access-Control-Allow-Headers` includes `X-Bulk-Operation`, `X-Request-ID`. |
| CORS on /health | ✅ | GET /health and /health/ set `Access-Control-Allow-Origin` for :5173. |
| Routing order | ✅ | OPTIONS → /health → /api/v1/mcp/* → /api/v1/notifications* → /api/v1/* (Go) → /api/py/* → /ws/* → /docs* → prometheus → grafana → catch-all (frontend). |
| Notifications | ✅ | /api/v1/notifications, /api/v1/notifications/, /api/v1/notifications/* → Python :8000. |
| WebSocket | ✅ | Frontend uses gateway host for WS; `/api/v1/ws` matched by handle /api/v1/* → Go :8080. Caddy handle /ws/* exists but frontend uses /api/v1/ws. |
| Caddy config reload | ✅ | `caddy run ... --watch` reloads Caddyfile.dev on change. |
| Logging | ✅ | JSON logs to `.process-compose/logs/caddy-access.log`. |

**Gaps / risks**

- Only `http://localhost:5173` in CORS origins; no `127.0.0.1:5173` (minor; add if needed).
- /ws/* in Caddy proxies to Go with path /ws/…; Go serves /api/v1/ws. Unused unless something hits gateway /ws/…; low risk.

### 1.2 Process-Compose (main)

| Area | Status | Notes |
|------|--------|--------|
| Layering | ✅ | L1 infra → L2 temporal/prometheus → L3 exporters → L4 app (go, python, frontend) → L5 caddy, grafana. |
| Dependencies | ✅ | caddy depends on go-backend, python-backend, frontend healthy; grafana on prometheus; app on postgres, redis, nats, temporal. |
| Health probes | ✅ | HTTP/exec probes with sensible delays and thresholds. |
| Config reload (Caddy) | ✅ | Native `--watch`. |
| Config reload (Prometheus/Grafana) | ✅ | Optional watchexec via `scripts/run-with-config-watch.sh`; fallback: no watch. |
| Watchexec dependency | ⚠️ | Optional; doc’d in header and script. No lockfile/version. |
| Working dir | ✅ | prometheus, grafana use `working_dir: "."` for script + config paths. |

**Gaps / risks**

- Windows/Linux compose files not aligned with main: no `--watch` for Caddy, no config-watch script, different paths.
- No single “dev stack” doc that lists required tools (process-compose, caddy, watchexec optional, air, bun, etc.).

### 1.3 Scripts

| Script | Purpose | Audit note |
|--------|--------|------------|
| `run-with-config-watch.sh` | Wrap Prometheus/Grafana with watchexec for config reload | ✅ Usage clear; fallback when watchexec missing. |
| `run-air-in-backend.sh` | Start Go backend with Air | ✅ Referenced by process-compose. |
| `run-caddy.sh` | Run Caddy with --watch | Exists; process-compose invokes caddy binary directly. |
| `postgres-if-not-running.sh` etc. | Avoid “already in use” when services run externally | ✅ Used by main compose. |
| `test_gateway.sh` | Gateway tests | Present; not run from process-compose. |

**Gaps**

- `run-caddy.sh` uses `Caddyfile`; main compose uses `Caddyfile.dev` and `--watch` in-line. Inconsistency is minor (compose is source of truth).

### 1.4 Frontend–Gateway Wiring

| Area | Status | Notes |
|------|--------|--------|
| API base URL | ✅ | `VITE_API_URL=http://localhost:4000` in process-compose; client uses `getBackendURL()` / constants. |
| WebSocket URL | ✅ | Derived from API base (gateway host); `/api/v1/ws`. |
| X-Bulk-Operation | ✅ | Sent by hooks; CORS allows it. |
| Notifications API | ✅ | Gateway routes to Python; frontend calls `/api/v1/notifications/`. |

**Gaps**

- No single “gateway contract” doc in repo root; reference lives in docs (e.g. API_CONTRACTS_AND_GATEWAY_ARCHITECTURE.md).

### 1.5 Platform Variants

| File | Caddy | Config watch | Probes / deps |
|------|--------|--------------|----------------|
| process-compose.yaml | `--watch` | watchexec wrapper for prometheus, grafana | Full |
| process-compose.windows.yaml | No `--watch` | No wrapper | Minimal |
| process-compose.linux.yaml | Not checked | Not checked | Partial |

**Gap:** Windows (and Linux if used) lack gateway config reload and config-file watch parity with main.

---

## 2. Plan

### 2.1 High priority (gateway + daily dev)

1. **Align Windows/Linux compose with main (gateway + reload)**  
   - In `process-compose.windows.yaml`: add `--watch` to Caddy command; add optional config-watch (e.g. PowerShell wrapper or document “no watchexec on Windows” and keep simple restart).  
   - In `process-compose.linux.yaml` (if used): same Caddy `--watch`; add `run-with-config-watch.sh` for Prometheus/Grafana where bash is available.

2. **Document required/optional dev tools**  
   - Add a short “Dev stack” section to README or `00_START_HERE.md`: process-compose, Caddy, Go (air), Python (uvicorn), Node/bun, optional watchexec.  
   - Link to “Config / hot reload” comment in process-compose.yaml.

3. **Optional: CORS 127.0.0.1**  
   - If any client uses `http://127.0.0.1:5173`, add that origin to Caddy OPTIONS and /health responses (and to Go CORS if requests bypass Caddy).

### 2.2 Medium priority (consistency + docs)

4. **Single “gateway contract” entrypoint**  
   - In README or `00_START_HERE.md`, add one sentence + link: “All external traffic goes through the gateway (port 4000). See [API_CONTRACTS_AND_GATEWAY_ARCHITECTURE](link).”

5. **run-caddy.sh vs compose**  
   - Either: (a) change `run-caddy.sh` to use `Caddyfile.dev` and `--watch` and document “for standalone Caddy” or (b) leave as-is and add a one-line comment in script: “process-compose uses Caddyfile.dev and --watch in-line.”

6. **Watchexec**  
   - Optional: add `watchexec` to a “recommended dev tools” list or install script (e.g. `setup-native-dev.sh` or docs) without making it required.

### 2.3 Low priority / later

7. **Caddy /ws***  
   - Remove or narrow handle `/ws/*` if nothing will call gateway with path `/ws/...` to avoid confusion.

8. **Prometheus reload without restart**  
   - Already documented (POST /-/reload). Optionally add a tiny script `scripts/prometheus-reload.sh` that curls that endpoint, for convenience.

9. **Health dashboard**  
   - Optional: one-page doc or script that curls gateway /health, backend /health, and Python /health and reports status.

---

## 3. Checklist (from plan)

- [ ] process-compose.windows.yaml: Caddy `--watch`; document or add config reload.
- [ ] process-compose.linux.yaml: same as main for Caddy + config watch if applicable.
- [ ] README or 00_START_HERE: “Dev stack” (required/optional tools).
- [ ] README or 00_START_HERE: one-line “gateway contract” + link.
- [ ] run-caddy.sh: comment or switch to Caddyfile.dev + --watch.
- [ ] Optional: add 127.0.0.1:5173 to CORS.
- [ ] Optional: list watchexec in recommended tools/install doc.
- [ ] Optional: remove or restrict Caddy handle /ws/*.
- [ ] Optional: scripts/prometheus-reload.sh and/or health-check doc.

---

## 4. Out of scope for this audit

- Kubernetes/infra (separate configs).
- Backend internals (Go/Python) beyond “serves /api/v1/ws” and “notifications on Python”.
- Auth, rate limiting, TLS.
- Production Caddy config (no production Caddyfile in scope).
