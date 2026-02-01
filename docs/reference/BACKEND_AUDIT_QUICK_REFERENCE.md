# Backend Audit - Quick Reference

## TL;DR

**Question**: Do we have 2x backends (Go + Python) that need to be reconciled?

**Answer**: **YES** - ~80% code duplication exists. Consolidation recommended.

---

## At a Glance

| Dimension | Go Backend | Python Backend | Gap |
|-----------|-----------|-----------------|-----|
| **Purpose** | Production HTTP API | CLI/TUI + secondary API | ✅ Clear |
| **Models** | 15 (sqlc) | 51 (SQLAlchemy) | ❌ DUPLICATE |
| **Services** | 27 | 95 | ❌ DUPLICATE |
| **Handlers** | 52 | 10 | ❌ DUPLICATE |
| **Real-time** | ✅ NATS+WebSocket | ❌ None | ⚠️ Gap |
| **Cache** | ✅ Redis | ❌ None | ⚠️ Gap |
| **Performance** | ~50ms p95 | ~200ms p95 | ❌ Slower |
| **Unique** | Neo4j, S3, Temporal | MCP, TUI, Chaos | ✅ Good |

---

## The Problem (In 30 Seconds)

```
Go Backend:
- 52 handlers handling all API requests
- 27 services with business logic
- 15 models for data access

Python Backend:
- Duplicates same 52 handlers (10+ in FastAPI)
- Duplicates same 27 services (95 total files)
- Duplicates same 15 models (51 total files)
- ALSO has CLI/TUI and MCP integration

Result:
→ Same data model defined in TWO places
→ Same business logic coded twice
→ Risk of inconsistency
→ Double maintenance burden
```

---

## Quick Architecture

### Current (Problematic)

```
Frontend
   ↓
   ├─→ Go Backend (primary) ← Recommended
   │
   └─→ Python API Server (redundant) ← Remove
        (duplicate endpoints, different auth)

Plus: Python CLI/TUI (good, keep it)
```

### Recommended (Clean)

```
Frontend
   ↓
   Go Backend (single API server)
   ↓
   Python CLI/TUI (thin HTTP client)
```

---

## 3-Phase Fix Plan

### Phase 1: Immediate (1-2 weeks)
- [ ] Deprecate Python API server
- [ ] Unified `.env` configuration
- [ ] Clear service boundaries
- **Effort**: 1-2 devs
- **Risk**: LOW

### Phase 2: Short-term (2-4 weeks)
- [ ] Migrate unique Python services to Go
- [ ] Move Python CLI to HTTP client pattern
- [ ] Auto-generate Python models from schema
- **Effort**: 2-3 devs
- **Risk**: MEDIUM

### Phase 3: Long-term (1-2 months)
- [ ] Unified data schema definition
- [ ] Shared sync framework
- [ ] Integrated testing
- **Effort**: 3-4 devs
- **Risk**: MEDIUM-HIGH

---

## Key Duplications to Fix

### 1. Data Models (CRITICAL)

**Go** defines models in sqlc:
```go
// database/models.go
type Item struct {
  ID, Title, Type, Status string
  ...
}
```

**Python** redefines in SQLAlchemy:
```python
# models/item.py
class Item(Base):
  id = Column(String)
  title = Column(String)
  type = Column(String)
  ...
```

**Fix**: Single OpenAPI/GraphQL schema → auto-generate both

### 2. Service Logic (HIGH)

**Go**:
```go
services.ItemService {
  Create(item)
  Update(item)
  Delete(itemID)
  GetByID(itemID)
  Search(query)
}
```

**Python**:
```python
class ItemService:
  def create(self, item)
  def update(self, item)
  def delete(self, item_id)
  def get_by_id(self, item_id)
  def search(self, query)
```

**Fix**: Move logic to Go, Python uses HTTP client

### 3. API Endpoints (MEDIUM)

**Go** (52 handlers):
```
POST /api/v1/items
POST /api/v1/links
POST /api/v1/projects
...
```

**Python** (10+ FastAPI routers):
```
Same endpoints, different implementation
```

**Fix**: Use Go backend only, Python calls it via HTTP

---

## What's Good (Don't Touch)

✅ **Python CLI/TUI** - Unique, keep it
✅ **MCP Integration** - Unique, keep it
✅ **Go real-time features** - Critical, optimize it
✅ **Async patterns** - Already mature

---

## Risks & Mitigations

| Risk | Fix |
|------|-----|
| **Data inconsistency** | Single schema source of truth |
| **Performance gap** | Go as primary API |
| **Lost features** | Keep Go's NATS + Redis |
| **Deployment complexity** | Gradual migration, parallel running |
| **Auth divergence** | Centralized JWT handling |

---

## Success Metrics

When done, verify:

```
✅ <5% code duplication
✅ Zero schema drift
✅ API latency consistent (<5% diff)
✅ Python CLI works offline + online
✅ No data inconsistencies
✅ <2 week deployment cycle
✅ <15 min rollback time
```

---

## Files to Review

- **Detailed Audit**: `/BACKEND_ARCHITECTURE_AUDIT.md`
- **Go Backend**: `/backend/internal/`
- **Python Backend**: `/src/tracertm/`
- **Configuration**: `/backend/.env`, `/pyproject.toml`

---

## Decision Matrix

| Decision | Impact | Timeline | Effort | Risk |
|----------|--------|----------|--------|------|
| **Deprecate Python API** | HIGH ↓ maintenance | NOW | 2 days | LOW |
| **Consolidate models** | CRITICAL | 2-4 weeks | 1 week | MEDIUM |
| **Consolidate services** | HIGH | 2-4 weeks | 1 week | MEDIUM |
| **Unified schema** | CRITICAL | 1-2 months | 2 weeks | HIGH |
| **Unified auth** | HIGH | 1-2 months | 1 week | MEDIUM |

---

**Bottom Line**: Fix high-impact items first (Phase 1), gain quick wins, then tackle deeper consolidation.
