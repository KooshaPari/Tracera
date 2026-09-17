# WP-00 - Reconcile Accepted Horizon

**Work Packet:** WP-00
**Product:** Tracera
**Owner Role:** program
**State:** reconciliation_recorded
**Prepared:** 2026-09-16
**Acceptance Cases:** T38, T39

---

## 1. Current Refs

| Item | Value |
|---|---|
| Git HEAD | f4f28bb77c29db45cdc8bf9c10be38417557993d |
| Branch | main |
| Rust toolchain | stable (channel), edition 2021, rust-version 1.82 |
| Workspace crate count | 9 workspace members |
| SWEE node types | 30 (no Product or Capability variant) |
| SWEE edge types | 35 taxonomy rows (32 CHECK constraint strings) |

All references recorded at reconciliation time. Product execution status for this package: **not executed**.

---

## 2. Current Intent Inventory (R01-R36)

Every requirement is **specified_not_product_verified** unless otherwise noted. No requirement in this document is claimed as product-verified.

### Retained (valid obligation, mapped to existing code)

| Req | Title | Owner | Code Evidence |
|---|---|---|---|
| R02 | Searchable traversable computable graph | Tracera | `swee/` module: 30 NodeKind, 35 EdgeKind, graph CRUD via Store trait |
| R03 | Intent/observation/hypothesis distinct | Tracera | `queue/lifecycle.rs`: task states (ready/in_progress/done/failed) separate intent from execution |
| R05 | Violation/missing/stale/inconclusive distinguished | Tracera | Product program assessment model defines five statuses; reference `reports/demo/*.json` |
| R07 | Repo-scoped work persists across sessions | AgilePlus | `queue/lifecycle.rs`: SQLite-backed task lifecycle; claims table for agent assignment |
| R08 | One authoritative work lifecycle | AgilePlus | Atlas `delegation.rs`: WorkItem + AgentAssignment lifecycle |
| R13 | Collector failures cannot yield silent green | Tracera | Assessment model status `inconclusive` and `unknown`; collector failure rule family defined |
| R14 | Idempotent delivery, conflicting replay rejected | integration | `ingest/persist.rs` idempotency key handling; `ingest/trace_refs.rs` conflict detection |
| R15 | Identifiers survive transports | AgilePlus | Atlas WorkItemId/AgentId types with serde; cross-crate ID consistency |
| R23 | Deleted-project restoration excluded | program | `program.json:restoration_exclusions` explicitly lists Frostify, Pheno MLX, five unspecified |
| R32 | Use existing harness/substrate | integration | Workspace SQLite/Postgres dual-store; `tracera-cli`; existing migrations |
| R35 | AgentLens identity unresolved | program | `program.json:unresolved_names` lists AgentLens; no substitution permitted |
| R36 | Autonomy increases after measured outcomes | program | Program allocation rule in `00-executive-decision.md`; not yet measured |

### Deferred (valid obligation, specified but not yet implemented in code)

| Req | Title | Owner | Gap |
|---|---|---|---|
| R01 | Persistent product identity and canonical product model | Tracera | NodeKind has 30 types; no `Product` or `Capability` variant. Domain types in `store.rs` cover stories/sprints/projects but not the product-model identity required by the charter. |
| R04 | Automatic dissatisfaction | Tracera | Assessment model and rule families defined in program docs; no automated dissatisfaction engine code exists. |
| R06 | Human/external-agent resolution without native planning | AgilePlus | Spec 009 defines the ingestion contract; no AP adapter code in Tracera workspace. |
| R09 | AP works offline; Tracera supports external work systems | integration | Spec 009 drafted; no bidirectional bridge code exists. |
| R10 | Acceptance criteria cannot be weakened by same change | verification | No code enforcement; requires verified separation of concerns. |
| R11 | Authorization and optimistic concurrency on product changes | Tracera | `Store` trait has no version column or compare-and-swap operation. |
| R12 | Verification binds artifact, baseline, expectation, target | verification | Atlas `ci_bridge` normalizes CI events; no full verification-binding chain. |
| R16 | Persistent writes never advance false state | storage | `sqlite_store` and `pg_store` exist; migration safety not yet validated. |
| R17 | Atomic claims with fencing | AgilePlus | `queue/lifecycle.rs` claims table exists; no fencing token mechanism. |
| R18 | Truthful bounded errors and cancellation | integration | `StoreError::Database(String)` exists; no structured error contract. |
| R19 | Untrusted content cannot grant mutation authority | security | MCP write tools check auth; no formal trust boundary enforcement. |
| R20 | Release proof from exact installed candidate | release | R2 artifact uploader exists; no release-proof binding to installed target. |
| R21 | Independent evidence and denominators per quality family | verification | No quality-family evidence tracking code. |
| R22 | Reuse existing audit tools, no rival registry | integration | ADR-GOV-001 establishes AgilePlus as governance SSOT; no production registry integration. |
| R24 | Product map/dissatisfaction lead UI, not raw logs | Tracera | Frontend exists; dissatisfaction engine not implemented. |
| R25 | Equivalent human/machine product semantics | integration | MCP tools expose graph ops; no formal semantic parity contract. |
| R26 | Observation append does not revise baseline | Tracera | Assessment model defines this rule; no code-level enforcement. |
| R27 | Semantic findings retain assumptions | Tracera | No semantic/predictive findings code exists. |
| R28 | Repeat closed loop on second product | program | First loop not yet closed. |
| R29 | Migrations require consumer parity and tested rollback | storage | No migration validation tooling. |
| R30 | Reconcile and freeze accepted horizon | program | This document fulfills R30. |
| R31 | Implementation claims require artifacts | program | Documented as policy; not enforced in code. |
| R33 | Performance claims require measured workloads | verification | No benchmark harness. |
| R34 | Retention/redaction preserves identity | security | No retention/redaction code. |

### Retired (no longer applicable)

None. All 36 requirements remain either retained or deferred. No requirement has been retired by this reconciliation.

---

## 3. Native Work Claims

What the Tracera codebase currently owns and implements:

### 3.1 SWEE Graph Storage (`crates/tracera-server/src/swee/`)

- **NodeKind**: 30 typed variants (Requirement, Specification, Design, SourceFile, Module, Class, Function, Test, TestSuite, Commit, PullRequest, Branch, Issue, Epic, Story, Task, Bug, Sprint, Release, Build, Deployment, Evidence, Problem, Incident, ChangeRequest, Person, Team, Environment, Artifact, Metric)
- **EdgeKind**: 35-row taxonomy with 32 unique type strings (ADR-SWEE-001)
- **Domain types**: `SwreeNode`, `SweeEdge`, `SwreeNodeLabel`, `NodeRef`, `EdgeDefinition`
- **Schema**: `migrations/sqlite/003_swee_graph.sql`
- **ADR**: `docs/governance/ADR-SWEE-001-graph-schema-design.md`

### 3.2 Store Trait and Persistence (`crates/tracera-server/src/store.rs`)

- `Store` trait with `Arc<dyn Store + Send + Sync>` handler pattern
- `PgStore` (Postgres) and `SqliteStore` (SQLite) implementations
- Domain types: `EvidenceItem`, `Sprint`, `Story`, `TeamRow`, `ProjectSummary`
- Pagination via `ListParams` with validated page/page_size
- `StoreError` and `StoreResult<T>` error handling

### 3.3 Queue Lifecycle (`crates/tracera-server/src/queue/lifecycle.rs`)

- Task lifecycle: `release_task`, `complete_task`, `fail_task`
- SQLite-backed with claims table
- States: `ready`, `in_progress`, `done`, `failed`
- Ported from phenodag v0.3.0 (Go)

### 3.4 Ingest Pipeline (`crates/tracera-server/src/ingest/`)

- Adapters: `agcord.rs`, `github.rs`, `jira.rs`
- Persistence: `persist.rs` (idempotent write-through)
- Trace refs: `trace_refs.rs` (conflict detection)
- Benchmarking: `benchmark.rs`

### 3.5 Memory/Distillation (`crates/tracera-server/src/memory/`)

- `distillation/` sub-module: `config.rs`, `distiller.rs`, `graph_input.rs`, `memory.rs`, `pattern.rs`
- Pattern extraction and memory entry creation
- Graph input for distillation pipeline

### 3.6 Atlas ALM Engine (`crates/tracera-atlas/src/`)

- **delegation**: WorkItem, AgentAssignment, assignment lifecycle
- **agent_of_record**: Append-only mutation log, SignOff records
- **ci_bridge**: GitHub Actions webhook normalization to SDLC events
- **observability**: EventBus, SdlcEvent, SdlcStage, StageLog
- In-memory and pluggable persistence (SQLite/Postgres features)

### 3.7 MCP Bridge (`crates/tracera-mcp/src/`)

- `TraceraMcpServer` wrapping `Arc<dyn Store>`
- Tools: `list_nodes`, `get_node`, `neighbours` (read); `create_node`, `create_edge` (write); `propose_change` (propose)
- rmcp 3.2 transport (stdio, JSON-RPC 2.0)

### 3.8 Auth/WorkOS (`crates/tracera-workos/src/`)

- `auth.rs`: authentication
- `router.rs`: HTTP routing
- `webhooks.rs`: webhook handling
- `sync.rs`: synchronization
- `audit.rs`: audit logging

### 3.9 Supporting Infrastructure

- **Cache**: `cache/` (Upstash Redis REST, auto-disabled without `CACHE_URL`)
- **Neo4j sync**: `neo4j/` (Bolt client, auto-disabled without `NEO4J_URL`)
- **R2 artifacts**: `r2/` (Cloudflare R2 upload, auto-disabled without `R2_*`)
- **Events**: `tracera-events/` (ClickHouse ingestion)
- **GraphQL**: `tracera-graphql/` (schema, resolvers, REST parity)
- **ML**: `tracera-ml/` (embeddings, pgvector, qdrant, RAG)
- **Edge**: `tracera-edge/`
- **CLI**: `tracera-cli/` (bundle, compose, runtime)
- **Go CLI**: `tracera-go-cli/`
- **Python SDK**: `tracera-py-sdk/`
- **9 migration files** (0001-0009)

---

## 4. Exclusions (Not Restored)

The following are explicitly excluded from restoration and do not block the current horizon:

| Exclusion | Status | Source |
|---|---|---|
| Frostify | Restoration excluded | `program.json:restoration_exclusions`, R23 |
| Pheno MLX | Restoration excluded | `program.json:restoration_exclusions`, R23 |
| Five unspecified deleted projects | Restoration excluded | `program.json:restoration_exclusions`, R23 |
| AgentLens | Identity unresolved | `program.json:unresolved_names`, R35 |

No work item restores these projects or substitutes Agentora for AgentLens. This satisfies acceptance case T38.

---

## 5. Boundary Decisions

### 5.1 One Owner Per Fact

| Domain Fact | Authority | Integration Rule |
|---|---|---|
| Product identity, accepted intent, product relations, product-state interpretation | **Tracera** | Versioned commands and immutable baseline revisions |
| Working change intent, specs, work packages, execution transitions, claims/leases/checkpoints | **AgilePlus** | Repo/project isolation; optional Tracera projection; no competing state machine |
| Source content and revision | **Source repository** | Reference exact revision/blob; graph is not a replacement Git store |
| Measurement or test result | **Authenticated producing verifier** | Preserve input artifact, context, checker version, time, raw-result identity |
| Product assessment | **Tracera** assessment semantics over accepted inputs | A result may be failed, stale, unknown or inconclusive; no silent success |

### 5.2 Key Boundary Decisions

1. **Tracera owns the product model.** AgilePlus owns execution. Neither substitutes for the other.
2. **One owner per fact.** No dual-write, no competing state machines.
3. **No new repos, registries, or SDKs.** Reuse existing infrastructure.
4. **Atlas/AP consolidation.** Prefer AP's canonical work authority; migrate one capability at a time with parity tests (ADR-GOV-001).
5. **Existing Rust workspace and proven storage.** Start with SQLite/Postgres dual-store; optional graph/cache/object-store adapters remain optional.
6. **AP must remain useful offline without Tracera.** Tracera must represent externally managed products without AP.
7. **Product acceptance and work completion are different commands.**

### 5.3 Scope Boundaries (This Document)

- **Included:** Current intent, native work claims, obligation classification, boundary decisions, exact refs, rollback description.
- **Excluded:** No source retirement, no new repo creation, no silent scope shrink.

---

## 6. Rollback

This reconciliation is a documentation-only work package. No code was changed.

| Aspect | Pre-WP-00 State | Post-WP-00 State |
|---|---|---|
| Git HEAD | f4f28bb77c29db45cdc8bf9c10be38417557993d | Same (no code change) |
| Obligations | Implicit from scattered ADRs, specs, and program.json | Explicitly classified as retained/deferred/retired |
| Exclusions | Listed in program.json only | Documented here with R01-R36 mapping |
| Boundaries | ADR-GOV-001 + docs/03-boundaries-and-architecture.md | Confirmed and cross-referenced here |
| Native work claims | Implicit from crate inventory | Explicitly enumerated with file paths |

**Rollback action:** Delete `docs/WP-00-reconciliation.md`. No code or schema rollback required.

---

## 7. Acceptance Status

| Case | Description | Status | Evidence |
|---|---|---|---|
| T38 | Deleted projects stay outside restoration queue | **Pass** | R01-R36 classification shows no retired requirements restore excluded projects; R23 retained; R35 retained (AgentLens unresolved). No work items created for excluded projects. |
| T39 | Accepted horizon does not silently shrink | **Pass** | All 36 requirements classified: 12 retained, 24 deferred, 0 retired. Deferred items documented with specific code gaps. No requirement removed from scope. |

---

## 8. Remaining Risks and Next Steps

1. **R01 gap is critical.** The SWEE graph has no `Product` or `Capability` node kind. The product charter requires persistent canonical product identity. This is the first implementation gap to close (likely WP-01 territory).
2. **R04 (automatic dissatisfaction) has no code.** The assessment model is fully specified in program docs but no engine implements it.
3. **Atlas/AP consolidation is specified but not started.** ADR-GOV-001 and the boundaries doc define the approach; no migration has begun.
4. **No product-verified acceptance cases.** Every T01-T39 in program.json shows `not_executed_in_this_package`. The first closed loop requires at least T05/T06 (failed/healthy assessment) to pass on a real surface.
5. **Schema migration safety untested.** R16 and R29 require tested rollback; current migrations have no rollback rehearsal.

---

## 9. Capability Return (AGENT_RETURN template)

- **Work packet / mapped native work ID:** WP-00
- **Product / project / owning repository:** Tracera / `C:\Users\koosh\tracera`
- **Base commit / final commit / source blob references:** f4f28bb77c29db45cdc8bf9c10be38417557993d (main)
- **Accepted requirements and criteria revisions:** R01-R36 classified (12 retained, 24 deferred, 0 retired); T38/T39 pass
- **Reachable implementation and consumer path:** Documentation artifact; no code path changed
- **Candidate artifact digest / installed target digest:** This document (`docs/WP-00-reconciliation.md`)
- **Commands run, environment, raw result locations and outcomes:** File reads of all source crates, `git rev-parse HEAD`, `rust-toolchain.toml` inspection; all succeeded
- **Critical acceptance cases (passed / failed / unknown / inapplicable with reason):** T38 pass; T39 pass
- **Independent quality families and denominators:** Documentation deliverable; code quality N/A
- **Product outcome versus work-item state:** Reconciliation recorded; no product state changed
- **Current source/data coverage and observation cutoff:** All 9 workspace crates inspected; all 36 requirements classified; cutoff 2026-09-16
- **Regression/negative controls:** No code changed; zero regression risk
- **Migration / backup / restore / rollback evidence:** Delete this file to rollback
- **Remaining risk, conflict, blocked owner and exact unblock action:** R01 (no Product node kind) blocks product-model claims; unblock by adding node kinds in WP-01
- **Existing ledger/work item updated:** `docs/WP-00-reconciliation.md` created
- **Next smallest accepted outcome:** WP-01: Add Product and Capability node kinds to SWEE taxonomy; create product identity storage

---

*This document satisfies WP-00 outcome: "Reconcile current accepted obligations with the product-first owner clarification." All requirements remain `specified_not_product_verified`. No requirements were retired or silently removed.*
