/**
 * Quality Dimension Radar Component
 * Displays ISO 29148 quality dimensions as a radar/spider chart
 */

import type { QualityDimension, QualityGrade } from '@/hooks/useItemSpecAnalytics';

import { cn } from '@/lib/utils';

interface QualityDimensionRadarProps {
  dimensions: Record<string, number>;
  overallScore: number;
  grade: QualityGrade;
  size?: number;
  className?: string;
}

const dimensionLabels: Record<QualityDimension, string> = {
  completeness: 'Completeness',
  consistency: 'Consistency',
  feasibility: 'Feasibility',
  necessity: 'Necessity',
  singularity: 'Singularity',
  traceability: 'Traceability',
  unambiguity: 'Unambiguity',
  verifiability: 'Verifiability',
};

const gradeColors: Record<QualityGrade, { bg: string; text: string; ring: string }> = {
  A: { bg: 'bg-green-100', ring: 'ring-green-500', text: 'text-green-800' },
  B: { bg: 'bg-blue-100', ring: 'ring-blue-500', text: 'text-blue-800' },
  C: { bg: 'bg-yellow-100', ring: 'ring-yellow-500', text: 'text-yellow-800' },
  D: { bg: 'bg-orange-100', ring: 'ring-orange-500', text: 'text-orange-800' },
  F: { bg: 'bg-red-100', ring: 'ring-red-500', text: 'text-red-800' },
};

export function QualityDimensionRadar({
  dimensions,
  overallScore,
  grade,
  size = 200,
  className,
}: QualityDimensionRadarProps) {
  const dimKeys = Object.keys(dimensions) as QualityDimension[];
  const numDimensions = dimKeys.length;
  const angleStep = (2 * Math.PI) / numDimensions;
  const center = size / 2;
  const maxRadius = size / 2 - 30;

  // Generate polygon points for the score
  const scorePoints = dimKeys.map((key, i) => {
    const angle = i * angleStep - Math.PI / 2;
    const value = dimensions[key] ?? 0;
    const radius = (value / 100) * maxRadius;
    return {
      x: center + radius * Math.cos(angle),
      y: center + radius * Math.sin(angle),
    };
  });

  const polygonPath = `${scorePoints
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`)
    .join(' ')} Z`;

  // Generate grid circles
  const gridLevels = [0.25, 0.5, 0.75, 1];

  const gradeConfig = gradeColors[grade];

  return (
    <div className={cn('flex flex-col items-center gap-4', className)}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* Grid circles */}
        {gridLevels.map((level) => (
          <circle
            key={level}
            cx={center}
            cy={center}
            r={maxRadius * level}
            fill='none'
            stroke='currentColor'
            strokeOpacity={0.1}
            strokeWidth={1}
          />
        ))}

        {/* Axis lines */}
        {dimKeys.map((_, i) => {
          const angle = i * angleStep - Math.PI / 2;
          const x2 = center + maxRadius * Math.cos(angle);
          const y2 = center + maxRadius * Math.sin(angle);
          return (
            <line
              key={i}
              x1={center}
              y1={center}
              x2={x2}
              y2={y2}
              stroke='currentColor'
              strokeOpacity={0.2}
              strokeWidth={1}
            />
          );
        })}

        {/* Score polygon */}
        <path
          d={polygonPath}
          fill='hsl(var(--primary))'
          fillOpacity={0.2}
          stroke='hsl(var(--primary))'
          strokeWidth={2}
        />

        {/* Score points */}
        {scorePoints.map((point, i) => (
          <circle key={i} cx={point.x} cy={point.y} r={4} fill='hsl(var(--primary))' />
        ))}

        {/* Labels */}
        {dimKeys.map((key, i) => {
          const angle = i * angleStep - Math.PI / 2;
          const labelRadius = maxRadius + 20;
          const x = center + labelRadius * Math.cos(angle);
          const y = center + labelRadius * Math.sin(angle);
          const label = dimensionLabels[key] || key;

          return (
            <text
              key={key}
              x={x}
              y={y}
              textAnchor='middle'
              dominantBaseline='middle'
              className='fill-current text-[10px]'
            >
              {label.slice(0, 4)}
            </text>
          );
        })}
      </svg>

      {/* Overall Score */}
      <div className='flex items-center gap-3'>
        <div
          className={cn(
            'flex items-center justify-center w-12 h-12 rounded-full ring-2',
            gradeConfig.bg,
            gradeConfig.text,
            gradeConfig.ring,
          )}
        >
          <span className='text-xl font-bold'>{grade}</span>
        </div>
        <div className='text-sm'>
          <div className='font-medium'>Overall Score</div>
          <div className='text-muted-foreground'>{Math.round(overallScore)}%</div>
        </div>
      </div>
    </div>
  );
}

interface QualityDimensionBarProps {
  dimensions: Record<string, number>;
  className?: string;
}

export function QualityDimensionBars({ dimensions, className }: QualityDimensionBarProps) {
  const dimKeys = Object.keys(dimensions) as QualityDimension[];

  return (
    <div className={cn('space-y-2', className)}>
      {dimKeys.map((key) => {
        const value = dimensions[key] ?? 0;
        const label = dimensionLabels[key] || key;
        const colorClass =
          value >= 80
            ? 'bg-green-500'
            : value >= 60
              ? 'bg-blue-500'
              : value >= 40
                ? 'bg-yellow-500'
                : value >= 20
                  ? 'bg-orange-500'
                  : 'bg-red-500';

        return (
          <div key={key} className='space-y-1'>
            <div className='flex justify-between text-sm'>
              <span className='font-medium'>{label}</span>
              <span className='text-muted-foreground'>{Math.round(value)}%</span>
            </div>
            <div className='bg-muted h-2 overflow-hidden rounded-full'>
              <div
                className={cn('h-full rounded-full transition-all', colorClass)}
                style={{ width: `${value}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
