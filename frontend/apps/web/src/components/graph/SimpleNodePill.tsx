// Simple Node Pill - LOD-reduced node (label only, minimal DOM)
// Used when zoom is low or node count is high (B3 perf)

import type { Node, NodeProps } from '@xyflow/react';

import { Handle, Position } from '@xyflow/react';
import { memo } from 'react';

import { ENHANCED_TYPE_COLORS } from './types';

export interface SimpleNodePillData {
  id: string;
  type: string;
  label: string;
  status?: string;
  /** Optional; when provided, clicking selects/focuses */
  onSelect?: ((id: string) => void) | undefined;
  [key: string]: unknown;
}

function SimpleNodePillComponent({
  data,
  selected,
}: NodeProps<Node<SimpleNodePillData, 'simplePill'>>) {
  const bgColor = ENHANCED_TYPE_COLORS[data.type] ?? '#64748b';

  const handleClick = () => {
    data.onSelect?.(data.id);
  };

  return (
    <>
      <Handle
        type='target'
        position={Position.Left}
        className='!-left-1 !h-2 !min-h-2 !w-2 !min-w-2 !border-2'
        style={{ backgroundColor: 'var(--background)', borderColor: bgColor }}
      />
      <div
        role='button'
        tabIndex={0}
        onClick={handleClick}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleClick();
          }
        }}
        className={`max-w-[140px] cursor-pointer truncate rounded-md border px-2 py-1 text-xs font-medium transition-colors ${selected ? 'ring-primary ring-offset-background ring-2 ring-offset-2' : ''} `}
        style={{
          backgroundColor: `${bgColor}20`,
          borderColor: bgColor,
          color: 'var(--foreground)',
        }}
        title={data.label}
      >
        {data.label}
      </div>
      <Handle
        type='source'
        position={Position.Right}
        className='!-right-1 !h-2 !min-h-2 !w-2 !min-w-2 !border-2'
        style={{ backgroundColor: 'var(--background)', borderColor: bgColor }}
      />
    </>
  );
}

export const SimpleNodePill = memo(SimpleNodePillComponent);
