# Phase 4: CreateItemDialog - Quick Reference

## Import

```typescript
import { CreateItemDialog } from "@/components/forms";
```

## Basic Usage

```typescript
function MyView() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const projectId = useParams().projectId;
  const currentView: ViewType = "TEST";

  return (
    <>
      <button onClick={() => setDialogOpen(true)}>
        Create New Item
      </button>

      <CreateItemDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        projectId={projectId}
        defaultView={currentView}
      />
    </>
  );
}
```

## Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| open | boolean | Yes | Controls dialog visibility |
| onOpenChange | (open: boolean) => void | Yes | Callback when dialog opens/closes |
| projectId | string | Yes | Current project ID |
| defaultView | ViewType | Yes | Current view (filters available types) |

## User Flow

1. **User clicks "Create Item" button** → Dialog opens (Step 1)
2. **Step 1: Type Selection**
   - User sees grid of available item types
   - Types filtered based on current view
   - User clicks desired type → Step 2
   - Or clicks Cancel → Dialog closes
3. **Step 2: Form**
   - Type-specific form appears
   - User fills in fields
   - User clicks Submit → Item created, dialog closes
   - Or clicks Cancel → Back to Step 1

## Supported Types

- `test` - Test items
- `requirement` - Requirements
- `epic` - Epics
- `user_story`/`story` - User Stories
- `task` - Tasks
- `bug`/`defect` - Defects/Bugs

## State Management

```typescript
// In CreateItemDialog component
const [selectedType, setSelectedType] = useState<string | null>(null);
const [isSubmitting, setIsSubmitting] = useState(false);

// null = Step 1 (type selection)
// string = Step 2 (form for that type)
```

## API Integration (TODO)

Replace mock in `CreateItemDialog.tsx`:

```typescript
// Current (line 65-73)
console.log("Creating item:", {
  projectId,
  type: selectedType,
  view: defaultView,
  data,
});
await new Promise((resolve) => setTimeout(resolve, 500));

// Replace with:
const response = await apiClient.post(`/projects/${projectId}/items`, {
  type: selectedType,
  view: defaultView,
  ...data,
});

// Show success notification
toast.success(`${selectedType} created successfully`);
```

## File Locations

- **Component:** `/frontend/apps/web/src/components/forms/CreateItemDialog.tsx`
- **Tests:** `/frontend/apps/web/src/components/forms/CreateItemDialog.test.tsx`
- **Example:** `/frontend/apps/web/src/components/forms/CreateItemDialog.example.tsx`
- **Docs:** `/frontend/apps/web/src/components/forms/PHASE_4_IMPLEMENTATION.md`

## Integration Checklist

When adding to a new view:

- [ ] Import CreateItemDialog
- [ ] Add state for dialog open/close
- [ ] Add trigger button/action
- [ ] Pass correct projectId
- [ ] Pass correct defaultView
- [ ] Handle creation success (refresh data, show notification)
- [ ] Test keyboard navigation
- [ ] Test screen reader compatibility

## Common Patterns

### With TanStack Router

```typescript
import { useParams } from "@tanstack/react-router";

const { projectId } = useParams({ from: "/projects/$projectId" });
```

### With View Type

```typescript
import type { ViewType } from "@tracertm/types";

const currentView: ViewType = "TEST"; // or from route params
```

### With Data Refresh

```typescript
const { refetch } = useQuery({
  queryKey: ["items", projectId],
  queryFn: () => fetchItems(projectId),
});

// After successful creation
const handleOpenChange = (open: boolean) => {
  if (!open) {
    refetch(); // Refresh items list
  }
  setDialogOpen(open);
};
```

## Keyboard Shortcuts

- **ESC** - Close dialog / Go back to type selection
- **Enter** - Submit form (when valid)
- **Tab** - Navigate between form fields
- **Arrow Keys** - Navigate type selector grid

## Accessibility

- Dialog uses proper ARIA attributes
- Focus trap within dialog
- Keyboard navigation supported
- Screen reader announcements
- High contrast compatible

## Performance

- Lightweight component (~200 lines)
- Lazy renders forms (only when type selected)
- No unnecessary re-renders
- Fast state transitions

## Troubleshooting

### Dialog doesn't open
- Check `open` prop is true
- Check parent component state management

### Form doesn't appear after selecting type
- Check type name matches form switch case
- Check form component is imported
- Check browser console for errors

### Submit doesn't work
- Check browser console (currently logs to console)
- Replace mock with API call for production

### Types not showing
- Check `defaultView` matches view configuration
- Check ItemTypeSelector configuration
- Check `itemTypeConfig.ts`

## Next Steps

1. Replace mock API call with real endpoint
2. Add toast notifications
3. Add to relevant views
4. Add integration tests
5. Accessibility audit

## Quick Links

- [Full Implementation Docs](./PHASE_4_IMPLEMENTATION.md)
- [Usage Example](../../../frontend/apps/web/src/components/forms/CreateItemDialog.example.tsx)
- [Component Tests](../../../frontend/apps/web/src/components/forms/CreateItemDialog.test.tsx)
- [Type-Aware Node System Docs](../../../docs/TYPE_AWARE_NODE_SYSTEM.md)
