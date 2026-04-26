# Observably

**Unified Observability Dashboard & Metrics Aggregation Framework**

## Overview

Observably is a comprehensive observability stack builder and metrics aggregation platform for distributed systems. It provides a centralized dashboard for metrics, traces, logs, and alerts across the entire Phenotype infrastructure, integrating with industry-standard observability backends (Prometheus, Grafana, Tempo, Loki).

**Core Mission**: Aggregate observability signals from all Phenotype services into one actionable dashboard; enable real-time incident detection, health monitoring, and SLO tracking.

## Technology Stack

- **Backend**: Rust, Tokio async runtime
- **Metrics Collection**: Prometheus client SDK, OpenTelemetry SDKs (Go, Python, JavaScript)
- **Storage**: Prometheus (time-series), Tempo (traces), Loki (logs), S3/ObjectStorage backend
- **Dashboard**: Grafana integration with custom panels and dashboards
- **Alerting**: Prometheus AlertManager with webhook integration
- **API**: GraphQL + REST for metric queries, trace retrieval, and dashboard management
- **Deployment**: Kubernetes (Helm charts), Docker Compose, standalone binary

## Key Features

- **Multi-Backend Aggregation** — Unified API abstracting Prometheus, InfluxDB, TimescaleDB, CloudWatch
- **Real-Time Dashboards** — Grafana-powered visualizations with dynamic thresholds and custom metrics
- **Distributed Tracing** — Tempo integration for end-to-end request tracing and latency analysis
- **Log Aggregation** — Loki-backed centralized logging with label-based filtering and querying
- **SLO Management** — Define, track, and alert on Service Level Objectives with automated compliance reporting
- **Custom Metrics** — Push/pull metrics from any service via Prometheus remote write API
- **Incident Correlation** — Link metrics, traces, and logs to correlate root causes during incidents
- **Multi-Tenant Support** — Segregate metrics and dashboards by environment, team, or workload

## Quick Start

```bash
# Clone the repository
git clone https://github.com/KooshaPari/Observably
cd Observably

# Review project configuration
cat CLAUDE.md

# Build the observability aggregator
cargo build --release

# Start local dev stack (Prometheus + Grafana + Tempo + Loki)
docker-compose -f docker-compose.dev.yml up

# Initialize database and dashboards
cargo run --bin observably-setup -- --init

# Run tests with coverage
cargo test --workspace -- --test-threads=1

# Format and lint
cargo fmt
cargo clippy --workspace -- -D warnings
```

## Project Structure

```
src/
  ├─ aggregator/      # Metrics aggregation engine (Prometheus, InfluxDB, CloudWatch adapters)
  ├─ dashboard/       # Dashboard builder and Grafana API client
  ├─ tracing/         # Tempo trace integration and distributed tracing pipeline
  ├─ logging/         # Loki log aggregation with label extraction
  ├─ alerting/        # AlertManager integration and alert routing
  ├─ slo/             # SLO definition, tracking, and compliance evaluation
  ├─ api/             # GraphQL + REST API (queries, mutations, subscriptions)
  ├─ storage/         # Time-series storage abstraction and retention policies
  └─ config/          # Configuration management (YAML, environment overrides)
tests/
  ├─ integration/     # End-to-end dashboard, metric, and trace aggregation tests
  └─ unit/            # Aggregator, SLO, and alerting logic tests
```

## Status

**Active Development** — Core aggregation engine complete; Grafana integration in progress.

- ✓ Prometheus metrics collection
- ✓ Tempo trace integration
- ✓ Loki log aggregation
- ✓ AlertManager webhook routing
- WIP: Multi-backend query federation
- WIP: Advanced SLO visualization

## Related Phenotype Projects

- **Tracera** — Distributed tracing platform (upstream source for traces)
- **ObservabilityKit** — Multi-language OTEL SDKs for metrics and tracing instrumentation
- **vibeproxy-monitoring-unified** — Health checks and unified monitoring interface

## Governance & Architecture

- **Documentation**: See `CLAUDE.md` for local development setup
- **Specification**: `docs/spec/observably-observability-stack.md` — Architecture and data flow
- **Integration**: Cross-project observability architecture in `phenotype-infrakit`
- **License**: MIT + Proprietary (Phenotype ecosystem use only)

---

**Maintained by**: Phenotype Infrastructure Team  
**Last Updated**: 2026-04-25
