# INTG-A4 – Config & Logging Toggle Matrix

**Status:** ✅ Documented
**Date:** 2025-10-14
**Owner:** Platform Integration Office
**Consumers:** Morph (`ConfigAdapter`, `LoggingAdapter`), Router configuration stack

---

## 1. Purpose

Capture required configuration and logging toggles that Pheno-SDK must expose to support Morph and Router migrations. This matrix informs updates to `pheno.config` schemas and `pheno.logging` bootstrap defaults.

---

## 2. Feature Toggle Inventory

| Toggle ID | Description | Default | Scope | Notes |
|-----------|-------------|---------|-------|-------|
| `pheno.morph.sandbox.enabled` | Enforce Morph sandbox policies when true | `true` | Morph | Maps to Morph SecurityAdapter behaviour; set false for Router. |
| `pheno.morph.sandbox.allow_symlinks` | Allow symlink traversal | `false` | Morph | Controlled via `ConfigAdapter`; requires SDK support for allow/deny lists. |
| `pheno.logging.format` | Structured logging format (`json`, `console`) | `json` | Morph/Router | Must preserve Morph schema (`timestamp`, `level`, `tool`, `message`). |
| `pheno.logging.level` | Global log level | `INFO` | Morph/Router | Allow override via env `PHENO_LOG_LEVEL`. |
| `pheno.logging.sinks` | Additional sinks (stdout, file, otel) | `["stdout"]` | Morph/Router | Router requires Prometheus-compatible metrics logs. |
| `pheno.embeddings.provider` | Embedding backend (`vertex`, `openai`, `local`) | `vertex` | Morph/Router | Morph uses local fallback; Router uses Vertex. |
| `pheno.analytics.radon.enabled` | Enable radon integration | `false` | Morph/Router | Allows staged rollout. |
| `pheno.analytics.grimp.enabled` | Enable grimp dependency graph | `false` | Morph/Router | Similar gating. |
| `pheno.security.secret_scan.strict_mode` | Fail on high severity secrets | `true` | Morph | Router may set to `warn`. |
| `pheno.cache.strategy` | Cache backend (`lru`, `redis`, `none`) | `lru` | Morph/Router | Connects to INTG-A5 LRU utilities. |
| `pheno.vector.search.provider` | Vector search engine (`vertex`, `pinecone`, `weaviate`) | `vertex` | Morph/Router | Morph uses `pheno.vector.search` in Phase 2. |
| `pheno.router.rate_limit.enabled` | Enable Router rate limiter | `true` | Router | Aligns with aiolimiter integration. |

---

## 3. Configuration Schema Changes

- Extend `pheno.config` with new `IntegrationSettings` dataclass containing Morph/Router specific toggles.
- Provide environment variable mapping for each toggle (e.g., `PHENO_MORPH_SANDBOX_ENABLED`).
- Add `.yaml`/`.env` template under `templates/integration/config`.

---

## 4. Logging Requirements

- Provide JSON formatter replicating Morph fields: `timestamp`, `level`, `tool`, `action`, `message`, `correlation_id`.
- Support Router-specific fields: `request_id`, `provider`, `cost_estimate`, `latency_ms`.
- Add optional OTLP exporter configuration for Router metrics.

---

## 5. Migration Path

1. SDK implements toggles with defaults matching current Morph behaviour.
2. Morph adopts SDK config by mapping existing environment variables; toggles ensure feature parity.
3. Router applies toggle overrides in config files, turning off Morph-specific sandbox features and enabling Router rate limiting.
4. Logging sinks verified by QA; sample outputs captured in migration guide appendices.

---

## 6. Deliverables

- [x] Toggle matrix and schema requirements (this document).
- [ ] SDK config/logging implementation (future sprint).
- [ ] Migration examples for Morph/Router (INTG-A6).
- [ ] QA validation scripts verifying log fields and config toggles.

Approved 2025-10-14.
