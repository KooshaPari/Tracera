import { render, renderHook, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { PerformanceChart } from '@/components/graph/PerformanceChart';
import { PerformanceOverlay } from '@/components/graph/PerformanceOverlay';
import { PerformanceStats } from '@/components/graph/PerformanceStats';
import { useFPSMonitor } from '@/hooks/useFPSMonitor';
import { useMemoryMonitor } from '@/hooks/useMemoryMonitor';

describe(PerformanceStats, () => {
  it('renders compact variant with FPS and node counts', () => {
    render(
      <PerformanceStats
        fps={60}
        nodeCount={1000}
        edgeCount={2000}
        visibleNodeCount={250}
        visibleEdgeCount={500}
        variant='compact'
      />,
    );

    expect(screen.getByText('60 FPS')).toBeInTheDocument();
    expect(screen.getByText('250/1000 nodes')).toBeInTheDocument();
    expect(screen.getByText('75% culled')).toBeInTheDocument();
  });

  it('renders detailed variant with all metrics', () => {
    render(
      <PerformanceStats
        fps={45}
        nodeCount={1000}
        edgeCount={2000}
        visibleNodeCount={750}
        visibleEdgeCount={1500}
        memoryUsage={45.2}
        renderTime={12.5}
        variant='detailed'
      />,
    );

    expect(screen.getByText('45 FPS')).toBeInTheDocument();
    expect(screen.getByText('750/1000')).toBeInTheDocument();
    expect(screen.getByText('1500/2000')).toBeInTheDocument();
    expect(screen.getByText('45.2 MB')).toBeInTheDocument();
    expect(screen.getByText('12.5 ms')).toBeInTheDocument();
  });

  it('applies correct FPS color classes', () => {
    render(
      <PerformanceStats
        fps={60}
        nodeCount={100}
        edgeCount={100}
        visibleNodeCount={50}
        visibleEdgeCount={50}
        variant='compact'
      />,
    );

    // Green for >= 55 FPS
    let fpsElement = screen.getByText('60 FPS');
    expect(fpsElement).toHaveClass('text-green-600');

    // Yellow for 30-54 FPS
    rerender(
      <PerformanceStats
        fps={40}
        nodeCount={100}
        edgeCount={100}
        visibleNodeCount={50}
        visibleEdgeCount={50}
        variant='compact'
      />,
    );
    fpsElement = screen.getByText('40 FPS');
    expect(fpsElement).toHaveClass('text-yellow-600');

    // Red for < 30 FPS
    rerender(
      <PerformanceStats
        fps={20}
        nodeCount={100}
        edgeCount={100}
        visibleNodeCount={50}
        visibleEdgeCount={50}
        variant='compact'
      />,
    );
    fpsElement = screen.getByText('20 FPS');
    expect(fpsElement).toHaveClass('text-red-600');
  });

  it('calculates culling percentage correctly', () => {
    render(
      <PerformanceStats
        fps={60}
        nodeCount={1000}
        edgeCount={2000}
        visibleNodeCount={200}
        visibleEdgeCount={400}
        variant='compact'
      />,
    );

    // (1 - 200/1000) * 100 = 80%
    expect(screen.getByText('80% culled')).toBeInTheDocument();
  });

  it('does not show culling when no nodes are culled', () => {
    render(
      <PerformanceStats
        fps={60}
        nodeCount={1000}
        edgeCount={2000}
        visibleNodeCount={1000}
        visibleEdgeCount={2000}
        variant='compact'
      />,
    );

    expect(screen.queryByText(/culled/)).not.toBeInTheDocument();
  });

  it('does not render memory or render time when not provided', () => {
    render(
      <PerformanceStats
        fps={60}
        nodeCount={1000}
        edgeCount={2000}
        visibleNodeCount={500}
        visibleEdgeCount={1000}
        variant='detailed'
      />,
    );

    expect(screen.queryByText(/MB/)).not.toBeInTheDocument();
    expect(screen.queryByText(/ms/)).not.toBeInTheDocument();
  });
});

describe(PerformanceOverlay, () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  it('renders at specified position', () => {
    render(
      <PerformanceOverlay
        nodeCount={1000}
        edgeCount={2000}
        visibleNodeCount={250}
        visibleEdgeCount={500}
        position='top-right'
      />,
    );

    let overlay = container.querySelector('.absolute');
    expect(overlay).toHaveClass('top-4', 'right-4');

    rerender(
      <PerformanceOverlay
        nodeCount={1000}
        edgeCount={2000}
        visibleNodeCount={250}
        visibleEdgeCount={500}
        position='bottom-left'
      />,
    );

    overlay = container.querySelector('.absolute');
    expect(overlay).toHaveClass('bottom-4', 'left-4');
  });

  it('forwards variant to PerformanceStats', () => {
    render(
      <PerformanceOverlay
        nodeCount={1000}
        edgeCount={2000}
        visibleNodeCount={250}
        visibleEdgeCount={500}
        variant='compact'
      />,
    );

    expect(screen.getByText(/FPS/)).toBeInTheDocument();

    rerender(
      <PerformanceOverlay
        nodeCount={1000}
        edgeCount={2000}
        visibleNodeCount={250}
        visibleEdgeCount={500}
        variant='detailed'
      />,
    );

    expect(screen.getByText('Performance')).toBeInTheDocument();
  });
});

describe(PerformanceChart, () => {
  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D;

  beforeEach(() => {
    // Mock canvas and context
    canvas = document.createElement('canvas');
    ctx = {
      beginPath: vi.fn(),
      clearRect: vi.fn(),
      fillText: vi.fn(),
      lineTo: vi.fn(),
      moveTo: vi.fn(),
      stroke: vi.fn(),
    } as any;

    canvas.getContext = vi.fn(() => ctx);
    vi.spyOn(document, 'createElement').mockReturnValue(canvas);
  });

  it('renders canvas with correct dimensions', () => {
    render(<PerformanceChart fps={60} width={300} height={80} />);

    const canvasElement = container.querySelector('canvas');
    expect(canvasElement).toBeInTheDocument();
    expect(canvasElement).toHaveAttribute('width', '300');
    expect(canvasElement).toHaveAttribute('height', '80');
  });

  it('draws FPS value on canvas', () => {
    render(<PerformanceChart fps={45} />);

    expect(vi.mocked(ctx).fillText).toHaveBeenCalledWith(
      expect.stringContaining('45 FPS'),
      expect.any(Number),
      expect.any(Number),
    );
  });

  it('uses correct color based on FPS', () => {
    render(<PerformanceChart fps={60} />);

    // Green for >= 55
    expect(ctx.strokeStyle).toBe('#10b981');

    rerender(<PerformanceChart fps={40} />);
    // Yellow for 30-54
    expect(ctx.strokeStyle).toBe('#f59e0b');

    rerender(<PerformanceChart fps={20} />);
    // Red for < 30
    expect(ctx.strokeStyle).toBe('#ef4444');
  });

  it('maintains FPS history', () => {
    render(<PerformanceChart fps={60} />);

    rerender(<PerformanceChart fps={55} />);
    rerender(<PerformanceChart fps={50} />);

    // Should have drawn multiple points
    expect(vi.mocked(ctx).lineTo).toHaveBeenCalled();
  });
});

describe(useFPSMonitor, () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  it('starts with default stats', () => {
    const { result } = renderHook(() => useFPSMonitor());

    expect(result.current).toEqual({
      average: 60,
      current: 60,
      max: 60,
      min: 60,
    });
  });

  it('can be disabled', () => {
    const { result } = renderHook(() => useFPSMonitor(false));

    expect(result.current).toEqual({
      average: 60,
      current: 60,
      max: 60,
      min: 60,
    });
  });

  it('uses requestAnimationFrame for updates', () => {
    const rafSpy = vi.spyOn(globalThis, 'requestAnimationFrame');

    renderHook(() => useFPSMonitor(true));

    expect(rafSpy).toHaveBeenCalled();
  });

  it('cancels animation frame on unmount', () => {
    const cancelSpy = vi.spyOn(globalThis, 'cancelAnimationFrame');

    const { unmount } = renderHook(() => useFPSMonitor(true));
    unmount();

    expect(cancelSpy).toHaveBeenCalled();
  });
});

describe(useMemoryMonitor, () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  it('returns null when memory API is not available', () => {
    const { result } = renderHook(() => useMemoryMonitor());

    expect(result.current).toBeNull();
  });

  it.skip('returns memory stats when API is available', async () => {
    // Mock performance.memory (Chrome only)
    Object.defineProperty(performance, 'memory', {
      configurable: true,
      value: {
        usedJSHeapSize: 50 * 1024 * 1024, // 50 MB
        totalJSHeapSize: 100 * 1024 * 1024, // 100 MB
        jsHeapSizeLimit: 200 * 1024 * 1024, // 200 MB
      },
    });

    const { result } = renderHook(() => useMemoryMonitor());

    await waitFor(() => {
      expect(result.current).toEqual({
        jsHeapSizeLimit: 200,
        totalJSHeapSize: 100,
        usage: 0.25,
        usedJSHeapSize: 50,
      });
    });
  });

  it('can be disabled', () => {
    const { result } = renderHook(() => useMemoryMonitor(false));

    expect(result.current).toBeNull();
  });

  it('uses custom interval', () => {
    const setIntervalSpy = vi.spyOn(globalThis, 'setInterval');

    renderHook(() => useMemoryMonitor(true, 2000));

    expect(setIntervalSpy).toHaveBeenCalledWith(expect.any(Function), 2000);
  });

  it('clears interval on unmount', () => {
    const clearIntervalSpy = vi.spyOn(globalThis, 'clearInterval');

    const { unmount } = renderHook(() => useMemoryMonitor(true));
    unmount();

    expect(clearIntervalSpy).toHaveBeenCalled();
  });
});

describe('Integration Tests', () => {
  it('PerformanceOverlay integrates hooks correctly', async () => {
    render(
      <PerformanceOverlay
        nodeCount={1000}
        edgeCount={2000}
        visibleNodeCount={250}
        visibleEdgeCount={500}
      />,
    );

    await waitFor(() => {
      expect(screen.getByText(/FPS/)).toBeInTheDocument();
      expect(screen.getByText(/nodes/)).toBeInTheDocument();
    });
  });

  it('handles rapid updates without errors', () => {
    render(
      <PerformanceStats
        fps={60}
        nodeCount={1000}
        edgeCount={2000}
        visibleNodeCount={500}
        visibleEdgeCount={1000}
      />,
    );

    for (let i = 0; i < 100; i++) {
      rerender(
        <PerformanceStats
          fps={60 - i * 0.1}
          nodeCount={1000}
          edgeCount={2000}
          visibleNodeCount={500 - i}
          visibleEdgeCount={1000 - i * 2}
        />,
      );
    }

    expect(screen.getByText(/FPS/)).toBeInTheDocument();
  });
});
