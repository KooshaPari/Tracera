/**
 * ComplianceGaugeFull - Full compliance score visualization
 * Circular gauge with color gradient and animated fill
 */

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

import { cn } from '@/lib/utils';

interface ComplianceGaugeFullProps {
  score: number; // 0-100
  size?: number;
  strokeWidth?: number;
  showAnimation?: boolean;
  label?: string;
  showSubtext?: boolean;
  className?: string;
}

function getGaugeColor(value: number): string {
  if (value >= 90) {
    return '#10b981';
  } // Emerald
  if (value >= 80) {
    return '#06b6d4';
  } // Cyan
  if (value >= 70) {
    return '#3b82f6';
  } // Blue
  if (value >= 60) {
    return '#f59e0b';
  } // Amber
  if (value >= 40) {
    return '#f97316';
  } // Orange
  return '#ef4444'; // Red
}

function getStatus(value: number): string {
  if (value >= 90) {
    return 'Excellent';
  }
  if (value >= 80) {
    return 'Very Good';
  }
  if (value >= 70) {
    return 'Good';
  }
  if (value >= 60) {
    return 'Fair';
  }
  if (value >= 40) {
    return 'Poor';
  }
  return 'Critical';
}

export function ComplianceGaugeFull({
  score,
  size = 200,
  strokeWidth = 12,
  showAnimation = true,
  label = 'Compliance',
  showSubtext = true,
  className,
}: ComplianceGaugeFullProps) {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    if (!showAnimation) {
      setAnimatedScore(score);
      return;
    }

    let current = 0;
    const target = score;
    const increment = target / 30;

    const interval = setInterval(() => {
      current += increment;
      if (current >= target) {
        setAnimatedScore(target);
        clearInterval(interval);
      } else {
        setAnimatedScore(Math.round(current));
      }
    }, 16);

    return () => {
      clearInterval(interval);
    };
  }, [score, showAnimation]);

  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (animatedScore / 100) * circumference;

  const gaugeColor = getGaugeColor(animatedScore);

  return (
    <motion.div
      className={cn('flex flex-col items-center justify-center gap-4', className)}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* SVG Gauge */}
      <div style={{ height: size, width: size }}>
        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
          className='-rotate-90 transform'
        >
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill='none'
            stroke='hsl(var(--muted))'
            strokeWidth={strokeWidth}
          />

          {/* Progress circle with animation */}
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill='none'
            stroke={gaugeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{
              duration: 1,
              ease: 'easeInOut',
            }}
            strokeLinecap='round'
          />
        </svg>

        {/* Center content */}
        <div className='absolute inset-0 flex flex-col items-center justify-center'>
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
            className='text-center'
          >
            <div className='text-4xl font-bold' style={{ color: gaugeColor }}>
              {animatedScore}%
            </div>
            <div className='text-muted-foreground mt-1 text-xs font-medium tracking-widest uppercase'>
              {label}
            </div>
          </motion.div>
        </div>
      </div>

      {/* Status and text */}
      <motion.div
        className='text-center'
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <div className='text-sm font-medium' style={{ color: gaugeColor }}>
          {getStatus(animatedScore)}
        </div>
        {showSubtext && (
          <div className='text-muted-foreground mt-1 text-xs'>
            {animatedScore >= 90 && 'Exceptional compliance levels achieved'}
            {animatedScore >= 80 && animatedScore < 90 && 'Strong compliance position'}
            {animatedScore >= 70 && animatedScore < 80 && 'Good compliance status'}
            {animatedScore >= 60 && animatedScore < 70 && 'Room for improvement'}
            {animatedScore >= 40 && animatedScore < 60 && 'Significant gaps identified'}
            {animatedScore < 40 && 'Critical attention required'}
          </div>
        )}
      </motion.div>

      {/* Details grid */}
      <div className='grid w-full grid-cols-3 gap-2 text-center text-xs'>
        <div className='bg-muted/30 rounded p-2'>
          <div className='text-muted-foreground text-[10px]'>SCORE</div>
          <div className='font-bold'>{animatedScore}%</div>
        </div>
        <div className='bg-muted/30 rounded p-2'>
          <div className='text-muted-foreground text-[10px]'>REMAINING</div>
          <div className='font-bold'>{100 - animatedScore}%</div>
        </div>
        <div className='bg-muted/30 rounded p-2'>
          <div className='text-muted-foreground text-[10px]'>STATUS</div>
          <div className='font-bold capitalize'>{getStatus(animatedScore).split(' ')[0]}</div>
        </div>
      </div>
    </motion.div>
  );
}
