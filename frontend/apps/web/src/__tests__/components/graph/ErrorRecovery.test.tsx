import { act, fireEvent, render, renderHook, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { EnhancedErrorState } from '@/components/graph/EnhancedErrorState';
import { GraphErrorBoundary } from '@/components/graph/GraphErrorBoundary';
import { NetworkErrorState } from '@/components/graph/NetworkErrorState';
import { RecoveryProgress } from '@/components/graph/RecoveryProgress';
import { TimeoutErrorState } from '@/components/graph/TimeoutErrorState';
import { useAutoRecovery } from '@/hooks/useAutoRecovery';

describe(EnhancedErrorState, () => {
  it('renders error message as string', () => {
    render(<EnhancedErrorState error='Test error message' />);
    expect(screen.getByText('Test error message')).toBeInTheDocument();
  });

  it('renders error as Error object', () => {
    const error = new Error('Test error');
    render(<EnhancedErrorState error={error} />);
    expect(screen.getByText('Test error')).toBeInTheDocument();
  });

  it('renders inline variant', () => {
    render(<EnhancedErrorState error='Test error' variant='inline' />);
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('shows retry button when onRetry provided', () => {
    const onRetry = vi.fn();
    render(<EnhancedErrorState error='Test error' onRetry={onRetry} />);

    const retryButton = screen.getByText('Retry');
    fireEvent.click(retryButton);

    expect(onRetry).toHaveBeenCalledOnce();
  });

  it('copies error to clipboard', async () => {
    const writeText = vi.fn();
    Object.assign(navigator, {
      clipboard: { writeText },
    });

    const error = new Error('Test error');
    render(<EnhancedErrorState error={error} />);

    const copyButton = screen.getByText('Copy error');
    fireEvent.click(copyButton);

    await waitFor(() => {
      expect(writeText).toHaveBeenCalledWith(expect.stringContaining('Test error'));
    });
  });

  it('shows bug report button when onReportBug provided', () => {
    const onReportBug = vi.fn();
    render(<EnhancedErrorState error='Test error' onReportBug={onReportBug} />);

    const reportButton = screen.getByText('Report bug');
    fireEvent.click(reportButton);

    expect(onReportBug).toHaveBeenCalledWith({
      message: 'Test error',
    });
  });

  it('shows technical details when showDetails is true', () => {
    const error = new Error('Test error');
    error.stack = 'Stack trace here';

    render(<EnhancedErrorState error={error} showDetails />);

    const detailsButton = screen.getByText('Show technical details');
    expect(detailsButton).toBeInTheDocument();
  });

  it('hides technical details when showDetails is false', () => {
    const error = new Error('Test error');
    error.stack = 'Stack trace here';

    render(<EnhancedErrorState error={error} showDetails={false} />);

    expect(screen.queryByText('Show technical details')).not.toBeInTheDocument();
  });
});

describe(GraphErrorBoundary, () => {
  const ErrorComponent = () => {
    throw new Error('Test error');
  };

  beforeEach(() => {
    // Suppress console errors in tests
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('catches errors and shows error state', () => {
    render(
      <GraphErrorBoundary>
        <ErrorComponent />
      </GraphErrorBoundary>,
    );

    expect(screen.getByText('Unable to load graph')).toBeInTheDocument();
  });

  it('calls onError callback when error occurs', () => {
    const onError = vi.fn();

    render(
      <GraphErrorBoundary onError={onError}>
        <ErrorComponent />
      </GraphErrorBoundary>,
    );

    expect(onError).toHaveBeenCalledWith(expect.any(Error), expect.any(Object));
  });

  it('uses custom fallback when provided', () => {
    const fallback = (error: Error) => <div>Custom error: {error.message}</div>;

    render(
      <GraphErrorBoundary fallback={fallback}>
        <ErrorComponent />
      </GraphErrorBoundary>,
    );

    expect(screen.getByText(/Custom error:/)).toBeInTheDocument();
  });

  it('renders children when no error', () => {
    render(
      <GraphErrorBoundary>
        <div>Normal content</div>
      </GraphErrorBoundary>,
    );

    expect(screen.getByText('Normal content')).toBeInTheDocument();
  });
});

describe(NetworkErrorState, () => {
  it('renders offline message when isOffline is true', () => {
    render(<NetworkErrorState isOffline />);
    expect(screen.getByText('No internet connection')).toBeInTheDocument();
  });

  it('renders network error message when isOffline is false', () => {
    render(<NetworkErrorState isOffline={false} />);
    expect(screen.getByText('Network error')).toBeInTheDocument();
  });

  it('shows retry button when onRetry provided', () => {
    const onRetry = vi.fn();
    render(<NetworkErrorState onRetry={onRetry} />);

    const retryButton = screen.getByText('Retry');
    fireEvent.click(retryButton);

    expect(onRetry).toHaveBeenCalledOnce();
  });
});

describe(TimeoutErrorState, () => {
  it('renders timeout message with duration', () => {
    render(<TimeoutErrorState timeout={30_000} />);
    expect(screen.getByText(/30s/)).toBeInTheDocument();
  });

  it('shows retry button when onRetry provided', () => {
    const onRetry = vi.fn();
    render(<TimeoutErrorState onRetry={onRetry} />);

    const retryButton = screen.getByText('Retry');
    fireEvent.click(retryButton);

    expect(onRetry).toHaveBeenCalledOnce();
  });
});

describe(RecoveryProgress, () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders retry progress', () => {
    render(<RecoveryProgress retryCount={1} maxRetries={3} nextRetryIn={5000} />);

    expect(screen.getByText('Retrying connection...')).toBeInTheDocument();
    expect(screen.getByText(/Attempt 2 of 3/)).toBeInTheDocument();
  });

  it('shows countdown timer', () => {
    render(<RecoveryProgress retryCount={0} maxRetries={3} nextRetryIn={5000} />);

    expect(screen.getByText(/Next retry in 5s/)).toBeInTheDocument();
  });

  it('updates countdown over time', () => {
    render(<RecoveryProgress retryCount={0} maxRetries={3} nextRetryIn={5000} />);

    act(() => {
      vi.advanceTimersByTime(1000);
    });

    rerender(<RecoveryProgress retryCount={0} maxRetries={3} nextRetryIn={5000} />);

    expect(screen.getByText(/Next retry in 4s/)).toBeInTheDocument();
  });
});

describe(useAutoRecovery, () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('returns initial state when no error', () => {
    const retry = vi.fn();
    const { result } = renderHook(() => useAutoRecovery(null, retry));

    expect(result.current).toEqual({
      isRetrying: false,
      nextRetryIn: null,
      retryCount: 0,
    });
  });

  it('triggers retry after delay', () => {
    const retry = vi.fn();
    const error = new Error('Test error');

    const { result } = renderHook(() => useAutoRecovery(error, retry, { retryDelay: 1000 }));

    expect(result.current.isRetrying).toBeTruthy();

    act(() => {
      vi.advanceTimersByTime(1000);
    });

    expect(retry).toHaveBeenCalledOnce();
  });

  it('uses exponential backoff', () => {
    const retry = vi.fn();
    const error = new Error('Test error');

    const { rerender } = renderHook(() =>
      useAutoRecovery(error, retry, {
        exponentialBackoff: true,
        retryDelay: 1000,
      }),
    );

    // First retry: 1000ms
    act(() => {
      vi.advanceTimersByTime(1000);
    });
    expect(retry).toHaveBeenCalledOnce();

    // Second retry: 2000ms
    rerender();
    act(() => {
      vi.advanceTimersByTime(2000);
    });
    expect(retry).toHaveBeenCalledTimes(2);
  });

  it('stops retrying after max retries', () => {
    const retry = vi.fn();
    const onMaxRetriesReached = vi.fn();
    const error = new Error('Test error');

    const { rerender } = renderHook(() =>
      useAutoRecovery(error, retry, {
        maxRetries: 2,
        onMaxRetriesReached,
        retryDelay: 1000,
      }),
    );

    // First retry
    act(() => {
      vi.advanceTimersByTime(1000);
    });

    // Second retry
    rerender();
    act(() => {
      vi.advanceTimersByTime(2000);
    });

    expect(retry).toHaveBeenCalledTimes(2);

    // Should not retry again
    rerender();
    act(() => {
      vi.advanceTimersByTime(5000);
    });

    expect(retry).toHaveBeenCalledTimes(2);
    expect(onMaxRetriesReached).toHaveBeenCalledOnce();
  });

  it('calls onRetry callback with attempt number', () => {
    const retry = vi.fn();
    const onRetry = vi.fn();
    const error = new Error('Test error');

    renderHook(() =>
      useAutoRecovery(error, retry, {
        onRetry,
        retryDelay: 1000,
      }),
    );

    act(() => {
      vi.advanceTimersByTime(1000);
    });

    expect(onRetry).toHaveBeenCalledWith(1);
  });

  it('resets state when error is cleared', () => {
    const retry = vi.fn();
    let error: Error | null = new Error('Test error');

    const { result: _result, rerender } = renderHook(() => useAutoRecovery(error, retry));

    expect(result.current.isRetrying).toBeTruthy();

    // Clear error
    error = null;
    rerender();

    expect(result.current).toEqual({
      isRetrying: false,
      nextRetryIn: null,
      retryCount: 0,
    });
  });
});
