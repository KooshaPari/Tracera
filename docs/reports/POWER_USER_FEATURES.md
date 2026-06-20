# Power User Productivity Features Guide

This guide documents the keyboard shortcuts, undo/redo, and bulk selection features that enhance user productivity.

## Overview

The power user features include:

1. **Global Keyboard Shortcuts** - Quick access to common actions
2. **Undo/Redo System** - Full history management with state restoration
3. **Bulk Selection** - Select multiple items and perform batch operations
4. **Keyboard Shortcuts Help Modal** - Discoverable shortcut documentation

## Quick Start

### 1. Using Keyboard Shortcuts

Import the hook and define shortcuts:

```typescript
import {
  useKeyboardShortcuts,
  type KeyboardShortcutAction,
} from "@/hooks";

const shortcuts: KeyboardShortcutAction[] = [
  {
    key: "n",
    meta: true, // Cmd on Mac, Ctrl on Windows
    description: "Create new item",
    category: "editing",
    action: () => {
      // Handle Cmd+N
    },
  },
  {
    key: "f",
    meta: true,
    description: "Search",
    category: "navigation",
    action: () => {
      // Handle Cmd+F
    },
  },
];

function MyComponent() {
  const {
    isShortcutsModalOpen,
    setIsShortcutsModalOpen,
    allShortcuts,
  } = useKeyboardShortcuts(shortcuts);

  return (
    <>
      {/* Your component UI */}
      <KeyboardShortcutsModal
        isOpen={isShortcutsModalOpen}
        onClose={() => setIsShortcutsModalOpen(false)}
        shortcuts={allShortcuts}
      />
    </>
  );
}
```

### 2. Using Undo/Redo

Manage state with full undo/redo support:

```typescript
import { useUndoRedo } from "@/hooks";

function MyComponent() {
  interface State {
    items: string[];
    count: number;
  }

  const {
    state,
    setState,
    undo,
    redo,
    canUndo,
    canRedo,
    history,
  } = useUndoRedo<State>({
    items: [],
    count: 0,
  });

  const addItem = (item: string) => {
    setState(
      {
        items: [...state.items, item],
        count: state.count + 1,
      },
      `Added "${item}"`, // Optional description
    );
  };

  return (
    <div>
      <button onClick={undo} disabled={!canUndo}>
        Undo (Cmd+Z)
      </button>
      <button onClick={redo} disabled={!canRedo}>
        Redo (Cmd+Shift+Z)
      </button>
      {/* ... */}
    </div>
  );
}
```

### 3. Using Bulk Selection

Manage multiple item selection:

```typescript
import { useBulkSelection } from "@/hooks";
import { BulkActionToolbar } from "@/components";

function ItemsList() {
  const bulkSelection = useBulkSelection();
  const [items, setItems] = useState<Item[]>([]);

  const handleDelete = async () => {
    const idsToDelete = bulkSelection.selectedIds;
    await deleteItems(idsToDelete);
    setItems(items.filter((item) => !idsToDelete.includes(item.id)));
    bulkSelection.deselectAll();
  };

  return (
    <>
      <div>
        {items.map((item) => (
          <div key={item.id}>
            <input
              type="checkbox"
              checked={bulkSelection.isSelected(item.id)}
              onChange={() => bulkSelection.toggle(item.id)}
            />
            {item.title}
          </div>
        ))}
      </div>

      <BulkActionToolbar
        selectedCount={bulkSelection.count}
        totalCount={items.length}
        onSelectAll={() =>
          bulkSelection.selectAll(items.map((item) => item.id))
        }
        onSelectNone={bulkSelection.deselectAll}
        actions={[
          {
            id: "delete",
            label: "Delete",
            icon: <Trash2 />,
            action: handleDelete,
            variant: "destructive",
          },
        ]}
      />
    </>
  );
}
```

## Keyboard Shortcuts Reference

### Global Shortcuts

| Shortcut | Action                   | Category   |
| -------- | ------------------------ | ---------- |
| `Cmd+K`  | Open command palette     | System     |
| `Cmd+N`  | Create new item          | Editing    |
| `Cmd+F`  | Search/Focus search      | Navigation |
| `/`      | Focus search (slash key) | Navigation |
| `?`      | Show shortcuts help      | System     |

### Editing Shortcuts

| Shortcut      | Action |
| ------------- | ------ |
| `Cmd+Z`       | Undo   |
| `Cmd+Shift+Z` | Redo   |

### Selection Shortcuts

| Shortcut | Action      | Context    |
| -------- | ----------- | ---------- |
| `Cmd+A`  | Select all  | Items view |
| `Delete` | Bulk delete | Items view |

## API Reference

### useKeyboardShortcuts Hook

```typescript
const result = useKeyboardShortcuts(
  shortcuts: KeyboardShortcutAction[],
  enabled?: boolean,
);
```

**Returns:**

- `isShortcutsModalOpen: boolean` - Modal visibility state
- `setIsShortcutsModalOpen: (open: boolean) => void` - Control modal
- `allShortcuts: KeyboardShortcut[]` - All registered shortcuts
- `register: (shortcut: KeyboardShortcutAction) => () => void` - Dynamically add shortcut
- `unregister: (id: string) => void` - Remove shortcut

**Types:**

```typescript
interface KeyboardShortcutAction extends KeyboardShortcut {
  action: () => void;
  enabled?: boolean;
}

interface KeyboardShortcut {
  key: string;
  meta?: boolean; // Cmd on Mac, Ctrl on Windows
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  description: string;
  category: 'navigation' | 'selection' | 'editing' | 'system';
  context?: string; // Optional context info
}
```

### useUndoRedo Hook

```typescript
const result = useUndoRedo<T>(initialState: T);
```

**Returns:**

- `state: T` - Current state
- `setState: (newState: T, description?: string) => void` - Update state
- `undo: () => void` - Go to previous state
- `redo: () => void` - Go to next state
- `canUndo: boolean` - Can undo flag
- `canRedo: boolean` - Can redo flag
- `history: HistoryEntry<T>[]` - Full history
- `currentIndex: number` - Current position in history
- `clear: () => void` - Clear history and reset

**HistoryEntry:**

```typescript
interface HistoryEntry<T> {
  state: T;
  description?: string;
  timestamp: number;
}
```

### useBulkSelection Hook

```typescript
const result = useBulkSelection();
```

**Returns:**

- `selected: Set<string>` - Selected item IDs set
- `selectedIds: string[]` - Selected item IDs array
- `isSelected: (id: string) => boolean` - Check if item selected
- `toggle: (id: string) => void` - Toggle item selection
- `selectAll: (ids: string[]) => void` - Select all items
- `deselectAll: () => void` - Deselect all items
- `count: number` - Number of selected items
- `hasSelection: boolean` - Has any selection flag
- `clear: () => void` - Clear selection

### BulkActionToolbar Component

```typescript
<BulkActionToolbar
  selectedCount={number}
  totalCount={number}
  onSelectAll={() => {}}
  onSelectNone={() => {}}
  actions={BulkAction[]}
  loading={boolean}
  onActionComplete={(actionId: string) => {}}
/>
```

**BulkAction:**

```typescript
interface BulkAction {
  id: string;
  label: string;
  icon: React.ReactNode;
  action: (selectedIds: string[]) => Promise<void> | void;
  variant?: 'default' | 'destructive';
  disabled?: boolean;
}
```

### KeyboardShortcutsModal Component

```typescript
<KeyboardShortcutsModal
  isOpen={boolean}
  onClose={() => {}}
  shortcuts={KeyboardShortcut[]}
/>
```

## formatKeyboardShortcut Utility

Format keyboard shortcuts for display:

```typescript
import { formatKeyboardShortcut } from '@/hooks';

const formatted = formatKeyboardShortcut({
  key: 'z',
  meta: true,
  shift: true,
  description: 'Redo',
  category: 'editing',
});

console.log(formatted); // "⌘+Shift+Z"
```

## Best Practices

### 1. Keyboard Shortcut Design

- **Use standard conventions:**
  - `Cmd+Z` / `Cmd+Shift+Z` for undo/redo
  - `Cmd+N` for new
  - `Cmd+F` for search
  - `Cmd+S` for save

- **Avoid conflicts:** Don't override browser shortcuts
- **Provide feedback:** Show toast notifications for actions
- **Document shortcuts:** Always provide help modal with `?`

### 2. Undo/Redo Best Practices

```typescript
// ✓ GOOD: Provide descriptions for clarity
setState(newState, `Added item "${item.title}"`);

// ✓ GOOD: Group related changes
const startIndex = state.items.length;
// ... multiple item additions ...
setState(newState, `Added ${addedCount} items`);

// ✗ AVOID: No descriptions make history unclear
setState(newState);
```

### 3. Bulk Selection Best Practices

```typescript
// ✓ GOOD: Confirm destructive actions
const handleDelete = async () => {
  if (!confirm(`Delete ${bulkSelection.count} items?`)) {
    return;
  }
  // ... proceed with deletion
};

// ✓ GOOD: Show progress for slow operations
const handleDelete = async () => {
  toast.loading('Deleting items...');
  try {
    await deleteItems(bulkSelection.selectedIds);
    toast.success(`Deleted ${bulkSelection.count} items`);
  } catch (error) {
    toast.error('Failed to delete items');
  }
};

// ✓ GOOD: Clear selection after action
await deleteItems(ids);
bulkSelection.deselectAll();
toast.success('Items deleted');
```

## Testing

All hooks and components include comprehensive tests:

```typescript
// Tests for useUndoRedo
- Initialization with initial state
- State changes with descriptions
- Undo/redo operations
- History management
- Clear functionality

// Tests for useBulkSelection
- Toggle individual items
- Select/deselect all
- Count tracking
- Selection state queries

// Tests for useKeyboardShortcuts
- Shortcut registration/unregistration
- Category grouping
- Modal open/close
- Formatting shortcuts

// Tests for BulkActionToolbar
- Rendering when items selected
- Action execution
- Select all/none
- Loading state handling
```

Run tests with:

```bash
bun run test:run -- useUndoRedo.test.ts
bun run test:run -- useBulkSelection.test.ts
bun run test:run -- useKeyboardShortcuts.test.ts
bun run test:run -- BulkActionToolbar.test.tsx
```

## Examples

See `PowerUserExample.tsx` for a complete working example demonstrating:

- All keyboard shortcuts
- Undo/redo with toast notifications
- Bulk selection with toolbar
- Shortcuts help modal

## Accessibility

All components include:

- Proper ARIA labels
- Keyboard navigation support
- Screen reader announcements
- Focus management
- High contrast support

## Performance Considerations

- Shortcuts registry uses local state to minimize re-renders
- Bulk selection uses Set for O(1) lookups
- History is optimized for typical use (10-50 states)
- Modal only renders when open

## Troubleshooting

### Shortcuts not working

1. Check `enabled` flag is `true`
2. Verify key combinations don't conflict with OS/browser
3. Ensure component is mounted when shortcut is defined
4. Check browser console for errors

### Undo/redo not restoring state

1. Ensure state is immutable (use new objects)
2. Check descriptions are provided for debugging
3. Verify `setState` is being called correctly
4. Use Redux DevTools for history inspection

### Bulk selection toolbar not appearing

1. Verify `selectedCount > 0`
2. Check `onSelectAll`/`onSelectNone` handlers
3. Ensure `actions` array is not empty
4. Check z-index if hidden behind other elements

## Future Enhancements

- [ ] Persistent undo history (LocalStorage)
- [ ] Keyboard shortcut customization UI
- [ ] Advanced bulk actions (archive, move, etc.)
- [ ] Shortcut conflict detection
- [ ] Analytics for shortcut usage
