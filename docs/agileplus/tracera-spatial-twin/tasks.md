# TRACERA-SPATIAL-001 — dependency-aware implementation DAG

**All tasks OPEN unless a separately linked native/consumer proof explicitly certifies them.** Code exists for parts of T03/T04 but is unverified.

| Task | Depends | Deliverable | Independent failure/acceptance oracle |
| --- | --- | --- | --- |
| T00 Source/intent reconciliation | — | Raw user prompts/hash + actual product graph current-state audit | Distinguish direct intent, inference, code, deployed behavior |
| T01 Product identity/capability scoping | T00 | Correct persisted product ↔ capability model and query adapter | Cross-product isolation, corrupted IDs fail closed |
| T02 Observations and baseline time | T01 | Explicit capability refs, real accepted_at, revision matching, historic lineage | Old/unknown/unlinked evidence not green; revision ≠ timestamp |
| T03 Read-side storage and APIs | T01,T02 | SQLite/Postgres parity + read-only bounded graph traversal | Reboot persist/read, no 501 for accepted product paths, no silent page clipping |
| T04 Scene IR / geometry truth | T01,T03 | Deterministic semantic scene with typed ports/references | Identity/edge roundtrip; physical meshes require provenance |
| T05 Semantic assembly UI | T03,T04 | Inspect, search, select, isolate, explode, navigate back | Real persisted product, no fabricated capability or source |
| T06 Trace/evidence lens | T02,T05 | User journey → capability → runtime/test/problem | Fail/unknown/stale/inconclusive distinct |
| T07 Temporal comparisons | T02,T04 | Two pinned baselines or configurations with stable IDs | No impossible temporal merge |
| T08 Physical/hybrid adapter | T04,T07 | One external CAD/BOM/firmware/geometry fixture with true units | Metaphor does not imply measured dimensions |
| T09 Dense graph and auth negatives | T03,T04,T05 | Bounded/paginated, ACL/redaction, aggregate membership checks | Hidden nodes/edges/counts cannot leak; truncate labeled |
| T10 Comparative research/UX | T05,T06,T09 | Controlled vs 2D/search/matrix tasks, reproducible resource metrics | Reject misleading/slow 3D patterns |
| T11 Release/CI and independent signoff | T00–T10 | Fresh local/installable/source/prod receipts + third-party review | Never substitute CI/file counts for real user witness |
| T12 Registry/ADR closure | T00,T11 | Curated producer-generated PhenoRegistry metadata and accepted decisions | No manual prose mistaken for regenerated canonical bindings |

## Work receipt schema

Each task's evidence must include: task_id, source_commit, product/baseline IDs, configuration and environment, test/fixture identity, exact observable output, timestamp, reviewer, assertion status (passed/failed/inconclusive/skipped/blocked), invalidation rule, and external source/evidence links.

## Execution ordering

Immediate: T01/T02/T03 with source-level tests; then T04/T05 proof using Tracera itself; then T06/T09. Parallel research T00/T10 can run independently. T07/T08 after baseline and scene semantics qualify. ADR decision and release remain blocked until T11/T12.

**CLI registration missing:** This work package is repo-local as required by AgilePlus project-scope policy. It has not been run through the AgilePlus CLI/SQLite acceptance path in this tool session.
