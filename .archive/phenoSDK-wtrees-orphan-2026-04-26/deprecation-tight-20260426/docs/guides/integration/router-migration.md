# Router Migration to Pheno-SDK

**Status:** Draft (INTG-A6)
**Last Updated:** 2025-10-14
**Audience:** Router Core Engineering, ML/Analytics Team
**Related Plan:** `morph/INTEGRATION_MASTER_PLAN.md`

---

## 1. Overview

This document outlines how Router replaces its bespoke logging, configuration, routing analytics, and caching infrastructure with Pheno-SDK modules delivered by WBS-A. Use alongside Router Phase 2 integration tasks.

---

## 2. Prerequisites

- Pheno-SDK `>=2.1.0` with extras: `analytics-code`, `analytics-ast`, `security-scanners`, `vector`.
- Router regression benchmarks collected pre-migration (latency, cost, accuracy).
- Rate limiting requirements documented per provider.

---

## 3. Migration Checklist

### 3.1 Dependency Updates

```toml
pheno-sdk[analytics-code,analytics-ast,security-scanners,vector,router]
litellm>=1.39.0
aiolimiter>=1.1.0
scikit-learn>=1.5.2
xgboost>=2.1.0
```

### 3.2 Configuration

Set environment toggles:

```
PHENO_MORPH_SANDBOX_ENABLED=false
PHENO_LOGGING_FORMAT=json
PHENO_LOGGING_SINKS=["stdout","otel"]
PHENO_ANALYTICS_RADON_ENABLED=true
PHENO_ANALYTICS_GRIMP_ENABLED=true
PHENO_CACHE_STRATEGY=lru
PHENO_ROUTER_RATE_LIMIT_ENABLED=true
PHENO_VECTOR_SEARCH_PROVIDER=vertex
```

### 3.3 Adapter Swap Steps

1. Replace Router logging with `pheno.logging.bootstrap.configure` using Router schema overrides.
2. Use `pheno.config.integration.get_router_settings()` for environment parsing.
3. Integrate routing analytics via `pheno.analytics.code`/`ast` outputs feeding new `pheno.routing.learning` (Phase 3 dependency).
4. Replace SQLite metrics with `pheno.observability` exporters (Prometheus, OTLP).
5. Swap caching logic for `pheno.utilities.cache.LruCache` or Redis wrapper depending on deployment.
6. Leverage `pheno.vector.search.semantic_search` for embedding comparisons.

```python
from pheno.utilities.cache import LruCache
from pheno.vector.search import SemanticSearch, semantic_search

# Assume `search` is a configured SemanticSearch instance bound to Router providers
search_cache = LruCache(namespace="router-vector", max_entries=2048)
results = await semantic_search(
    "streamlined batch inference",
    search=search,
    top_k=5,
    cache=search_cache,
)
```

### 3.4 Verification

- Run load tests vs baseline; ensure latency delta within ±7%.
- Validate rate limiter behaviour with `aiolimiter` integration.
- Confirm cost tracking metrics align with legacy implementation.

---

## 4. Rollback

- Maintain legacy providers/metrics code behind feature flag `ROUTER_LEGACY_STACK=true`.
- Keep sqlite metrics pipeline for at least one sprint post-rollout.
- Document issues in `docs/migration/router-issues.md`.

---

## 5. Support

- Integration Office (#sdk-integration-warroom)
- SDK Architecture Guild for analyzer or cache questions
- Security WG for secret scanning adjustments

---

_Draft prepared 2025-10-14; update per sprint deliverables._
