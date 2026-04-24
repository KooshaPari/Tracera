# Research Notes

## Source comparison

- `Tracera` started as a governance-heavy shell with docs, specs, and traceability files
  but no recovered runtime tree.
- `Tracera-recovered` contains the runnable implementation surface:
  - `backend/` Go API and test suites
  - `src/tracertm/` Python services and observability helpers
  - `frontend/` React/TypeScript apps and packages
  - `config/process-compose*.yaml` for native orchestration
  - `deploy/` k8s manifests and observability config

## Stack findings

- No Rust source files or `Cargo.toml` were present in the recovered implementation
  outside the Python virtualenv dependency cache.
- The recovered implementation is Go + Python + React, with Temporal, NATS, Redis-compatible
  cache, PostgreSQL, and Grafana Alloy/Tempo for observability.

## Validation findings

- `python3 Tracera/validate_governance.py` passes after restoring FR specs 4-6.
- `deploy/k8s/base/deployment-go-backend.yaml` was still pointing at the legacy tracing env var
  and was updated to `PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT=tracera-collector:4317`.
