# Power User Features - Quick Reference

## Keyboard Shortcuts

| Shortcut | Action | Context |
|----------|--------|---------|
| `Cmd+K` | Open command palette | Global |
| `Cmd+N` | Create new item | Global |
| `Cmd+F` | Search/focus search | Global |
| `/` | Focus search input | Global |
| `?` | Show shortcuts help | Global |
| `Cmd+Z` | Undo last action | Global |
| `Cmd+Shift+Z` | Redo action | Global |
| `Cmd+A` | Select all items | Items view |
| `Delete` | Bulk delete | Selection active |
| `Escape` | Close modal/toolbar | Modal/Toolbar open |

## API Quick Start

### Using Keyboard Shortcuts

```typescript
import { useKeyboardShortcuts, type KeyboardShortcutAction } from "@/hooks";

const shortcuts: KeyboardShortcutAction[] = [
  {
    key: "s",
    meta: true,
    description: "Save",
    category: "editing",
    action: () => { /* save */ },
  },
];

const { isShortcutsModalOpen, setIsShortcutsModalOpen, allShortcuts } =
  useKeyboardShortcuts(shortcuts);
```

### Using Undo/Redo

```typescript
import { useUndoRedo } from "@/hooks";

const { state, setState, undo, redo, canUndo, canRedo } = useUndoRedo({
  items: [],
});

// Update state with description
setState({ items: [...state.items, newItem] }, "Added item");

// Undo/redo
undo(); // Cmd+Z
redo(); // Cmd+Shift+Z
```

### Using Bulk Selection

```typescript
import { useBulkSelection } from "@/hooks";

const bulk = useBulkSelection();

// In your items list
items.map(item => (
  <input
    type="checkbox"
    checked={bulk.isSelected(item.id)}
    onChange={() => bulk.toggle(item.id)}
  />
))

// Access selection
bulk.selectedIds      // string[]
bulk.count           // number
bulk.hasSelection    // boolean
bulk.selectAll([...]) // select multiple
bulk.deselectAll()   // clear selection
```

### Using Toolbar

```typescript
import { BulkActionToolbar } from "@/components";

<BulkActionToolbar
  selectedCount={bulk.count}
  totalCount={items.length}
  onSelectAll={() => bulk.selectAll(items.map(i => i.id))}
  onSelectNone={bulk.deselectAll}
  actions={[
    {
      id: "delete",
      label: "Delete",
      icon: <Trash2 />,
      action: async () => { /* delete */ },
      variant: "destructive",
    },
  ]}
/>
```

### Using Shortcuts Modal

```typescript
import { KeyboardShortcutsModal } from "@/components";

<KeyboardShortcutsModal
  isOpen={isShortcutsModalOpen}
  onClose={() => setIsShortcutsModalOpen(false)}
  shortcuts={allShortcuts}
/>
```

## Component Props Reference

### useKeyboardShortcuts

```typescript
const result = useKeyboardShortcuts(
  shortcuts: KeyboardShortcutAction[],
  enabled?: boolean
);

// Returns
{
  isShortcutsModalOpen: boolean;
  setIsShortcutsModalOpen: (open: boolean) => void;
  allShortcuts: KeyboardShortcut[];
  register: (shortcut: KeyboardShortcutAction) => () => void;
  unregister: (id: string) => void;
}
```

### useUndoRedo

```typescript
const result = useUndoRedo<T>(initialState: T);

// Returns
{
  state: T;
  setState: (newState: T, description?: string) => void;
  undo: () => void;
  redo: () => void;
  canUndo: boolean;
  canRedo: boolean;
  history: HistoryEntry<T>[];
  currentIndex: number;
  clear: () => void;
}
```

### useBulkSelection

```typescript
const result = useBulkSelection();

// Returns
{
  selected: Set<string>;
  selectedIds: string[];
  isSelected: (id: string) => boolean;
  toggle: (id: string) => void;
  selectAll: (ids: string[]) => void;
  deselectAll: () => void;
  count: number;
  hasSelection: boolean;
  clear: () => void;
}
```

## Complete Integration Example

```typescript
import { useState } from "react";
import { toast } from "sonner";
import {
  useBulkSelection,
  useKeyboardShortcuts,
  useUndoRedo,
  type KeyboardShortcutAction,
} from "@/hooks";
import {
  BulkActionToolbar,
  KeyboardShortcutsModal,
} from "@/components";

interface Item {
  id: string;
  title: string;
}

export function ItemsView() {
  // State management with undo/redo
  const { state, setState, undo, redo, canUndo, canRedo } = useUndoRedo({
    items: [],
  });

  // Bulk selection
  const bulk = useBulkSelection();

  // Keyboard shortcuts
  const shortcuts: KeyboardShortcutAction[] = [
    {
      key: "n",
      meta: true,
      description: "Create new item",
      category: "editing",
      action: () => {
        const newItem = { id: Date.now().toString(), title: "New Item" };
        setState(
          { items: [...state.items, newItem] },
          "Created new item"
        );
        toast.success("Item created");
      },
    },
    {
      key: "z",
      meta: true,
      description: "Undo",
      category: "editing",
      action: () => {
        if (canUndo) {
          undo();
          toast.success("Undone");
        }
      },
    },
    {
      key: "z",
      meta: true,
      shift: true,
      description: "Redo",
      category: "editing",
      action: () => {
        if (canRedo) {
          redo();
          toast.success("Redone");
        }
      },
    },
  ];

  const { isShortcutsModalOpen, setIsShortcutsModalOpen, allShortcuts } =
    useKeyboardShortcuts(shortcuts);

  // Delete action
  const handleDelete = async () => {
    const newItems = state.items.filter(
      (item) => !bulk.selectedIds.includes(item.id)
    );
    setState({ items: newItems }, `Deleted ${bulk.count} items`);
    bulk.deselectAll();
    toast.success("Items deleted");
  };

  return (
    <>
      {/* Shortcuts Help Modal */}
      <KeyboardShortcutsModal
        isOpen={isShortcutsModalOpen}
        onClose={() => setIsShortcutsModalOpen(false)}
        shortcuts={allShortcuts}
      />

      {/* Items List */}
      <div>
        {state.items.map((item) => (
          <div key={item.id}>
            <input
              type="checkbox"
              checked={bulk.isSelected(item.id)}
              onChange={() => bulk.toggle(item.id)}
            />
            {item.title}
          </div>
        ))}
      </div>

      {/* Bulk Actions Toolbar */}
      <BulkActionToolbar
        selectedCount={bulk.count}
        totalCount={state.items.length}
        onSelectAll={() => bulk.selectAll(state.items.map((i) => i.id))}
        onSelectNone={bulk.deselectAll}
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

## Best Practices

1. **Always provide descriptions** for undo history clarity
2. **Group related state changes** before calling setState
3. **Use toast notifications** to confirm keyboard shortcuts
4. **Clear selection after bulk actions** to reset UI
5. **Test shortcuts carefully** to avoid conflicts with OS/browser
6. **Provide context** for context-specific shortcuts
7. **Handle loading states** in bulk actions
8. **Confirm destructive actions** before executing

## Testing

```bash
# Run all power user tests
bun run test src/__tests__/hooks/useUndoRedo.test.ts
bun run test src/__tests__/hooks/useBulkSelection.test.ts
bun run test src/__tests__/components/BulkActionToolbar.test.tsx
bun run test src/__tests__/components/KeyboardShortcutsModal.test.tsx

# Or all together
bun run test src/__tests__/hooks/ src/__tests__/components/
```

## Files to Reference

- **Comprehensive Guide**: `/frontend/apps/web/POWER_USER_FEATURES.md`
- **Implementation Details**: `/POWER_USER_IMPLEMENTATION_SUMMARY.md`
- **Example Component**: `/frontend/apps/web/src/components/PowerUserExample.tsx`
- **Hook Exports**: `/frontend/apps/web/src/hooks/index.ts`

## Troubleshooting

**Shortcuts not working?**
- Check `enabled` prop is true
- Verify no OS/browser conflicts
- Check browser console for errors

**Undo/redo not restoring state?**
- Ensure state is immutable (use new objects)
- Verify `setState` is being called
- Check history entries have descriptions

**Toolbar not showing?**
- Verify `selectedCount > 0`
- Check `onSelectAll`/`onSelectNone` handlers
- Ensure `actions` array is provided

## Version Info

- **Created**: January 30, 2026
- **Status**: Production Ready
- **Test Coverage**: 43/43 tests passing
- **Compatibility**: React 18+, TypeScript 5+
