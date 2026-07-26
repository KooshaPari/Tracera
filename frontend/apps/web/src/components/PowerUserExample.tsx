/**
 * PowerUserExample Component
 *
 * This example demonstrates how to integrate all power user productivity features:
 * - Keyboard shortcuts (Cmd+K, Cmd+N, Cmd+F, /)
 * - Undo/Redo (Cmd+Z, Cmd+Shift+Z)
 * - Bulk selection and actions
 * - Shortcuts help modal (?)
 *
 * NOTE: This is an example/documentation component. To use these features:
 * 1. Import the hooks in your component
 * 2. Set up keyboard shortcuts with useKeyboardShortcuts
 * 3. Use useBulkSelection for item selection
 * 4. Render KeyboardShortcutsModal and BulkActionToolbar
 */

import { Plus, Trash2 } from 'lucide-react';
import { useCallback, useState } from 'react';
import { toast } from 'sonner';

import type { KeyboardShortcutAction } from '@/hooks/useKeyboardShortcuts';

import { BulkActionToolbar } from '@/components/BulkActionToolbar';
import { KeyboardShortcutsModal } from '@/components/KeyboardShortcutsModal';
import { useBulkSelection } from '@/hooks/useBulkSelection';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';
import { useUndoRedo } from '@/hooks/useUndoRedo';

interface Item {
  id: string;
  title: string;
  checked: boolean;
}

interface ItemListState {
  items: Item[];
}

export function PowerUserExample() {
  const [searchQuery, setSearchQuery] = useState('');

  // Initialize undo/redo with list state
  const {
    state: listState,
    setState: setListState,
    undo,
    redo,
    canUndo,
    canRedo,
  } = useUndoRedo<ItemListState>({
    items: [
      { checked: false, id: '1', title: 'Learn Keyboard Shortcuts' },
      { checked: false, id: '2', title: 'Use Bulk Selection' },
      { checked: false, id: '3', title: 'Master Undo/Redo' },
    ],
  });

  // Bulk selection management
  const bulkSelection = useBulkSelection();

  // Define keyboard shortcuts
  const shortcuts: KeyboardShortcutAction[] = [
    {
      action: useCallback(() => {
        const newItem: Item = {
          checked: false,
          id: Date.now().toString(),
          title: 'New Item',
        };
        const newState = {
          items: [...listState.items, newItem],
        };
        setListState(newState, 'Created new item');
        toast.success('New item created');
      }, [listState, setListState]),
      category: 'editing',
      description: 'Create new item',
      key: 'n',
      meta: true,
    },
    {
      action: useCallback(() => {
        const searchInput = document.querySelector<HTMLElement>('#search-input');
        searchInput?.focus();
        toast.info('Focus on search');
      }, []),
      category: 'navigation',
      description: 'Focus search',
      key: 'f',
      meta: true,
    },
    {
      action: useCallback(() => {
        const searchInput = document.querySelector<HTMLElement>('#search-input');
        searchInput?.focus();
        setSearchQuery('/');
      }, []),
      category: 'navigation',
      description: 'Focus search with slash',
      key: '/',
    },
    {
      action: useCallback(() => {
        if (canUndo) {
          undo();
          toast.success('Undo');
        }
      }, [canUndo, undo]),
      category: 'editing',
      description: 'Undo last action',
      key: 'z',
      meta: true,
    },
    {
      action: useCallback(() => {
        if (canRedo) {
          redo();
          toast.success('Redo');
        }
      }, [canRedo, redo]),
      category: 'editing',
      description: 'Redo last action',
      key: 'z',
      meta: true,
      shift: true,
    },
    {
      action: useCallback(() => {
        bulkSelection.selectAll(listState.items.map((item) => item.id));
        toast.success(`Selected ${listState.items.length} items`);
      }, [listState.items, bulkSelection]),
      category: 'selection',
      context: 'Items view',
      description: 'Select all items',
      key: 'a',
      meta: true,
    },
    {
      action: useCallback(async () => {
        if (bulkSelection.selectedIds.length === 0) {
          toast.error('No items selected');
          return;
        }

        const newItems = listState.items.filter(
          (item) => !bulkSelection.selectedIds.includes(item.id),
        );
        setListState({ items: newItems }, `Deleted ${bulkSelection.selectedIds.length} items`);
        bulkSelection.deselectAll();
        toast.success('Items deleted');
      }, [listState, bulkSelection, setListState]),
      category: 'selection',
      description: 'Bulk delete selected items',
      key: 'Delete',
    },
  ];

  // Setup keyboard shortcuts and modal
  const { isShortcutsModalOpen, setIsShortcutsModalOpen, allShortcuts } =
    useKeyboardShortcuts(shortcuts);

  // Handle item toggle
  const toggleItem = useCallback(
    (id: string) => {
      const newItems = listState.items.map((item) =>
        item.id === id ? { ...item, checked: !item.checked } : item,
      );
      setListState({ items: newItems }, 'Toggled item');
    },
    [listState, setListState],
  );

  // Handle bulk delete
  const handleBulkDelete = useCallback(async () => {
    const newItems = listState.items.filter((item) => !bulkSelection.selectedIds.includes(item.id));
    setListState({ items: newItems }, `Deleted ${bulkSelection.selectedIds.length} items`);
    bulkSelection.deselectAll();
    toast.success(`${bulkSelection.selectedIds.length} items deleted`);
  }, [listState, bulkSelection, setListState]);

  const deleteAction = {
    action: handleBulkDelete,
    icon: <Trash2 className='h-4 w-4' />,
    id: 'delete',
    label: 'Delete',
    variant: 'destructive' as const,
  };

  const handleSelectAll = useCallback(() => {
    bulkSelection.selectAll(listState.items.map((item) => item.id));
  }, [listState.items, bulkSelection]);

  const handleSelectNone = useCallback(() => {
    bulkSelection.deselectAll();
  }, [bulkSelection]);

  // Filter items by search
  const filteredItems = listState.items.filter((item) =>
    item.title.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  return (
    <div className='mx-auto w-full max-w-2xl space-y-6 p-6'>
      {/* Header */}
      <div className='space-y-2'>
        <h1 className='text-2xl font-bold'>Power User Features Demo</h1>
        <p className='text-muted-foreground text-sm'>
          Try the keyboard shortcuts below! Press{' '}
          <kbd className='bg-muted rounded border px-2 py-1'>?</kbd> to see all shortcuts.
        </p>
      </div>

      {/* Undo/Redo Controls */}
      <div className='flex gap-2'>
        <button
          onClick={undo}
          disabled={!canUndo}
          className='bg-primary/10 text-primary rounded px-3 py-2 text-sm font-bold disabled:cursor-not-allowed disabled:opacity-50'
        >
          ↶ Undo (Cmd+Z)
        </button>
        <button
          onClick={redo}
          disabled={!canRedo}
          className='bg-primary/10 text-primary rounded px-3 py-2 text-sm font-bold disabled:cursor-not-allowed disabled:opacity-50'
        >
          ↷ Redo (Cmd+Shift+Z)
        </button>
        <button
          onClick={() => {
            setIsShortcutsModalOpen(true);
          }}
          className='bg-primary/10 text-primary hover:bg-primary/20 ml-auto rounded px-3 py-2 text-sm font-bold'
        >
          ⌨️ Shortcuts (?)
        </button>
      </div>

      {/* Search Input */}
      <div>
        <input
          id='search-input'
          type='text'
          placeholder='Search items... (Cmd+F)'
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
          }}
          className='bg-background w-full rounded border px-4 py-2'
        />
        <p className='text-muted-foreground mt-1 text-xs'>
          Try pressing <kbd className='bg-muted rounded border px-2 py-1'>/</kbd> to focus
        </p>
      </div>

      {/* Items List with Bulk Selection */}
      <div className='bg-muted/20 space-y-2 rounded-lg border p-4'>
        <div className='mb-4 flex items-center justify-between'>
          <h2 className='font-bold'>Items ({filteredItems.length})</h2>
          <button
            onClick={() => {
              const newItem: Item = {
                checked: false,
                id: Date.now().toString(),
                title: 'New Item',
              };
              const newState = {
                items: [...listState.items, newItem],
              };
              setListState(newState, 'Created new item');
              toast.success('New item created');
            }}
            className='bg-primary/10 text-primary hover:bg-primary/20 flex items-center gap-2 rounded px-3 py-1 text-sm font-bold'
          >
            <Plus className='h-4 w-4' />
            New (Cmd+N)
          </button>
        </div>

        <div className='space-y-2'>
          {filteredItems.map((item) => (
            <div
              key={item.id}
              className='bg-background hover:bg-muted/30 flex items-center gap-3 rounded p-3 transition-colors'
            >
              <input
                type='checkbox'
                checked={bulkSelection.isSelected(item.id)}
                onChange={() => {
                  bulkSelection.toggle(item.id);
                }}
                className='rounded'
              />
              <input
                type='checkbox'
                checked={item.checked}
                onChange={() => {
                  toggleItem(item.id);
                }}
                className='rounded'
              />
              <span className={item.checked ? 'text-muted-foreground line-through' : ''}>
                {item.title}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Keyboard Shortcuts Modal */}
      <KeyboardShortcutsModal
        isOpen={isShortcutsModalOpen}
        onClose={() => {
          setIsShortcutsModalOpen(false);
        }}
        shortcuts={allShortcuts}
      />

      {/* Bulk Actions Toolbar */}
      <BulkActionToolbar
        selectedCount={bulkSelection.count}
        totalCount={listState.items.length}
        onSelectAll={handleSelectAll}
        onSelectNone={handleSelectNone}
        actions={[deleteAction]}
      />

      {/* Feature Info */}
      <div className='space-y-2 rounded-lg bg-blue-50/50 p-4 text-sm dark:bg-blue-950/20'>
        <p className='font-bold'>Features Demonstrated:</p>
        <ul className='text-muted-foreground space-y-1 text-sm'>
          <li>
            ✓ <strong>Keyboard Shortcuts:</strong> Cmd+K, Cmd+N, Cmd+F, Cmd+A, /
          </li>
          <li>
            ✓ <strong>Undo/Redo:</strong> Cmd+Z, Cmd+Shift+Z with history tracking
          </li>
          <li>
            ✓ <strong>Bulk Selection:</strong> Checkboxes, select all/none
          </li>
          <li>
            ✓ <strong>Bulk Actions:</strong> Toolbar with delete action
          </li>
          <li>
            ✓ <strong>Shortcuts Modal:</strong> Press ? to view all shortcuts
          </li>
        </ul>
      </div>
    </div>
  );
}
