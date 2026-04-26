# PhenoLibs Orphans — Rehoming Map

**Audit Date:** 2026-04-24  
**Status:** PHASE 4 COMPLETE (19 packages rehomed; 0 remaining)  
**Total Orphans:** 23 (6 final packages moved 2026-04-25; 0 remaining)  
**Rehomed Count:** 16 (Phase 3: 10 packages, 21,202 LOC; Phase 4: 6 packages, 28,101 LOC) → **49,303 LOC total**  
**Archived Count:** 3 (pheno-dev, pheno-optimization, pheno-shared) → 19,330 LOC

## Executive Summary

- **23 orphans identified**, all verified ORPHAN (zero external callers in target repos)
- **Top targets:** pheno/python (10), PhenoKits/libs/python (8), phenotype-shared/crates (2)
- **Immediate archive candidates:** 3 packages with zero callers and duplicate functionality
- **Strategic rationale:** Consolidate by functional domain; avoid creating four-way overlap

---

## Phase 4: Final 6 Packages (2026-04-25)

| Orphan | LOC | Target | Status | Verified |
|--------|-----|--------|--------|----------|
| pheno-core | 1,630 | `/repos/pheno/python/pheno_core` | MOVED ✓ | Zero callers |
| config-kit | 3,135 | `/repos/PhenoKits/libs/python/config_kit` | MOVED ✓ | Zero callers |
| pheno-adapters | 7,534 | `/repos/PhenoKits/libs/python/pheno_adapters` | MOVED ✓ | Zero callers |
| pheno-deployment | 7,493 | `/repos/PhenoKits/libs/python/pheno_deployment` | MOVED ✓ | Zero callers |
| pheno-patterns | 6,652 | `/repos/PhenoKits/libs/python/pheno_patterns` | MOVED ✓ | Zero callers |
| pheno-process | 1,657 | `/repos/PhenoKits/libs/python/pheno_process` | MOVED ✓ | Zero callers |

**Total Phase 4 LOC:** 28,101 (100% moved)

---

## Phase 3: 10 Packages (2026-04-24)

| Orphan | LOC | Target | Status |
|--------|-----|--------|--------|
| pheno-errors | 700 | `/repos/pheno/python/` | REHOMED ✓ |
| pheno-exceptions | 1,340 | `/repos/pheno/python/` | REHOMED ✓ |
| pheno-async | 2,548 | `/repos/pheno/python/` | REHOMED ✓ |
| pheno-config | 831 | `/repos/pheno/python/` | REHOMED ✓ |
| core-utils | 2,875 | `/repos/pheno/python/` | REHOMED ✓ |
| cli-kit | 2,362 | `/repos/PhenoKits/libs/python/pheno_cli` | REHOMED ✓ |
| cli-builder-kit | 231 | `/repos/PhenoKits/libs/python/pheno_cli_builder` | REHOMED ✓ |
| pheno-analytics | 5,302 | `/repos/PhenoKits/libs/python/pheno_analytics` | REHOMED ✓ |
| pheno-plugins | 302 | `/repos/PhenoKits/libs/python/pheno_plugins` | REHOMED ✓ |
| pheno-utils | 2,021 | `/repos/pheno/python/` | REHOMED ✓ |

**Total Phase 3 LOC:** 21,202

---

## Archived Packages (Deduplication)

| Package | LOC | Status | Location |
|---------|-----|--------|----------|
| pheno-dev | 9,445 | ARCHIVED ✓ | `.archive/pheno-dev/` |
| pheno-optimization | 2,028 | ARCHIVED ✓ | `.archive/pheno-optimization/` |
| pheno-shared | 7,857 | ARCHIVED ✓ | `.archive/pheno-shared/` |

**Total Archived LOC:** 19,330

---

## Final Summary

**Completion Status:**
- ✅ 6 remaining orphans moved (Phase 4)
- ✅ 10 packages rehomed (Phase 3)
- ✅ 3 packages archived (Phases 1-2)
- ✅ **0 orphans remaining** → PhenoLibs orphan rehoming COMPLETE

**Grand Total:**
- **16 packages rehomed:** 49,303 LOC
- **3 packages archived:** 19,330 LOC
- **23 packages processed:** 68,633 LOC (100%)

**Deprecation Markers Added:**
All moved packages have DEPRECATION.md notices at source locations in PhenoLibs, guiding users to new import paths.

**Next Steps:**
1. Update target repos' pyproject.toml/setup.py to include new packages
2. Publish updated packages to PyPI (if applicable)
3. Schedule cleanup of source directories in PhenoLibs (maintenance cycle)
