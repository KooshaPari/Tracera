import {
  Download,
  Layers,
  LayoutGrid,
  Maximize2,
  PanelRight,
  PanelRightClose,
  RotateCcw,
  ZoomIn,
  ZoomOut,
} from 'lucide-react';

import type { LayoutType } from '@tracertm/types';

import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui/components/Select';
import { Separator } from '@tracertm/ui/components/Separator';

const LAYOUT_OPTIONS = [
  'cose',
  'breadthfirst',
  'circle',
  'elk',
] as const satisfies readonly LayoutType[];

function isLayoutType(value: string): value is LayoutType {
  return (LAYOUT_OPTIONS as readonly string[]).includes(value);
}

interface GraphControlsProps {
  layout: LayoutType;
  onExport: () => void;
  onFit: () => void;
  onLayoutChange: (layout: LayoutType) => void;
  onReset: () => void;
  onToggleDetailPanel: () => void;
  onToggleUITree: () => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  showDetailPanel: boolean;
  showUITree: boolean;
}

export function GraphControls({
  layout,
  showUITree,
  showDetailPanel,
  onLayoutChange,
  onToggleUITree,
  onToggleDetailPanel,
  onZoomIn,
  onZoomOut,
  onFit,
  onReset,
  onExport,
}: GraphControlsProps): JSX.Element {
  return (
    <Card className='p-3'>
      <div className='flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between'>
        <div className='flex flex-wrap items-center gap-2'>
          <Select
            value={layout}
            onValueChange={(v) => {
              if (isLayoutType(v)) {
                onLayoutChange(v);
              }
            }}
          >
            <SelectTrigger className='h-9 w-[160px]'>
              <Layers className='mr-2 h-4 w-4' />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value='cose'>Force-directed</SelectItem>
              <SelectItem value='breadthfirst'>Hierarchical</SelectItem>
              <SelectItem value='circle'>Circular</SelectItem>
              <SelectItem value='elk'>Directed Graph</SelectItem>
            </SelectContent>
          </Select>

          <Separator orientation='vertical' className='h-6' />

          <Button
            variant={showUITree ? 'default' : 'outline'}
            size='sm'
            onClick={onToggleUITree}
            className='h-9'
          >
            <LayoutGrid className='mr-2 h-4 w-4' />
            UI Library
          </Button>

          <Button variant='ghost' size='sm' onClick={onToggleDetailPanel} className='h-9'>
            {showDetailPanel ? (
              <PanelRightClose className='h-4 w-4' />
            ) : (
              <PanelRight className='h-4 w-4' />
            )}
          </Button>
        </div>

        <div className='flex items-center gap-2'>
          <div className='flex items-center gap-1 rounded-md border p-1'>
            <Button variant='ghost' size='sm' onClick={onZoomIn} className='h-7 w-7 p-0'>
              <ZoomIn className='h-4 w-4' />
            </Button>
            <Button variant='ghost' size='sm' onClick={onZoomOut} className='h-7 w-7 p-0'>
              <ZoomOut className='h-4 w-4' />
            </Button>
            <Button variant='ghost' size='sm' onClick={onFit} className='h-7 w-7 p-0'>
              <Maximize2 className='h-4 w-4' />
            </Button>
            <Button variant='ghost' size='sm' onClick={onReset} className='h-7 w-7 p-0'>
              <RotateCcw className='h-4 w-4' />
            </Button>
          </div>

          <Button variant='outline' size='sm' onClick={onExport} className='h-9'>
            <Download className='mr-2 h-4 w-4' />
            Export
          </Button>
        </div>
      </div>
    </Card>
  );
}
