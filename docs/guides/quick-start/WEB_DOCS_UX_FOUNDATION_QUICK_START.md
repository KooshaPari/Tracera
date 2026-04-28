# UX Foundation Components - Quick Start Guide

## Copy-Paste Templates

### 1. Single Item Delete

```tsx
import { useState } from 'react';
import { ConfirmationDialog } from '@/components/ui/confirmation-dialog';
import { useConfirmedDelete } from '@/hooks/useConfirmedDelete';
import { Button } from '@tracertm/ui';
import { Trash2 } from 'lucide-react';

function DeleteItemButton({ itemId, itemName }: Props) {
  const { dialogOpen, pendingDelete, isDeleting, requestDelete, executeDelete, cancelDelete } =
    useConfirmedDelete();

  return (
    <>
      <Button
        variant='ghost'
        size='sm'
        onClick={() =>
          requestDelete({
            id: itemId,
            name: itemName,
            title: `Delete "${itemName}"?`,
            description: 'This action cannot be undone.',
            severity: 'danger',
          })
        }
      >
        <Trash2 className='h-4 w-4' />
      </Button>

      <ConfirmationDialog
        open={dialogOpen}
        onOpenChange={(open) => {
          if (!open) cancelDelete();
        }}
        title={pendingDelete?.title || 'Delete?'}
        description={pendingDelete?.description || ''}
        isLoading={isDeleting}
        onConfirm={() =>
          executeDelete(async () => {
            await deleteItemAPI(pendingDelete!.id);
          })
        }
      />
    </>
  );
}
```

### 2. Bulk Delete

```tsx
import { BulkConfirmationDialog } from '@/components/ui/confirmation-dialog';
import { useConfirmedBulkDelete } from '@/hooks/useConfirmedDelete';

function BulkDeleteToolbar({ selectedIds }: Props) {
  const { dialogOpen, pendingDelete, isDeleting, requestDelete, executeDelete, cancelDelete } =
    useConfirmedBulkDelete();

  return (
    <>
      <Button
        onClick={() =>
          requestDelete({
            count: selectedIds.length,
            itemType: 'items',
          })
        }
      >
        Delete {selectedIds.length}
      </Button>

      <BulkConfirmationDialog
        open={dialogOpen}
        onOpenChange={(open) => {
          if (!open) cancelDelete();
        }}
        actionType='delete'
        itemCount={pendingDelete?.count || 0}
        isLoading={isDeleting}
        onConfirm={() =>
          executeDelete(async () => {
            await bulkDeleteAPI(selectedIds);
          })
        }
      />
    </>
  );
}
```

### 3. Empty State

```tsx
import { NoItemsEmptyState, NoSearchResultsEmptyState } from '@/components/ui/empty-state';
import { Plus } from 'lucide-react';

function ItemsList() {
  const { items, searchQuery } = useItems();

  if (items.length === 0 && !searchQuery) {
    return (
      <NoItemsEmptyState
        itemType='requirements'
        actions={[
          {
            label: 'Create First Item',
            icon: <Plus className='h-4 w-4' />,
            onClick: () => openCreateDialog(),
          },
        ]}
        helpText='Keyboard: Cmd+K'
      />
    );
  }

  if (items.length === 0 && searchQuery) {
    return (
      <NoSearchResultsEmptyState
        query={searchQuery}
        actions={[
          {
            label: 'Clear Search',
            onClick: () => setSearchQuery(''),
          },
        ]}
      />
    );
  }

  return <ItemsTable items={items} />;
}
```

### 4. With Error Handling

```tsx
const performDelete = async () => {
  try {
    await deleteItemAPI(pendingDelete!.id);
    // Toast handled automatically by hook
  } catch (error) {
    // Error toast handled automatically
    throw error;
  }
};

await executeDelete(performDelete);
```

## Common Patterns

### Custom Error Message

```tsx
requestDelete({
  id: item.id,
  name: item.title,
  errorMessage: 'Could not delete item. Please try again.',
});
```

### Custom Success Message

```tsx
requestDelete({
  id: item.id,
  name: item.title,
  successMessage: `"${item.title}" has been moved to trash`,
});
```

### Different Severity Levels

```tsx
// For casual deletes
requestDelete({ ..., severity: "warning" })

// For important deletes
requestDelete({ ..., severity: "danger" })

// For critical data
requestDelete({ ..., severity: "critical" })
```

### Bulk Operations (Non-Delete)

```tsx
<BulkConfirmationDialog
  actionType='archive' // or "status-change", "assign"
  itemCount={selectedCount}
  onConfirm={performArchive}
/>
```

## Hook Options

```tsx
useConfirmedDelete({
  showSuccessToast: true, // Auto show success
  showErrorToast: true, // Auto show errors
  successToastDuration: 3000, // Toast duration ms
});
```

## Import Checklist

```tsx
// Components
import { ConfirmationDialog, BulkConfirmationDialog } from '@/components/ui/confirmation-dialog';
import {
  EmptyState,
  NoItemsEmptyState,
  NoSearchResultsEmptyState,
  FilteredEmptyState,
  ErrorEmptyState,
} from '@/components/ui/empty-state';

// Hooks
import { useConfirmedDelete, useConfirmedBulkDelete } from '@/hooks/useConfirmedDelete';

// Icons
import { Trash2, Plus } from 'lucide-react';

// Toast (sonner)
import { toast } from 'sonner';
```

## Test Examples

```tsx
// Test confirmation dialog appears
test('shows delete confirmation', async ({ page }) => {
  await page.click('[data-testid="delete-button"]');
  await expect(page.locator('text=Delete item?')).toBeVisible();
});

// Test delete execution
test('deletes item after confirmation', async ({ page }) => {
  await page.click('[data-testid="delete-button"]');
  await page.click('button:has-text("Delete")');
  await expect(page.locator('text=deleted')).toBeVisible();
});

// Test empty state
test('shows empty state when no items', async ({ page }) => {
  await page.goto('/items');
  await expect(page.locator('text=No items yet')).toBeVisible();
});
```

## Styling Customization

```tsx
// Override colors
<ConfirmationDialog
  severity="critical"
  // Styles:
  // warning: amber colors
  // danger: red colors
  // critical: rose colors
/>

// Custom button variants
<Button variant="destructive">Delete</Button>
<Button variant="outline">Cancel</Button>

// Empty state variants
<EmptyState
  variant="compact"  // Smaller padding
  variant="full"     // Large spacing
  iconSize="sm"      // h-12 w-12
  iconSize="md"      // h-16 w-16
  iconSize="lg"      // h-24 w-24
/>
```

## Accessibility Keyboard Shortcuts

- `Tab` - Navigate between buttons
- `Enter` - Confirm action
- `Escape` - Cancel/close dialog
- `Space` - Activate button

## Mobile Considerations

- Full-width dialogs on mobile
- Touch-friendly button sizes (min 44px)
- Stacked button layout on small screens
- Scrollable content on small viewport

## Performance Tips

1. Memoize callbacks with `useCallback`
2. Use `useMemo` for expensive computations
3. Split large lists with virtualization
4. Lazy load heavy components
5. Use Next.js Image for images

## Troubleshooting

**Dialog not opening?**

```tsx
// Check:
- open prop is true
- onOpenChange callback is called
- Component is not hidden with CSS
```

**Toast not showing?**

```tsx
// Check:
- Toaster is in root layout
- import { toast } from "sonner"
- successMessage or errorMessage is set
```

**Empty state not displaying?**

```tsx
// Check order:
1. Check if loading
2. Check if items.length === 0
3. Check if searchQuery !== ""
4. Check if filters.length > 0
```

## Quick Wins

- [ ] Add delete confirmations to ItemsTableView
- [ ] Add empty states to ProjectsListView
- [ ] Add bulk delete to search results
- [ ] Add delete confirmation to project detail
- [ ] Add undo for trash operations

## Next Steps

1. Copy template matching your use case
2. Adjust item type names and messages
3. Test with E2E tests
4. Verify accessibility (keyboard nav, screen reader)
5. Collect user feedback

## Documentation Links

- Full guide: `/docs/UX_FOUNDATION_IMPLEMENTATION.md`
- Examples: `/src/components/DeleteOperationDemo.tsx`
- Tests: `/src/__tests__/components/`
