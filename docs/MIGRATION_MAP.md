# Tracera Migration Map (Oracle-Gated)

**Oracle source:** `C:/Users/koosh/Dev/_tracera_feature_inventory.md`  
**Constraint:** 24 main endpoints across 11 routers are the preserved capability baseline.  
**Hard gate (MANDATORY):** after each migration step, re-run the endpoint inventory and API diff; zero net capability loss is required before proceeding.

## Per-component migration map

| Component | Decision | ADR-style rationale |
|---|---|---|
| FastAPI service (`src/tracertm/api/main.py`, `src/tracertm/api/deps.py`, middleware) | KEEP-on-UV-Python-3.14 | Gateway logic (DI, middleware, auth dependency chain, app bootstrapping) is the integration layer and remains safest in Python while keeping endpoint contracts stable. |
| `tracera-core` Rust crate (`crates/tracera-core`) | KEEP-on-Rust | Existing Rust crate already owns shared traceability domain types and impact/coverage primitives; keeping core algorithms in Rust minimizes drift and improves deterministic, high-performance computation. |
| TS frontend SDK (`frontend/packages/api-client`, `frontend/packages/types`) | KEEP-on-Bun+TS7 | SDK is a client/typed-contract consumer surface; Bun+TS7 keeps consumer velocity and aligns with existing frontend packaging. |
| Router `__init__` (`src/tracertm/api/routers/__init__.py`) | REDUCE/DELETE | It only carries package docs and is a no-op routing surface; migration can safely remove this indirection after all active routers are explicitly registered in the target service layout. |
| Router `auth` (`src/tracertm/api/routers/auth.py`) | KEEP-on-UV-Python-3.14 | Identity and auth flow is edge-tier infra, with strong external provider dependencies and no algorithmic core value over Rust migration. |
| Router `code_trace` (`src/tracertm/api/routers/code_trace.py`) | KEEP-on-UV-Python-3.14 | Domain-assembly endpoint (repository lookups + serialization shaping) is IO-bound and tightly coupled to existing Python repositories. |
| Router `comments` (`src/tracertm/api/routers/comments.py`) | KEEP-on-UV-Python-3.14 | CRUD-like collaboration feature is Tier-2 UX/business functionality; keep in Python for parity with ORM/session conventions. |
| Router `evidence` (`src/tracertm/api/routers/evidence.py`) | KEEP-on-UV-Python-3.14 | Currently lightweight/pillar-style API; no strong perf pressure and no evidence of mature Rust equivalents. |
| Router `impact` (`src/tracertm/api/routers/impact.py`) | MIGRATE→Rust | `impact` traversal and affected-artifact semantics are core graph-analysis behavior and should move to Rust once Neo4j access adapters are bridged. |
| Router `impact_scoring` (`src/tracertm/api/routers/impact_scoring.py`) | MIGRATE→Rust | Pure blast-radius scoring is deterministic numeric logic; matches Tier-1 core doctrine and should live in Rust for consistency with `traceability_core`-style models. |
| Router `ingest` (`src/tracertm/api/routers/ingest.py`) | KEEP-on-UV-Python-3.14 | Integration adapters for GitHub/Jira ingestion are glue-heavy and service-connector bound; keep as fast-moving Python edges. |
| Router `org_intel` (`src/tracertm/api/routers/org_intel.py`) | KEEP-on-UV-Python-3.14 | Organizational metrics/teams is operational/supporting surface; no compelling reason to move before product semantics are finalized. |
| Router `sdlc_pm` (`src/tracertm/api/routers/sdlc_pm.py`) | KEEP-on-UV-Python-3.14 | PM/project-management data shape is domain-edge capability and should remain near the application layer. |
| Router `traceability` (`src/tracertm/api/routers/traceability.py`) | MIGRATE→Rust | Coverage matrix + governance + confidence are core algorithmic contracts and align with `tracera-core`/`traceability_core` ownership. |

## Preservation checklist (24 endpoints to keep)

All routes are shown with the service mount path currently used by FastAPI: prefix `/api/v1` when routers are mounted via `include_router(..., prefix="/api/v1")`.

1. `GET /api/v1/auth/me`  
   Request: Auth claims + DB dep (`claims`, `db`)  
   Response: `MeResponse`
2. `GET /api/v1/analysis/code-trace/{component_id}`  
   Request: `component_id`, optional `project_id`, claims/db deps  
   Response: inline object (`id`, `name`, `description`, `levels`, `overallConfidence`, `lastUpdated`)
3. `GET /api/v1/items/{item_id}/comments/`  
   Request: `item_id` + claims/db deps  
   Response: `list[CommentResponse]`
4. `POST /api/v1/items/{item_id}/comments/`  
   Request: `CreateCommentBody`  
   Response: `CommentResponse`
5. `DELETE /api/v1/items/{item_id}/comments/{comment_id}`  
   Request: `item_id`, `comment_id` + claims/db deps  
   Response: 204 No Content
6. `GET /api/v1/evidence/health`  
   Request: none  
   Response: `{pillar: "evidence", status: "ok"}`
7. `GET /api/v1/evidence`  
   Request: none  
   Response: `List[EvidenceResponse]`
8. `POST /api/v1/evidence`  
   Request: `EvidenceCreate`  
   Response: `EvidenceResponse`
9. `GET /api/v1/impact/forward/{artifact_id}`  
   Request: `artifact_id`, claims/db-like driver dep  
   Response: `{artifact_id, direction, total, affected}`
10. `GET /api/v1/impact/reverse/{artifact_id}`  
    Request: `artifact_id`, claims/db-like driver dep  
    Response: `{artifact_id, direction, total, upstream}`
11. `POST /api/v1/impact/blast-radius`  
    Request: `BlastRadiusRequest`  
    Response: `BlastRadiusResult`
12. `POST /api/v1/ingest/github`  
    Request: `GitHubIssueIngestRequest`  
    Response: `BulkIngestionResult`
13. `POST /api/v1/ingest/jira`  
    Request: `JiraIssueIngestRequest`  
    Response: `BulkIngestionResult`
14. `GET /api/v1/org-intel/health`  
    Request: none  
    Response: `{pillar: "org_intel", status: "ok"}`
15. `GET /api/v1/org-intel/metrics`  
    Request: none  
    Response: `MetricsResponse`
16. `GET /api/v1/org-intel/teams`  
    Request: none  
    Response: `List[TeamResponse]`
17. `GET /api/v1/sdlc-pm/health`  
    Request: none  
    Response: `{pillar: "sdlc_pm", status: "ok"}`
18. `GET /api/v1/sdlc-pm/sprints`  
    Request: none  
    Response: `List[SprintResponse]`
19. `GET /api/v1/sdlc-pm/stories`  
    Request: none  
    Response: `List[StoryResponse]`
20. `POST /api/v1/sdlc-pm/sprints`  
    Request: `SprintCreate`  
    Response: `SprintResponse`
21. `POST /api/v1/coverage-matrix`  
    Request: `CoverageMatrixRequest`  
    Response: `CoverageMatrixResponse`
22. `POST /api/v1/governance/spec-check`  
    Request: `GovernanceCheckRequest`  
    Response: `GovernanceReport`
23. `POST /api/v1/impact`  
    Request: `ImpactRequest`  
    Response: `ImpactResponse`
24. `POST /api/v1/confidence`  
    Request: `ConfidenceRequest`  
    Response: `ConfidenceResponse`

## Oracle gap callout

The oracle explicitly marks `adrs`, `linear`, `blockchain`, `chat`, and `codex` as genuinely absent from main. Per doctrine, these are out-of-scope for this map and must not be reintroduced without a separate capability decision record.
