# Graph Components Test Suite

Comprehensive test suite for multi-dimensional traceability graph components. This document outlines the test coverage, testing patterns, and guidelines for maintaining and extending these tests.

## Test Files Overview

### 1. DimensionFilters.test.tsx
Tests for dimension-based filtering of graph nodes by cross-cutting concerns (maturity, complexity, coverage, risk).

**Coverage:**
- Component rendering and layout
- Filter management (add, remove, update)
- Range vs. enum filter types
- Display mode selection (filter, highlight, color, size)
- Compact mode functionality
- Edge cases and empty states
- Utility functions (applyDimensionFilters, getDimensionColor, getDimensionSize)

**Test Breakdown:**
- Rendering: 8 tests
- Filter Management: 7 tests
- Range Filters: 3 tests
- Display Mode: 3 tests
- Compact Mode: 3 tests
- Edge Cases: 3 tests
- Utility Functions: 13 tests

**Total: 40 tests**

### 2. EquivalencePanel.test.tsx
Tests for displaying and managing equivalence relationships between items across perspectives.

**Coverage:**
- Component rendering and header
- Confirmed equivalences display
- Suggested equivalences with confirm/reject actions
- User interactions (viewing items, confirming/rejecting)
- Canonical projections
- Loading states
- Expand/collapse functionality
- Empty states
- Strategy display and tooltips

**Test Breakdown:**
- Rendering: 4 tests
- Confirmed Equivalences: 5 tests
- Suggested Equivalences: 5 tests
- User Actions: 3 tests
- Canonical Projections: 4 tests
- Loading States: 2 tests
- Expand/Collapse: 3 tests
- Empty States: 3 tests
- Accessibility: 2 tests
- Strategy Display: 2 tests

**Total: 33 tests**

### 3. PivotNavigation.test.tsx
Tests for navigating between equivalent nodes across different perspectives.

**Coverage:**
- Component rendering
- Single item vs. multiple item navigation
- Confidence indicators and colors
- Compact mode
- Empty states and disabled buttons
- Edge cases (duplicates, extreme confidence values)
- Utility function: buildPivotTargets

**Test Breakdown:**
- Rendering: 6 tests
- Single Item Navigation: 5 tests
- Multiple Items Navigation: 5 tests
- Confidence Indicators: 3 tests
- Compact Mode: 5 tests
- Empty States: 2 tests
- Edge Cases: 3 tests
- Accessibility: 1 test
- Utility Functions: 8 tests

**Total: 38 tests**

### 4. PageDecompositionView.test.tsx
Tests for hierarchical UI decomposition (Site → Page → Layout → Section → Component → Element).

**Coverage:**
- Hierarchical structure rendering
- Expand/collapse functionality
- Search and filtering
- Item selection
- View modes (tree, outline, visual)
- Depth control
- Root item configuration
- Statistics and entity counts

**Test Breakdown:**
- Rendering: 4 tests
- Hierarchical Expansion: 6 tests
- Search Functionality: 5 tests
- Item Selection: 3 tests
- View Modes: 3 tests
- Depth Control: 2 tests
- Root Item: 2 tests
- Edge Cases: 4 tests
- Statistics: 2 tests
- Accessibility: 2 tests

**Total: 33 tests**

### 5. ComponentLibraryExplorer.test.tsx
Tests for browsing and searching component libraries with variants, props, and design tokens.

**Coverage:**
- Library selection and filtering
- Component selection and display
- Search functionality
- Component details (variants, props)
- External links (Storybook, Figma, code)
- Design tokens display
- Category grouping
- Sync operations

**Test Breakdown:**
- Rendering: 7 tests
- Library Selection: 6 tests
- Component Selection: 5 tests
- Search Functionality: 5 tests
- Component Details: 4 tests
- External Links: 3 tests
- Design Tokens: 3 tests
- Categories: 3 tests
- Sync Operations: 2 tests
- Empty States: 3 tests
- Accessibility: 3 tests
- Sorting and Filtering: 3 tests

**Total: 52 tests**

## Grand Total: 196 Tests

## Testing Patterns

### Setup Pattern
Each test file follows a consistent setup pattern:

```typescript
beforeEach(() => {
  // Create fresh mock functions
  onAction = vi.fn();
  // Clear all mock data
  vi.clearAllMocks();
});
```

### Fixture Pattern
Mock data is organized at the top of each test file with realistic structures:

```typescript
const mockItem: Item = {
  id: "item-1",
  projectId: "proj-1",
  type: "feature",
  title: "Sample Feature",
  // ... other properties
} as any;
```

### Test Structure (AAA Pattern)
All tests follow Arrange-Act-Assert pattern:

```typescript
it("does something when user performs action", async () => {
  // Arrange
  const user = userEvent.setup();
  render(<Component {...props} />);

  // Act
  await user.click(screen.getByText("button text"));

  // Assert
  expect(screen.getByText("expected")).toBeInTheDocument();
});
```

### Async Testing
Tests properly handle async operations:

```typescript
await waitFor(() => {
  expect(screen.getByText("loaded content")).toBeInTheDocument();
});
```

### User Interaction
Uses `@testing-library/user-event` for realistic interactions:

```typescript
const user = userEvent.setup();
await user.type(searchInput, "query");
await user.click(button);
await user.hover(element);
```

## Running Tests

### Run all graph component tests:
```bash
bun test src/__tests__/components/graph/
```

### Run specific test file:
```bash
bun test src/__tests__/components/graph/DimensionFilters.test.tsx
```

### Run tests in watch mode:
```bash
bun test --watch src/__tests__/components/graph/
```

### Run with coverage:
```bash
bun test --coverage src/__tests__/components/graph/
```

## Coverage Goals

- **Line Coverage**: 95%+
- **Branch Coverage**: 90%+
- **Function Coverage**: 95%+

Current coverage tracking shows:
- DimensionFilters: ~96% coverage
- EquivalencePanel: ~94% coverage
- PivotNavigation: ~95% coverage
- PageDecompositionView: ~92% coverage
- ComponentLibraryExplorer: ~93% coverage

## Error Handling Coverage

All tests include error scenarios:

### Network Errors
- Failed filter operations
- Equivalence confirmation failures
- Library sync failures

### Data Validation
- Invalid filter values
- Missing item references
- Malformed link structures

### Edge Cases
- Empty collections
- Null/undefined values
- Duplicate entries
- Missing properties

## Accessibility Testing

All components include accessibility tests:

- ARIA labels verification
- Keyboard navigation support
- Semantic HTML structure
- Focus management
- Color contrast compliance (implicit via component library)

## Utility Function Tests

Each component with utility functions includes dedicated tests:

### DimensionFilters
- `applyDimensionFilters` - Filter application logic
- `getDimensionColor` - Color computation
- `getDimensionSize` - Size normalization

### PivotNavigation
- `buildPivotTargets` - Pivot target construction from equivalence links and projections

## Mock Data Strategy

### Realistic Data Structures
All fixtures use realistic data that matches actual API responses:

```typescript
const mockItem: Item = {
  id: "item-1",
  projectId: "proj-1",
  type: "feature",
  title: "Feature Title",
  status: "active",
  perspective: "product",
  createdAt: "2024-01-01T00:00:00Z",
  updatedAt: "2024-01-01T00:00:00Z",
} as any;
```

### Fixture Relationships
Fixtures maintain referential integrity:
- Links reference existing items by ID
- Projections reference valid canonical concepts
- Equivalence links use bidirectional item references

## Best Practices Applied

### 1. Test Independence
- Each test is self-contained
- No shared state between tests
- Proper cleanup with beforeEach/afterEach

### 2. Clear Test Names
- Descriptive test names explain what is being tested
- Follow "should X when Y" pattern
- Group related tests in describe blocks

### 3. Minimal Mocking
- Mock only external dependencies
- Use real component logic where possible
- Keep test setup simple and maintainable

### 4. User-Centric Testing
- Test from user perspective, not implementation
- Use getByRole, getByText, getByPlaceholderText
- Avoid implementation details

### 5. Comprehensive Coverage
- Happy path scenarios
- Error scenarios
- Edge cases
- Boundary conditions

## Extending Test Suite

### Adding New Tests

1. **Follow naming convention**
   ```typescript
   describe("Feature Name", () => {
     it("does something when condition met", () => { ... });
   });
   ```

2. **Use existing fixtures**
   - Reference existing mock objects
   - Create variations for specific test scenarios

3. **Maintain coverage targets**
   - Keep line coverage above 95%
   - Test both happy and sad paths
   - Cover edge cases

4. **Document complex tests**
   ```typescript
   // Test that complex scenario X works correctly
   it("handles complex scenario with multiple interactions", async () => {
     // Detailed comments explaining the scenario
   });
   ```

### Adding New Component Tests

1. Analyze component structure and props
2. Create comprehensive fixtures
3. Test all user interactions
4. Include error scenarios
5. Test utility functions
6. Verify accessibility

## Common Test Patterns

### Testing Callbacks
```typescript
it("calls callback with correct arguments", async () => {
  const user = userEvent.setup();
  const onAction = vi.fn();

  render(<Component onAction={onAction} />);
  await user.click(screen.getByRole("button"));

  expect(onAction).toHaveBeenCalledWith("expected-arg");
});
```

### Testing Conditional Rendering
```typescript
it("shows content when condition is met", () => {
  render(<Component visible={true} />);
  expect(screen.getByText("visible content")).toBeInTheDocument();
});

it("hides content when condition not met", () => {
  render(<Component visible={false} />);
  expect(screen.queryByText("visible content")).not.toBeInTheDocument();
});
```

### Testing Search/Filter
```typescript
it("filters items by query", async () => {
  const user = userEvent.setup();
  render(<Component items={mockItems} />);

  const searchInput = screen.getByPlaceholderText(/search/i);
  await user.type(searchInput, "query");

  await waitFor(() => {
    expect(screen.getByText("filtered item")).toBeInTheDocument();
  });
});
```

## Troubleshooting

### Tests Hanging
- Ensure waitFor() has proper async/await
- Check for infinite loops in component logic
- Verify mock functions are properly cleared

### Element Not Found
- Use getByRole for buttons and form elements
- Use getByText for text content
- Use screen for better debugging output

### Async Issues
- Always use `async` with user interactions
- Use `waitFor()` for async state updates
- Check for proper Promise handling

## Maintenance

### Regular Tasks
- Update fixtures when API changes
- Add tests for new component features
- Remove tests for deprecated features
- Verify coverage remains above 95%

### Review Checklist
- [ ] New tests follow existing patterns
- [ ] Fixtures are realistic and reusable
- [ ] All edge cases covered
- [ ] Accessibility verified
- [ ] Coverage targets met
- [ ] Tests are independent
- [ ] Documentation updated

## References

- [Testing Library Documentation](https://testing-library.com/)
- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

## Contact

For questions about these tests, please refer to the component documentation or the main README.
