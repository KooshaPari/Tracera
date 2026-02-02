# Coverage Improvement - Quick Start Guide

## 🎯 Goal: 70% → 95% Coverage

---

## 🔴 Critical Priority: API Layer

### Current State
- **API Overall**: 44.16% statements, 38.23% branches, 21.17% functions
- **endpoints.ts**: 17.39% coverage (483 uncovered lines!) ⚠️
- **19 API files**, only **1 test file** exists

### Immediate Action Items

#### Day 1: endpoints.ts (CRITICAL)
**File**: `src/api/endpoints.ts` (~570 lines)  
**Current**: 17.39% coverage  
**Target**: 95% coverage  
**Uncovered**: ~483 lines

**Test Cases Needed**:
1. ✅ Test all API object exports (projectsApi, itemsApi, linksApi, etc.)
2. ✅ Test all CRUD operations (list, get, create, update, delete)
3. ✅ Test compatibility aliases (runTask, getTask, cancelTask)
4. ✅ Test error handling paths
5. ✅ Test edge cases (null inputs, invalid IDs, etc.)

**Estimated**: 50-70 test cases  
**Impact**: +15-20% API coverage immediately

#### Day 2: client.ts
**File**: `src/api/client.ts`  
**Current**: 58.06% coverage  
**Target**: 95% coverage

**Test Cases Needed**:
1. ✅ Test apiClient initialization
2. ✅ Test error interceptors
3. ✅ Test request/response handling
4. ✅ Test network failure scenarios

**Estimated**: 15-20 test cases  
**Impact**: +10-15% API coverage

#### Day 3: websocket.ts
**File**: `src/api/websocket.ts`  
**Current**: 58.76% coverage  
**Target**: 95% coverage

**Test Cases Needed**:
1. ✅ Test WebSocket connection
2. ✅ Test reconnection logic
3. ✅ Test error scenarios
4. ✅ Test message handling

**Estimated**: 20-25 test cases  
**Impact**: +15-20% API coverage

---

## 📊 Week 1 Target

**Goal**: API coverage from 44% → 85%

**Plan**:
- Day 1: endpoints.ts (17% → 60%)
- Day 2: client.ts (58% → 85%)
- Day 3: websocket.ts (59% → 85%)
- Day 4: Remaining API files (events, graph, impact, items, links, projects, search, system)
- Day 5: Review and fix gaps

**Expected Result**: 
- API coverage: 44% → 85% (+41%)
- Overall coverage: 70% → 80% (+10%)

---

## 🚀 Getting Started

### Step 1: Create Test Infrastructure
```typescript
// src/__tests__/api/endpoints.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { projectsApi, itemsApi, linksApi, agentsApi, graphApi } from '@/api/endpoints'

describe('API Endpoints', () => {
  // Test structure
})
```

### Step 2: Test Error Paths First
- Highest ROI
- Most critical for production
- Relatively easy to test

### Step 3: Test Happy Paths
- Ensure all methods work
- Test with valid inputs
- Test response handling

### Step 4: Test Edge Cases
- Null/undefined inputs
- Invalid IDs
- Boundary conditions
- Empty responses

---

## 📈 Progress Tracking

### Week 1 Milestones
- [ ] Day 1: endpoints.ts tests written
- [ ] Day 2: client.ts tests written
- [ ] Day 3: websocket.ts tests written
- [ ] Day 4: All API files have tests
- [ ] Day 5: API coverage reaches 85%

### Coverage Targets
- **Week 1 End**: 80% overall (API: 85%)
- **Week 2 End**: 90% overall
- **Week 3 End**: 93% overall
- **Week 4 End**: 95% overall ✅

---

## 💡 Testing Tips

1. **Use MSW** for API mocking
2. **Test error paths** - they're often untested
3. **Test edge cases** - null, undefined, empty
4. **Focus on branches** - currently lowest at 64.89%
5. **Keep tests fast** - use mocks, avoid real network calls

---

## 🎯 Success Criteria

- All API methods have tests
- All error paths covered
- All edge cases handled
- Coverage report shows 95%+
- All tests pass
- Test suite runs in < 30s
