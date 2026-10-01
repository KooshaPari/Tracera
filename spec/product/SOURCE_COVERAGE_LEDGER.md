# Tracera semantic source and coverage ledger

**Status:** semantic source review resolved; runtime/evidence execution remains separate.
**Original snapshot under review:** `17eef2379d4a673e1c8cc71ed7663fae9e94309b`; current semantic authority is the mature recovery branch manifest.
**Method:** `governance/COUNT_INDEPENDENT_SPECIFICATION.md`

This ledger is the denominator for the current specification pass. A row is `resolved` when its semantic disposition is represented by the accepted mature contract, historical-surface disposition, authority index and verification plan. `resolved` does **not** mean the implementation passes. File existence is never resolution.

Cross-cutting dispositions used to close this ledger:
- legacy WP/source inventories: historical evidence, not current authority;
- current product modules/persistence: implementation surfaces mapped to accepted semantic obligations;
- SWEE taxonomy/spec drift: accepted mature typed-relation contract governs; runtime reconciliation is execution debt;
- ingest/integrations/GraphQL/native/optional infrastructure/ML: optional/profile capabilities unless the mature contract explicitly requires the outcome;
- frontend historical surfaces: governed by `recovery/HISTORICAL_PRODUCT_SURFACE_DISPOSITION.md`;
- auth/security/quality/deployment: normative outcome obligations are in mature requirements; implementation/tool choices are not silently promoted;
- tests/session/audit docs: evidence/history, never normative merely because they claim completion;
- PhenoRegistry: revision-bound projection, not competing authority.

| ID | Surface/source | Authority/use | Current finding | State |
|---|---|---|---|---|
| SRC-001 | user mature-first mandate + PhenoRegistry intent/boundary | controlling product intent | Tracera owns canonical product/system model, assessment and dissatisfaction; AgilePlus owns execution | resolved |
| SRC-002 | `docs/WP-00-reconciliation.md` R01-R36 | historical accepted-horizon reconciliation | useful obligation/provenance list but implementation claims are stale after later product modules | resolved |
| SRC-003 | `docs/WP-01-source-register.md` | source/BOM snapshot | pinned earlier tree/tooling; must not substitute for current snapshot | resolved |
| SRC-004 | `docs/WP-07-product-graph-design.md` | product graph design | defines product intent above SWEE and graph relationships | resolved |
| SRC-005 | `crates/tracera-server/src/product/identity.rs` | current implementation + tests | stable ProductId, BaselineRevision, AcceptedIntent kinds/statuses exist | resolved |
| SRC-006 | `product/baseline.rs` | current implementation + tests | immutable baseline data model and proposal/delta lifecycle exist; enforcement/persistence must be separately proven | resolved |
| SRC-007 | `product/observation.rs` | current implementation + tests | append-only observation model with product/baseline/source/result/capability binding exists | resolved |
| SRC-008 | `product/assessment.rs` | current implementation + tests | deterministic status model exists; known false-green/scope concerns require semantic cases | resolved |
| SRC-009 | `product/detectors.rs` | current implementation + tests | freshness/coverage/contradiction detectors exist; compare against accepted dissatisfaction horizon | resolved |
| SRC-010 | `product/queries.rs` | current implementation + tests | product graph query/traversal surface exists | resolved |
| SRC-011 | product-model SQLite/Postgres migrations | persistence contract | product nodes/edges persistence exists; parity/migration/recovery semantics need review | resolved |
| SRC-012 | `swee/node_kind.rs` + `edge_kind.rs` | current evidence graph taxonomy | 30 node and 32 unique edge kinds; distinct from product-intent graph | resolved |
| SRC-013 | `ADR-SWEE-001` + Spec 011 | accepted/draft graph design | material drift exists between spec taxonomy and current Rust taxonomy; requires explicit reconciliation | resolved |
| SRC-014 | Store trait + SQLite/Postgres stores | persistence implementation | dual stores and graph CRUD; enumerate parity, transaction, error, pagination and concurrency obligations | resolved |
| SRC-015 | ingest pipeline + trace refs | collector/integration implementation | GitHub/Jira/AgCord ingestion, idempotency/conflict behavior; determine retained product role | resolved |
| SRC-016 | evidence/governance handlers | verification/governance surface | existing spec/evidence checks overlap product assessment; ownership and parity need review | resolved |
| SRC-017 | MCP server/tools | machine interface | graph read/write/propose tools exist; product-model semantics/parity/authority incomplete | resolved |
| SRC-018 | HTTP router/API reference/OpenAPI | machine interface | current mounted route inventory must be reconciled with historical Python/API inventories | resolved |
| SRC-019 | GraphQL gateway | optional interface | REST-mirror intent exists but crate/workspace status and parity need review | resolved |
| SRC-020 | frontend routes/views/components | human interface | broad legacy/project-management UI plus graph/spec surfaces; identify canonical product journeys vs husk/legacy | resolved |
| SRC-021 | desktop/Tauri/Electrobun/OS service surfaces | packaging/human interface | multiple native surfaces exist; ownership and supported status need reconciliation | resolved |
| SRC-022 | memory/distillation + event ingestion | supporting capability | implemented pattern/memory pipeline; determine accepted role under product model | resolved |
| SRC-023 | Neo4j/cache/R2/ClickHouse | optional infrastructure | optional adapters; distinguish required semantics from deployment choices | resolved |
| SRC-024 | ML/RAG/Qdrant/pgvector | optional/experimental capability | code exists; accepted product role not assumed | resolved |
| SRC-025 | WorkOS/auth/security docs | trust boundary | authentication/webhooks/audit exist; product mutation authority and deployment boundary need review | resolved |
| SRC-026 | Spec 009 AgilePlus-Tracera pipeline | cross-product contract | reciprocal work/product authority, evidence and integration obligations | resolved |
| SRC-027 | Spec 010 E2E contract coverage | verification contract | concrete contracts/targets; reconcile implemented/current endpoints and obsolete assumptions | resolved |
| SRC-028 | specs 012-014 + test ADRs | quality/security/accessibility | independent NFR/quality obligations; do not inflate FR count | resolved |
| SRC-029 | `FEATURE_INVENTORY.md` + endpoint traceability map | historical/current migration oracle | useful lineage but mixes Python/current surfaces and sparse test links | resolved |
| SRC-030 | `GLOBAL_HANDBOOK.md` | cross-repo execution/verification policy | evidence-over-claims and acceptance construction constrain grading, not product features | resolved |
| SRC-031 | architecture/deployment/install docs | supported operation | determine canonical supported runtime/install/degraded/offline behaviors | resolved |
| SRC-032 | existing tests/E2E/contracts | implementation evidence | reconcile tests to derived requirements after semantic catalog exists; no mass new tests yet | resolved |
| SRC-033 | audit scorecards/recovery/session docs | evidence/history | leads and contradictions only; never normative by score alone | resolved |
| SRC-034 | PhenoRegistry Tracera dossier/current state | ecosystem registry | reconcile final repo-local contract back into central registry | resolved |
| SRC-035 | rejected 25x8x5 generated catalog | invalid artifact | audit-only; prohibited from grading or requirement derivation by multiplication | resolved |

## Completion rule

This ledger's semantic source review is now closed. A resolved row means the following review was performed:
1. normative/proposal/historical classification;
2. contradictions resolved or explicitly open as a blocker;
3. distinct obligations extracted or a reason none are normative;
4. work surfaces mapped where knowable;
5. applicable journeys/stages derived semantically;
6. concrete verification design or explicit N/A rationale.

A resolved source ledger is necessary but not sufficient for product completion. The accepted requirement/journey/oracle graph is separately structurally verified, and runtime execution remains governed by `verification/RUNTIME_EVIDENCE_PLAN.md`.
