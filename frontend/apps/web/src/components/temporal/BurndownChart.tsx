import type React from 'react';

import { useMemo } from 'react';
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import type { BurndownDataPoint, Sprint } from '@tracertm/types';

export interface BurndownChartProps {
  sprint: Sprint;
  data?: BurndownDataPoint[];
  height?: number;
}

function BurndownCustomTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: {
    payload: {
      date: string;
      ideal: number;
      actual: number;
      completed?: number;
    };
  }[];
}) {
  if (active && payload && payload.length > 0) {
    const first = payload[0];
    const data = first?.payload;
    if (!data) {
      return null;
    }
    return (
      <div className='rounded border border-gray-200 bg-white p-3 shadow-lg dark:border-gray-700 dark:bg-gray-800'>
        <p className='text-sm font-medium text-gray-900 dark:text-gray-100'>{data.date}</p>
        <p className='text-sm text-blue-600 dark:text-blue-400'>Ideal: {data.ideal} points</p>
        <p className='text-sm text-red-600 dark:text-red-400'>Actual: {data.actual} points</p>
        {data.completed !== undefined && (
          <p className='text-sm text-green-600 dark:text-green-400'>
            Completed: {data.completed} points
          </p>
        )}
      </div>
    );
  }
  return null;
}

export const BurndownChart: React.FC<BurndownChartProps> = ({
  sprint,
  data = [],
  height = 300,
}) => {
  const chartData = useMemo(() => {
    if (data.length === 0) {
      // Generate mock data for demo
      const days = Math.ceil(
        (new Date(sprint.endDate).getTime() - new Date(sprint.startDate).getTime()) /
          (1000 * 60 * 60 * 24),
      );
      const mockData: {
        day: number;
        date: string;
        ideal: number;
        actual: number;
      }[] = [];

      for (let i = 0; i <= days; i += 1) {
        const idealRemaining = Math.max(sprint.plannedPoints * ((days - i) / days), 0);
        const actualRemaining = Math.max(
          sprint.plannedPoints - sprint.completedPoints * (i / days),
          0,
        );

        mockData.push({
          actual: Math.round(actualRemaining),
          date: new Date(sprint.startDate).toLocaleDateString('en-US', {
            day: 'numeric',
            month: 'short',
          }),
          day: i,
          ideal: Math.round(idealRemaining),
        });
      }

      return mockData;
    }

    return data.map((point, index) => ({
      actual: point.remainingPoints,
      completed: point.completedPoints,
      date: new Date(point.date).toLocaleDateString('en-US', {
        day: 'numeric',
        month: 'short',
      }),
      day: index,
      ideal: point.idealPoints,
    }));
  }, [sprint, data]);

  return (
    <div className='w-full'>
      <ResponsiveContainer width='100%' height={height}>
        <LineChart data={chartData} margin={{ bottom: 5, left: 0, right: 30, top: 5 }}>
          <defs>
            <linearGradient id='colorIdeal' x1='0' y1='0' x2='0' y2='1'>
              <stop offset='5%' stopColor='#3b82f6' stopOpacity={0.3} />
              <stop offset='95%' stopColor='#3b82f6' stopOpacity={0} />
            </linearGradient>
            <linearGradient id='colorActual' x1='0' y1='0' x2='0' y2='1'>
              <stop offset='5%' stopColor='#ef4444' stopOpacity={0.3} />
              <stop offset='95%' stopColor='#ef4444' stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray='3 3' stroke='#e5e7eb' />
          <XAxis dataKey='date' stroke='#6b7280' style={{ fontSize: '12px' }} />
          <YAxis
            stroke='#6b7280'
            style={{ fontSize: '12px' }}
            label={{
              angle: -90,
              position: 'insideLeft',
              value: 'Points Remaining',
            }}
          />
          <Tooltip content={<BurndownCustomTooltip />} />
          <Legend wrapperStyle={{ paddingTop: '20px' }} iconType='line' />
          <Line
            type='monotone'
            dataKey='ideal'
            stroke='#3b82f6'
            strokeWidth={2}
            dot={false}
            name='Ideal Burndown'
            isAnimationActive={false}
          />
          <Line
            type='monotone'
            dataKey='actual'
            stroke='#ef4444'
            strokeWidth={2}
            dot={false}
            name='Actual Progress'
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Status Summary */}
      <div className='mt-4 grid grid-cols-3 gap-4 text-sm'>
        <div className='rounded-lg border border-blue-200 bg-blue-50 p-3 dark:border-blue-800 dark:bg-blue-900/20'>
          <p className='font-medium text-blue-600 dark:text-blue-400'>Ideal Rate</p>
          <p className='text-lg font-bold text-blue-900 dark:text-blue-100'>
            {sprint.plannedPoints > 0
              ? Math.round(
                  (sprint.plannedPoints /
                    Math.max(
                      Math.ceil(
                        (new Date(sprint.endDate).getTime() -
                          new Date(sprint.startDate).getTime()) /
                          (1000 * 60 * 60 * 24),
                      ),
                      1,
                    )) *
                    10,
                ) / 10
              : 0}
            points/day
          </p>
        </div>
        <div className='rounded-lg border border-red-200 bg-red-50 p-3 dark:border-red-800 dark:bg-red-900/20'>
          <p className='font-medium text-red-600 dark:text-red-400'>Current Rate</p>
          <p className='text-lg font-bold text-red-900 dark:text-red-100'>
            {sprint.completedPoints > 0
              ? Math.round(
                  (sprint.completedPoints /
                    Math.max(
                      Math.ceil(
                        (Date.now() - new Date(sprint.startDate).getTime()) / (1000 * 60 * 60 * 24),
                      ),
                      1,
                    )) *
                    10,
                ) / 10
              : 0}
            points/day
          </p>
        </div>
        <div className='rounded-lg border border-green-200 bg-green-50 p-3 dark:border-green-800 dark:bg-green-900/20'>
          <p className='font-medium text-green-600 dark:text-green-400'>Remaining</p>
          <p className='text-lg font-bold text-green-900 dark:text-green-100'>
            {sprint.remainingPoints} points
          </p>
        </div>
      </div>
    </div>
  );
};

export default BurndownChart;
