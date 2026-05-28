import {
  Maximize,
  Maximize2,
  Minimize,
  PanelRight,
  PanelRightClose,
  RotateCcw,
  ZoomIn,
  ZoomOut,
} from 'lucide-react';

import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';
import { Separator } from '@tracertm/ui/components/Separator';

import { LayoutSelector } from '../layouts/LayoutSelector';
import type { LayoutType } from '../layouts/useDagLayout';

interface FlowGraphControlsProps {
  layout: LayoutType;
  onLayoutChange: (layout: LayoutType) => void;
  showDetailPanel: boolean;
  onDetailPanelToggle: () => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFit: () => void;
  onFullscreenToggle: () => void;
  onReset: () => void;
  isFullscreen: boolean;
}

export function FlowGraphControls({
  layout,
  onLayoutChange,
  showDetailPanel,
  onDetailPanelToggle,
  onZoomIn,
  onZoomOut,
  onFit,
  onFullscreenToggle,
  onReset,
  isFullscreen,
}: FlowGraphControlsProps) {
  return (
    <Card className='mb-2 p-1.5 sm:mb-3 sm:p-2'>
      <div className='flex min-w-0 flex-wrap items-center justify-between gap-2 sm:gap-3'>
        <div className='flex min-w-0 items-center gap-1.5 sm:gap-2'>
          <LayoutSelector
            value={layout}
            onChange={onLayoutChange}
            variant='select'
            className='h-7 w-full max-w-[160px] min-w-0 text-xs sm:h-8 sm:max-w-[180px] sm:text-sm md:max-w-[200px]'
          />

          <Separator orientation='vertical' className='hidden h-5 sm:block sm:h-6' />

          <Button
            variant='ghost'
            size='sm'
            onClick={onDetailPanelToggle}
            className='h-7 w-7 shrink-0 p-0 sm:h-8 sm:w-8'
          >
            {showDetailPanel ? (
              <PanelRightClose className='h-4 w-4' />
            ) : (
              <PanelRight className='h-4 w-4' />
            )}
          </Button>
        </div>

        <div className='flex items-center gap-1 rounded-md border p-0.5'>
          <Button variant='ghost' size='sm' onClick={onZoomIn} className='h-7 w-7 p-0'>
            <ZoomIn className='h-4 w-4' />
          </Button>
          <Button variant='ghost' size='sm' onClick={onZoomOut} className='h-7 w-7 p-0'>
            <ZoomOut className='h-4 w-4' />
          </Button>
          <Button
            variant='ghost'
            size='sm'
            onClick={onFit}
            className='h-7 w-7 p-0'
            title='Fit view'
          >
            <Maximize2 className='h-4 w-4' />
          </Button>
          <Button
            variant='ghost'
            size='sm'
            onClick={onFullscreenToggle}
            className='h-7 w-7 p-0'
            title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
          >
            {isFullscreen ? <Minimize className='h-4 w-4' /> : <Maximize className='h-4 w-4' />}
          </Button>
          <Button
            variant='ghost'
            size='sm'
            onClick={onReset}
            className='h-7 w-7 p-0'
            title='Reset view'
          >
            <RotateCcw className='h-4 w-4' />
          </Button>
        </div>
      </div>
    </Card>
  );
}
