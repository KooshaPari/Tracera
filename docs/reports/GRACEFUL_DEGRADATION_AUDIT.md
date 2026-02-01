# Graceful Degradation / Silent Failure Audit

Per **CLAUDE.md**: require dependencies where they belong; fail clearly, not silently. No optionality or silent fallbacks as a substitute for fixing or starting the real dependency.

## Antipatterns Found and Status

### 1. **Startup: Go client and NATS made optional** — FIXED
- **Location**: `src/tracertm/api/main.py` (lifespan / startup)
- **Antipattern**: `except Exception: app.state.go_client = None` and `except Exception: app.state.nats_client = None; app.state.event_bus = None` with comment "Don't fail startup if …"
- **Preflight**: `build_api_checks()` marks `go-backend` and `nats` as **required=True**.
- **Fix**: Fail startup when Go client or NATS init fails: re-raise (or raise with clear message naming the failing service).

### 2. **list_items: DB/schema errors return empty** — FIXED
- **Location**: `src/tracertm/api/main.py` (~1151–1156)
- **Antipattern**: `except (OperationalError, ProgrammingError): logger.warning(...); total_count = 0; items = []` — returns empty list when table/schema not ready.
- **Fix**: Raise `HTTPException(status_code=503, detail="Database/schema not ready: ...")` so operators see the failure.

### 3. **list_notifications: Any exception returns []** — FIXED
- **Location**: `src/tracertm/api/routers/notifications.py` (~58–60)
- **Antipattern**: `except Exception: logger.warning(...); return []` — hides DB/other failures.
- **Fix**: Re-raise or raise `HTTPException(status_code=500, detail=...)` so the failure is visible.

### 4. **Event handlers: Cache invalidation errors swallowed** — FIXED
- **Location**: `src/tracertm/api/main.py` (NATS event handlers: item.created, item.updated, item.deleted, link.created, link.deleted, project.updated, project.deleted)
- **Antipattern**: `try: await cache_service.clear_prefix(...); except Exception as e: logger.error(...)` — continues without failing. Redis is required; cache failures should not be silent.
- **Fix**: Re-raise `RedisUnavailableError` (and optionally other failures) so event processing fails clearly.

### 5. **Workflow run recording: Failure returns "queued"** — FIXED
- **Location**: `src/tracertm/api/main.py` (multiple workflow trigger endpoints: trigger_workflow, trigger_graph_snapshot, trigger_graph_validation, trigger_graph_export, trigger_graph_diff, etc.)
- **Antipattern**: `try: await repo.create_run(...); except Exception: logger.warning(...); return {"status": "queued", "result": result}` — client is told "queued" even when recording failed.
- **Fix**: Raise `HTTPException(status_code=500, detail="Failed to record workflow run: ...")` when `create_run` fails.

### 6. **Auth /me: User lookup exception → user=None** — DOCUMENTED
- **Location**: `src/tracertm/api/main.py` (~1725–1726)
- **Pattern**: `except Exception: user = None` when fetching user from WorkOS. Response still 200 with `user: null`.
- **Note**: Arguably acceptable if "user" is optional (e.g. WorkOS down → show claims without profile). If user is required for /me, this should raise. Left as-is; document as known optional-user path.

### 7. **Auth logout: Logout URL failure → log only** — DOCUMENTED
- **Location**: `src/tracertm/api/main.py` (~1783–1784)
- **Pattern**: `except Exception: logger.warning(...)`; still return 200 with `logout_url: null`.
- **Note**: Logout URL can be optional (frontend can redirect without it). Left as-is; document as optional logout URL.

### 8. **Health endpoint: Component failures → 200 with unhealthy** — FIXED
- **Location**: `src/tracertm/api/main.py` (`/api/v1/health`)
- **Antipattern**: Each component try/except sets `components["x"] = {"status": "unhealthy", ...}` and `status = "unhealthy"` but response was still 200.
- **Fix**: When `status == "unhealthy"`, return **503** with the same body and a `detail` field listing unhealthy components (e.g. `"Unhealthy components: redis; nats"`). Operators and load balancers see 503 and the named failing components.

---

## Summary

- **Fixed**: Startup (Go/NATS), list_items DB errors, list_notifications exception swallow, event-handler cache swallow, workflow run recording swallow, **health 503 when any component unhealthy**.
- **Documented / left as-is**: Auth /me user=None (optional user), logout URL (optional).
