# ADR Index

## ADR Catalog

### Accepted

- [`ADR-SERVER-001-endpoint-regression-audit.md`](ADR-SERVER-001-endpoint-regression-audit.md) — Tiered inventory of endpoints deleted during the Python→Rust migration
- [`ADR-GOV-001-agileplus-governance-source.md`](../ADR-GOV-001-agileplus-governance-source.md) — AgilePlus as single authoritative governance source for all projects
- [`ADR-GOV-002-graph-ingestion-architecture.md`](../ADR-GOV-002-graph-ingestion-architecture.md) — Three-phase ingestion (polling→webhooks→event bus) for AgilePlus→Tracera
- [`ADR-GOV-003-signed-commits-branch-protection.md`](../ADR-GOV-003-signed-commits-branch-protection.md) — Signed commits and branch protection policy for main
- [`ADR-TEST-001-test-coverage-policy.md`](../ADR-TEST-001-test-coverage-policy.md) — 100% public function coverage threshold, CI enforcement
- [`ADR-TEST-002-mutation-testing.md`](../ADR-TEST-002-mutation-testing.md) — cargo-mutants adoption with 80% kill rate target
- [`ADR-SWEE-001-graph-schema-design.md`](../ADR-SWEE-001-graph-schema-design.md) — Typed graph schema (30 node types, 35 edge types) for SWE-E evidence model
- [`ADR-ARCH-001-hexagonal-architecture.md`](../ADR-ARCH-001-hexagonal-architecture.md) — Hexagonal (ports & adapters) architecture for tracera-server
- [`ADR-DATA-001-dual-store-strategy.md`](../ADR-DATA-001-dual-store-strategy.md) — PostgreSQL prod / SQLite dev dual-store strategy
- [`ADR-DEP-001-phenodag-absorption.md`](../ADR-DEP-001-phenodag-absorption.md) — Phenodag queue absorption decision
- [`ADR-OBS-001-opentelemetry-adoption.md`](../ADR-OBS-001-opentelemetry-adoption.md) — OpenTelemetry for distributed tracing and metrics

### Referenced (not yet created as standalone ADRs)

- [`ADR_MODEL_DECOUPLE_STRATEGY.md`](../ADR_MODEL_DECOUPLE_STRATEGY.md)
- [`docs/reports/SECURITY_AUDIT_DAG.md`](../reports/SECURITY_AUDIT_DAG.md)

## Current Governance Evidence

- Endpoint traceability map: [`endpoint_traceability_map.md`](endpoint_traceability_map.md)
- Self-application matrix: [`coverage_matrix_self_application.md`](coverage_matrix_self_application.md)

## Planned (Not Yet Accepted)

- `ADR-SEC-001`: API input-validation hardening and request-shape controls (planned)
- `ADR-SEC-002`: Secret transport hardening and environment-only credentials (planned)
