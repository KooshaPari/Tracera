# Deployment Fix Action Plan

**Date:** 2026-02-01
**Status:** 🔴 CRITICAL - Deployment Blocked
**Priority:** P0
**Estimated Time:** 16-23 hours (2-3 days)

---

## Overview

This document provides a systematic action plan to fix all deployment-blocking issues identified in Phase 3 validation.

**Current Status:** 52% deployment ready (threshold: 89%)
**Target:** 100% deployment ready

---

## Critical Path (Sequential Tasks)

### Phase 1: Backend Stabilization (4-5 hours)

#### Task 1.1: Fix Syntax Errors (30 minutes)
**Priority:** P0
**Blocker:** Backend tests

```bash
# Fix env_test.go comparison operator
# File: backend/internal/env/env_test.go:23
# Change: if x = y  →  if x == y
```

**Action:**
```bash
cd backend/internal/env
# Edit env_test.go line 23
# Before: if value = "expected"
# After:  if value == "expected"
```

#### Task 1.2: Fix Autoupdate Tests (1 hour)
**Priority:** P0
**Blocker:** Backend tests

**Errors to Fix:**
1. `fmt.Fprint` returns 2 values (n int, err error)
2. `server.Close()` returns void, cannot be assigned

```go
// Fix 1: Handle fmt.Fprint return values
// Before:
err := fmt.Fprint(w, "content")

// After:
_, err := fmt.Fprint(w, "content")

// Fix 2: Call server.Close() without assignment
// Before:
err := server.Close()

// After:
server.Close()
```

**Files:**
- `backend/internal/autoupdate/autoupdate_test.go:138, 141, 177, 211, 214, 236, 255, 258, 302, 305`

#### Task 1.3: Update Config Tests (30 minutes)
**Priority:** P0
**Blocker:** Backend tests

**Remove Supabase references** (migrated to WorkOS):
```go
// Remove these test assertions:
cfg.SupabaseServiceRoleKey
cfg.SupabaseURL
```

**Files:**
- `backend/internal/config/config_test.go:148`
- `backend/internal/config/loader_test.go:210, 242, 501, 502`

#### Task 1.4: Fix Auth Mock Types (1 hour)
**Priority:** P0
**Blocker:** Backend tests

**Problem:** Cannot use `pgxmock.PgxPoolIface` as `*gorm.DB`

**Solution:** Update test setup to use proper GORM mocks
```go
// Use github.com/DATA-DOG/go-sqlmock with GORM
import (
    "github.com/DATA-DOG/go-sqlmock"
    "gorm.io/driver/postgres"
    "gorm.io/gorm"
)

// Create mock DB
sqlDB, mock, err := sqlmock.New()
gormDB, err := gorm.Open(postgres.New(postgres.Config{
    Conn: sqlDB,
}), &gorm.Config{})
```

**Files:**
- `backend/internal/auth/authkit_adapter_test.go` (10 test functions)

#### Task 1.5: Fix Cache Test Precision (30 minutes)
**Priority:** P1
**Blocker:** Soft

**Problem:** Floating point comparison fails
```
expected: 0.3
actual:   0.30000000000000004
```

**Solution:** Use epsilon comparison
```go
// Use math package or testify's InDelta
import "github.com/stretchr/testify/assert"

// Before:
assert.Equal(t, 0.3, missRate)

// After:
assert.InDelta(t, 0.3, missRate, 0.0001)
```

**Files:**
- `backend/internal/cache/metrics_test.go:30, 205`
- `backend/internal/cache/redis_cache_test.go:273`

#### Task 1.6: Fix Middleware Rate Limiter (30 minutes)
**Priority:** P0
**Blocker:** Backend tests

**Problem:** Type conversion `RateLimitConfig` to `RateLimitMiddleware`

**Solution:** Create middleware instance properly
```go
// Before:
middleware := RateLimitConfig{...}

// After:
config := RateLimitConfig{...}
middleware := NewRateLimitMiddleware(config)
```

**Files:**
- `backend/internal/middleware/auth_adapter_test.go:437, 474, 716`

#### Task 1.7: Fix Database Schema Tests (2 hours)
**Priority:** P0
**Blocker:** Backend tests

**Actions:**
1. Run pending migrations
2. Verify schema consistency
3. Update test expectations

```bash
# Run migrations
cd backend
go run cmd/migrate/main.go up

# Verify schema
psql $DATABASE_URL -c "\dt"  # List tables
psql $DATABASE_URL -c "\d views"  # Check views table
psql $DATABASE_URL -c "\d profiles"  # Check profiles table
```

**Files:**
- `backend/internal/models/*_test.go` (13 failing tests)

**Failing Tests:**
- ViewTableExists
- ProfileTableExists
- ProfileModelMatchesSchema
- CodeEntityTableExists
- PrimaryKeyConstraints
- ForeignKeyConstraints
- IndexesExist
- NoOrphanedColumns
- UUIDTypeConsistency
- JSONBTypeConsistency
- TimestampTypeConsistency
- NotNullConstraints
- UniqueConstraints

---

### Phase 2: Frontend Stabilization (4-6 hours)

#### Task 2.1: Create Error/Logger Utilities (30 minutes)
**Priority:** P0
**Blocker:** Frontend build

**Create utility file:**
```typescript
// frontend/apps/web/src/lib/error-logger.ts
export function error(...args: any[]): void {
  console.error(...args);
}

export const logger = {
  error(...args: any[]): void {
    console.error(...args);
  },
  warn(...args: any[]): void {
    console.warn(...args);
  },
  info(...args: any[]): void {
    console.info(...args);
  },
  debug(...args: any[]): void {
    console.debug(...args);
  },
};
```

#### Task 2.2: Import Utilities in Workers (1 hour)
**Priority:** P0
**Blocker:** Frontend build

**Add to all worker files:**
```typescript
import { error, logger } from '../lib/error-logger';
```

**Files:**
- `frontend/apps/web/src/workers/export-import.worker.ts`
- `frontend/apps/web/src/workers/graph-layout.worker.ts`
- `frontend/apps/web/src/workers/graphLayout.worker.ts`
- `frontend/apps/web/src/workers/search-index.worker.ts`
- `frontend/apps/web/src/api/auth.ts`
- `frontend/apps/web/src/components/auth/AuthKitSync.tsx`
- And 40+ other files with `error` or `logger` usage

#### Task 2.3: Fix Null Safety in search-index.worker (2 hours)
**Priority:** P0
**Blocker:** Frontend build

**Add null checks:**
```typescript
// Before:
update.field

// After:
update?.field

// Or with guard:
if (!update) {
  logger.warn('Update is undefined');
  return;
}
update.field
```

**28 errors to fix** in `search-index.worker.ts`

#### Task 2.4: Fix export-import.worker Type Guards (1 hour)
**Priority:** P0
**Blocker:** Frontend build

**Add type guards for optional objects:**
```typescript
// Before:
Object.keys(metadata)

// After:
Object.keys(metadata || {})

// Or:
if (!metadata) return [];
Object.keys(metadata)
```

**8 errors to fix** in `export-import.worker.ts`

#### Task 2.5: Fix WorkerPool Type Conversion (30 minutes)
**Priority:** P0
**Blocker:** Frontend build

**Fix timeout type:**
```typescript
// Before:
const timeoutId: number = setTimeout(...)

// After (Node.js environment):
const timeoutId: NodeJS.Timeout = setTimeout(...)

// Or (browser environment):
const timeoutId: number = setTimeout(...) as any as number
```

**Files:**
- `frontend/apps/web/src/workers/WorkerPool.ts:328`

#### Task 2.6: Fix EventSourcePolyfill Import (15 minutes)
**Priority:** P0
**Blocker:** Frontend build

**Update import:**
```typescript
// Before:
import { EventSourcePolyfill } from 'event-source-polyfill';

// After:
import EventSourcePolyfill from 'event-source-polyfill';
// Or:
const EventSourcePolyfill = require('event-source-polyfill').EventSourcePolyfill;
```

**Files:**
- `frontend/apps/web/src/api/mcp-client.ts:11`

#### Task 2.7: Fix Remaining Type Errors (2-3 hours)
**Priority:** P0
**Blocker:** Frontend build

**Systematic approach:**
1. Run typecheck and save output
2. Group errors by file
3. Fix file by file, starting with most errors
4. Re-run typecheck after each file
5. Repeat until 0 errors

```bash
cd frontend/apps/web
bun run typecheck 2>&1 | tee typecheck-errors.txt
# Fix errors
bun run typecheck 2>&1 | wc -l  # Track progress
```

**Estimated breakdown:**
- Auth components: 50 errors (30 min)
- API client: 100 errors (45 min)
- Workers: 200 errors (1 hour)
- Components: 500 errors (1.5 hours)
- Remaining: 1,880 errors (systematic fixes)

---

### Phase 3: Validation (2-3 hours)

#### Task 3.1: Backend Test Suite (30 minutes)
```bash
cd backend
go test ./... -v | tee test-results.txt
# Verify: 46/46 packages pass
```

#### Task 3.2: Frontend Build (15 minutes)
```bash
cd frontend/apps/web
bun run build
# Verify: 0 TypeScript errors
# Verify: dist/ directory created
```

#### Task 3.3: Frontend Test Suite (45 minutes)
```bash
cd frontend/apps/web
bun test
# Verify: All tests pass
```

#### Task 3.4: Smoke Load Test (30 minutes)
```bash
cd tests/load/k6
k6 run scenarios/smoke-test.js
# Verify: P95 < 500ms, error rate < 0.1%
```

#### Task 3.5: Monitoring Dashboard Check (15 minutes)
```bash
# Access Grafana
open http://localhost:3001

# Verify dashboards:
# - System Overview
# - Application Metrics
# - Business Metrics
```

#### Task 3.6: Chaos Scenario Test (30 minutes)
```bash
cd tests/chaos
docker-compose -f docker-compose.chaos.yml up -d
pytest test_network_latency.py -v
pytest test_connection_failures.py -v
# Verify: Resilience patterns working
```

---

## Parallel Tasks (Can Run Concurrently)

### Task P1: Security Audit (4-8 hours)
**Priority:** P1
**Blocker:** Soft

```bash
# Run automated scans
cd backend
go run golang.org/x/vuln/cmd/govulncheck@latest ./...

cd frontend/apps/web
bun audit

# Run security tests
cd backend
go test ./tests/security/... -v

cd frontend/apps/web
bun test src/__tests__/security/
```

**Deliverable:** Security audit report documenting findings

---

## Verification Checklist

### Critical (Must Pass)
- [ ] Backend builds without errors
- [ ] All 46 backend test packages pass
- [ ] Frontend builds without TypeScript errors
- [ ] All frontend tests pass
- [ ] Database schema validated (13 tests pass)
- [ ] Authentication tests pass
- [ ] Cache tests pass
- [ ] Smoke load test passes
- [ ] Monitoring dashboards operational
- [ ] Chaos tests pass

### Important (Should Pass)
- [ ] Security audit complete
- [ ] Security tests pass (backend + frontend)
- [ ] Load test baseline established
- [ ] Runbooks reviewed
- [ ] Environment configuration verified

### Optional (Nice to Have)
- [ ] Bundle analysis run
- [ ] Performance profiling complete
- [ ] Canary deployment tested
- [ ] Documentation updated

---

## Timeline Estimate

### Optimistic (16 hours)
- Day 1 (8 hours): Phase 1 (Backend) + Phase 2 Start
- Day 2 (8 hours): Phase 2 (Frontend) + Phase 3 (Validation)

### Realistic (20 hours)
- Day 1 (8 hours): Phase 1 (Backend) + 50% Phase 2
- Day 2 (8 hours): 50% Phase 2 (Frontend) + Phase 3
- Day 3 (4 hours): Buffer + Final validation

### Conservative (23 hours)
- Day 1 (8 hours): Phase 1 (Backend)
- Day 2 (8 hours): Phase 2 (Frontend)
- Day 3 (7 hours): Phase 3 (Validation) + Security Audit

---

## Risk Mitigation

### High Priority Risks
1. **Backend schema issues persist**
   - Mitigation: Allocate extra time for database debugging
   - Fallback: Restore from backup, re-run all migrations
2. **Frontend type errors multiply**
   - Mitigation: Fix systematically by file
   - Fallback: Disable strict type checking temporarily (NOT RECOMMENDED)
3. **New test failures discovered**
   - Mitigation: Fix immediately, don't defer
   - Fallback: Document as known issues, fix post-launch

### Medium Priority Risks
4. **Security audit reveals critical issues**
   - Mitigation: Fix before deployment
   - Fallback: Document and monitor, fix in hotfix
5. **Load tests fail under stress**
   - Mitigation: Tune performance, optimize queries
   - Fallback: Reduce traffic limits, scale horizontally

---

## Success Criteria

### Phase Complete When:
1. ✅ All backend tests pass (46/46)
2. ✅ Frontend builds with 0 TypeScript errors
3. ✅ All frontend tests pass
4. ✅ Database schema validated
5. ✅ Smoke load test passes
6. ✅ Monitoring confirms system health
7. ✅ Chaos tests confirm resilience
8. ✅ Security audit scheduled/complete

### Deployment Ready When:
- **Deployment Readiness Score ≥ 89%** (currently 52%)
- **All P0 blockers resolved**
- **Staging deployment successful**

---

## Post-Fix Deployment Plan

### Staging Deployment
1. Deploy to staging environment
2. Run full test suite
3. Execute load tests
4. Monitor for 24 hours
5. Get stakeholder approval

### Production Deployment
1. Blue-green deployment to production
2. 10% canary traffic
3. Monitor for 1 hour
4. 50% traffic
5. Monitor for 2 hours
6. 100% traffic
7. Monitor for 24 hours

---

## Resources Required

### Personnel
- 1 Backend Engineer (full-time, 2-3 days)
- 1 Frontend Engineer (full-time, 2-3 days)
- 1 DevOps Engineer (part-time, validation support)
- 1 QA Engineer (part-time, test execution)

### Tools
- Go test runner
- Bun/TypeScript compiler
- k6 load testing tool
- Docker/Kubernetes cluster
- Monitoring stack (Grafana, Prometheus)

### Environment
- Development environment
- Staging environment (for validation)
- Load testing infrastructure

---

## Contact & Escalation

### Primary Contact
- **Project Lead:** [Name]
- **Status Updates:** Every 4 hours

### Escalation Path
1. Blocker encountered → Alert project lead immediately
2. Timeline slips > 4 hours → Alert stakeholders
3. Critical issue discovered → Emergency meeting

---

**Action Plan Created:** 2026-02-01
**Priority:** P0 - CRITICAL
**Status:** 🔴 READY TO EXECUTE
**Estimated Completion:** 2-3 days
