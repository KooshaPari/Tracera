import { Link } from '@tanstack/react-router';
import { ArrowRight, Calendar } from 'lucide-react';
import { memo } from 'react';

import { Button } from '@tracertm/ui';

interface ProjectCardFooterProps {
  projectId: string;
  createdDateLabel: string;
}

export const ProjectCardFooter = memo(function ProjectCardFooter({
  projectId,
  createdDateLabel,
}: ProjectCardFooterProps): JSX.Element {
  return (
    <div className='flex items-center justify-between pt-2'>
      <div className='text-muted-foreground/60 flex items-center gap-2 text-[10px] font-bold uppercase'>
        <Calendar className='h-3 w-3' />
        {createdDateLabel}
      </div>
      <Link to={`/projects/${projectId}`}>
        <Button
          variant='ghost'
          size='sm'
          className='group/btn gap-2 text-[10px] font-black tracking-widest uppercase'
        >
          Connect
          <ArrowRight className='h-3 w-3 transition-transform group-hover/btn:translate-x-1' />
        </Button>
      </Link>
    </div>
  );
});
