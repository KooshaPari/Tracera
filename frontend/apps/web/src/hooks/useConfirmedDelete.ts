/**
 * Hook for managing delete operations with confirmation dialogs
 * Provides consistent UX for all destructive operations
 */

import { useCallback, useState } from 'react';
import { toast } from 'sonner';

import { logger } from '@/lib/logger';

export interface DeleteConfig {
  /** Item identifier (for logging) */
  id: string;

  /** Item display name/title */
  name: string;

  /** Confirm dialog title */
  title?: string;

  /** Confirm dialog description */
  description?: string;

  /** Confirm button text */
  confirmText?: string;

  /** Success message */
  successMessage?: string;

  /** Error message */
  errorMessage?: string;

  /** Context info (e.g., "and 5 related items") */
  context?: string;

  /** Severity level for styling */
  severity?: 'warning' | 'danger' | 'critical';
}

export interface UseConfirmedDeleteOptions {
  /** Enable automatic success toast */
  showSuccessToast?: boolean;

  /** Enable automatic error toast */
  showErrorToast?: boolean;

  /** Auto-dismiss success toast after ms */
  successToastDuration?: number;
}

export interface UseConfirmedDeleteState {
  /** Is delete dialog open */
  dialogOpen: boolean;

  /** Current pending delete config */
  pendingDelete: DeleteConfig | null;

  /** Is delete in progress */
  isDeleting: boolean;
}

export interface UseConfirmedDeleteActions {
  /** Request delete confirmation */
  requestDelete: (config: DeleteConfig) => void;

  /** Execute delete after confirmation */
  executeDelete: (deleteFunction: () => Promise<void> | void) => Promise<void>;

  /** Cancel delete operation */
  cancelDelete: () => void;

  /** Close dialog without side effects */
  closeDialog: () => void;
}

export function useConfirmedDelete(
  options: UseConfirmedDeleteOptions = {},
): UseConfirmedDeleteState & UseConfirmedDeleteActions {
  const { showSuccessToast = true, showErrorToast = true, successToastDuration = 3000 } = options;

  const [dialogOpen, setDialogOpen] = useState(false);
  const [pendingDelete, setPendingDelete] = useState<DeleteConfig | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const requestDelete = useCallback((config: DeleteConfig) => {
    setPendingDelete(config);
    setDialogOpen(true);
  }, []);

  const executeDelete = useCallback(
    async (deleteFunction: () => Promise<void> | void) => {
      if (!pendingDelete) {
        return;
      }

      setIsDeleting(true);

      try {
        await deleteFunction();

        setDialogOpen(false);

        if (showSuccessToast) {
          toast.success(
            pendingDelete.successMessage ?? `${pendingDelete.name} deleted successfully`,
            {
              duration: successToastDuration,
            },
          );
        }
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : 'Unknown error';

        if (showErrorToast) {
          toast.error(
            pendingDelete.errorMessage ?? `Failed to delete ${pendingDelete.name}: ${errorMsg}`,
          );
        }

        logger.error(`[Delete Error] ${pendingDelete.id}:`, error);
      } finally {
        setIsDeleting(false);
        setPendingDelete(null);
      }
    },
    [pendingDelete, showSuccessToast, showErrorToast, successToastDuration],
  );

  const cancelDelete = useCallback(() => {
    setDialogOpen(false);
    setPendingDelete(null);
  }, []);

  const closeDialog = useCallback(() => {
    setDialogOpen(false);
  }, []);

  return {
    cancelDelete,
    closeDialog,
    dialogOpen,
    executeDelete,
    isDeleting,
    pendingDelete,
    requestDelete,
  };
}

/**
 * Hook for bulk delete operations
 */
export interface BulkDeleteConfig {
  /** Item count */
  count: number;

  /** Item type name */
  itemType: string;

  /** Success message */
  successMessage?: string;

  /** Error message */
  errorMessage?: string;

  /** Severity level */
  severity?: 'warning' | 'danger' | 'critical';
}

export function useConfirmedBulkDelete(options: UseConfirmedDeleteOptions = {}) {
  const { showSuccessToast = true, showErrorToast = true, successToastDuration = 3000 } = options;

  const [dialogOpen, setDialogOpen] = useState(false);
  const [pendingDelete, setPendingDelete] = useState<BulkDeleteConfig | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const requestDelete = useCallback((config: BulkDeleteConfig) => {
    setPendingDelete(config);
    setDialogOpen(true);
  }, []);

  const executeDelete = useCallback(
    async (deleteFunction: () => Promise<void> | void) => {
      if (!pendingDelete) {
        return;
      }

      setIsDeleting(true);

      try {
        await deleteFunction();

        setDialogOpen(false);

        if (showSuccessToast) {
          const itemWord = pendingDelete.count === 1 ? 'item' : 'items';
          toast.success(
            pendingDelete.successMessage ??
              `${pendingDelete.count} ${itemWord} deleted successfully`,
            {
              duration: successToastDuration,
            },
          );
        }
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : 'Unknown error';

        if (showErrorToast) {
          toast.error(pendingDelete.errorMessage ?? `Failed to delete items: ${errorMsg}`);
        }

        logger.error('[Bulk Delete Error]:', error);
      } finally {
        setIsDeleting(false);
        setPendingDelete(null);
      }
    },
    [pendingDelete, showSuccessToast, showErrorToast, successToastDuration],
  );

  const cancelDelete = useCallback(() => {
    setDialogOpen(false);
    setPendingDelete(null);
  }, []);

  const closeDialog = useCallback(() => {
    setDialogOpen(false);
  }, []);

  return {
    cancelDelete,
    closeDialog,
    dialogOpen,
    executeDelete,
    isDeleting,
    pendingDelete,
    requestDelete,
  };
}
