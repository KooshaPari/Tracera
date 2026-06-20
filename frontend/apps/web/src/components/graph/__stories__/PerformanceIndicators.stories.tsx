import type { Meta, StoryObj } from '@storybook/react';

import { useEffect, useState } from 'react';

import { useFPSMonitor } from '@/hooks/useFPSMonitor';

import { PerformanceChart } from '../PerformanceChart';
import { PerformanceOverlay } from '../PerformanceOverlay';
import { PerformanceStats } from '../PerformanceStats';

const meta = {
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs', 'skip-tests'],
  title: 'Graph/Performance Indicators',
} satisfies Meta;

export default meta;

// PerformanceStats Stories
export const CompactStats: StoryObj = {
  render: () => (
    <PerformanceStats
      fps={58.5}
      nodeCount={1000}
      edgeCount={2000}
      visibleNodeCount={250}
      visibleEdgeCount={500}
      variant='compact'
    />
  ),
};

export const DetailedStats: StoryObj = {
  render: () => (
    <PerformanceStats
      fps={58.5}
      nodeCount={1000}
      edgeCount={2000}
      visibleNodeCount={250}
      visibleEdgeCount={500}
      memoryUsage={45.2}
      renderTime={12.5}
      variant='detailed'
    />
  ),
};

export const HighPerformance: StoryObj = {
  render: () => (
    <PerformanceStats
      fps={60}
      nodeCount={1000}
      edgeCount={2000}
      visibleNodeCount={100}
      visibleEdgeCount={200}
      memoryUsage={25.5}
      renderTime={8.2}
      variant='detailed'
    />
  ),
};

export const MediumPerformance: StoryObj = {
  render: () => (
    <PerformanceStats
      fps={40}
      nodeCount={5000}
      edgeCount={10_000}
      visibleNodeCount={800}
      visibleEdgeCount={1600}
      memoryUsage={85.5}
      renderTime={22.5}
      variant='detailed'
    />
  ),
};

export const LowPerformance: StoryObj = {
  render: () => (
    <PerformanceStats
      fps={18}
      nodeCount={10_000}
      edgeCount={20_000}
      visibleNodeCount={5000}
      visibleEdgeCount={10_000}
      memoryUsage={150.2}
      renderTime={55.5}
      variant='detailed'
    />
  ),
};

export const NoCulling: StoryObj = {
  render: () => (
    <PerformanceStats
      fps={45}
      nodeCount={500}
      edgeCount={1000}
      visibleNodeCount={500}
      visibleEdgeCount={1000}
      variant='compact'
    />
  ),
};

// PerformanceChart Stories
export const ChartStable: StoryObj = {
  render: () => {
    const [fps, setFps] = useState(60);

    useEffect(() => {
      const interval = setInterval(() => {
        setFps(60 + Math.random() * 2 - 1); // Slight variation around 60
      }, 16);
      return () => {
        clearInterval(interval);
      };
    }, []);

    return <PerformanceChart fps={fps} width={300} height={80} />;
  },
};

export const ChartFluctuating: StoryObj = {
  render: () => {
    const [fps, setFps] = useState(60);

    useEffect(() => {
      const interval = setInterval(() => {
        setFps(40 + Math.random() * 30); // Varies between 40-70
      }, 16);
      return () => {
        clearInterval(interval);
      };
    }, []);

    return <PerformanceChart fps={fps} width={300} height={80} />;
  },
};

export const ChartDegrading: StoryObj = {
  render: () => {
    const [fps, setFps] = useState(60);

    useEffect(() => {
      let currentFps = 60;
      const interval = setInterval(() => {
        currentFps = Math.max(15, currentFps - 0.5); // Gradually decrease
        setFps(currentFps);
      }, 100);
      return () => {
        clearInterval(interval);
      };
    }, []);

    return <PerformanceChart fps={fps} width={300} height={80} />;
  },
};

export const ChartRecovering: StoryObj = {
  render: () => {
    const [fps, setFps] = useState(20);

    useEffect(() => {
      let currentFps = 20;
      const interval = setInterval(() => {
        currentFps = Math.min(60, currentFps + 0.5); // Gradually increase
        setFps(currentFps);
      }, 100);
      return () => {
        clearInterval(interval);
      };
    }, []);

    return <PerformanceChart fps={fps} width={300} height={80} />;
  },
};

// PerformanceOverlay Stories
export const OverlayTopRight: StoryObj = {
  render: () => (
    <div className='bg-muted relative h-[600px] w-[800px] rounded border'>
      <PerformanceOverlay
        nodeCount={1000}
        edgeCount={2000}
        visibleNodeCount={250}
        visibleEdgeCount={500}
        position='top-right'
        variant='compact'
      />
    </div>
  ),
};

export const OverlayTopLeft: StoryObj = {
  render: () => (
    <div className='bg-muted relative h-[600px] w-[800px] rounded border'>
      <PerformanceOverlay
        nodeCount={1000}
        edgeCount={2000}
        visibleNodeCount={250}
        visibleEdgeCount={500}
        position='top-left'
        variant='detailed'
      />
    </div>
  ),
};

export const OverlayBottomRight: StoryObj = {
  render: () => (
    <div className='bg-muted relative h-[600px] w-[800px] rounded border'>
      <PerformanceOverlay
        nodeCount={1000}
        edgeCount={2000}
        visibleNodeCount={250}
        visibleEdgeCount={500}
        position='bottom-right'
        variant='detailed'
      />
    </div>
  ),
};

export const OverlayBottomLeft: StoryObj = {
  render: () => (
    <div className='bg-muted relative h-[600px] w-[800px] rounded border'>
      <PerformanceOverlay
        nodeCount={1000}
        edgeCount={2000}
        visibleNodeCount={250}
        visibleEdgeCount={500}
        position='bottom-left'
        variant='compact'
      />
    </div>
  ),
};

// Real-time FPS Monitoring
export const LiveFPSMonitor: StoryObj = {
  render: () => {
    const fpsStats = useFPSMonitor(true);

    return (
      <div className='space-y-4'>
        <PerformanceStats
          fps={fpsStats.current}
          nodeCount={1000}
          edgeCount={2000}
          visibleNodeCount={250}
          visibleEdgeCount={500}
          variant='detailed'
        />
        <div className='text-muted-foreground text-sm'>
          <p>Average: {fpsStats.average.toFixed(1)} FPS</p>
          <p>Min: {fpsStats.min.toFixed(1)} FPS</p>
          <p>Max: {fpsStats.max.toFixed(1)} FPS</p>
        </div>
      </div>
    );
  },
};

export const LiveChart: StoryObj = {
  render: () => {
    const fpsStats = useFPSMonitor(true);

    return (
      <div className='space-y-2'>
        <PerformanceChart fps={fpsStats.current} width={400} height={100} />
        <div className='text-muted-foreground text-center text-xs'>
          Current: {fpsStats.current.toFixed(1)} FPS | Average: {fpsStats.average.toFixed(1)} FPS
        </div>
      </div>
    );
  },
};

// Combined Dashboard
export const CompleteDashboard: StoryObj = {
  render: () => {
    const fpsStats = useFPSMonitor(true);
    const [nodeCount] = useState(1000);
    const [visibleCount] = useState(250);

    return (
      <div className='bg-muted relative h-[600px] w-[1000px] rounded border p-4'>
        <div className='absolute top-4 right-4 space-y-4'>
          <PerformanceStats
            fps={fpsStats.current}
            nodeCount={nodeCount}
            edgeCount={nodeCount * 2}
            visibleNodeCount={visibleCount}
            visibleEdgeCount={visibleCount * 2}
            variant='detailed'
          />
          <PerformanceChart fps={fpsStats.current} width={256} height={80} />
        </div>

        <div className='text-muted-foreground absolute bottom-4 left-4 text-sm'>
          <p>
            FPS Range: {fpsStats.min.toFixed(1)} - {fpsStats.max.toFixed(1)}
          </p>
          <p>Average FPS: {fpsStats.average.toFixed(1)}</p>
        </div>
      </div>
    );
  },
};

// Stress Test Scenarios
export const StressTestSmall: StoryObj = {
  render: () => (
    <PerformanceStats
      fps={60}
      nodeCount={100}
      edgeCount={200}
      visibleNodeCount={100}
      visibleEdgeCount={200}
      memoryUsage={15.5}
      renderTime={5.2}
      variant='detailed'
    />
  ),
};

export const StressTestMedium: StoryObj = {
  render: () => (
    <PerformanceStats
      fps={45}
      nodeCount={1000}
      edgeCount={2000}
      visibleNodeCount={500}
      visibleEdgeCount={1000}
      memoryUsage={55.5}
      renderTime={18.2}
      variant='detailed'
    />
  ),
};

export const StressTestLarge: StoryObj = {
  render: () => (
    <PerformanceStats
      fps={28}
      nodeCount={5000}
      edgeCount={10_000}
      visibleNodeCount={2500}
      visibleEdgeCount={5000}
      memoryUsage={125.5}
      renderTime={35.2}
      variant='detailed'
    />
  ),
};

export const StressTestExtraLarge: StoryObj = {
  render: () => (
    <PerformanceStats
      fps={15}
      nodeCount={10_000}
      edgeCount={20_000}
      visibleNodeCount={8000}
      visibleEdgeCount={16_000}
      memoryUsage={250.5}
      renderTime={65.2}
      variant='detailed'
    />
  ),
};

// Comparison View
export const ComparisonView: StoryObj = {
  render: () => (
    <div className='grid grid-cols-2 gap-4'>
      <div>
        <h3 className='mb-2 text-sm font-medium'>Before Optimization</h3>
        <PerformanceStats
          fps={25}
          nodeCount={5000}
          edgeCount={10_000}
          visibleNodeCount={5000}
          visibleEdgeCount={10_000}
          memoryUsage={180.5}
          renderTime={40.2}
          variant='detailed'
        />
      </div>
      <div>
        <h3 className='mb-2 text-sm font-medium'>After Optimization</h3>
        <PerformanceStats
          fps={58}
          nodeCount={5000}
          edgeCount={10_000}
          visibleNodeCount={500}
          visibleEdgeCount={1000}
          memoryUsage={65.5}
          renderTime={17.2}
          variant='detailed'
        />
      </div>
    </div>
  ),
};

// Interactive Toggle
export const InteractiveToggle: StoryObj = {
  render: () => {
    const [variant, setVariant] = useState<'compact' | 'detailed'>('compact');

    return (
      <div className='space-y-4'>
        <div className='flex gap-2'>
          <button
            className='bg-primary text-primary-foreground rounded px-3 py-1 text-sm'
            onClick={() => {
              setVariant(variant === 'compact' ? 'detailed' : 'compact');
            }}
          >
            Toggle Variant
          </button>
        </div>
        <PerformanceStats
          fps={58.5}
          nodeCount={1000}
          edgeCount={2000}
          visibleNodeCount={250}
          visibleEdgeCount={500}
          memoryUsage={45.2}
          renderTime={12.5}
          variant={variant}
        />
      </div>
    );
  },
};
