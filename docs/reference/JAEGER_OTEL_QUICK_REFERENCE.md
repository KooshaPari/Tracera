> Historical note: this document preserves the pre-Phenotype observability stack. The active org path is the shared collector, Grafana Alloy, and Grafana Tempo. Treat Jaeger and Promtail references below as legacy context only.

# Legacy Jaeger Compatibility Quick Reference

**Last Updated:** 2026-02-05

This file exists for compatibility with older Tracera-recovered references only.
The current tracing path is documented in `TRACING_QUICK_REFERENCE.md` and uses the
shared Phenotype collector, Grafana Alloy, and Grafana Tempo.

---

## 1. Go Backend (OTEL SDK + HTTP instrumentation)

- **SDK:** `go.opentelemetry.io/otel` + `otel/sdk` + `otel/exporters/otlp/otlptrace/otlptracegrpc`
- **HTTP instrumentation:** Echo middleware via `go.opentelemetry.io/contrib/instrumentation/github.com/labstack/echo/otelecho`
- **Export:** OTLP gRPC to `PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT` (default `127.0.0.1:4317`)
- **Config:** `TRACING_ENABLED`, `PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT`, `TRACING_ENVIRONMENT`
- **Code:** `backend/internal/tracing/` (tracer.go, middleware.go), `backend/internal/infrastructure/infrastructure.go` (initTracing)

---

## 2. Python Backend (OTEL SDK + FastAPI instrumentation)

- **SDK:** `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-exporter-otlp-proto-grpc`
- **FastAPI instrumentation:** `opentelemetry-instrumentation-fastapi` (FastAPIInstrumentor)
- **Export:** OTLP gRPC to `PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT` (default `127.0.0.1:4317`)
- **Config:** `TRACING_ENABLED`, `PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT`, `TRACING_ENVIRONMENT`
- **Code:** `src/tracertm/observability/tracing.py`, `instrumentation.py`; `src/tracertm/api/main.py` (init on startup)
- **Propagation:** W3C Trace Context for cross-service traces (aligned with Go).

---

## 3. Historical Notes

The remaining Jaeger-specific material below is retained only as historical context.
The current tracing path is the shared collector, Grafana Alloy, and Grafana Tempo.

---

## 4. Verify: Traces visible in Grafana

1. **Start stack (including shared collector):**
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

3. **Open Grafana UI:** http://localhost:3000

4. **Search:**
   - **Service:** `tracertm-backend` (Go) or `tracertm-python-backend` (Python)
   - Use Grafana's trace view to inspect spans for `/health` and `/api/v1/health`.

5. **Optional:** Trigger a request that crosses backends (e.g. Go calling Python) to see a single trace with spans from both services (W3C propagation).
