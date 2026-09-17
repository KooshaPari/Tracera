# WP-00 — G0 Reconciliation: Owner Intent, Authority and Accepted Horizon

**Date:** 2026-09-17
**Author:** Jcode (coordinator agent)
**Status:** Reconciled (proposed)
**Source ref:** `66ce888ba` (HEAD at reconciliation time)
**Rust toolchain:** stable 1.98.0 (88d9e12ae 2026-08-18)

---

## 1. Current Intent Inventory

All 36 requirements from the Tracera Product Program v1 are classified as `specified_not_product_verified`.
No requirement has been promoted to product-verified status. This reconciliation maps each to the codebase.

### Retained (code exists, direction confirmed)

| Req | Title | Code Location |
|-----|-------|--------------|
| R01 | Persistent product identity and canonical accepted product model | `product/identity.rs`, `product/baseline.rs` (new) |
| R02 | Searchable traversable computable graph with bounded expansion | `swee/` module (NodeKind 30 types, EdgeKind 32 types) |
| R03 | Accepted intent, observed state and hypotheses remain distinct | `product/identity.rs` (IntentKind, IntentStatus) |
| R04 | Automatic dissatisfaction exists in the first accepted horizon | Not yet implemented — WP-10/11 scope |
| R05 | Violation, missing assurance, stale and inconclusive results are distinguished | `product/observation.rs` (ObservationResult enum) |
| R06 | Human or external-agent resolution works without native autonomous planning | `tracera-mcp` bridge |
| R07 | Repo/project-scoped work persists across sessions | `store.rs` (projects, sprints, stories, evidence) |
| R08 | One authoritative work lifecycle; Tracera delegates scoped execution | Atlas (`tracera-atlas`) + AgilePlus (`agileplus-domain`) |
| R22 | Reuse existing audit/evaluation/ledger tools; no rival registry | `audit/` directory, scorecard tooling |
| R23 | Deleted-project restoration is excluded | **Exclusion confirmed** — see §3 |
| R24 | Product map, capabilities and dissatisfaction lead the UI | Target state — not implemented |
| R29 | Product-first graph semantics above SWEE | WP-07 design complete (`docs/WP-07-product-graph-design.md`) |
| R30 | Reconciled horizon with no silent shrink | This document |

### Deferred (valid, not yet implemented)

| Req | Title | Target WP |
|-----|-------|-----------|
| R04 | Automatic dissatisfaction | WP-10, WP-11 |
| R10 | Acceptance criteria cannot be weakened by unapproved change | WP-12, WP-14 |
| R11 | Accepted product changes use authorization and optimistic concurrency | WP-02 (partially), WP-17 |
| R12 | Verification binds artifact, product baseline, expectation, installed target | WP-12, WP-14 |
| R13 | Evidence expiry, collector failures and conflicts cannot yield silent green | WP-10, WP-11 |
| R14 | Duplicate delivery is idempotent; conflicting replay is rejected | WP-17 |
| R16 | Persistent writes, recovery and migration failures never advance false state | WP-17 |
| R17 | Concurrent claims use atomic ownership, leases and fencing | WP-06 |
| R18 | Machine interfaces return truthful bounded errors | WP-05 |
| R19 | Untrusted repository/model content cannot grant mutation authority | WP-17 |
| R20 | Release proof from exact installed/deployed candidate | WP-19 |
| R21 | Applicable quality families have independent evidence and denominators | WP-18 |
| R25 | Human and machine clients expose equivalent product/work semantics | WP-25 |
| R26 | Observation append does not revise accepted baseline; invalidation is explicit | WP-02 (types), WP-09 (queries) |

### Not Applicable (excluded or unrelated)

| Req | Title | Reason |
|-----|-------|--------|
| R23 | Deleted-project restoration is excluded | Program prohibition — Frostify, Pheno MLX, 5 unspecified deleted projects |
| R35 | AgentLens identity | **Unresolved** — do not substitute Agentora |

---

## 2. Native Work Claims

Current capabilities owned by the Tracera workspace:

| Component | Crate | Lines | Status |
|-----------|-------|-------|--------|
| SWEE graph schema | `tracera-server/src/swee/` | 853 | Active, split into modules |
| Store trait + SQLite/PG impls | `tracera-server/src/store.rs`, `sqlite_store/`, `pg_store/` | ~1200 | Active, domain modules |
| Ingest pipeline | `tracera-server/src/ingest/` | ~600 | Active, split by source |
| Product identity types | `tracera-server/src/product/` | 569 | **New this session** |
| Memory/distillation | `tracera-server/src/memory/` | 635 | Active, split into modules |
| Traceability matrix | `tracera-server/src/traceability.rs` | 423 | Active |
| HTTP handlers | `tracera-server/src/handlers/` | ~800 | Active, split by domain |
| Router + middleware | `tracera-server/src/router.rs`, `middleware.rs` | ~500 | Active |
| MCP bridge | `tracera-mcp/` | ~200 | Active |
| Atlas (agent of record) | `tracera-atlas/` | ~400 | Active, overlapping with AP |
| AgilePlus domain | `agileplus-domain/` | ~300 | Active, overlapping with Atlas |
| Traceability core | `traceability-core/` | ~300 | Active, lifecycle state machine |
| WorkOS integration | `tracera-workos/` | ~500 | Active |

---

## 3. Exclusions

The following are explicitly NOT restored, recreated, or substituted:

- **Frostify** — excluded by program prohibition
- **Pheno MLX** — excluded by program prohibition
- **Five unspecified deleted projects** — excluded; cannot restore without identification
- **AgentLens** — identity unresolved; do NOT substitute Agentora
- **No new repos** — everything stays in the existing workspace
- **No new registries** — no parallel identity/assessment registries
- **No new SDKs** — reuse existing transport contracts

---

## 4. Boundary Decisions

| Decision | Authority | Confirmation |
|----------|-----------|-------------|
| Tracera owns product model | Tracera | R01, WP-02 types created |
| AgilePlus owns execution | AgilePlus | R08, existing AP domain crate |
| One owner per fact | Program | Architecture doc §1 confirmed |
| No new infrastructure | Program | Existing Rust workspace + SQLite/PG |
| AP works offline without Tracera | Integration | R09 — not yet verified |
| Product acceptance ≠ work completion | Program | R10 — types distinguish these |

---

## 5. Current Refs

| Item | Value |
|------|-------|
| Git HEAD | `66ce888ba` |
| Rust toolchain | stable 1.98.0 (88d9e12ae) |
| Cargo workspace | 13 crates |
| Frontend | Bun + Next.js (apps/web) |
| CI | GitHub Actions (ci.yml, deploy-*.yml) |
| Database | SQLite (repo-local) + Postgres (optional) |
| Product program | v1.0.0 (2026-09-15) |

---

## 6. Gate G0 Exit Criteria

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Current ref recorded | ✅ | `66ce888ba` above |
| Intent reconciled | ✅ | §1 classifies all 36 reqs |
| Exclusions confirmed | ✅ | §3 |
| Boundary decisions documented | ✅ | §4 |
| Native work claims inventoried | ✅ | §2 |
| No silent horizon shrink | ✅ | Deferred items explicitly listed |

---

## 7. Rollback

- Prior commit: `1f55ff952` (before product types were introduced)
- Revert: `git revert 66ce888ba 925e616d3`
- No schema changes to roll back (migrations are forward-only, not yet applied)
- No data changes (types are additive, `#![allow(dead_code)]`)

---

*This document is the WP-00 deliverable. It reconciles intent without starting a new governance platform.*
*Next: WP-01 (source register) and WP-02 (types) are already completed this session.*
