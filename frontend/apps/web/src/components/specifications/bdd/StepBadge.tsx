import type { ComponentType, JSX } from 'react';

import { AlertCircle, CheckCircle2, GitBranch, Zap } from 'lucide-react';

import { Badge, cn } from '@tracertm/ui';

export type StepType = 'Given' | 'When' | 'Then' | 'And' | 'But' | 'Background';

interface StepBadgeProps {
  type: StepType;
  className?: string;
  compact?: boolean;
}

const stepConfig: Record<
  StepType,
  {
    color: string;
    bgColor: string;
    icon: ComponentType<{ className?: string }>;
    description: string;
  }
> = {
  And: {
    bgColor: 'bg-gray-500/5',
    color: 'bg-gray-500/10 text-gray-600 border-gray-500/20',
    description: 'Additional',
    icon: GitBranch,
  },
  Background: {
    bgColor: 'bg-purple-500/5',
    color: 'bg-purple-500/10 text-purple-600 border-purple-500/20',
    description: 'Setup',
    icon: GitBranch,
  },
  But: {
    bgColor: 'bg-gray-500/5',
    color: 'bg-gray-500/10 text-gray-600 border-gray-500/20',
    description: 'Alternative',
    icon: GitBranch,
  },
  Given: {
    bgColor: 'bg-blue-500/5',
    color: 'bg-blue-500/10 text-blue-600 border-blue-500/20',
    description: 'Precondition',
    icon: AlertCircle,
  },
  Then: {
    bgColor: 'bg-green-500/5',
    color: 'bg-green-500/10 text-green-600 border-green-500/20',
    description: 'Outcome',
    icon: CheckCircle2,
  },
  When: {
    bgColor: 'bg-amber-500/5',
    color: 'bg-amber-500/10 text-amber-600 border-amber-500/20',
    description: 'Action',
    icon: Zap,
  },
};

export function StepBadge({ type, className, compact = false }: StepBadgeProps): JSX.Element {
  const config = stepConfig[type];
  const Icon = config.icon;

  if (compact) {
    return (
      <Badge
        variant='outline'
        className={cn(config.color, 'flex items-center gap-1 font-medium text-xs', className)}
        title={config.description}
      >
        <Icon className='h-3 w-3' />
        {type}
      </Badge>
    );
  }

  return (
    <div
      className={cn(
        'inline-flex items-center gap-2 px-2.5 py-1 rounded-md border',
        config.color,
        className,
      )}
    >
      <Icon className='h-4 w-4 flex-shrink-0' />
      <span className='text-sm font-medium'>{type}</span>
      <span className='text-xs opacity-75'>({config.description})</span>
    </div>
  );
}
