# Tracera Architecture

> **Status:** Living document — last updated 2026-06-14.
> **Scope:** This document covers the entire Tracera codebase: Python services (`src/tracertm/`), Rust core (`crates/tracera-core/`), Go backend (`backend/`), frontend (`frontend/`), and test suites (`tests/`).

---

## Table of Contents

1. [Overview](#overview)
2. [Components](#components)
3. [Data Flow](#data-flow)
4. [Key Invariants](#key-invariants)
5. [Cross-Cutting Concerns](#cross-cutting-concerns)
6. [Future Considerations](#future-considerations)

---

## Overview

Tracera is an **agent-native, multi-view requirements traceability and project-management system**. It provides deterministic coverage matrices, impact-analysis graphs, spec-first governance gates, and a content-addressed ML model registry — all exposed through a small, stable REST API surface.

The project is deliberately **polyglot** to match each layer to its best-fit toolchain:

| Layer | Language | Role | Build Tool |
|-------|----------|------|------------|
| **Core entity model & algorithms** | Rust | Canonical types, matrix build, impact scoring, caching | Cargo |
| **Integration & API** | Python | FastAPI endpoints, MLflow-compatible tracking, CLI, governance | Poetry / uv |
| **Services** | Go | Configuration, observability wiring, ML registry port | Go Modules |
| **Frontend** | TypeScript / Bun | TUI, web dashboard, documentation site | pnpm / Bun |
| **Docs** | VitePress | Static documentation site | VitePress |

### Design Philosophy

1. **Deterministic over stochastic** — Coverage classification, impact scoring, and governance gates are rule-based and reproducible. ML models are shadowed and only promoted after measurable offline evaluation.
2. **Spec-first** — Every implementation must trace back to an approved specification item before it can pass governance (`spec_id → implementation → test → evidence`).
3. **Content-addressed** — Model registry artifacts are stored by SHA-256, making builds hermetic and reproducible.
4. **Polyglot parity** — The Rust core (`tracera-core`) maintains 1:1 ports of Python algorithms so future native consumers (e.g., CLI tools, WASM) can reuse the same logic without Python runtime overhead.

---

## Components

### 1. Python API Layer (`src/tracertm/`)

The Python layer is the **primary integration surface** today. It is a standard FastAPI application with a small router surface.

#### 1.1 `api/` — REST API

| File | Responsibility |
|------|----------------|
| `api/main.py` | FastAPI app factory (`create_app`). Wires `RequestIdMiddleware` from `phenotype_request_id` and mounts the traceability router at `/api/v1`. |
| `api/routers/traceability.py` | Coverage matrix, impact analysis, and governance gate endpoints. |
| `api/tests/test_request_id_middleware.py` | Ensures `X-Request-Id` is echoed and propagated. |

**Endpoints:**

- `POST /api/v1/coverage-matrix` — Build a coverage matrix from trace links.
- `POST /api/v1/impact` — Compute blast radius and weighted impact scores from changed artifact IDs.
- `POST /api/v1/governance/spec-check` — Run the spec-first governance gate.

**Pydantic models:** `TraceLinkInput`, `MatrixCellResponse`, `CoverageMatrixRequest`, `CoverageMatrixResponse`, `ImpactRequest`, `ImpactNodeResponse`, `ImpactResponse`, `GovernanceCheckRequest`.

#### 1.2 `governance.py` — Spec-First Governance

Pure, stateless logic. Given a list of `GovernanceSpec` items and `GovernanceTrace` links, produces a `GovernanceReport` with `pass` or `fail` status.

Rules enforced:
- Every spec must be `approved` before execution.
- Every implementation must have a matching spec.
- Orphan traces (no matching spec) are violations.
- Missing test traces for approved specs are violations.

#### 1.3 `performance/matrix.py` — Matrix Construction

Deterministic, side-effect-free builder.

- `build_traceability_matrix(links)` → `TraceabilityMatrix` (sparse, immutable, `frozen` dataclasses).
- Optimized for fast construction: single pass, `O(n)` where `n = link count`.

#### 1.4 `ml/registry.py` — Content-Addressed Model Registry

Disk-backed registry with per-blob SHA-256 content addressing.

- `save(name, version, artifact)` → `ModelEntry`
- `load(name, version=None)` — uses pinned version when `version` is omitted.
- `pin(name, version)` — freeze the default load target.
- Supports `pickle`, `onnx`, `sklearn`, and raw bytes via `ModelAdapter` protocol.

#### 1.5 `mlflow_compat.py` — MLflow-Compatible Tracking

Small, dependency-light client that speaks a subset of the MLflow REST API.

- `Run` class: `log_metric`, `log_param`, `log_artifact`, `set_tag`.
- Backends: `file://` (local JSONL) or `http(s)://` (MLflow server).
- Every emit creates an OpenTelemetry span (`tracertm.bus.emit`).

### 2. Rust Core (`crates/tracera-core/`)

The Rust crate is the **canonical entity model** for the entire system. It is designed to be embedded in other languages (Python via PyO3, Go via cgo, or WASM) in the future.

#### 2.1 Modules

| Module | Phase | Responsibility |
|--------|-------|----------------|
| `lib.rs` | Phase 1 | Core enums (`TraceLinkType`, `ArtifactKind`, `RequirementStatus`), structs (`Artifact`, `Requirement`, `TraceLink`), and error types. |
| `ids.rs` | Phase 1 | Macro-generated typed IDs (`RequirementId`, `NfrId`) with `FR-` / `NFR-` prefixes. |
| `workspace.rs` | Phase 1 | Exposes Cargo metadata (version, MSRV, license) as a stable JSON value. |
| `coverage.rs` | Phase 1 | Coverage-state classification logic (same rules as Python `_classify_coverage`). |
| `impact.rs` | Phase 3 | BFS-based blast radius + weighted impact scoring. Configurable `kind_weights`, `conflict_multiplier`, `max_depth`. |
| `matrix.rs` | Phase 2 | `build_matrix(links) → BuildResult` with provenance (`built_at`, `link_count`, `cell_count`, `stale_links`). |
| `registry.rs` | Phase 4 | Content-addressed model registry (port of `backend/internal/ml/registry.go`). |
| `config.rs` | Phase 5 | Environment-driven configuration loader (`HTTPConfig`, `Neo4jConfig`, `S3Config`, `ObservabilityConfig`, `SentryConfig`, `EmbeddingsConfig`). |
| `cache.rs` | Phase 6 | Thread-safe in-memory TTL cache with LRU/LFU eviction policies and `CacheStats`. |
| `health.rs` | Phase 6 | Kubernetes-style probe registry (`Liveness`, `Readiness`, `Startup`) with async trait-based checks. |
| `notification.rs` | Phase 6 | Multi-channel dispatch (Email, Slack, Webhook, Push) with pluggable sender functions. |
| `pagination.rs` | Phase 6 | Offset, cursor, and keyset pagination primitives (no I/O, pure logic). |
| `rate_limit.rs` | Phase 6 | `TokenBucket`, `SlidingWindow`, `LeakyBucket` — all `Send + Sync`. |
| `observability.rs` | Phase 6 | Tracing initialization, OTLP endpoint resolution, and bus-span creation. |
| `ui_links.rs` | Phase 6 | API navigation payloads for clickable traceability links in UIs. |

#### 2.2 Build & Test

- `cargo test -p tracera-core --lib` — unit tests.
- `cargo clippy --all-targets --all-features -- -D warnings` — linting.
- `cargo deny --locked check` — license and advisory audit.

### 3. Go Backend (`backend/`)

A small, read-only reference layer that ports Python/Rust logic to Go for future microservice extraction.

| File | Responsibility |
|------|----------------|
| `internal/config/config.go` | Environment-driven `Config` struct with typed defaults and `get_required_env` helpers. |
| `internal/config/config_test.go` | Table-driven tests for config parsing. |
| `internal/ml/registry.go` | Go port of the content-addressed model registry (247 LOC). |
| `internal/ml/registry_test.go` | Go tests for registry save/load/list/pin. |
| `internal/observability/otel.go` | OTel collector wiring derived from `Config`. |
| `internal/observability/otel_test.go` | Tests for environment mapping. |

### 4. Frontend (`frontend/`)

> **Note:** The frontend is currently a build-artifact skeleton. The planned architecture is a monorepo with shared packages and two apps:

| Directory | Planned Contents |
|-----------|------------------|
| `packages/types/` | Shared TypeScript types generated from Rust/Pydantic schemas. |
| `packages/api-client/` | Auto-generated HTTP client for the FastAPI surface. |
| `packages/state/` | Global state management (React Context / Zustand). |
| `packages/ui/` | Shared UI component library. |
| `packages/config/` | Shared tooling config (ESLint, Prettier, TS). |
| `packages/env-manager/` | Environment variable validation and injection. |
| `apps/web/` | Next.js dashboard for coverage matrices and impact graphs. |
| `apps/desktop/` | Tauri or Electron desktop app. |
| `apps/docs/` | VitePress documentation site. |

### 5. Test Suites (`tests/`)

| File | Scope |
|------|-------|
| `test_traceability_api.py` | Integration tests for coverage matrix and impact endpoints via `TestClient`. |
| `test_registry.py` | Unit tests for `ModelRegistry` (save, load, list, pin, ONNX adapter). |
| `performance/test_matrix_build_benchmark.py` | Regression benchmark: 10k links must build within 5% of reference time. |
| `performance/test_matrix_export.py` | Export format benchmarks (JSON, CSV, Parquet). |

Inline tests also live next to source files:
- `src/tracertm/test_governance.py`
- `src/tracertm/test_mlflow_compat.py`
- `src/tracertm/ml/test_model_registry.py`
- `src/tracertm/ml/test_inference_models.py`
- `src/tracertm/api/tests/test_request_id_middleware.py`

### 6. Documentation (`docs/`)

| File | Purpose |
|------|---------|
| `SSOT.md` | Source-of-truth index for all docs and specs. |
| `evidence-contract.md` | Canonical schema for requirement coverage status and verification evidence. |
| `ML-OPERATIONS.md` | Runbook for ML-adjacent traceability features (data pipeline, validation, versioning, deployment). |
| `specs/HEALTH-UPGRADE.md` | Draft spec for Kubernetes-style health probes (`/healthz`, `/readyz`). |
| `ARCHITECTURE.md` | (this file) System-level architecture overview. |

---

## Data Flow

### 1. Traceability Matrix Pipeline

```
Trace links (source, target, relationship, confidence, updated_at)
    │
    ▼
POST /api/v1/coverage-matrix
    │
    ├──► Group by (source_id, target_id)
    │
    ├──► Classify each cell:
    │       conflict     → any "conflicts_with"
    │       covered      → "verifies"/"satisfies" with confidence ≥ 0.9
    │       partial      → "verifies"/"satisfies" with confidence < 0.9
    │       stale        → updated_at > stale_after_days
    │       missing      → everything else
    │
    ├──► Count stale links
    │
    └──► CoverageMatrixResponse (generated_at, link_count, cell_count, stale_links, cells)
```

**Classification is deterministic and ordered:** `conflict > covered > partial > stale > missing`. The first match wins.

### 2. Impact Analysis Pipeline

```
CoverageMatrixRequest + changed_artifact_ids
    │
    ▼
POST /api/v1/impact
    │
    ├──► Build adjacency graph (bidirectional from grouped links)
    │
    ├──► BFS from seed artifacts:
    │       depth 0 → score = 1.0
    │       depth N → score = decay^N × confidence × relationship_multiplier
    │
    ├──► Track conflicts (negative-multiplier edges)
    │
    └──► ImpactResponse (seeds, affected[], total_score, truncated, max_depth_seen, conflicts)
```

**Relationship multipliers:**

| Relationship | Multiplier |
|--------------|------------|
| `conflicts_with` | -1.5 |
| `satisfies`, `implements`, `refines` | 1.0 |
| `verifies` | 0.75 |
| `derives_from`, `duplicates` | 0.25 |

**Decay factor:** 0.85 per depth level.

### 3. Governance Gate Pipeline

```
GovernanceSpec[] + GovernanceTrace[]
    │
    ▼
POST /api/v1/governance/spec-check
    │
    ├──► Validate every spec is approved
    │
    ├──► Validate every trace has a matching spec
    │
    ├──► Validate every approved spec has ≥ 1 test trace
    │
    └──► GovernanceReport (status: pass | fail, spec_count, trace_count, violations[])
```

### 4. ML Tracking Event Flow

```
Client code (training or scoring)
    │
    ▼
Run.log_metric / log_param / log_artifact
    │
    ├──► OpenTelemetry span: tracertm.bus.emit
    │       attributes: event.id, event.type, source, correlation_id
    │
    └──► Route by tracking URI scheme:
            file://  →  .tracertm/mlflow-runs/<run_id>/events.jsonl + artifacts/
            http(s):// → POST /api/2.0/mlflow/*
```

### 5. Model Registry Flow

```
Model artifact (pickle, onnx, sklearn)
    │
    ▼
ModelRegistry.save(name, version, artifact)
    │
    ├──► Compute SHA-256
    │
    ├──► Store blob: models/<name>/<version>/blobs/<sha256>.<ext>
    │
    ├──► Update index: registry.json (models + pins)
    │
    └──► Return ModelEntry (name, version, sha256, format, path, metadata, created_at)
```

Load path:
```
ModelRegistry.load(name, version=None)
    │
    ├──► If version is None → lookup pinned version
    │
    ├──► Validate SHA-256 against stored blob
    │
    └──► Deserialize via ModelAdapter and return
```

---

## Key Invariants

### 1. Coverage Classification Order

The classification logic in `traceability.py:_classify_coverage` and `coverage.rs` must **always** evaluate in this order:

1. `conflict` — if any link is `conflicts_with`.
2. `covered` — if any `verifies` or `satisfies` link has `confidence >= 0.9`.
3. `partial` — if any `verifies` or `satisfies` link exists (regardless of confidence).
4. `stale` — if any link has `updated_at` older than `stale_after_days`.
5. `missing` — default.

Changing this order changes the semantics of every matrix cell. Add a regression test before any modification.

### 2. Content-Addressed Registry Integrity

- A model blob is **never** overwritten. `save()` with an existing `(name, version)` raises `ModelRegistryError`.
- The SHA-256 in the index must match the blob on disk at all times. `load()` validates this.
- Pins are immutable: `pin(name, version)` records the version and SHA at call time. Subsequent `save()` with a different SHA does not affect the pin.

### 3. Spec-First Governance

- `evaluate_spec_first_governance` is a **pure function**. It must not read from the database or filesystem.
- The only inputs are the `specs` and `traces` lists passed by the caller.
- A `fail` status is always accompanied by at least one `GovernanceViolation` with a human-readable `message` and stable `code`.

### 4. Request ID Propagation

- Every inbound HTTP request must carry a `X-Request-Id` header (or have one generated).
- The same value must be echoed on the response and stored in a `ContextVar` for the duration of the request.
- This is enforced by `phenotype_request_id.fastapi.RequestIdMiddleware`.

### 5. Rust/Python Algorithm Parity

- Any algorithm change in `src/tracertm/` must be mirrored in `crates/tracera-core/` (or vice versa) until the decouple plan is complete.
- The decouple plan is tracked in `crates/tracera-core/README.md` and `src/lib.rs` comments.

### 6. Health Probe Semantics

- `/healthz` (liveness) — cheap, never fails on dependencies. Returns `{"status": "alive"}`.
- `/readyz` (readiness) — may depend on caches, DB pools, etc. Returns the `HealthStatus` of all registered probes.
- `/startupz` — one-shot readiness used at boot. Returns `Healthy` after first-time initialization completes.

### 7. Test Isolation

- `test_traceability_api.py` uses `TestClient` against an ephemeral `create_app()` instance. No database required.
- `test_registry.py` uses `tmp_path` for each test. No shared state.
- `test_governance.py` is a pure function test suite. No I/O at all.

---

## Cross-Cutting Concerns

### 1. Observability

- **OpenTelemetry** spans are emitted on every ML tracking event (`tracertm.bus.emit`) and every HTTP request (`phenotype_request_id`).
- **Tracing** in Rust is initialized via `tracing_subscriber` with `RUST_LOG` filter.
- **Metrics** are not yet implemented but planned (Phase 6 of decouple plan).
- **Health probes** are registered in the `HealthRegistry` and polled by Kubernetes-style HTTP endpoints.

### 2. Configuration

- **Python** uses `pydantic-settings` with `.env` file support.
- **Rust** uses `std::env` with typed helpers (`get_env_int`, `get_env_bool`, `get_required_env`).
- **Go** uses `os.Getenv` with defaults in `internal/config/config.go`.
- **No secrets** are hard-coded. All secrets are injected via environment variables.

### 3. Error Handling

- **Python** uses custom exception types (`ModelRegistryError`, `ValueError` subclasses) and Pydantic validation.
- **Rust** uses `thiserror` enums (`TraceLinkError`, `RegistryError`, `ConfigError`).
- **Go** uses standard `error` wrapping with `fmt.Errorf`.

### 4. Rate Limiting

The Rust crate provides `TokenBucket`, `SlidingWindow`, and `LeakyBucket` rate limiters. They are `Send + Sync` and use no background threads (lazy refill on `try_acquire`).

### 5. Caching

The Rust `Cache<K, V>` is an in-memory TTL cache with LRU or LFU eviction. It is `Send + Sync` and exposes `CacheStats` for observability. Used for hot-path coverage and impact computations.

### 6. Pagination

Three strategies are provided in Rust, all pure logic (no I/O):

- `OffsetRequest` — simple `?page=N&size=M`.
- `Cursor` — opaque base64url-encoded cursor, stable across inserts.
- `KeysetRequest` — explicit `(last_id, last_sort_key)` tuple, most efficient with covering indexes.

### 7. Notifications

The Rust `Dispatcher` routes `Notification` structs to `Email`, `Slack`, `Webhook`, or `Push` channels. It is deliberately I/O-free; callers inject sender closures. This makes the core dependency-free and trivial to unit-test.

### 8. Type Safety & ID Generation

- Rust uses macro-generated typed IDs (`RequirementId`, `NfrId`) with prefixes to prevent mixing up identifiers.
- Python uses Pydantic `Field(..., min_length=1)` to reject empty strings.
- Go uses `safePartPattern` and `semverPattern` regexes to validate names and versions.

### 9. CI/CD & Task Runners

- **Rust:** `cargo fmt`, `cargo clippy`, `cargo test`, `cargo deny` (see `Taskfile.yml`).
- **Python:** `ruff` (lint + format), `mypy` (type check), `pytest` (see `pyproject.toml`).
- **Go:** `go fmt`, `go vet`, `golangci-lint`.
- **Frontend:** `eslint`, `prettier`, `tsc --noEmit`.
- **Justfile:** Polyglot convenience layer (`just dev`, `just build`, `just test`).

---

## Future Considerations

### 1. Decouple Plan (Rust Core Migration)

The `tracera-core` crate is being built in phases to replace the Python backend as the canonical source of truth:

| Phase | Status | Deliverable |
|-------|--------|-------------|
| Phase 1 | ✅ Complete | Core entity model (`lib.rs`, `ids.rs`, `workspace.rs`, `coverage.rs`). |
| Phase 2 | 🔄 In Progress | Matrix operations (`matrix.rs`). |
| Phase 3 | 🔄 In Progress | Impact scoring (`impact.rs`). |
| Phase 4 | ✅ Complete | Model registry (`registry.rs`). |
| Phase 5 | ✅ Complete | Configuration loader (`config.rs`). |
| Phase 6 | 🔄 Planned | Cache, health, notifications, pagination, rate limit, observability, UI links. |

Once Phase 6 is complete, the Python layer will become a thin binding around the Rust core, and the Go backend will be deprecated in favor of a Rust-native service.

### 2. Frontend Realization

The frontend is currently a skeleton. Next steps:

- Generate TypeScript types from Rust/Pydantic schemas (OpenAPI or custom codegen).
- Implement the web dashboard (`apps/web`) for coverage matrix visualization and impact graph navigation.
- Implement the TUI (`apps/desktop`) for CLI-first users.

### 3. Database & Persistence

Today the system is stateless in the API layer (all data is passed in the request body). Future plans:

- **Neo4j** for graph persistence of trace links (schema already defined in `ArtifactKind::neo4j_label`).
- **PostgreSQL** for structured data (requirements, evidence contracts, governance reports).
- **S3** for model registry blob storage (config already present in `S3Config`).
- **Redis / Upstash** for distributed caching and rate limiting.

### 4. ML Model Promotion

The ML-operations runbook (`docs/ML-OPERATIONS.md`) defines a strict promotion pipeline:

1. **Snapshot** dataset before any scorer change.
2. **Offline evaluation** on immutable evaluation inputs.
3. **Registry candidate** with measured lift.
4. **Shadow / canary** deployment before production.
5. **Production scoring** only after proven value.

Learned models must never replace deterministic heuristics without measurable evidence.

### 5. Health Probe Expansion

The draft spec (`docs/specs/HEALTH-UPGRADE.md`) proposes:

- `/healthz` → alias for liveness.
- `/readyz` → alias for readiness.
- `/live` → alias for liveness.
- `/ready` → alias for readiness.
- Kubernetes probe integration.

### 6. Multi-Workspace Support

The `WorkspaceMetadata` struct and `project_id` fields on all entities suggest a future multi-tenant or multi-workspace model. The `project_id` boundary is already enforced in validation rules (no cross-project joins).

### 7. WASM / WebAssembly

The Rust core is designed to be `no_std`-friendly where possible. Future plans include compiling `tracera-core` to WASM for browser-side matrix computation and visualization.

### 8. Evidence Contract Enforcement

The `evidence-contract.md` specifies a canonical schema for requirement coverage. Future work includes:

- A database migration to create the `requirement_evidence_contract` table.
- An `evidence_contract_writer` service that is the sole authority for writes.
- Policy enforcement: direct DB writes outside the service are forbidden.

---

## Appendix: File References

### Core API
- `src/tracertm/api/main.py:11-22` — FastAPI app factory.
- `src/tracertm/api/routers/traceability.py:103-225` — Coverage, impact, and governance endpoints.
- `src/tracertm/governance.py:49-116` — Spec-first governance logic.
- `src/tracertm/performance/matrix.py:30-47` — Matrix construction.
- `src/tracertm/ml/registry.py:26-279` — Model registry.
- `src/tracertm/mlflow_compat.py:29-219` — MLflow tracking client.

### Rust Core
- `crates/tracera-core/src/lib.rs:1-490` — Entity model and core types.
- `crates/tracera-core/src/matrix.rs:27-50` — Matrix build.
- `crates/tracera-core/src/impact.rs:17-50` — Impact scoring config.
- `crates/tracera-core/src/registry.rs:44-50` — Model entry.
- `crates/tracera-core/src/config.rs:19-50` — Configuration structs.
- `crates/tracera-core/src/cache.rs:48-50` — Cache interface.
- `crates/tracera-core/src/health.rs:19-50` — Health probe types.
- `crates/tracera-core/src/notification.rs:35-50` — Notification struct.

### Go Backend
- `backend/internal/config/config.go:22-50` — Config struct.
- `backend/internal/ml/registry.go:31-48` — Registry types.
- `backend/internal/observability/otel.go:11-50` — OTel wiring.

### Tests
- `tests/test_traceability_api.py:13-83` — API integration tests.
- `tests/test_registry.py:12-48` — Registry unit tests.
- `tests/performance/test_matrix_build_benchmark.py:38-46` — Performance regression gate.

---

*This document is a living artifact. When adding new components, update the relevant section and add file references in the appendix.*
