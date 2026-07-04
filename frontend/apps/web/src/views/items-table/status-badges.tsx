import type { LucideIcon } from 'lucide-react';

import { AlertCircle, CheckCircle2, Clock, Terminal, X } from 'lucide-react';

import type { ItemStatus } from '@tracertm/types';

import { cn } from '@/lib/utils';
import { Badge } from '@tracertm/ui';

const STATUS_CONFIG: Record<ItemStatus, { color: string; icon: LucideIcon }> = {
  blocked: {
    color: 'bg-red-500/10 text-red-600 border-red-500/20',
    icon: AlertCircle,
  },
  cancelled: {
    color: 'bg-orange-500/10 text-orange-600 border-orange-500/20',
    icon: X,
  },
  done: {
    color: 'bg-green-500/10 text-green-600 border-green-500/20',
    icon: CheckCircle2,
  },
  in_progress: {
    color: 'bg-blue-500/10 text-blue-600 border-blue-500/20',
    icon: Clock,
  },
  todo: { color: 'bg-muted text-muted-foreground', icon: Terminal },
};

interface StatusBadgeProps {
  status: ItemStatus;
}

function StatusBadge({ status }: StatusBadgeProps): JSX.Element {
  const fallback = STATUS_CONFIG.todo;
  const config = STATUS_CONFIG[status];
  let resolved = fallback;
  if (config !== undefined) {
    resolved = config;
  }
  const Icon = resolved.icon;
  return (
    <Badge
      className={cn(
        'text-[9px] font-black uppercase tracking-tighter gap-1 border',
        resolved.color,
      )}
      data-testid='status-badge'
    >
      <Icon className='h-2.5 w-2.5' />
      {status.replace('_', ' ')}
    </Badge>
  );
}

export { StatusBadge };
