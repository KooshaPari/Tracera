// Edit Affordances Component
// Shows edit capability indicators with visual feedback
// Supports instant, agent-assisted, and manual edit types

import { Bot, Check, Edit3, Zap } from 'lucide-react';
import { memo, useCallback, useState } from 'react';

import { cn } from '@tracertm/ui';
import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@tracertm/ui/components/Tooltip';

export type EditType = 'instant' | 'agent_required' | 'manual';

interface EditAffordanceData {
  editType: EditType;
  label: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  isPending?: boolean;
}

const EDIT_TYPE_CONFIG: Record<EditType, EditAffordanceData> = {
  agent_required: {
    color: '#8b5cf6',
    description: 'An AI agent will help implement changes',
    editType: 'agent_required',
    icon: <Bot className='h-4 w-4' />,
    label: 'Agent-Assisted Edit', // Violet
  },
  instant: {
    color: '#3b82f6',
    description: 'Changes apply immediately via automation',
    editType: 'instant',
    icon: <Zap className='h-4 w-4' />,
    label: 'Instant Edit', // Blue
  },
  manual: {
    color: '#f59e0b',
    description: 'Edit manually in the full editor',
    editType: 'manual',
    icon: <Edit3 className='h-4 w-4' />,
    label: 'Manual Edit', // Amber
  },
};

interface EditAffordancesProps {
  editType: EditType;
  isEditing?: boolean;
  onEdit?: () => void;
  compact?: boolean;
  showLabel?: boolean;
  className?: string;
}

/**
 * Edit affordance badge component
 */
function EditAffordancesComponent({
  editType,
  isEditing = false,
  onEdit,
  compact = false,
  showLabel = true,
  className,
}: EditAffordancesProps) {
  const [hasInteracted, setHasInteracted] = useState(false);
  const config = EDIT_TYPE_CONFIG[editType];

  const handleClick = useCallback(() => {
    setHasInteracted(true);
    onEdit?.();
  }, [onEdit]);

  if (compact) {
    return (
      <TooltipProvider>
        <Tooltip delayDuration={200}>
          <TooltipTrigger asChild>
            <Button
              variant='ghost'
              size='sm'
              className={cn('h-7 w-7 p-0', className)}
              style={{ color: config.color }}
              onClick={handleClick}
              disabled={isEditing}
            >
              {isEditing ? (
                <div className='h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent' />
              ) : (
                config.icon
              )}
            </Button>
          </TooltipTrigger>
          <TooltipContent side='right'>
            <div className='space-y-1'>
              <p className='text-sm font-semibold'>{config.label}</p>
              <p className='text-muted-foreground text-xs'>{config.description}</p>
            </div>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return (
    <TooltipProvider>
      <Tooltip delayDuration={200}>
        <TooltipTrigger asChild>
          <div
            className={cn(
              'inline-flex items-center gap-2 px-3 py-2 rounded-lg border transition-all',
              hasInteracted && !isEditing && 'bg-green-50 border-green-200',
              isEditing && 'bg-blue-50 border-blue-200',
              !hasInteracted &&
                !isEditing &&
                'bg-muted/30 border-muted-foreground/20 hover:border-muted-foreground/40',
              className,
            )}
            onClick={handleClick}
            style={
              !hasInteracted && !isEditing
                ? {}
                : {
                    backgroundColor: `${config.color}10`,
                    borderColor: `${config.color}30`,
                  }
            }
          >
            {/* Icon */}
            <div style={{ color: config.color }}>
              {isEditing ? (
                <div className='h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent' />
              ) : (
                config.icon
              )}
            </div>

            {/* Label and description */}
            {showLabel && (
              <div className='text-sm'>
                <div className='font-semibold'>{config.label}</div>
                <div className='text-muted-foreground text-xs'>{config.description}</div>
              </div>
            )}

            {/* Success indicator */}
            {hasInteracted && !isEditing && <Check className='ml-auto h-4 w-4 text-green-500' />}
          </div>
        </TooltipTrigger>
        <TooltipContent>
          <div className='space-y-2'>
            <p className='font-semibold'>{config.label}</p>
            <p className='text-sm'>{config.description}</p>
            {editType === 'instant' && (
              <div className='text-muted-foreground border-t pt-2 text-xs'>
                Changes are applied automatically through system automation.
              </div>
            )}
            {editType === 'agent_required' && (
              <div className='text-muted-foreground border-t pt-2 text-xs'>
                An AI agent will analyze the request and implement changes.
              </div>
            )}
            {editType === 'manual' && (
              <div className='text-muted-foreground border-t pt-2 text-xs'>
                You will be taken to the full editor to make changes manually.
              </div>
            )}
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

/**
 * Edit affordance badge (simple badge display)
 */
export function EditAffordanceBadge({
  editType,
  className,
}: {
  editType: EditType;
  className?: string;
}) {
  const config = EDIT_TYPE_CONFIG[editType];

  return (
    <Badge className={cn('text-white gap-1', className)} style={{ backgroundColor: config.color }}>
      <span className='text-sm'>{config.icon}</span>
      {config.label}
    </Badge>
  );
}

/**
 * Inline edit affordance indicator
 */
export function InlineEditAffordance({
  editType,
  className,
}: {
  editType: EditType;
  className?: string;
}) {
  const config = EDIT_TYPE_CONFIG[editType];

  return (
    <div
      className={cn('flex items-center gap-1 p-1.5 rounded-md', className)}
      style={{
        backgroundColor: `${config.color}15`,
        borderLeft: `3px solid ${config.color}`,
      }}
    >
      <div style={{ color: config.color }}>{config.icon}</div>
      <span className='text-xs font-medium'>{config.label}</span>
    </div>
  );
}

/**
 * Edit affordance info panel
 */
export function EditAffordancePanel({
  editType,
  className,
}: {
  editType: EditType;
  className?: string;
}) {
  const config = EDIT_TYPE_CONFIG[editType];

  return (
    <div
      className={cn('p-3 rounded-lg border-l-4', className)}
      style={{
        backgroundColor: `${config.color}10`,
        borderLeftColor: config.color,
      }}
    >
      <div className='flex items-start gap-3'>
        <div style={{ color: config.color }} className='mt-0.5'>
          {config.icon}
        </div>
        <div className='min-w-0 flex-1'>
          <h4 className='text-sm font-semibold'>{config.label}</h4>
          <p className='text-muted-foreground mt-1 text-xs'>{config.description}</p>
        </div>
      </div>
    </div>
  );
}

export const EditAffordances = memo(EditAffordancesComponent);
