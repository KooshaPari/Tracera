# Test Coverage Improvement Plan

## Goal: Increase from 70% to 95% coverage

---

## Current State

- **Statements**: 70.4% (need +24.6%)
- **Branches**: 64.89% (need +30.11%)
- **Functions**: 67.02% (need +27.98%)
- **Lines**: 70.41% (need +24.59%)

**Gap**: ~25-30% increase needed across all metrics

---

## Phase 1: API Layer (Highest Priority) 🔴

**Current**: 44.16% statements, 38.23% branches, 21.17% functions  
**Target**: 95%  
**Impact**: High (foundation layer)  
**Gap**: ~50% statements, ~57% branches, ~74% functions

### Critical Findings

- **endpoints.ts**: Only 17.39% coverage (483 uncovered lines!)
- **websocket.ts**: 58.76% coverage (needs improvement)
- **client.ts**: 58.06% coverage (error paths missing)
- **Only 1 test file** exists for 19 API files

### Files to Cover

1. **`src/api/endpoints.ts`** (Core API client)
   - [ ] Test all API method wrappers
   - [ ] Test error handling paths
   - [ ] Test compatibility aliases (runTask, getTask, cancelTask)
   - [ ] Test graph API methods
   - [ ] Test export/import API methods
   - **Estimated**: 15-20 test cases

2. **`src/api/client.ts`** (Base client)
   - [ ] Test apiClient initialization
   - [ ] Test error handling
   - [ ] Test request/response interceptors
   - **Estimated**: 8-10 test cases

3. **`src/api/events.ts`**
   - [ ] Test fetchEvents with various params
   - [ ] Test fetchEvent by ID
   - [ ] Test error scenarios
   - **Estimated**: 6-8 test cases

4. **`src/api/graph.ts`**
   - [ ] Test fetchGraph
   - [ ] Test fetchImpactAnalysis
   - [ ] Test fetchDependencyAnalysis
   - [ ] Test error handling
   - **Estimated**: 8-10 test cases

5. **`src/api/impact.ts`**
   - [ ] Test impact analysis methods
   - [ ] Test dependency analysis
   - **Estimated**: 6-8 test cases

6. **`src/api/items.ts`**
   - [ ] Test all CRUD operations
   - [ ] Test fetchRecentItems
   - [ ] Test error paths
   - **Estimated**: 10-12 test cases

7. **`src/api/links.ts`**
   - [ ] Test all link operations
   - [ ] Test error handling
   - **Estimated**: 8-10 test cases

8. **`src/api/projects.ts`**
   - [ ] Test all project operations
   - [ ] Test error scenarios
   - **Estimated**: 8-10 test cases

9. **`src/api/search.ts`**
   - [ ] Test search functionality
   - [ ] Test query building
   - **Estimated**: 6-8 test cases

10. **`src/api/system.ts`**
    - [ ] Test fetchSystemStatus
    - [ ] Test health check
    - **Estimated**: 4-6 test cases

**Phase 1 Total**: ~80-100 test cases  
**Expected Coverage Gain**: +15-20% statements, +12-18% branches

---

## Phase 2: Hooks (High Priority)

**Current**: Unknown (needs analysis)  
**Target**: 95%  
**Impact**: High (used throughout app)

### Hooks to Cover

1. **`src/hooks/useItems.ts`**
   - [ ] Test all query variations
   - [ ] Test error states
   - [ ] Test loading states
   - [ ] Test mutations (create, update, delete)
   - [ ] Test optimistic updates
   - **Estimated**: 15-20 test cases

2. **`src/hooks/useProjects.ts`**
   - [ ] Test project queries
   - [ ] Test CRUD operations
   - [ ] Test error handling
   - **Estimated**: 12-15 test cases

3. **`src/hooks/useLinks.ts`**
   - [ ] Test link queries
   - [ ] Test link operations
   - [ ] Test filtering
   - **Estimated**: 10-12 test cases

4. **`src/hooks/useItem.ts`** (single item)
   - [ ] Test single item fetch
   - [ ] Test error scenarios
   - [ ] Test loading states
   - **Estimated**: 6-8 test cases

5. **`src/hooks/useProject.ts`** (single project)
   - [ ] Test single project fetch
   - [ ] Test error handling
   - **Estimated**: 6-8 test cases

**Phase 2 Total**: ~50-65 test cases  
**Expected Coverage Gain**: +8-12% statements, +10-15% branches

---

## Phase 3: Views/Components (Medium Priority)

**Current**: Needs analysis  
**Target**: 95%  
**Impact**: Medium (UI layer)

### Priority Views

1. **Error States**
   - [ ] Test error boundaries
   - [ ] Test error displays
   - [ ] Test error recovery
   - **Estimated**: 10-15 test cases

2. **Loading States**
   - [ ] Test skeleton loaders
   - [ ] Test loading indicators
   - [ ] Test progressive loading
   - **Estimated**: 8-10 test cases

3. **Edge Cases**
   - [ ] Test empty states
   - [ ] Test null/undefined handling
   - [ ] Test boundary conditions
   - **Estimated**: 15-20 test cases

4. **User Interactions**
   - [ ] Test form submissions
   - [ ] Test button clicks
   - [ ] Test navigation
   - [ ] Test search/filter
   - **Estimated**: 20-25 test cases

**Phase 3 Total**: ~50-70 test cases  
**Expected Coverage Gain**: +5-8% statements, +8-12% branches

---

## Phase 4: Utils/Helpers (Lower Priority)

**Current**: Needs analysis  
**Target**: 95%  
**Impact**: Medium (supporting code)

### Areas to Cover

1. **`src/lib/openapi-utils.ts`**
   - [ ] Test all utility functions
   - [ ] Test edge cases
   - [ ] Test error handling
   - **Estimated**: 10-12 test cases

2. **`src/lib/enterprise-optimizations.ts`**
   - [ ] Test all hooks
   - [ ] Test performance optimizations
   - [ ] Test edge cases
   - **Estimated**: 8-10 test cases

3. **`src/utils/formatters.ts`**
   - [ ] Test all formatters
   - [ ] Test edge cases
   - [ ] Test null/undefined handling
   - **Estimated**: 12-15 test cases

4. **`src/utils/validators.ts`**
   - [ ] Test all validators
   - [ ] Test edge cases
   - [ ] Test error messages
   - **Estimated**: 15-20 test cases

5. **`src/utils/helpers.ts`**
   - [ ] Test all helper functions
   - [ ] Test edge cases
   - **Estimated**: 10-12 test cases

**Phase 4 Total**: ~55-70 test cases  
**Expected Coverage Gain**: +4-6% statements, +5-8% branches

---

## Phase 5: Stores (Lower Priority)

**Current**: 95.9% statements (already good!)  
**Target**: Maintain 95%+  
**Impact**: Low (already well covered)

### Areas to Maintain

1. **`src/stores/authStore.ts`**
   - [ ] Ensure all paths covered
   - [ ] Test edge cases
   - **Estimated**: 3-5 test cases

2. **`src/stores/itemsStore.ts`**
   - [ ] Test remaining edge cases
   - [ ] Test complex state transitions
   - **Estimated**: 5-8 test cases

3. **`src/stores/websocketStore.ts`**
   - [ ] Test WebSocket connections
   - [ ] Test reconnection logic
   - [ ] Test error handling
   - **Estimated**: 8-10 test cases

**Phase 5 Total**: ~15-25 test cases  
**Expected Coverage Gain**: +1-2% (maintenance)

---

## Implementation Strategy

### Week 1: API Layer Foundation (Critical) 🔴

- **Day 1**: endpoints.ts error paths (17% → 60%)
- **Day 2**: client.ts error handling (58% → 85%)
- **Day 3**: websocket.ts error scenarios (59% → 85%)
- **Day 4**: Remaining API files (events, graph, impact, etc.)
- **Day 5**: Review and fix gaps
- **Goal**: Reach 85% API coverage (+40% gain)

### Week 2: Hooks & Core Logic

- **Days 1-2**: useItems, useProjects, useLinks comprehensive tests
- **Day 3**: Remaining hooks (useItem, useProject, etc.)
- **Days 4-5**: Review and fix gaps
- **Goal**: Reach 90% overall coverage

### Week 3: Views & Edge Cases

- **Days 1-2**: Error states and loading states
- **Day 3**: Edge cases (empty, null, boundaries)
- **Days 4-5**: User interactions and form submissions
- **Goal**: Reach 93% overall coverage

### Week 4: Utils & Polish

- **Days 1-2**: Utils/helpers comprehensive tests
- **Day 3**: Fill remaining gaps
- **Days 4-5**: Review coverage reports, final verification
- **Goal**: Reach 95% coverage ✅

---

## Testing Best Practices

### 1. Test Structure

```typescript
describe('Component/Function Name', () => {
  describe('Happy Path', () => {
    it('should handle normal case', () => {});
  });

  describe('Error Handling', () => {
    it('should handle errors gracefully', () => {});
  });

  describe('Edge Cases', () => {
    it('should handle null/undefined', () => {});
    it('should handle empty inputs', () => {});
    it('should handle boundary conditions', () => {});
  });
});
```

### 2. Coverage Priorities

1. **Branches** (currently lowest at 64.89%)
   - Test all if/else paths
   - Test ternary operators
   - Test switch cases
   - Test early returns

2. **Functions** (67.02%)
   - Test all exported functions
   - Test all helper functions
   - Test error handlers

3. **Statements** (70.4%)
   - Test all code paths
   - Test error paths
   - Test edge cases

4. **Lines** (70.41%)
   - Ensure all lines executed
   - Test all branches

### 3. Mock Strategy

- Use MSW for API mocking
- Mock external dependencies
- Test error scenarios with mocked failures
- Test loading states

### 4. Test Types

- **Unit Tests**: Individual functions/components
- **Integration Tests**: Component interactions
- **Error Tests**: Error paths and recovery
- **Edge Case Tests**: Boundary conditions

---

## Success Metrics

### Milestones

- **Week 1 End**: 85% coverage
- **Week 2 End**: 90% coverage
- **Week 3 End**: 93% coverage
- **Week 4 End**: 95% coverage ✅

### Quality Gates

- All tests must pass
- No test flakiness
- Fast test execution (< 30s)
- Clear test descriptions

---

## Estimated Effort

- **Total Test Cases**: ~250-330 new tests
- **Time Estimate**: 3-4 weeks
- **Developer Days**: 15-20 days
- **Priority**: High (blocks production readiness)

---

## Quick Wins (Start Here) ⚡

### Week 1 Quick Wins (Highest ROI)

1. **endpoints.ts Error Paths** (1 day) - 🔴 CRITICAL
   - Current: 17.39% coverage, 483 uncovered lines
   - Add tests for all error handling
   - Test all API method wrappers
   - **Impact**: +15-20% API coverage immediately

2. **API Client Error Handling** (1 day)
   - Current: 58.06% coverage
   - Test error interceptors
   - Test network failures
   - **Impact**: +10-15% API coverage

3. **WebSocket Error Scenarios** (1 day)
   - Current: 58.76% coverage
   - Test connection failures
   - Test reconnection logic
   - **Impact**: +15-20% API coverage

4. **Hook Error States** (2 days)
   - Test error states in all hooks
   - Test loading states
   - **Impact**: +8-12% overall coverage

5. **Edge Cases in Utils** (1 day)
   - Test null/undefined handling
   - Test boundary conditions
   - **Impact**: +4-6% overall coverage

**Week 1 Total**: 6 days  
**Expected Gain**: +25-35% API coverage, +12-18% overall coverage

---

## Next Steps

1. ✅ Review this plan
2. ⏳ Run detailed coverage report to identify specific uncovered lines
3. ⏳ Prioritize based on actual coverage gaps
4. ⏳ Start with Phase 1 (API Layer)
5. ⏳ Track progress weekly

---

## Notes

- Focus on **branch coverage** first (currently lowest)
- API layer is the foundation - fix it first
- Use coverage reports to identify exact lines to cover
- Don't sacrifice test quality for quantity
- Maintain test performance (keep suite fast)
