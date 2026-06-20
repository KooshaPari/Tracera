import { Clock, RefreshCw } from 'lucide-react';
import { memo } from 'react';

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

interface TimeoutErrorStateProps {
  onRetry?: () => void;
  timeout?: number;
}

export const TimeoutErrorState = memo(function TimeoutErrorState({
  onRetry,
  timeout = 30_000,
}: TimeoutErrorStateProps) {
  const MS_PER_SEC = 1000;
  return (
    <Alert variant='destructive'>
      <Clock className='h-4 w-4' />
      <AlertTitle>Request timed out</AlertTitle>
      <AlertDescription className='flex items-center justify-between'>
        <span>
          The request took too long ({timeout / MS_PER_SEC}s). This might be due to a large dataset
          or slow connection.
        </span>
        {onRetry && (
          <Button size='sm' variant='outline' onClick={onRetry}>
            <RefreshCw className='mr-1 h-3 w-3' />
            Retry
          </Button>
        )}
      </AlertDescription>
    </Alert>
  );
});
