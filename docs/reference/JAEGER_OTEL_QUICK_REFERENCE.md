# Jaeger & OpenTelemetry Quick Reference

**Last Updated:** 2026-02-05

Distributed tracing is implemented with OpenTelemetry (OTEL) and exported to Jaeger. Both backends send traces over OTLP gRPC.

---

## 1. Go Backend (OTEL SDK + HTTP instrumentation)

- **SDK:** `go.opentelemetry.io/otel` + `otel/sdk` + `otel/exporters/otlp/otlptrace/otlptracegrpc`
- **HTTP instrumentation:** Echo middleware via `go.opentelemetry.io/contrib/instrumentation/github.com/labstack/echo/otelecho`
- **Export:** OTLP gRPC to Jaeger (default `127.0.0.1:4317`)
- **Config:** `TRACING_ENABLED`, `JAEGER_ENDPOINT`, `TRACING_ENVIRONMENT`
- **Code:** `backend/internal/tracing/` (tracer.go, middleware.go), `backend/internal/infrastructure/infrastructure.go` (initTracing)

---

## 2. Python Backend (OTEL SDK + FastAPI instrumentation)

- **SDK:** `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-exporter-otlp-proto-grpc`
- **FastAPI instrumentation:** `opentelemetry-instrumentation-fastapi` (FastAPIInstrumentor)
- **Export:** OTLP gRPC to Jaeger (default `127.0.0.1:4317`)
- **Config:** `TRACING_ENABLED`, `OTLP_ENDPOINT` (or `JAEGER_ENDPOINT`), `TRACING_ENVIRONMENT`
- **Code:** `src/tracertm/observability/tracing.py`, `instrumentation.py`; `src/tracertm/api/main.py` (init on startup)
- **Propagation:** W3C Trace Context for cross-service traces (aligned with Go).

---

## 3. Jaeger Export Config

| Item        | Value |
|------------|--------|
| **UI**     | http://localhost:16686 |
| **OTLP gRPC** | `127.0.0.1:4317` (used by both backends) |
| **OTLP HTTP**  | `127.0.0.1:4318` (optional) |
| **Start**  | `make dev` / process-compose runs `jaeger-if-not-running.sh` |
| **Install** | `brew install jaegertracing/jaeger/jaeger` (or `jaeger-all-in-one`) |

Backends depend on Jaeger being healthy before start (`depends_on: jaeger: process_healthy` in `config/process-compose.yaml`).

---

## 4. Verify: Traces visible in Jaeger

1. **Start stack (including Jaeger):**
   ```bash
   make dev
   ```
   Wait until go-backend and python-backend are healthy.

2. **Generate traces:**
   ```bash
   # Go backend
   curl -s http://localhost:8080/health
   curl -s http://localhost:8080/api/v1/health

   # Python backend
   curl -s http://localhost:8000/health
   curl -s http://localhost:8000/api/v1/health
   ```

3. **Open Jaeger UI:** http://localhost:16686

4. **Search:**
   - **Service:** `tracertm-backend` (Go) or `tracertm-python-backend` (Python)
   - Click **Find Traces**. You should see spans for `/health` and `/api/v1/health`.

5. **Optional:** Trigger a request that crosses backends (e.g. Go calling Python) to see a single trace with spans from both services (W3C propagation).
