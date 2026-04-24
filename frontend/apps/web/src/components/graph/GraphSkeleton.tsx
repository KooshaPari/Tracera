import { memo } from 'react';

interface GraphSkeletonProps {
  nodeCount?: number;
  edgeCount?: number;
}

export const GraphSkeleton = memo(function GraphSkeleton({
  nodeCount = 20,
  edgeCount = 30,
}: GraphSkeletonProps) {
  return (
    <div
      className='bg-background/50 relative h-full w-full animate-pulse'
      data-testid='graph-skeleton'
    >
      {/* Skeleton nodes */}
      {Array.from({ length: nodeCount }).map((_, i) => (
        <div
          key={`node-${i}`}
          className='bg-card absolute rounded-lg border'
          style={{
            height: '60px',
            left: `${Math.floor(i / 5) * 20 + 10}%`,
            top: `${(i % 5) * 20 + 10}%`,
            width: '120px',
          }}
        >
          <div className='space-y-2 p-3'>
            <div className='bg-muted h-4 w-3/4 rounded' />
            <div className='bg-muted/60 h-3 w-1/2 rounded' />
          </div>
        </div>
      ))}

      {/* Skeleton edges */}
      <svg className='pointer-events-none absolute inset-0'>
        {Array.from({ length: edgeCount }).map((_, i) => {
          const sourceIdx = i % nodeCount;
          const targetIdx = (i + 1) % nodeCount;
          return (
            <line
              key={`edge-${i}`}
              x1={`${Math.floor(sourceIdx / 5) * 20 + 15}%`}
              y1={`${(sourceIdx % 5) * 20 + 15}%`}
              x2={`${Math.floor(targetIdx / 5) * 20 + 15}%`}
              y2={`${(targetIdx % 5) * 20 + 15}%`}
              stroke='currentColor'
              strokeWidth='2'
              className='text-muted'
              opacity='0.3'
            />
          );
        })}
      </svg>
    </div>
  );
});
