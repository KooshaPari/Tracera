# Phase 1 Frontend Testing Planning

**Status:** Phase 1 Backend Complete ✅ | Frontend Tests Pending
**Target:** Complete 10 frontend component tests to reach Phase 1 completion
**Expected Completion:** End of Week 2

---

## 📋 Frontend Components Requiring Tests (10 Total)

### UI Component Tests (3 files)

#### 1. **test_Button.test.tsx**
**Location:** `frontend/apps/web/src/components/Button.test.tsx`

**Tests to Implement:**
- Render button with default props
- Render button with custom label
- Render button with different variants (primary, secondary, danger, ghost)
- Render button with different sizes (small, medium, large)
- Render button with disabled state
- Render button with loading state
- Click handler execution
- Keyboard accessibility (Enter, Space)
- ARIA attributes
- Icon rendering with button
- Tooltip presence

**Test Pattern:**
```typescript
import { render, screen } from '@testing-library/react';
import Button from '@/components/Button';

describe('Button Component', () => {
  it('renders with label', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });
});
```

#### 2. **test_Header.test.tsx**
**Location:** `frontend/apps/web/src/components/Header.test.tsx`

**Tests to Implement:**
- Render header with navigation
- Render header with user menu
- Navigation links present and clickable
- User profile dropdown
- Project selector
- Search functionality
- Mobile responsive behavior
- Menu icon visibility on mobile
- Logo rendering
- Breadcrumb navigation

**Existing Test Reference:**
- Check `frontend/apps/web/src/__tests__/` for Header component usage patterns
- Verify navigation structure matches existing implementations

#### 3. **test_Sidebar.test.tsx**
**Location:** `frontend/apps/web/src/components/Sidebar.test.tsx`

**Tests to Implement:**
- Render sidebar with menu items
- Menu item selection and highlighting
- Sidebar collapse/expand toggle
- Sub-menu expansion
- Active item indication
- Scrolling behavior for long lists
- Search in sidebar
- Mobile sidebar visibility
- Close sidebar on route change

### Form Component Tests (3 files)

#### 4. **test_CreateItemForm.test.tsx**
**Location:** `frontend/apps/web/src/components/forms/CreateItemForm.test.tsx`

**Tests to Implement:**
- Form renders with all fields (title, description, type, status, priority)
- Title field required validation
- Form submission with valid data
- Form validation on submit with empty title
- Error messages display for invalid fields
- Success message on form submission
- Reset form after submission
- Item type selector options
- Status selector options
- Priority selector options
- Character counter for title (max length)
- Rich text editor for description

**Test Pattern:**
```typescript
it('validates required title field', async () => {
  render(<CreateItemForm />);
  const submitButton = screen.getByRole('button', { name: /create/i });

  fireEvent.click(submitButton);

  expect(screen.getByText(/title is required/i)).toBeInTheDocument();
});
```

#### 5. **test_CreateProjectForm.test.tsx**
**Location:** `frontend/apps/web/src/components/forms/CreateProjectForm.test.tsx`

**Tests to Implement:**
- Form renders with all fields (name, description, visibility)
- Name field required validation
- Form submission with valid data
- Form validation on submit with empty name
- Error messages display
- Success message on form submission
- Visibility selector (private, internal, public)
- Owner field selection
- Team member addition
- Form reset after submission

#### 6. **test_CreateLinkForm.test.tsx**
**Location:** `frontend/apps/web/src/components/forms/CreateLinkForm.test.tsx`

**Tests to Implement:**
- Form renders with source/target item selectors
- Form renders with link type selector
- Source item selection
- Target item selection
- Link type options display
- Form submission creates link
- Prevent self-reference validation
- Prevent duplicate link validation
- Error handling for missing items
- Success feedback on link creation

### Dialog Component Tests (2 files)

#### 7. **test_Dialog.test.tsx**
**Location:** `frontend/apps/web/src/components/Dialog.test.tsx`

**Tests to Implement:**
- Dialog renders when open prop is true
- Dialog hidden when open prop is false
- Dialog title renders
- Dialog content renders
- Dialog close button works
- Dialog closes on Escape key
- Dialog outside click closes it (configurable)
- Dialog actions (OK, Cancel) buttons
- Dialog modal overlay
- Focus management in dialog
- ARIA attributes for accessibility

#### 8. **test_ConfirmDialog.test.tsx**
**Location:** `frontend/apps/web/src/components/dialogs/ConfirmDialog.test.tsx`

**Tests to Implement:**
- Confirm dialog renders title
- Confirm dialog renders message
- Confirm button text customizable
- Cancel button text customizable
- Confirm button callback execution
- Cancel button callback execution
- Dialog closes after confirm
- Dialog closes after cancel
- Danger state styling
- Custom action button styling

### Table/Tree Component Tests (2 files)

#### 9. **test_ItemsTable.test.tsx**
**Location:** `frontend/apps/web/src/components/tables/ItemsTable.test.tsx`

**Tests to Implement:**
- Table renders with items
- Table columns display correctly
- Item selection checkbox
- Bulk selection (select all)
- Sorting by columns
- Column resizing
- Pagination controls
- Row actions menu
- Status indicator styling
- Priority indicator styling
- Type indicator styling
- Empty state message
- Loading state skeleton
- Infinite scroll or pagination

**Props Expected:**
```typescript
interface ItemsTableProps {
  items: Item[];
  selectedItems?: string[];
  onSelectItem?: (id: string) => void;
  onSelectAll?: (selected: boolean) => void;
  onSort?: (column: string, direction: 'asc' | 'desc') => void;
  onPageChange?: (page: number) => void;
}
```

#### 10. **test_ItemsTree.test.tsx**
**Location:** `frontend/apps/web/src/components/trees/ItemsTree.test.tsx`

**Tests to Implement:**
- Tree renders with items
- Tree expands/collapses nodes
- Tree shows hierarchy correctly
- Tree item selection
- Bulk selection in tree
- Drag and drop within tree
- Context menu on tree items
- Search filtering tree
- Empty state when no items
- Loading state for children

---

## 🏗️ Frontend Testing Architecture

### Testing Stack
- **Framework:** Vitest (or Jest)
- **UI Testing:** React Testing Library (@testing-library/react)
- **User Interactions:** userEvent for realistic testing
- **Assertions:** @testing-library/jest-dom matchers

### Test File Structure
```typescript
// Standard test file template
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ComponentName } from '@/components/ComponentName';

describe('ComponentName', () => {
  describe('Rendering', () => {
    it('renders component', () => {
      render(<ComponentName />);
      // assertions
    });
  });

  describe('User Interactions', () => {
    it('handles click events', async () => {
      render(<ComponentName />);
      // interaction and assertions
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA attributes', () => {
      render(<ComponentName />);
      // accessibility assertions
    });
  });
});
```

### Test Patterns to Use

#### 1. **Component Rendering**
```typescript
it('renders with required props', () => {
  const { container } = render(<Button>Click</Button>);
  expect(container).toBeInTheDocument();
});
```

#### 2. **User Events**
```typescript
it('handles click events', async () => {
  const handleClick = vi.fn();
  render(<Button onClick={handleClick}>Click</Button>);

  await userEvent.click(screen.getByRole('button'));
  expect(handleClick).toHaveBeenCalled();
});
```

#### 3. **Form Validation**
```typescript
it('validates required field', async () => {
  render(<Form />);
  const submitButton = screen.getByRole('button', { name: /submit/i });

  await userEvent.click(submitButton);

  expect(screen.getByText(/required/i)).toBeInTheDocument();
});
```

#### 4. **Async Operations**
```typescript
it('displays data after loading', async () => {
  render(<Component />);

  expect(screen.getByRole('status')).toHaveTextContent('Loading');

  const element = await screen.findByText('Loaded Data');
  expect(element).toBeInTheDocument();
});
```

#### 5. **Accessibility**
```typescript
it('has proper ARIA labels', () => {
  render(<Component />);

  expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
  expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
});
```

---

## 📊 Frontend Test Metrics Target

| Component | Test Cases | Target Classes | Scenarios |
|-----------|-----------|-----------------|-----------|
| Button | 12 | 3 | rendering, interactions, accessibility |
| Header | 10 | 3 | navigation, responsive, user menu |
| Sidebar | 10 | 3 | menu, collapse, mobile |
| CreateItemForm | 15 | 3 | form, validation, submission |
| CreateProjectForm | 12 | 3 | form, visibility, team |
| CreateLinkForm | 10 | 3 | form, validation, creation |
| Dialog | 12 | 3 | dialog, accessibility, actions |
| ConfirmDialog | 10 | 3 | confirm, callbacks, styling |
| ItemsTable | 18 | 4 | rendering, sorting, selection, pagination |
| ItemsTree | 15 | 4 | tree, expansion, selection, search |
| **TOTAL** | **134** | **32** | **Complete component coverage** |

---

## 🎯 Frontend Test Creation Strategy

### Phase 1A: Basic Component Tests (Days 1-2)
1. Button component tests
2. Header component tests
3. Dialog component tests

### Phase 1B: Form Component Tests (Days 3-4)
1. CreateItemForm tests
2. CreateProjectForm tests
3. CreateLinkForm tests

### Phase 1C: Complex Component Tests (Days 5-6)
1. ItemsTable tests
2. ItemsTree tests
3. Sidebar tests

### Phase 1D: Integration & Polish (Days 7)
1. Full test execution
2. Coverage reporting
3. Documentation

---

## ✅ Quality Checklist for Frontend Tests

- [ ] All 10 component test files created
- [ ] Each test file has 12-18 test cases
- [ ] Rendering tests verify component appears
- [ ] User interaction tests use userEvent
- [ ] Form tests include validation scenarios
- [ ] Accessibility tests verify ARIA attributes
- [ ] Mock data matches expected component props
- [ ] Error states are tested
- [ ] Loading states are tested
- [ ] Empty states are tested
- [ ] All tests pass (100% green)
- [ ] Coverage reports generated

---

## 📚 Resources for Frontend Testing

### Existing Component Reference
- Check `frontend/apps/web/src/components/` for actual component implementations
- Review props interfaces in component files
- Check existing mock data in `src/mocks/` for realistic test data

### Testing Best Practices
1. **Use React Testing Library principles** - Test behavior, not implementation
2. **Write descriptive test names** - Clear intent of what is being tested
3. **Keep tests focused** - One behavior per test
4. **Mock external dependencies** - API calls, hooks, context
5. **Avoid testing implementation details** - Focus on user experience
6. **Use semantic queries** - getByRole, getByLabelText over getByTestId

### Common Pitfalls to Avoid
- ❌ Testing React internals instead of user behavior
- ❌ Using container.querySelector instead of semantic queries
- ❌ Testing CSS/styling directly
- ❌ Creating overly brittle tests
- ❌ Missing accessibility testing

---

## 🚀 Execution Plan

### Step 1: Setup Frontend Test Environment
```bash
# Verify testing dependencies are installed
npm list @testing-library/react @testing-library/user-event
```

### Step 2: Create Test Files
```bash
# Create frontend test files directory if needed
mkdir -p frontend/apps/web/src/__tests__/components

# Create individual test files
touch frontend/apps/web/src/components/Button.test.tsx
# ... etc for all 10 components
```

### Step 3: Implement Tests
- Follow the test patterns outlined above
- Use mock data from existing fixtures
- Reference component implementations
- Ensure tests cover all user workflows

### Step 4: Run & Validate
```bash
# Run frontend tests
npm run test -- frontend/apps/web

# Generate coverage
npm run test:coverage -- frontend/apps/web
```

---

## 📋 Test File Template

```typescript
/**
 * @file Component name tests
 * @description Test cases for [Component] component covering rendering,
 * user interactions, form validation, accessibility, and edge cases.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ComponentName } from '@/components/ComponentName';

describe('ComponentName', () => {
  beforeEach(() => {
    // Setup before each test
  });

  describe('Rendering', () => {
    it('renders successfully', () => {
      render(<ComponentName />);
      // assertions
    });
  });

  describe('User Interactions', () => {
    it('handles user actions', async () => {
      render(<ComponentName />);
      // user actions and assertions
    });
  });

  describe('Validation', () => {
    it('validates input correctly', () => {
      render(<ComponentName />);
      // validation assertions
    });
  });

  describe('Accessibility', () => {
    it('meets accessibility standards', () => {
      render(<ComponentName />);
      // accessibility assertions
    });
  });
});
```

---

## 📞 Handoff Notes

### For Frontend Test Developer
1. Each component should have 12-18 test cases
2. Follow React Testing Library best practices
3. Test user workflows, not implementation
4. Include accessibility testing
5. Use semantic queries (getByRole, getByLabelText)
6. Mock external dependencies appropriately
7. Keep tests fast and isolated
8. Document complex test scenarios

### For Frontend Component Authors
- Component props should be clearly defined
- ARIA attributes should be present
- Semantic HTML should be used
- Components should be testable (avoid implementation details)

---

## ✨ Success Criteria

✅ **Phase 1 Frontend Completion = 10 test files with 134+ test cases**

Upon completion:
- All 10 component tests pass (100% green)
- Coverage > 80% for all components
- All accessibility requirements met
- Documentation complete
- Ready for Phase 2 integration testing

---

**Next Steps:** Create 10 frontend component test files to reach Phase 1 completion
**Target Completion:** End of Week 2
**Total Phase 1 Achievement:** 12 backend + 10 frontend = 22 files, 555+ test cases
