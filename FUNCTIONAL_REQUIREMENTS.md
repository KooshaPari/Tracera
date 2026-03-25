# TracerTM: Functional Requirements

## FR-TRACE: Traceability Core

| ID | Requirement | Traces To |
|----|------------|-----------|
| FR-TRACE-001 | System SHALL maintain bidirectional links between requirements, code, tests, and deployments | E1.2 |
| FR-TRACE-002 | System SHALL support 5 architectural lenses: code, API, database, deployment, documentation | E1.1 |
| FR-TRACE-003 | System SHALL compute impact analysis showing all downstream artifacts affected by a change | E1.3 |
| FR-TRACE-004 | System SHALL report coverage percentage of requirements with linked artifacts | E1.4 |

## FR-GRAPH: Graph Visualization

| ID | Requirement | Traces To |
|----|------------|-----------|
| FR-GRAPH-001 | System SHALL render interactive dependency graphs from Neo4j data | E2.1 |
| FR-GRAPH-002 | System SHALL highlight impact propagation subgraph on node selection | E2.2 |
| FR-GRAPH-003 | System SHALL support filtering graph nodes by type, status, and text search | E2.3 |

## FR-RT: Real-Time Collaboration

| ID | Requirement | Traces To |
|----|------------|-----------|
| FR-RT-001 | System SHALL propagate mutations to all connected WebSocket clients within 1 second | E3.1 |
| FR-RT-002 | System SHALL show presence indicators for concurrent users | E3.2 |
| FR-RT-003 | System SHALL log every mutation with actor, timestamp, and diff in an audit trail | E3.3 |

## FR-AGENT: Agent Integration

| ID | Requirement | Traces To |
|----|------------|-----------|
| FR-AGENT-001 | System SHALL suggest traceability links using AI analysis of code and requirements | E4.1 |
| FR-AGENT-002 | System SHALL re-index requirement links on new commits | E4.2 |
| FR-AGENT-003 | System SHALL support semantic similarity search via embeddings | E4.3 |

## FR-OBS: Observability

| ID | Requirement | Traces To |
|----|------------|-----------|
| FR-OBS-001 | System SHALL export Prometheus metrics for latency, throughput, and error rates | E5.1 |
| FR-OBS-002 | All services SHALL emit structured JSON logs compatible with Loki | E5.2 |
| FR-OBS-003 | System SHALL support distributed tracing via OpenTelemetry/Jaeger | E5.3 |

## FR-ITEM: Item Management

| ID | Requirement | Traces To |
|----|------------|-----------|
| FR-ITEM-001 | System SHALL provide CRUD operations for requirements, features, and tasks | E6.1 |
| FR-ITEM-002 | System SHALL support Figma design artifact linking | E6.2 |
| FR-ITEM-003 | System SHALL provide full-text search across all indexed documents | E6.3 |

## FR-AUTH: Authentication and Authorization

| ID | Requirement | Traces To |
|----|------------|-----------|
| FR-AUTH-001 | System SHALL authenticate users via session-based auth with CSRF protection | E1.1 |
| FR-AUTH-002 | System SHALL enforce role-based access control on all API endpoints | E1.1 |
