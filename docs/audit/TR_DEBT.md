# TracerTM Debt & Crash-Risk Audit

Audit date: 2026-06-14
Scope: Go, Python, TypeScript across `backend/`, `src/`, `frontend/`, `tests/`
Search patterns: `TODO`, `FIXME`, `panic(`, `[:N]` (unchecked slice)

---

## 1. Go — `panic(` occurrences

**Total: 35 occurrences across 21 files**

| Count | File |
|-------|------|
| 5 | `backend/tests/integration_setup_test.go` |
| 4 | `backend/internal/middleware/middleware_edge_cases_test.go` |
| 3 | `backend/internal/services/project_service_impl.go` |
| 2 | `backend/internal/agents/coordinator.go` |
| 2 | `backend/internal/services/codeindex_service_impl.go` |
| 2 | `backend/internal/services/graph_analysis_service_impl.go` |
| 2 | `backend/internal/services/item_service_impl.go` |
| 2 | `backend/internal/services/link_service_impl.go` |
| 1 | `backend/internal/cache/versioned.go` |
| 1 | `backend/internal/handlers/mock_db_test.go` |
| 1 | `backend/internal/handlers/routes_test.go` |
| 1 | `backend/internal/sentry/sentry.go` |
| 1 | `backend/internal/server/server_middleware_test.go` |
| 1 | `backend/internal/services/agent_service_impl.go` |
| 1 | `backend/internal/services/container.go` |
| 1 | `backend/internal/services/graph_analysis_service_common_test.go` |
| 1 | `backend/internal/services/snapshot_service.go` |
| 1 | `backend/internal/services/transaction_test.go` |
| 1 | `backend/internal/services/view_service_impl.go` |
| 1 | `backend/internal/validation/id_validator.go` |
| 1 | `backend/tests/integration_test.go` |

### Key file:line references
- `backend/tests/integration_setup_test.go:33`, `36`, `48`, `72`, `85` — `panic(err)` in test setup
- `backend/internal/middleware/middleware_edge_cases_test.go:282`, `307`, `336` — `panic("failed to sign token: " + err.Error())` in test helpers
- `backend/internal/middleware/middleware_edge_cases_test.go:716` — `panic("test panic")` in middleware recovery test
- `backend/internal/sentry/sentry.go:145` — `panic(err)` after Sentry capture
- `backend/internal/agents/coordinator.go:85`, `88` — `panic(fmt.Errorf(...))` in agent coordinator init
- `backend/internal/cache/versioned.go:120` — `panic("BumpVersion must be done by updating CacheVersion constant and redeploying")` (deployment guard)

---

## 2. Go — `[:N]` (slice) occurrences

**Total: 17 occurrences across 14 files**

### 2.1 Safe (guaranteed size or explicit `len()` guard)

| File | Line | Slice | Guard / Guarantee |
|------|------|-------|-------------------|
| `backend/internal/handlers/auth_handler_endpoints.go` | 103 | `authHeader[:7]` | `len(authHeader) > 7` |
| `backend/internal/handlers/auth_handler_endpoints.go` | 131 | `authHeader[:7]` | `len(authHeader) > 7` |
| `backend/internal/clients/ai_client.go` | 243 | `line[:6]` | `len(line) > 6` |
| `backend/internal/metrics/middleware.go` | 67 | `path[:8]` | `len(path) >= 8` |
| `backend/internal/models/schema_validation_test.go` | 884 | `parts[i][:1]` | `len(parts[i]) > 0` |
| `backend/internal/middleware/cache.go` | 312 | `hex.EncodeToString(hash[:])[:16]` | SHA-256 hex is always 64 chars |
| `backend/internal/graph/cache.go` | 45 | `hash[:8]` | `sha256.Sum256` is always 32 bytes |
| `backend/internal/clients/spec_analytics_client.go` | 359 | `h.Sum(nil)[:16]` | SHA-256 sum is always 32 bytes |
| `backend/internal/clients/python_client.go` | 212 | `hasher.Sum(nil)[:16]` | SHA-256 sum is always 32 bytes |
| `backend/internal/pagination/cursor_test.go` | 75 | `EncodeCursor(... )[:10]` | Base64 of `"invalid:1234567890"` is always > 10 chars |
| `backend/tests/integration/comprehensive_scenarios_integration_test.go` | 122 | `agentID[:8]` | `uuid.New().String()` is always 36 chars |
| `backend/tests/e2e/service_layer_project_e2e_test.go` | 158 | `featureID[:8]` | `createItem` returns a UUID (36 chars) |
| `backend/tests/e2e/service_layer_agent_e2e_test.go` | 134 | `itemIDs[:2]` | `itemIDs` is initialized with exactly 3 elements |
| `backend/internal/services/edge_cases_integration_test.go` | 128 | `longTitle[:255]` | `longTitle` is built to 275 chars (25×11) |
| `backend/internal/services/edge_cases_integration_test.go` | 334 | `longName[:255]` | `longName` is built to 260 chars (26×10) |
| `backend/internal/services/edge_cases_integration_test.go` | 467 | `longName[:255]` | `longName` is built to 260 chars (26×10) |

### 2.2 CRASH BUG — Unchecked slice without adequate `len()` guard

| File | Line | Code | Guard | Issue |
|------|------|------|-------|-------|
| `backend/internal/docindex/extractor_test.go` | 464 | `path[:8] == "https://"` | `len(path) > 4` | **Guard `len(path) > 4` is insufficient for `path[:8]`**. If `path` is 5–7 characters long, the slice `path[:8]` will panic with a runtime out-of-bounds error. |

**Additional context:**
```go
// backend/internal/docindex/extractor_test.go:463-464
func isExternalURL(path string) bool {
    return len(path) > 4 && (path[:7] == "http://" || path[:8] == "https://")
}
```
The guard should be `len(path) >= 8` (or split into two separate checks: `len(path) > 7 && path[:7] == "http://"` and `len(path) > 8 && path[:8] == "https://"`).

---

## 3. Python — `TODO` / `FIXME` occurrences

**Total: 8 occurrences across 6 files**

| Count | File |
|-------|------|
| 2 | `tests/unit/services/test_requirement_miner.py` |
| 2 | `src/tracertm/services/requirement_miner.py` |
| 1 | `tests/integration/tui/test_tui_execution_coverage.py` |
| 1 | `tests/integration/services/test_status_workflow_service_comprehensive.py` |
| 1 | `src/tracertm/services/item_spec_service.py` |
| 1 | `src/tracertm/models/item_spec.py` |

### Key file:line references
- `src/tracertm/services/requirement_miner.py:20` — docstring describing TODO/spec markers
- `src/tracertm/services/requirement_miner.py:69` — regex pattern for TODO/FIXME
- `tests/unit/services/test_requirement_miner.py:214-215` — test case for TODO marker extraction
- `tests/integration/tui/test_tui_execution_coverage.py:632` — `"currently a TODO"` comment
- `tests/integration/services/test_status_workflow_service_comprehensive.py:505` — `"TODO → in_progress"` comment
- `src/tracertm/services/item_spec_service.py:213` — `"no TBD/TODO markers"` comment
- `src/tracertm/models/item_spec.py:858` — `default="todo"` status column comment

---

## 4. Python — `[:N]` slice occurrences

**Total: 108 occurrences across 56+ files**

Python slicing is bounds-safe (returns empty or truncated rather than panicking), so these are **not crash risks**.

### Top 10 files by occurrence count

| Count | File |
|-------|------|
| 10 | `src/tracertm/mcp/resources/tracertm.py` |
| 9 | `src/tracertm/mcp/tools/streaming.py` |
| 8 | `src/tracertm/mcp/tools/response_optimizer.py` |
| 4 | `src/tracertm/services/bulk_operation_service.py` |
| 4 | `src/tracertm/repositories/specification_repository.py` |
| 3 | `src/tracertm/api/routers/errors.py` |
| 3 | `src/tracertm/api/routers/qa_metrics.py` |
| 3 | `src/tracertm/api/middleware/logging.py` |
| 3 | `src/tracertm/services/recording/playwright_service.py` |
| 3 | `src/tracertm/services/recording/vhs_service.py` |

### Representative file:line references
- `src/tracertm/mcp/tools/streaming.py:141` — `item_id_str[:8]`
- `src/tracertm/mcp/tools/streaming.py:161` — `str(item.id)[:8]`
- `src/tracertm/mcp/tools/response_optimizer.py:218` — `str(item.id)[:8]`
- `src/tracertm/clients/go_client.py:287` — `h.hexdigest()[:32]`
- `src/tracertm/api/sync_client.py:289` — `hashlib.sha256(data.encode()).hexdigest()[:16]`
- `src/tracertm/database/ensure_problems_processes.py:199` — `stmt[:60]`

---

## 5. TypeScript / TSX — `TODO` / `FIXME` occurrences

**Total: 0 occurrences in project source code (excluding `node_modules/` and `storybook-static/` build artifacts)**

The `frontend/` codebase contains no `TODO` or `FIXME` comments in authored `.ts` or `.tsx` files.

---

## 6. Summary

| Category | Count | Crash Risk |
|----------|-------|------------|
| Go `panic(` | 35 | Low (mostly test files / constructor guards) |
| Go `[:N]` unchecked | **1** | **Yes** — `backend/internal/docindex/extractor_test.go:464` |
| Python `TODO`/`FIXME` | 8 | None |
| Python `[:N]` | 108 | None (Python slicing is safe) |
| TS/TSX `TODO`/`FIXME` | 0 | None |

**Immediate action:** Fix the `len(path) > 4` guard in `backend/internal/docindex/extractor_test.go:464` to `len(path) >= 8` (or split the protocol checks) to prevent a runtime panic on short path strings.
