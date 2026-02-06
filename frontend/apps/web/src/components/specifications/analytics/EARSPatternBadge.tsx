/**
 * EARS Pattern Badge Component
 * Displays the EARS (Easy Approach to Requirements Syntax) classification
 * for a requirement specification.
 */

import type { EARSPatternType } from '@/hooks/useItemSpecAnalytics';

import { cn } from '@/lib/utils';

interface EARSPatternBadgeProps {
  patternType: EARSPatternType;
  confidence?: number;
  isWellFormed?: boolean;
  showConfidence?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const patternConfig: Record<
  EARSPatternType,
  { label: string; description: string; color: string; icon: string }
> = {
  complex: {
    color: 'bg-orange-100 text-orange-800 border-orange-300',
    description: 'Multiple conditions combined',
    icon: '⊕',
    label: 'Complex',
  },
  event_driven: {
    color: 'bg-purple-100 text-purple-800 border-purple-300',
    description: 'When <trigger>, the system shall...',
    icon: '⚡',
    label: 'Event-Driven',
  },
  optional: {
    color: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    description: 'Where <feature>, the system shall...',
    icon: '?',
    label: 'Optional',
  },
  state_driven: {
    color: 'bg-green-100 text-green-800 border-green-300',
    description: 'While <state>, the system shall...',
    icon: '◉',
    label: 'State-Driven',
  },
  ubiquitous: {
    color: 'bg-blue-100 text-blue-800 border-blue-300',
    description: 'The system shall always...',
    icon: '∀',
    label: 'Ubiquitous',
  },
  unwanted: {
    color: 'bg-red-100 text-red-800 border-red-300',
    description: 'If <condition>, the system shall not...',
    icon: '⊘',
    label: 'Unwanted',
  },
};

const sizeClasses = {
  lg: 'text-base px-3 py-1.5',
  md: 'text-sm px-2.5 py-1',
  sm: 'text-xs px-2 py-0.5',
};

export function EARSPatternBadge({
  patternType,
  confidence,
  isWellFormed,
  showConfidence = false,
  size = 'md',
  className,
}: EARSPatternBadgeProps) {
  const config = patternConfig[patternType];

  return (
    <div
      className={cn(
        'inline-flex items-center gap-1.5 rounded-md border font-medium',
        config.color,
        sizeClasses[size],
        className,
      )}
      title={config.description}
    >
      <span className='font-mono'>{config.icon}</span>
      <span>{config.label}</span>
      {showConfidence && confidence !== undefined && (
        <span className='opacity-70'>({Math.round(confidence * 100)}%)</span>
      )}
      {isWellFormed === false && (
        <span
          className='text-red-600'
          title='Requirement is not well-formed according to EARS syntax'
        >
          ⚠
        </span>
      )}
    </div>
  );
}

interface EARSPatternDetailProps {
  patternType: EARSPatternType;
  trigger?: string | null;
  precondition?: string | null;
  postcondition?: string | null;
  systemName?: string | null;
  formalStructure?: string | null;
  suggestions?: string[];
  className?: string;
}

export function EARSPatternDetail({
  patternType,
  trigger,
  precondition,
  postcondition,
  systemName,
  formalStructure,
  suggestions,
  className,
}: EARSPatternDetailProps) {
  const config = patternConfig[patternType];

  return (
    <div className={cn('space-y-3 rounded-lg border p-4', className)}>
      <div className='flex items-center justify-between'>
        <EARSPatternBadge patternType={patternType} size='lg' />
        <span className='text-muted-foreground text-sm'>{config.description}</span>
      </div>

      <div className='grid gap-2 text-sm'>
        {systemName && (
          <div className='flex gap-2'>
            <span className='text-muted-foreground w-24 font-medium'>System:</span>
            <span>{systemName}</span>
          </div>
        )}
        {trigger && (
          <div className='flex gap-2'>
            <span className='text-muted-foreground w-24 font-medium'>Trigger:</span>
            <span className='bg-muted rounded px-2 py-1 font-mono text-xs'>{trigger}</span>
          </div>
        )}
        {precondition && (
          <div className='flex gap-2'>
            <span className='text-muted-foreground w-24 font-medium'>Precondition:</span>
            <span className='bg-muted rounded px-2 py-1 font-mono text-xs'>{precondition}</span>
          </div>
        )}
        {postcondition && (
          <div className='flex gap-2'>
            <span className='text-muted-foreground w-24 font-medium'>Postcondition:</span>
            <span className='bg-muted rounded px-2 py-1 font-mono text-xs'>{postcondition}</span>
          </div>
        )}
        {formalStructure && (
          <div className='flex gap-2'>
            <span className='text-muted-foreground w-24 font-medium'>Formal:</span>
            <code className='rounded bg-slate-100 px-2 py-1 text-xs dark:bg-slate-800'>
              {formalStructure}
            </code>
          </div>
        )}
      </div>

      {suggestions && suggestions.length > 0 && (
        <div className='mt-3 border-t pt-3'>
          <p className='mb-2 text-sm font-medium'>Suggestions:</p>
          <ul className='text-muted-foreground list-inside list-disc space-y-1 text-sm'>
            {suggestions.map((suggestion, idx) => (
              <li key={idx}>{suggestion}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
