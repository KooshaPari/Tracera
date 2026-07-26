/**
 * Confirmation Dialog Component
 *
 * Provides a consistent confirmation UI for destructive actions (delete, bulk operations).
 * Includes danger warnings, action buttons, and keyboard support.
 */

import { AnimatePresence, motion } from 'framer-motion';
import { AlertTriangle } from 'lucide-react';
import * as React from 'react';

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { cn } from '@/lib/utils';

/**
 * Confirmation Dialog Props
 */
export interface ConfirmationDialogProps {
  /** Dialog open state */
  open: boolean;

  /** Callback when dialog state changes */
  onOpenChange: (open: boolean) => void;

  /** Dialog title */
  title: string;

  /** Dialog description/message */
  description: string;

  /** Confirm button text (default: "Delete") */
  confirmText?: string | undefined;

  /** Cancel button text (default: "Cancel") */
  cancelText?: string | undefined;

  /** Confirm button variant (default: "destructive") */
  confirmVariant?: 'destructive' | 'default' | undefined;

  /** Is confirm action loading? */
  isLoading?: boolean | undefined;

  /** Callback when user confirms */
  onConfirm: () => void | Promise<void>;

  /** Callback when user cancels */
  onCancel?: (() => void) | undefined;

  /** Danger level - affects styling */
  severity?: 'warning' | 'danger' | 'critical' | undefined;

  /** Additional context (e.g., count of items) */
  context?: string | undefined;

  /** Show additional warning text */
  showWarning?: boolean | undefined;
}

/**
 * Confirmation Dialog Component
 *
 * Usage:
 * ```tsx
 * const [confirmOpen, setConfirmOpen] = useState(false);
 *
 * return (
 *   <>
 *     <Button onClick={() => setConfirmOpen(true)}>Delete Item</Button>
 *
 *     <ConfirmationDialog
 *       open={confirmOpen}
 *       onOpenChange={setConfirmOpen}
 *       title="Delete Item?"
 *       description="This action cannot be undone."
 *       onConfirm={() => deleteItem()}
 *       context="1 item will be permanently deleted"
 *     />
 *   </>
 * );
 * ```
 */
const ConfirmationDialog = React.forwardRef<HTMLDivElement, ConfirmationDialogProps>(
  (
    {
      open,
      onOpenChange,
      title,
      description,
      confirmText = 'Delete',
      cancelText = 'Cancel',
      confirmVariant = 'destructive',
      isLoading = false,
      onConfirm,
      onCancel,
      severity = 'danger',
      context,
      showWarning = true,
    },
    ref,
  ) => {
    const [isConfirming, setIsConfirming] = React.useState(false);

    const handleConfirm = async () => {
      setIsConfirming(true);
      try {
        await onConfirm();
        onOpenChange(false);
      } finally {
        setIsConfirming(false);
      }
    };

    const handleCancel = () => {
      onCancel?.();
      onOpenChange(false);
    };

    const severityConfig = {
      critical: {
        bgColor: 'bg-rose-50 dark:bg-rose-950/20',
        borderColor: 'border-rose-200 dark:border-rose-900/40',
        iconColor: 'text-rose-600 dark:text-rose-500',
      },
      danger: {
        bgColor: 'bg-red-50 dark:bg-red-950/20',
        borderColor: 'border-red-200 dark:border-red-900/40',
        iconColor: 'text-red-600 dark:text-red-500',
      },
      warning: {
        bgColor: 'bg-amber-50 dark:bg-amber-950/20',
        borderColor: 'border-amber-200 dark:border-amber-900/40',
        iconColor: 'text-amber-600 dark:text-amber-500',
      },
    };

    const config = severityConfig[severity];

    return (
      <AlertDialog open={open} onOpenChange={onOpenChange}>
        <AlertDialogContent
          ref={ref}
          className={cn('relative border shadow-lg', config.bgColor, config.borderColor)}
        >
          <AnimatePresence mode='wait'>
            <motion.div
              key='content'
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              <AlertDialogHeader>
                <div className='flex items-start gap-3'>
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{
                      damping: 10,
                      stiffness: 400,
                      type: 'spring',
                    }}
                  >
                    <AlertTriangle
                      className={cn('h-5 w-5 flex-shrink-0 mt-0.5', config.iconColor)}
                    />
                  </motion.div>

                  <div className='flex-1'>
                    <AlertDialogTitle className='text-base font-semibold'>{title}</AlertDialogTitle>

                    <AlertDialogDescription className='mt-1 text-sm'>
                      {description}
                    </AlertDialogDescription>

                    {context && (
                      <div className={cn('mt-2 text-xs font-medium', config.iconColor)}>
                        {context}
                      </div>
                    )}

                    {showWarning && severity === 'critical' && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ delay: 0.1, duration: 0.2 }}
                        className={cn(
                          'mt-3 p-2 rounded text-xs font-medium',
                          config.bgColor,
                          config.borderColor,
                          'border',
                        )}
                      >
                        This action cannot be undone.
                      </motion.div>
                    )}
                  </div>
                </div>
              </AlertDialogHeader>

              <AlertDialogFooter className='mt-6'>
                <AlertDialogCancel
                  onClick={handleCancel}
                  disabled={isConfirming || isLoading}
                  className='bg-background hover:bg-accent rounded-md border px-4 py-2 text-sm font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50'
                >
                  {cancelText}
                </AlertDialogCancel>

                <AlertDialogAction
                  onClick={handleConfirm}
                  disabled={isConfirming || isLoading}
                  className={cn(
                    'px-4 py-2 text-sm font-medium rounded-md text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all inline-flex items-center gap-2',
                    confirmVariant === 'destructive'
                      ? 'bg-red-600 hover:bg-red-700'
                      : 'bg-primary hover:bg-primary/90',
                  )}
                >
                  {isConfirming || isLoading ? (
                    <>
                      <div className='h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent' />
                      <span>Deleting...</span>
                    </>
                  ) : (
                    confirmText
                  )}
                </AlertDialogAction>
              </AlertDialogFooter>
            </motion.div>
          </AnimatePresence>
        </AlertDialogContent>
      </AlertDialog>
    );
  },
);

ConfirmationDialog.displayName = 'ConfirmationDialog';

/**
 * Bulk Action Confirmation Dialog
 * Specialized version for bulk operations (delete, status change, etc.)
 */
export interface BulkConfirmationDialogProps extends Omit<
  ConfirmationDialogProps,
  'title' | 'description'
> {
  /** Type of bulk operation */
  actionType: 'delete' | 'status-change' | 'archive' | 'assign';

  /** Number of items affected */
  itemCount: number;

  /** Custom action label (e.g., "Archive") */
  actionLabel?: string | undefined;
}

export const BulkConfirmationDialog = React.forwardRef<HTMLDivElement, BulkConfirmationDialogProps>(
  (
    {
      actionType,
      itemCount,
      actionLabel: _actionLabel,
      open,
      onOpenChange,
      confirmText,
      onConfirm,
      isLoading,
      ...props
    },
    ref,
  ) => {
    const pluralItem = itemCount === 1 ? 'item' : 'items';

    const actionConfig = {
      archive: {
        confirmText: confirmText ?? 'Archive',
        description: `You're about to archive ${itemCount} ${pluralItem}. You can restore them later.`,
        severity: 'warning' as const,
        title: `Archive ${itemCount} ${pluralItem}?`,
      },
      assign: {
        confirmText: confirmText ?? 'Assign',
        description: `You're about to assign ${itemCount} ${pluralItem} to a team member.`,
        severity: 'warning' as const,
        title: `Assign ${itemCount} ${pluralItem}?`,
      },
      delete: {
        confirmText: confirmText ?? 'Delete',
        description: `You're about to permanently delete ${itemCount} ${pluralItem}. This cannot be undone.`,
        severity: 'critical' as const,
        title: `Delete ${itemCount} ${pluralItem}?`,
      },
      'status-change': {
        confirmText: confirmText ?? 'Update',
        description: `You're about to update the status of ${itemCount} ${pluralItem}.`,
        severity: 'warning' as const,
        title: `Change status of ${itemCount} ${pluralItem}?`,
      },
    };

    const config = actionConfig[actionType];

    return (
      <ConfirmationDialog
        ref={ref}
        open={open}
        onOpenChange={onOpenChange}
        title={config.title}
        description={config.description}
        confirmText={config.confirmText}
        severity={config.severity}
        isLoading={isLoading}
        onConfirm={onConfirm}
        context={`${itemCount} ${pluralItem} will be ${actionType === 'delete' ? 'permanently deleted' : 'affected'}`}
        {...props}
      />
    );
  },
);

BulkConfirmationDialog.displayName = 'BulkConfirmationDialog';

export {
  ConfirmationDialog,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
};
