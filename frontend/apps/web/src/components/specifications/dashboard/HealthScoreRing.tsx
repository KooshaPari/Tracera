/**
 * HealthScoreRing - Animated ring chart showing overall health score
 * Displays breakdown by category with color-coded segments
 */

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { Cell, Pie, PieChart, ResponsiveContainer } from 'recharts';

import { cn } from '@/lib/utils';

// Constants for animation and styling
const _ANIMATION_DURATION_MS = 500;
const FRAME_INTERVAL_MS = 16; // ~60fps
const ANIMATION_STEPS = 30;
const SCORE_EXCELLENT = 90;
const SCORE_GOOD = 70;
const SCORE_FAIR = 50;

const COLOR_EXCELLENT = '#10b981';
const COLOR_GOOD = '#3b82f6';
const COLOR_FAIR = '#f59e0b';
const COLOR_POOR = '#ef4444';

interface HealthScoreRingProps {
  score: number; // 0-100
  categories?: {
    name: string;
    value: number;
    color: string;
  }[];
  showAnimation?: boolean;
  showLegend?: boolean;
  size?: number;
  className?: string;
}

const DEFAULT_CATEGORIES = [
  { color: COLOR_EXCELLENT, name: 'Excellent', value: 0 },
  { color: COLOR_GOOD, name: 'Good', value: 0 },
  { color: COLOR_FAIR, name: 'Fair', value: 0 },
  { color: COLOR_POOR, name: 'Poor', value: 0 },
];

const getScoreColor = (value: number) => {
  if (value >= SCORE_EXCELLENT) {
    return COLOR_EXCELLENT;
  }
  if (value >= SCORE_GOOD) {
    return COLOR_GOOD;
  }
  if (value >= SCORE_FAIR) {
    return COLOR_FAIR;
  }
  return COLOR_POOR;
};

export const HealthScoreRing = ({
  score,
  categories,
  showAnimation = true,
  showLegend = true,
  size = 300,
  className,
}: HealthScoreRingProps) => {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    if (!showAnimation) {
      setAnimatedScore(score);
      return;
    }

    let current = 0;
    const target = score;
    const increment = target / ANIMATION_STEPS;

    const interval = setInterval(() => {
      current += increment;
      if (current >= target) {
        setAnimatedScore(target);
        clearInterval(interval);
      } else {
        setAnimatedScore(Math.round(current));
      }
    }, FRAME_INTERVAL_MS);

    return () => {
      clearInterval(interval);
    };
  }, [score, showAnimation]);

  // Use provided categories or generate from score
  const data = categories ?? DEFAULT_CATEGORIES;

  const scoreColor = getScoreColor(animatedScore);

  return (
    <motion.div
      className={cn('flex flex-col items-center gap-6', className)}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Ring Chart */}
      <div style={{ height: size, width: size }}>
        <ResponsiveContainer width='100%' height='100%'>
          <PieChart>
            <Pie
              data={[
                { name: 'Score', value: animatedScore },
                { name: 'Remaining', value: 100 - animatedScore },
              ]}
              cx='50%'
              cy='50%'
              innerRadius={size / 2 - 40}
              outerRadius={size / 2}
              startAngle={180}
              endAngle={0}
              dataKey='value'
              stroke='none'
            >
              <Cell fill={scoreColor} />
              <Cell fill='hsl(var(--muted))' />
            </Pie>
          </PieChart>
        </ResponsiveContainer>

        {/* Center Text */}
        <div className='absolute inset-0 flex flex-col items-center justify-center'>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className='text-center'
          >
            <motion.div className='text-5xl font-bold' style={{ color: scoreColor }}>
              {animatedScore}%
            </motion.div>
            <div className='text-muted-foreground mt-1 text-xs font-medium tracking-widest uppercase'>
              Health Score
            </div>
          </motion.div>
        </div>
      </div>

      {/* Legend */}
      {showLegend && data.length > 0 && (
        <motion.div
          className='grid w-full grid-cols-2 gap-3'
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          {data.map((item) => (
            <div key={item.name} className='flex items-center gap-2'>
              <div
                className='h-3 w-3 shrink-0 rounded-full'
                style={{ backgroundColor: item.color }}
              />
              <span className='text-muted-foreground text-xs'>{item.name}</span>
            </div>
          ))}
        </motion.div>
      )}

      {/* Status Message */}
      <motion.div
        className='text-center text-sm'
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        {animatedScore >= SCORE_EXCELLENT && (
          <p className='font-medium text-green-600'>Excellent specification health!</p>
        )}
        {animatedScore >= SCORE_GOOD && animatedScore < SCORE_EXCELLENT && (
          <p className='font-medium text-blue-600'>Good specification coverage.</p>
        )}
        {animatedScore >= SCORE_FAIR && animatedScore < SCORE_GOOD && (
          <p className='font-medium text-amber-600'>Consider improving specifications.</p>
        )}
        {animatedScore < SCORE_FAIR && (
          <p className='font-medium text-red-600'>Significant specification gaps detected.</p>
        )}
      </motion.div>
    </motion.div>
  );
};
