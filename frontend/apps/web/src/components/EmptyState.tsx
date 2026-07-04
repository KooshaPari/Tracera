import type { LucideIcon } from 'lucide-react';

import { Button } from '@tracertm/ui/components/Button';

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
    variant?: 'default' | 'outline' | 'secondary';
  };
  testId?: string;
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  testId = 'empty-state',
}: EmptyStateProps) {
  return (
    <div
      className='border-muted-foreground/25 animate-in-fade-up flex flex-col items-center justify-center rounded-lg border border-dashed px-8 py-16 text-center transition-all duration-200 ease-out'
      data-testid={testId}
    >
      {Icon && <Icon className='text-muted-foreground/50 mb-4 h-16 w-16' />}
      <h3 className='text-foreground mb-2 text-lg font-semibold'>{title}</h3>
      <p className='text-muted-foreground mb-6 text-sm'>{description}</p>
      {action && (
        <Button onClick={action.onClick} variant={action.variant ?? 'default'}>
          {action.label}
        </Button>
      )}
    </div>
  );
}
