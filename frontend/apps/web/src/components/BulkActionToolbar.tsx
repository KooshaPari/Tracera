import type { ReactNode } from 'react';

import { Trash2, X } from 'lucide-react';
import { useCallback } from 'react';

import { logger } from '@/lib/logger';
import { cn } from '@/lib/utils';

export interface BulkAction {
  id: string;
  label: string;
  icon: ReactNode;
  action: (selectedIds: string[]) => Promise<void> | void;
  variant?: 'default' | 'destructive';
  disabled?: boolean;
}

interface BulkActionToolbarProps {
  selectedCount: number;
  totalCount: number;
  onSelectAll: () => void;
  onSelectNone: () => void;
  actions: BulkAction[];
  loading?: boolean;
  onActionComplete?: (actionId: string) => void;
}

const runBulkAction = async (
  action: BulkAction,
  onActionComplete?: (id: string) => void,
): Promise<void> => {
  try {
    await action.action([]);
    onActionComplete?.(action.id);
  } catch (error) {
    logger.error('Bulk action failed:', error);
  }
};

interface BulkActionButtonProps {
  action: BulkAction;
  disabled: boolean;
  onRun: (action: BulkAction) => void;
}

const BulkActionButton = ({ action, disabled, onRun }: BulkActionButtonProps) => {
  const handleClick = useCallback(() => {
    onRun(action);
  }, [action, onRun]);
  return (
    <button
      type='button'
      onClick={handleClick}
      disabled={disabled}
      className={cn(
        'flex items-center gap-2 px-4 py-2 rounded-lg font-bold text-[11px] uppercase tracking-widest transition-all duration-200 ease-out active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed',
        action.variant === 'destructive'
          ? 'bg-destructive/10 text-destructive hover:bg-destructive/20 disabled:hover:bg-destructive/10'
          : 'bg-primary/10 text-primary hover:bg-primary/20 disabled:hover:bg-primary/10',
      )}
      title={action.label}
    >
      {action.icon}
      <span className='hidden sm:inline'>{action.label}</span>
    </button>
  );
};

const SelectionControls = ({
  loading,
  onSelectAll,
  onSelectNone,
  selectedCount,
  totalCount,
}: {
  loading: boolean;
  onSelectAll: () => void;
  onSelectNone: () => void;
  selectedCount: number;
  totalCount: number;
}) => (
  <div className='border-border/50 flex items-center gap-3 border-r pr-4'>
    <span className='text-sm font-bold'>
      {selectedCount} of {totalCount} selected
    </span>
    <div className='flex items-center gap-2'>
      <button
        type='button'
        onClick={onSelectAll}
        disabled={loading || selectedCount === totalCount}
        className='text-primary hover:text-primary/80 disabled:text-muted-foreground text-[10px] font-black tracking-widest uppercase transition-all duration-200 ease-out active:scale-95 disabled:cursor-not-allowed'
      >
        Select All
      </button>
      <span className='text-border/50'>•</span>
      <button
        type='button'
        onClick={onSelectNone}
        disabled={loading}
        className='text-primary hover:text-primary/80 disabled:text-muted-foreground text-[10px] font-black tracking-widest uppercase transition-all duration-200 ease-out active:scale-95 disabled:cursor-not-allowed'
      >
        Deselect
      </button>
    </div>
  </div>
);

const ActionButtons = ({
  actions,
  disabled,
  onRun,
}: {
  actions: BulkAction[];
  disabled: boolean;
  onRun: (action: BulkAction) => void;
}) => (
  <div className='flex items-center gap-2'>
    {actions.map((action) => (
      <BulkActionButton
        key={action.id}
        action={action}
        disabled={disabled || action.disabled === true}
        onRun={onRun}
      />
    ))}
  </div>
);

const CloseButton = ({
  disabled,
  onSelectNone,
}: {
  disabled: boolean;
  onSelectNone: () => void;
}) => (
  <button
    type='button'
    onClick={onSelectNone}
    disabled={disabled}
    className='hover:bg-muted border-border/50 ml-2 rounded-lg border-l p-2 pl-2 transition-all duration-200 ease-out active:scale-95'
    aria-label='Close toolbar'
  >
    <X className='h-4 w-4' />
  </button>
);

export const BulkActionToolbar = ({
  selectedCount,
  totalCount,
  onSelectAll,
  onSelectNone,
  actions,
  loading = false,
  onActionComplete,
}: BulkActionToolbarProps) => {
  const handleAction = useCallback(
    (action: BulkAction) => {
      if (selectedCount === 0 || loading) {
        return;
      }
      runBulkAction(action, onActionComplete);
    },
    [selectedCount, loading, onActionComplete],
  );

  if (selectedCount === 0) {
    return null;
  }

  return (
    <div className='animate-in slide-in-from-bottom-4 fixed bottom-6 left-1/2 z-50 -translate-x-1/2 duration-300'>
      <div className='bg-card border-primary/30 ring-primary/20 flex items-center gap-3 rounded-2xl border px-6 py-4 shadow-lg ring-1 backdrop-blur-sm'>
        <SelectionControls
          loading={loading}
          onSelectAll={onSelectAll}
          onSelectNone={onSelectNone}
          selectedCount={selectedCount}
          totalCount={totalCount}
        />
        <ActionButtons
          actions={actions}
          disabled={loading || selectedCount === 0}
          onRun={handleAction}
        />
        <CloseButton disabled={loading} onSelectNone={onSelectNone} />
      </div>
    </div>
  );
};

// Predefined bulk actions
export const commonBulkActions = {
  delete: (onDelete: (ids: string[]) => Promise<void>): BulkAction => ({
    action: onDelete,
    icon: <Trash2 className='h-4 w-4' />,
    id: 'delete',
    label: 'Delete',
    variant: 'destructive',
  }),
};
