import { memo } from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { WifiOff, RefreshCw } from 'lucide-react';

interface NetworkErrorStateProps {
  onRetry?: () => void;
  isOffline?: boolean;
}

export const NetworkErrorState = memo(function NetworkErrorState({
  onRetry,
  isOffline = false,
}: NetworkErrorStateProps) {
  return (
    <Alert variant="destructive">
      <WifiOff className="h-4 w-4" />
      <AlertTitle>
        {isOffline ? 'No internet connection' : 'Network error'}
      </AlertTitle>
      <AlertDescription className="flex items-center justify-between">
        <span>
          {isOffline
            ? 'Please check your internet connection and try again.'
            : 'Failed to load data. Please try again.'}
        </span>
        {onRetry && (
          <Button size="sm" variant="outline" onClick={onRetry}>
            <RefreshCw className="h-3 w-3 mr-1" />
            Retry
          </Button>
        )}
      </AlertDescription>
    </Alert>
  );
});
