# Stashly-Migrations Adoption Survey — 2026-04-25

## Current Adoption Status

| Repository | Status | Approach | LOC | Notes |
|------------|--------|----------|-----|-------|
| **phenotype-shared** | ADOPTED | `stashly-migrations` | — | Only adopter from W-71 (confirmed active) |
| **AgilePlus** | HAND-ROLLED | In-house `MigrationRunner` | ~600 | Embedded SQL, version-tracked in `_migrations` meta table |
| **FocalPoint** | HAND-ROLLED | In-house `migrations.rs` | ~200+ | Ordered `(u32, &str)` tuples, rusqlite adapter, audit-append pattern |
| **heliosCLI** | SQLX-MIGRATE | sqlx `migrate!("./migrations")` | — | External migration files; separate from stashly ecosystem |

## Adoption Count: 1 (unchanged since W-71)

**No new adopters identified.** AgilePlus, FocalPoint, and heliosCLI each maintain isolated migration systems.

## High-Value Adoption Candidates

### 1. FocalPoint (Priority: HIGH)
- **Current:** Hand-rolled migrations with audit-append semantics
- **Match:** stashly's version tracking + embedded SQL would fit naturally
- **Benefit:** Consolidate auditable schema changes; reuse phenotype-shared patterns
- **Effort:** Moderate (audit-append integration required)

### 2. AgilePlus (Priority: MEDIUM)
- **Current:** In-house `MigrationRunner` with custom version tracking
- **Match:** stashly's migration composition would reduce ~600 LOC
- **Blocker:** Requires API compatibility layer for existing `(version, sql)` tuples
- **Effort:** High (established migration patterns; risky refactor)

### 3. heliosCLI (Priority: LOW)
- **Current:** sqlx's external file-based `migrate!("./migrations")`
- **Match:** stashly is embedded-SQL focused; sqlx workflow is orthogonal
- **Blocker:** Architecture mismatch (external files vs. inline definitions)
- **Effort:** Very high (rearchitect state/migration boundary)

## Recommendation

**Pilot FocalPoint adoption** in next cycle. Low risk, high demonstrative value for observably-driven patterns. Success would unlock AgilePlus evaluation.

---

**Audit Date:** 2026-04-25  
**Surveyor:** Agent  
**Next Review:** 2026-05-25 (or post-W-72 FocalPoint completion)
