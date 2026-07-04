import { Folder } from 'lucide-react';
import { memo } from 'react';

import { Badge } from '@tracertm/ui';

import { ProjectCardMenu } from './ProjectCardMenu';

interface ProjectCardHeaderProps {
  itemCount: number;
  projectId: string;
  onEdit: () => void;
  onRequestDelete: () => void;
}

export const ProjectCardHeader = memo(function ProjectCardHeader({
  itemCount,
  projectId,
  onEdit,
  onRequestDelete,
}: ProjectCardHeaderProps): JSX.Element {
  return (
    <div className='flex items-start justify-between'>
      <div className='bg-primary/5 group-hover:bg-primary group-hover:text-primary-foreground flex h-12 w-12 items-center justify-center rounded-2xl transition-all duration-500'>
        <Folder className='h-6 w-6' />
      </div>
      <div className='flex items-center gap-2'>
        <Badge
          variant='secondary'
          className='shrink-0 px-2 text-[10px] font-black tracking-tighter uppercase'
        >
          {itemCount} Items
        </Badge>
        <ProjectCardMenu projectId={projectId} onEdit={onEdit} onRequestDelete={onRequestDelete} />
      </div>
    </div>
  );
});
