import { Cell, Pie, PieChart, ResponsiveContainer } from 'recharts';

import { cn } from '@/lib/utils';

interface ComplianceGaugeProps {
  score: number; // 0-100
  size?: number;
  showLabel?: boolean;
  className?: string;
}

function getColor(value: number) {
  if (value >= 90) {
    return '#10b981';
  } // Green-500
  if (value >= 70) {
    return '#f59e0b';
  } // Amber-500
  return '#ef4444'; // Red-500
}

export function ComplianceGauge({
  score,
  size = 100,
  showLabel = true,
  className,
}: ComplianceGaugeProps) {
  const data = [
    { name: 'Score', value: score },
    { name: 'Remaining', value: 100 - score },
  ];

  const color = getColor(score);

  return (
    <div
      className={cn('relative flex flex-col items-center', className)}
      style={{ height: size, width: size }}
    >
      <ResponsiveContainer width='100%' height='100%'>
        <PieChart>
          <Pie
            data={data}
            cx='50%'
            cy='50%'
            innerRadius={size / 2 - 8}
            outerRadius={size / 2}
            startAngle={180}
            endAngle={0}
            paddingAngle={0}
            dataKey='value'
            stroke='none'
          >
            <Cell fill={color} />
            <Cell fill='hsl(var(--muted))' />
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      {showLabel && (
        <div className='absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1 text-center'>
          <span className='text-2xl font-bold' style={{ color }}>
            {Math.round(score)}%
          </span>
          <span className='text-muted-foreground -mt-1 block text-[10px] tracking-wider uppercase'>
            Compliance
          </span>
        </div>
      )}
    </div>
  );
}
