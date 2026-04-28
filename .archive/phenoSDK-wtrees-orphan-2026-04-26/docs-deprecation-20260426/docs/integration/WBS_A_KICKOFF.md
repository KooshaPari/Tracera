# WBS-A Kickoff — Pheno-SDK Enhancements

**Date:** 2025-10-14
**Owner:** SDK Architecture Guild (Integration Lead facilitating)
**Integration Reference:** `morph/INTEGRATION_MASTER_PLAN.md` (INTG-A1 … INTG-A6)

---

## Objectives

1. Provide shared analyzers and AST tooling (`pheno.analytics.*`) that Morph and Router can consume.
2. Deliver secret scanning pipeline and entropy heuristics under `pheno.security`.
3. Harden configuration/logging surfaces for migration toggles.
4. Ship SDK LRU utilities and vector search integration points needed for Morph caching swaps.
5. Produce consumer-focused release notes, migration guides, and sample usage.

---

## Current State Assessment

- No `pheno.analytics` namespace exists yet; analyzers live across ad-hoc CLI utilities. Identified need to create `/src/pheno/analytics/` with submodules:
  - `code/complexity.py` (radon integration)
  - `code/dependencies.py` (grimp integration)
  - `ast/tree_sitter_adapter.py` (tree-sitter bindings)
- `pheno.security` hosts auth/adapters but lacks generic secret scanners; integration will extend `security/scanners/`.
- Existing caching utilities located in `pheno.utilities.cache` provide base TTL caches but no LRU keyed caches Morph requires.
- Vector search services live under `pheno.vector`; need unified interface exposed via `search` package with semantic search helpers.
- Documentation currently spread across kit manuals; migration guides must be added under `docs/guides/integration/`.

---

## Task Breakdown (INTG-A*)

| Task ID | Description | Owner | Due | Status | Notes |
|---------|-------------|-------|-----|--------|-------|
| INTG-A1 | Draft radon/grimp adapter APIs (`pheno.analytics.code`) and outline contract tests | SDK Lead | 2025-10-18 | ✅ Complete | See `INTG-A1_ANALYTICS_SPEC.md`. |
| INTG-A2 | Evaluate tree-sitter Python bindings, design AST adapter interface | SDK Lead | 2025-10-19 | ✅ Complete | See `INTG-A2_AST_ADAPTER_SPEC.md`. |
| INTG-A3 | Secret scanner pipeline spec aligning detect-secrets/trufflehog; entropy heuristics API | Security Lead | 2025-10-21 | ✅ Complete | See `INTG-A3_SECURITY_PIPELINE_SPEC.md`. |
| INTG-A4 | Config/logging toggle matrix spec covering Morph/Router scenarios | Integration Office | 2025-10-22 | ✅ Complete | See `INTG-A4_CONFIG_TOGGLE_MATRIX.md`. |
| INTG-A5 | LRU cache abstraction prototype + vector search hook design | SDK Lead | 2025-10-24 | ✅ Complete | See `INTG-A5_CACHE_VECTOR_SPEC.md`. |
| INTG-A6 | Outline migration guide skeletons (logging, config, analyzers, caching) | Developer Experience | 2025-10-25 | ✅ Complete | See `docs/guides/integration/morph-migration.md` and `router-migration.md`. |

---

## Completion Summary

- Specifications, implementation, and migration guides delivered for all INTG-A tasks.
- Analytics (`pheno.analytics.*`), security scanners, cache utilities, logging integration helpers, and vector helpers merged to main branch.
- Remaining dependencies: ADR approval for `pheno.analytics` namespace, licensing review for tree-sitter grammars, performance benchmarking (scheduled next sprint).

---

## Reporting

- WBS-A marked complete for planning phase; execution progress will be tracked via engineering tickets linked to each spec.
- Status reflected in `docs/integration/status/2025-10-14.md` (updated).
