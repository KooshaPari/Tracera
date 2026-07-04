/**
 * ODC Classification Card Component
 * Displays IBM Orthogonal Defect Classification for defects
 */

import type { ODCDefectType, ODCTrigger } from '@/hooks/useItemSpecAnalytics';

import { cn } from '@/lib/utils';

interface ODCClassificationCardProps {
  defectType: ODCDefectType;
  trigger: ODCTrigger;
  impact: string;
  confidence?: number;
  likelyInjectionPhase?: string | null;
  suggestedPrevention?: string[];
  className?: string;
}

const defectTypeConfig: Record<
  ODCDefectType,
  { label: string; description: string; color: string }
> = {
  algorithm: {
    color: 'bg-pink-100 text-pink-800 border-pink-300',
    description: 'Incorrect or inefficient algorithm implementation',
    label: 'Algorithm',
  },
  assignment: {
    color: 'bg-green-100 text-green-800 border-green-300',
    description: 'Incorrect initialization or setting of data values',
    label: 'Assignment',
  },
  build: {
    color: 'bg-indigo-100 text-indigo-800 border-indigo-300',
    description: 'Build process, library references, or version control issues',
    label: 'Build/Package',
  },
  checking: {
    color: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    description: 'Missing or incorrect validation of data, values, or conditions',
    label: 'Checking',
  },
  documentation: {
    color: 'bg-purple-100 text-purple-800 border-purple-300',
    description: 'Issues in publications, maintenance notes, or documentation',
    label: 'Documentation',
  },
  function: {
    color: 'bg-red-100 text-red-800 border-red-300',
    description:
      'Affects capability, end-user interfaces, product interfaces, or global data structure',
    label: 'Function',
  },
  interface: {
    color: 'bg-orange-100 text-orange-800 border-orange-300',
    description: 'Incorrect interaction with other components, modules, or drivers',
    label: 'Interface',
  },
  timing: {
    color: 'bg-blue-100 text-blue-800 border-blue-300',
    description: 'Race conditions, resource contention, or synchronization issues',
    label: 'Timing/Serialization',
  },
};

const triggerConfig: Record<ODCTrigger, { label: string; description: string }> = {
  complex_path: {
    description: 'Found through complex interactions or sequences',
    label: 'Complex Path',
  },
  coverage: {
    description: 'Found through simple path testing',
    label: 'Coverage',
  },
  design_conformance: {
    description: 'Found by verifying design specifications',
    label: 'Design Conformance',
  },
  exception_handling: {
    description: 'Found through exception/error path testing',
    label: 'Exception Handling',
  },
  rare_situation: {
    description: 'Found in unusual or edge-case conditions',
    label: 'Rare Situation',
  },
  side_effects: {
    description: 'Found through interaction with other modules',
    label: 'Side Effects',
  },
  simple_path: {
    description: 'Found through basic code path execution',
    label: 'Simple Path',
  },
};

export const ODCClassificationCard = ({
  defectType,
  trigger,
  impact,
  confidence,
  likelyInjectionPhase,
  suggestedPrevention,
  className,
}: ODCClassificationCardProps) => {
  const typeConfig = defectTypeConfig[defectType];
  const triggerInfo = triggerConfig[trigger];

  return (
    <div className={cn('rounded-lg border p-4 space-y-4', className)}>
      {/* Header */}
      <div className='flex items-start justify-between'>
        <div>
          <h3 className='text-muted-foreground mb-1 text-sm font-medium'>ODC Classification</h3>
          <div className='flex items-center gap-2'>
            <span className={cn('px-2 py-1 rounded text-sm font-medium border', typeConfig.color)}>
              {typeConfig.label}
            </span>
            {confidence !== undefined && (
              <span className='text-muted-foreground text-sm'>
                {Math.round(confidence * 100)}% confidence
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Classification Grid */}
      <div className='grid grid-cols-1 gap-4 md:grid-cols-3'>
        {/* Defect Type */}
        <div className='bg-muted rounded-lg p-3'>
          <div className='text-muted-foreground mb-1 text-xs'>Defect Type</div>
          <div className='font-medium'>{typeConfig.label}</div>
          <p className='text-muted-foreground mt-1 text-xs'>{typeConfig.description}</p>
        </div>

        {/* Trigger */}
        <div className='bg-muted rounded-lg p-3'>
          <div className='text-muted-foreground mb-1 text-xs'>Trigger</div>
          <div className='font-medium'>{triggerInfo.label}</div>
          <p className='text-muted-foreground mt-1 text-xs'>{triggerInfo.description}</p>
        </div>

        {/* Impact */}
        <div className='bg-muted rounded-lg p-3'>
          <div className='text-muted-foreground mb-1 text-xs'>Impact</div>
          <div className='font-medium capitalize'>{impact}</div>
          {likelyInjectionPhase && (
            <p className='text-muted-foreground mt-1 text-xs'>
              Likely injected during: {likelyInjectionPhase}
            </p>
          )}
        </div>
      </div>

      {/* Prevention Suggestions */}
      {suggestedPrevention && suggestedPrevention.length > 0 && (
        <div className='border-t pt-4'>
          <h4 className='mb-2 text-sm font-medium'>Prevention Suggestions</h4>
          <ul className='space-y-1.5'>
            {suggestedPrevention.map((suggestion, idx) => (
              <li key={idx} className='flex items-start gap-2 text-sm'>
                <span className='mt-0.5 text-green-600'>✓</span>
                <span>{suggestion}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

interface ODCBadgeProps {
  defectType: ODCDefectType;
  size?: 'sm' | 'md';
  className?: string;
}

export const ODCBadge = ({ defectType, size = 'md', className }: ODCBadgeProps) => {
  const config = defectTypeConfig[defectType];
  const sizeClass = size === 'sm' ? 'text-xs px-1.5 py-0.5' : 'text-sm px-2 py-1';

  return (
    <span
      className={cn(
        'inline-flex items-center rounded border font-medium',
        config.color,
        sizeClass,
        className,
      )}
      title={config.description}
    >
      {config.label}
    </span>
  );
};

interface ODCTriggerBadgeProps {
  trigger: ODCTrigger;
  size?: 'sm' | 'md';
  className?: string;
}

export const ODCTriggerBadge = ({ trigger, size = 'md', className }: ODCTriggerBadgeProps) => {
  const config = triggerConfig[trigger];
  const sizeClass = size === 'sm' ? 'text-xs px-1.5 py-0.5' : 'text-sm px-2 py-1';

  return (
    <span
      className={cn(
        'inline-flex items-center rounded border bg-slate-100 text-slate-800 border-slate-300',
        sizeClass,
        className,
      )}
      title={config.description}
    >
      {config.label}
    </span>
  );
};
