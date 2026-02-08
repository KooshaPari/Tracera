import { Download, Plus, Upload } from 'lucide-react';
import { memo } from 'react';

import { Button } from '@tracertm/ui';

interface ProjectsListHeaderProps {
  onExport: () => void;
  onImport: () => void;
  onCreate: () => void;
}

export const ProjectsListHeader = memo(function ProjectsListHeader({
  onExport,
  onImport,
  onCreate,
}: ProjectsListHeaderProps): JSX.Element {
  return (
    <div className='flex flex-col justify-between gap-4 md:flex-row md:items-center'>
      <div>
        <h1 className='text-2xl font-black tracking-tight uppercase'>Project Registry</h1>
        <p className='text-muted-foreground text-sm font-medium'>
          Coordinate and scale multiple traceability domains from a single interface.
        </p>
      </div>
      <div className='flex items-center gap-2'>
        <Button
          variant='ghost'
          size='sm'
          onClick={onExport}
          className='gap-2 rounded-xl text-[10px] font-black tracking-widest uppercase'
        >
          <Download className='h-3.5 w-3.5' /> Export
        </Button>
        <Button
          variant='ghost'
          size='sm'
          onClick={onImport}
          className='gap-2 rounded-xl text-[10px] font-black tracking-widest uppercase'
        >
          <Upload className='h-3.5 w-3.5' /> Import
        </Button>
        <Button
          size='sm'
          onClick={onCreate}
          className='shadow-primary/20 gap-2 rounded-xl text-[10px] font-black tracking-widest uppercase shadow-lg'
        >
          <Plus className='h-4 w-4' /> New Registry
        </Button>
      </div>
    </div>
  );
});
