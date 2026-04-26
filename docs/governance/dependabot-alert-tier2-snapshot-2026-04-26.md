# TIER-2 Dependabot Alert Snapshot — 2026-04-26

**Scope:** All 21 TIER-2 repos (BytePort, Civis, Tracera, phenoData, phenoAI, phenoDesign, Tokn, GDK, KDesktopVirt, Stashly, Tasken, Metron, Conft, DevHex, phenoXdd, PhenoLang, PhenoVCS, PhenoRuntime, PhenoProc, PhenoPlugins, PhenoSpecs)

**Date:** 2026-04-26  
**Total Alerts:** 121 open across all repos  
**Repos with 0 Alerts:** 11  
**Repos with Alerts:** 10

---

## Summary by Severity (All Repos)

| Severity | Count | % of Total |
|----------|-------|-----------|
| **CRITICAL** | 5 | 4.1% |
| **HIGH** | 26 | 21.5% |
| **MODERATE** | 60 | 49.6% |
| **LOW** | 30 | 24.8% |

---

## Alert Distribution by Repo (Sorted by Total Descending)

| Repo | Total | CRITICAL | HIGH | MODERATE | LOW | Status |
|------|-------|----------|------|----------|-----|--------|
| **PhenoLang** | 37 | 2 | 8 | 19 | 8 | 🔴 CRITICAL |
| **Tracera** | 30 | 2 | 13 | 14 | 1 | 🔴 CRITICAL |
| **KDesktopVirt** | 24 | 1 | 3 | 12 | 8 | 🔴 CRITICAL |
| **BytePort** | 16 | 0 | 0 | 11 | 5 | 🟡 MODERATE |
| **PhenoRuntime** | 6 | 0 | 1 | 1 | 4 | 🟢 LOW |
| **DevHex** | 3 | 0 | 1 | 1 | 1 | 🟢 LOW |
| **phenoDesign** | 2 | 0 | 0 | 2 | 0 | 🟢 LOW |
| **Civis** | 2 | 0 | 0 | 0 | 2 | 🟢 LOW |
| **PhenoProc** | 1 | 0 | 0 | 0 | 1 | 🟢 LOW |
| **Tokn** | 0 | 0 | 0 | 0 | 0 | ✅ CLEAN |
| **Tasken** | 0 | 0 | 0 | 0 | 0 | ✅ CLEAN |
| **Stashly** | 0 | 0 | 0 | 0 | 0 | ✅ CLEAN |
| **phenoXdd** | 0 | 0 | 0 | 0 | 0 | ✅ CLEAN |
| **PhenoVCS** | 0 | 0 | 0 | 0 | 0 | ✅ CLEAN |
| **PhenoSpecs** | 0 | 0 | 0 | 0 | 0 | ✅ CLEAN |
| **PhenoPlugins** | 0 | 0 | 0 | 0 | 0 | ✅ CLEAN |
| **phenoData** | 0 | 0 | 0 | 0 | 0 | ✅ CLEAN |
| **phenoAI** | 0 | 0 | 0 | 0 | 0 | ✅ CLEAN |
| **Metron** | 0 | 0 | 0 | 0 | 0 | ✅ CLEAN |
| **GDK** | 0 | 0 | 0 | 0 | 0 | ✅ CLEAN |
| **Conft** | 0 | 0 | 0 | 0 | 0 | ✅ CLEAN |

---

## Top 3 Actionable (CRITICAL + HIGH Count)

### 1. **PhenoLang** — 37 total (2 CRITICAL, 8 HIGH)

**Risk:** Highest CRITICAL count; 10 security-blocking issues.  
**Action:** Prioritize dependency upgrade cycle; audit Rust/LLVM/compiler toolchain deps.  
**Next Step:** `gh api repos/KooshaPari/PhenoLang/dependabot/alerts` (or GraphQL full fetch) → identify blocked deps → plan cascade upgrades.

### 2. **Tracera** — 30 total (2 CRITICAL, 13 HIGH)

**Risk:** 15 high-severity vulnerabilities across polyglot stack.  
**Action:** Audit dependency manifests (package.json, Cargo.toml, etc.); prioritize CRITICAL.  
**Next Step:** Batch-fetch all alerts via GraphQL; categorize by ecosystem; identify lowest-friction upgrades.

### 3. **KDesktopVirt** — 24 total (1 CRITICAL, 3 HIGH)

**Risk:** 4 high-severity issues; likely infrastructure/system-level deps.  
**Action:** Review Dockerfile, systemd configs, kernel/VM toolchain versions.  
**Next Step:** Identify CRITICAL, verify exploitability in deployment context.

---

## Repos with 0 Alerts (11 CLEAN)

- Tokn
- Tasken
- Stashly
- phenoXdd
- PhenoVCS
- PhenoSpecs
- PhenoPlugins
- phenoData
- phenoAI
- Metron
- GDK
- Conft

These repos may have:
- No dependencies (pure logic, no external packages)
- Minimal dependencies with recent versions
- Archived or minimal-maintenance status
- Strong dependency upgrade discipline

---

## Recommendations

### Immediate (This Sprint)

1. **PhenoLang & Tracera:** Open issues in AgilePlus to prioritize CRITICAL vulnerabilities.
2. **KDesktopVirt:** Security review for deployment context (production-facing?).
3. **BytePort:** Evaluate MODERATE alerts; most should be patchable via dependency bump.

### Short-Term (2–4 Weeks)

1. Enable automated Dependabot PRs on all TIER-2 repos (if not already enabled).
2. Set branch protection rule: Dependabot PRs require passing CI + security checks.
3. Establish SLA: CRITICAL → fix within 48h; HIGH → within 1 week; MODERATE → backlog; LOW → quarterly.

### Long-Term

1. **Dependency Inventory:** Maintain `docs/reference/DEPENDENCY_INVENTORY.md` tracking top-level deps and their current versions.
2. **Supply Chain Audit:** Integrate `syft` SBOM + OSV-Scanner into CI pipeline.
3. **Cross-Repo Shared Deps:** Identify if PhenoLang, Tracera, and KDesktopVirt share common vulnerable deps; coordinate upgrades.

---

## Notes

- Repos with **0 alerts** are exceptions; investigate if Dependabot is disabled or if repos have no dependencies.
- **Private repos** (Civis, KDesktopVirt) have limited Dependabot API visibility in some GitHub orgs; verify Dependabot is enabled in org settings.
- **Archived repos** may show stale alerts; not included in this snapshot (none were archived).
- Snapshot taken via GraphQL API (`vulnerabilityAlerts(states: OPEN)` query); REST API Dependabot alerts endpoint returns 404 on many repos.

---

## Related

- [Previous TIER-1 + agentapi-plusplus audit](dependabot-alert-tier1-snapshot.md) — cross-reference for ecosystem-wide priority.
- [Billing-Blocked Rulesets](billing_blocked_rules.md) — 5 security rulesets dropped; Dependabot not directly affected.
- Governance: `docs/governance/supply_chain_security.md` (if exists)

