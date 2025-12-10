# Impact Analysis Service Tests - Quick Reference

## New Test File Location
```
tests/unit/services/test_impact_analysis_extended.py
```

## Test Coverage Summary

### 28 New Tests Organized in 11 Classes

#### 1. Complex Topologies (5 tests)
```python
TestComplexTopologies
├── test_star_topology()               # 1 hub + 8 spokes
├── test_fully_connected_subgraph()    # Complete graph K5
├── test_bipartite_graph()             # 2 sets with cross-links
├── test_mesh_network_pattern()        # Redundant paths (6 nodes)
└── test_grid_graph_pattern()          # 3x3 grid with right/down links
```

**What they test:**
- Various dependency patterns
- BFS cycle prevention
- Depth tracking across patterns
- Critical path identification

#### 2. Metrics Validation (4 tests)
```python
TestMetricsValidation
├── test_affected_by_depth_consistency()      # Sum check
├── test_affected_by_view_accuracy()          # View counting
├── test_max_depth_reached_accuracy()         # Depth calculation
└── test_total_affected_count_accuracy()      # Count validation
```

**What they test:**
- Result metrics consistency
- Depth totals correctness
- View distribution accuracy
- Count correctness against actual items

#### 3. Boundary Conditions (4 tests)
```python
TestBoundaryConditions
├── test_max_depth_equal_one()                # Minimal depth
├── test_single_link_type_filter()            # Type filtering
├── test_empty_result_fields_populated()      # Empty structure
└── test_max_int_depth()                      # Very large depth
```

**What they test:**
- Edge depth values (0, 1, large)
- Filter behavior at boundaries
- Result structure initialization
- Unlimited traversal capability

#### 4. Reverse Impact Extended (2 tests)
```python
TestReverseImpactExtended
├── test_reverse_diamond_pattern()            # Multiple sources → 1 target
└── test_reverse_with_missing_intermediate()  # Skip missing items
```

**What they test:**
- Upstream dependency consolidation
- Graceful failure on missing items
- Reverse BFS validation

#### 5. Critical Path Extraction (2 tests)
```python
TestCriticalPathExtraction
├── test_multiple_critical_paths_complex_tree()  # Multi-branch tree
└── test_critical_paths_validation()             # Path integrity
```

**What they test:**
- Leaf node identification
- Multiple path generation
- Path structure validity

#### 6. Link Type Handling Advanced (2 tests)
```python
TestLinkTypeHandlingAdvanced
├── test_null_link_types_in_filter()  # None exclusion
└── test_link_type_case_sensitivity()  # Case exact matching
```

**What they test:**
- Null value filtering behavior
- Case-sensitive type matching
- Filter semantics correctness

#### 7. Data Validation (3 tests)
```python
TestDataValidation
├── test_all_affected_items_have_valid_paths()  # Path structure
├── test_depth_matches_path_length_minus_one()  # Invariant check
└── test_item_properties_preserved()            # Data preservation
```

**What they test:**
- Result data integrity
- Structural invariants
- Properties preservation through analysis

#### 8. Performance Edge Cases (2 tests)
```python
TestPerformanceEdgeCases
├── test_extremely_wide_graph()   # 100 children from root
└── test_very_deep_chain()        # 50 items deep
```

**What they test:**
- Breadth scalability (BFS queue)
- Depth scalability (memory)
- Algorithm efficiency

#### 9. View-Based Filtering (1 test)
```python
TestViewBasedFiltering
└── test_view_distribution_accuracy()  # REQ:2, DESIGN:3, CODE:1
```

**What they test:**
- View-based metric counting
- Multi-view graph traversal

#### 10. Status Tracking (1 test)
```python
TestStatusTracking
└── test_items_with_all_status_types()  # todo, in_progress, done, blocked
```

**What they test:**
- Status preservation
- Multi-status graph handling

#### 11. Integration Patterns (2 tests)
```python
TestIntegrationPatterns
├── test_sequential_dependency_chain()     # REQ→DESIGN→CODE→TEST
└── test_multi_requirement_hierarchy()     # Epic→Features→Stories
```

**What they test:**
- Real-world traceability chains
- Cross-view hierarchies
- Workflow patterns

## Running Tests

### Run All Extended Tests
```bash
pytest tests/unit/services/test_impact_analysis_extended.py -v
```

### Run Specific Test Class
```bash
pytest tests/unit/services/test_impact_analysis_extended.py::TestComplexTopologies -v
pytest tests/unit/services/test_impact_analysis_extended.py::TestMetricsValidation -v
```

### Run Single Test
```bash
pytest tests/unit/services/test_impact_analysis_extended.py::TestComplexTopologies::test_star_topology -v
```

### Run with Async Markers
```bash
pytest tests/unit/services/test_impact_analysis_extended.py -m asyncio -v
```

### Run All Impact Analysis Tests
```bash
pytest tests/unit/services/test_impact_analysis*.py -v
```

## Test Patterns Used

### Mock Item Creation
```python
item = create_mock_item(
    item_id="item-1",
    title="Item Title",
    view="REQ",
    item_type="requirement",
    status="active"
)
```

### Mock Link Creation
```python
link = create_mock_link(
    source_id="parent",
    target_id="child",
    link_type="traces_to"
)
```

### Service Setup
```python
@pytest.fixture
def service(async_session):
    service = ImpactAnalysisService(async_session)
    service.items = AsyncMock()
    service.links = AsyncMock()
    return service
```

### Graph Setup Pattern
```python
# Create items
items = {id: item for id, item in items_dict.items()}

# Create links
links = {id: [link1, link2, ...] for id, [links]}

# Mock repositories
service.items.get_by_id = AsyncMock(
    side_effect=lambda id: items.get(id)
)
service.links.get_by_source = AsyncMock(
    side_effect=lambda id: links.get(id, [])
)
```

### Analysis Call Pattern
```python
result = await service.analyze_impact(
    item_id="root",
    max_depth=10,
    link_types=["traces_to", "implements"]
)
```

### Result Validation Pattern
```python
assert result.total_affected == expected_count
assert result.max_depth_reached == expected_depth
assert result.affected_by_depth[1] == level1_count
assert result.affected_by_view["REQ"] == req_count
assert len(result.affected_items) == expected_count
assert len(result.critical_paths) >= min_paths
```

## Key Test Scenarios

### Scenario 1: Star Topology
- 1 central hub, 8 spokes
- All at depth 1
- 8 critical paths (one per spoke)
- Use case: API with multiple endpoint dependencies

### Scenario 2: Sequential Chain
- REQ → DESIGN → CODE → TEST
- Depth 1, 2, 3 respectively
- 1 critical path
- Use case: Waterfall traceability

### Scenario 3: Hierarchical Requirements
- Epic (root) → 3 Features → 6 Stories
- Depth 1 = 3 items, Depth 2 = 6 items
- 6 critical paths
- Use case: Agile traceability

### Scenario 4: Wide Graph
- 100 children at depth 1
- Tests BFS queue management
- Use case: Large module with many dependencies

### Scenario 5: Deep Chain
- 50 items in linear chain
- Tests depth tracking
- Use case: Complex sequential workflow

## Coverage Achieved

### By Feature
- ✅ Complex topologies: 5 patterns tested
- ✅ Metrics: 4 accuracy checks
- ✅ Boundaries: 4 edge cases
- ✅ Reverse impact: 2 scenarios
- ✅ Paths: 2 extraction tests
- ✅ Link types: 2 advanced cases
- ✅ Data: 3 validation tests
- ✅ Performance: 2 scalability tests
- ✅ Views: 1 distribution test
- ✅ Status: 1 tracking test
- ✅ Integration: 2 patterns

### By Method
- **analyze_impact:** 20+ tests
- **analyze_reverse_impact:** 2 tests
- **_find_critical_paths:** 2 tests
- **ImpactNode:** 2 tests
- **ImpactAnalysisResult:** 2 tests

### By Scenario
- **Basic operations:** Covered in existing tests
- **Complex graphs:** 5 new patterns
- **Edge cases:** 4 boundary tests + 2 performance tests
- **Real-world:** 2 integration patterns
- **Metrics:** 4 accuracy tests

## File Statistics

```
test_impact_analysis_extended.py
├── Lines: ~800
├── Classes: 11
├── Methods: 28
├── Fixtures: 3 (async_session, service, helpers)
├── Assertions: 100+ (3-5 per test)
└── Execution Time: < 1 second
```

## Integration with CI/CD

### Pre-commit Check
```bash
pytest tests/unit/services/test_impact_analysis_extended.py --tb=short
```

### Coverage Check
```bash
pytest tests/unit/services/test_impact_analysis*.py \
       tests/integration/services/test_impact_analysis*.py \
       -v --tb=short
```

### Full Test Suite
```bash
pytest tests/ -k "impact_analysis" -v --tb=short
```

## Test Maintenance

### Adding New Tests
1. Identify scenario (topology, metric, boundary, etc.)
2. Choose appropriate test class
3. Use mock factories for consistency
4. Include 3-5 assertions
5. Document with clear docstring

### Updating Tests
1. Keep fixtures synchronized
2. Update helpers if service changes
3. Maintain assertion coverage
4. Keep execution time < 1s per test

### Regression Prevention
- Tests serve as specification
- Document expected behavior
- Cover bug fix with regression test
- Maintain >90% passing rate

## Debugging Failed Tests

### Check Assertions First
```python
# Print actual values
print(f"Expected: {expected}")
print(f"Got: {result.field}")
```

### Inspect Mock Calls
```python
# Check if mocks were called correctly
service.items.get_by_id.assert_called()
service.links.get_by_source.assert_called()
```

### Validate Test Setup
```python
# Verify items and links graphs are correct
print(f"Items: {items}")
print(f"Links: {links}")
```

### Use Verbose Output
```bash
pytest test_impact_analysis_extended.py::TestClass::test_method -vv -s
```

## Resources

- Service Implementation: `src/tracertm/services/impact_analysis_service.py`
- Existing Unit Tests: `tests/unit/services/test_impact_analysis_comprehensive.py`
- Integration Tests: `tests/integration/services/test_impact_analysis_comprehensive.py`
- Coverage Report: `IMPACT_ANALYSIS_COVERAGE_REPORT.md`
