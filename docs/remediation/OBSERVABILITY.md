# Tracera Remediation: Observability (G-Obs) Additions

> Historical record: the implementation snippets below describe the former
> Python `tracertm` service. Runtime observability is now implemented by the
> Rust `crates/tracera-server` binary. Use [`docs/API_REFERENCE.md`](../API_REFERENCE.md)
> and [`deploy/selfhost/README.md`](../../deploy/selfhost/README.md) for the
> current operational contract.

## Scope

- Add missing standard operational endpoints `/health` and `/ready`.
- Add structured logging with correlation metadata (`request_id`, `correlation_id`).
- Ensure request correlation identifier middleware remains active on all API paths.
- Add a lightweight request access-log path for timing signal (`elapsed_ms`).

## Concrete remediation status

### 1) Endpoints: `/health` and `/ready`

- Added in `src/tracertm/api/main.py`:
  - `GET /health` → `{"status": "ok"}`
  - `GET /ready` → `{"status": "ready", "version": app.version}`
  - Existing `/healthz` and `/readyz` kept as compatibility aliases.
- `create_app()` now exposes both canonical and k8s-compatible probes.

### 2) Structured logging config

- Added `src/tracertm/api/observability.py` with:
  - `configure_api_logging()` (json formatter + request-id injection filter)
  - `CorrelationIdFilter` writing:
    - `correlation_id`
    - `request_id`
  - `log_request_metrics()` helper for access-style timing events.
- `create_app()` now calls `configure_api_logging()` before middleware/route setup.

### 3) Correlation-id middleware hardening

- Updated `src/tracertm/api/middleware/request_id.py`:
  - preserve request ID in ASGI context via `ContextVar` as before
  - expose `get_request_id()` helper
  - write `request.state.request_id`

## Applied diff snapshots (for paste-in review)

### `src/tracertm/api/main.py`

```diff
@@
+configure_api_logging()
+logger = logging.getLogger("tracertm")
@@
+class LoggingMiddleware(BaseHTTPMiddleware):
+    ...
@@
+    app = FastAPI(title="Tracera API", version="0.2.0")
+    app.add_middleware(LoggingMiddleware)
+    app.add_middleware(RequestIdMiddleware)
@@
 @app.get("/healthz", include_in_schema=False)
 async def healthz() -> dict[str, str]:
     return {"status": "ok"}

+@app.get("/health", include_in_schema=True)
+async def health() -> dict[str, str]:
+    return {"status": "ok"}
+
@@
 @app.get("/readyz", include_in_schema=False)
 async def readyz() -> dict[str, str]:
     return {"status": "ready", "version": app.version}
+
+@app.get("/ready", include_in_schema=True)
+async def ready() -> dict[str, str]:
+    return {"status": "ready", "version": app.version}
```

### `src/tracertm/api/observability.py`

```diff
+class CorrelationIdFilter(logging.Filter):
+    ...
+class JSONFormatter(logging.Formatter):
+    ...
```

### `src/tracertm/api/middleware/request_id.py`

```diff
+def get_request_id() -> str:
+    return request_id_var.get("")
```

## Remaining observability follow-up (not yet implemented)

- Export correlation IDs in OpenTelemetry spans (if/when OTel middleware is enabled).
- Add histogram metrics for request latency and error-rate by route and method.
- Emit startup/durable dependency checks in `/ready` after optional graph and storage checks are stabilized.
