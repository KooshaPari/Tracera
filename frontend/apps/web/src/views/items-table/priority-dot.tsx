import type { Priority } from '@tracertm/types';

import { cn } from '@/lib/utils';

import itemsTableConstants from './constants';

const PRIORITY_COLORS: Record<Priority, string> = {
  critical: 'bg-red-500',
  high: 'bg-orange-500',
  low: 'bg-green-500',
  medium: 'bg-blue-500',
};

interface PriorityDotProps {
  priority?: Priority;
}

function PriorityDot({ priority }: PriorityDotProps): JSX.Element {
  let key: Priority = itemsTableConstants.DEFAULT_PRIORITY;
  if (priority !== undefined) {
    key = priority;
  }
  return <div className={cn('h-1.5 w-1.5 rounded-full', PRIORITY_COLORS[key])} />;
}

export { PriorityDot };
