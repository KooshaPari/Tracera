---
audience: [developers, agents, pms]
status: active
---

# Specifications

## Functional Requirements

### FR-REC-001: Recovered Working Tree

The repo must have a usable recovered checkout that contains live backend, Python service,
frontend, infrastructure, and documentation paths without relying on the tainted local `Tracera/`
snapshot.

Acceptance criteria:

- `Tracera-recovered/` exists and points at `KooshaPari/Tracera`.
- `backend/`, `src/tracertm/`, `frontend/`, and `config/` are present.
- Root governance files do not remain dirty because of macOS case collisions.

### FR-INFRA-001: Modern Observability Collector

Promtail must be removed from the active local stack and replaced with Grafana Alloy.

Acceptance criteria:

- No active process-compose service named `promtail`.
- Alloy has a local process entry and health/readiness behavior.
- Logs still reach Loki.
- Traces are accepted via OTLP and remain viewable through the chosen local trace backend.

### FR-INFRA-002: Redis Responsibility Split

Redis must no longer be treated as the default place for every fast state problem.

Acceptance criteria:

- Redis usage is classified by responsibility: cache, rate limit, session, lock, pub/sub, queue.
- NATS JetStream handles event/watch/history workloads where appropriate.
- PostgreSQL handles durable transactional coordination and locks where appropriate.
- Dragonfly is the default Redis-compatible runtime for remaining cache-shaped workloads.
- Notification pub/sub is not backed by Redis.
- Feature flags and operational config are backed by PostgreSQL.

### FR-PROD-001: Traceability Core Consolidation

Traceability, history, event sourcing, graph snapshots, and temporal workflows must have clear
bounded domains.

Acceptance criteria:

- One canonical traceability application service entrypoint.
- One canonical graph snapshot/history path.
- Advanced or experimental services are either integrated, archived, or deleted.
- API, MCP, and frontend callers route through the canonical boundaries.

### FR-DEMO-001: Reader-Friendly Demo Journeys

Tracera must include runnable demo journeys that prove the product works end to end.

Acceptance criteria:

- A seeded demo project exercises requirements, code links, tests, graph rendering, and versions.
- Guides include expected outputs and screenshots or recordings where practical.
- Demo validation can be run by agents without requiring user handoff.

## ARUs

| ID | Type | Statement | Mitigation |
| --- | --- | --- | --- |
| ARU-001 | Risk | Full checkout may keep colliding on macOS until lowercase root docs are removed. | Stage forward deletion of lowercase duplicates. |
| ARU-002 | Risk | Redis may have hidden coupling in Go/Python tests. | Classify before replacing; use compatibility profile during migration. |
| ARU-003 | Risk | Alloy migration can change metrics/log labels. | Preserve dashboards by documenting label mapping and running local smoke checks. |
| ARU-004 | Uncertainty | Rust may exist on older refs or unrecovered branches. | Search historical refs after current recovery is stable. |
| ARU-005 | Risk | Graph renderer is powerful but may not be wired to product data. | Build demo seed data and run graph performance smoke tests. |
