# UX Foundation Components Implementation Guide

## Overview

This guide shows how to implement confirmation dialogs and empty states across all views to prevent accidental deletions and provide consistent user feedback.

## Components Created

### 1. ConfirmationDialog Component
**File:** `/src/components/ui/confirmation-dialog.tsx`

The primary component for all destructive operations. Provides:
- Customizable title, description, and action text
- Severity levels (warning, danger, critical) with visual styling
- Loading states with spinner
- Context information (e.g., "5 related items")
- Keyboard support and accessibility

#### Usage Example

```tsx
import { ConfirmationDialog } from "@/components/ui/confirmation-dialog";
import { useState } from "react";

function ItemDeleteButton() {
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await deleteItemAPI(itemId);
      setConfirmOpen(false);
      toast.success("Item deleted");
    } catch (error) {
      toast.error("Failed to delete");
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <>
      <Button onClick={() => setConfirmOpen(true)}>Delete</Button>

      <ConfirmationDialog
        open={confirmOpen}
        onOpenChange={setConfirmOpen}
        title="Delete Item?"
        description="This action cannot be undone. The item will be permanently deleted."
        confirmText="Delete"
        severity="danger"
        isLoading={isDeleting}
        onConfirm={handleDelete}
        context="1 item will be deleted"
        showWarning={true}
      />
    </>
  );
}
```

### 2. BulkConfirmationDialog Component
**File:** `/src/components/ui/confirmation-dialog.tsx`

Specialized version for bulk operations:
- Automatically calculates plural forms
- Supports different action types (delete, archive, status-change, assign)
- Shows item count context
- Adapts severity based on action

#### Usage Example

```tsx
import { BulkConfirmationDialog } from "@/components/ui/confirmation-dialog";
import { useConfirmedBulkDelete } from "@/hooks/useConfirmedDelete";

function BulkDeleteToolbar() {
  const selectedIds = useSelection((s) => s.selectedIds);
  const {
    dialogOpen,
    pendingDelete,
    isDeleting,
    requestDelete,
    executeDelete,
  } = useConfirmedBulkDelete();

  const handleBulkDelete = () => {
    requestDelete({
      count: selectedIds.length,
      itemType: "items",
    });
  };

  const performDelete = async () => {
    await bulkDeleteAPI(selectedIds);
    clearSelection();
  };

  return (
    <>
      <Button onClick={handleBulkDelete}>Delete {selectedIds.length}</Button>

      <BulkConfirmationDialog
        open={dialogOpen}
        onOpenChange={(open) => {
          if (!open) cancelDelete();
        }}
        actionType="delete"
        itemCount={pendingDelete?.count || 0}
        isLoading={isDeleting}
        onConfirm={() => executeDelete(performDelete)}
      />
    </>
  );
}
```

### 3. EmptyState Component
**File:** `/src/components/ui/empty-state.tsx`

Friendly empty states for all list views. Includes:
- Icon, title, and description
- Optional action buttons
- Multiple specialized variants
- Animation support
- Responsive layout

#### Usage Example

```tsx
import { EmptyState, NoItemsEmptyState } from "@/components/ui/empty-state";
import { Plus, Search } from "lucide-react";

function ItemsList() {
  const { items, isLoading, searchQuery } = useItems();

  // Empty with no filters
  if (items.length === 0 && !searchQuery) {
    return (
      <NoItemsEmptyState
        itemType="requirements"
        actions={[
          {
            label: "Create First Item",
            onClick: () => openCreateDialog(),
          },
        ]}
        helpText="Keyboard shortcut: Cmd+K"
      />
    );
  }

  // No search results
  if (items.length === 0 && searchQuery) {
    return (
      <NoSearchResultsEmptyState
        query={searchQuery}
        actions={[
          {
            label: "Clear Search",
            onClick: () => setSearchQuery(""),
          },
        ]}
      />
    );
  }

  return <ItemsTable items={items} />;
}
```

### 4. useConfirmedDelete Hook
**File:** `/src/hooks/useConfirmedDelete.ts`

Manages delete operation state and UX:
- Dialog state management
- Success/error toast handling
- Loading state tracking
- Support for both single and bulk deletes

#### Hook API

```tsx
const {
  // State
  dialogOpen,           // Is dialog open
  pendingDelete,        // Current delete config
  isDeleting,          // Is delete in progress

  // Actions
  requestDelete,       // Show confirmation dialog
  executeDelete,       // Execute delete with handler
  cancelDelete,        // Cancel and close dialog
  closeDialog,         // Close without side effects
} = useConfirmedDelete({
  showSuccessToast: true,
  showErrorToast: true,
  successToastDuration: 3000,
});
```

#### Complete Example

```tsx
function ListViewWithDelete() {
  const {
    dialogOpen,
    pendingDelete,
    isDeleting,
    requestDelete,
    executeDelete,
    cancelDelete,
  } = useConfirmedDelete();

  const handleDeleteClick = (item) => {
    requestDelete({
      id: item.id,
      name: item.title,
      title: `Delete "${item.title}"?`,
      description: "This action cannot be undone.",
      confirmText: "Delete",
      successMessage: `${item.title} deleted`,
      severity: "danger",
    });
  };

  const performDelete = async () => {
    await deleteItemAPI(pendingDelete.id);
  };

  return (
    <>
      <List>
        {items.map((item) => (
          <ListItem key={item.id}>
            <span>{item.title}</span>
            <Button onClick={() => handleDeleteClick(item)}>Delete</Button>
          </ListItem>
        ))}
      </List>

      <ConfirmationDialog
        open={dialogOpen}
        onOpenChange={(open) => {
          if (!open) cancelDelete();
        }}
        title={pendingDelete?.title}
        description={pendingDelete?.description}
        confirmText={pendingDelete?.confirmText}
        severity={pendingDelete?.severity}
        isLoading={isDeleting}
        onConfirm={() => executeDelete(performDelete)}
      />
    </>
  );
}
```

## Implementation Checklist

### Step 1: Add Confirmation to Single Item Deletes

For each view/component with delete buttons:

```tsx
// Before
const handleDelete = async (id: string) => {
  await deleteItemAPI(id);
  toast.success("Deleted");
};

// After
const {
  dialogOpen,
  pendingDelete,
  isDeleting,
  requestDelete,
  executeDelete,
  cancelDelete,
} = useConfirmedDelete();

const handleDeleteClick = (item) => {
  requestDelete({
    id: item.id,
    name: item.title,
    title: `Delete "${item.title}"?`,
    description: "This action cannot be undone.",
    severity: "danger",
  });
};

const performDelete = async () => {
  await deleteItemAPI(pendingDelete.id);
};

// In JSX
<Button onClick={() => handleDeleteClick(item)}>
  <Trash2 className="h-4 w-4" />
</Button>

<ConfirmationDialog
  open={dialogOpen}
  onOpenChange={(open) => {
    if (!open) cancelDelete();
  }}
  title={pendingDelete?.title}
  description={pendingDelete?.description}
  isLoading={isDeleting}
  onConfirm={() => executeDelete(performDelete)}
/>
```

### Step 2: Add Empty States to All Lists

For each view showing a list:

```tsx
// Check for empty state conditions in order
if (isLoading) {
  return <LoadingSkeleton />;
}

if (items.length === 0 && searchQuery !== "" && filters.length === 0) {
  return (
    <NoItemsEmptyState
      itemType="requirements"
      actions={[
        { label: "Create Item", onClick: createItem },
      ]}
    />
  );
}

if (items.length === 0 && searchQuery !== "") {
  return (
    <NoSearchResultsEmptyState
      query={searchQuery}
      actions={[
        { label: "Clear Search", onClick: clearSearch },
      ]}
    />
  );
}

if (items.length === 0 && filters.length > 0) {
  return (
    <FilteredEmptyState
      filters={filters}
      actions={[
        { label: "Clear Filters", onClick: clearFilters },
      ]}
    />
  );
}

return <ItemsList items={items} />;
```

### Step 3: Add Bulk Operation Support

For views with multi-select:

```tsx
const [selectedItems, setSelectedItems] = useState<string[]>([]);
const {
  dialogOpen: bulkOpen,
  pendingDelete: bulkPending,
  isDeleting: bulkDeleting,
  requestDelete: requestBulkDelete,
  executeDelete: executeBulkDelete,
} = useConfirmedBulkDelete();

const handleBulkDelete = () => {
  if (selectedItems.length === 0) {
    toast.error("Select items to delete");
    return;
  }

  requestBulkDelete({
    count: selectedItems.length,
    itemType: "items",
  });
};

const performBulkDelete = async () => {
  await bulkDeleteAPI(selectedItems);
  setSelectedItems([]);
};

// In toolbar
{selectedItems.length > 0 && (
  <BulkConfirmationDialog
    open={bulkOpen}
    onOpenChange={(open) => {
      if (!open) cancelBulkDelete();
    }}
    actionType="delete"
    itemCount={selectedItems.length}
    isLoading={bulkDeleting}
    onConfirm={() => executeBulkDelete(performBulkDelete)}
  />
)}
```

## Views to Update

### Core Views (Priority 1)
- `ItemsTableView` - ✓ Delete buttons
- `ItemsKanbanView` - ✓ Delete card
- `ItemsTreeView` - ✓ Delete node
- `ProjectsListView` - ✓ Delete project
- `ItemDetailView` - ✓ Delete button
- `ProjectDetailView` - ✓ Delete button

### Secondary Views (Priority 2)
- `SearchView` - ✓ Delete from results
- `ReportsView` - ✓ Delete report
- `SettingsView` - ✓ Delete configuration
- `LinksView` - ✓ Delete link
- `TraceabilityMatrixView` - ✓ Delete item

### Supporting Components
- Table rows with inline delete
- Card components with delete
- List item with delete
- Context menus with delete option
- Bulk action toolbars

## Success Toast Implementation

All delete operations show success feedback with optional undo:

```tsx
// Simple success
toast.success("Item deleted", {
  duration: 3000,
});

// With undo option
toast.success("Item deleted", {
  description: "Item moved to trash",
  action: {
    label: "Undo",
    onClick: async () => {
      await restoreItemAPI(itemId);
      toast.success("Item restored");
    },
  },
});

// Error with retry
toast.error("Failed to delete", {
  action: {
    label: "Retry",
    onClick: () => performDelete(),
  },
});
```

## Testing

### Component Tests
- Dialog open/close states
- Confirm/cancel actions
- Loading states
- Error handling
- Accessibility features

Run tests:
```bash
bun run test:run src/__tests__/components/ConfirmationDialog.test.tsx
bun run test:run src/__tests__/components/EmptyState.test.tsx
bun run test:run src/__tests__/hooks/useConfirmedDelete.test.ts
```

### E2E Tests
```tsx
// Test delete confirmation flow
test("shows confirmation before delete", async ({ page }) => {
  await page.click('[data-testid="delete-button"]');
  await expect(page.locator("text=Delete item?")).toBeVisible();

  await page.click('button:has-text("Delete")');
  await expect(page.locator("text=deleted")).toBeVisible();
});

// Test empty state
test("shows empty state when no items", async ({ page }) => {
  await page.goto("/items");
  await expect(page.locator("text=No items yet")).toBeVisible();
});
```

## Accessibility Features

All components include:
- ARIA labels and descriptions
- Keyboard navigation (Tab, Enter, Escape)
- Focus management
- Screen reader support
- High contrast support
- Reduced motion support

Test with:
```bash
bun run test:a11y
```

## Files Created/Modified

**New Components:**
- `/src/components/ui/alert-dialog.tsx` - Radix UI wrapper
- `/src/components/ui/confirmation-dialog.tsx` - Main confirmation component
- `/src/components/ui/empty-state.tsx` - Empty state variants

**New Hooks:**
- `/src/hooks/useConfirmedDelete.ts` - Delete state management

**New Tests:**
- `/src/__tests__/components/ConfirmationDialog.test.tsx`
- `/src/__tests__/components/EmptyState.test.tsx`
- `/src/__tests__/hooks/useConfirmedDelete.test.ts`

**Demo/Reference:**
- `/src/components/DeleteOperationDemo.tsx` - Complete examples

**Modified:**
- `/src/hooks/index.ts` - Export new hooks

## Best Practices

1. **Always confirm destructive actions** - Every delete/archive should show confirmation
2. **Show success feedback** - User needs confirmation action completed
3. **Provide undo when possible** - Soft deletes can be restored
4. **Handle errors gracefully** - Show error toast with retry option
5. **Empty states everywhere** - No confusing blank screens
6. **Loading states** - Show spinner during async operations
7. **Keyboard support** - Allow Escape to cancel, Enter to confirm
8. **Accessibility first** - ARIA labels, focus management, keyboard nav

## Performance Considerations

- Components are memoized to prevent unnecessary re-renders
- Dialogs use Radix UI for efficient DOM management
- Empty states animate only on first render
- Hooks use proper dependency arrays
- No memory leaks from event listeners

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari 14+, Chrome Android)

## Troubleshooting

### Dialog not opening
- Check `open` prop is passed correctly
- Verify `onOpenChange` callback is working
- Ensure component is not hidden with `display: none`

### Toasts not showing
- Verify `<Toaster />` is rendered in root layout
- Check toast import: `import { toast } from "sonner"`
- Confirm success message in hook options

### Empty state not displaying
- Check conditions in correct order (no filters first, then search, then filtered)
- Verify items array is empty
- Check variant is "default" for basic empty state

### Accessibility issues
- Run `bun run test:a11y`
- Use keyboard to navigate (Tab, Escape, Enter)
- Check ARIA labels in DevTools
- Test with screen reader (VoiceOver, NVDA)

## Migration Path

1. Start with high-impact views (ItemsTableView, ProjectsListView)
2. Add confirmation dialogs first, then empty states
3. Test locally with E2E tests
4. Roll out incrementally to other views
5. Collect user feedback on UX
6. Iterate on copy/timing/styling
