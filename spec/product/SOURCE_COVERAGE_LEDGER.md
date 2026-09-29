# Tracera semantic source and coverage ledger

**Status:** active replacement work; incomplete until every row is resolved.
**Snapshot under review:** `17eef2379d4a673e1c8cc71ed7663fae9e94309b`
**Method:** `governance/COUNT_INDEPENDENT_SPECIFICATION.md`

This ledger is the denominator for the current specification pass. A row may only become `resolved` after its normative intent, current implementation surface, contradictions, requirement decomposition, stage/journey relevance, and verification design have been reviewed. File existence is not resolution.

| ID | Surface/source | Authority/use | Current finding | State |
|---|---|---|---|---|
| SRC-001 | user mature-first mandate + PhenoRegistry intent/boundary | controlling product intent | Tracera owns canonical product/system model, assessment and dissatisfaction; AgilePlus owns execution | resolved |
| SRC-002 | `docs/WP-00-reconciliation.md` R01-R36 | historical accepted-horizon reconciliation | useful obligation/provenance list but implementation claims are stale after later product modules | reviewing |
| SRC-003 | `docs/WP-01-source-register.md` | source/BOM snapshot | pinned earlier tree/tooling; must not substitute for current snapshot | reviewing |
| SRC-004 | `docs/WP-07-product-graph-design.md` | product graph design | defines product intent above SWEE and graph relationships | reviewing |
| SRC-005 | `crates/tracera-server/src/product/identity.rs` | current implementation + tests | stable ProductId, BaselineRevision, AcceptedIntent kinds/statuses exist | reviewing |
| SRC-006 | `product/baseline.rs` | current implementation + tests | immutable baseline data model and proposal/delta lifecycle exist; enforcement/persistence must be separately proven | reviewing |
| SRC-007 | `product/observation.rs` | current implementation + tests | append-only observation model with product/baseline/source/result/capability binding exists | reviewing |
| SRC-008 | `product/assessment.rs` | current implementation + tests | deterministic status model exists; known false-green/scope concerns require semantic cases | reviewing |
| SRC-009 | `product/detectors.rs` | current implementation + tests | freshness/coverage/contradiction detectors exist; compare against accepted dissatisfaction horizon | reviewing |
| SRC-010 | `product/queries.rs` | current implementation + tests | product graph query/traversal surface exists | reviewing |
| SRC-011 | product-model SQLite/Postgres migrations | persistence contract | product nodes/edges persistence exists; parity/migration/recovery semantics need review | pending |
| SRC-012 | `swee/node_kind.rs` + `edge_kind.rs` | current evidence graph taxonomy | 30 node and 32 unique edge kinds; distinct from product-intent graph | reviewing |
| SRC-013 | `ADR-SWEE-001` + Spec 011 | accepted/draft graph design | material drift exists between spec taxonomy and current Rust taxonomy; requires explicit reconciliation | reviewing |
| SRC-014 | Store trait + SQLite/Postgres stores | persistence implementation | dual stores and graph CRUD; enumerate parity, transaction, error, pagination and concurrency obligations | pending |
| SRC-015 | ingest pipeline + trace refs | collector/integration implementation | GitHub/Jira/AgCord ingestion, idempotency/conflict behavior; determine retained product role | pending |
| SRC-016 | evidence/governance handlers | verification/governance surface | existing spec/evidence checks overlap product assessment; ownership and parity need review | pending |
| SRC-017 | MCP server/tools | machine interface | graph read/write/propose tools exist; product-model semantics/parity/authority incomplete | reviewing |
| SRC-018 | HTTP router/API reference/OpenAPI | machine interface | current mounted route inventory must be reconciled with historical Python/API inventories | pending |
| SRC-019 | GraphQL gateway | optional interface | REST-mirror intent exists but crate/workspace status and parity need review | pending |
| SRC-020 | frontend routes/views/components | human interface | broad legacy/project-management UI plus graph/spec surfaces; identify canonical product journeys vs husk/legacy | pending |
| SRC-021 | desktop/Tauri/Electrobun/OS service surfaces | packaging/human interface | multiple native surfaces exist; ownership and supported status need reconciliation | pending |
| SRC-022 | memory/distillation + event ingestion | supporting capability | implemented pattern/memory pipeline; determine accepted role under product model | reviewing |
| SRC-023 | Neo4j/cache/R2/ClickHouse | optional infrastructure | optional adapters; distinguish required semantics from deployment choices | pending |
| SRC-024 | ML/RAG/Qdrant/pgvector | optional/experimental capability | code exists; accepted product role not assumed | pending |
| SRC-025 | WorkOS/auth/security docs | trust boundary | authentication/webhooks/audit exist; product mutation authority and deployment boundary need review | pending |
| SRC-026 | Spec 009 AgilePlus-Tracera pipeline | cross-product contract | reciprocal work/product authority, evidence and integration obligations | reviewing |
| SRC-027 | Spec 010 E2E contract coverage | verification contract | concrete contracts/targets; reconcile implemented/current endpoints and obsolete assumptions | reviewing |
| SRC-028 | specs 012-014 + test ADRs | quality/security/accessibility | independent NFR/quality obligations; do not inflate FR count | pending |
| SRC-029 | `FEATURE_INVENTORY.md` + endpoint traceability map | historical/current migration oracle | useful lineage but mixes Python/current surfaces and sparse test links | reviewing |
| SRC-030 | `GLOBAL_HANDBOOK.md` | cross-repo execution/verification policy | evidence-over-claims and acceptance construction constrain grading, not product features | reviewing |
| SRC-031 | architecture/deployment/install docs | supported operation | determine canonical supported runtime/install/degraded/offline behaviors | pending |
| SRC-032 | existing tests/E2E/contracts | implementation evidence | reconcile tests to derived requirements after semantic catalog exists; no mass new tests yet | pending |
| SRC-033 | audit scorecards/recovery/session docs | evidence/history | leads and contradictions only; never normative by score alone | pending |
| SRC-034 | PhenoRegistry Tracera dossier/current state | ecosystem registry | reconcile final repo-local contract back into central registry | pending |
| SRC-035 | rejected 25x8x5 generated catalog | invalid artifact | audit-only; prohibited from grading or requirement derivation by multiplication | resolved |

## Completion rule

This ledger reaches 100% source-coverage review only when every non-excluded row is `resolved` with:
1. normative/proposal/historical classification;
2. contradictions resolved or explicitly open as a blocker;
3. distinct obligations extracted or a reason none are normative;
4. work surfaces mapped where knowable;
5. applicable journeys/stages derived semantically;
6. concrete verification design or explicit N/A rationale.

A resolved source ledger is necessary but not sufficient for the final 100% specification claim; the requirement catalog and trace graph receive separate semantic and structural verification.
