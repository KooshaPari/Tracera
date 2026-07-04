import { AlertCircle, RefreshCcw } from 'lucide-react';
import { memo } from 'react';

import { Button } from '@tracertm/ui/components/Button';

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export const ErrorState = memo(function ErrorState({
  title = 'Failed to load graph',
  message = 'An error occurred while loading the graph data.',
  onRetry,
}: ErrorStateProps) {
  return (
    <div className='flex h-full flex-col items-center justify-center space-y-4 p-8'>
      <AlertCircle className='text-destructive h-12 w-12' />
      <div className='space-y-2 text-center'>
        <h3 className='text-lg font-semibold'>{title}</h3>
        <p className='text-muted-foreground max-w-md text-sm'>{message}</p>
      </div>
      {onRetry && (
        <Button onClick={onRetry} variant='outline' className='gap-2'>
          <RefreshCcw className='h-4 w-4' />
          Retry
        </Button>
      )}
    </div>
  );
});
