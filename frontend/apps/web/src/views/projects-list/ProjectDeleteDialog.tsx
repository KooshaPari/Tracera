import { memo, useCallback, useState } from 'react';
import { toast } from 'sonner';

import type { Project } from '@tracertm/types';

import { useDeleteProject } from '@/hooks/useProjects';
import { getProjectDisplayName } from '@/lib/project-name-utils';
import { Button, Dialog, DialogContent } from '@tracertm/ui';

interface ProjectDeleteDialogProps {
  open: boolean;
  project: Project;
  onOpenChange: (open: boolean) => void;
  onClosed: () => void;
}

export const ProjectDeleteDialog = memo(function ProjectDeleteDialog({
  open,
  project,
  onOpenChange,
  onClosed,
}: ProjectDeleteDialogProps): JSX.Element {
  const deleteProject = useDeleteProject();
  const [isDeleting, setIsDeleting] = useState(false);

  const handleCancel = useCallback((): void => {
    onOpenChange(false);
    onClosed();
  }, [onClosed, onOpenChange]);

  const handleConfirm = useCallback((): void => {
    const displayName = getProjectDisplayName(project);
    setIsDeleting(true);
    deleteProject.mutate(project.id, {
      onError: () => {
        toast.error('Failed to delete project');
      },
      onSettled: () => {
        setIsDeleting(false);
      },
      onSuccess: () => {
        toast.success(`Project "${displayName}" deleted`);
        onOpenChange(false);
        onClosed();
      },
    });
  }, [deleteProject, onClosed, onOpenChange, project]);

  let deleteLabel = 'Delete';
  if (isDeleting) {
    deleteLabel = 'Deleting…';
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className='bg-card max-w-[420px] rounded-[2rem] border-none p-6 shadow-2xl'>
        <div className='space-y-4'>
          <div>
            <h2 className='text-lg font-black tracking-tight uppercase'>Delete Project</h2>
            <p className='text-muted-foreground mt-1 text-xs font-medium'>
              Deleting this project removes all related items and links. This cannot be undone.
            </p>
          </div>
          <div className='flex gap-3'>
            <Button
              type='button'
              variant='ghost'
              onClick={handleCancel}
              className='flex-1 rounded-xl text-[10px] font-black tracking-widest uppercase'
            >
              Cancel
            </Button>
            <Button
              type='button'
              onClick={handleConfirm}
              disabled={isDeleting}
              className='bg-destructive text-destructive-foreground flex-1 rounded-xl text-[10px] font-black tracking-widest uppercase'
            >
              {deleteLabel}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
});
