import { useMutation } from '@tanstack/react-query';
import { Link } from '@tanstack/react-router';
import { Copy, Edit, ExternalLink, MoreVertical, Trash2 } from 'lucide-react';
import { memo, useCallback } from 'react';
import { toast } from 'sonner';

import {
  Button,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@tracertm/ui';

interface ProjectCardMenuProps {
  projectId: string;
  onEdit: () => void;
  onRequestDelete: () => void;
}

const stopPropagation: React.MouseEventHandler<HTMLElement> = (event): void => {
  event.stopPropagation();
};

const copyToClipboard = async (text: string): Promise<void> => {
  const clipboard = globalThis.navigator?.clipboard;
  if (clipboard === undefined) {
    throw new Error('Clipboard unavailable');
  }
  await clipboard.writeText(text);
};

interface ProjectCardMenuViewProps {
  onCopyId: () => void;
  onEdit: (event: React.MouseEvent<HTMLDivElement>) => void;
  onMenuButtonClick: (event: React.MouseEvent<HTMLButtonElement>) => void;
  onRequestDelete: (event: React.MouseEvent<HTMLDivElement>) => void;
  projectId: string;
}

function renderProjectCardMenuView({
  onCopyId,
  onEdit,
  onMenuButtonClick,
  onRequestDelete,
  projectId,
}: ProjectCardMenuViewProps): JSX.Element {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <span>
          <Button
            variant='ghost'
            size='icon'
            className='text-muted-foreground hover:text-foreground hover:bg-muted z-10 h-8 w-8 shrink-0 transition-colors'
            onClick={onMenuButtonClick}
            aria-label='Project options'
          >
            <MoreVertical className='h-4 w-4' />
            <span className='sr-only'>Open project menu</span>
          </Button>
        </span>
      </DropdownMenuTrigger>
      <DropdownMenuContent align='end' className='w-48'>
        <DropdownMenuItem
          asChild
          className='hover:bg-accent hover:text-accent-foreground cursor-pointer gap-2 transition-colors'
        >
          <Link to={`/projects/${projectId}`} onClick={stopPropagation}>
            <ExternalLink className='h-4 w-4' />
            Open Project
          </Link>
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={onEdit}
          className='hover:bg-accent hover:text-accent-foreground cursor-pointer gap-2 transition-colors'
        >
          <Edit className='h-4 w-4' />
          Edit
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={onCopyId}
          className='hover:bg-accent hover:text-accent-foreground cursor-pointer gap-2 transition-colors'
        >
          <Copy className='h-4 w-4' />
          Copy ID
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          onClick={onRequestDelete}
          className='text-destructive focus:text-destructive focus:bg-destructive/10 hover:bg-destructive/10 hover:text-destructive cursor-pointer gap-2 transition-colors'
        >
          <Trash2 className='h-4 w-4' />
          Delete
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export const ProjectCardMenu = memo(function ProjectCardMenu({
  projectId,
  onEdit,
  onRequestDelete,
}: ProjectCardMenuProps): JSX.Element {
  const copyMutation = useMutation({
    mutationFn: copyToClipboard,
    onError: (error) => {
      let message = 'Failed to copy project ID';
      if (error instanceof Error) {
        const { message: errorMessage } = error;
        message = errorMessage;
      }
      toast.error(message);
    },
    onSuccess: () => {
      toast.success('Project ID copied');
    },
  });

  const handleMenuButtonClick = useCallback((event: React.MouseEvent<HTMLButtonElement>): void => {
    event.stopPropagation();
  }, []);

  const handleEdit = useCallback(
    (event: React.MouseEvent<HTMLDivElement>): void => {
      event.stopPropagation();
      onEdit();
    },
    [onEdit],
  );

  const handleCopyId = useCallback((): void => {
    copyMutation.mutate(projectId);
  }, [copyMutation, projectId]);

  const handleDeleteRequest = useCallback(
    (event: React.MouseEvent<HTMLDivElement>): void => {
      event.stopPropagation();
      onRequestDelete();
    },
    [onRequestDelete],
  );

  return renderProjectCardMenuView({
    onCopyId: handleCopyId,
    onEdit: handleEdit,
    onMenuButtonClick: handleMenuButtonClick,
    onRequestDelete: handleDeleteRequest,
    projectId,
  });
});
