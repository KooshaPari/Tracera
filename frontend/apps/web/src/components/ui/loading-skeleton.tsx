/**
 * Enterprise Loading Skeletons
 *
 * Replaces inline loading states with polished, animated skeletons
 * Professional feel that matches enterprise applications like Jira/Linear
 */

import { motion } from 'framer-motion';

import { cn } from '@/lib/utils';

const TABLE_ROW_DELAY_STEP = 0.02;
const TRANSITION_DELAY_STEP = 0.1;
const GRAPH_POS_RANGE = 300;
const GRAPH_POS_OFFSET = 150;
const SCALE_BOUNCE = 1.2;
const CONTENT_ANIM_DELAY = 0.3;

interface SkeletonProps {
  className?: string;
  animate?: boolean;
}

export const Skeleton = ({ className, animate = true }: SkeletonProps) => (
  <motion.div
    className={cn('animate-pulse rounded-md bg-muted', animate && 'shimmer-effect', className)}
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    transition={{ duration: 0.15 }}
  >
    <style
      dangerouslySetInnerHTML={{
        __html: `
        .shimmer-effect {
          background: linear-gradient(
            90deg,
            hsl(var(--muted)) 0%,
            hsl(var(--muted) / 0.8) 50%,
            hsl(var(--muted)) 100%
          );
          background-size: 200% 100%;
          animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
      `,
      }}
    />
  </motion.div>
);

// Card skeleton for projects/items
export function CardSkeleton() {
  return (
    <motion.div
      className='bg-card space-y-4 rounded-lg border p-6'
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      <div className='flex items-center space-x-4'>
        <Skeleton className='h-12 w-12 rounded-full' />
        <div className='flex-1 space-y-2'>
          <Skeleton className='h-4 w-3/4' />
          <Skeleton className='h-3 w-1/2' />
        </div>
        <Skeleton className='h-6 w-16 rounded-full' />
      </div>
      <Skeleton className='h-4 w-full' />
      <Skeleton className='h-4 w-2/3' />
    </motion.div>
  );
}

// Table skeleton for data grids
export function TableSkeleton({ rows = 10, cols = 6 }: { rows?: number; cols?: number }) {
  return (
    <div className='w-full'>
      <div className='mb-4 border-b pb-4'>
        <div className='grid gap-4' style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
          {Array.from({ length: cols }).map((_, i) => (
            <Skeleton key={i} className='h-4' animate={false} />
          ))}
        </div>
      </div>

      <div className='space-y-2'>
        {Array.from({ length: rows }).map((_, rowIndex) => (
          <motion.div
            key={rowIndex}
            className='border-b py-2'
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: rowIndex * TABLE_ROW_DELAY_STEP, duration: 0.15 }}
          >
            <div className='grid gap-4' style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
              {Array.from({ length: cols }).map((_, colIndex) => (
                <Skeleton key={colIndex} className='h-4' animate={colIndex === 0} />
              ))}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

// Kanban board skeleton
export function KanbanSkeleton({ columns = 4 }: { columns?: number }) {
  return (
    <div className='flex gap-4 pb-4'>
      {Array.from({ length: columns }).map((_, i) => (
        <motion.div
          key={i}
          className='min-w-0 flex-1'
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: i * TRANSITION_DELAY_STEP, duration: 0.2 }}
        >
          <div className='bg-muted/30 rounded-lg border p-4'>
            <Skeleton className='mb-4 h-4 w-3/4' animate={false} />
            <div className='space-y-2'>
              {Array.from({ length: Math.floor(Math.random() * 5) + 3 }).map((_, j) => (
                <CardSkeleton key={j} />
              ))}
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}

// Graph visualization skeleton
export function GraphSkeleton() {
  return (
    <motion.div
      className='flex h-full min-h-[400px] items-center justify-center'
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div className='relative'>
        {/* Simulate nodes */}
        {Array.from({ length: 8 }).map((_, i) => (
          <motion.div
            key={i}
            className='absolute'
            style={{
              left: `${Math.random() * GRAPH_POS_RANGE - GRAPH_POS_OFFSET}px`,
              top: `${Math.random() * GRAPH_POS_RANGE - GRAPH_POS_OFFSET}px`,
            }}
            initial={{ scale: 0 }}
            animate={{ scale: [0, SCALE_BOUNCE, 1] }}
            transition={{
              delay: i * TRANSITION_DELAY_STEP,
              duration: 0.5,
              repeat: Infinity,
              repeatType: 'reverse',
            }}
          >
            <Skeleton className='h-8 w-8 rounded-full' animate={false} />
          </motion.div>
        ))}
        <div className='flex min-h-[400px] min-w-[400px] items-center justify-center'>
          <Skeleton className='h-6 w-32' animate={false} />
        </div>
      </div>
    </motion.div>
  );
}

// Dashboard skeleton with multiple sections
export function DashboardSkeleton() {
  return (
    <div className='space-y-6'>
      {/* Metrics row */}
      <div className='grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4'>
        {Array.from({ length: 4 }).map((_, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * TRANSITION_DELAY_STEP }}
          >
            <div className='bg-card rounded-lg border p-6'>
              <Skeleton className='mb-2 h-4 w-20' animate={false} />
              <Skeleton className='h-8 w-16' />
            </div>
          </motion.div>
        ))}
      </div>

      {/* Main content */}
      <div className='grid grid-cols-1 gap-6 lg:grid-cols-3'>
        {/* Recent projects */}
        <motion.div
          className='lg:col-span-2'
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: CONTENT_ANIM_DELAY }}
        >
          <div className='bg-card rounded-lg border p-6'>
            <Skeleton className='mb-4 h-6 w-32' animate={false} />
            <div className='space-y-2'>
              {Array.from({ length: 5 }).map((_, i) => (
                <CardSkeleton key={i} />
              ))}
            </div>
          </div>
        </motion.div>

        {/* Activity feed */}
        <motion.div
          initial={{ opacity: 0, x: 10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className='bg-card rounded-lg border p-6'>
            <Skeleton className='mb-4 h-6 w-24' animate={false} />
            <div className='space-y-3'>
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className='flex items-center space-x-3'>
                  <Skeleton className='h-8 w-8 rounded-full' />
                  <div className='flex-1 space-y-1'>
                    <Skeleton className='h-3 w-full' />
                    <Skeleton className='h-2 w-3/4' />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

// Professional loading spinner for overlays
export function LoadingOverlay({ message }: { message?: string }) {
  return (
    <motion.div
      className='bg-background/80 fixed inset-0 z-50 flex items-center justify-center backdrop-blur-sm'
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <motion.div
        className='bg-card flex flex-col items-center space-y-4 rounded-lg border p-6 shadow-lg'
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
      >
        <div className='relative'>
          <div className='border-primary h-12 w-12 animate-spin rounded-full border-4 border-t-transparent' />
          <div className='border-primary/20 absolute inset-0 h-12 w-12 animate-spin rounded-full border-4 border-t-transparent' />
        </div>
        {message && <p className='text-muted-foreground max-w-sm text-center'>{message}</p>}
      </motion.div>
    </motion.div>
  );
}
