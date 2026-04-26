# Changelog

All notable changes to Tracera are documented in this file.

## [0.1.1] — 2026-04-25

### Added
- FUNCTIONAL_REQUIREMENTS.md scaffolded with 12 core FRs (FR-TRACERA-{001..012})
- env_test.go: 29 environment integration tests annotated with FR-TRACERA-001 trace markers
- 5 handler test files scaffolded for GRPC/HTTP/streaming/error/async patterns (FR-TRACERA-{002..006})
- 10 smoke test cases across handler suite

### Changed
- Test infrastructure reorganized for FR traceability

## [0.1.0] — 2026-04-25

**Distributed Tracing & Observability Platform GA Release**

### Added

**Backend (Go)**
- 266 comprehensive test cases across 66 packages
- W-30 audit correction: validated test coverage and traceability matrix
- Distributed tracing pipeline with OpenTelemetry integration
- Multi-backend support (Tempo, Prometheus, Loki, Grafana)
- gRPC service definitions and handlers
- Repository layer with caching and transaction management
- Configuration management (file-based, environment variable overrides)

**CLI & Instrumentation**
- tracertm.cli (21/21 unit tests, 100% pytest collection)
- W-23 commit 8873600b: CLI stub unblocks 30% of pytest collection
- Python HTTP client middleware with automatic tracing
- Process-compose configuration (18-service orchestrated stack)
- Alembic database migrations (68 schema versions)
- Health checks and liveness probes

**Observability Stack**
- Tempo distributed trace backend with WAL-based retention
- Prometheus metrics scraping and time-series aggregation
- Loki log aggregation with full-text search
- Grafana unified dashboards and alerting rules
- Alloy observability pipeline (collection, transformation, export)
- Vault secret management and credential rotation

**Testing & Quality**
- 90% test coverage target achieved
- Property-based testing (Hypothesis framework)
- Performance benchmarking suite
- Chaos engineering test scenarios
- Integration & E2E workflow validation
- Load testing and stress benchmarks

**Recovery & Resilience**
- R1-R10 recovery progression patterns implemented
- Failover and graceful degradation modes
- Data consistency checks and repair utilities
- Health monitoring and automatic restarts

### Technical Highlights

- **Languages**: Python (Jupyter, Hypothesis), Go (backend), Rust (SDKs)
- **Architecture**: Microservices with distributed tracing, event sourcing
- **Storage**: PostgreSQL + TimescaleDB, S3/MinIO object store
- **Transport**: gRPC + HTTP/2, OpenTelemetry Protocol (OTLP)
- **Deployment**: process-compose for local dev, Kubernetes-ready manifests

### Known Limitations

- Recovery patterns R11-R15 deferred to v0.2.0
- Kubernetes operator scheduled for v0.2.0
- Advanced query DSL (TraceQL v2) scheduled for v0.3.0

---

**Deployment & Upgrade Notes**

- Minimum: Go 1.23+, Python 3.11+
- Database: PostgreSQL 15+ with TimescaleDB extension
- Infrastructure: 4GB RAM, 20GB storage (single-node), Docker/K8s support
- Backward compatibility: Schema migrations auto-applied on startup

See `docs/release-notes/v0.1.0.md` for detailed feature matrix and migration guide.
