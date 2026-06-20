# CreateTestItemForm Component

## Overview

The `CreateTestItemForm` component is a comprehensive form for creating test items with detailed test specifications. It implements Phase 3.2 of the form system implementation plan.

## Location

```
/frontend/apps/web/src/components/forms/CreateTestItemForm.tsx
```

## Features

### Base Item Fields

- **Title** (required): Test item title
- **Description**: Optional detailed description
- **Status**: todo, in_progress, done, blocked, cancelled
- **Priority**: low, medium, high, critical
- **Owner**: Optional assignment field

### Test Specification Fields

- **Test Type** (required): unit, integration, e2e, performance, security, smoke, regression, acceptance
- **Test Framework**: Optional framework name (e.g., Vitest, Jest, Pytest)
- **Language**: Optional programming language (e.g., TypeScript, Python)
- **Oracle Type**: assertion, golden, metamorphic, property, differential
- **Coverage Type**: statement, branch, mcdc, path, condition
- **Safety Level (DO-178C)**: DAL-A through DAL-E
- **Expected Duration (ms)**: Expected test execution time
- **Critical Path**: Boolean flag for critical path tests

## Schema

The form uses Zod validation with the following schema:

```typescript
const testItemSchema = z.object({
  // Base fields
  title: z.string().min(1).max(500),
  description: z.string().max(5000).optional(),
  status: z.enum(["todo", "in_progress", "done", "blocked", "cancelled"]),
  priority: z.enum(["low", "medium", "high", "critical"]),
  owner: z.string().max(255).optional(),

  // Test spec fields
  test_type: z.enum([...]),
  test_framework: z.string().max(100).optional(),
  language: z.string().max(50).optional(),
  oracle_type: z.enum([...]).optional(),
  coverage_type: z.enum([...]).optional(),
  safety_level: z.enum([...]).optional(),
  expected_duration_ms: z.coerce.number().int().positive().optional(),
  is_critical_path: z.boolean().optional(),
});
```

## Usage

```typescript
import { CreateTestItemForm } from "@/components/forms";

function MyComponent() {
  const handleSubmit = (data: TestItemFormData) => {
    // Handle form submission
    console.log(data);
  };

  const handleCancel = () => {
    // Handle cancel action
  };

  return (
    <CreateTestItemForm
      onSubmit={handleSubmit}
      onCancel={handleCancel}
      isLoading={false}
    />
  );
}
```

## Props

```typescript
interface CreateTestItemFormProps {
  onSubmit: (data: TestItemFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}
```

## Backend Integration

The form fields match the `TestSpec` model in the backend:

- **Backend Model**: `/src/tracertm/models/item_spec.py` - `TestSpec` class
- **Backend Schema**: `/src/tracertm/schemas/item_spec.py` - `TestSpecCreate`

Key backend fields mapped:

- `test_type` → `TestType` enum
- `oracle_type` → `TestOracleType` enum
- `coverage_type` → `CoverageType` enum
- `safety_level` → `SafetyLevel` enum (DO-178C DAL levels)

## Form Components Used

- `FormInput` - Text input fields
- `FormSelect` - Dropdown selection fields
- `FormTextarea` - Multi-line text areas

All components use `react-hook-form` with Zod validation.

## Styling

The form uses Tailwind CSS classes and follows the application's design system:

- Modal dialog with backdrop
- Two-column grid layout for field pairs
- Responsive design (stacks on mobile)
- Accessible form controls with proper labels
- Loading states for submit button

## Validation

- Client-side validation via Zod schema
- Required fields marked with validation
- Error messages displayed inline
- Form submission disabled during loading
- Blur validation mode for better UX

## Accessibility

- Proper ARIA labels
- Modal dialog with `role="dialog"` and `aria-modal="true"`
- Keyboard navigation support
- Focus management
- Screen reader friendly error messages

## Test Coverage

Test file location: `/frontend/apps/web/src/__tests__/components/CreateTestItemForm.test.tsx`

Tests cover:

- Form rendering with all fields
- Cancel button functionality
- Required field validation
- Form submission with valid data
- Test type selection
- Critical path checkbox toggling
- Loading state display

## Export

The component is exported from the forms index:

```typescript
export { CreateTestItemForm } from './CreateTestItemForm';
```

## Related Files

- Form components: `/frontend/apps/web/src/components/forms/`
- Form index: `/frontend/apps/web/src/components/forms/index.ts`
- Test file: `/frontend/apps/web/src/__tests__/components/CreateTestItemForm.test.tsx`
