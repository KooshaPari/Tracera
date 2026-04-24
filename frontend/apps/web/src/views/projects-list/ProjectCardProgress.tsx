import { memo, useMemo } from 'react';

import { Progress } from '@tracertm/ui';

const PROGRESS_BASE = 60;
const PROGRESS_SPAN = 40;

export const ProjectCardProgress = memo(function ProjectCardProgress(): JSX.Element {
  const progress = useMemo<number>(
    () => Math.floor(Math.random() * PROGRESS_SPAN) + PROGRESS_BASE,
    [],
  );

  return (
    <div className='space-y-3'>
      <div className='text-muted-foreground flex items-center justify-between text-[10px] font-black tracking-widest uppercase'>
        <span>Integrity Ratio</span>
        <span>{progress}%</span>
      </div>
      <Progress value={progress} className='bg-muted h-1.5' />
    </div>
  );
});
