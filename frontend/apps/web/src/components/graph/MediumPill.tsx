import type { Node, NodeProps } from '@xyflow/react';

import { memo } from 'react';

export interface MediumPillData extends Record<string, unknown> {
  id?: string;
  label?: string;
  status?: string;
  type?: string;
}

export const MediumPill = memo(function MediumPill({ data }: NodeProps<Node<MediumPillData>>) {
  const typeColors: Record<string, string> = {
    default: '#64748b',
    defect: '#ef4444',
    epic: '#8b5cf6',
    requirement: '#3b82f6',
    story: '#f59e0b',
    task: '#06b6d4',
    test: '#10b981',
  };

  const typeColor = data.type
    ? (typeColors[data.type] ?? typeColors['default'])
    : typeColors['default'];

  const indicatorStyle = {
    backgroundColor: typeColor,
  };

  return (
    <div className='bg-card rounded-lg border px-3 py-2'>
      <div className='flex items-center gap-2'>
        <div className='h-2 w-2 flex-shrink-0 rounded-full' style={indicatorStyle} />
        <span className='max-w-[120px] truncate text-sm font-medium'>
          {data.label ?? 'Untitled'}
        </span>
        {data.status && (
          <span className='bg-muted flex-shrink-0 rounded px-1 text-[10px]'>{data.status}</span>
        )}
      </div>
    </div>
  );
});
