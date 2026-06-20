# Test Coverage Audit & Next Steps Plan

## Current Status Summary

### Test Execution Results (Latest Run)
- **Total Tests**: 576 integration tests
- **Passing**: 396 tests (68.75%)
- **Failing**: 176 tests (30.56%)
- **Skipped**: 4 tests (0.69%)

### Coverage Metrics
- **Current Coverage**: ~26.85% (from last successful run)
- **Target**: 85%+
- **5 modules at 80%+**: ✅ Proving the approach works
- **Critical infrastructure** (API, storage): Strong progress

## Primary Failure Analysis

### 1. Async/Sync Pattern Issues (90+ failures)
**Pattern**: `AttributeError: 'Session' object has no attribute 'run_sync'`
**Root Cause**: Mixing sync SQLAlchemy sessions with async test framework
**Location**: Services integration tests, Repository tests

### 2. Coroutine Handling Errors (50+ failures)
**Pattern**: `AttributeError: 'coroutine' object has no attribute 'id'`
**Root Cause**: Not awaiting coroutines before accessing attributes
**Location**: TraceabilityService, BulkOperationService, ExportImportService

### 3. Database Schema Issues (10+ failures)
**Pattern**: `no such table: sync_queue`
**Root Cause**: Missing table initialization in test fixtures
**Location**: SyncEngine integration tests

### 4. TUI Widget Event Issues (20+ failures)
**Pattern**: `RuntimeError: missing expected attributes`
**Root Cause**: Custom event classes not inheriting properly
**Location**: TUI widget interaction tests

## Actionable Roadmap to 85%

### Phase 1: Fix Critical Async Issues (Est. 2-3 hours, +10-15pp)
1. **Fix Session.run_sync errors**
   - Replace with proper `session.execute()` calls
   - Use `AsyncSession` consistently in tests
   - Target: Services & Repositories tests (90+ fixes)

2. **Fix coroutine attribute access**
   - Add proper `await` before accessing coroutine attributes
   - Fix service method calls that return coroutines
   - Target: All service integration tests (50+ fixes)

3. **Fix database setup**
   - Add missing table creation to fixtures
   - Ensure proper test isolation
   - Target: SyncEngine tests (10+ fixes)

### Phase 2: Stabilize Test Infrastructure (Est. 1-2 hours, +5-10pp)
1. **TUI Event System Fixes**
   - Fix custom event class inheritance
   - Update widget interaction patterns
   - Target: 20 TUI test failures

2. **CLI Import/Environment Issues**
   - Fix any remaining import path errors
   - Ensure proper test environment setup
   - Target: Any remaining CLI errors

### Phase 3: Strategic Coverage Gaps (Est. 4-6 hours, +25-30pp)
1. **TUI Module Coverage (Current: 0%)**
   - Generate TUI integration tests (100-150 tests)
   - Target: 70-80% coverage on TUI modules (+10pp)

2. **CLI Commands (Current: 5-10%)**
   - Focus on high-impact commands: item.py, link.py, project.py
   - Generate command-line integration tests
   - Target: 70-80% coverage (+10pp)

3. **Zero-Coverage Services (15+ services at 0%)**
   - Prioritize business-critical services
   - Generate focused integration tests
   - Target: 50-60% coverage (+8pp)

### Phase 4: Edge Cases & Fine-tuning (Est. 2-3 hours, +5-10pp)
1. **Push 70-80% modules to 85%**
   - api/sync_client.py (70% → 85%)
   - cycle_detection_service.py (79% → 85%)
   - bulk_operation_service.py (77% → 85%)

2. **Error handling & edge cases**
   - Add comprehensive error path testing
   - Boundary conditions and validation

## Priority Implementation Order

### Immediate (Do Now)
1. Fix async/sync pattern issues in services
2. Fix coroutine handling in integration tests
3. Initialize missing database tables

### Short-term (This Session)
1. Stabilize TUI event system
2. Fix any remaining CLI infrastructure
3. Run full test suite to validate fixes

### Medium-term (Next Session)
1. Generate TUI integration tests
2. Focus on high-impact CLI commands
3. Target zero-coverage services

### Long-term (Future Sessions)
1. Frontend test coverage (not in current scope)
2. Performance and edge case testing
3. Documentation test coverage

## Expected Coverage Progression

| Phase | Time | Expected Coverage | Key Wins |
|-------|------|------------------|----------|
| Current | - | 26.85% | 5 modules at 80%+ |
| Phase 1 | 2-3h | 35-40% | All integration tests passing |
| Phase 2 | 1-2h | 40-45% | Stable test infrastructure |
| Phase 3 | 4-6h | 65-75% | Major module coverage |
| Phase 4 | 2-3h | 75-85% | Target achieved |

## Success Metrics

### Short-term (Next 4 hours)
- [ ] 176 failing tests → < 50 failing tests
- [ ] Coverage increase to 35-40%
- [ ] All API and Storage tests passing

### Medium-term (Next 8 hours)
- [ ] TUI module coverage > 70%
- [ ] CLI command coverage > 70%
- [ ] Overall coverage > 65%

### Target (Next 12 hours)
- [ ] Overall coverage > 85%
- [ ] All critical modules > 80%
- [ ] Stable, maintainable test suite

## Resource Requirements

### Code Changes Needed
1. Async/sync pattern fixes (~15 files)
2. Test fixture improvements (~5 files)
3. TUI event system fixes (~10 files)
4. New test generation (~20 files)

### No Additional Dependencies
All required tools (pytest, pytest-asyncio, pytest-cov) are already installed and configured.

## Risk Mitigation

### Technical Risks
1. **Async complexity**: Use existing patterns from working tests
2. **Test isolation**: Ensure proper cleanup in fixtures
3. **Performance issues**: Use pytest-xdist for parallel execution

### Timeline Risks
1. **Unexpected bugs**: Focus on high-impact fixes first
2. **Scope creep**: Stay focused on 85% target
3. **Integration issues**: Test incrementally, validate each phase

## Conclusion

The foundation is solid with:
- 5 modules already at 80%+ coverage
- 396/576 integration tests passing (68.75%)
- Comprehensive test infrastructure in place

The path to 85% is clear and achievable with focused effort on:
1. Fixing async/sync patterns (immediate impact)
2. Generating TUI tests (major coverage boost)
3. Targeting CLI commands (significant contribution)

Estimated total time: **10-14 hours** to reach 85%+ coverage.
