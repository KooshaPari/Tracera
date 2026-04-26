# Governance & Policy Findings

**Index:** Worklog entries from governance audits, policy enforcement, and architectural decisions.

---

## 2026-04-26 | Archive State Canonical Verification

**Scope:** Repo archived/active status audit across ~11 claimed archive repos  
**Finding:** 8 repos confirmed archived (KVirtualStage, kmobile, Logify, Authvault, Settly, worktree-manager, phenoXddLib, phenotype-infrakit); 2 active non-archived (DevHex, phenodocs); 1 deleted (Pyron → 404). Recently archived (2026-04-26): Authvault, Settly, worktree-manager. Memory drift risk documented — archive state goes stale between audits; no passive sync, remediation recommends weekly periodic refresh.  
**Evidence:** `docs/governance/archive-state-canonical-2026-04-26.md`  
**Tag:** `[governance]` — archive/state tracking

---

## 2026-04-26 | phenoShared Deep Dependency Audit (Phase 1 Partial)

**Scope:** Consumer adoption of phenotype-error-core, phenotype-health across claimed 4 repos  
**Finding:** Shallow audit incomplete. Deep audit (recursive Cargo.toml + src/ grep) found: 3 real consumers (AuthKit phenotype-policy-engine + phenotype-security-aggregator; TestingKit phenotype-compliance-scanner); 2 dead/orphaned dependencies (ResilienceKit phenotype-state-machine, TestingKit phenotype-test-fixtures declared but unused); hwLedger = zero dependencies (not a consumer). Memory claim "Phase 1 forced-adoption 3/3 closed" is partially correct but misses 2 orphaned declarations. Cleanup opportunity: remove dead deps from ResilienceKit and TestingKit.  
**Evidence:** `docs/governance/phenoshared-consumer-audit-DEEP-2026-04-26.md`  
**Tag:** `[governance]` — dependency tracking, Phase 1 partial closure

---
