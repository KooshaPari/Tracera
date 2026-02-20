import { act, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { ErrorState } from '@/components/graph/ErrorState';
import { GraphSkeleton } from '@/components/graph/GraphSkeleton';
import { LoadingProgress } from '@/components/graph/LoadingProgress';
import { LoadingTransition } from '@/components/graph/LoadingTransition';

describe(GraphSkeleton, () => {
  it('should render with default node and edge count', () => {
    const { container } = render(<GraphSkeleton />);

    // Should have the skeleton container
    const skeleton = screen.getByTestId('graph-skeleton');
    expect(skeleton).toBeInTheDocument();
    expect(skeleton).toHaveClass('animate-pulse');

    // Default is 20 nodes
    const nodes = container.querySelectorAll('[class*="absolute rounded-lg border bg-card"]');
    expect(nodes.length).toBe(20);
  });

  it('should render with custom node count', () => {
    const { container } = render(<GraphSkeleton nodeCount={10} edgeCount={15} />);

    // Should have 10 nodes
    const nodes = container.querySelectorAll('[class*="absolute rounded-lg border bg-card"]');
    expect(nodes.length).toBe(10);
  });

  it('should render skeleton edges', () => {
    const { container } = render(<GraphSkeleton nodeCount={5} edgeCount={8} />);

    // Should have SVG with edges
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();

    const edges = container.querySelectorAll('line');
    expect(edges.length).toBe(8);
  });

  it('should have proper positioning for nodes', () => {
    const { container } = render(<GraphSkeleton nodeCount={5} />);

    const nodes = container.querySelectorAll('[class*="absolute rounded-lg border bg-card"]');
    nodes.forEach((node) => {
      if (node instanceof HTMLElement) {
        expect(node.style.top).toBeTruthy();
        expect(node.style.left).toBeTruthy();
        expect(node.style.width).toBe('120px');
        expect(node.style.height).toBe('60px');
      }
    });
  });
});

describe(ErrorState, () => {
  it('should render with default props', () => {
    render(<ErrorState />);

    expect(screen.getByText('Failed to load graph')).toBeInTheDocument();
    expect(screen.getByText('An error occurred while loading the graph data.')).toBeInTheDocument();
  });

  it('should render with custom title and message', () => {
    render(<ErrorState title='Custom Error' message='This is a custom error message' />);

    expect(screen.getByText('Custom Error')).toBeInTheDocument();
    expect(screen.getByText('This is a custom error message')).toBeInTheDocument();
  });

  it('should show retry button when onRetry is provided', () => {
    const onRetry = vi.fn();
    render(<ErrorState onRetry={onRetry} />);

    const retryButton = screen.getByRole('button', { name: /retry/i });
    expect(retryButton).toBeInTheDocument();
  });

  it('should not show retry button when onRetry is not provided', () => {
    render(<ErrorState />);

    const retryButton = screen.queryByRole('button', { name: /retry/i });
    expect(retryButton).not.toBeInTheDocument();
  });

  it('should call onRetry when retry button is clicked', async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();

    render(<ErrorState onRetry={onRetry} />);

    const retryButton = screen.getByRole('button', { name: /retry/i });
    await user.click(retryButton);

    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it('should display error icon', () => {
    const { container } = render(<ErrorState />);

    // Lucide-react AlertCircle icon
    const icon = container.querySelector('svg');
    expect(icon).toBeInTheDocument();
    expect(icon).toHaveClass('text-destructive');
  });
});

describe(LoadingTransition, () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should show skeleton when loading', () => {
    render(
      <LoadingTransition isLoading>
        <div data-testid='content'>Content</div>
      </LoadingTransition>,
    );

    expect(screen.getByTestId('graph-skeleton')).toBeInTheDocument();
    expect(screen.queryByTestId('content')).not.toBeInTheDocument();
  });

  it('should show content when not loading', async () => {
    render(
      <LoadingTransition isLoading={false}>
        <div data-testid='content'>Content</div>
      </LoadingTransition>,
    );

    // Should show content immediately when not loading
    expect(screen.getByTestId('content')).toBeInTheDocument();
  });

  it('should transition from loading to content smoothly', async () => {
    const { rerender } = render(
      <LoadingTransition isLoading minDisplayTime={300}>
        <div data-testid='content'>Content</div>
      </LoadingTransition>,
    );

    // Should show skeleton initially
    expect(screen.getByTestId('graph-skeleton')).toBeInTheDocument();
    expect(screen.queryByTestId('content')).not.toBeInTheDocument();

    // Switch to loaded
    rerender(
      <LoadingTransition isLoading={false} minDisplayTime={300}>
        <div data-testid='content'>Content</div>
      </LoadingTransition>,
    );

    // Skeleton should fade out
    const skeleton = screen.getByTestId('graph-skeleton');
    expect(skeleton.parentElement).toHaveClass('opacity-0');

    // Fast-forward past minDisplayTime and run all timers
    await act(async () => {
      vi.runAllTimers();
      await Promise.resolve();
    });

    // Should show content after transition
    expect(screen.getByTestId('content')).toBeInTheDocument();
    expect(screen.queryByTestId('graph-skeleton')).not.toBeInTheDocument();
  });

  it('should reset to skeleton when switching back to loading', () => {
    const { rerender } = render(
      <LoadingTransition isLoading={false}>
        <div data-testid='content'>Content</div>
      </LoadingTransition>,
    );

    expect(screen.getByTestId('content')).toBeInTheDocument();

    // Switch back to loading
    rerender(
      <LoadingTransition isLoading>
        <div data-testid='content'>Content</div>
      </LoadingTransition>,
    );

    expect(screen.getByTestId('graph-skeleton')).toBeInTheDocument();
    expect(screen.queryByTestId('content')).not.toBeInTheDocument();
  });

  it('should respect custom minDisplayTime', async () => {
    const { rerender } = render(
      <LoadingTransition isLoading minDisplayTime={500}>
        <div data-testid='content'>Content</div>
      </LoadingTransition>,
    );

    rerender(
      <LoadingTransition isLoading={false} minDisplayTime={500}>
        <div data-testid='content'>Content</div>
      </LoadingTransition>,
    );

    // Advance less than minDisplayTime
    await act(async () => {
      vi.advanceTimersByTime(300);
      await Promise.resolve();
    });

    // Skeleton should still be visible
    expect(screen.getByTestId('graph-skeleton')).toBeInTheDocument();

    // Advance past minDisplayTime and run all remaining timers
    await act(async () => {
      vi.runAllTimers();
      await Promise.resolve();
    });

    // Content should now be visible
    expect(screen.getByTestId('content')).toBeInTheDocument();
  });
});

describe(LoadingProgress, () => {
  it('should render with progress information', () => {
    render(<LoadingProgress loaded={50} total={100} />);

    expect(screen.getByText('Loading graph data')).toBeInTheDocument();
    expect(screen.getByText('50%')).toBeInTheDocument();
    expect(screen.getByText('50 / 100 nodes')).toBeInTheDocument();
  });

  it('should render with custom label', () => {
    render(<LoadingProgress loaded={30} total={100} label='Loading nodes' />);

    expect(screen.getByText('Loading nodes')).toBeInTheDocument();
  });

  it('should calculate progress percentage correctly', () => {
    render(<LoadingProgress loaded={75} total={100} />);

    expect(screen.getByText('75%')).toBeInTheDocument();
  });

  it('should handle zero total without crashing', () => {
    render(<LoadingProgress loaded={0} total={0} />);

    expect(screen.getByText('0%')).toBeInTheDocument();
    expect(screen.getByText('0 / 0 nodes')).toBeInTheDocument();
  });

  it('should format large numbers with locale string', () => {
    render(<LoadingProgress loaded={1234} total={5678} />);

    expect(screen.getByText(/1,234 \/ 5,678 nodes/)).toBeInTheDocument();
  });

  it('should round progress percentage', () => {
    render(<LoadingProgress loaded={33} total={100} />);

    expect(screen.getByText('33%')).toBeInTheDocument();
  });

  it('should have progress bar with correct value', () => {
    const { container } = render(<LoadingProgress loaded={60} total={100} />);

    // Progress component uses Radix UI's Progress primitive
    const progressRoot = container.querySelector('[role="progressbar"]');
    expect(progressRoot).toBeInTheDocument();
  });
});

describe('Loading States Integration', () => {
  it('should work together in a complete loading flow', async () => {
    const onRetry = vi.fn();
    const { rerender } = render(
      <LoadingTransition isLoading>
        <div data-testid='content'>Graph Content</div>
      </LoadingTransition>,
    );

    // Initial loading state
    expect(screen.getByTestId('graph-skeleton')).toBeInTheDocument();

    // Simulate load complete
    rerender(
      <LoadingTransition isLoading={false}>
        <div data-testid='content'>Graph Content</div>
      </LoadingTransition>,
    );

    // Should show content
    await waitFor(() => {
      expect(screen.getByTestId('content')).toBeInTheDocument();
    });

    // Simulate error state
    rerender(
      <ErrorState title='Load Failed' message='Could not load graph data' onRetry={onRetry} />,
    );

    expect(screen.getByText('Load Failed')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });
});
