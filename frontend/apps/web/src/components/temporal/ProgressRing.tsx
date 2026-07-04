import type React from 'react';

const PERCENTAGE_EXCELLENT = 75;
const PERCENTAGE_GOOD = 50;
const PERCENTAGE_FAIR = 25;

export interface ProgressRingProps {
  percentage: number;
  radius?: number | undefined;
  strokeWidth?: number | undefined;
  size?: 'sm' | 'md' | 'lg' | undefined;
  animated?: boolean | undefined;
  showLabel?: boolean | undefined;
  color?: string | undefined;
}

export const ProgressRing: React.FC<ProgressRingProps> = ({
  percentage,
  size = 'md',
  animated = true,
  showLabel = true,
  color,
}) => {
  // Adjust radius and stroke based on size
  const sizeMap = {
    lg: { fontSize: '24px', radius: 60, strokeWidth: 5 },
    md: { fontSize: '16px', radius: 45, strokeWidth: 4 },
    sm: { fontSize: '12px', radius: 30, strokeWidth: 3 },
  };

  const config = sizeMap[size];
  const normalizedRadius = config.radius;
  const circumference = normalizedRadius * 2 * Math.PI;
  const offset = circumference - (percentage / 100) * circumference;

  // Determine color based on percentage
  let ringColor = color;
  if (!ringColor) {
    if (percentage >= PERCENTAGE_EXCELLENT) {
      ringColor = '#22c55e'; // Green
    } else if (percentage >= PERCENTAGE_GOOD) {
      ringColor = '#3b82f6'; // Blue
    } else if (percentage >= PERCENTAGE_FAIR) {
      ringColor = '#eab308'; // Yellow
    } else {
      ringColor = '#ef4444'; // Red
    }
  }

  return (
    <div className='flex items-center justify-center'>
      <div className='relative inline-flex items-center justify-center'>
        <svg
          height={normalizedRadius * 2 + 10}
          width={normalizedRadius * 2 + 10}
          className='-rotate-90 transform'
        >
          {/* Background circle */}
          <circle
            stroke='#e5e7eb'
            fill='none'
            strokeWidth={config.strokeWidth}
            r={normalizedRadius}
            cx={normalizedRadius + 5}
            cy={normalizedRadius + 5}
            className='dark:stroke-gray-700'
          />
          {/* Progress circle */}
          <circle
            stroke={ringColor}
            fill='none'
            strokeWidth={config.strokeWidth}
            strokeDasharray={`${circumference} ${circumference}`}
            strokeDashoffset={offset}
            strokeLinecap='round'
            r={normalizedRadius}
            cx={normalizedRadius + 5}
            cy={normalizedRadius + 5}
            style={{
              filter: 'drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1))',
              transition: animated ? 'stroke-dashoffset 0.5s ease' : 'none',
            }}
          />
        </svg>

        {/* Center label */}
        {showLabel && (
          <div className='absolute flex flex-col items-center justify-center'>
            <span
              style={{ fontSize: config.fontSize, fontWeight: '600' }}
              className='text-gray-900 dark:text-gray-100'
            >
              {Math.round(percentage)}%
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export interface ProgressBarProps {
  percentage: number;
  height?: 'sm' | 'md' | 'lg' | undefined;
  showLabel?: boolean | undefined;
  color?: string | undefined;
  animated?: boolean | undefined;
  className?: string | undefined;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  percentage,
  height = 'md',
  showLabel = true,
  color,
  animated = true,
  className = '',
}) => {
  const heightMap = {
    lg: 'h-3',
    md: 'h-2',
    sm: 'h-1',
  };

  // Determine color based on percentage
  let barColor = color;
  if (!barColor) {
    if (percentage >= PERCENTAGE_EXCELLENT) {
      barColor = 'bg-green-500';
    } else if (percentage >= PERCENTAGE_GOOD) {
      barColor = 'bg-blue-500';
    } else if (percentage >= PERCENTAGE_FAIR) {
      barColor = 'bg-yellow-500';
    } else {
      barColor = 'bg-red-500';
    }
  }

  return (
    <div className={className}>
      <div
        className={`w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700 ${heightMap[height]}`}
      >
        <div
          className={`${barColor} ${heightMap[height]} rounded-full ${animated ? 'transition-all duration-500' : ''}`}
          style={{ width: `${Math.min(Math.max(percentage, 0), 100)}%` }}
        />
      </div>
      {showLabel && (
        <p className='mt-1 text-xs text-gray-600 dark:text-gray-400'>{Math.round(percentage)}%</p>
      )}
    </div>
  );
};

export interface LinearProgressProps {
  value: number;
  max: number;
  label?: string | undefined;
  color?: string | undefined;
  showLabel?: boolean | undefined;
}

export const LinearProgress: React.FC<LinearProgressProps> = ({
  value,
  max,
  label,
  color,
  showLabel = true,
}) => {
  const percentage = (value / max) * 100;

  return (
    <div className='space-y-2'>
      {(label ?? showLabel) && (
        <div className='flex items-center justify-between text-sm'>
          {label && <span className='font-medium text-gray-700 dark:text-gray-300'>{label}</span>}
          {showLabel && (
            <span className='text-gray-600 dark:text-gray-400'>
              {value}/{max}
            </span>
          )}
        </div>
      )}
      <ProgressBar percentage={percentage} height='md' showLabel={false} color={color} />
    </div>
  );
};

export default ProgressRing;
