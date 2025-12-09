# Advanced Services Batch 1 - Quick Reference

## Test File Location
```
tests/integration/services/test_advanced_services_batch1.py
```

## Quick Stats
| Metric | Value |
|--------|-------|
| Total Tests | 60+ |
| Services Covered | 5 |
| Previous Coverage | 0% |
| Target Coverage | 95%+ |
| Test Lines | ~1,340 |
| Test Classes | 5 |

## Services Under Test

### 1. AdvancedAnalyticsService
```python
# Location: src/tracertm/services/advanced_analytics_service.py
# Tests: TestAdvancedAnalyticsServiceIntegration (15 tests)
# Methods: project_metrics, team_analytics, trend_analysis,
#          dependency_metrics, quality_metrics, generate_report
```

### 2. AdvancedTraceabilityService
```python
# Location: src/tracertm/services/advanced_traceability_service.py
# Tests: TestAdvancedTraceabilityServiceIntegration (15 tests)
# Methods: find_all_paths, transitive_closure, bidirectional_impact,
#          coverage_gaps, circular_dependency_check
```

### 3. AdvancedTraceabilityEnhancementsService
```python
# Location: src/tracertm/services/advanced_traceability_enhancements_service.py
# Tests: TestAdvancedTraceabilityEnhancementsServiceIntegration (10 tests)
# Methods: detect_circular_dependencies, coverage_gap_analysis,
#          bidirectional_link_analysis, traceability_matrix_generation,
#          impact_propagation_analysis
```

### 4. AgentCoordinationService
```python
# Location: src/tracertm/services/agent_coordination_service.py
# Tests: TestAgentCoordinationServiceIntegration (10 tests)
# Methods: register_agent, detect_conflicts, resolve_conflict,
#          get_agent_activity
```

### 5. AgentPerformanceService
```python
# Location: src/tracertm/services/agent_performance_service.py
# Tests: TestAgentPerformanceServiceIntegration (10 tests)
# Methods: get_agent_stats, get_team_performance, get_agent_efficiency,
#          get_agent_workload, recommend_agent_assignment
```

## Run Commands

### Run All Batch 1 Tests
```bash
pytest tests/integration/services/test_advanced_services_batch1.py -v
```

### Run Specific Service Tests
```bash
# Analytics only
pytest tests/integration/services/test_advanced_services_batch1.py::TestAdvancedAnalyticsServiceIntegration -v

# Traceability only
pytest tests/integration/services/test_advanced_services_batch1.py::TestAdvancedTraceabilityServiceIntegration -v

# Enhancements only
pytest tests/integration/services/test_advanced_services_batch1.py::TestAdvancedTraceabilityEnhancementsServiceIntegration -v

# Coordination only
pytest tests/integration/services/test_advanced_services_batch1.py::TestAgentCoordinationServiceIntegration -v

# Performance only
pytest tests/integration/services/test_advanced_services_batch1.py::TestAgentPerformanceServiceIntegration -v
```

### Run with Coverage
```bash
pytest tests/integration/services/test_advanced_services_batch1.py \
  --cov=src/tracertm/services/advanced_analytics_service \
  --cov=src/tracertm/services/advanced_traceability_service \
  --cov=src/tracertm/services/advanced_traceability_enhancements_service \
  --cov=src/tracertm/services/agent_coordination_service \
  --cov=src/tracertm/services/agent_performance_service \
  --cov-report=term-missing \
  --cov-report=html
```

### Run Single Test
```bash
pytest tests/integration/services/test_advanced_services_batch1.py::TestAdvancedAnalyticsServiceIntegration::test_project_metrics_with_populated_project -v
```

## Test Fixtures

### Available Fixtures
```python
test_project          # Base project for tests
sample_items         # 10 items across 5 views
dependency_graph     # 9 links with various types
sample_events        # 50 events from 4 agents
sample_agents        # 5 agents with different types
```

### Fixture Data
```python
# sample_items (10 items)
Views: FEATURE (3), STORY (2), CODE (2), TEST (2), API (1)
Statuses: todo (3), in_progress (2), done (4), complete (1)
Priorities: high (5), medium (3), low (2)

# dependency_graph (9 links)
Types: implements (4), depends_on (3), tested_by (2), related_to (1)

# sample_events (50 events)
Types: item_created, item_updated, item_deleted, link_created, status_changed
Agents: agent-alpha, agent-beta, agent-gamma, agent-delta
Period: 15 days

# sample_agents (5 agents)
Types: developer, tester, analyst, designer, reviewer
Statuses: active (4), idle (1)
```

## Test Categories by Service

### AdvancedAnalyticsService
- ✅ Project metrics (populated, empty, completion rates)
- ✅ Team analytics (with/without events)
- ✅ Trend analysis (default/custom windows)
- ✅ Dependency metrics (with/without links)
- ✅ Quality metrics (descriptions, links)
- ✅ Comprehensive report generation

### AdvancedTraceabilityService
- ✅ Path finding (direct, multi-hop, none, depth-limited)
- ✅ Transitive closure (complete, isolated)
- ✅ Bidirectional impact (with/without links)
- ✅ Coverage gaps (partial, full)
- ✅ Circular dependencies (none, with cycles)

### AdvancedTraceabilityEnhancementsService
- ✅ Circular dependency detection
- ✅ Coverage gap analysis (full, partial, empty)
- ✅ Bidirectional link analysis (valid, not found)
- ✅ Traceability matrix (complete, empty)
- ✅ Impact propagation (depth-limited, errors)

### AgentCoordinationService
- ✅ Agent registration (success, with metadata)
- ✅ Conflict detection (none, concurrent)
- ✅ Conflict resolution (strategies, errors)
- ✅ Activity tracking (with events, limited)

### AgentPerformanceService
- ✅ Agent statistics (with events, time windows, errors)
- ✅ Team performance (multiple agents, empty)
- ✅ Efficiency metrics (high, low, ratings)
- ✅ Workload analysis (heavy, idle)
- ✅ Agent assignment (recommendation, errors)

## Common Test Patterns

### Given-When-Then Format
```python
"""
GIVEN: Project with items in various statuses
WHEN: project_metrics is called
THEN: Returns accurate counts and completion rate
"""
```

### Async Test Structure
```python
@pytest.mark.asyncio
async def test_something(db_session, test_project):
    # Arrange
    service = SomeService(db_session)

    # Act
    result = await service.some_method(test_project.id)

    # Assert
    assert result["key"] == expected_value
```

### Error Handling Tests
```python
# Test for errors
result = await service.method("nonexistent-id")
assert "error" in result

# Test for exceptions
with pytest.raises(ValueError, match="not found"):
    await service.method("bad-id")
```

## Coverage Validation

### Check Current Coverage
```bash
# Generate coverage report
pytest tests/integration/services/test_advanced_services_batch1.py --cov --cov-report=term

# View detailed HTML report
pytest tests/integration/services/test_advanced_services_batch1.py --cov --cov-report=html
open htmlcov/index.html
```

### Expected Results
```
advanced_analytics_service.py          95%+
advanced_traceability_service.py       95%+
advanced_traceability_enhancements_    90%+
agent_coordination_service.py          95%+
agent_performance_service.py           95%+
```

## Test Execution Time

| Service | Tests | Est. Time |
|---------|-------|-----------|
| AdvancedAnalytics | 15 | ~2-3s |
| AdvancedTraceability | 15 | ~3-4s |
| TraceabilityEnhancements | 10 | ~2-3s |
| AgentCoordination | 10 | ~2s |
| AgentPerformance | 10 | ~2s |
| **Total** | **60+** | **~12s** |

## Key Test Scenarios

### Analytics Service
```python
# Project metrics with diverse items
test_project_metrics_with_populated_project()

# Completion rate edge cases
test_calculate_completion_rate_all_done()
test_calculate_completion_rate_none_done()

# Comprehensive reporting
test_generate_report_comprehensive()
```

### Traceability Service
```python
# Multi-hop path finding
test_find_all_paths_multi_hop()

# Circular dependency detection
test_circular_dependency_check_with_cycle()

# Transitive closure
test_transitive_closure_complete_graph()
```

### Agent Services
```python
# Conflict detection and resolution
test_detect_conflicts_concurrent_activity()
test_resolve_conflict_last_write_wins()

# Performance metrics
test_get_agent_efficiency_high_activity()
test_recommend_agent_assignment_best_available()
```

## Troubleshooting

### Common Issues

**Issue**: Tests fail with database errors
```bash
# Solution: Ensure test database is clean
pytest --create-db tests/integration/services/test_advanced_services_batch1.py
```

**Issue**: Async warnings
```bash
# Solution: Ensure pytest-asyncio is installed
pip install pytest-asyncio
```

**Issue**: Import errors
```bash
# Solution: Ensure PYTHONPATH includes src
export PYTHONPATH=/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src:$PYTHONPATH
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Run Advanced Services Tests
  run: |
    pytest tests/integration/services/test_advanced_services_batch1.py \
      --cov --cov-report=xml --cov-report=term
```

### Coverage Thresholds
```ini
# pytest.ini or setup.cfg
[tool:pytest]
addopts =
    --cov-fail-under=95
    --cov=src/tracertm/services/advanced_analytics_service
    --cov=src/tracertm/services/advanced_traceability_service
    # ... other services
```

## Quick Debugging

### Run with Verbose Output
```bash
pytest tests/integration/services/test_advanced_services_batch1.py -vv -s
```

### Run Failed Tests Only
```bash
pytest tests/integration/services/test_advanced_services_batch1.py --lf
```

### Run with PDB on Failure
```bash
pytest tests/integration/services/test_advanced_services_batch1.py --pdb
```

### Show Test Durations
```bash
pytest tests/integration/services/test_advanced_services_batch1.py --durations=10
```

## Status

- ✅ Test file created
- ✅ 60+ tests implemented
- ✅ All 5 services covered
- ✅ Fixtures configured
- ✅ Documentation complete
- ⏳ Ready for execution (DO NOT RUN per user request)

## Next Actions

1. Validate test syntax (when ready to run)
2. Execute test suite
3. Review coverage reports
4. Address any gaps
5. Document final coverage metrics
