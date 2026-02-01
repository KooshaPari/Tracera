import { memo, useEffect, useState } from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { RefreshCw } from 'lucide-react';

interface RecoveryProgressProps {
  retryCount: number;
  maxRetries: number;
  nextRetryIn: number; // ms
}

export const RecoveryProgress = memo(function RecoveryProgress({
  retryCount,
  maxRetries,
  nextRetryIn,
}: RecoveryProgressProps) {
  const [countdown, setCountdown] = useState(nextRetryIn);

  useEffect(() => {
    setCountdown(nextRetryIn);

    const interval = setInterval(() => {
      setCountdown(prev => Math.max(0, prev - 100));
    }, 100);

    return () => clearInterval(interval);
  }, [nextRetryIn]);

  const progress = ((nextRetryIn - countdown) / nextRetryIn) * 100;

  return (
    <Alert>
      <RefreshCw className="h-4 w-4 animate-spin" />
      <AlertTitle>Retrying connection...</AlertTitle>
      <AlertDescription>
        <div className="space-y-2 mt-2">
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Attempt {retryCount + 1} of {maxRetries}</span>
            <span>Next retry in {Math.ceil(countdown / 1000)}s</span>
          </div>
          <Progress value={progress} className="h-1" />
        </div>
      </AlertDescription>
    </Alert>
  );
});
