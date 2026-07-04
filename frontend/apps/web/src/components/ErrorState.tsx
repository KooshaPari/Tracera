import { AlertCircle, RefreshCw } from 'lucide-react';

import { Alert, AlertDescription, AlertTitle } from '@tracertm/ui/components/Alert';
import { Button } from '@tracertm/ui/components/Button';

interface ErrorStateProps {
  title?: string;
  description: string;
  onRetry?: () => void;
}

export function ErrorState({
  title = 'Something went wrong',
  description,
  onRetry,
}: ErrorStateProps) {
  return (
    <Alert variant='destructive' className='mb-4' data-testid='error-message'>
      <AlertCircle className='h-4 w-4' />
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription className='mt-2'>
        <p className='mb-4'>{description}</p>
        {onRetry && (
          <Button
            variant='outline'
            size='sm'
            onClick={onRetry}
            className='gap-2'
            data-testid='retry-button'
          >
            <RefreshCw className='h-4 w-4' />
            Retry
          </Button>
        )}
      </AlertDescription>
    </Alert>
  );
}
