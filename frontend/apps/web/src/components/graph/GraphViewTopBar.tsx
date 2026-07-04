import type { ChangeEvent, CSSProperties, PointerEvent } from 'react';

import { Search } from 'lucide-react';
import { useMemo } from 'react';

import { Badge } from '@tracertm/ui/components/Badge';
import { Input } from '@tracertm/ui/components/Input';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui/components/Select';
import { Separator } from '@tracertm/ui/components/Separator';

import type { GraphViewMode, ViewConfig } from './GraphViewConfig';

interface GraphViewTopBarProps {
  viewMode: GraphViewMode;
  viewTypeSearch: string;
  currentConfig: ViewConfig | undefined;
  filteredGraphViews: ViewConfig[];
  filteredDiagramViews: ViewConfig[];
  filteredPerspectiveViews: ViewConfig[];
  onSelectChange: (mode: string) => void;
  onSearchChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onSearchPointerDown: (event: PointerEvent<HTMLDivElement>) => void;
  perspectiveColor: string | undefined;
}

function buildBadgeStyle(color: string | undefined): CSSProperties | undefined {
  if (!color) {
    return undefined;
  }

  return {
    backgroundColor: `${color}20`,
    borderColor: color,
  };
}

function GraphViewTopBar({
  viewMode,
  viewTypeSearch,
  currentConfig,
  filteredGraphViews,
  filteredDiagramViews,
  filteredPerspectiveViews,
  onSelectChange,
  onSearchChange,
  onSearchPointerDown,
  perspectiveColor,
}: GraphViewTopBarProps): JSX.Element {
  const badgeStyle = useMemo(() => buildBadgeStyle(perspectiveColor), [perspectiveColor]);
  let descriptionNode: JSX.Element | undefined;
  let badgeNode: JSX.Element | undefined;

  if (currentConfig) {
    descriptionNode = (
      <div className='hidden max-w-[40vw] min-w-0 flex-1 sm:block md:max-w-[50vw] lg:max-w-none'>
        <p className='text-muted-foreground truncate text-xs sm:line-clamp-2 sm:text-sm md:text-base'>
          {currentConfig.description}
        </p>
      </div>
    );
  }

  if (currentConfig?.perspective) {
    badgeNode = (
      <Badge
        variant='outline'
        className='shrink-0 px-2 py-0.5 text-[10px] sm:px-3 sm:py-1 sm:text-xs'
        style={badgeStyle}
      >
        {currentConfig.label}
      </Badge>
    );
  }

  return (
    <div className='bg-background flex min-w-0 flex-wrap items-center justify-between gap-2 border-b p-2 sm:gap-4 sm:p-3'>
      <div className='flex min-w-0 flex-1 items-center gap-2 sm:gap-3'>
        <Select value={viewMode} onValueChange={onSelectChange}>
          <SelectTrigger
            className='h-8 w-full max-w-[240px] min-w-0 text-xs sm:h-9 sm:max-w-[260px] sm:text-sm md:max-w-[280px] [&>span]:min-w-0 [&>span]:truncate'
            aria-label='Graph or diagram view type'
          >
            <SelectValue placeholder='View type' />
          </SelectTrigger>
          <SelectContent position='popper' sideOffset={4} className='max-h-[min(70vh,400px)]'>
            <div
              className='bg-background sticky top-0 z-10 border-b p-1.5 sm:p-2'
              onPointerDown={onSearchPointerDown}
            >
              <div className='relative'>
                <Search className='text-muted-foreground absolute top-1/2 left-2 h-3.5 w-3.5 -translate-y-1/2 sm:left-2.5 sm:h-4 sm:w-4' />
                <Input
                  placeholder='Search view types...'
                  value={viewTypeSearch}
                  onChange={onSearchChange}
                  className='h-7 pl-7 text-xs sm:h-8 sm:pl-8 sm:text-sm'
                  aria-label='Filter view types'
                />
              </div>
            </div>
            <div className='p-1'>
              <SelectGroup>
                <div className='text-muted-foreground px-2 py-1 text-[10px] font-semibold tracking-wide uppercase sm:text-[11px]'>
                  Graph & diagram views
                </div>
                {filteredGraphViews.map((config) => (
                  <SelectItem key={config.id} value={config.id}>
                    <div className='flex min-w-0 items-center gap-2'>
                      <config.icon className='h-3.5 w-3.5 shrink-0 sm:h-4 sm:w-4' />
                      <div className='min-w-0 flex-1'>
                        <span className='block truncate text-xs sm:text-sm'>{config.label}</span>
                        <span className='text-muted-foreground line-clamp-2 block text-[10px] sm:text-[11px]'>
                          {config.description}
                        </span>
                      </div>
                    </div>
                  </SelectItem>
                ))}
                {filteredDiagramViews.map((config) => (
                  <SelectItem key={config.id} value={config.id}>
                    <div className='flex min-w-0 items-center gap-2'>
                      <config.icon className='h-3.5 w-3.5 shrink-0 sm:h-4 sm:w-4' />
                      <div className='min-w-0 flex-1'>
                        <span className='block truncate text-xs sm:text-sm'>{config.label}</span>
                        <span className='text-muted-foreground line-clamp-2 block text-[10px] sm:text-[11px]'>
                          {config.description}
                        </span>
                      </div>
                    </div>
                  </SelectItem>
                ))}
              </SelectGroup>
              <Separator className='my-1.5 sm:my-2' />
              <SelectGroup>
                <div className='text-muted-foreground px-2 py-1 text-[10px] font-semibold tracking-wide uppercase sm:text-[11px]'>
                  Perspectives
                </div>
                {filteredPerspectiveViews.map((config) => (
                  <SelectItem key={config.id} value={config.id}>
                    <div className='flex min-w-0 items-center gap-2'>
                      <config.icon className='h-3.5 w-3.5 shrink-0 sm:h-4 sm:w-4' />
                      <div className='min-w-0 flex-1'>
                        <span className='block truncate text-xs sm:text-sm'>{config.label}</span>
                        <span className='text-muted-foreground line-clamp-2 block text-[10px] sm:text-[11px]'>
                          {config.description}
                        </span>
                      </div>
                    </div>
                  </SelectItem>
                ))}
              </SelectGroup>
            </div>
          </SelectContent>
        </Select>

        {descriptionNode}
      </div>

      {badgeNode}
    </div>
  );
}

export { GraphViewTopBar };
