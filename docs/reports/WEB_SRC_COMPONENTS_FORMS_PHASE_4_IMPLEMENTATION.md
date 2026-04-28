# Phase 4: Unified Multi-Step Item Creation Dialog

## Overview

Phase 4 of the Type-Aware Node System implements a unified dialog component that provides a consistent two-step flow for creating items of any type.

## Implementation Summary

### Files Created

1. **CreateItemDialog.tsx** - Main dialog component
   - Location: `/frontend/apps/web/src/components/forms/CreateItemDialog.tsx`
   - Purpose: Unified multi-step item creation dialog
   - Lines: 198

2. **CreateItemDialog.test.tsx** - Unit tests
   - Location: `/frontend/apps/web/src/components/forms/CreateItemDialog.test.tsx`
   - Purpose: Test coverage for the dialog component
   - Lines: 48

3. **CreateItemDialog.example.tsx** - Usage documentation
   - Location: `/frontend/apps/web/src/components/forms/CreateItemDialog.example.tsx`
   - Purpose: Example usage and documentation
   - Lines: 67

### Files Modified

1. **index.ts** - Updated exports
   - Location: `/frontend/apps/web/src/components/forms/index.ts`
   - Changes: Added exports for CreateItemDialog, ItemTypeSelector, CreateRequirementItemForm, CreateDefectItemForm

## Component Structure

### CreateItemDialog

```typescript
interface CreateItemDialogProps {
  open: boolean; // Dialog open state
  onOpenChange: (open: boolean) => void; // State change handler
  projectId: string; // Current project ID
  defaultView: ViewType; // Current view (determines available types)
}
```

### Two-Step Flow

#### Step 1: Type Selection

- Renders ItemTypeSelector component
- Shows available item types based on current view
- User selects desired item type
- Cancel button closes dialog

#### Step 2: Type-Specific Form

- Renders appropriate form based on selected type:
  - `test` → CreateTestItemForm
  - `requirement` → CreateRequirementItemForm
  - `epic` → CreateEpicItemForm
  - `user_story`/`story` → CreateUserStoryItemForm
  - `task` → CreateTaskItemForm
  - `bug`/`defect` → CreateDefectItemForm
- Cancel button returns to type selection
- Submit button creates item (currently mocked)

### State Management

```typescript
const [selectedType, setSelectedType] = useState<string | null>(null);
const [isSubmitting, setIsSubmitting] = useState(false);
```

- `selectedType`: Tracks which type is selected (null = step 1, string = step 2)
- `isSubmitting`: Prevents double submissions during API calls

## Key Features

### 1. Conditional Rendering

- Step 1: Custom dialog with ItemTypeSelector
- Step 2: Delegates to type-specific forms (which have their own dialog structure)

### 2. State Reset

- Automatically resets to step 1 when dialog closes
- Clears submitting state on close

### 3. Navigation Flow

- Forward: Type selection → Form
- Backward: Form cancel → Type selection
- Cancel from type selection → Close dialog

### 4. Form Delegation

Each type-specific form:

- Receives `onSubmit`, `onCancel`, and `isLoading` props
- Handles its own validation and field management
- Renders its own dialog structure with form content

### 5. API Integration (Mocked)

```typescript
const handleFormSubmit = async (data: unknown) => {
  setIsSubmitting(true);
  try {
    // TODO: Replace with actual API call
    console.log('Creating item:', {
      projectId,
      type: selectedType,
      view: defaultView,
      data,
    });

    // Mock API delay
    await new Promise((resolve) => setTimeout(resolve, 500));

    // Success - close dialog and reset
    handleOpenChange(false);
  } catch (error) {
    console.error('Failed to create item:', error);
    // TODO: Show error notification
  } finally {
    setIsSubmitting(false);
  }
};
```

## Usage Example

```typescript
import { CreateItemDialog } from "@/components/forms";

function MyComponent() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button onClick={() => setIsOpen(true)}>
        Create Item
      </button>

      <CreateItemDialog
        open={isOpen}
        onOpenChange={setIsOpen}
        projectId="project-123"
        defaultView="TEST"
      />
    </>
  );
}
```

## Integration Points

### Required Dependencies

- `@tracertm/types` - ViewType and other type definitions
- `ItemTypeSelector` - Type selection UI component
- Type-specific forms:
  - `CreateTestItemForm`
  - `CreateRequirementItemForm`
  - `CreateEpicItemForm`
  - `CreateUserStoryItemForm`
  - `CreateTaskItemForm`
  - `CreateDefectItemForm`

### Future Enhancements

1. **API Integration**
   - Replace console.log with actual API call to create item
   - Add proper error handling and user feedback
   - Implement optimistic updates

2. **Notifications**
   - Success notification on item creation
   - Error notification on failure
   - Loading indicator during submission

3. **Analytics**
   - Track which item types are most commonly created
   - Monitor form completion rates
   - Identify drop-off points

4. **Accessibility**
   - Add keyboard navigation between steps
   - Announce step changes to screen readers
   - Improve focus management

## Testing

### Unit Tests

See `CreateItemDialog.test.tsx` for basic component tests:

- Renders type selection when open
- Hides when closed
- Calls onOpenChange on cancel
- Shows type selector for different views

### Integration Testing Needed

- Full flow: type selection → form fill → submission
- Error handling scenarios
- State reset on various close paths
- Form validation integration

## Accessibility

### Current Implementation

- Dialog role and aria-modal attributes
- Proper heading structure (h2 with id)
- Focus trap within dialog
- Keyboard navigation (ESC to close)
- Descriptive labels and instructions

### Future Improvements

- Announce step transitions
- Better focus management between steps
- High contrast mode support
- Screen reader testing

## Performance

### Current Characteristics

- Lightweight component (~200 lines)
- Lazy renders forms only when type is selected
- No unnecessary re-renders
- Fast state transitions

### Optimization Opportunities

- Code-split type-specific forms
- Memoize form components
- Virtualize type selector for views with many types

## Documentation

- Component is fully documented with JSDoc comments
- Usage example provided in `.example.tsx`
- Props clearly defined with TypeScript interfaces
- Implementation notes in code comments

## Compliance with Phase 4 Requirements

✅ Import all type-specific forms
✅ Import ItemTypeSelector
✅ Props: open, onOpenChange, projectId, defaultView
✅ State: selectedType, isSubmitting
✅ Two-step flow implementation
✅ Dialog structure (custom, compatible with form dialogs)
✅ Form submission handling (mocked, ready for API)
✅ Close and reset on submit/cancel
✅ Updated form index.ts exports
✅ Proper TypeScript types
✅ All imports working correctly

## Next Steps

1. Integrate with actual API endpoints
2. Add to relevant views (e.g., ItemsTableView, FlowGraphView)
3. Implement notification system
4. Add comprehensive integration tests
5. Accessibility audit and improvements
6. Performance profiling with real data
