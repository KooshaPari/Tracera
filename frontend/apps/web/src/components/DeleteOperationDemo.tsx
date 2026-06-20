/**
 * Delete Operation Demo Component
 *
 * Shows best practices for integrating confirmation dialogs and empty states
 * into list views. This is a reference implementation.
 *
 * Copy patterns from here to implement in your own views.
 */

import { InboxIcon, Trash2 } from 'lucide-react';
import { useCallback, useState } from 'react';
import { toast } from 'sonner';

import { BulkConfirmationDialog, ConfirmationDialog } from '@/components/ui/confirmation-dialog';
import {
  EmptyState,
  FilteredEmptyState,
  NoItemsEmptyState,
  NoSearchResultsEmptyState,
} from '@/components/ui/empty-state';
import { useConfirmedBulkDelete, useConfirmedDelete } from '@/hooks/useConfirmedDelete';
import { logger } from '@/lib/logger';
import { Button } from '@tracertm/ui';

/**
 * PATTERN 1: Single Item Delete with Confirmation
 *
 * Usage in components:
 * - Item cards with delete button
 * - List items with delete action
 * - Detail views with delete button
 */
export function SingleItemDeleteExample() {
  const { dialogOpen, pendingDelete, isDeleting, requestDelete, executeDelete, cancelDelete } =
    useConfirmedDelete({
      showSuccessToast: true,
      successToastDuration: 3000,
    });

  const handleDeleteClick = (itemId: string, itemName: string) => {
    requestDelete({
      confirmText: 'Delete',
      description: 'This action cannot be undone. The item will be permanently deleted.',
      errorMessage: `Failed to delete ${itemName}`,
      id: itemId,
      name: itemName,
      severity: 'danger',
      successMessage: `${itemName} has been deleted`,
      title: `Delete "${itemName}"?`,
    });
  };

  const performDelete = async () => {
    // Your actual delete function here
    // Await deleteItemAPI(pendingDelete!.id);
    logger.info(`Deleting item: ${pendingDelete?.id}`);
  };

  return (
    <div className='space-y-4 p-6'>
      <div className='flex gap-2'>
        <Button
          variant='outline'
          onClick={() => {
            handleDeleteClick('item-123', 'Project Roadmap');
          }}
        >
          <Trash2 className='h-4 w-4' />
          Delete Item
        </Button>
      </div>

      {pendingDelete && (
        <ConfirmationDialog
          open={dialogOpen}
          onOpenChange={(open) => {
            if (!open) {
              cancelDelete();
            }
          }}
          title={pendingDelete.title ?? 'Delete?'}
          description={pendingDelete.description ?? ''}
          confirmText={pendingDelete.confirmText ?? 'Delete'}
          severity={pendingDelete.severity ?? 'danger'}
          isLoading={isDeleting}
          onConfirm={async () => executeDelete(performDelete)}
          context={pendingDelete.name}
          showWarning
        />
      )}
    </div>
  );
}

/**
 * PATTERN 2: Bulk Delete with Confirmation
 *
 * Usage in components:
 * - Table with multi-select and bulk delete
 * - Bulk operation toolbars
 * - Batch deletion endpoints
 */
export function BulkDeleteExample() {
  const [selectedItems, setSelectedItems] = useState<string[]>([]);

  const { dialogOpen, pendingDelete, isDeleting, requestDelete, executeDelete, cancelDelete } =
    useConfirmedBulkDelete({
      showSuccessToast: true,
      successToastDuration: 3000,
    });

  const handleBulkDelete = () => {
    if (selectedItems.length === 0) {
      toast.error('Select items to delete');
      return;
    }

    requestDelete({
      count: selectedItems.length,
      itemType: 'items',
      severity: 'critical',
    });
  };

  const performBulkDelete = async () => {
    // Your actual bulk delete function here
    // Await deleteItemsAPI(selectedItems);
    logger.info(`Deleting ${selectedItems.length} items:`, selectedItems);
    setSelectedItems([]);
  };

  return (
    <div className='space-y-4 p-6'>
      <div className='flex items-center gap-2'>
        <span className='text-muted-foreground text-sm'>{selectedItems.length} selected</span>
        <Button
          variant='destructive'
          onClick={handleBulkDelete}
          disabled={selectedItems.length === 0}
        >
          <Trash2 className='h-4 w-4' />
          Delete Selected
        </Button>
      </div>

      <BulkConfirmationDialog
        open={dialogOpen}
        onOpenChange={(open) => {
          if (!open) {
            cancelDelete();
          }
        }}
        actionType='delete'
        itemCount={pendingDelete?.count ?? 0}
        isLoading={isDeleting}
        onConfirm={async () => executeDelete(performBulkDelete)}
      />
    </div>
  );
}

/**
 * PATTERN 3: Empty State in List Views
 *
 * Usage in components:
 * - No items message
 * - No search results
 * - No filtered items
 * - Error states
 */
export function EmptyStateExample() {
  const [items, _setItems] = useState<{ id: string; name: string }[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<string[]>([]);

  // Show different empty states based on conditions
  if (items.length === 0 && searchQuery === '' && filters.length === 0) {
    return (
      <NoItemsEmptyState
        itemType='requirements'
        actions={[
          {
            label: 'Create First Item',
            onClick: () => {
              logger.info('Create clicked');
            },
          },
          {
            label: 'View Documentation',
            onClick: () => window.open('/docs', '_blank'),
            variant: 'outline',
          },
        ]}
        helpText='Keyboard shortcut: Cmd+K to create'
      />
    );
  }

  if (items.length === 0 && searchQuery !== '') {
    return (
      <NoSearchResultsEmptyState
        query={searchQuery}
        actions={[
          {
            label: 'Clear Search',
            onClick: () => {
              setSearchQuery('');
            },
          },
        ]}
      />
    );
  }

  if (items.length === 0 && filters.length > 0) {
    return (
      <FilteredEmptyState
        filters={filters}
        actions={[
          {
            label: 'Clear Filters',
            onClick: () => {
              setFilters([]);
            },
          },
        ]}
      />
    );
  }

  return <div>Items list here</div>;
}

/**
 * PATTERN 4: Delete with Success Toast (Inline Pattern)
 *
 * Use when you want to skip the confirmation dialog
 * for non-critical operations
 */
export function InlineDeleteExample() {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleQuickDelete = async (itemId: string) => {
    setIsDeleting(true);
    try {
      // Await deleteItemAPI(itemId);
      logger.info(`Deleting: ${itemId}`);

      // Show success with undo option
      toast.success('Item deleted', {
        action: {
          label: 'Undo',
          onClick: () => {
            // Await restoreItemAPI(itemId);
            toast.success('Item restored');
          },
        },
        description: 'Item moved to trash',
      });
    } catch {
      toast.error('Failed to delete item');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <Button
      variant='ghost'
      size='sm'
      disabled={isDeleting}
      onClick={async () => handleQuickDelete('item-456')}
    >
      <Trash2 className='h-4 w-4' />
    </Button>
  );
}

/**
 * PATTERN 5: Complete List View with All Features
 *
 * This is a comprehensive example showing:
 * - Empty state
 * - Delete confirmation
 * - Bulk operations
 * - Success feedback
 */
export function CompleteListViewExample() {
  const [items, setItems] = useState<{ id: string; name: string }[]>([]);
  const [selectedItems, setSelectedItems] = useState<string[]>([]);

  const {
    dialogOpen: deleteDialogOpen,
    pendingDelete: pendingDeleteItem,
    isDeleting,
    requestDelete,
    executeDelete,
    cancelDelete,
  } = useConfirmedDelete();

  const {
    dialogOpen: bulkDialogOpen,
    pendingDelete: pendingBulkDelete,
    isDeleting: isBulkDeleting,
    requestDelete: requestBulkDelete,
    executeDelete: executeBulkDelete,
    cancelDelete: cancelBulkDelete,
  } = useConfirmedBulkDelete();

  const handleDeleteItem = useCallback(
    (item: { id: string; name: string }) => {
      requestDelete({
        confirmText: 'Delete',
        description: 'This action cannot be undone.',
        id: item.id,
        name: item.name,
        severity: 'danger',
        title: `Delete "${item.name}"?`,
      });
    },
    [requestDelete],
  );

  const handleBulkDelete = useCallback(() => {
    if (selectedItems.length === 0) {
      return;
    }

    requestBulkDelete({
      count: selectedItems.length,
      itemType: 'items',
      severity: 'critical',
    });
  }, [selectedItems, requestBulkDelete]);

  // Perform actual deletion
  const performDelete = useCallback(async () => {
    const remainingItems = items.filter((i) => i.id !== pendingDeleteItem?.id);
    setItems(remainingItems);
  }, [items, pendingDeleteItem?.id]);

  const performBulkDelete = useCallback(async () => {
    const remainingItems = items.filter((i) => !selectedItems.includes(i.id));
    setItems(remainingItems);
    setSelectedItems([]);
  }, [items, selectedItems]);

  // Empty state
  if (items.length === 0) {
    return (
      <EmptyState
        icon={InboxIcon}
        title='No items yet'
        description='Create your first item to get started'
        actions={[
          {
            label: 'Create Item',
            onClick: () => {
              setItems([{ id: '1', name: 'Sample Item' }]);
            },
          },
        ]}
      />
    );
  }

  return (
    <div className='space-y-4 p-6'>
      {/* Bulk action toolbar */}
      {selectedItems.length > 0 && (
        <div className='flex items-center gap-2 rounded-lg border border-blue-200 bg-blue-50 p-3 dark:border-blue-900/50 dark:bg-blue-950/20'>
          <span className='text-sm font-medium'>{selectedItems.length} selected</span>
          <Button variant='destructive' size='sm' onClick={handleBulkDelete}>
            Delete Selected
          </Button>
        </div>
      )}

      {/* Item list */}
      <div className='space-y-2'>
        {items.map((item) => (
          <div key={item.id} className='flex items-center justify-between rounded-lg border p-4'>
            <div className='flex items-center gap-3'>
              <input
                type='checkbox'
                checked={selectedItems.includes(item.id)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setSelectedItems([...selectedItems, item.id]);
                  } else {
                    setSelectedItems(selectedItems.filter((id) => id !== item.id));
                  }
                }}
              />
              <span>{item.name}</span>
            </div>
            <Button
              variant='ghost'
              size='sm'
              onClick={() => {
                handleDeleteItem(item);
              }}
            >
              <Trash2 className='h-4 w-4' />
            </Button>
          </div>
        ))}
      </div>

      {/* Dialogs */}
      <ConfirmationDialog
        open={deleteDialogOpen}
        onOpenChange={(open) => {
          if (!open) {
            cancelDelete();
          }
        }}
        title={pendingDeleteItem?.title ?? 'Delete?'}
        description={pendingDeleteItem?.description ?? ''}
        isLoading={isDeleting}
        onConfirm={async () => executeDelete(performDelete)}
      />

      <BulkConfirmationDialog
        open={bulkDialogOpen}
        onOpenChange={(open) => {
          if (!open) {
            cancelBulkDelete();
          }
        }}
        actionType='delete'
        itemCount={pendingBulkDelete?.count ?? 0}
        isLoading={isBulkDeleting}
        onConfirm={async () => executeBulkDelete(performBulkDelete)}
      />
    </div>
  );
}

/** Named export for barrel file */
export const DeleteOperationDemo = CompleteListViewExample;
