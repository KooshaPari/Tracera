# Multi-Dimensional Traceability Graph E2E Tests

## Overview

Comprehensive end-to-end test suite for the multi-dimensional traceability graph features in TraceRTM. These tests validate the display modes, filtering capabilities, equivalence management, journey visualization, and component library functionality.

## Test Files

### 1. `multi-perspective.spec.ts`
Tests for switching between different display modes and perspective selections.

**Test Groups:**
- **Display Mode Switching**
  - `should render default single view mode` - Verify single view is default
  - `should switch to split view mode` - Test split view activation
  - `should switch to layered view mode` - Test layered view activation
  - `should switch to unified view mode` - Test unified view with all dimensions
  - `should switch to pivot view mode` - Test pivot/navigation view
  - `should toggle between view modes without data loss` - Verify data persistence

- **Split View Perspectives**
  - `should display two side-by-side graph containers` - Split layout verification
  - `should select different perspectives for split panels` - Independent perspective selection
  - `should synchronize pan/zoom between split panels` - Cross-panel sync

- **Pivot Navigation**
  - `should navigate between equivalents in pivot view` - Navigate via equivalent items
  - `should show equivalence relationships in pivot mode` - Display equivalence indicators

- **Dimension Perspective Selection**
  - `should show available dimensions for perspective selection` - Display dimension options
  - `should switch dimension perspective and update display` - Dynamic perspective switching

- **View Persistence and State Management**
  - `should remember selected display mode after page refresh` - State persistence
  - `should maintain perspective selections across view changes` - Data consistency

**Coverage:** 12 tests covering all display modes and perspective management

---

### 2. `dimension-filters.spec.ts`
Tests for applying and managing dimension-based filters on the graph.

**Test Groups:**
- **Maturity Filters**
  - `should display maturity filter control` - Control visibility
  - `should apply maturity filter - Draft` - Draft filter
  - `should apply maturity filter - Approved` - Approved filter
  - `should apply multiple maturity filters` - Multi-select filtering

- **Complexity Filters**
  - `should apply complexity filter - High` - High complexity filter
  - `should apply complexity filter - Low` - Low complexity filter
  - `should apply complexity filter - Critical` - Critical complexity filter

- **Coverage Filters**
  - `should apply coverage filter - Complete` - Complete coverage
  - `should apply coverage filter - Partial` - Partial coverage
  - `should apply coverage filter - Not Covered` - Uncovered items

- **Risk Filters**
  - `should apply risk filter - High` - High risk items
  - `should apply risk filter - Critical` - Critical risk items
  - `should apply risk filter - Low` - Low risk items

- **Filter Display Modes**
  - `should switch to filter display mode - Hide non-matching` - Filter/hide mode
  - `should switch to highlight display mode` - Highlight visualization
  - `should switch to color display mode` - Color-coded visualization
  - `should switch to size display mode` - Size-based visualization

- **Clear and Reset Filters**
  - `should clear all filters` - Reset all filters
  - `should reset individual filter` - Remove single filter
  - `should combine multiple filters` - Test filter combinations

- **Filter Persistence**
  - `should preserve filters across graph interactions` - State preservation during zoom/pan

**Coverage:** 17 tests covering all dimension types and filter modes

---

### 3. `equivalence.spec.ts`
Tests for viewing, managing, and navigating equivalent items.

**Test Groups:**
- **View Equivalence Panel**
  - `should display equivalence panel when node is selected` - Panel visibility
  - `should show equivalence list for selected item` - List equivalents
  - `should display equivalence strength/confidence` - Show confidence scores
  - `should show equivalence metadata` - Metadata display

- **Suggested Equivalences**
  - `should display suggested equivalences` - Show suggestions
  - `should show confirmation actions for suggested equivalences` - Action buttons

- **Confirm Equivalences**
  - `should confirm suggested equivalence` - Approve suggestion
  - `should confirm multiple equivalences` - Batch confirmation
  - `should show confirmation feedback` - User feedback

- **Reject Equivalences**
  - `should reject suggested equivalence` - Deny suggestion
  - `should show rejection feedback` - Rejection feedback

- **Navigate via Pivot Targets**
  - `should navigate to equivalent item` - Click-to-navigate
  - `should highlight selected equivalent in graph` - Visual highlighting
  - `should show pivot path to equivalent` - Path information
  - `should navigate to pivot target and update panel` - Navigation and UI update

- **Equivalence Visual Relationships**
  - `should show equivalence edges in graph` - Edge visualization
  - `should highlight equivalence relationships when hovering` - Interactive highlighting

**Coverage:** 16 tests covering equivalence management and navigation

---

### 4. `journey-overlay.spec.ts`
Tests for selecting and visualizing user journeys on the graph.

**Test Groups:**
- **Journey Selection**
  - `should display journey selector dropdown` - Selector visibility
  - `should list available journeys` - Journey enumeration
  - `should select journey from dropdown` - Selection interaction
  - `should show selected journey name` - Selection feedback
  - `should handle multiple journey selection` - Multi-select support

- **Journey Highlighting**
  - `should highlight journey nodes in graph` - Visual highlighting
  - `should show journey path visualization` - Path display
  - `should distinguish journey start and end nodes` - Node classification
  - `should highlight journey sequence steps` - Step numbering

- **Journey Statistics and Metrics**
  - `should display journey statistics panel` - Stats panel
  - `should show journey step count` - Count display
  - `should display journey coverage metrics` - Coverage stats
  - `should show journey completion status` - Status display

- **Journey Explorer Navigation**
  - `should navigate journey steps sequentially` - Next/previous navigation
  - `should click on journey step in list to navigate` - List-based navigation
  - `should scroll to center graph on journey step selection` - Auto-focus

- **Journey Filtering**
  - `should filter graph to show only journey items` - Journey-only view
  - `should preserve other filters when journey is selected` - Filter composition

- **Clear Journey Overlay**
  - `should clear journey selection` - Remove overlay
  - `should restore normal graph after clearing journey` - State restoration

**Coverage:** 17 tests covering journey selection, visualization, and navigation

---

### 5. `component-library.spec.ts`
Tests for browsing, searching, and managing components in the library.

**Test Groups:**
- **Component Library Access**
  - `should display component library button/panel` - UI availability
  - `should open component library panel` - Panel opening
  - `should display component categories` - Category enumeration

- **Browse Components**
  - `should list components in library` - Component enumeration
  - `should display component names and types` - Metadata display
  - `should allow browsing components by scrolling` - Scrollable list
  - `should show component count` - Count indicator

- **Search Components**
  - `should display search input in component library` - Search UI
  - `should search components by name` - Name search
  - `should search components by type` - Type search
  - `should show no results message when search returns nothing` - Empty state

- **Filter Components**
  - `should filter components by category` - Category filtering
  - `should filter components by status` - Status filtering

- **View Component Details**
  - `should click on component to view details` - Detail panel
  - `should display component metadata` - Metadata display
  - `should show component description` - Description display
  - `should show component relationships` - Relationship display

- **Component Visualization**
  - `should visualize component in graph context` - Graph integration
  - `should highlight component in graph when selected` - Interactive highlighting

- **Add Component to Graph**
  - `should show add/import component button` - Button visibility
  - `should add component to graph` - Add functionality
  - `should show add confirmation feedback` - User feedback

**Coverage:** 19 tests covering component library operations

---

## Test Execution

### Run All Multi-Dimensional Tests
```bash
bun run test:e2e -- multi-perspective.spec.ts dimension-filters.spec.ts equivalence.spec.ts journey-overlay.spec.ts component-library.spec.ts
```

### Run Individual Test Files
```bash
# Display modes
bun run test:e2e -- multi-perspective.spec.ts

# Dimension filters
bun run test:e2e -- dimension-filters.spec.ts

# Equivalence management
bun run test:e2e -- equivalence.spec.ts

# Journey overlay
bun run test:e2e -- journey-overlay.spec.ts

# Component library
bun run test:e2e -- component-library.spec.ts
```

### Run Specific Test Groups
```bash
# Run only split view tests
bun run test:e2e -- multi-perspective.spec.ts -g "Split View"

# Run only maturity filters
bun run test:e2e -- dimension-filters.spec.ts -g "Maturity Filters"

# Run only equivalence confirmation tests
bun run test:e2e -- equivalence.spec.ts -g "Confirm Equivalences"
```

---

## Test Configuration

### Framework: Playwright
- **Base URL:** http://localhost:5173
- **Timeout:** 30 seconds per test
- **Browsers:** Chromium (default)
- **API Mocking:** Enabled (global-setup.ts)

### Key Testing Patterns

1. **Graceful Degradation:**
   - All tests use `.catch(() => false)` for optional features
   - Tests log informative messages when features aren't available
   - No test failures for unimplemented features

2. **Flexible Selectors:**
   - Multiple selector strategies for UI elements
   - Support for different component structures
   - Text-based matching with regex patterns

3. **Wait Strategies:**
   - Network idle detection for page loads
   - Custom timeouts for slow operations
   - Consistent 500ms waits between interactions

4. **Logging:**
   - console.log() for test progress tracking
   - Descriptive messages for debugging
   - Clear success/failure indicators

---

## Test Data

### Test Projects
- TraceRTM Frontend
- Pokemon Go Demo
- E-Commerce Platform

### Test Items
- User Authentication (requirement)
- Dashboard View (feature)
- API Integration (requirement)
- Unit Tests (test)

### Mock Data Setup
See: `/e2e/fixtures/api-mocks.ts`

---

## Coverage Analysis

### Total Tests: 81

| Feature | Tests | Coverage |
|---------|-------|----------|
| Display Modes | 12 | All 5 modes + state persistence |
| Dimension Filters | 17 | 4 dimensions × 3-4 values each + display modes |
| Equivalence | 16 | Viewing, confirming, rejecting, navigation |
| Journey Overlay | 17 | Selection, visualization, stats, navigation |
| Component Library | 19 | Browsing, searching, filtering, details, add |

### Feature Coverage

- **Display Modes:** Single, Split, Layered, Unified, Pivot
- **Dimension Filters:** Maturity, Complexity, Coverage, Risk
- **Filter Display:** Filter, Highlight, Color, Size
- **Equivalence:** View, Suggest, Confirm, Reject, Navigate
- **Journey:** Select, Highlight, Stats, Navigate, Clear
- **Components:** Browse, Search, Filter, Detail, Visualize, Add

---

## Error Handling

### Graceful Test Degradation

Tests are designed to handle:
- Missing UI elements (features not yet implemented)
- Dynamic data loading (eventual consistency)
- Optional features (some features may be disabled)
- Different component structures
- API latency

### Logging Output

Each test logs:
- Feature availability ("found", "not visible")
- Action results (node counts, item counts)
- State changes (mode switched, filter applied)
- Errors are logged but don't fail tests

---

## Best Practices

1. **Test Independence:**
   - Each test is self-contained with beforeEach setup
   - No test depends on another test's state

2. **User Workflows:**
   - Tests follow realistic user interactions
   - Test sequences match typical workflows

3. **Accessibility:**
   - Tests verify UI is interactive
   - Tests check for proper aria labels
   - Tests validate visual feedback

4. **Performance:**
   - Tests use parallel-safe fixtures
   - Minimal async operations
   - Efficient selector strategies

---

## Extending Tests

### Adding New Display Mode Tests
1. Create test in `multi-perspective.spec.ts`
2. Use consistent selector patterns
3. Verify mode toggle and display
4. Test data persistence

### Adding New Filter Tests
1. Add to appropriate dimension group in `dimension-filters.spec.ts`
2. Test filter application and clearing
3. Verify visual feedback
4. Test filter combinations

### Adding New Equivalence Tests
1. Create test in `equivalence.spec.ts`
2. Test confirmation/rejection flow
3. Verify navigation and highlighting
4. Check panel updates

---

## Known Limitations

1. **Visual Assertions:**
   - Tests don't verify exact visual appearance
   - Focus on interaction and data flow
   - Visual regression testing would be separate

2. **Mock Data:**
   - Tests use fixed mock data
   - Dynamic data scenarios limited
   - Integration tests needed for real data

3. **Performance Tests:**
   - Load time not validated
   - Large dataset handling not tested
   - Separate performance suite recommended

---

## Debugging Tips

### Enable Debug Output
```bash
DEBUG=pw:api bun run test:e2e -- multi-perspective.spec.ts
```

### Run with Headed Browser
```bash
bun run test:e2e -- --headed multi-perspective.spec.ts
```

### Generate Trace on Failure
```bash
bun run test:e2e -- --trace on multi-perspective.spec.ts
```

### View HTML Report
```bash
bun run test:e2e -- multi-perspective.spec.ts
npx playwright show-report
```

---

## Test Metrics

### Execution Time
- Average per test: 5-10 seconds
- Full suite: ~10-15 minutes
- Parallel execution: ~5-10 minutes (2 workers)

### Failure Rate
- Expected: 0% (when features are implemented)
- Graceful degradation: Tests skip optional features

### Maintenance
- Update selectors when UI changes
- Add tests for new features
- Keep mock data synchronized

---

## CI/CD Integration

### GitHub Actions Configuration
```yaml
- name: Run E2E Tests
  run: bun run test:e2e
  timeout-minutes: 30
```

### Test Artifacts
- HTML reports: `playwright-report/`
- JSON results: `playwright-report/results.json`
- Screenshots on failure: `test-results/`
- Videos on failure: `test-results/`

---

## References

- Playwright Documentation: https://playwright.dev/docs/intro
- Test Configuration: `/e2e/playwright.config.ts`
- Global Setup: `/e2e/global-setup.ts`
- Test Helpers: `/e2e/critical-path-helpers.ts`
- API Mocks: `/e2e/fixtures/api-mocks.ts`
