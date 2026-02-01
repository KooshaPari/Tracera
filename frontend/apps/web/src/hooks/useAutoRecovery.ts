import { useEffect, useRef, useState } from 'react';

export interface AutoRecoveryOptions {
  maxRetries?: number;
  retryDelay?: number; // ms
  exponentialBackoff?: boolean;
  onRetry?: (attempt: number) => void;
  onMaxRetriesReached?: () => void;
}

export interface AutoRecoveryState {
  isRetrying: boolean;
  retryCount: number;
  nextRetryIn: number | null; // ms
}

export function useAutoRecovery(
  error: Error | null,
  retry: () => void,
  options: AutoRecoveryOptions = {}
): AutoRecoveryState {
  const {
    maxRetries = 3,
    retryDelay = 1000,
    exponentialBackoff = true,
    onRetry,
    onMaxRetriesReached,
  } = options;

  const [state, setState] = useState<AutoRecoveryState>({
    isRetrying: false,
    retryCount: 0,
    nextRetryIn: null,
  });

  const retryTimeoutRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    if (!error) {
      setState({ isRetrying: false, retryCount: 0, nextRetryIn: null });
      return;
    }

    if (state.retryCount >= maxRetries) {
      onMaxRetriesReached?.();
      return;
    }

    const delay = exponentialBackoff
      ? retryDelay * Math.pow(2, state.retryCount)
      : retryDelay;

    setState(prev => ({
      ...prev,
      isRetrying: true,
      nextRetryIn: delay,
    }));

    retryTimeoutRef.current = setTimeout(() => {
      onRetry?.(state.retryCount + 1);
      retry();
      setState(prev => ({
        ...prev,
        retryCount: prev.retryCount + 1,
        isRetrying: false,
      }));
    }, delay);

    return () => {
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
    };
  }, [error, state.retryCount, maxRetries, retryDelay, exponentialBackoff]);

  return state;
}
