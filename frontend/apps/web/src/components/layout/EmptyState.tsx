import type { ReactNode } from 'react';

import { Button } from '@tracertm/ui';

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
}

export const EmptyState = function EmptyState({
  icon,
  title,
  description,
  action,
  secondaryAction,
}: EmptyStateProps) {
  return (
    <div className='flex flex-col items-center justify-center px-4 py-12 text-center'>
      {icon && (
        <div className='mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gray-100 text-gray-400 dark:bg-gray-800 dark:text-gray-600'>
          {icon}
        </div>
      )}

      <h3 className='mb-2 text-lg font-semibold text-gray-900 dark:text-gray-100'>{title}</h3>

      {description && (
        <p className='mb-6 max-w-md text-sm text-gray-600 dark:text-gray-400'>{description}</p>
      )}

      {(action ?? secondaryAction) && (
        <div className='flex items-center space-x-3'>
          {action && (
            <Button onClick={action.onClick} variant='default'>
              {action.label}
            </Button>
          )}
          {secondaryAction && (
            <Button onClick={secondaryAction.onClick} variant='outline'>
              {secondaryAction.label}
            </Button>
          )}
        </div>
      )}
    </div>
  );
};
