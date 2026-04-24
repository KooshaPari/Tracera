import type { Node, NodeProps } from '@xyflow/react';

import { memo, useMemo } from 'react';

import { ENHANCED_TYPE_COLORS } from './types';

export interface SimplePillData extends Record<string, unknown> {
  id?: string;
  type?: string;
  label?: string;
  status?: string;
}

export const SimplePill = memo(function SimplePill({ data }: NodeProps<Node<SimplePillData>>) {
  const typeColor = data.type ? (ENHANCED_TYPE_COLORS[data.type] ?? '#64748b') : '#64748b';
  const style = useMemo(
    () => ({
      backgroundColor: typeColor + '20',
      borderColor: typeColor,
      color: typeColor,
    }),
    [typeColor],
  );

  return (
    <div className='rounded-md border px-2 py-1 text-xs font-medium' style={style}>
      {data.label ?? 'Untitled'}
    </div>
  );
});
