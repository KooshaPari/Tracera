# phenoShared Consumer Audit — 2026-04-26

**Scope:** Verify 6 claimed consumers of phenoShared (phenotype-shared alias) and its sublibraries (phenotype-error-core, phenotype-health) are actually consuming them as documented.

**Finding:** **5 of 6 repos DO NOT contain documented dependencies**. Phase 1 forced-adoption claims are unverified.

---

## Executive Summary

| Repo | Dependency | Claimed | Actual | Status |
|------|------------|---------|--------|--------|
| AuthKit | phenotype-error-core | Yes (error-core) | NO | **UNVERIFIED** |
| ResilienceKit | phenotype-error-core | Yes (error-core) | NO | **UNVERIFIED** |
| hwLedger-core | phenotype-error-core | Yes (error-core) | NO | **UNVERIFIED** |
| TestingKit | phenotype-health | Yes (health) | NO | **UNVERIFIED** |
| hwledger-server | phenotype-health | Yes (health) | NO | **UNVERIFIED** |
| hwledger-agent | phenotype-health | Yes (health) | NO | **UNVERIFIED** |

**1 partial match:** AuthKit/phenotype-security-aggregator references phenotype-health as optional feature.

---

## Detailed Findings

### Error-Core Consumers (Claimed Phase 1)

#### 1. AuthKit
- **Root Cargo.toml:** `/Users/kooshapari/CodeProjects/Phenotype/repos/AuthKit/rust/Cargo.toml`
- **Status:** UNVERIFIED
- **Workspace dependencies:** thiserror, serde, tokio, chrono — NO phenotype-error-core
- **Child crate: phenotype-security-aggregator** — References `phenotype-health` (optional, path = "../phenotype-health")
  - **Feature gate:** `health-integration = ["dep:phenotype-health"]`
  - **Note:** phenotype-health IS referenced, but phenotype-error-core is NOT
- **Verdict:** AuthKit DOES consume phenotype-health (conditionally), but NOT phenotype-error-core

#### 2. ResilienceKit
- **Root Cargo.toml:** `/Users/kooshapari/CodeProjects/Phenotype/repos/ResilienceKit/rust/Cargo.toml`
- **Status:** UNVERIFIED
- **Workspace dependencies:** 
  - serde, thiserror, async-trait, tokio
  - phenotype-port-interfaces (from PhenoContracts, not phenoShared)
- **NO phenotype-error-core, NO phenotype-health**
- **Verdict:** ResilienceKit does NOT consume phenotype-error-core or phenotype-health

#### 3. hwLedger-core
- **Cargo.toml:** `/Users/kooshapari/CodeProjects/Phenotype/repos/hwLedger/crates/hwledger-core/Cargo.toml`
- **Status:** UNVERIFIED
- **Dependencies:** thiserror, serde_json only
- **NO phenotype-error-core or phenotype-health**
- **Verdict:** hwLedger-core does NOT consume phenotype-error-core or phenotype-health

### Health Consumers (Claimed Phase 1)

#### 4. TestingKit
- **Root Cargo.toml:** `/Users/kooshapari/CodeProjects/Phenotype/repos/TestingKit/rust/Cargo.toml`
- **Status:** UNVERIFIED
- **Workspace dependencies:** tokio, serde, mockall
- **NO phenotype-health or phenotype-error-core**
- **Verdict:** TestingKit does NOT consume phenotype-health

#### 5. hwledger-server
- **Cargo.toml:** `/Users/kooshapari/CodeProjects/Phenotype/repos/hwLedger/crates/hwledger-server/Cargo.toml`
- **Status:** UNVERIFIED
- **Dependencies:** tokio, tracing, axum, sqlx, hwledger-fleet-proto, hwledger-ledger, and standard utilities
- **NO phenotype-health or phenotype-error-core**
- **Verdict:** hwledger-server does NOT consume phenotype-health

#### 6. hwledger-agent
- **Cargo.toml:** `/Users/kooshapari/CodeProjects/Phenotype/repos/hwLedger/crates/hwledger-agent/Cargo.toml`
- **Status:** UNVERIFIED
- **Dependencies:** tokio, tracing, reqwest, serde, hwledger-fleet-proto, hwledger-probe, and standard utilities
- **NO phenotype-health or phenotype-error-core**
- **Verdict:** hwledger-agent does NOT consume phenotype-health

---

## Cross-Cutting Observations

### phenoShared Reference in hwLedger Workspace
The root `Cargo.toml` DOES declare phenotype-event-sourcing from phenoShared:
```toml
[workspace.dependencies]
# phenotype-shared reuse (ADR-0005). Pulled from KooshaPari/PhenoKits via git
phenotype-event-sourcing = { path = "vendor/phenotype-event-sourcing" }
```

**Note:** Only `hwledger-ledger` actually uses this vendored crate (per inline comment). phenotype-error-core and phenotype-health are NOT declared in hwLedger workspace.

### What's Actually Being Consumed
- **hwLedger:** phenotype-event-sourcing (ONLY, vendored)
- **AuthKit:** phenotype-health (optional feature in phenotype-security-aggregator)
- **ResilienceKit, TestingKit:** NO phenoShared libraries
- **hwledger-server, hwledger-agent:** NO phenoShared libraries

---

## Impact

**Phase 1 Forced-Adoption Claim:** "3/3 closed" (AuthKit, ResilienceKit, hwLedger-core error-core; TestingKit, hwledger-server, hwledger-agent health)

**Audit Finding:** Only **1 partial match** (AuthKit phenotype-health, optional). The other 5 repos are **NOT consuming the documented libraries**.

**Implications:**
1. phenotype-error-core was never forcibly adopted into ResilienceKit or hwLedger-core
2. phenotype-health was never adopted into TestingKit, hwledger-server, or hwledger-agent
3. Claims of "Phase 1 closed" are unsubstantiated by Cargo.toml evidence
4. phenotype-event-sourcing IS consumed (hwLedger via vendor), but phenotype-health/phenotype-error-core adoption remains incomplete

---

## Recommendations

1. **Verify memory note:** Cross-check `/repos/docs/governance/phenoshared-consumer-audit-2026-04-25.md` (if exists) for original claim provenance
2. **Reconcile adoption timeline:** If Phase 1 was meant to close these dependencies, determine why they are absent from Cargo.toml
3. **Clarify consumption:** If these libraries ARE used but not declared, resolve missing dependency declarations
4. **Update tracking:** Correct any AgilePlus specs or status docs claiming Phase 1 completion

---

## Audit Metadata

- **Date:** 2026-04-26
- **Method:** Cargo.toml inspection via Contents API (direct file read)
- **Repos Checked:** 6/6
- **Tool Calls:** 14
- **Branch:** pre-extract/tracera-sprawl-commit
