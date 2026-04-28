# Morph Migration to Pheno-SDK

**Status:** Draft (INTG-A6)
**Last Updated:** 2025-10-14
**Audience:** Morph Core Engineering, QA, Platform Enablement
**Related Plan:** `morph/INTEGRATION_MASTER_PLAN.md`

---

## 1. Overview

This guide documents the steps required for Morph to migrate from bespoke adapters to Pheno-SDK modules introduced via WBS-A. It is intended to accompany Phase 2 integration work and should be updated alongside code changes.

---

## 2. Prerequisites

- Pheno-SDK version `>=2.1.0` (includes analytics, security, caching enhancements).
- Feature flags toggled according to `INTG-A4_CONFIG_TOGGLE_MATRIX.md`.
- Integration tests green against Morph staging environment.

---

## 3. Migration Steps

### 3.1 Update Dependencies

1. Bump Morph `pyproject.toml` to Pheno-SDK `2.1.x`.
2. Enable optional extras:
   ```toml
   pheno-sdk[analytics-code,analytics-ast,security-scanners,vector]
   ```
3. Run `pip install -r requirements.txt` and verify no conflicts.

### 3.2 Configure Feature Flags

- Set in `.env` / deployment config:
  ```
  PHENO_MORPH_SANDBOX_ENABLED=true
  PHENO_ANALYTICS_RADON_ENABLED=true
  PHENO_ANALYTICS_GRIMP_ENABLED=true
  PHENO_SECURITY_SECRET_SCAN_STRICT_MODE=true
  PHENO_CACHE_STRATEGY=lru
  ```
- Adjust toggles per environment (see matrix appendix).

### 3.3 Replace Adapters

- Swap Morph `ConfigAdapter` usage with `pheno.config.integration.get_morph_settings()`.
- Replace logging setup with `pheno.logging.bootstrap.configure(...)`.
- Redirect secret scanning to `pheno.security.scanners.scan_paths`.
- Use `pheno.analytics.code.analyze_complexity` and `.analyze_dependencies`.
- Adopt `pheno.analytics.ast.get_adapter` for AST needs.
- Replace local caches with `pheno.utilities.cache.LruCache`.
- Wire semantic search to `pheno.vector.search.semantic_search`.

```python
from pathlib import Path

from pheno.analytics.code import analyze_complexity
from pheno.analytics.ast import get_adapter
from pheno.security.scanners import scan_paths
from pheno.utilities.cache import LruCache

cache = LruCache(namespace="morph-analytics", max_entries=512)
reports = await analyze_complexity(Path("morph_core"), cache=cache)

python_adapter = get_adapter("python", cache=cache)
ast_root = await python_adapter.parse(Path("morph_core/tools.py").read_text())

summary = await scan_paths([Path("morph_core")])
```

### 3.4 Validate

- Run Morph regression suite with feature flags enabled.
- Execute new SDK contract tests imported into Morph CI.
- Capture telemetry snapshots (logs, metrics) to confirm field parity.

---

## 4. Rollback Plan

- Maintain feature flags to disable SDK integrations.
- Keep legacy adapters behind `legacy_` namespace until Phase 3 cleanup.
- Document known issues and mitigations in `docs/migration/issues.md`.

---

## 5. Appendices

- **A. Toggle Matrix:** Reference `INTG-A4_CONFIG_TOGGLE_MATRIX.md`.
- **B. Benchmark Checklist:** Ensure performance delta ≤5%.
- **C. Contact:** Integration Office (#sdk-integration-warroom).

---

_Draft prepared 2025-10-14; update after each integration milestone._
