# Bulk Operations - Implementation Guide

This guide maps the E2E tests to implementation requirements. Use this to understand what features need to be built or fixed to pass the test suite.

## Overview

The bulk operations test suite validates 31 test cases across 10 functional areas. This document outlines what needs to be implemented to pass all tests.

---

## 1. Selection System Implementation

### Required Components

#### 1.1 Checkbox UI

```typescript
// Each item row should have a checkbox
<input
  type="checkbox"
  onChange={() => toggleItemSelection(item.id)}
  checked={selectedItemIds.includes(item.id)}
/>
```

**Test Coverage:** 6 tests

- Checkbox must be visible for each item
- Checkbox state must update on click
- Multiple checkboxes can be selected simultaneously

#### 1.2 Selection State Management (UIStore)

The `uiStore.ts` already has:

```typescript
selectedItemIds: string[];
toggleItemSelection: (id: string) => void;
clearSelection: () => void;
```

**Verify:**

- State updates on selection/deselection
- State persists across operations
- Clearing selection works properly

#### 1.3 Bulk Action Bar

**Required when items selected:**

```typescript
{selectedItemIds.length > 0 && (
  <div data-testid="bulk-action-bar">
    <span>{selectedItemIds.length} selected</span>
    <button onClick={handleDelete}>Delete</button>
    <button onClick={handleStatusUpdate}>Change Status</button>
    <button onClick={handleMove}>Move to Project</button>
    <button onClick={handleAddTags}>Add Tags</button>
    <button onClick={handleArchive}>Archive</button>
    <button onClick={clearSelection}>Clear Selection</button>
  </div>
)}
```

**Key Requirements:**

- Only visible when items selected
- Shows count of selected items
- All action buttons present
- Clear selection button available
- Sticky positioning (stays visible while scrolling)

#### 1.4 Select All / Deselect All

**Implementation Options:**

Option A: Header checkbox (table view)

```typescript
<input
  type="checkbox"
  checked={items.length > 0 && selectedItemIds.length === items.length}
  onChange={() => selectedItemIds.length === items.length ?
    clearSelection() : selectAllItems()}
/>
```

Option B: "Select All" button

```typescript
<button onClick={selectAllItems}>Select All</button>
```

---

## 2. Delete Operations Implementation

### Required Features

#### 2.1 Delete Button in Bulk Actions

```typescript
<button
  onClick={handleBulkDelete}
  disabled={selectedItemIds.length === 0}
>
  Delete {selectedItemIds.length > 0 && `(${selectedItemIds.length})`}
</button>
```

#### 2.2 Confirmation Dialog

```typescript
// Show dialog when delete clicked
<Dialog open={showDeleteConfirm}>
  <DialogTitle>Delete Items?</DialogTitle>
  <DialogDescription>
    Are you sure you want to delete {selectedItemIds.length} item(s)?
    This action cannot be undone.
  </DialogDescription>
  <Button onClick={confirmDelete}>Delete</Button>
  <Button onClick={cancelDelete}>Cancel</Button>
</Dialog>
```

**Test Requirements:**

- Dialog appears before deletion
- Dialog shows item count
- Confirm button deletes items
- Cancel button closes dialog without deleting
- Selection cleared after successful deletion

#### 2.3 API Integration

```typescript
async function bulkDeleteItems(ids: string[]) {
  const results = await Promise.allSettled(
    ids.map((id) => fetch(`/api/v1/items/${id}`, { method: 'DELETE' })),
  );

  return results.map((r, i) => ({
    id: ids[i],
    success: r.status === 'fulfilled' && r.value.ok,
  }));
}
```

**Requirements:**

- Call DELETE endpoint for each item
- Handle errors gracefully
- Update store after successful deletion
- Show error message if deletion fails

#### 2.4 Undo Functionality

```typescript
// After delete, show undo option
showUndoToast({
  message: 'Items deleted',
  action: 'Undo',
  onUndo: () => {
    restoreDeletedItems(deletedItems);
    showConfirmationToast('Items restored');
  },
  duration: 5000,
});
```

**Requirements:**

- Undo button visible after deletion
- Undo restores deleted items
- Undo button disappears after timeout
- Store maintains deleted item backup

---

## 3. Status Update Operations Implementation

### Required Features

#### 3.1 Status Menu Button

```typescript
<Menu>
  <MenuTrigger asChild>
    <Button>Change Status</Button>
  </MenuTrigger>
  <MenuContent>
    <MenuItem onClick={() => bulkUpdateStatus('todo')}>To Do</MenuItem>
    <MenuItem onClick={() => bulkUpdateStatus('in_progress')}>In Progress</MenuItem>
    <MenuItem onClick={() => bulkUpdateStatus('done')}>Done</MenuItem>
    <MenuItem onClick={() => bulkUpdateStatus('blocked')}>Blocked</MenuItem>
  </MenuContent>
</Menu>
```

**Test Requirements:**

- Menu appears on click
- Status options available
- Menu closes after selection
- Shows current status as active/disabled

#### 3.2 Bulk Status Update API

```typescript
async function bulkUpdateStatus(ids: string[], status: ItemStatus) {
  const results = await Promise.allSettled(
    ids.map((id) =>
      fetch(`/api/v1/items/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      }),
    ),
  );

  return results;
}
```

#### 3.3 Confirmation Feedback

```typescript
showToast({
  type: 'success',
  message: `Updated status for ${successCount} item(s)`,
  duration: 3000,
});

if (failedCount > 0) {
  showToast({
    type: 'warning',
    message: `Failed to update ${failedCount} item(s)`,
  });
}
```

---

## 4. Move to Project Operations Implementation

### Required Features

#### 4.1 Move Menu

```typescript
<Menu>
  <MenuTrigger asChild>
    <Button>Move to Project</Button>
  </MenuTrigger>
  <MenuContent>
    {projects.map(project => (
      <MenuItem
        key={project.id}
        onClick={() => bulkMoveToProject(selectedItemIds, project.id)}
      >
        {project.name}
      </MenuItem>
    ))}
  </MenuContent>
</Menu>
```

**Test Requirements:**

- Projects list loaded and displayed
- Click project moves items
- Confirmation message shown
- Items no longer visible in old project (if filtered by project)

#### 4.2 Bulk Move API

```typescript
async function bulkMoveToProject(ids: string[], projectId: string) {
  return Promise.allSettled(
    ids.map((id) =>
      fetch(`/api/v1/items/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({ project_id: projectId }),
      }),
    ),
  );
}
```

#### 4.3 State Updates

```typescript
// Update store after successful move
selectedItemIds.forEach((id) => {
  const item = getItem(id);
  updateItem(id, { projectId: newProjectId });
});
```

---

## 5. Tag Operations Implementation

### Required Features

#### 5.1 Tags Menu

```typescript
<Menu>
  <MenuTrigger asChild>
    <Button>Add Tags</Button>
  </MenuTrigger>
  <MenuContent>
    <div className="p-2">
      <input
        type="text"
        placeholder="Enter tag name"
        data-testid="tag-input"
        onKeyPress={(e) => {
          if (e.key === 'Enter') {
            bulkAddTag(selectedItemIds, e.target.value);
            e.target.value = '';
          }
        }}
      />
    </div>
  </MenuContent>
</Menu>
```

#### 5.2 Bulk Add Tags API

```typescript
async function bulkAddTag(ids: string[], tag: string) {
  return Promise.allSettled(
    ids.map((id) => {
      const item = getItem(id);
      const newTags = [...(item.tags || []), tag];
      return fetch(`/api/v1/items/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({ tags: newTags }),
      });
    }),
  );
}
```

#### 5.3 Confirmation and Undo

```typescript
showToast({
  message: `Added tag to ${successCount} item(s)`,
  action: 'Undo',
  onUndo: () => bulkRemoveTag(selectedItemIds, tag),
});
```

---

## 6. Archive Operations Implementation

### Required Features

#### 6.1 Archive Button

```typescript
<Button
  onClick={() => setShowArchiveConfirm(true)}
  disabled={selectedItemIds.length === 0}
>
  Archive
</Button>
```

#### 6.2 Archive Confirmation

```typescript
<Dialog open={showArchiveConfirm}>
  <DialogTitle>Archive Items?</DialogTitle>
  <DialogDescription>
    Archive {selectedItemIds.length} item(s)?
    You can unarchive them later.
  </DialogDescription>
  <Button onClick={confirmArchive}>Archive</Button>
  <Button onClick={cancelArchive}>Cancel</Button>
</Dialog>
```

#### 6.3 Bulk Archive API

```typescript
async function bulkArchiveItems(ids: string[]) {
  return Promise.allSettled(
    ids.map((id) =>
      fetch(`/api/v1/items/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({ archived: true }),
      }),
    ),
  );
}
```

---

## 7. Error Handling Implementation

### Required Error States

#### 7.1 Disabled Actions When No Selection

```typescript
<Button
  onClick={handleDelete}
  disabled={selectedItemIds.length === 0}
>
  Delete
</Button>
```

**Test:** Button should be disabled until items selected.

#### 7.2 Error Messages

```typescript
// On API failure
if (!response.ok) {
  showToast({
    type: 'error',
    message: 'Failed to delete items. Please try again.',
    duration: 5000,
  });
}
```

**Test Requirements:**

- Error message visible
- Error message describes what failed
- User can retry operation
- Selection remains active for retry

#### 7.3 Partial Failure Handling

```typescript
async function bulkOperation(ids, operation) {
  const results = await Promise.allSettled(ids.map((id) => operation(id)));

  const succeeded = results.filter((r) => r.status === 'fulfilled').length;
  const failed = results.filter((r) => r.status === 'rejected').length;

  if (failed > 0) {
    showToast({
      type: 'warning',
      message: `${succeeded} succeeded, ${failed} failed`,
    });
  } else {
    showToast({
      type: 'success',
      message: `${succeeded} items updated`,
    });
  }

  return results;
}
```

---

## 8. Keyboard Shortcuts Implementation

### Required Shortcuts

#### 8.1 Range Selection (Shift+Click)

```typescript
// In table/list component
function handleCheckboxChange(id: string, event: React.ChangeEvent) {
  if (event.shiftKey && lastSelectedId) {
    // Select range from lastSelectedId to current id
    const itemIds = getItemsInRange(lastSelectedId, id);
    itemIds.forEach((itemId) => {
      if (!selectedItemIds.includes(itemId)) {
        toggleItemSelection(itemId);
      }
    });
  } else {
    toggleItemSelection(id);
  }
  setLastSelectedId(id);
}
```

#### 8.2 Escape to Clear Selection

```typescript
useEffect(() => {
  function handleKeyPress(e: KeyboardEvent) {
    if (e.key === 'Escape' && selectedItemIds.length > 0) {
      clearSelection();
    }
  }

  document.addEventListener('keydown', handleKeyPress);
  return () => document.removeEventListener('keydown', handleKeyPress);
}, [selectedItemIds, clearSelection]);
```

#### 8.3 Delete Key to Delete Selected

```typescript
useEffect(() => {
  function handleKeyPress(e: KeyboardEvent) {
    if (e.key === 'Delete' && selectedItemIds.length > 0) {
      showDeleteConfirmation();
    }
  }

  document.addEventListener('keydown', handleKeyPress);
  return () => document.removeEventListener('keydown', handleKeyPress);
}, [selectedItemIds]);
```

---

## 9. UI/UX Features

### Required UI Elements

#### 9.1 Selection Counter

```typescript
{selectedItemIds.length > 0 && (
  <div className="selection-counter">
    {selectedItemIds.length} item{selectedItemIds.length !== 1 ? 's' : ''} selected
  </div>
)}
```

#### 9.2 Sticky Bulk Action Bar

```css
/* CSS */
.bulk-action-bar {
  position: sticky;
  bottom: 0;
  background: #fff;
  border-top: 1px solid #e5e7eb;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 40;
}
```

---

## 10. Store Integration

### ItemsStore Requirements

The `itemsStore.ts` already has optimistic update methods. Use these:

```typescript
// Optimistic delete
store.optimisticDelete(id);
// Then on success:
store.confirmDelete(id);
// Or on failure:
store.rollbackDelete(id, previousItem);

// Optimistic update
store.optimisticUpdate(id, { status: 'done' });
// Then on success:
store.confirmUpdate(id, updatedItem);
// Or on failure:
store.rollbackUpdate(id);
```

### UIStore Selection Management

```typescript
// Already implemented
store.toggleItemSelection(id);
store.clearSelection();
```

---

## 11. API Integration

### Required Endpoints

| Method | Endpoint            | Payload                                  |
| ------ | ------------------- | ---------------------------------------- |
| DELETE | `/api/v1/items/:id` | -                                        |
| PATCH  | `/api/v1/items/:id` | `{ status, tags, archived, project_id }` |

### Header Requirements

```typescript
// From useItems.ts - already implemented
headers: {
  "X-Bulk-Operation": "true", // Skip rate limiting
}
```

---

## 12. Testing Checklist

Before tests, verify:

- [ ] Checkbox component renders for each item
- [ ] Selection state updates in UIStore
- [ ] Bulk action bar appears when selected
- [ ] All action buttons present and working
- [ ] Delete confirmation dialog shows
- [ ] Delete API calls succeed
- [ ] Status update menu works
- [ ] Move to project option available
- [ ] Tags menu renders
- [ ] Archive button functional
- [ ] Error messages display
- [ ] Undo functionality present
- [ ] Keyboard shortcuts work
- [ ] Selection counter updates
- [ ] Bulk action bar stays visible when scrolling

---

## 13. Common Implementation Patterns

### Pattern 1: Bulk Operation with Confirmation

```typescript
function useBulkOperation(operation: string) {
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [showConfirm, setShowConfirm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  async function execute() {
    setIsLoading(true);
    try {
      const results = await Promise.allSettled(selectedIds.map((id) => performOperation(id)));

      const succeeded = results.filter((r) => r.status === 'fulfilled').length;
      showToast(`${operation} completed for ${succeeded} items`);

      setSelectedIds([]);
    } catch (error) {
      showToast(`${operation} failed: ${error.message}`, 'error');
    } finally {
      setIsLoading(false);
      setShowConfirm(false);
    }
  }

  return { selectedIds, setSelectedIds, showConfirm, setShowConfirm, execute, isLoading };
}
```

### Pattern 2: With Undo

```typescript
async function executeWithUndo(ids: string[], operation: string) {
  // Store backup
  const backup = ids.map((id) => getItem(id));

  // Execute operation
  const results = await bulkOperation(ids);

  // Show undo
  showToast({
    message: `${operation} completed`,
    action: 'Undo',
    onUndo: async () => {
      await restoreItems(backup);
      showToast('Undone', 'success');
    },
    duration: 5000,
  });
}
```

---

## 14. Debugging Tests

If tests fail:

1. **Check if elements exist:**

   ```bash
   npx playwright test --debug
   ```

   Then inspect elements in DevTools

2. **Enable verbose logging:**

   ```typescript
   // In test
   console.log('Selected items:', selectedItemIds);
   console.log('Delete button visible:', await deleteButton.isVisible());
   ```

3. **Check mock data:**
   Ensure items exist in mock with required fields

4. **Verify selectors:**
   Update selectors in tests if UI structure differs

---

## 15. Performance Considerations

### Optimizations

1. **Batch API calls** for large selections
2. **Debounce selection updates** if many clicks
3. **Use virtual scrolling** if bulk action bar hides items
4. **Implement pagination** for large item lists

### Monitoring

```typescript
// Log operation duration
const start = performance.now();
await bulkDelete(selectedIds);
const duration = performance.now() - start;
console.log(`Bulk delete took ${duration}ms for ${selectedIds.length} items`);
```

---

## Summary

To pass all 31 tests, implement:

1. ✓ Checkbox selection UI
2. ✓ Bulk action bar
3. ✓ Delete with confirmation + undo
4. ✓ Status update menu
5. ✓ Move to project menu
6. ✓ Add tags functionality
7. ✓ Archive button
8. ✓ Error handling
9. ✓ Keyboard shortcuts
10. ✓ Selection counter
11. ✓ Sticky action bar
12. ✓ Store integration

---

**Version:** 1.0
**Updated:** January 23, 2026
