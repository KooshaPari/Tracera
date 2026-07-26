// Layout Selector with intuitive names and descriptions
// Replaces technical layout names with user-friendly options

import {
  ArrowDown,
  ArrowRight,
  Circle,
  CircleDot,
  GitBranch,
  LayoutGrid,
  Minimize2,
  Network,
} from 'lucide-react';

import { cn } from '@tracertm/ui';
import { Button } from '@tracertm/ui/components/Button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui/components/Select';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@tracertm/ui/components/Tooltip';

import type { LayoutType } from './useDagLayout';

import { LAYOUT_CONFIGS } from './useDagLayout';

// Map icon names to components
const ICON_MAP: Record<string, React.ComponentType<{ className?: string }>> = {
  ArrowDown,
  ArrowRight,
  Circle,
  CircleDot,
  GitBranch,
  LayoutGrid,
  Minimize2,
  Network,
};

interface LayoutSelectorProps {
  value: LayoutType;
  onChange: (layout: LayoutType) => void;
  variant?: 'select' | 'buttons' | 'compact';
  className?: string;
}

export function LayoutSelector({
  value,
  onChange,
  variant = 'select',
  className,
}: LayoutSelectorProps) {
  if (variant === 'buttons') {
    return (
      <TooltipProvider>
        <div className={cn('flex flex-wrap gap-1', className)}>
          {LAYOUT_CONFIGS.map((config) => {
            const Icon = ICON_MAP[config.icon] ?? Network;
            const isActive = value === config.id;

            return (
              <Tooltip key={config.id}>
                <TooltipTrigger asChild>
                  <Button
                    variant={isActive ? 'secondary' : 'ghost'}
                    size='sm'
                    className={cn(
                      'h-8 w-8 p-0',
                      isActive && 'bg-primary/10 text-primary border-primary/30',
                    )}
                    onClick={() => {
                      onChange(config.id);
                    }}
                  >
                    <Icon className='h-4 w-4' />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side='bottom' className='max-w-[200px]'>
                  <p className='font-medium'>{config.label}</p>
                  <p className='text-muted-foreground text-xs'>{config.description}</p>
                </TooltipContent>
              </Tooltip>
            );
          })}
        </div>
      </TooltipProvider>
    );
  }

  if (variant === 'compact') {
    return (
      <TooltipProvider>
        <div className={cn('flex gap-0.5 rounded-md border p-0.5', className)}>
          {LAYOUT_CONFIGS.slice(0, 4).map((config) => {
            const Icon = ICON_MAP[config.icon] ?? Network;
            const isActive = value === config.id;

            return (
              <Tooltip key={config.id}>
                <TooltipTrigger asChild>
                  <Button
                    variant='ghost'
                    size='sm'
                    className={cn('h-7 w-7 p-0', isActive && 'bg-primary/20 text-primary')}
                    onClick={() => {
                      onChange(config.id);
                    }}
                  >
                    <Icon className='h-3.5 w-3.5' />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side='bottom'>
                  <p>{config.label}</p>
                </TooltipContent>
              </Tooltip>
            );
          })}
        </div>
      </TooltipProvider>
    );
  }

  // Default: select dropdown (single icon via SelectValue only)
  return (
    <Select
      value={value}
      onValueChange={(v) => {
        onChange(v as LayoutType);
      }}
    >
      <SelectTrigger
        className={cn(
          'min-w-0 w-full max-w-[180px] sm:max-w-[200px] h-7 sm:h-9 text-xs sm:text-sm [&>span]:truncate [&>span]:min-w-0',
          className,
        )}
      >
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {LAYOUT_CONFIGS.map((config) => {
          const Icon = ICON_MAP[config.icon] ?? Network;
          return (
            <SelectItem key={config.id} value={config.id}>
              <div className='flex min-w-0 items-center gap-2'>
                <Icon className='h-3.5 w-3.5 shrink-0 sm:h-4 sm:w-4' />
                <div className='min-w-0 flex-1'>
                  <span className='block truncate text-xs sm:text-sm'>{config.label}</span>
                  <span className='text-muted-foreground block truncate text-[9px] sm:text-[10px]'>
                    {config.description}
                  </span>
                </div>
              </div>
            </SelectItem>
          );
        })}
      </SelectContent>
    </Select>
  );
}

// Recommended layouts for different perspectives
export const PERSPECTIVE_RECOMMENDED_LAYOUTS: Record<string, LayoutType> = {
  all: 'organic-network',
  components: 'tree',
  'page-flow': 'timeline',
  product: 'flow-chart',
  technical: 'tree',
  test: 'tree',
  traceability: 'flow-chart',
  ui: 'tree',
};

export function getRecommendedLayout(perspective: string): LayoutType {
  return PERSPECTIVE_RECOMMENDED_LAYOUTS[perspective] ?? 'flow-chart';
}
