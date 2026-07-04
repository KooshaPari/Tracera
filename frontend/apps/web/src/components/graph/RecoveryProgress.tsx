import { RefreshCw } from 'lucide-react';
import { memo, useEffect, useState } from 'react';

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';

interface RecoveryProgressProps {
  retryCount: number;
  maxRetries: number;
  nextRetryIn: number; // Ms
}

export const RecoveryProgress = memo(function RecoveryProgress({
  retryCount,
  maxRetries,
  nextRetryIn,
}: RecoveryProgressProps) {
  const MS_PER_TICK = 100;
  const MS_PER_SEC = 1000;
  const PERCENT_MULTIPLIER = 100;
  const [countdown, setCountdown] = useState(nextRetryIn);

  useEffect(() => {
    setCountdown(nextRetryIn);
    const tick = (): void => {
      setCountdown((prev) => Math.max(0, prev - MS_PER_TICK));
    };
    const interval = setInterval(tick, MS_PER_TICK);
    return () => {
      clearInterval(interval);
    };
  }, [nextRetryIn]);

  const progress = ((nextRetryIn - countdown) / nextRetryIn) * PERCENT_MULTIPLIER;

  return (
    <Alert>
      <RefreshCw className='h-4 w-4 animate-spin' />
      <AlertTitle>Retrying connection...</AlertTitle>
      <AlertDescription>
        <div className='mt-2 space-y-2'>
          <div className='text-muted-foreground flex justify-between text-xs'>
            <span>
              Attempt {retryCount + 1} of {maxRetries}
            </span>
            <span>Next retry in {Math.ceil(countdown / MS_PER_SEC)}s</span>
          </div>
          <Progress value={progress} className='h-1' />
        </div>
      </AlertDescription>
    </Alert>
  );
});
