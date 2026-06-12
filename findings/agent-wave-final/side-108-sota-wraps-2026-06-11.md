# SOTA Wrap Analysis: StrictDoc, Kuzu, OpenFastTrace, Graphiti

Date: 2026-06-11

Note: Network access was unavailable in this agent session; this is based on known public project facts.

## Summary Table

| Project | Summary | License | Integration effort | Why / why not |
| --- | --- | --- | --- | --- |
| StrictDoc | Requirements and documentation system built around structured requirements, traceability, exports, and static-site style documentation. Strong fit for requirements-as-code and auditable requirement IDs. | Apache-2.0 | Medium | Wrap now if Tracera needs requirement ingestion/export and document-first traceability. Defer deeper coupling until Tracera's own schema is stable. |
| Kuzu | Embedded property graph database written in C++ with Cypher support and language bindings; designed for local analytical graph workloads. Strong fit for fast local trace graph traversal without running Neo4j. | MIT | Medium | Wrap now as an optional graph backend or analysis engine because it maps directly to traceability queries. Avoid making it mandatory until storage abstractions and packaging constraints are validated. |
| OpenFastTrace | Java tool for requirement tracing across source, docs, and test artifacts using lightweight tags and generated trace reports. Useful as a reference/interop target for existing trace-tag workflows. | MIT | Medium-high | Defer wrapping because JVM/toolchain orchestration adds operational cost and its model overlaps with functionality Tracera likely wants natively. Consider import/export compatibility later. |
| Graphiti | Temporal knowledge graph framework for building evolving entity/relation memory over time, commonly paired with LLM workflows. Strong concept fit for temporal provenance and evolving trace context. | Apache-2.0 | High | Defer for now unless temporal KG is the immediate product bet. Its LLM/memory orientation is promising but heavier and less directly requirements-trace-specific than StrictDoc or Kuzu. |

## Recommendations

Wrap now:

1. **Kuzu**: best immediate infrastructure leverage for local trace graph queries, impact analysis, and dependency traversal.
2. **StrictDoc**: best immediate requirements interoperability target for structured requirements and human-readable trace artifacts.

Defer:

1. **OpenFastTrace**: useful compatibility target, but JVM integration and overlap with native tracing make it a second-wave wrapper.
2. **Graphiti**: valuable for temporal KG strategy, but too broad/heavy for a first wrapper unless Tracera is prioritizing AI memory/provenance immediately.

## Practical Wrapper Shape

- Kuzu: adapter behind Tracera's graph/query boundary; support import, traversal queries, and export of trace edges.
- StrictDoc: importer/exporter for requirement documents and stable IDs; keep source-of-truth ownership in Tracera.
- OpenFastTrace: later CLI bridge for tag ingestion/report comparison.
- Graphiti: later experimental temporal layer for evented traces and evolving rationale.
