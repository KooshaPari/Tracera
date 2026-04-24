/**
 * CoverageHeatmap - Requirement coverage visualization grid
 * Shows coverage intensity with hover details and click navigation
 */

import { motion } from 'framer-motion';
import { ChevronRight } from 'lucide-react';
import { useState } from 'react';

import { cn } from '@/lib/utils';

// Coverage threshold constants
const COVERAGE_EXCELLENT = 90;
const COVERAGE_GOOD = 70;
const COVERAGE_FAIR = 50;
const COVERAGE_MODERATE = 30;
const COVERAGE_LOW = 10;
const COVERAGE_VERY_LOW = 20;
const COVERAGE_MODERATE_LOW = 40;
const COVERAGE_MODERATE_HIGH = 60;

// Animation constants
const ANIMATION_DURATION = 0.3;
const CELL_ANIMATION_DELAY_MS = 10;
const HOVER_SCALE = 1.05;
const TAP_SCALE = 0.95;

interface CoverageCell {
  id: string;
  label: string;
  coverage: number; // 0-100
  testCases?: number;
  adrs?: number;
  contracts?: number;
  linked?: boolean;
}

interface CoverageHeatmapProps {
  data: CoverageCell[];
  onCellClick?: (cell: CoverageCell) => void;
  columns?: number;
  className?: string;
}

const getCoverageColor = (coverage: number): string => {
  if (coverage >= COVERAGE_EXCELLENT) {
    return 'bg-emerald-600';
  }
  if (coverage >= COVERAGE_GOOD) {
    return 'bg-emerald-500';
  }
  if (coverage >= COVERAGE_FAIR) {
    return 'bg-amber-500';
  }
  if (coverage >= COVERAGE_MODERATE) {
    return 'bg-orange-500';
  }
  if (coverage >= COVERAGE_LOW) {
    return 'bg-red-500';
  }
  return 'bg-slate-300';
};

const getCoverageOpacity = (coverage: number): string => {
  if (coverage === 0) {
    return 'opacity-30';
  }
  if (coverage < COVERAGE_VERY_LOW) {
    return 'opacity-40';
  }
  if (coverage < COVERAGE_MODERATE_LOW) {
    return 'opacity-60';
  }
  if (coverage < COVERAGE_MODERATE_HIGH) {
    return 'opacity-75';
  }
  return 'opacity-100';
};

export const CoverageHeatmap = ({
  data,
  onCellClick,
  columns = 8,
  className,
}: CoverageHeatmapProps) => {
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [hoveredDetails, setHoveredDetails] = useState<CoverageCell | null>(null);

  const handleMouseEnter = (cell: CoverageCell) => {
    setHoveredId(cell.id);
    setHoveredDetails(cell);
  };

  const handleMouseLeave = () => {
    setHoveredId(null);
    setHoveredDetails(null);
  };

  const handleCellClick = (cell: CoverageCell) => {
    onCellClick?.(cell);
  };

  // Calculate summary stats
  const totalItems = data.length;
  const avgCoverage = Math.round(data.reduce((sum, c) => sum + c.coverage, 0) / totalItems);
  const fullyCovered = data.filter((c) => c.coverage >= COVERAGE_EXCELLENT).length;
  const uncovered = data.filter((c) => c.coverage === 0).length;

  return (
    <motion.div
      className={cn('space-y-4', className)}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: ANIMATION_DURATION }}
    >
      {/* Summary Stats */}
      <div className='grid grid-cols-4 gap-3 text-xs'>
        <div className='bg-muted/30 rounded-lg p-3'>
          <div className='text-muted-foreground'>Total Items</div>
          <div className='text-xl font-bold'>{totalItems}</div>
        </div>
        <div className='bg-muted/30 rounded-lg p-3'>
          <div className='text-muted-foreground'>Avg Coverage</div>
          <div className='text-xl font-bold'>{avgCoverage}%</div>
        </div>
        <div className='bg-muted/30 rounded-lg p-3'>
          <div className='text-muted-foreground'>Fully Covered</div>
          <div className='text-xl font-bold'>{fullyCovered}</div>
        </div>
        <div className='bg-muted/30 rounded-lg p-3'>
          <div className='text-muted-foreground'>Uncovered</div>
          <div className='text-xl font-bold'>{uncovered}</div>
        </div>
      </div>

      {/* Heatmap Grid */}
      <div className='bg-card rounded-lg border p-4'>
        <div
          className='grid gap-2'
          style={{
            gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))`,
          }}
        >
          {data.map((cell, idx) => (
            <motion.div
              key={cell.id}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: idx * CELL_ANIMATION_DELAY_MS }}
              onMouseEnter={() => {
                handleMouseEnter(cell);
              }}
              onMouseLeave={handleMouseLeave}
              className='relative'
            >
              <motion.button
                onClick={() => {
                  handleCellClick(cell);
                }}
                className={cn(
                  'w-full aspect-square rounded-lg transition-all',
                  'border border-border/50 hover:border-primary',
                  'cursor-pointer relative group overflow-hidden',
                  getCoverageColor(cell.coverage),
                  getCoverageOpacity(cell.coverage),
                  'hover:ring-2 hover:ring-primary/50 hover:shadow-lg',
                )}
                whileHover={{ scale: HOVER_SCALE }}
                whileTap={{ scale: TAP_SCALE }}
              >
                {/* Coverage percentage */}
                <div className='absolute inset-0 flex items-center justify-center'>
                  <span className='text-sm font-bold text-white drop-shadow-md'>
                    {cell.coverage}%
                  </span>
                </div>

                {/* Hover indicator */}
                {hoveredId === cell.id && (
                  <motion.div
                    className='absolute inset-0 flex items-center justify-center bg-white/10 backdrop-blur-sm'
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                  >
                    <ChevronRight className='h-4 w-4 text-white' />
                  </motion.div>
                )}

                {/* Linked indicator */}
                {cell.linked && (
                  <div className='absolute top-1 right-1 h-2 w-2 rounded-full bg-white ring-2 ring-white/30' />
                )}
              </motion.button>

              {/* Tooltip */}
              {hoveredDetails && hoveredDetails.id === cell.id && (
                <motion.div
                  className='bg-popover border-border absolute bottom-full left-1/2 z-50 mb-2 w-72 -translate-x-1/2 rounded-lg border p-3 shadow-lg'
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 5 }}
                >
                  <div className='space-y-3'>
                    <div>
                      <div className='text-sm font-semibold'>{cell.label}</div>
                      <div className='text-muted-foreground text-xs'>Requirement ID: {cell.id}</div>
                    </div>

                    <div className='grid grid-cols-3 gap-2 text-xs'>
                      <div>
                        <div className='text-muted-foreground'>Coverage</div>
                        <div className='text-lg font-bold'>{cell.coverage}%</div>
                      </div>
                      {cell.testCases !== undefined && (
                        <div>
                          <div className='text-muted-foreground'>Tests</div>
                          <div className='text-lg font-bold'>{cell.testCases}</div>
                        </div>
                      )}
                      {cell.adrs !== undefined && (
                        <div>
                          <div className='text-muted-foreground'>ADRs</div>
                          <div className='text-lg font-bold'>{cell.adrs}</div>
                        </div>
                      )}
                    </div>

                    {cell.contracts !== undefined && (
                      <div className='text-muted-foreground text-xs'>
                        {cell.contracts} contract(s) linked
                      </div>
                    )}

                    {cell.coverage < COVERAGE_FAIR && (
                      <div className='rounded border border-amber-500/20 bg-amber-500/10 px-2 py-1 text-xs text-amber-700'>
                        Low coverage - Consider adding tests or documentation
                      </div>
                    )}
                  </div>
                  <div className='bg-popover border-border absolute bottom-0 left-1/2 h-2 w-2 -translate-x-1/2 translate-y-1 rotate-45 border-r border-b' />
                </motion.div>
              )}
            </motion.div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className='flex flex-wrap gap-4 text-xs'>
        <div className='flex items-center gap-2'>
          <div className='h-4 w-4 rounded bg-emerald-600' />
          <span className='text-muted-foreground'>&ge;90% (Excellent)</span>
        </div>
        <div className='flex items-center gap-2'>
          <div className='h-4 w-4 rounded bg-amber-500' />
          <span className='text-muted-foreground'>50-70% (Fair)</span>
        </div>
        <div className='flex items-center gap-2'>
          <div className='h-4 w-4 rounded bg-red-500' />
          <span className='text-muted-foreground'>&lt;30% (Poor)</span>
        </div>
        <div className='flex items-center gap-2'>
          <div className='h-2 w-2 rounded-full bg-white ring-2 ring-white/30' />
          <span className='text-muted-foreground'>Linked item</span>
        </div>
      </div>

      {/* Empty State */}
      {data.length === 0 && (
        <div className='text-muted-foreground py-12 text-center'>
          <p className='text-sm'>No requirements to display</p>
        </div>
      )}
    </motion.div>
  );
};
