---
audience: [developers, agents, pms]
status: active
---

# DAG WBS

| Phase | Task ID | Description | Depends On |
| --- | --- | --- | --- |
| 1 | TREC-001 | Preserve tainted local `Tracera/` and work from `Tracera-recovered/` | none |
| 1 | TREC-002 | Resolve case-collision governance files on macOS | TREC-001 |
| 1 | TREC-003 | Inventory root docs/status artifacts and route them into session/docs surfaces | TREC-001 |
| 1 | TREC-004 | Validate sparse checkout paths and recover any missing live source directories | TREC-001 |
| 2 | TREC-010 | Replace Promtail process/config with Grafana Alloy | TREC-004 |
| 2 | TREC-011 | Route OTLP telemetry through Alloy while preserving local Jaeger compatibility | TREC-010 |
| 2 | TREC-012 | Decide Loki versus Tempo/Grafana stack shape for local dev and org standard | TREC-011 |
| 2 | TREC-013 | Split Redis responsibilities into rate-limit/cache/session/lock/pubsub buckets | TREC-004 |
| 2 | TREC-014 | Move event/pubsub/watch/history duties to NATS JetStream where already natural | TREC-013 |
| 2 | TREC-015 | Move durable coordination and locks to PostgreSQL where transactional guarantees matter | TREC-013 |
| 2 | TREC-016 | Make Dragonfly the default Redis-compatible cache/rate-limit/session runtime | TREC-013 |
| 2 | TREC-017 | Move notification pub/sub off Redis and onto NATS JetStream | TREC-014 |
| 2 | TREC-018 | Move feature flags and operational config off Redis and into PostgreSQL | TREC-015 |
| 3 | TREC-020 | Consolidate overlapping traceability/versioning services into clear bounded domains | TREC-004 |
| 3 | TREC-021 | Preserve high-scale graph rendering while enforcing a single default graph path | TREC-020 |
| 3 | TREC-022 | Re-evaluate archived Rust/Tauri surface and decide whether to revive or delete | TREC-020 |
| 4 | TREC-030 | Bring up required local services and fix preflight failures with loud errors | TREC-010,TREC-014,TREC-015 |
| 4 | TREC-031 | Run backend Go unit/build validation | TREC-030 |
| 4 | TREC-032 | Run Python lint/type/test baseline | TREC-030 |
| 4 | TREC-033 | Run frontend build/performance smoke baseline | TREC-030 |
| 5 | TREC-040 | Build demo projects that exercise requirements, graph, versioning, and agent journeys | TREC-031,TREC-032,TREC-033 |
| 5 | TREC-041 | Write long-form operator and reader journeys with screenshots or recordings | TREC-040 |
| 6 | TREC-050 | Align AgilePlus completion plan to Tracera recovered state and shared org infra | TREC-041 |
