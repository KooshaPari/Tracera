import { Link } from '@tanstack/react-router';
import { memo, useCallback, useMemo, useState } from 'react';

import type { Project } from '@tracertm/types';

import { getProjectDisplayName } from '@/lib/project-name-utils';
import { Card } from '@tracertm/ui';

import { ProjectCardFooter } from './ProjectCardFooter';
import { ProjectCardHeader } from './ProjectCardHeader';
import { ProjectCardProgress } from './ProjectCardProgress';
import { ProjectDeleteDialog } from './ProjectDeleteDialog';

interface ProjectCardProps {
  project: Project;
  itemCount: number;
  onEdit: (project: Project) => void;
}

const getProjectDescription = (project: Project): string => {
  const { description } = project;
  if (typeof description === 'string' && description.length > 0) {
    return description;
  }
  return 'Distributed traceability graph for requirements and implementation mapping.';
};

const getCreatedDateLabel = (createdAt?: string): string => {
  if (typeof createdAt !== 'string' || createdAt.length === 0) {
    return 'N/A';
  }
  return new Date(createdAt).toLocaleDateString();
};

export const ProjectCard = memo(function ProjectCard({
  project,
  itemCount,
  onEdit,
}: ProjectCardProps): JSX.Element {
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const description = useMemo<string>(() => getProjectDescription(project), [project]);
  const createdDateLabel = useMemo<string>(
    () => getCreatedDateLabel(project.createdAt),
    [project.createdAt],
  );

  const handleEdit = useCallback((): void => {
    onEdit(project);
  }, [onEdit, project]);

  const handleOpenDelete = useCallback((): void => {
    setIsDeleteOpen(true);
  }, []);

  const handleCloseDelete = useCallback((): void => {
    setIsDeleteOpen(false);
  }, []);

  return (
    <Card className='group border-border bg-card hover:border-primary/30 hover:bg-card relative cursor-pointer overflow-hidden rounded-[2rem] border p-5 shadow-lg backdrop-blur-sm transition-all duration-300 ease-out hover:-translate-y-0.5 hover:shadow-2xl active:translate-y-0 active:scale-[0.99] sm:p-6'>
      <div className='bg-primary/30 group-hover:bg-primary absolute top-0 left-0 h-full w-1 transition-colors' />

      <div className='flex h-full flex-col space-y-6'>
        <ProjectCardHeader
          itemCount={itemCount}
          projectId={project.id}
          onEdit={handleEdit}
          onRequestDelete={handleOpenDelete}
        />

        <div className='flex-1'>
          <Link to={`/projects/${project.id}`} className='block'>
            <h3 className='group-hover:text-primary line-clamp-2 text-xl font-black tracking-tight break-words transition-colors'>
              {getProjectDisplayName(project)}
            </h3>
          </Link>
          <p className='text-muted-foreground mt-2 line-clamp-4 text-xs leading-relaxed font-medium sm:line-clamp-3'>
            {description}
          </p>
        </div>

        <ProjectCardProgress />

        <ProjectCardFooter projectId={project.id} createdDateLabel={createdDateLabel} />
      </div>

      <ProjectDeleteDialog
        open={isDeleteOpen}
        project={project}
        onOpenChange={setIsDeleteOpen}
        onClosed={handleCloseDelete}
      />
    </Card>
  );
});
